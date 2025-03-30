import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.volatility import Volatility
from utils.earnings import is_near_earnings
from utils.data_loader import get_price_history
from utils.volatility import VolatilityToolkit
import numpy as np

class TradeSignalFeatures:
    def __init__(self, symbol="NVDA"):
        self.symbol = symbol
        self.vol = VolatilityToolkit(symbol)

    def get_features(self, option, side="CALL"):
        price_history = get_price_history(self.symbol, days=21)
        rsi = self.compute_rsi(price_history)
        momentum = price_history[-1] - price_history[-10] if len(price_history) >= 10 else 0
        iv_percentile = self.vol.get_iv_percentile()
        yield_to_strike = option.yield_
        delta = option.delta
        roc = self.vol.calculate_roc(option.strike * option.yield_, option.strike, option.days_to_expiry)
        near_earnings = int(is_near_earnings(self.symbol))

        return {
            "symbol": self.symbol,
            "side": side,
            "strike": option.strike,
            "expiry": option.expiry,
            "delta": round(delta, 3),
            "yield_to_strike": round(yield_to_strike, 4),
            "roc": round(roc, 3),
            "rsi": round(rsi, 2),
            "momentum": round(momentum, 2),
            "iv_percentile": round(iv_percentile, 2),
            "near_earnings": near_earnings
        }

    def compute_rsi(self, prices, period=14):
        deltas = np.diff(prices)
        seed = deltas[:period]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down if down != 0 else 0
        return 100. - 100. / (1. + rs)