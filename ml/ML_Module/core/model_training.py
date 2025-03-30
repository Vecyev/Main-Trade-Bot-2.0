# core/model_training.py

import xgboost as xgb
import optuna
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score


def train_model(X, y, config):
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    def objective(trial):
        params = {
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
            'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
            'subsample': trial.suggest_float('subsample', 0.5, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
            'use_label_encoder': False,
            'eval_metric': 'logloss'
        }
        model = xgb.XGBClassifier(**params)
        model.fit(X_train, y_train)
        preds = model.predict_proba(X_val)[:, 1]
        return roc_auc_score(y_val, preds)

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=config.get('optuna_trials', 25))

    best_model = xgb.XGBClassifier(**study.best_params)
    best_model.fit(X, y)
    joblib.dump(best_model, config['model_path'])
    return best_model


def load_model(model_path):
    return joblib.load(model_path)


def predict_trades(trade_log, features, model, threshold=0.5):
    proba = model.predict_proba(features)[:, 1]
    trade_log['score'] = proba
    trade_log['predicted_label'] = (proba >= threshold).astype(int)
    return trade_log
