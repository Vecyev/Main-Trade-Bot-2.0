# utils/pnl_tracker.py
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

logger = logging.getLogger(__name__)

@dataclass
class TradeRecord:
    """
    Represents a single trade for PnL tracking.
    For a short option, 'premium' is typically a credit received.
    """
    symbol: str
    strike: float
    expiry: str
    side: str          # "PUT", "CALL", or "UNDERLYING", etc.
    quantity: int
    entry_price: float # The price (premium) at which the position was opened
    entry_time: datetime = field(default_factory=datetime.utcnow)
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None

    @property
    def is_open(self) -> bool:
        return self.exit_price is None

    def unrealized_pnl(self, current_price: float) -> float:
        """
        Calculate an approximate unrealized PnL based on the current market price of the option.
        For a short option, PnL is (entry_price - current_price) * quantity * 100 (assuming 100 shares/contract).
        For a long option, it would be (current_price - entry_price).
        Adjust logic as needed for your strategy.
        """
        if self.side in ("PUT", "CALL"):  # short options in this example
            return (self.entry_price - current_price) * self.quantity * 100
        else:
            # For underlying or other trade types, adapt accordingly
            return 0.0

    def realized_pnl(self) -> float:
        """
        If the trade is closed, calculates realized PnL. 
        For a short option: (entry_price - exit_price) * quantity * 100.
        """
        if not self.is_open and self.exit_price is not None:
            if self.side in ("PUT", "CALL"):
                return (self.entry_price - self.exit_price) * self.quantity * 100
            else:
                return 0.0
        return 0.0


class PnLTracker:
    """
    Institutional-grade PnL tracker that logs trades, computes realized/unrealized PnL,
    and provides a summary report. In a real system, you might store these records in a
    database or external service.
    """

    def __init__(self):
        # Store all trades in memory. Extend with DB or persistent storage if needed.
        self.trades: List[TradeRecord] = []

    def record_trade(self, option, premium: float, side: str = "PUT", quantity: int = 1):
        """
        Record a new trade. For a short put, 'premium' is the credit received.
        'option' is expected to have .symbol, .strike, .expiry, etc.
        """
        # Create a TradeRecord from the option data
        trade = TradeRecord(
            symbol=option.symbol,
            strike=option.strike,
            expiry=option.expiry,
            side=side,
            quantity=quantity,
            entry_price=premium
        )
        self.trades.append(trade)

        logger.info(f"[PnLTracker] Recorded trade: {trade.side} {trade.symbol} "
                    f"@ strike {trade.strike}, expiry {trade.expiry}, "
                    f"premium={trade.entry_price:.2f}, qty={trade.quantity}")

    def close_trade(self, option, exit_price: float):
        """
        Mark a trade as closed by setting an exit_price and exit_time.
        If multiple trades match, closes the most recent open one by default.
        """
        # In practice, you might have logic to match specific trade IDs or timestamps.
        open_trades = [t for t in self.trades
                       if t.symbol == option.symbol and t.strike == option.strike
                       and t.expiry == option.expiry and t.is_open]
        if not open_trades:
            logger.warning(f"[PnLTracker] No open trade found for {option.symbol} {option.strike} {option.expiry}")
            return

        # Close the most recent matching open trade
        trade_to_close = open_trades[-1]
        trade_to_close.exit_price = exit_price
        trade_to_close.exit_time = datetime.utcnow()

        realized = trade_to_close.realized_pnl()
        logger.info(f"[PnLTracker] Closed trade: {trade_to_close.side} {trade_to_close.symbol} "
                    f"strike {trade_to_close.strike}, expiry {trade_to_close.expiry}, "
                    f"exit_price={exit_price:.2f}, realized PnL={realized:.2f}")

    def report(self):
        """
        Logs a summary of open/closed trades and realized/unrealized PnL.
        Extend this for more detailed risk or PnL breakdowns.
        """
        open_positions = [t for t in self.trades if t.is_open]
        closed_positions = [t for t in self.trades if not t.is_open]

        realized_pnl = sum(t.realized_pnl() for t in closed_positions)
        # Unrealized requires current option prices. For demonstration, we assume 0.0
        # In production, you'd pass in or fetch the current price for each option to compute properly.
        unrealized_pnl = 0.0

        logger.info("[PnLTracker] ===== PnL Report =====")
        logger.info(f"[PnLTracker] Open Positions: {len(open_positions)}")
        for t in open_positions:
            logger.info(f"  - {t.side} {t.symbol} strike {t.strike} exp {t.expiry}, "
                        f"entry={t.entry_price:.2f}, qty={t.quantity}")

        logger.info(f"[PnLTracker] Closed Positions: {len(closed_positions)}")
        logger.info(f"[PnLTracker] Total Realized PnL: {realized_pnl:.2f}")
        logger.info(f"[PnLTracker] Estimated Unrealized PnL: {unrealized_pnl:.2f}")
        logger.info("[PnLTracker] ======================")
