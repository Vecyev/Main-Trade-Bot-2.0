# strategy/trade_filter.py

class TradeFilter:
    def __init__(self, symbol, cost_basis):
        self.symbol = symbol
        self.cost_basis = cost_basis

    def select_strikes(self, chain):
        """
        Given an option chain, return a filtered list of 'option' objects
        that meet your strategy criteria. For now, we just return them all.
        """
        # In reality, you'd filter based on cost basis, delta, expiry, etc.
        return chain
