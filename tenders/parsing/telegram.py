import os
import requests

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]


def send_telegram_message(telegram_user_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    body = {
        "chat_id": telegram_user_id,
        "text": text,
    }
    response = requests.post(url, json=body)
    # print(response.text)
    response.raise_for_status()
