from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_message_type_keyboard():
    """
    Клавиатура для выбора типа сообщения при создании рассылки.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с кнопками выбора типа сообщения.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(
        KeyboardButton('📝 Текстовое сообщение'),
        KeyboardButton('📝 Текстовое сообщение + 🗂️ файл'),
        KeyboardButton('🧾 Использовать шаблон'),
        KeyboardButton('🔙 Назад')
    )
    return keyboard

def get_confirm_keyboard():
    """
    Клавиатура для подтверждения или отмены рассылки.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с кнопками подтверждения и отмены.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton('✅ Подтвердить'),
        KeyboardButton('❌ Отменить')
    )
    return keyboard

def get_template_selection_keyboard(templates):
    """
    Создает клавиатуру с доступными шаблонами для рассылки.
    
    Аргументы:
        templates (list): Список словарей с информацией о шаблонах.
        
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с кнопками доступных шаблонов и кнопкой "Назад".
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    # Добавляем кнопку для каждого шаблона
    for template in templates:
        keyboard.add(KeyboardButton(template['name']))
    
    # Добавляем кнопку "Назад"
    keyboard.add(KeyboardButton('🔙 Назад'))
    
    return keyboard

def get_back_to_broadcast_keyboard():
    """
    Клавиатура с единственной кнопкой для возврата к созданию рассылки.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с кнопкой "Создать рассылку".
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('📢 Создать рассылку'))
    return keyboard

def get_cancel_keyboard():
    """
    Клавиатура с кнопкой отмены операции.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с кнопкой "Отменить".
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('❌ Отменить'))
    return keyboard

def get_pagination_keyboard(current_page, total_pages, template_count):
    """
    Создает inline-клавиатуру для пагинации при большом количестве шаблонов.
    
    Аргументы:
        current_page (int): Текущая страница.
        total_pages (int): Общее количество страниц.
        template_count (int): Общее количество шаблонов.
        
    Возвращает:
        InlineKeyboardMarkup: Inline-клавиатура с кнопками пагинации.
    """
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    buttons = []
    
    if current_page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"template_page_{current_page-1}"))
    
    buttons.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="current_page"))
    
    if current_page < total_pages:
        buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"template_page_{current_page+1}"))
    
    keyboard.add(*buttons)
    return keyboard