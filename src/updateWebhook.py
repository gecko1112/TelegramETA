import requests
import time
import os

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
NGROK_API = 'http://localhost:4040/api/tunnels'
WEBHOOK_PATH = '/welcome'  # the endpoint your Flask app uses
LOCAL_PORT = 8080  # the port your Flask app runs on


def get_ngrok_url():
    try:
        tunnels = requests.get(NGROK_API).json()['tunnels']
        for tunnel in tunnels:
            if tunnel['proto'] == 'https':
                return tunnel['public_url']
    except Exception as e:
        print("Error getting ngrok URL:", e)
    return None


def set_telegram_webhook(url):
    full_url = f'{url}{WEBHOOK_PATH}'
    webhook_url = f'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook'
    response = requests.post(webhook_url, data={'url': full_url})
    print("Telegram webhook response:", response.json())


if __name__ == "__main__":
    print("Waiting for ngrok to start...")
    time.sleep(2)  # wait for ngrok to initialize
    public_url = get_ngrok_url()
    if public_url:
        print("Ngrok public URL:", public_url)
        set_telegram_webhook(public_url)
    else:
        print("Failed to get public URL from ngrok.")
