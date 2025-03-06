import requests
import os
import mimetypes

def get_instance_state(api_url, id_instance, api_token_instance):
    """
    Проверяет состояние инстанса Green API.

    Аргументы:
        api_url (str): Базовый URL API (например, "https://1103.api.green-api.com").
        id_instance (str): ID инстанса.
        api_token_instance (str): API токен инстанса.

    Возвращает:
        dict или None: JSON-ответ от API в случае успеха, None в противном случае.
    """
    url = f"{api_url}/waInstance{id_instance}/getStateInstance/{api_token_instance}"
    payload = {}
    headers = {}

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        response.raise_for_status()  # Вызывает HTTPError для плохих ответов (4xx или 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка проверки состояния инстанса: {e}")
        return None

def send_message(api_url, id_instance, api_token_instance, chat_id, message):
    """
    Отправляет текстовое сообщение в указанный ID чата через Green API.

    Аргументы:
        api_url (str): Базовый URL API.
        id_instance (str): ID инстанса.
        api_token_instance (str): API токен инстанса.
        chat_id (str): ID чата в формате "7xxxxxxxxxx@c.us".
        message (str): Текстовое сообщение для отправки.

    Возвращает:
        dict или None: JSON-ответ от API в случае успеха, None в противном случае.
    """
    url = f"{api_url}/waInstance{id_instance}/sendMessage/{api_token_instance}"
    payload = {
        "chatId": chat_id,
        "message": message
    }
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки сообщения: {e}")
        return None

def send_file_by_upload(media_url, id_instance, api_token_instance, chat_id, file_path, caption=""):
    """
    Отправляет файл путем его загрузки в Green API.

    Аргументы:
        media_url (str): Базовый URL Media API (например, "https://1103.media.green-api.com").
        id_instance (str): ID инстанса.
        api_token_instance (str): API токен инстанса.
        chat_id (str): ID чата в формате "7xxxxxxxxxx@c.us".
        file_path (str): Путь к файлу для отправки.
        caption (str, optional): Подпись к файлу. По умолчанию "".

    Возвращает:
        dict или None: JSON-ответ от API в случае успеха, None в противном случае.
    """
    url = f"{media_url}/waInstance{id_instance}/sendFileByUpload/{api_token_instance}"
    payload = {
        'chatId': chat_id,
        'caption': caption
    }

    filename = os.path.basename(file_path)
    mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream' # MIME-тип по умолчанию, если не определен

    try:
        with open(file_path, 'rb') as file_obj:
            files = [
                ('file', (filename, file_obj, mime_type))
            ]
            response = requests.post(url, data=payload, files=files)
            response.raise_for_status()
            return response.json()
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден по пути: {file_path}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки файла: {e}")
        return None
    
