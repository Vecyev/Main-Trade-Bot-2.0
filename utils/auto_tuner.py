import json
import pandas as pd
import os
from statistics import mean

class StrategyAutoTuner:
    def __init__(self, log_path="logs/trades.json"):
        self.log_path = log_path
        self.df = self.load_trades()

    def load_trades(self):
        if not os.path.exists(self.log_path):
            print("[AUTO-TUNER] No trade log found.")
            return pd.DataFrame()

        with open(self.log_path, "r") as f:
            trades = json.load(f)

        return pd.DataFrame(trades)

    def tune(self):
        if self.df.empty or len(self.df) < 10:
            print("[AUTO-TUNER] Not enough data to tune.")
            return {}

        suggestions = {}

        # Delta tuning
        delta_bins = pd.cut(self.df["delta"], bins=[0, 0.15, 0.25, 0.35, 0.5])
        delta_group = self.df.groupby(delta_bins)["score"].mean()
        best_delta_range = delta_group.idxmax()
        suggestions["DELTA_TARGET"] = round(best_delta_range.mid, 3)

        # ROC tuning
        roc_bins = pd.cut(self.df["roc"], bins=[0, 0.1, 0.15, 0.2, 0.3])
        roc_group = self.df.groupby(roc_bins)["score"].mean()
        best_roc_range = roc_group.idxmax()
        suggestions["MIN_ROC"] = round(best_roc_range.left, 2)

        # Yield-to-strike tuning
        yield_bins = pd.cut(self.df["yield_to_strike"], bins=4)
        yield_group = self.df.groupby(yield_bins)["score"].mean()
        best_yield_range = yield_group.idxmax()
        suggestions["MIN_YIELD"] = round(best_yield_range.left, 3)

        # RSI filter tuning
        rsi_bins = pd.cut(self.df["rsi"], bins=[0, 30, 50, 70, 100])
        rsi_group = self.df.groupby(rsi_bins)["score"].mean()
        best_rsi_range = rsi_group.idxmax()
        suggestions["RSI_MAX"] = round(best_rsi_range.right, 0)

        # IV percentile tuning
        iv_bins = pd.cut(self.df["iv_percentile"], bins=5)
        iv_group = self.df.groupby(iv_bins)["score"].mean()
        best_iv_range = iv_group.idxmax()
        suggestions["IV_PREFERRED"] = round(best_iv_range.mid, 2)

        print("[AUTO-TUNER] Suggested Parameters:")
        for k, v in suggestions.items():
            print(f" - {k}: {v}")

        return suggestions