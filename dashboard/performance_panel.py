import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

def run():
    st.title("Performance Analytics")

    LOG_PATH = "logs/trade_history.csv"

    if not os.path.exists(LOG_PATH):
        st.warning("No trade data available yet.")
    else:
        df = pd.read_csv(LOG_PATH)
        df["Date"] = pd.to_datetime(df["Date"])
        df.sort_values("Date", inplace=True)

        st.subheader("Conviction Score Over Time")
        fig, ax = plt.subplots()
        ax.plot(df["Date"], df["Conviction"], marker='o')
        ax.set_ylabel("Conviction Score")
        ax.set_xlabel("Date")
        st.pyplot(fig)

        st.subheader("Premium Collected Over Time")
        fig2, ax2 = plt.subplots()
        df.groupby("Date")["Premium"].sum().plot(kind="bar", ax=ax2)
        ax2.set_ylabel("Premium ($)")
        st.pyplot(fig2)

        st.subheader("Average Conviction vs. Premium")
        avg_df = df.groupby("Type").agg({"Conviction": "mean", "Premium": "mean"})
        st.dataframe(avg_df)

        st.subheader("Trade Frequency by Type")
        st.bar_chart(df["Type"].value_counts())

run()
