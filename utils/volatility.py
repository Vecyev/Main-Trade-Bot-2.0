import yfinance as yf
import numpy as np
from datetime import datetime, timedelta

class VolatilityToolkit:
    def __init__(self, symbol="NVDA"):
        self.symbol = symbol

    def get_iv_percentile(self, days=252):
        ticker = yf.Ticker(self.symbol)
        hist = ticker.history(period="1y")
        if "Close" not in hist or hist.empty:
            return 0.5  # fallback

        hist['returns'] = np.log(hist['Close'] / hist['Close'].shift(1))
        hist.dropna(inplace=True)
        hist['vol'] = hist['returns'].rolling(window=21).std() * np.sqrt(252)

        current_vol = hist['vol'].iloc[-1]
        iv_rank = np.sum(hist['vol'] < current_vol) / len(hist['vol'])
        return round(iv_rank, 2)

    def calculate_roc(self, premium, strike, days_to_expiry):
        capital = strike * 100
        annualized_yield = (premium * 100) / capital * (365 / days_to_expiry)
        return round(annualized_yield, 3)