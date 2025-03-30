import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from utils.conviction import compute_conviction_score

def run():
    import streamlit as st
    st.title("Conviction Score Panel")
    st.write("This panel displays conviction scores.")

    # Example usage of compute_conviction_score
    score = compute_conviction_score()
    st.write(f"Computed Conviction Score: {score}")

st.title("Conviction Score Evaluator")

# Example trade input
st.header("Trade Parameters")

dte = st.slider("Days to Expiry (DTE)", 0, 100, 14)
strike_dist = st.slider("Strike Distance (% above spot)", 0.0, 0.5, 0.2)
premium_yield = st.slider("Premium Yield (%)", 0.0, 0.05, 0.02)
delta = st.slider("Delta", -1.0, 0.0, -0.25)
iv_rank = st.slider("IV Rank", 0, 100, 60)
rsi = st.slider("RSI", 0, 100, 50)
earnings = st.checkbox("Earnings Within 5 Days?", value=False)
cost_above = st.checkbox("Strike Above Cost Basis?", value=True)
qty = st.slider("Contracts (sizing)", 1, 10, 2)

# Prepare input dict
features = {
    "DTE": 1 if 5 <= dte <= 21 else 0.5 if dte <= 35 else 0,
    "Strike Distance": 1 if 0.15 <= strike_dist <= 0.25 else 0.5 if 0.10 <= strike_dist <= 0.30 else 0,
    "Premium Yield": 1 if premium_yield >= 0.015 else 0.5 if premium_yield >= 0.01 else 0,
    "Delta": 1 if -0.30 <= delta <= -0.10 else 0.5 if -0.35 <= delta <= -0.05 else 0,
    "IV Rank": 1 if 50 <= iv_rank <= 80 else 0.5 if 40 <= iv_rank <= 90 else 0,
    "RSI": 1 if 40 <= rsi <= 60 else 0.5 if 30 <= rsi <= 70 else 0,
    "Earnings Proximity": 1 if not earnings else 0,
    "Cost Basis Awareness": 1 if cost_above else 0.5,
    "Sizing": 1 if qty <= 2 else 0.5
}

# Scoring weights
weights = {
    "DTE": 0.15,
    "Strike Distance": 0.15,
    "Premium Yield": 0.15,
    "Delta": 0.10,
    "IV Rank": 0.10,
    "RSI": 0.10,
    "Earnings Proximity": 0.10,
    "Cost Basis Awareness": 0.10,
    "Sizing": 0.05,
}

# Override rules
overrides = {
    "sizing": {"threshold": 90},
    "strike_distance": {"threshold": 92},
    "premium_yield": {"threshold": 95}
}

# Compute score and display
result = compute_conviction_score(features, weights, overrides)
st.metric("Conviction Score", f"{result['score']}%")
st.write("Overrides Allowed:", result['overrides'])
