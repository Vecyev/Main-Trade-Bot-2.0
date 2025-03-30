import os
import json
from datetime import datetime
from utils.signals import TradeSignalFeatures

class TradeScorer:
    def __init__(self, symbol="NVDA"):
        self.symbol = symbol
        self.feature_engine = TradeSignalFeatures(symbol)
        self.log_path = "logs/trades.json"
        os.makedirs("logs", exist_ok=True)

    def score_and_log_trade(self, option, premium, side="CALL"):
        features = self.feature_engine.get_features(option, side=side)
        features["premium"] = premium
        features["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Score: simple metric for now = ROC * (1 - near_earnings)
        score = features["roc"] * (1 - features["near_earnings"])
        features["score"] = round(score, 4)

        # Append to log file
        trades = []
        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, "r") as f:
                    trades = json.load(f)
            except Exception:
                trades = []

        trades.append(features)
        with open(self.log_path, "w") as f:
            json.dump(trades, f, indent=2)

        print(f"[TRADE SCORE] {features['side']} score: {features['score']}, ROC: {features['roc']}, RSI: {features['rsi']}")