import streamlit as st
import pandas as pd
import os
import datetime

def run():
    st.title("Trade Bot Main Dashboard")

    # === STATUS SUMMARY ===
    st.header("Bot Status Overview")

    log_path = "logs/trade_history.csv"
    last_trade_time = "No trades yet."
    trade_count = 0

    if os.path.exists(log_path):
        df = pd.read_csv(log_path)
        if not df.empty:
            trade_count = len(df)
            last_trade_time = df["Date"].iloc[-1]

    st.metric("Total Trades Executed", trade_count)
    st.metric("Last Trade Date", last_trade_time)

    # === SCORE DISTRIBUTIONS ===
    if trade_count > 0:
        st.subheader("Recent Score Distribution")
        score_cols = ["Conviction", "ML Score", "Hybrid Score"]
        for col in score_cols:
            if col in df.columns:
                st.line_chart(df[[col]])

    # === PnL Snapshot ===
        st.subheader("PnL Summary (Completed Trades)")
        if "Actual PnL" in df.columns:
            pnl_df = df[df["Actual PnL"].notnull()]
            st.metric("Total Realized PnL", f"${pnl_df['Actual PnL'].sum():,.2f}")
            st.metric("Avg PnL per Trade", f"${pnl_df['Actual PnL'].mean():.2f}")

    # === RECENT TRADES ===
        st.subheader("Most Recent Trades")
        st.dataframe(df.tail(5))

    # === SLACK STATUS PLACEHOLDER ===
    st.header("Slack Alerts")
    st.success("Discord alerts enabled and configured.")  # Placeholder until live wiring

    # === CONTROLS ===
    st.header("Controls")
    st.button("Retrain ML Model (coming soon)")
    st.button("Run Backtest (coming soon)")

if __name__ == "__main__":
    run()
