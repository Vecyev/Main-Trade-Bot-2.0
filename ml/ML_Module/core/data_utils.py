# core/data_utils.py

import pandas as pd
import os

def load_trade_data(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No data found at {path}")
    return pd.read_csv(path)
