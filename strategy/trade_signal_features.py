# strategy/trade_signal_features.py
import logging

logger = logging.getLogger(__name__)

class TradeSignalFeatures:
    def __init__(self, symbol: str):
        self.symbol = symbol

    def get_features(self, option, side: str = "CALL") -> dict:
        """
        Returns a dictionary of features extracted from the option and market data.
        In production, integrate with live data feeds and technical analysis libraries.
        """
        try:
            features = {
                "delta": getattr(option, "delta", 0),
                "yield_to_strike": getattr(option, "yield_", 0),
                "roc": getattr(option, "roc", 0),
                "rsi": getattr(option, "rsi", 50),  # neutral RSI if not provided
                "momentum": getattr(option, "momentum", 0),
                "iv_percentile": getattr(option, "iv_percentile", 0.5),
                "near_earnings": int(getattr(option, "near_earnings", False))
            }
            logger.debug(f"Extracted features for option: {features}")
            return features
        except Exception as e:
            logger.error(f"Error extracting features for {self.symbol} option: {e}")
            return {}
