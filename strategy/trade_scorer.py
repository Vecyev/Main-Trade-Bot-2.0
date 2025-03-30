# strategy/trade_scorer.py

import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import risk adjustment function from your risk module.
from utils.risk_module import adjust_for_risk
# Import your conviction logic.
from utils.conviction import compute_conviction_score

logger = logging.getLogger(__name__)

class TradeScorer:
    """
    An advanced trade scorer that integrates ML predictions, conviction scores,
    and risk adjustments. It logs trade details in a structured format and supports
    both synchronous and asynchronous execution.
    """

    def __init__(self, symbol: str, ml_model: Optional[Any] = None,
                 risk_params: Optional[Dict[str, Any]] = None,
                 conviction_weights: Optional[Dict[str, float]] = None,
                 override_config: Optional[Dict[str, Any]] = None):
        """
        Args:
            symbol (str): Trading symbol (e.g., "NVDA").
            ml_model: Optional ML model for predicting trade scores.
            risk_params (dict): Parameters for risk adjustment.
            conviction_weights (dict): Weights for computing the conviction score.
            override_config (dict): Override rules for conviction logic.
        """
        self.symbol = symbol
        self.ml_model = ml_model
        self.risk_params = risk_params or {}
        self.conviction_weights = conviction_weights or {
            "DTE": 0.15,
            "Strike Distance": 0.15,
            "Premium Yield": 0.15,
            "Delta": 0.10,
            "IV Rank": 0.10,
            "RSI": 0.10,
            "Earnings Proximity": 0.10,
            "Cost Basis Awareness": 0.10,
            "Sizing": 0.05,
        }
        self.override_config = override_config or {
            "sizing": {"threshold": 90},
            "strike_distance": {"threshold": 92},
            "premium_yield": {"threshold": 95}
        }

    async def score_and_log_trade_async(self, option, premium: float, side: str = "CALL",
                                          additional_features: Optional[Dict[str, float]] = None) -> float:
        """
        Asynchronously computes the trade score and logs trade details.
        """
        return await asyncio.to_thread(
            self.score_and_log_trade, option, premium, side, additional_features
        )

    def score_and_log_trade(self, option, premium: float, side: str = "CALL",
                            additional_features: Optional[Dict[str, float]] = None) -> float:
        """
        Synchronously computes the trade score by combining:
         - An ML prediction (if available)
         - Conviction scoring via compute_conviction_score
         - A risk adjustment via adjust_for_risk
        Logs all details in a structured format.

        Args:
            option: The trade/option object (expected to have attributes like strike, expiry, delta).
            premium (float): Trade premium or execution price.
            side (str): "CALL", "PUT", etc.
            additional_features (dict): Optional additional numeric features.

        Returns:
            final_score (float): The final adjusted trade score.
        """
        # 1. Gather base features
        base_features = self._gather_base_features(option, side, premium)
        if additional_features:
            base_features.update(additional_features)

        # 2. ML Prediction (if ml_model is provided)
        ml_score = 0.0
        if self.ml_model:
            ml_score = self._predict_ml_score(base_features)
        
        # 3. Conviction Score using our conviction module
        conviction_result = compute_conviction_score(base_features, self.conviction_weights, self.override_config)
        conviction_score = conviction_result.get("score", 0)

        # 4. Combine ML prediction and conviction score (weighted, e.g., 70%-30%)
        raw_score = 0.7 * ml_score + 0.3 * (conviction_score / 100.0)

        # 5. Adjust the combined score for risk using your risk module
        final_score = adjust_for_risk(raw_score, option, self.risk_params)

        # 6. Log trade details
        self._log_trade(option, premium, side, ml_score, conviction_score, final_score)

        return final_score

    def _gather_base_features(self, option, side: str, premium: float) -> Dict[str, float]:
        """
        Extracts a dictionary of base features from the option object.
        """
        features = {
            "strike": float(getattr(option, "strike", 0.0)),
            "delta": float(getattr(option, "delta", 0.0)),
            "premium": premium,
            # Convert expiry to a numeric value (e.g., timestamp) if needed
            "expiry": float(getattr(option, "expiry", 0.0)),
            "side": 1.0 if side.upper() == "CALL" else 0.0,
        }
        return features

    def _predict_ml_score(self, features: Dict[str, float]) -> float:
        """
        Predicts a 0-1 score from the given features using the ML model.
        Adjusts the feature ordering as needed by your model.
        """
        try:
            sorted_keys = sorted(features.keys())
            X = np.array([[features[k] for k in sorted_keys]], dtype=float)
            probas = self.ml_model.predict_proba(X)
            # Assumes the positive class probability is at index 1
            return float(probas[0][1])
        except Exception as e:
            logger.error(f"[TradeScorer] ML prediction failed: {e}")
            return 0.0

    def _log_trade(self, option, premium: float, side: str, ml_score: float,
                   conviction_score: float, final_score: float):
        """
        Logs trade details in a structured format.
        """
        log_message = (
            f"[TradeScorer] {side.upper()} trade for {self.symbol} | "
            f"Strike={getattr(option, 'strike', 'N/A')}, "
            f"Expiry={getattr(option, 'expiry', 'N/A')}, "
            f"Delta={getattr(option, 'delta', 0.0):.2f}, "
            f"Premium={premium:.2f}, "
            f"ML Score={ml_score:.3f}, Conviction={conviction_score:.2f}, "
            f"Final Adjusted Score={final_score:.3f}"
        )
        logger.info(log_message)
