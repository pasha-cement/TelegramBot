import telebot
import json
import os
from telebot import types

# Импорт клавиатур
from keyboards.main_menu_keyboard import get_main_menu_keyboard, get_settings_menu_keyboard
from keyboards.broadcast_keyboards import get_message_type_keyboard
from keyboards.template_keyboards import get_template_management_keyboard

# Словарь для хранения состояний пользователей
user_states = {}

def register_main_menu_handlers(bot):
    """
    Регистрирует все обработчики команд главного меню.
    
    Аргументы:
        bot (telebot.TeleBot): Экземпляр бота Telegram.
    """
    # Обработчик команды /start
    @bot.message_handler(commands=['start'])
    def start_command(message):
        chat_id = message.chat.id
        user_states[chat_id] = 'main_menu'
        
        welcome_text = "👋 Добро пожаловать в Telegram Бот для рассылки сообщений!\n\n" \
                      "С помощью этого бота вы можете:\n" \
                      "• Создавать рассылки по списку номеров\n" \
                      "• Управлять шаблонами сообщений\n" \
                      "• Настраивать параметры подключения и рассылки\n\n" \
                      "Выберите действие в меню ниже:"
        
        bot.send_message(chat_id, welcome_text, reply_markup=get_main_menu_keyboard())
    
    # Обработчик для возврата в главное меню
    @bot.message_handler(func=lambda message: message.text == '🔙 Назад' and 
                         (user_states.get(message.chat.id) == 'settings' or 
                          user_states.get(message.chat.id) == 'broadcast' or 
                          user_states.get(message.chat.id) == 'templates'))
    def back_to_main_menu(message):
        chat_id = message.chat.id
        user_states[chat_id] = 'main_menu'
        
        bot.send_message(chat_id, "Вы вернулись в главное меню. Выберите действие:", 
                         reply_markup=get_main_menu_keyboard())
    
    # Обработчик выбора в главном меню
    @bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'main_menu')
    def main_menu_handler(message):
        chat_id = message.chat.id
        
        if message.text == '📢 Создать рассылку':
            user_states[chat_id] = 'broadcast'
            bot.send_message(chat_id, "Для начала рассылки прикрепите файл Excel с номерами телефонов.", 
                            reply_markup=types.ReplyKeyboardRemove())
            
            # Эта часть может меняться в зависимости от логики в broadcast_handlers.py
            # Здесь мы только переключаем состояние и передаем управление другому обработчику
        
        elif message.text == '📄 Управление шаблонами':
            user_states[chat_id] = 'templates'
            bot.send_message(chat_id, "Раздел управления шаблонами. Выберите действие:", 
                            reply_markup=get_template_management_keyboard())
        
        elif message.text == '⚙️ Настройки':
            user_states[chat_id] = 'settings'
            bot.send_message(chat_id, "Раздел настроек. Выберите параметр для настройки:", 
                            reply_markup=get_settings_menu_keyboard())
        
        else:
            bot.send_message(chat_id, "Пожалуйста, используйте кнопки меню для навигации.", 
                            reply_markup=get_main_menu_keyboard())

    # Обработчик команды /help
    @bot.message_handler(commands=['help'])
    def help_command(message):
        chat_id = message.chat.id
        
        help_text = "📌 *Справка по использованию бота*\n\n" \
                   "*Основные команды:*\n" \
                   "/start - запуск бота и переход в главное меню\n" \
                   "/help - показать эту справку\n\n" \
                   "*Разделы бота:*\n" \
                   "• 📢 *Создать рассылку* - отправка сообщений по списку номеров\n" \
                   "• 📄 *Управление шаблонами* - создание и редактирование шаблонов сообщений\n" \
                   "• ⚙️ *Настройки* - настройка профиля и параметров рассылки\n\n" \
                   "При возникновении вопросов обратитесь к администратору."
        
        bot.send_message(chat_id, help_text, parse_mode='Markdown')

    # Обработчик команды /menu для быстрого возврата в главное меню из любого состояния
    @bot.message_handler(commands=['menu'])
    def menu_command(message):
        chat_id = message.chat.id
        user_states[chat_id] = 'main_menu'
        
        bot.send_message(chat_id, "Главное меню:", reply_markup=get_main_menu_keyboard())

def get_user_state(user_id):
    """
    Возвращает текущее состояние пользователя.
    
    Аргументы:
        user_id (int): ID пользователя.
        
    Возвращает:
        str: Текущее состояние пользователя или None, если состояние не задано.
    """
    return user_states.get(user_id)

def set_user_state(user_id, state):
    """
    Устанавливает состояние пользователя.
    
    Аргументы:
        user_id (int): ID пользователя.
        state (str): Новое состояние пользователя.
    """
    user_states[user_id] = state