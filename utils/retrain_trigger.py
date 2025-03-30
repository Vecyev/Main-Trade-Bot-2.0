from utils.trade_model import TradeModel
import os
import json

def retrain_if_needed(log_path="logs/trades.json", min_trades=20):
    if not os.path.exists(log_path):
        return

    with open(log_path, "r") as f:
        trades = json.load(f)

    if len(trades) % min_trades == 0:
        print("[ML] Auto-retraining triggered")
        model = TradeModel()
        model.train_model()