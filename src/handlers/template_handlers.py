import json
import uuid
import telebot
from telebot import types
import os

# Импорт клавиатур
from keyboards.template_keyboards import (
    get_template_management_keyboard,
    get_template_list_keyboard,
    get_template_actions_keyboard,
    get_template_edit_keyboard,
    get_file_management_keyboard,
    get_confirmation_keyboard,
    get_back_keyboard,
    get_cancel_keyboard,
    get_template_pagination_keyboard
)
from keyboards.main_menu_keyboard import get_main_menu_keyboard

# Импорт утилит
from utils import load_config, save_config, validate_file_path, get_file_extension

# Словарь для хранения временных данных шаблонов каждого пользователя
template_data = {}

def register_template_handlers(bot):
    """
    Регистрирует обработчики для раздела управления шаблонами.
    
    Аргументы:
        bot (telebot.TeleBot): Экземпляр бота Telegram.
    """
    # Импортируем get_user_state и set_user_state из main_menu_handlers
    from handlers.main_menu_handlers import get_user_state, set_user_state
    
    # Обработчик главного меню управления шаблонами
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'templates')
    def template_management_handler(message):
        chat_id = message.chat.id
        
        if message.text == '📋 Просмотреть шаблоны':
            # Загружаем шаблоны
            templates_config = load_config(os.path.join('config', 'templates.json'))
            
            if templates_config and 'templates' in templates_config and templates_config['templates']:
                templates = templates_config['templates']
                
                # Сохраняем список шаблонов во временные данные
                template_data[chat_id] = {'templates': templates}
                
                set_user_state(chat_id, 'templates_list')
                bot.send_message(
                    chat_id, 
                    f"Доступные шаблоны ({len(templates)}):\nВыберите шаблон для просмотра деталей:",
                    reply_markup=get_template_list_keyboard(templates)
                )
            else:
                bot.send_message(
                    chat_id, 
                    "📂 У вас пока нет сохраненных шаблонов. Вы можете создать новый шаблон.",
                    reply_markup=get_template_management_keyboard()
                )
                
        elif message.text == '➕ Создать шаблон':
            set_user_state(chat_id, 'templates_create_name')
            template_data[chat_id] = {'new_template': {}}
            
            bot.send_message(
                chat_id, 
                "Создание нового шаблона.\nВведите название шаблона:",
                reply_markup=get_cancel_keyboard()
            )
            
        elif message.text == '🔙 Назад':
            set_user_state(chat_id, 'main_menu')
            bot.send_message(
                chat_id, 
                "Вы вернулись в главное меню. Выберите действие:",
                reply_markup=get_main_menu_keyboard()
            )
            
        else:
            bot.send_message(
                chat_id, 
                "Пожалуйста, используйте кнопки меню для навигации.",
                reply_markup=get_template_management_keyboard()
            )
    
    # Обработчик списка шаблонов
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'templates_list')
    def template_list_handler(message):
        chat_id = message.chat.id
        
        if message.text == '🔙 Назад':
            set_user_state(chat_id, 'templates')
            bot.send_message(
                chat_id, 
                "Раздел управления шаблонами. Выберите действие:",
                reply_markup=get_template_management_keyboard()
            )
            return
        
        # Проверяем, выбран ли шаблон из списка
        if chat_id not in template_data or 'templates' not in template_data[chat_id]:
            bot.send_message(
                chat_id, 
                "❌ Ошибка: список шаблонов не найден. Пожалуйста, вернитесь в раздел управления шаблонами.",
                reply_markup=get_template_management_keyboard()
            )
            set_user_state(chat_id, 'templates')
            return
        
        # Ищем выбранный шаблон по имени
        selected_template = None
        for template in template_data[chat_id]['templates']:
            if template['name'] == message.text:
                selected_template = template
                break
        
        if not selected_template:
            bot.send_message(
                chat_id, 
                "❌ Шаблон не найден. Пожалуйста, выберите шаблон из списка.",
                reply_markup=get_template_list_keyboard(template_data[chat_id]['templates'])
            )
            return
        
        # Сохраняем выбранный шаблон
        template_data[chat_id]['selected_template'] = selected_template
        
        set_user_state(chat_id, 'templates_actions')
        bot.send_message(
            chat_id, 
            f"Шаблон: *{selected_template['name']}*\n\nВыберите действие:",
            parse_mode='Markdown',
            reply_markup=get_template_actions_keyboard()
        )
    
    # Обработчик действий с шаблоном
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'templates_actions')
    def template_actions_handler(message):
        chat_id = message.chat.id
        
        # Проверяем наличие выбранного шаблона
        if chat_id not in template_data or 'selected_template' not in template_data[chat_id]:
            bot.send_message(
                chat_id, 
                "❌ Ошибка: шаблон не выбран. Пожалуйста, вернитесь к списку шаблонов.",
                reply_markup=get_template_management_keyboard()
            )
            set_user_state(chat_id, 'templates')
            return
        
        selected_template = template_data[chat_id]['selected_template']
        
        if message.text == '👁️ Просмотреть':
            # Формируем текст для отображения информации о шаблоне
            template_info = f"📄 *Шаблон:* {selected_template['name']}\n\n"
            template_info += f"💬 *Текст сообщения:*\n```\n{selected_template['text']}\n```\n\n"
            
            # Информация о файле
            if selected_template.get('hasFile', False) and selected_template.get('filePath'):
                file_path = selected_template['filePath']
                file_exists = os.path.exists(file_path)
                file_name = os.path.basename(file_path)
                file_status = "✅ Доступен" if file_exists else "❌ Недоступен"
                
                template_info += f"📎 *Прикрепленный файл:*\n"
                template_info += f"Имя файла: {file_name}\n"
                template_info += f"Путь: `{file_path}`\n"
                template_info += f"Статус: {file_status}"
            else:
                template_info += "📎 *Прикрепленный файл:* нет"
            
            bot.send_message(
                chat_id, 
                template_info,
                parse_mode='Markdown',
                reply_markup=get_template_actions_keyboard()
            )
            
        elif message.text == '✏️ Изменить':
            set_user_state(chat_id, 'templates_edit')
            bot.send_message(
                chat_id, 
                f"Редактирование шаблона: *{selected_template['name']}*\n\n"
                f"Выберите параметр для изменения:",
                parse_mode='Markdown',
                reply_markup=get_template_edit_keyboard()
            )
            
        elif message.text == '🗑️ Удалить':
            set_user_state(chat_id, 'templates_delete_confirm')
            bot.send_message(
                chat_id, 
                f"⚠️ Вы действительно хотите удалить шаблон *{selected_template['name']}*?\n\n"
                f"Это действие нельзя отменить.",
                parse_mode='Markdown',
                reply_markup=get_confirmation_keyboard()
            )
            
        elif message.text == '🔙 Назад':
            # Возвращаемся к списку шаблонов
            if chat_id in template_data and 'templates' in template_data[chat_id]:
                set_user_state(chat_id, 'templates_list')
                bot.send_message(
                    chat_id, 
                    "Выберите шаблон:",
                    reply_markup=get_template_list_keyboard(template_data[chat_id]['templates'])
                )
            else:
                set_user_state(chat_id, 'templates')
                bot.send_message(
                    chat_id, 
                    "Раздел управления шаблонами. Выберите действие:",
                    reply_markup=get_template_management_keyboard()
                )
                
        else:
            bot.send_message(
                chat_id, 
                "Пожалуйста, выберите действие из списка.",
                reply_markup=get_template_actions_keyboard()
            )
    
    # Обработчик подтверждения удаления шаблона
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'templates_delete_confirm')
    def template_delete_confirm_handler(message):
        chat_id = message.chat.id
        
        if message.text == '✅ Подтвердить':
            # Проверяем наличие выбранного шаблона
            if chat_id not in template_data or 'selected_template' not in template_data[chat_id]:
                bot.send_message(
                    chat_id, 
                    "❌ Ошибка: шаблон не выбран. Пожалуйста, вернитесь к списку шаблонов.",
                    reply_markup=get_template_management_keyboard()
                )
                set_user_state(chat_id, 'templates')
                return
            
            selected_template = template_data[chat_id]['selected_template']
            
            # Загружаем все шаблоны
            templates_path = os.path.join('config', 'templates.json')
            templates_config = load_config(templates_path)
            
            if not templates_config or 'templates' not in templates_config:
                bot.send_message(
                    chat_id, 
                    "❌ Ошибка при загрузке шаблонов.",
                    reply_markup=get_template_management_keyboard()
                )
                set_user_state(chat_id, 'templates')
                return
            
            # Удаляем выбранный шаблон
            templates_config['templates'] = [t for t in templates_config['templates'] if t['id'] != selected_template['id']]
            
            # Сохраняем обновленный список шаблонов
            success = save_config(templates_path, templates_config)
            
            if success:
                bot.send_message(
                    chat_id, 
                    f"✅ Шаблон *{selected_template['name']}* успешно удален.",
                    parse_mode='Markdown',
                    reply_markup=get_template_management_keyboard()
                )
                set_user_state(chat_id, 'templates')
            else:
                bot.send_message(
                    chat_id, 
                    "❌ Ошибка при удалении шаблона.",
                    reply_markup=get_template_management_keyboard()
                )
                set_user_state(chat_id, 'templates')
            
        elif message.text == '❌ Отменить':
            # Возвращаемся к действиям с шаблоном
            set_user_state(chat_id, 'templates_actions')
            
            if chat_id in template_data and 'selected_template' in template_data[chat_id]:
                selected_template = template_data[chat_id]['selected_template']
                bot.send_message(
                    chat_id, 
                    f"Шаблон: *{selected_template['name']}*\n\nВыберите действие:",
                    parse_mode='Markdown',
                    reply_markup=get_template_actions_keyboard()
                )
            else:
                bot.send_message(
                    chat_id, 
                    "Выберите действие:",
                    reply_markup=get_template_actions_keyboard()
                )
                
        else:
            bot.send_message(
                chat_id, 
                "Пожалуйста, подтвердите или отмените удаление шаблона.",
                reply_markup=get_confirmation_keyboard()
            )
    
    # Обработчик меню редактирования шаблона
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'templates_edit')
    def template_edit_handler(message):
        chat_id = message.chat.id
        
        # Проверяем наличие выбранного шаблона
        if chat_id not in template_data or 'selected_template' not in template_data[chat_id]:
            bot.send_message(
                chat_id, 
                "❌ Ошибка: шаблон не выбран. Пожалуйста, вернитесь к списку шаблонов.",
                reply_markup=get_template_management_keyboard()
            )
            set_user_state(chat_id, 'templates')
            return
        
        selected_template = template_data[chat_id]['selected_template']
        
        if message.text == '📝 Изменить название':
            set_user_state(chat_id, 'templates_edit_name')
            bot.send_message(
                chat_id, 
                f"Текущее название шаблона: *{selected_template['name']}*\n\n"
                f"Введите новое название:",
                parse_mode='Markdown',
                reply_markup=get_cancel_keyboard()
            )
            
        elif message.text == '📄 Изменить текст':
            set_user_state(chat_id, 'templates_edit_text')
            bot.send_message(
                chat_id, 
                f"Текущий текст шаблона:\n```\n{selected_template['text']}\n```\n\n"
                f"Введите новый текст:",
                parse_mode='Markdown',
                reply_markup=get_cancel_keyboard()
            )
            
        elif message.text == '📎 Управление файлом':
            set_user_state(chat_id, 'templates_edit_file')
            has_file = selected_template.get('hasFile', False)
            bot.send_message(
                chat_id, 
                f"Управление файлом шаблона *{selected_template['name']}*:",
                parse_mode='Markdown',
                reply_markup=get_file_management_keyboard(has_file)
            )
            
        elif message.text == '🔙 Назад':
            set_user_state(chat_id, 'templates_actions')
            bot.send_message(
                chat_id, 
                f"Шаблон: *{selected_template['name']}*\n\nВыберите действие:",
                parse_mode='Markdown',
                reply_markup=get_template_actions_keyboard()
            )
            
        else:
            bot.send_message(
                chat_id, 
                "Пожалуйста, выберите параметр для изменения.",
                reply_markup=get_template_edit_keyboard()
            )
    
    # Обработчик редактирования названия шаблона
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'templates_edit_name')
    def template_edit_name_handler(message):
        chat_id = message.chat.id
        
        if message.text == '❌ Отменить':
            set_user_state(chat_id, 'templates_edit')
            
            if chat_id in template_data and 'selected_template' in template_data[chat_id]:
                selected_template = template_data[chat_id]['selected_template']
                bot.send_message(
                    chat_id, 
                    f"Редактирование шаблона: *{selected_template['name']}*\n\n"
                    f"Выберите параметр для изменения:",
                    parse_mode='Markdown',
                    reply_markup=get_template_edit_keyboard()
                )
            else:
                bot.send_message(
                    chat_id, 
                    "Выберите параметр для изменения:",
                    reply_markup=get_template_edit_keyboard()
                )
            return
        
        # Проверяем наличие выбранного шаблона
        if chat_id not in template_data or 'selected_template' not in template_data[chat_id]:
            bot.send_message(
                chat_id, 
                "❌ Ошибка: шаблон не выбран. Пожалуйста, вернитесь к списку шаблонов.",
                reply_markup=get_template_management_keyboard()
            )
            set_user_state(chat_id, 'templates')
            return
        
        # Обновляем название шаблона
        selected_template = template_data[chat_id]['selected_template']
        new_name = message.text
        
        # Загружаем все шаблоны
        templates_path = os.path.join('config', 'templates.json')
        templates_config = load_config(templates_path)
        
        if not templates_config or 'templates' not in templates_config:
            bot.send_message(
                chat_id, 
                "❌ Ошибка при загрузке шаблонов.",
                reply_markup=get_template_management_keyboard()
            )
            set_user_state(chat_id, 'templates')
            return
        
        # Обновляем название выбранного шаблона
        for template in templates_config['templates']:
            if template['id'] == selected_template['id']:
                template['name'] = new_name
                # Обновляем также в локальной копии
                selected_template['name'] = new_name
                break
        
        # Сохраняем обновленный список шаблонов
        success = save_config(templates_path, templates_config)
        
        if success:
            bot.send_message(
                chat_id, 
                f"✅ Название шаблона успешно изменено на *{new_name}*.",
                parse_mode='Markdown',
                reply_markup=get_template_edit_keyboard()
            )
            set_user_state(chat_id, 'templates_edit')
        else:
            bot.send_message(
                chat_id, 
                "❌ Ошибка при обновлении названия шаблона.",
                reply_markup=get_template_edit_keyboard()
            )
            set_user_state(chat_id, 'templates_edit')
    
    # Обработчик редактирования текста шаблона
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'templates_edit_text')
    def template_edit_text_handler(message):
        chat_id = message.chat.id
        
        if message.text == '❌ Отменить':
            set_user_state(chat_id, 'templates_edit')
            
            if chat_id in template_data and 'selected_template' in template_data[chat_id]:
                selected_template = template_data[chat_id]['selected_template']
                bot.send_message(
                    chat_id, 
                    f"Редактирование шаблона: *{selected_template['name']}*\n\n"
                    f"Выберите параметр для изменения:",
                    parse_mode='Markdown',
                    reply_markup=get_template_edit_keyboard()
                )
            else:
                bot.send_message(
                    chat_id, 
                    "Выберите параметр для изменения:",
                    reply_markup=get_template_edit_keyboard()
                )
            return
        
        # Проверяем наличие выбранного шаблона
        if chat_id not in template_data or 'selected_template' not in template_data[chat_id]:
            bot.send_message(
                chat_id, 
                "❌ Ошибка: шаблон не выбран. Пожалуйста, вернитесь к списку шаблонов.",
                reply_markup=get_template_management_keyboard()
            )
            set_user_state(chat_id, 'templates')
            return
        
        # Обновляем текст шаблона
        selected_template = template_data[chat_id]['selected_template']
        new_text = message.text
        
        # Загружаем все шаблоны
        templates_path = os.path.join('config', 'templates.json')
        templates_config = load_config(templates_path)
        
        if not templates_config or 'templates' not in templates_config:
            bot.send_message(
                chat_id, 
                "❌ Ошибка при загрузке шаблонов.",
                reply_markup=get_template_management_keyboard()
            )
            set_user_state(chat_id, 'templates')
            return
        
        # Обновляем текст выбранного шаблона
        for template in templates_config['templates']:
            if template['id'] == selected_template['id']:
                template['text'] = new_text
                # Обновляем также в локальной копии
                selected_template['text'] = new_text
                break
        
        # Сохраняем обновленный список шаблонов
        success = save_config(templates_path, templates_config)
        
        if success:
            bot.send_message(
                chat_id, 
                "✅ Текст шаблона успешно обновлен.",
                reply_markup=get_template_edit_keyboard()
            )
            set_user_state(chat_id, 'templates_edit')
        else:
            bot.send_message(
                chat_id, 
                "❌ Ошибка при обновлении текста шаблона.",
                reply_markup=get_template_edit_keyboard()
            )
            set_user_state(chat_id, 'templates_edit')
    
    # Обработчик управления файлом шаблона
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'templates_edit_file')
    def template_edit_file_handler(message):
        chat_id = message.chat.id
        
        # Проверяем наличие выбранного шаблона
        if chat_id not in template_data or 'selected_template' not in template_data[chat_id]:
            bot.send_message(
                chat_id, 
                "❌ Ошибка: шаблон не выбран. Пожалуйста, вернитесь к списку шаблонов.",
                reply_markup=get_template_management_keyboard()
            )
            set_user_state(chat_id, 'templates')
            return
        
        selected_template = template_data[chat_id]['selected_template']
        has_file = selected_template.get('hasFile', False)
        
        if message.text == '👁️ Просмотреть файл' and has_file:
            file_path = selected_template.get('filePath', '')
            
            if not file_path or not os.path.exists(file_path):
                bot.send_message(
                    chat_id, 
                    f"❌ Файл не найден по пути: {file_path}",
                    reply_markup=get_file_management_keyboard(has_file)
                )
                return
            
            # Отправляем файл пользователю в зависимости от типа
            try:
                file_ext = os.path.splitext(file_path)[1].lower()
                
                with open(file_path, 'rb') as file:
                    if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                        bot.send_photo(chat_id, file)
                    elif file_ext in ['.mp4', '.avi', '.mov']:
                        bot.send_video(chat_id, file)
                    elif file_ext in ['.mp3', '.ogg', '.wav']:
                        bot.send_audio(chat_id, file)
                    else:
                        bot.send_document(chat_id, file)
                
                bot.send_message(
                    chat_id, 
                    f"📄 Файл: {os.path.basename(file_path)}",
                    reply_markup=get_file_management_keyboard(has_file)
                )
            except Exception as e:
                bot.send_message(
                    chat_id, 
                    f"❌ Ошибка при отправке файла: {str(e)}",
                    reply_markup=get_file_management_keyboard(has_file)
                )
            
        elif message.text == '🔄 Заменить файл' and has_file:
            set_user_state(chat_id, 'templates_replace_file')
            bot.send_message(
                chat_id, 
                "Загрузите новый файл, который заменит текущий:",
                reply_markup=get_cancel_keyboard()
            )
            
        elif message.text == '🗑️ Удалить файл' and has_file:
            set_user_state(chat_id, 'templates_delete_file_confirm')
            bot.send_message(
                chat_id, 
                "⚠️ Вы действительно хотите удалить файл из шаблона?",
                reply_markup=get_confirmation_keyboard()
            )
            
        elif message.text == '➕ Добавить файл' and not has_file:
            set_user_state(chat_id, 'templates_add_file')
            bot.send_message(
                chat_id, 
                "Загрузите файл, который нужно прикрепить к шаблону:",
                reply_markup=get_cancel_keyboard()
            )
            
        elif message.text == '🔙 Назад':
            set_user_state(chat_id, 'templates_edit')
            bot.send_message(
                chat_id, 
                f"Редактирование шаблона: *{selected_template['name']}*\n\n"
                f"Выберите параметр для изменения:",
                parse_mode='Markdown',
                reply_markup=get_template_edit_keyboard()
            )
            
        else:
            bot.send_message(
                chat_id, 
                "Пожалуйста, выберите действие из списка.",
                reply_markup=get_file_management_keyboard(has_file)
            )
                         
    # Обработчик подтверждения удаления файла
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'templates_delete_file_confirm')
    def template_delete_file_confirm_handler(message):
        chat_id = message.chat.id
        
        if message.text == '✅ Подтвердить':
            # Проверяем наличие выбранного шаблона
            if chat_id not in template_data or 'selected_template' not in template_data[chat_id]:
                bot.send_message(
                    chat_id, 
                    "❌ Ошибка: шаблон не выбран. Пожалуйста, вернитесь к списку шаблонов.",
                    reply_markup=get_template_management_keyboard()
                )
                set_user_state(chat_id, 'templates')
                return
            
            # Загружаем все шаблоны
            templates_path = os.path.join('config', 'templates.json')
            templates_config = load_config(templates_path)
            
            if not templates_config or 'templates' not in templates_config:
                bot.send_message(
                    chat_id, 
                    "❌ Ошибка при загрузке шаблонов.",
                    reply_markup=get_template_management_keyboard()
                )
                set_user_state(chat_id, 'templates')
                return
            
            # Обновляем данные шаблона (удаляем ссылку на файл)
            selected_template = template_data[chat_id]['selected_template']
            for template in templates_config['templates']:
                if template['id'] == selected_template['id']:
                    template['hasFile'] = False
                    template['filePath'] = None
                    # Обновляем также в локальной копии
                    selected_template['hasFile'] = False
                    selected_template['filePath'] = None
                    break
            
            # Сохраняем обновленный список шаблонов
            success = save_config(templates_path, templates_config)
            
            if success:
                bot.send_message(
                    chat_id, 
                    "✅ Файл успешно удален из шаблона.",
                    reply_markup=get_file_management_keyboard(False)
                )
                set_user_state(chat_id, 'templates_edit_file')
            else:
                bot.send_message(
                    chat_id, 
                    "❌ Ошибка при удалении файла из шаблона.",
                    reply_markup=get_file_management_keyboard(True)
                )
                set_user_state(chat_id, 'templates_edit_file')
            
        elif message.text == '❌ Отменить':
            set_user_state(chat_id, 'templates_edit_file')
            
            if chat_id in template_data and 'selected_template' in template_data[chat_id]:
                selected_template = template_data[chat_id]['selected_template']
                has_file = selected_template.get('hasFile', False)
                bot.send_message(
                    chat_id, 
                    f"Управление файлом шаблона *{selected_template['name']}*:",
                    parse_mode='Markdown',
                    reply_markup=get_file_management_keyboard(has_file)
                )
            else:
                bot.send_message(
                    chat_id, 
                    "Управление файлом шаблона:",
                    reply_markup=get_file_management_keyboard(False)
                )
        else:
            bot.send_message(
                chat_id, 
                "Пожалуйста, подтвердите или отмените удаление файла.",
                reply_markup=get_confirmation_keyboard()
            )
    
    # Обработчик загрузки файла при добавлении к шаблону
    @bot.message_handler(content_types=['document', 'photo', 'video', 'audio'],
                        func=lambda message: get_user_state(message.chat.id) == 'templates_add_file')
    def template_add_file_handler(message):
        chat_id = message.chat.id
        
        # Проверяем наличие выбранного шаблона
        if chat_id not in template_data or 'selected_template' not in template_data[chat_id]:
            bot.send_message(
                chat_id, 
                "❌ Ошибка: шаблон не выбран. Пожалуйста, вернитесь к списку шаблонов.",
                reply_markup=get_template_management_keyboard()
            )
            set_user_state(chat_id, 'templates')
            return
        
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
        file_path = os.path.join('files', file_name)
        with open(file_path, 'wb') as file:
            file.write(downloaded_file)
        
        # Загружаем все шаблоны
        templates_path = os.path.join('config', 'templates.json')
        templates_config = load_config(templates_path)
        
        if not templates_config or 'templates' not in templates_config:
            bot.send_message(
                chat_id, 
                "❌ Ошибка при загрузке шаблонов.",
                reply_markup=get_template_management_keyboard()
            )
            set_user_state(chat_id, 'templates')
            return
        
        # Обновляем данные шаблона (добавляем ссылку на файл)
        selected_template = template_data[chat_id]['selected_template']
        for template in templates_config['templates']:
            if template['id'] == selected_template['id']:
                template['hasFile'] = True
                template['filePath'] = file_path
                # Обновляем также в локальной копии
                selected_template['hasFile'] = True
                selected_template['filePath'] = file_path
                break
        
        # Сохраняем обновленный список шаблонов
        success = save_config(templates_path, templates_config)
        
        if success:
            bot.send_message(
                chat_id, 
                f"✅ Файл успешно добавлен к шаблону: {file_name}",
                reply_markup=get_file_management_keyboard(True)
            )
            set_user_state(chat_id, 'templates_edit_file')
        else:
            bot.send_message(
                chat_id, 
                "❌ Ошибка при добавлении файла к шаблону.",
                reply_markup=get_file_management_keyboard(False)
            )
            set_user_state(chat_id, 'templates_edit_file')
    
    # Обработчик загрузки файла при замене существующего
    @bot.message_handler(content_types=['document', 'photo', 'video', 'audio'],
                        func=lambda message: get_user_state(message.chat.id) == 'templates_replace_file')
    def template_replace_file_handler(message):
        chat_id = message.chat.id
        
        # Проверяем наличие выбранного шаблона
        if chat_id not in template_data or 'selected_template' not in template_data[chat_id]:
            bot.send_message(
                chat_id, 
                "❌ Ошибка: шаблон не выбран. Пожалуйста, вернитесь к списку шаблонов.",
                reply_markup=get_template_management_keyboard()
            )
            set_user_state(chat_id, 'templates')
            return
        
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
        file_path = os.path.join('files', file_name)
        with open(file_path, 'wb') as file:
            file.write(downloaded_file)
        
        # Загружаем все шаблоны
        templates_path = os.path.join('config', 'templates.json')
        templates_config = load_config(templates_path)
        
        if not templates_config or 'templates' not in templates_config:
            bot.send_message(
                chat_id, 
                "❌ Ошибка при загрузке шаблонов.",
                reply_markup=get_template_management_keyboard()
            )
            set_user_state(chat_id, 'templates')
            return
        
        # Обновляем данные шаблона (меняем путь к файлу)
        selected_template = template_data[chat_id]['selected_template']
        for template in templates_config['templates']:
            if template['id'] == selected_template['id']:
                template['filePath'] = file_path
                # Обновляем также в локальной копии
                selected_template['filePath'] = file_path
                break
        
        # Сохраняем обновленный список шаблонов
        success = save_config(templates_path, templates_config)
        
        if success:
            bot.send_message(
                chat_id, 
                f"✅ Файл успешно заменен на: {file_name}",
                reply_markup=get_file_management_keyboard(True)
            )
            set_user_state(chat_id, 'templates_edit_file')
        else:
            bot.send_message(
                chat_id, 
                "❌ Ошибка при замене файла.",
                reply_markup=get_file_management_keyboard(True)
            )
            set_user_state(chat_id, 'templates_edit_file')

    # Обработчик отмены загрузки файла
    @bot.message_handler(func=lambda message: message.text == '❌ Отменить' and
                         (get_user_state(message.chat.id) == 'templates_add_file' or
                          get_user_state(message.chat.id) == 'templates_replace_file'))
    def cancel_file_upload_handler(message):
        chat_id = message.chat.id
        
        set_user_state(chat_id, 'templates_edit_file')
        
        if chat_id in template_data and 'selected_template' in template_data[chat_id]:
            selected_template = template_data[chat_id]['selected_template']
            has_file = selected_template.get('hasFile', False)
            bot.send_message(
                chat_id, 
                f"Управление файлом шаблона *{selected_template['name']}*:",
                parse_mode='Markdown',
                reply_markup=get_file_management_keyboard(has_file)
            )
        else:
            bot.send_message(
                chat_id, 
                "Управление файлом шаблона:",
                reply_markup=get_file_management_keyboard(False)
            )

    # Обработчики для создания нового шаблона
    
    # Обработчик ввода имени нового шаблона
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'templates_create_name')
    def template_create_name_handler(message):
        chat_id = message.chat.id
        
        if message.text == '❌ Отменить':
            set_user_state(chat_id, 'templates')
            # Очищаем данные создания шаблона
            if chat_id in template_data and 'new_template' in template_data[chat_id]:
                del template_data[chat_id]['new_template']
            
            bot.send_message(
                chat_id, 
                "Создание шаблона отменено. Выберите действие:",
                reply_markup=get_template_management_keyboard()
            )
            return
        
        # Сохраняем название нового шаблона
        if chat_id not in template_data:
            template_data[chat_id] = {}
        if 'new_template' not in template_data[chat_id]:
            template_data[chat_id]['new_template'] = {}
        
        template_data[chat_id]['new_template']['name'] = message.text
        
        # Переходим к вводу текста шаблона
        set_user_state(chat_id, 'templates_create_text')
        bot.send_message(
            chat_id, 
            "Введите текст шаблона:",
            reply_markup=get_cancel_keyboard()
        )
    
    # Обработчик ввода текста нового шаблона
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'templates_create_text')
    def template_create_text_handler(message):
        chat_id = message.chat.id
        
        if message.text == '❌ Отменить':
            set_user_state(chat_id, 'templates')
            # Очищаем данные создания шаблона
            if chat_id in template_data and 'new_template' in template_data[chat_id]:
                del template_data[chat_id]['new_template']
            
            bot.send_message(
                chat_id, 
                "Создание шаблона отменено. Выберите действие:",
                reply_markup=get_template_management_keyboard()
            )
            return
        
        # Сохраняем текст нового шаблона
        if chat_id not in template_data or 'new_template' not in template_data[chat_id]:
            bot.send_message(
                chat_id, 
                "❌ Ошибка: данные о создаваемом шаблоне не найдены.",
                reply_markup=get_template_management_keyboard()
            )
            set_user_state(chat_id, 'templates')
            return
        
        template_data[chat_id]['new_template']['text'] = message.text
        
        # Спрашиваем, нужно ли добавить файл
        set_user_state(chat_id, 'templates_create_file_query')
        bot.send_message(
            chat_id, 
            "Хотите добавить файл к шаблону?",
            reply_markup=get_confirmation_keyboard()
        )
    
    # Обработчик запроса на добавление файла к новому шаблону
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'templates_create_file_query')
    def template_create_file_query_handler(message):
        chat_id = message.chat.id
        
        if message.text == '✅ Подтвердить':
            set_user_state(chat_id, 'templates_create_add_file')
            bot.send_message(
                chat_id, 
                "Загрузите файл для шаблона (изображение, видео, документ и т.д.):",
                reply_markup=get_cancel_keyboard()
            )
            
        elif message.text == '❌ Отменить':
            # Создаем шаблон без файла
            create_new_template(bot, chat_id, False)
            
        else:
            bot.send_message(
                chat_id, 
                "Пожалуйста, используйте кнопки для выбора.",
                reply_markup=get_confirmation_keyboard()
            )
    
    # Обработчик загрузки файла для нового шаблона
    @bot.message_handler(content_types=['document', 'photo', 'video', 'audio'],
                        func=lambda message: get_user_state(message.chat.id) == 'templates_create_add_file')
    def template_create_add_file_handler(message):
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
        file_path = os.path.join('files', file_name)
        with open(file_path, 'wb') as file:
            file.write(downloaded_file)
        
        # Сохраняем путь к файлу
        if chat_id not in template_data or 'new_template' not in template_data[chat_id]:
            bot.send_message(
                chat_id, 
                "❌ Ошибка: данные о создаваемом шаблоне не найдены.",
                reply_markup=get_template_management_keyboard()
            )
            set_user_state(chat_id, 'templates')
            return
        
        template_data[chat_id]['new_template']['filePath'] = file_path
        
        # Создаем новый шаблон с файлом
        create_new_template(bot, chat_id, True)
    
    # Обработчик отмены создания шаблона с файлом
    @bot.message_handler(func=lambda message: message.text == '❌ Отменить' and
                         get_user_state(message.chat.id) == 'templates_create_add_file')
    def cancel_template_create_file_handler(message):
        chat_id = message.chat.id
        
        # Создаем шаблон без файла
        create_new_template(bot, chat_id, False)

def create_new_template(bot, chat_id, with_file=False):
    """
    Создает новый шаблон и сохраняет его в конфигурации.
    
    Аргументы:
        bot (telebot.TeleBot): Экземпляр бота Telegram.
        chat_id (int): ID чата пользователя.
        with_file (bool): Флаг наличия файла.
    """
    # Импортируем set_user_state из main_menu_handlers
    from handlers.main_menu_handlers import set_user_state
    
    # Проверяем наличие данных шаблона
    if chat_id not in template_data or 'new_template' not in template_data[chat_id]:
        bot.send_message(
            chat_id, 
            "❌ Ошибка: данные о создаваемом шаблоне не найдены.",
            reply_markup=get_template_management_keyboard()
        )
        set_user_state(chat_id, 'templates')
        return
    
    new_template = template_data[chat_id]['new_template']
    
    if 'name' not in new_template or 'text' not in new_template:
        bot.send_message(
            chat_id, 
            "❌ Ошибка: неполные данные шаблона.",
            reply_markup=get_template_management_keyboard()
        )
        set_user_state(chat_id, 'templates')
        return
    
    # Загружаем существующие шаблоны
    templates_path = os.path.join('config', 'templates.json')
    templates_config = load_config(templates_path)
    
    if not templates_config:
        templates_config = {'templates': []}
    elif 'templates' not in templates_config:
        templates_config['templates'] = []
    
    # Создаем новый шаблон
    template = {
        'id': str(uuid.uuid4()),
        'name': new_template['name'],
        'text': new_template['text'],
        'hasFile': with_file,
        'filePath': new_template.get('filePath') if with_file else None
    }
    
    # Добавляем шаблон в список
    templates_config['templates'].append(template)
    
    # Сохраняем обновленный список шаблонов
    success = save_config(templates_path, templates_config)
    
    if success:
        bot.send_message(
            chat_id, 
            f"✅ Шаблон *{new_template['name']}* успешно создан.",
            parse_mode='Markdown',
            reply_markup=get_template_management_keyboard()
        )
    else:
        bot.send_message(
            chat_id, 
            "❌ Ошибка при сохранении шаблона.",
            reply_markup=get_template_management_keyboard()
        )
    
    # Очищаем данные создания шаблона
    del template_data[chat_id]['new_template']
    
    # Возвращаемся в меню управления шаблонами
    set_user_state(chat_id, 'templates')