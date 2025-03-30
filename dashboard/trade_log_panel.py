import streamlit as st
import pandas as pd
import os

def run():
    st.title("Trade Log Panel")
    st.write("This panel is under construction.")

st.title("Trade Log & Conviction History")

LOG_PATH = "logs/trade_history.csv"

if os.path.exists(LOG_PATH):
    df = pd.read_csv(LOG_PATH)
    st.dataframe(df)
else:
    st.warning("No trade log found yet. Once trades are executed, they will appear here.")
