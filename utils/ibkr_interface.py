from ib_insync import IB, Stock, Option, LimitOrder
from datetime import datetime
from typing import List

class IBKRClient:
    def __init__(self):
        self.ib = IB()
        self.ib.connect('127.0.0.1', 7497, clientId=1)

    def has_underlying(self, symbol: str) -> bool:
        positions = self.ib.positions()
        for pos in positions:
            if pos.contract.symbol == symbol and pos.position > 0:
                return True
        return False

    def buy_underlying(self, symbol: str, quantity: int = 100):
        contract = Stock(symbol, "SMART", "USD")
        self.ib.qualifyContracts(contract)
        order = LimitOrder("BUY", quantity, self.ib.reqMktData(contract).ask)
        self.ib.placeOrder(contract, order)

    def get_open_calls(self, symbol: str):
        positions = self.ib.positions()
        for pos in positions:
            if pos.contract.symbol == symbol and pos.contract.right == "C":
                return pos.contract
        return None

    def get_put_chain(self, symbol: str) -> List:
        contract = Stock(symbol, "SMART", "USD")
        chains = self.ib.reqSecDefOptParams(symbol, "", "STK", contract.conId)
        chain = next(c for c in chains if c.tradingClass == symbol and c.exchange == "SMART")
        expiries = sorted(chain.expirations)[:1]  # nearest expiry
        strikes = sorted(chain.strikes)
        return self._build_options(symbol, expiries, strikes, "P")

    def get_option_chain(self, symbol: str) -> List:
        contract = Stock(symbol, "SMART", "USD")
        chains = self.ib.reqSecDefOptParams(symbol, "", "STK", contract.conId)
        chain = next(c for c in chains if c.tradingClass == symbol and c.exchange == "SMART")
        expiries = sorted(chain.expirations)[:1]
        strikes = sorted(chain.strikes)
        return self._build_options(symbol, expiries, strikes, "C")

    def _build_options(self, symbol: str, expiries: List[str], strikes: List[float], right: str) -> List:
        options = []
        for expiry in expiries:
            for strike in strikes:
                opt = Option(symbol, expiry, strike, right, "SMART")
                self.ib.qualifyContracts(opt)
                ticker = self.ib.reqMktData(opt)
                self.ib.sleep(1)
                bid = ticker.bid or 0
                ask = ticker.ask or 0
                last = ticker.last or 0
                mark = (bid + ask) / 2 if bid and ask else last
                days = (datetime.strptime(expiry, "%Y%m%d") - datetime.now()).days
                yield_ = mark / (strike * 100) if strike else 0
                options.append(type('OptionData', (object,), {
                    'strike': strike,
                    'expiry': expiry,
                    'delta': getattr(ticker.modelGreeks, 'delta', 0),
                    'yield_': yield_,
                    'bid': bid,
                    'ask': ask,
                    'last': last,
                    'days_to_expiry': days
                }))
        return options

    def sell_option(self, option_data):
        contract = Option("NVDA", option_data.expiry, option_data.strike, "C", "SMART")
        self.ib.qualifyContracts(contract)
        order = LimitOrder("SELL", 1, round(option_data.bid or option_data.last or 1.0, 2))
        self.ib.placeOrder(contract, order)

    def sell_put(self, option_data):
        contract = Option("NVDA", option_data.expiry, option_data.strike, "P", "SMART")
        self.ib.qualifyContracts(contract)
        order = LimitOrder("SELL", 1, round(option_data.bid or option_data.last or 1.0, 2))
        self.ib.placeOrder(contract, order)

    def get_historical_data(self, symbol):
        # Fetch historical data for the given symbol
        pass
    
    def get_current_market_data(self, symbol):
        # Fetch current market data for the given symbol
        pass
    
    def place_order(self, symbol, quantity, order_type, price=None):
        # Place an order with the given parameters
        pass
    
    def get_account_balance(self):
        # Fetch account balance
        pass
    
    def get_open_positions(self):
        # Fetch open positions
        pass