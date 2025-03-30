from strategy.manager import StrategyManager
from utils.ibkr_interface import IBKRClient

def simulate_backtest():
    print("[BACKTEST] Running simulated strategy loop")
    ibkr = IBKRClient()
    manager = StrategyManager(ibkr, symbol="NVDA", cost_basis=650)
    for i in range(30):  # Simulate 30 trading days
        print(f"[DAY {i+1}]")
        manager.run()

if __name__ == "__main__":
    simulate_backtest()