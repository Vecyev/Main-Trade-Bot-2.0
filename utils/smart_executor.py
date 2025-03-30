from ib_insync import LimitOrder

class SmartExecutor:
    def __init__(self, ibkr_client):
        self.ibkr = ibkr_client

    def place_limit_order(self, contract, quantity, action="SELL", max_attempts=3):
        market_data = self.ibkr.ib.reqMktData(contract, "", False, False)
        self.ibkr.ib.sleep(2)

        bid = market_data.bid
        ask = market_data.ask
        mark = (bid + ask) / 2 if bid and ask else market_data.last or 0

        if not mark:
            print("[SMART ORDER] No valid market price available.")
            return

        limit_price = round(mark * 0.98, 2)
        print(f"[SMART ORDER] Placing limit {action} order at ${limit_price} (bid={bid}, ask={ask})")

        order = LimitOrder(action, quantity, limit_price)
        trade = self.ibkr.ib.placeOrder(contract, order)

        for attempt in range(max_attempts):
            self.ibkr.ib.sleep(2)
            if trade.orderStatus.status == "Filled":
                print(f"[ORDER] Filled at attempt {attempt+1}")
                return trade
            else:
                print(f"[RETRY] Attempt {attempt+1} failed, adjusting limit...")
                limit_price *= 0.99  # tighten price slightly
                trade = self.ibkr.ib.placeOrder(contract, LimitOrder(action, quantity, round(limit_price, 2)))

        print("[ORDER] Max attempts reached without fill.")
        return trade