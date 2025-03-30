# core/feature_engineering.py

import pandas as pd
import json
import os

def load_old_trade_log(log_path):
    if not os.path.exists(log_path):
        return pd.DataFrame()

    with open(log_path, 'r') as f:
        trades = json.load(f)

    df = pd.DataFrame(trades)
    return df


def generate_features(df):
    # Ensure required columns exist
    required = [
        "delta", "roc", "rsi", "momentum",
        "yield_to_strike", "iv_percentile", "near_earnings"
    ]
    df = df.dropna(subset=required)

    X = df[required].copy()

    # Binary label based on score if present
    if "score" in df.columns:
        threshold = df["score"].quantile(0.7)
        y = (df["score"] >= threshold).astype(int)
    else:
        y = None

    return X, y
