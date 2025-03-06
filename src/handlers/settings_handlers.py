import os
import json
import telebot
from telebot import types

# Импорт клавиатур
from keyboards.settings_keyboards import (
    get_settings_menu_keyboard,
    get_profile_menu_keyboard,
    get_profile_edit_keyboard,
    get_interval_keyboard,
    get_confirmation_keyboard,
    get_back_keyboard,
    get_cancel_keyboard,
    get_connection_test_result_keyboard
)
from keyboards.main_menu_keyboard import get_main_menu_keyboard

# Импорт утилит и API
from utils import load_config, save_config, is_valid_interval
from api import get_instance_state

# Словарь для хранения временных данных настроек каждого пользователя
settings_data = {}

def register_settings_handlers(bot):
    """
    Регистрирует обработчики для раздела настроек.
    
    Аргументы:
        bot (telebot.TeleBot): Экземпляр бота Telegram.
    """
    # Импортируем get_user_state и set_user_state из main_menu_handlers
    from handlers.main_menu_handlers import get_user_state, set_user_state
    
    # Обработчик входа в меню настроек
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'settings')
    def settings_menu_handler(message):
        chat_id = message.chat.id
        
        if message.text == '👤 Профиль':
            set_user_state(chat_id, 'settings_profile')
            bot.send_message(
                chat_id, 
                "Раздел управления профилем Green API. Выберите действие:",
                reply_markup=get_profile_menu_keyboard()
            )
            
        elif message.text == '⏱️ Интервал':
            set_user_state(chat_id, 'settings_interval')
            
            # Загружаем текущее значение интервала
            interval_config = load_config(os.path.join('config', 'interval.json'))
            current_interval = interval_config.get('interval', 5) if interval_config else 5
            
            bot.send_message(
                chat_id, 
                f"Настройка интервала между сообщениями при рассылке.\n\n"
                f"Текущее значение: *{current_interval} секунд*\n\n"
                f"Выберите новое значение или введите число от 1 до 60:",
                reply_markup=get_interval_keyboard(),
                parse_mode='Markdown'
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
                reply_markup=get_settings_menu_keyboard()
            )
    
    # === ОБРАБОТЧИКИ ДЛЯ РАЗДЕЛА ПРОФИЛЯ ===
    
    # Обработчик меню профиля
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'settings_profile')
    def profile_menu_handler(message):
        chat_id = message.chat.id
        
        if message.text == '✏️ Редактировать профиль':
            set_user_state(chat_id, 'settings_profile_edit')
            bot.send_message(
                chat_id, 
                "Выберите параметр профиля для редактирования:",
                reply_markup=get_profile_edit_keyboard()
            )
            
        elif message.text == '🔄 Проверить соединение':
            # Загружаем профиль
            profile_config = load_config(os.path.join('config', 'profile.json'))
            
            if not profile_config:
                bot.send_message(
                    chat_id, 
                    "❌ Ошибка: профиль не настроен. Пожалуйста, сначала настройте профиль.",
                    reply_markup=get_profile_menu_keyboard()
                )
                return
            
            # Получаем параметры API
            api_url = profile_config.get('apiUrl')
            id_instance = profile_config.get('idInstance')
            api_token = profile_config.get('apiTokenInstance')
            
            if not all([api_url, id_instance, api_token]):
                bot.send_message(
                    chat_id, 
                    "❌ Ошибка: неполные данные профиля. Пожалуйста, настройте все параметры.",
                    reply_markup=get_profile_menu_keyboard()
                )
                return
            
            # Пытаемся выполнить проверку соединения
            bot.send_message(chat_id, "⏳ Проверка соединения с API...", reply_markup=types.ReplyKeyboardRemove())
            
            try:
                response = get_instance_state(api_url, id_instance, api_token)
                
                if response and response.get('stateInstance') in ['authorized', 'online']:
                    # Соединение успешно
                    success = True
                    bot.send_message(
                        chat_id, 
                        f"✅ Соединение установлено успешно!\n\n"
                        f"📱 Номер WhatsApp: *{response.get('wid', 'Не указан')}*\n"
                        f"👤 Имя: *{response.get('name', 'Не указано')}*\n"
                        f"🔌 Статус: *{response.get('stateInstance', 'Не указан')}*\n",
                        parse_mode='Markdown',
                        reply_markup=get_connection_test_result_keyboard(True)
                    )
                else:
                    # Соединение установлено, но статус не authorized
                    success = False
                    state = response.get('stateInstance', 'неизвестно') if response else 'нет ответа'
                    bot.send_message(
                        chat_id, 
                        f"⚠️ Соединение установлено, но статус инстанса: *{state}*\n"
                        f"Для работы требуется статус *authorized* или *online*.\n"
                        f"Пожалуйста, проверьте авторизацию в Green API.",
                        parse_mode='Markdown',
                        reply_markup=get_connection_test_result_keyboard(False)
                    )
            except Exception as e:
                # Ошибка соединения
                success = False
                bot.send_message(
                    chat_id, 
                    f"❌ Ошибка при подключении к API: {str(e)}",
                    reply_markup=get_connection_test_result_keyboard(False)
                )
            
            # Переводим пользователя в состояние проверки соединения
            set_user_state(chat_id, 'settings_connection_test_result')
            
        elif message.text == '🔙 Назад':
            set_user_state(chat_id, 'settings')
            bot.send_message(
                chat_id, 
                "Выберите раздел настроек:",
                reply_markup=get_settings_menu_keyboard()
            )
            
        else:
            bot.send_message(
                chat_id, 
                "Пожалуйста, используйте кнопки меню для навигации.",
                reply_markup=get_profile_menu_keyboard()
            )
    
    # Обработчик результата проверки соединения
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'settings_connection_test_result')
    def connection_test_result_handler(message):
        chat_id = message.chat.id
        
        if message.text == '🔙 Назад':
            set_user_state(chat_id, 'settings_profile')
            bot.send_message(
                chat_id, 
                "Раздел управления профилем. Выберите действие:",
                reply_markup=get_profile_menu_keyboard()
            )
        else:
            bot.send_message(
                chat_id, 
                "Пожалуйста, нажмите кнопку 'Назад' для возврата в меню профиля.",
                reply_markup=get_back_keyboard()
            )
    
    # Обработчик меню редактирования профиля
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'settings_profile_edit')
    def profile_edit_handler(message):
        chat_id = message.chat.id
        
        # Параметры профиля для редактирования
        profile_params = {
            '📝 Название профиля': 'name',
            '🔗 API URL': 'apiUrl',
            '🔗 Media URL': 'mediaUrl',
            '🆔 ID инстанса': 'idInstance',
            '🔑 API токен инстанса': 'apiTokenInstance'
        }
        
        if message.text in profile_params:
            param_key = profile_params[message.text]
            
            # Загружаем текущий профиль
            profile_config = load_config(os.path.join('config', 'profile.json'))
            current_value = profile_config.get(param_key, '') if profile_config else ''
            
            # Сохраняем параметр для редактирования
            settings_data[chat_id] = {
                'edit_parameter': param_key,
                'current_value': current_value
            }
            
            set_user_state(chat_id, 'settings_profile_edit_param')
            bot.send_message(
                chat_id, 
                f"Редактирование параметра: *{message.text}*\n\n"
                f"Текущее значение: `{current_value}`\n\n"
                f"Введите новое значение:",
                parse_mode='Markdown',
                reply_markup=get_cancel_keyboard()
            )
            
        elif message.text == '🔙 Назад':
            set_user_state(chat_id, 'settings_profile')
            bot.send_message(
                chat_id, 
                "Раздел управления профилем. Выберите действие:",
                reply_markup=get_profile_menu_keyboard()
            )
            
        else:
            bot.send_message(
                chat_id, 
                "Пожалуйста, используйте кнопки меню для навигации.",
                reply_markup=get_profile_edit_keyboard()
            )
    
    # Обработчик ввода значения параметра профиля
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'settings_profile_edit_param')
    def profile_param_input_handler(message):
        chat_id = message.chat.id
        
        if message.text == '❌ Отменить':
            set_user_state(chat_id, 'settings_profile_edit')
            bot.send_message(
                chat_id, 
                "Редактирование отменено. Выберите параметр для редактирования:",
                reply_markup=get_profile_edit_keyboard()
            )
            return
        
        if chat_id not in settings_data or 'edit_parameter' not in settings_data[chat_id]:
            bot.send_message(
                chat_id, 
                "❌ Ошибка: данные для редактирования не найдены. Пожалуйста, начните заново.",
                reply_markup=get_profile_edit_keyboard()
            )
            set_user_state(chat_id, 'settings_profile_edit')
            return
        
        # Сохраняем новое значение
        settings_data[chat_id]['new_value'] = message.text
        param_name = settings_data[chat_id]['edit_parameter']
        
        # Запрашиваем подтверждение
        bot.send_message(
            chat_id, 
            f"Вы собираетесь изменить параметр *{param_name}*\n\n"
            f"Новое значение: `{message.text}`\n\n"
            f"Подтвердите изменение:",
            parse_mode='Markdown',
            reply_markup=get_confirmation_keyboard()
        )
        
        set_user_state(chat_id, 'settings_profile_confirm')
    
    # Обработчик подтверждения изменения параметра профиля
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'settings_profile_confirm')
    def profile_confirm_handler(message):
        chat_id = message.chat.id
        
        if message.text == '✅ Подтвердить':
            if chat_id not in settings_data or 'edit_parameter' not in settings_data[chat_id] or 'new_value' not in settings_data[chat_id]:
                bot.send_message(
                    chat_id, 
                    "❌ Ошибка: данные для редактирования не найдены. Пожалуйста, начните заново.",
                    reply_markup=get_profile_edit_keyboard()
                )
                set_user_state(chat_id, 'settings_profile_edit')
                return
            
            # Параметр и новое значение
            param_name = settings_data[chat_id]['edit_parameter']
            new_value = settings_data[chat_id]['new_value']
            
            # Загружаем текущий профиль
            profile_path = os.path.join('config', 'profile.json')
            profile_config = load_config(profile_path)
            
            if not profile_config:
                profile_config = {}
            
            # Обновляем параметр
            profile_config[param_name] = new_value
            
            # Сохраняем обновленный профиль
            success = save_config(profile_path, profile_config)
            
            if success:
                bot.send_message(
                    chat_id, 
                    f"✅ Параметр *{param_name}* успешно обновлен.",
                    parse_mode='Markdown',
                    reply_markup=get_profile_edit_keyboard()
                )
            else:
                bot.send_message(
                    chat_id, 
                    f"❌ Ошибка при сохранении параметра *{param_name}*. Пожалуйста, попробуйте еще раз.",
                    parse_mode='Markdown',
                    reply_markup=get_profile_edit_keyboard()
                )
            
            # Чистим временные данные
            if chat_id in settings_data:
                del settings_data[chat_id]
            
            # Возвращаемся к редактированию профиля
            set_user_state(chat_id, 'settings_profile_edit')
            
        elif message.text == '❌ Отменить':
            # Чистим временные данные
            if chat_id in settings_data:
                del settings_data[chat_id]
                
            set_user_state(chat_id, 'settings_profile_edit')
            bot.send_message(
                chat_id, 
                "Изменение отменено. Выберите параметр для редактирования:",
                reply_markup=get_profile_edit_keyboard()
            )
            
        else:
            bot.send_message(
                chat_id, 
                "Пожалуйста, подтвердите или отмените изменение параметра.",
                reply_markup=get_confirmation_keyboard()
            )
    
    # === ОБРАБОТЧИКИ ДЛЯ ИНТЕРВАЛА ===
    
    # Обработчик настройки интервала
    @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == 'settings_interval')
    def interval_handler(message):
        chat_id = message.chat.id
        
        if message.text == '🔙 Назад':
            set_user_state(chat_id, 'settings')
            bot.send_message(
                chat_id, 
                "Выберите раздел настроек:",
                reply_markup=get_settings_menu_keyboard()
            )
            return
        
        # Проверяем, является ли текст числом
        if message.text.isdigit() or message.text in ['2', '5', '10', '15', '30', '60']:
            interval = int(message.text)
            
            # Проверяем валидность интервала
            if not is_valid_interval(interval):
                bot.send_message(
                    chat_id, 
                    "❌ Недопустимый интервал. Пожалуйста, введите число от 1 до 60 секунд.",
                    reply_markup=get_interval_keyboard()
                )
                return
            
            # Сохраняем новый интервал
            interval_path = os.path.join('config', 'interval.json')
            interval_config = {'interval': interval}
            
            success = save_config(interval_path, interval_config)
            
            if success:
                bot.send_message(
                    chat_id, 
                    f"✅ Интервал между сообщениями успешно установлен на *{interval} секунд*.",
                    parse_mode='Markdown',
                    reply_markup=get_settings_menu_keyboard()
                )
                set_user_state(chat_id, 'settings')
            else:
                bot.send_message(
                    chat_id, 
                    "❌ Ошибка при сохранении интервала. Пожалуйста, попробуйте еще раз.",
                    reply_markup=get_interval_keyboard()
                )
        else:
            bot.send_message(
                chat_id, 
                "❌ Пожалуйста, введите число от 1 до 60 или выберите один из предустановленных вариантов.",
                reply_markup=get_interval_keyboard()
            )