# core/backtest_engine.py

import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import xgboost as xgb
import optuna
import joblib
import asyncio

# Import configuration from core/config.py
from core.config import config

# Setup institutional-grade logging
logger = logging.getLogger(__name__)
logger.setLevel(config.get("LOG_LEVEL", "INFO"))
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Import additional modules
from sklearn.metrics import accuracy_score
from utils.pnl_tracker import PnLTracker

class BacktestEngine:
    """
    An institutional-grade backtest engine that:
      - Loads data from config['data_path']
      - Trains an XGBoost model (with optional hyperparameter tuning via Optuna)
      - Runs backtests by applying predictions to simulate trade signals
      - Simulates position entry/exit and computes PnL via a PnL tracker
      - Logs performance metrics and workflow details
    """

    def __init__(self):
        self.data_path = config.get("data_path", "data/sample_trades.csv")
        self.model_path = config.get("model_path", "models/xgb_model.pkl")
        self.train_model_flag = config.get("train_model", True)
        self.predict_threshold = config.get("predict_threshold", 0.5)
        self.strategy_params = config.get("strategy_params", {})
        self.optuna_trials = config.get("optuna_trials", 25)

        self.model = None

        logger.info("[BacktestEngine] Initialized with configuration:")
        logger.info(f"  data_path={self.data_path}")
        logger.info(f"  model_path={self.model_path}")
        logger.info(f"  train_model={self.train_model_flag}")
        logger.info(f"  predict_threshold={self.predict_threshold}")
        logger.info(f"  optuna_trials={self.optuna_trials}")

    def load_data(self) -> pd.DataFrame:
        """
        Loads historical trade data from CSV.
        Expects a 'label' column for training and a 'price' column for simulation.
        """
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"[BacktestEngine] Data file not found: {self.data_path}")

        df = pd.read_csv(self.data_path)
        logger.info(f"[BacktestEngine] Loaded {len(df)} rows from {self.data_path}")
        return df

    def train_model(self, df: pd.DataFrame):
        """
        Trains an XGBoost classifier on the provided DataFrame.
        Assumes a 'label' column exists for the target.
        """
        logger.info("[BacktestEngine] Starting model training...")
        if 'label' not in df.columns:
            raise ValueError("[BacktestEngine] 'label' column missing in dataset for training.")

        X = df.drop('label', axis=1)
        y = df['label']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=True, random_state=42
        )

        model_params = {
            "n_estimators": 100,
            "max_depth": 4,
            "learning_rate": 0.1,
            "use_label_encoder": False,
            "eval_metric": "logloss"
        }
        model_params.update(self.strategy_params)

        # Optional hyperparameter tuning via Optuna
        if self.optuna_trials > 0:
            self.run_optuna_tuning(X_train, y_train)

        self.model = xgb.XGBClassifier(**model_params)
        self.model.fit(X_train, y_train)

        preds = self.model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds, zero_division=0)
        rec = recall_score(y_test, preds, zero_division=0)
        logger.info(f"[BacktestEngine] Model training complete. "
                    f"Test Accuracy={acc:.3f}, Precision={prec:.3f}, Recall={rec:.3f}")

        joblib.dump(self.model, self.model_path)
        logger.info(f"[BacktestEngine] Model saved to {self.model_path}")

    def run_optuna_tuning(self, X_train: pd.DataFrame, y_train: pd.Series):
        """
        Uses Optuna to tune hyperparameters for the XGBoost model.
        """
        logger.info("[BacktestEngine] Starting Optuna hyperparameter tuning...")

        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 300),
                "max_depth": trial.suggest_int("max_depth", 2, 8),
                "learning_rate": trial.suggest_float("learning_rate", 1e-3, 1e-1, log=True),
                "eval_metric": "logloss",
                "use_label_encoder": False
            }
            model = xgb.XGBClassifier(**params)
            model.fit(X_train, y_train)
            preds = model.predict(X_train)
            return accuracy_score(y_train, preds)

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=self.optuna_trials)
        logger.info(f"[BacktestEngine] Optuna best params: {study.best_params}, Best score: {study.best_value:.3f}")

    def load_model(self):
        """
        Loads a pre-trained model from disk.
        """
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"[BacktestEngine] Model file not found: {self.model_path}")

        self.model = joblib.load(self.model_path)
        logger.info(f"[BacktestEngine] Model loaded from {self.model_path}")

    async def run_backtest(self):
        """
        Asynchronously runs the backtesting workflow:
          - Loads the model (if not in memory)
          - Loads the dataset
          - Applies model predictions using a threshold to simulate trade signals
          - Simulates trade entry/exit and computes PnL using a PnL tracker
          - Logs performance metrics and generates a PnL report
        """
        if self.model is None:
            logger.info("[BacktestEngine] Model not in memory; loading from disk...")
            self.load_model()

        df = self.load_data()
        if 'label' in df.columns:
            X = df.drop('label', axis=1)
            y = df['label']
        else:
            logger.warning("[BacktestEngine] No 'label' column found. Using entire dataset as features only.")
            X = df
            y = None

        # Predict probabilities
        probas = self.model.predict_proba(X)[:, 1]
        predictions = (probas >= self.predict_threshold).astype(int)

        if y is not None:
            acc = accuracy_score(y, predictions)
            logger.info(f"[BacktestEngine] Backtest Accuracy={acc:.3f} with threshold={self.predict_threshold}")

        # -----------------------------
        # Integrated Trade Simulation
        # -----------------------------
        # We assume the DataFrame contains a 'price' column representing the market price at each time step.
        if "price" in df.columns:
            from utils.pnl_tracker import PnLTracker
            pnl_tracker = PnLTracker()

            # Create a dummy trade class to simulate trade records.
            class DummyTrade:
                def __init__(self, symbol, strike, expiry, side, entry_price, quantity=1):
                    self.symbol = symbol
                    self.strike = strike
                    self.expiry = expiry
                    self.side = side
                    self.entry_price = entry_price
                    self.quantity = quantity

            # Simulate trades:
            # For each row (except the last), if the prediction is 1, simulate entering a trade at that price,
            # and exit the trade in the next time step.
            for i in range(len(df) - 1):
                if predictions[i] == 1:
                    entry_price = df.iloc[i]["price"]
                    exit_price = df.iloc[i + 1]["price"]
                    # For simulation, use a dummy expiry (e.g., current date + 1 day)
                    expiry = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
                    trade = DummyTrade(
                        symbol="SIM", strike=entry_price, expiry=expiry, side="LONG", entry_price=entry_price, quantity=1
                    )
                    pnl_tracker.record_trade(trade, entry_price, side="LONG", quantity=1)
                    pnl_tracker.close_trade(trade, exit_price)
            pnl_tracker.report()
        else:
            logger.warning("[BacktestEngine] 'price' column not found in dataset; skipping trade simulation.")

        logger.info("[BacktestEngine] Backtest run complete. (Simulated trade signals and PnL computed.)")

    def run(self):
        """
        Main synchronous entry point for the backtest workflow.
        It loads data, optionally trains the model, then runs the backtest asynchronously.
        """
        logger.info("[BacktestEngine] Starting backtest workflow...")
        df = self.load_data()

        if self.train_model_flag:
            self.train_model(df)
        else:
            logger.info("[BacktestEngine] Skipping training (train_model=False).")

        asyncio.run(self.run_backtest())
        logger.info("[BacktestEngine] Workflow complete.")


# Standalone usage example
if __name__ == "__main__":
    def main():
        engine = BacktestEngine()
        engine.run()

    main()
