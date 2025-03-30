
import pandas as pd
import os
from datetime import datetime

LOG_PATH = "logs/trade_history.csv"
PRICE_AT_EXPIRY_COL = "Underlying Expiry Price"

def reconcile_outcomes():
    if not os.path.exists(LOG_PATH):
        print("No trade log found.")
        return

    df = pd.read_csv(LOG_PATH)
    updated = False

    for i, row in df.iterrows():
        if pd.notnull(row.get("Actual PnL")):
            continue  # already filled

        if row["Type"] == "Sell Call":
            expiry_price = row.get(PRICE_AT_EXPIRY_COL)
            strike = row["Strike"]
            premium = row["Premium"]

            if pd.notnull(expiry_price):
                pnl = premium if expiry_price <= strike else premium - (expiry_price - strike)
                df.at[i, "Actual PnL"] = round(pnl, 2)
                updated = True

    if updated:
        df.to_csv(LOG_PATH, index=False)
        print("Trade log updated with Actual PnL.")
    else:
        print("No updates made. Ensure expiry prices are available.")

if __name__ == "__main__":
    reconcile_outcomes()
