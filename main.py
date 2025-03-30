import logging
import sys
import os
import signal
import yaml
from strategy.manager import StrategyManager
from utils.ibkr_interface import IBKRClient
from ml.model import RegressionModel  # Assuming a machine learning model module

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'path_to_utils_parent')))

def load_config(config_file="config.yaml"):
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)
    else:
        return {
            "symbol": os.getenv("TRADE_SYMBOL", "NVDA"),
            "cost_basis": float(os.getenv("COST_BASIS", 650)),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "ml_model_path": os.getenv("ML_MODEL_PATH", "model.pkl")
        }

def setup_logging(log_level):
    logging.basicConfig(level=getattr(logging, log_level.upper(), None),
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.info("Logging setup complete.")

def signal_handler(signal, frame):
    logging.info("Received termination signal. Shutting down gracefully...")
    sys.exit(0)

def main():
    config = load_config()
    setup_logging(config.get("log_level", "INFO"))
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logging.info("Initializing IBKRClient...")
        ibkr = IBKRClient()
        logging.info("Initializing StrategyManager...")
        manager = StrategyManager(ibkr, symbol=config["symbol"], cost_basis=config["cost_basis"])
        
        logging.info("Loading Machine Learning Model...")
        model = RegressionModel(config["ml_model_path"])
        manager.set_ml_model(model)  # Assuming StrategyManager can accept an ML model
        
        logging.info("Running StrategyManager...")
        manager.run()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()