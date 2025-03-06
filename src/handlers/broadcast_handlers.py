import os
import json
import time
import pandas as pd
import telebot
from telebot import types
import threading

# Импорт клавиатур
from keyboards.broadcast_keyboards import (
    get_message_type_keyboard,
    get_confirm_keyboard,
    get_template_selection_keyboard,
    get_back_to_broadcast_keyboard,
    get_cancel_keyboard,
    get_pagination_keyboard
)
from keyboards.main_menu_keyboard import get_main_menu_keyboard

# Импорт утилит и API
from utils import (
    load_config,
    read_excel_numbers,
    normalize_phone_number,
    create_chat_id,
    is_valid_interval
)
from api import send_message, send_file_by_upload

# Словарь для хранения данных рассылки каждого пользователя
broadcast_data = {}

def register_broadcast_handlers(bot):
    """
    Регистрирует обработчики для создания и управления рассылками.
    
    Аргументы:
        bot (telebot.TeleBot): Экземпляр бота Telegram.
    """
    # Импортируем get_user_state и set_user_state из main_menu_handlers
    from handlers.main_menu_handlers import get_user_state, set_user_state
    
    # Обработка файла с номерами телефонов
    @bot.message_handler(content_types=['document'], 
                         func=lambda message: get_user_state(message.chat.id) == 'broadcast')
    def handle_document(message):
        chat_id = message.chat.id
        file_info = bot.get_file(message.document.file_id)
        
        # Проверяем тип файла
        file_name = message.document.file_name
        if not file_name.endswith(('.xls', '.xlsx')):
            bot.send_message(chat_id, "❌ Пожалуйста, загрузите файл в формате Excel (.xls или .xlsx)")
            return
        
        # Загружаем файл
        downloaded_file = bot.download_file(file_info.file_path)
        file_path = f"temp_{chat_id}.xlsx"
        
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        try:
            # Считываем номера из файла
            phone_numbers = read_excel_numbers(file_path)
            
            # Если файл пустой или нет номеров
            if not phone_numbers:
                bot.send_message(chat_id, "❌ В файле не найдены номера телефонов.")
                # Удаляем временный файл
                if os.path.exists(file_path):
                    os.remove(file_path)
                return
            
            # Сохраняем данные о рассылке
            broadcast_data[chat_id] = {
                'phone_numbers': phone_numbers,
                'file_path': file_path
            }
            
            # Информируем пользователя
            bot.send_message(
                chat_id, 
                f"✅ Файл успешно получен.\nОбнаружено {len(phone_numbers)} номеров.\n\nВыберите тип сообщения:",
                reply_markup=get_message_type_keyboard()
            )
            
            # Устанавливаем следующее состояние
            set_user_state(chat_id, 'broadcast_select_type')
            
        except Exception as e:
            bot.send_message(chat_id, f"❌ Ошибка при чтении файла: {str(e)}")
            # Удаляем временный файл в случае ошибки
            if os.path.exists(file_path):
                os.remove(file_path)
    
    # Обработчик отмены при ожидании файла
    @bot.message_handler(func=lambda message: message.text == '🔙 Назад' and 
                         get_user_state(message.chat.id) == 'broadcast')
    def cancel_broadcast_file_upload(message):
        chat_id = message.chat.id
        set_user_state(chat_id, 'main_menu')
        bot.send_message(chat_id, "Создание рассылки отменено. Вы вернулись в главное меню.", 
                         reply_markup=get_main_menu_keyboard())
    
    # Обработчик выбора типа сообщения
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'broadcast_select_type')
    def handle_message_type_selection(message):
        chat_id = message.chat.id
        
        if message.text == '📝 Текстовое сообщение':
            set_user_state(chat_id, 'broadcast_text_message')
            broadcast_data[chat_id]['message_type'] = 'text'
            bot.send_message(
                chat_id, 
                "Введите текстовое сообщение для рассылки:",
                reply_markup=get_cancel_keyboard()
            )
            
        elif message.text == '📝 Текстовое сообщение + 🗂️ файл':
            set_user_state(chat_id, 'broadcast_text_message_with_file')
            broadcast_data[chat_id]['message_type'] = 'text_with_file'
            bot.send_message(
                chat_id, 
                "Введите текстовое сообщение для рассылки:",
                reply_markup=get_cancel_keyboard()
            )
            
        elif message.text == '🧾 Использовать шаблон':
            # Загружаем шаблоны
            templates_path = os.path.join('config', 'templates.json')
            templates_config = load_config(templates_path)
            
            if templates_config and 'templates' in templates_config and templates_config['templates']:
                set_user_state(chat_id, 'broadcast_select_template')
                broadcast_data[chat_id]['message_type'] = 'template'
                broadcast_data[chat_id]['templates'] = templates_config['templates']
                
                bot.send_message(
                    chat_id, 
                    "Выберите шаблон сообщения:",
                    reply_markup=get_template_selection_keyboard(templates_config['templates'])
                )
            else:
                bot.send_message(
                    chat_id, 
                    "❌ Шаблоны не найдены. Пожалуйста, сначала создайте шаблоны в разделе 'Управление шаблонами'.",
                    reply_markup=get_message_type_keyboard()
                )
                
        elif message.text == '🔙 Назад':
            set_user_state(chat_id, 'broadcast')
            # Очищаем данные о рассылке
            if chat_id in broadcast_data:
                # Удаляем временный файл перед очисткой
                if 'file_path' in broadcast_data[chat_id] and os.path.exists(broadcast_data[chat_id]['file_path']):
                    os.remove(broadcast_data[chat_id]['file_path'])
                del broadcast_data[chat_id]
            
            bot.send_message(
                chat_id, 
                "Для начала рассылки прикрепите файл Excel с номерами телефонов.",
                reply_markup=types.ReplyKeyboardRemove()
            )
            
        else:
            bot.send_message(
                chat_id, 
                "❌ Пожалуйста, выберите тип сообщения, используя кнопки.",
                reply_markup=get_message_type_keyboard()
            )
    
    # Обработчик ввода текстового сообщения
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'broadcast_text_message')
    def handle_text_message(message):
        chat_id = message.chat.id
        
        if message.text == '❌ Отменить':
            set_user_state(chat_id, 'broadcast_select_type')
            bot.send_message(
                chat_id, 
                "Выберите тип сообщения:",
                reply_markup=get_message_type_keyboard()
            )
            return
        
        # Сохраняем текст сообщения
        broadcast_data[chat_id]['message'] = message.text
        
        # Показываем информацию о рассылке и запрашиваем подтверждение
        show_broadcast_info(bot, chat_id)
    
    # Обработчик ввода текстового сообщения с файлом (первый шаг - текст)
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'broadcast_text_message_with_file')
    def handle_text_message_with_file_step1(message):
        chat_id = message.chat.id
        
        if message.text == '❌ Отменить':
            set_user_state(chat_id, 'broadcast_select_type')
            bot.send_message(
                chat_id, 
                "Выберите тип сообщения:",
                reply_markup=get_message_type_keyboard()
            )
            return
        
        # Сохраняем текст сообщения
        broadcast_data[chat_id]['message'] = message.text
        
        # Просим загрузить файл
        set_user_state(chat_id, 'broadcast_upload_file')
        bot.send_message(
            chat_id, 
            "Загрузите файл для рассылки (изображение, видео, документ и т.д.):",
            reply_markup=get_cancel_keyboard()
        )
    
    # Обработчик загрузки файла для рассылки
    @bot.message_handler(content_types=['document', 'photo', 'video', 'audio'],
                        func=lambda message: get_user_state(message.chat.id) == 'broadcast_upload_file')
    def handle_file_upload(message):
        chat_id = message.chat.id
        
        # Определяем тип медиа и получаем file_id
        if message.content_type == 'document':
            file_id = message.document.file_id
            file_name = message.document.file_name
            file_type = 'document'
        elif message.content_type == 'photo':
            file_id = message.photo[-1].file_id  # Берем фото максимального размера
            file_name = f"photo_{file_id}.jpg"
            file_type = 'photo'
        elif message.content_type == 'video':
            file_id = message.video.file_id
            file_name = message.video.file_name if message.video.file_name else f"video_{file_id}.mp4"
            file_type = 'video'
        elif message.content_type == 'audio':
            file_id = message.audio.file_id
            file_name = message.audio.file_name if message.audio.file_name else f"audio_{file_id}.mp3"
            file_type = 'audio'
        
        # Скачиваем файл
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Создаем папку files, если её нет
        os.makedirs('files', exist_ok=True)
        
        # Сохраняем файл
        media_path = os.path.join('files', file_name)
        with open(media_path, 'wb') as media_file:
            media_file.write(downloaded_file)
        
        # Сохраняем информацию о файле
        broadcast_data[chat_id]['media'] = {
            'path': media_path,
            'type': file_type,
            'name': file_name
        }
        
        # Показываем информацию о рассылке
        show_broadcast_info(bot, chat_id)
    
    # Обработчик текстовых сообщений во время загрузки файла
    @bot.message_handler(func=lambda message: message.text == '❌ Отменить' and
                         get_user_state(message.chat.id) == 'broadcast_upload_file')
    def cancel_file_upload(message):
        chat_id = message.chat.id
        set_user_state(chat_id, 'broadcast_text_message_with_file')
        bot.send_message(
            chat_id, 
            "Загрузка файла отменена. Введите текстовое сообщение заново:",
            reply_markup=get_cancel_keyboard()
        )
    
    # Обработчик выбора шаблона
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'broadcast_select_template')
    def handle_template_selection(message):
        chat_id = message.chat.id
        
        if message.text == '🔙 Назад':
            set_user_state(chat_id, 'broadcast_select_type')
            bot.send_message(
                chat_id, 
                "Выберите тип сообщения:",
                reply_markup=get_message_type_keyboard()
            )
            return
        
        # Поиск выбранного шаблона
        selected_template = None
        for template in broadcast_data[chat_id].get('templates', []):
            if template['name'] == message.text:
                selected_template = template
                break
        
        if not selected_template:
            bot.send_message(
                chat_id, 
                "❌ Шаблон не найден. Пожалуйста, выберите шаблон из списка.",
                reply_markup=get_template_selection_keyboard(broadcast_data[chat_id].get('templates', []))
            )
            return
        
        # Сохраняем информацию о выбранном шаблоне
        broadcast_data[chat_id]['template'] = selected_template
        broadcast_data[chat_id]['message'] = selected_template['text']
        
        # Если шаблон содержит файл
        if selected_template.get('hasFile') and selected_template.get('filePath'):
            file_path = selected_template['filePath']
            if os.path.exists(file_path):
                # Получаем информацию о файле
                file_name = os.path.basename(file_path)
                file_extension = os.path.splitext(file_name)[1].lower()
                
                # Определяем тип файла
                if file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
                    file_type = 'photo'
                elif file_extension in ['.mp4', '.avi', '.mov']:
                    file_type = 'video'
                elif file_extension in ['.mp3', '.ogg', '.wav']:
                    file_type = 'audio'
                else:
                    file_type = 'document'
                
                # Сохраняем информацию о медиа файле
                broadcast_data[chat_id]['media'] = {
                    'path': file_path,
                    'type': file_type,
                    'name': file_name
                }
            else:
                bot.send_message(
                    chat_id, 
                    f"⚠️ Предупреждение: файл из шаблона не найден ({file_path}). Рассылка будет отправлена только с текстом."
                )
        
        # Показываем информацию о рассылке
        show_broadcast_info(bot, chat_id)
    
    # Обработчик подтверждения рассылки
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'broadcast_confirm')
    def handle_broadcast_confirmation(message):
        chat_id = message.chat.id
        
        if message.text == '✅ Подтвердить':
            # Проверяем наличие необходимых данных
            if not broadcast_data.get(chat_id, {}).get('phone_numbers'):
                bot.send_message(
                    chat_id, 
                    "❌ Ошибка: список номеров телефонов не найден. Начните создание рассылки заново.",
                    reply_markup=get_main_menu_keyboard()
                )
                clear_broadcast_data(chat_id)
                set_user_state(chat_id, 'main_menu')
                return
            
            if not broadcast_data[chat_id].get('message'):
                bot.send_message(
                    chat_id, 
                    "❌ Ошибка: текст сообщения не найден. Начните создание рассылки заново.",
                    reply_markup=get_main_menu_keyboard()
                )
                clear_broadcast_data(chat_id)
                set_user_state(chat_id, 'main_menu')
                return
            
            # Запускаем рассылку в отдельном потоке
            bot.send_message(
                chat_id, 
                "✅ Рассылка запущена. Вы получите уведомление по окончании процесса.",
                reply_markup=get_main_menu_keyboard()
            )
            
            # Запускаем рассылку в отдельном потоке
            broadcast_thread = threading.Thread(
                target=start_broadcast,
                args=(bot, chat_id, broadcast_data[chat_id])
            )
            broadcast_thread.start()
            
            # Возвращаем пользователя в главное меню
            set_user_state(chat_id, 'main_menu')
            
        elif message.text == '❌ Отменить':
            # Отменяем рассылку и возвращаемся к выбору типа
            set_user_state(chat_id, 'broadcast_select_type')
            bot.send_message(
                chat_id, 
                "Рассылка отменена. Выберите тип сообщения:",
                reply_markup=get_message_type_keyboard()
            )
            
        else:
            bot.send_message(
                chat_id, 
                "❌ Пожалуйста, подтвердите или отмените рассылку, используя кнопки.",
                reply_markup=get_confirm_keyboard()
            )
    
def show_broadcast_info(bot, chat_id):
    """
    Отображает информацию о настроенной рассылке и запрашивает подтверждение.
    
    Аргументы:
        bot (telebot.TeleBot): Экземпляр бота Telegram.
        chat_id (int): ID чата пользователя.
    """
    from handlers.main_menu_handlers import set_user_state
    
    if chat_id not in broadcast_data:
        bot.send_message(
            chat_id, 
            "❌ Данные о рассылке не найдены.",
            reply_markup=get_main_menu_keyboard()
        )
        set_user_state(chat_id, 'main_menu')
        return
    
    # Формируем сообщение с информацией о рассылке
    info_text = "📬 *Информация о рассылке:*\n\n"
    info_text += f"📱 Количество номеров: *{len(broadcast_data[chat_id]['phone_numbers'])}*\n\n"
    info_text += f"📝 Текст рассылки:\n```\n{broadcast_data[chat_id]['message']}\n```\n"
    
    # Информация о прикрепленном файле
    if 'media' in broadcast_data[chat_id]:
        file_name = broadcast_data[chat_id]['media']['name']
        file_type = broadcast_data[chat_id]['media']['type'].capitalize()
        info_text += f"📎 Прикрепленный файл: *{file_name}* ({file_type})\n"
    
    info_text += "\nПожалуйста, проверьте данные и подтвердите или отмените рассылку:"
    
    bot.send_message(
        chat_id, 
        info_text,
        reply_markup=get_confirm_keyboard(),
        parse_mode='Markdown'
    )
    
    # Устанавливаем состояние ожидания подтверждения
    set_user_state(chat_id, 'broadcast_confirm')

def start_broadcast(bot, chat_id, broadcast_info):
    """
    Запускает процесс рассылки сообщений.
    
    Аргументы:
        bot (telebot.TeleBot): Экземпляр бота Telegram.
        chat_id (int): ID чата пользователя.
        broadcast_info (dict): Информация о рассылке.
    """
    # Загружаем конфигурации
    profile_config = load_config(os.path.join('config', 'profile.json'))
    interval_config = load_config(os.path.join('config', 'interval.json'))
    
    if not profile_config:
        bot.send_message(chat_id, "❌ Ошибка: профиль не настроен.")
        clear_broadcast_data(chat_id)
        return
    
    # Получаем API-параметры
    api_url = profile_config.get('apiUrl')
    media_url = profile_config.get('mediaUrl')
    id_instance = profile_config.get('idInstance')
    api_token = profile_config.get('apiTokenInstance')
    
    if not all([api_url, id_instance, api_token]):
        bot.send_message(chat_id, "❌ Ошибка: неполные данные профиля.")
        clear_broadcast_data(chat_id)
        return
    
    # Получаем интервал между сообщениями
    interval = interval_config.get('interval', 5) if interval_config else 5
    
    # Получаем список номеров и сообщение
    phone_numbers = broadcast_info.get('phone_numbers', [])
    message = broadcast_info.get('message', '')
    
    # Счетчики для статистики
    total = len(phone_numbers)
    success = 0
    failed = 0
    
    # Отчет о начале рассылки
    bot.send_message(chat_id, f"🚀 Начинаем рассылку для {total} получателей...")
    
    # Логика рассылки
    for idx, phone in enumerate(phone_numbers):
        try:
            # Создаем chat_id для WhatsApp
            whatsapp_chat_id = create_chat_id(phone)
            
            # Если есть медиа, отправляем сообщение с медиа
            if 'media' in broadcast_info:
                media_path = broadcast_info['media']['path']
                if os.path.exists(media_path):
                    response = send_file_by_upload(
                        media_url, id_instance, api_token, 
                        whatsapp_chat_id, media_path, 
                        caption=message
                    )
                    if response and 'idMessage' in response:
                        success += 1
                    else:
                        failed += 1
                else:
                    # Если медиа файл не найден, отправляем только текст
                    response = send_message(api_url, id_instance, api_token, whatsapp_chat_id, message)
                    if response and 'idMessage' in response:
                        success += 1
                    else:
                        failed += 1
            else:
                # Отправляем только текстовое сообщение
                response = send_message(api_url, id_instance, api_token, whatsapp_chat_id, message)
                if response and 'idMessage' in response:
                    success += 1
                else:
                    failed += 1
            
            # Периодически отправляем статус (каждые 10 сообщений)
            if (idx + 1) % 10 == 0:
                progress = round((idx + 1) / total * 100)
                bot.send_message(
                    chat_id, 
                    f"📊 Прогресс: {idx + 1}/{total} ({progress}%)\n"
                    f"✅ Успешно: {success}\n"
                    f"❌ Ошибки: {failed}"
                )
            
            # Делаем паузу между отправками
            time.sleep(interval)
            
        except Exception as e:
            failed += 1
            print(f"Ошибка при отправке на номер {phone}: {str(e)}")
    
    # Отчет о завершении рассылки
    bot.send_message(
        chat_id, 
        f"✅ Рассылка завершена!\n\n"
        f"📊 Итоговая статистика:\n"
        f"📱 Всего номеров: {total}\n"
        f"✅ Успешно отправлено: {success}\n"
        f"❌ Ошибок: {failed}"
    )
    
    # Очищаем данные рассылки
    clear_broadcast_data(chat_id)

def clear_broadcast_data(chat_id):
    """
    Очищает данные рассылки для указанного пользователя.
    
    Аргументы:
        chat_id (int): ID чата пользователя.
    """
    if chat_id in broadcast_data:
        # Удаляем временный файл с номерами
        if 'file_path' in broadcast_data[chat_id]:
            file_path = broadcast_data[chat_id]['file_path']
            if os.path.exists(file_path) and 'temp_' in file_path:
                os.remove(file_path)
        
        # Удаляем запись из словаря
        del broadcast_data[chat_id]