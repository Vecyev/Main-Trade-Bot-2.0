from utils.env_loader import load_env
load_env()


import requests
import os

WEBHOOK_URL = os.getenv("TRADE_WEBHOOK_URL")

def post_trade_to_webhook(data):
    if not WEBHOOK_URL:
        print("No webhook URL configured.")
        return

    try:
        res = requests.post(WEBHOOK_URL, json=data)
        if res.status_code != 200:
            print("Webhook post failed:", res.text)
    except Exception as e:
        print("Webhook error:", e)