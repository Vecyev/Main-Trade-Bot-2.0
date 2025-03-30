import pandas as pd
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import joblib
import os

class TradeModel:
    def __init__(self, log_path="logs/trades.json", model_path="models/trade_model.pkl"):
        self.log_path = log_path
        self.model_path = model_path
        self.model = None

    def load_data(self):
        if not os.path.exists(self.log_path):
            return pd.DataFrame()

        with open(self.log_path, "r") as f:
            trades = json.load(f)

        df = pd.DataFrame(trades)
        df = df.dropna(subset=["score"])
        return df

    def train_model(self):
        df = self.load_data()
        if df.empty or len(df) < 20:
            print("[ML] Not enough data to train.")
            return None

        features = ["delta", "roc", "rsi", "momentum", "yield_to_strike", "iv_percentile", "near_earnings"]
        X = df[features]
        y = df["score"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        print(f"[ML] Model R² score: {r2_score(y_test, preds):.2f}")

        os.makedirs("models", exist_ok=True)
        joblib.dump(model, self.model_path)
        self.model = model
        return model

    def load_model(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        return self.model

    def predict_score(self, feature_dict):
        if not self.model:
            self.load_model()

        if not self.model:
            print("[ML] No trained model available.")
            return None

        features = ["delta", "roc", "rsi", "momentum", "yield_to_strike", "iv_percentile", "near_earnings"]
        X = pd.DataFrame([feature_dict])[features]
        return self.model.predict(X)[0]