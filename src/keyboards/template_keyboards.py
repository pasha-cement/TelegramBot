from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_template_management_keyboard():
    """
    Создает основную клавиатуру раздела управления шаблонами.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с функциями управления шаблонами.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(
        KeyboardButton('📋 Просмотреть шаблоны'),
        KeyboardButton('➕ Создать шаблон'),
        KeyboardButton('🔙 Назад')
    )
    return keyboard

def get_template_list_keyboard(templates):
    """
    Создает клавиатуру со списком доступных шаблонов.
    
    Аргументы:
        templates (list): Список словарей с данными шаблонов.
        
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура со списком шаблонов и кнопкой "Назад".
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    for template in templates:
        keyboard.add(KeyboardButton(template['name']))
    
    keyboard.add(KeyboardButton('🔙 Назад'))
    return keyboard

def get_template_actions_keyboard():
    """
    Создает клавиатуру действий для выбранного шаблона.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с действиями для шаблона.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton('👁️ Просмотреть'),
        KeyboardButton('✏️ Изменить'),
        KeyboardButton('🗑️ Удалить'),
        KeyboardButton('🔙 Назад')
    )
    return keyboard

def get_template_edit_keyboard():
    """
    Создает клавиатуру для редактирования параметров шаблона.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с параметрами шаблона для редактирования.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(
        KeyboardButton('📝 Изменить название'),
        KeyboardButton('📄 Изменить текст'),
        KeyboardButton('📎 Управление файлом'),
        KeyboardButton('🔙 Назад')
    )
    return keyboard

def get_file_management_keyboard(has_file):
    """
    Создает клавиатуру для управления файлом шаблона.
    
    Аргументы:
        has_file (bool): Флаг наличия прикрепленного файла.
        
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с кнопками управления файлом.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    if has_file:
        keyboard.add(
            KeyboardButton('👁️ Просмотреть файл'),
            KeyboardButton('🔄 Заменить файл'),
            KeyboardButton('🗑️ Удалить файл')
        )
    else:
        keyboard.add(KeyboardButton('➕ Добавить файл'))
    
    keyboard.add(KeyboardButton('🔙 Назад'))
    return keyboard

def get_confirmation_keyboard():
    """
    Создает клавиатуру для подтверждения действий с шаблоном.
    
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
    Создает клавиатуру с кнопкой для возврата к предыдущему меню.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с кнопкой "Назад".
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('🔙 Назад'))
    return keyboard

def get_cancel_keyboard():
    """
    Создает клавиатуру с кнопкой для отмены текущего действия.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с кнопкой "Отменить".
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('❌ Отменить'))
    return keyboard

def get_template_pagination_keyboard(current_page, total_pages):
    """
    Создает inline-клавиатуру для навигации по страницам списка шаблонов.
    
    Аргументы:
        current_page (int): Номер текущей страницы.
        total_pages (int): Общее количество страниц.
        
    Возвращает:
        InlineKeyboardMarkup: Inline-клавиатура с кнопками навигации.
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