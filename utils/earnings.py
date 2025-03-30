import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def is_near_earnings(symbol, window=7):
    try:
        ticker = yf.Ticker(symbol)
        earnings_calendar = ticker.calendar
        if "Earnings Date" in earnings_calendar.index:
            earnings_date = earnings_calendar.loc["Earnings Date"].values[0]
            if isinstance(earnings_date, pd.Timestamp):
                days_until = (earnings_date - datetime.now()).days
                if abs(days_until) <= window:
                    return True
    except Exception as e:
        print(f"[EARNINGS CHECK ERROR] {e}")
    return False