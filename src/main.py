# main.py
import requests
import os
import time
import threading
import random

import openrouteservice
from requests.models import MissingSchema

from static.messages import cute_messages, siktir_messages

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ORS_API_KEY = os.getenv("ORS_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID_SELF = os.getenv("CHAT_ID_SELF")
CHAT_ID_L = os.getenv("CHAT_ID_L")
# CHAT_ID_GROUP = "TELEGRAM_GRUPPEN_CHAT_ID"
# CHAT_IDS = [CHAT_ID_SELF, CHAT_ID_L]
CHAT_IDS = [CHAT_ID_SELF]

# FIXED COORDS
HOME_COORDS = (os.getenv("LONGITUDE"), os.getenv("LATITUDE"))  # (Lon, Lat)

# CONFIG
NOTIFY_INTERVAL = 5  # Sekunden

xalaz = False

client = openrouteservice.Client(key=ORS_API_KEY)
latest_coords = None
last_notification_time = 0

def get_eta_minutes(start_coords):
    route = client.directions(coordinates=[start_coords, HOME_COORDS],
                              profile='foot-walking',
                              format='geojson')
    seconds = route['features'][0]['properties']['summary']['duration']
    return int(seconds / 60) + 5  # 5 Minuten Puffer


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for chat_id in CHAT_IDS:
        requests.post(url, data={"chat_id": chat_id, "text": text})


def eta_loop():
    global latest_coords, xalaz
    no_coords_reported = False  # to avoid spamming Telegram
    while True:
        time.sleep(NOTIFY_INTERVAL)
        print(f"[DEBUG] latest_coords value: {latest_coords}")
        if latest_coords:
            no_coords_reported = False  # reset flag because coords are present
            try:
                lon, lat = latest_coords[1], latest_coords[0]
                eta = get_eta_minutes([lon, lat])
                print(f"[DEBUG] Calculated ETA: {eta} minutes")
                if eta <= 5:
                    msg = random.choice(
                        siktir_messages if xalaz else cute_messages)
                    send_telegram_message(msg)
                else:
                    send_telegram_message(f"ETA nach Hause: ca. {eta} Minuten")
            except Exception as e:
                print(f"[ERROR] ETA loop: {e}")
        else:
            if not no_coords_reported:
                print("[DEBUG] No coordinates received yet.")
                send_telegram_message("No Location Data found")
                no_coords_reported = True


@app.route('/welcome', methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if not data:
        return "no data", 400

    message = data.get("message")
    if not message:
        return "no message", 200

    chat_id = message["chat"]["id"]
    if chat_id not in CHAT_IDS:
        print(f"Ignoring message from unauthorized chat_id {chat_id}")
        return "unauthorized", 403
    text = message.get("text", "")

    if text.lower() == "/start":
        send_telegram_message("Hey! Ich bin online.")
    elif "xalaz" in text.lower():
        global xalaz
        xalaz = not xalaz
        send_telegram_message(f"Xalaz-Modus: {'an' if xalaz else 'aus'}")

    return "ok", 200


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/location', methods=['POST'])
def location():
    global latest_coords
    data = request.json
    print(f"[DEBUG] Received location data: {data}")

    lat = data.get('latitude')
    lon = data.get('longitude')

    if lat is None or lon is None:
        return jsonify({"error": "No coordinates received"}), 400

    latest_coords = (lat, lon)
    print(f"[DEBUG] Updated latest_coords to: {latest_coords}")
    return jsonify({"message": "Coordinates updated"}), 200


if __name__ == '__main__':
    threading.Thread(target=eta_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
