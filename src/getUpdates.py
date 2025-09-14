import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

response = requests.get(url)
data = response.json()

if data["ok"]:
    for update in data["result"]:
        message = update.get("message")
        if message:
            chat = message.get("chat")
            chat_id = chat.get("id")
            print(f"Chat ID: {chat_id}")
            print(f"Name: {chat.get('first_name')} {chat.get('last_name')}/n")
else:
    print("Failed to get updates:", data)