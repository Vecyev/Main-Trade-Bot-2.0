from datetime import datetime
from strategy.volatility_model import VolatilityRegime
from strategy.trade_filter import TradeFilter
from strategy.execution import TradeExecutor
from config import *
from utils.earnings import is_near_earnings
from models.trade_model import TradeModel

class CoveredCallStrategy:
    def __init__(self, ibkr_client, symbol, cost_basis=650):
        self.symbol = symbol
        self.ibkr = ibkr_client
        self.vol_model = VolatilityRegime(self.symbol)
        self.filter = TradeFilter(self.symbol, cost_basis)
        self.executor = TradeExecutor(self.ibkr)
        self.model = TradeModel()
        self.signal_engine = TradeSignalFeatures(symbol)
        self.scorer = TradeScorer(symbol)

    def run(self):
        if is_near_earnings(self.symbol):
            print("[EARNINGS] Skipping covered call due to upcoming earnings.")
            return

        vol_regime = self.vol_model.detect_regime()
        if not self.ibkr.has_underlying(self.symbol):
            self.ibkr.buy_underlying(self.symbol)

        open_call = self.ibkr.get_open_calls(self.symbol)
        if open_call and open_call.days_to_expiry > ROLL_DTE_THRESHOLD:
            return

        chain = self.ibkr.get_option_chain(self.symbol)
        
from utils.conviction import compute_conviction_score

# Define weights for scoring (can be moved to config)
conviction_weights = {
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

# Define conviction override rules
conviction_overrides = {
    "sizing": {"threshold": 90},
    "strike_distance": {"threshold": 92},
    "premium_yield": {"threshold": 95}
}

        selected = self.filter.select_strikes(chain)

        # Conviction scoring example
        model = TradeModel()
        features = {
            "delta": opt.delta,
            "roc": opt.roc,
            "rsi": opt.rsi,
            "momentum": opt.momentum,
            "yield_to_strike": opt.yield_to_strike,
            "iv_percentile": opt.iv_percentile,
            "near_earnings": int(opt.near_earnings),
        }
        opt.ml_score = model.predict_score(features)
        hybrid_score = 0.7 * opt.ml_score + 0.3 * (opt.conviction_score / 100)
        if hybrid_score < 0.15:
            continue
        
        for opt in selected:
            features = {
                'DTE': opt.dte_score,
                'Strike Distance': opt.strike_dist_score,
                'Premium Yield': opt.yield_score,
                'Delta': opt.delta_score,
                'IV Rank': opt.iv_rank_score,
                'RSI': opt.rsi_score,
                'Earnings Proximity': 1 if not opt.near_earnings else 0,
                'Cost Basis Awareness': 1 if opt.strike > self.filter.cost_basis else 0,
                'Sizing': 1  # assume valid unless flagged
            }
            result = compute_conviction_score(features, conviction_weights, conviction_overrides)
            opt.conviction_score = result['score']
            opt.overrides = result['overrides']

        if selected:
            self.executor.write_calls(self.symbol, selected)
            for opt in selected:
                signal = self.signal_engine.get_features(opt, side="CALL")
                score = self.model.predict_score(signal)

                # Combine ML prediction and conviction into a hybrid score
                hybrid_score = 0.7 * score + 0.3 * (opt.conviction_score / 100)

                if hybrid_score < 0.15:
                    continue

                if score is None:
                    continue
                premium = round(opt.strike * opt.yield_, 2)
                self.scorer.score_and_log_trade(opt, premium, side="CALL")
                send_discord_alert(f'[CALL] Sold NVDA call {opt.strike} exp {opt.expiry}')

                
                post_trade_to_webhook({
                    "type": "Sell Call",
                    "strike": opt.strike,
                    "premium": premium,
                    "dte": opt.dte,
                    "conviction": opt.conviction_score,
                    "ml_score": opt.ml_score,
                    "hybrid_score": hybrid_score,
                    "timestamp": datetime.now().isoformat()
                })
    
                log_trade({
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Type": "Sell Call",
            "Strike": opt.strike,
            "Premium": premium,
            "DTE": opt.dte,
            "Conviction": opt.conviction_score,
            "Overrides": ", ".join(opt.overrides),
            "ML Score": opt.ml_score,
            "Hybrid Score": hybrid_score
        })
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Type": "Sell Call",
                    "Strike": opt.strike,
                    "Premium": premium,
                    "DTE": opt.dte,
                    "Conviction": opt.conviction_score,
                    "Overrides": ", ".join(opt.overrides)
                })
