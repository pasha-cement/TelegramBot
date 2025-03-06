import pandas as pd
import json
import os
import re

def load_config(config_file):
    """
    Загружает конфигурацию из JSON файла.

    Аргументы:
        config_file (str): Путь к JSON файлу конфигурации.

    Возвращает:
        dict или None: Словарь с конфигурацией в случае успеха, None в случае ошибки.
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: Файл конфигурации не найден: {config_file}")
        return None
    except json.JSONDecodeError:
        print(f"Ошибка: Неверный формат JSON в файле: {config_file}")
        return None
    except Exception as e:
        print(f"Ошибка при загрузке конфигурации из {config_file}: {e}")
        return None

def save_config(config_file, config_data):
    """
    Сохраняет конфигурацию в JSON файл.

    Аргументы:
        config_file (str): Путь к JSON файлу конфигурации.
        config_data (dict): Словарь с данными конфигурации для сохранения.

    Возвращает:
        bool: True в случае успеха, False в случае ошибки.
    """
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении конфигурации в {config_file}: {e}")
        return False

def read_excel_numbers(file_path):
    """
    Читает номера телефонов из Excel файла (.xls или .xlsx).
    Предполагается, что номера телефонов находятся во втором столбце.

    Аргументы:
        file_path (str): Путь к Excel файлу.

    Возвращает:
        list или None: Список номеров телефонов в виде строк в случае успеха,
                       None в случае ошибки или если файл не содержит номеров.
    """
    try:
        df = pd.read_excel(file_path, header=None, engine='openpyxl')
        if df.empty:
            print(f"Файл Excel пуст: {file_path}")
            return []

        # Предполагаем, что номера во втором столбце. Преобразуем в строки, удаляем NaN и дубликаты
        phone_numbers = df.iloc[:, 1].astype(str).dropna().unique().tolist()

        if not phone_numbers:
            print(f"Номера телефонов не найдены в файле: {file_path}")
            return []

        return phone_numbers
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден: {file_path}")
        return None
    except Exception as e:
        print(f"Ошибка при чтении файла Excel: {e}")
        return None

def validate_file_path(file_path):
    """
    Проверяет, существует ли файл по указанному пути.

    Аргументы:
        file_path (str): Путь к файлу.

    Возвращает:
        bool: True, если файл существует, False в противном случае.
    """
    return os.path.exists(file_path)

def get_file_extension(file_path):
    """
    Возвращает расширение файла из указанного пути.

    Аргументы:
        file_path (str): Путь к файлу.

    Возвращает:
        str: Расширение файла (без точки), или пустая строка, если расширение не найдено.
    """
    _, extension = os.path.splitext(file_path)
    return extension.lstrip('.') # Удаляем точку в начале расширения, если есть

def remove_non_digits(phone_number):
    """
    Удаляет из строки номера телефона все символы, кроме цифр.

    Аргументы:
        phone_number (str): Номер телефона в виде строки.

    Возвращает:
        str: Строка, содержащая только цифры из исходного номера телефона.
    """
    return re.sub(r'\D', '', phone_number)

def replace_eight_with_seven(phone_number):
    """
    Заменяет первую цифру '8' на '7' в номере телефона, если номер начинается с '8'.
    Предполагается, что номер уже очищен от нецифровых символов.

    Аргументы:
        phone_number (str): Номер телефона в виде строки (только цифры).

    Возвращает:
        str: Номер телефона, где первая '8' заменена на '7', если исходный номер начинался с '8'.
             В противном случае возвращает исходный номер.
    """
    if phone_number.startswith('8'):
        return '7' + phone_number[1:]
    return phone_number

def check_phone_number_length(phone_number, expected_length=11):
    """
    Проверяет, состоит ли номер телефона из заданного количества цифр.
    Предполагается, что номер уже очищен от нецифровых символов.

    Аргументы:
        phone_number (str): Номер телефона в виде строки (только цифры).
        expected_length (int, optional): Ожидаемая длина номера телефона. По умолчанию 11.

    Возвращает:
        bool: True, если длина номера телефона соответствует ожидаемой, False в противном случае.
    """
    return len(phone_number) == expected_length

def normalize_phone_number(phone_number):
    """
    Нормализует номер телефона, выполняя следующие действия:
    1. Удаляет все нецифровые символы.
    2. Заменяет первую цифру '8' на '7', если номер начинается с '8'.
    3. Проверяет, что номер состоит из 11 цифр после нормализации.

    Аргументы:
        phone_number (str): Номер телефона в произвольном формате.

    Возвращает:
        str или None: Нормализованный номер телефона в виде строки, если он соответствует критериям.
                       None, если номер не соответствует ожидаемой длине после нормализации.
    """
    cleaned_number = remove_non_digits(phone_number)
    normalized_number = replace_eight_with_seven(cleaned_number)
    if check_phone_number_length(normalized_number):
        return normalized_number
    else:
        return None

def create_chat_id(phone_number):
    """
    Создает Chat ID на основе номера телефона.

    Аргументы:
        phone_number (str): Номер телефона.

    Возвращает:
        str: Chat ID в формате "79xxxxxxxxx@c.us".
    """
    return f"{phone_number}@c.us"

def is_valid_interval(interval):
    """
    Проверяет, является ли значение корректным интервалом для отправки сообщений.

    Аргументы:
        interval: Значение для проверки, как интервал.

    Возвращает:
        bool: True, если интервал валиден, False в противном случае.
    """
    if not isinstance(interval, (int, str)): # Проверяем тип данных, допускаем и строку, чтобы можно было проверить ввод пользователя
        return False

    try:
        interval_int = int(interval) # Пытаемся преобразовать в целое число
    except ValueError:
        return False # Если не удалось преобразовать в целое число, значит не валидный интервал

    if interval_int <= 0:
        return False # Интервал должен быть больше нуля

    return True # Если все проверки пройдены, интервал валиден

# Вспомогательные функции можно добавлять по мере необходимости.
# Например, функции для обработки текста, валидации данных и т.д.