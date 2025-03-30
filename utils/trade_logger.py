
import csv
import os
from datetime import datetime

LOG_PATH = "logs/trade_history.csv"

# Ensure log directory exists
os.makedirs("logs", exist_ok=True)

def log_trade(trade_data):
    """
    trade_data should be a dictionary containing:
    {
        "Date": str,
        "Type": str,
        "Strike": float,
        "Premium": float,
        "DTE": int,
        "Conviction": float,
        "Overrides": str
    }
    """
    file_exists = os.path.isfile(LOG_PATH)

    with open(LOG_PATH, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=trade_data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(trade_data)
