# ml_tradebot_template/main.py

from core.backtest_engine import run_backtest_simulation
from core.feature_engineering import generate_features
from core.model_training import train_model, load_model, predict_trades
from core.data_utils import load_trade_data
from core.config import config


def main():
    # Load raw historical trade data
    raw_data = load_trade_data(config['data_path'])

    # Backtest engine to simulate trades
    trade_log = run_backtest_simulation(raw_data, config['strategy_params'])

    # Generate features and labels for ML
    features, labels = generate_features(trade_log)

    # Train or load the ML model
    if config['train_model']:
        model = train_model(features, labels, config)
    else:
        model = load_model(config['model_path'])

    # Predict on trades
    trade_log = predict_trades(trade_log, features, model, config['predict_threshold'])

    # Output results
    print("Top 5 scored trades:")
    print(trade_log[['trade_id', 'score', 'predicted_label']].head())


if __name__ == "__main__":
    main()
