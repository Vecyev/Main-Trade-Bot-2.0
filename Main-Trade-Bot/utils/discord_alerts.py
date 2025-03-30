
import requests
import os
from utils.env_loader import load_env

load_env()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_alert(message):
    if not DISCORD_WEBHOOK_URL:
        print("Discord webhook URL not set.")
        return
    payload = {"content": message}
    try:
        r = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if r.status_code != 204:
            print("Discord post failed:", r.text)
    except Exception as e:
        print("Discord alert error:", e)
