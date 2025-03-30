import streamlit as st
import pandas as pd
import os
import json
from utils.trade_model import TradeModel

def run():
    st.title("ML Panel")
    st.write("This panel is under construction.")

st.subheader("ML Trade Scoring Insights")

try:
    with open("logs/trades.json", "r") as f:
        trades = json.load(f)
    df = pd.DataFrame(trades)
    df["date"] = pd.to_datetime(df["date"])
    df.sort_values("date", ascending=False, inplace=True)

    st.metric("Trades Logged", len(df))

    model = TradeModel()
    model.load_model()

    df["predicted_score"] = df.apply(lambda row: model.predict_score(row.to_dict()), axis=1)
    st.write("Recent Trades with Predicted Score:")
    st.dataframe(df[["date", "side", "strike", "roc", "score", "predicted_score"]].head(10))

    st.write("Actual vs Predicted Score")
    st.scatter_chart(df[["score", "predicted_score"]])

    if st.button("Retrain Model Now"):
        model.train_model()
        st.success("Model retrained.")

except Exception as e:
    st.warning(f"ML dashboard load failed: {e}")