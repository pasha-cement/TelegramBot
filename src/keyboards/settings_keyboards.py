from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_settings_menu_keyboard():
    """
    Создает клавиатуру для меню настроек.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с пунктами меню настроек.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(
        KeyboardButton('👤 Профиль'),
        KeyboardButton('⏱️ Интервал'),
        KeyboardButton('🔙 Назад')
    )
    return keyboard

def get_profile_menu_keyboard():
    """
    Создает клавиатуру для раздела управления профилем.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с функциями управления профилем.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(
        KeyboardButton('✏️ Редактировать профиль'),
        KeyboardButton('🔄 Проверить соединение'),
        KeyboardButton('🔙 Назад')
    )
    return keyboard

def get_profile_edit_keyboard():
    """
    Создает клавиатуру для редактирования параметров профиля.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с параметрами профиля для редактирования.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(
        KeyboardButton('📝 Название профиля'),
        KeyboardButton('🔗 API URL'),
        KeyboardButton('🔗 Media URL'),
        KeyboardButton('🆔 ID инстанса'),
        KeyboardButton('🔑 API токен инстанса'),
        KeyboardButton('🔙 Назад')
    )
    return keyboard

def get_interval_keyboard():
    """
    Создает клавиатуру для установки интервала между сообщениями.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с предустановленными значениями интервала.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    # Добавляем кнопки с предустановленными значениями интервала
    keyboard.add(
        KeyboardButton('2'),
        KeyboardButton('5'),
        KeyboardButton('10')
    )
    keyboard.add(
        KeyboardButton('15'),
        KeyboardButton('30'),
        KeyboardButton('60')
    )
    keyboard.add(KeyboardButton('🔙 Назад'))
    return keyboard

def get_confirmation_keyboard():
    """
    Создает клавиатуру для подтверждения изменений в настройках.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с кнопками подтверждения и отмены.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton('✅ Подтвердить'),
        KeyboardButton('❌ Отменить')
    )
    return keyboard

def get_back_keyboard():
    """
    Создает клавиатуру с единственной кнопкой для возврата к предыдущему меню.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с кнопкой "Назад".
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('🔙 Назад'))
    return keyboard

def get_cancel_keyboard():
    """
    Создает клавиатуру с единственной кнопкой для отмены текущей операции.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с кнопкой "Отменить".
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('❌ Отменить'))
    return keyboard

def get_connection_test_result_keyboard(success):
    """
    Создает клавиатуру, отображающую результат проверки соединения.
    
    Аргументы:
        success (bool): Успешность соединения (True - успех, False - ошибка)
        
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с информацией о результате и кнопкой возврата.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    status = '✅ Соединение установлено' if success else '❌ Ошибка соединения'
    keyboard.add(
        KeyboardButton(status),
        KeyboardButton('🔙 Назад')
    )
    return keyboard