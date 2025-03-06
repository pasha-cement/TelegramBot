import os
import telebot
import logging
from telebot import types

# Импорт обработчиков
from handlers.main_menu_handlers import register_main_menu_handlers, get_user_state, set_user_state
from handlers.broadcast_handlers import register_broadcast_handlers
from handlers.template_handlers import register_template_handlers
from handlers.settings_handlers import register_settings_handlers

# Импорт функций для работы с конфигурацией
from utils import load_config, save_config

def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Создание необходимых директорий, если их нет
    os.makedirs('config', exist_ok=True)
    os.makedirs('files', exist_ok=True)
    
    # Инициализация конфигурационных файлов, если их нет
    if not os.path.exists(os.path.join('config', 'profile.json')):
        initial_profile = {
            "name": "NAME_PROFILE",
            "apiUrl": "YOUR_API_URL",
            "mediaUrl": "YOUR_MEDIA_URL",
            "idInstance": "YOUR_ID_INSTANCE",
            "apiTokenInstance": "YOUR_API_TOKEN_INSTANCE"
        }
        save_config(os.path.join('config', 'profile.json'), initial_profile)
    
    if not os.path.exists(os.path.join('config', 'interval.json')):
        initial_interval = {"interval": 5}
        save_config(os.path.join('config', 'interval.json'), initial_interval)
    
    if not os.path.exists(os.path.join('config', 'templates.json')):
        initial_templates = {"templates": []}
        save_config(os.path.join('config', 'templates.json'), initial_templates)
    
    # Создаем экземпляр бота
    TOKEN = 'YOUR_BOT_TOKEN'
    bot = telebot.TeleBot(TOKEN)
    
    # Регистрация обработчиков
    register_main_menu_handlers(bot)
    register_broadcast_handlers(bot)
    register_template_handlers(bot)
    register_settings_handlers(bot)
    
    logging.info("Бот успешно запущен и готов к работе")
    
    # Запуск бота в режиме бесконечного опроса
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        logging.error(f"Произошла ошибка: {str(e)}")
        # Пытаемся перезапустить бота при ошибке
        bot.stop_polling()
        main()

if __name__ == "__main__":
    main()