from utils.smart_executor import SmartExecutor
from ib_insync import Option, LimitOrder

class TradeExecutor:
    def __init__(self, ibkr_client):
        self.ibkr = ibkr_client
        self.smart_exec = SmartExecutor(ibkr_client)

    def write_calls(self, symbol, options):
        for option in options:
            contract = Option(symbol, option.expiry.replace("-", ""), option.strike, "C", "SMART")
            self.ibkr.ib.qualifyContracts(contract)
            self.smart_exec.place_limit_order(contract, quantity=1, action="SELL")
            self.ibkr.sell_option(option)