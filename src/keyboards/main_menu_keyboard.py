from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_keyboard():
    """
    Создает клавиатуру главного меню бота.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура главного меню с основными функциями.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(
        KeyboardButton('📢 Создать рассылку'),
        KeyboardButton('📄 Управление шаблонами'),
        KeyboardButton('⚙️ Настройки')
    )
    return keyboard

def get_settings_menu_keyboard():
    """
    Создает клавиатуру для меню настроек.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с кнопками меню настроек.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(
        KeyboardButton('👤 Профиль'),
        KeyboardButton('⏱️ Интервал'),
        KeyboardButton('🔙 Назад')
    )
    return keyboard

def get_back_to_main_menu_keyboard():
    """
    Создает клавиатуру с единственной кнопкой для возврата в главное меню.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с кнопкой "Назад".
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('🔙 Назад'))
    return keyboard

def get_profile_edit_keyboard():
    """
    Создает клавиатуру для раздела профиля.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с кнопкой редактирования профиля и кнопкой "Назад".
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(
        KeyboardButton('✏️ Редактировать профиль'),
        KeyboardButton('🔙 Назад')
    )
    return keyboard

def get_confirmation_keyboard():
    """
    Создает клавиатуру для подтверждения действий в меню настроек.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с кнопками подтверждения и отмены.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton('✅ Подтвердить'),
        KeyboardButton('❌ Отменить')
    )
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