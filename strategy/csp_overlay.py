from config import DELTA_TARGET, MIN_YIELD
from utils.logger import logger
from utils.volatility import VolatilityToolkit
from utils.pnl_tracker import PnLTracker
from utils.trade_scorer import TradeScorer
from utils.trade_model import TradeModel
from utils.signals import TradeSignalFeatures
from utils.discord_alerts import send_discord_alert
from utils.smart_executor import SmartExecutor
from ib_insync import Option
from utils.earnings import is_near_earnings

class CSPOverlay:
    def __init__(self, ibkr_client, symbol):
        self.ibkr = ibkr_client
        self.symbol = symbol
        self.pnl = PnLTracker()
        self.smart_exec = SmartExecutor(ibkr_client)
        self.model = TradeModel()
        self.signal_engine = TradeSignalFeatures(symbol)
        self.scorer = TradeScorer(symbol)
        self.vol = VolatilityToolkit(symbol)
        self.min_roc = 0.10  # 10% annualized minimum ROC

    def run(self):
        if self.ibkr.get_open_calls(self.symbol):
            logger.info("[CSP] Skipping CSP: Call already open")
            return

        chain = self.ibkr.get_put_chain(self.symbol)
        filtered = []
        for opt in chain:
            roc = self.vol.calculate_roc(opt.strike * opt.yield_, opt.strike, opt.days_to_expiry)
            if abs(opt.delta - DELTA_TARGET) < 0.1 and opt.yield_ >= MIN_YIELD and roc >= self.min_roc:
                filtered.append((opt, roc))

        if not filtered:
            logger.info("[CSP] No puts met ROC or delta criteria")
            return

        sorted_trades = sorted(filtered, key=lambda x: -x[1])
        for candidate, roc in sorted_trades:
            signal = self.signal_engine.get_features(candidate, side="PUT")
            score = self.model.predict_score(signal)
            if score is not None and score >= 0.15:
                best = candidate
                break
        else:
            logger.info("[CSP] No trades passed ML filter")
            return
        roc = self.vol.calculate_roc(best.strike * best.yield_, best.strike, best.days_to_expiry)
        premium = round(best.strike * best.yield_, 2)

        logger.info(f"[SIMULATED CSP] Selling put: {self.symbol} {best.strike} @ {best.expiry}, "
                    f"delta={best.delta:.2f}, yield={best.yield_:.3f}, ROC={roc:.2%}, premium=${premium}")
        contract = Option(self.symbol, best.expiry.replace("-", ""), best.strike, "P", "SMART")
        self.ibkr.ib.qualifyContracts(contract)
        self.smart_exec.place_limit_order(contract, 1, action="SELL")
        self.ibkr.sell_put(best)
        send_discord_alert(f'[CSP] Sold NVDA put {best.strike} exp {best.expiry}')
        self.pnl.record_trade(best, premium)
        self.scorer.score_and_log_trade(best, premium, side="PUT")
        self.pnl.report()