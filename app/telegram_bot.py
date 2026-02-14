import requests
from django.conf import settings

def send_telegram_message(text):
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }

    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram error:", e)


