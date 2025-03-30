from utils.env_loader import load_env
load_env()


import smtplib
import pandas as pd
import os
from email.mime.text import MIMEText
from utils.discord_alerts import send_discord_alert
from datetime import datetime

def send_daily_email_summary():
    log_path = "logs/trade_history.csv"
    if not os.path.exists(log_path):
        print("No trade log to email.")
        return

    df = pd.read_csv(log_path)
    today = datetime.now().strftime("%Y-%m-%d")
    df_today = df[df["Date"] == today]

    if df_today.empty:
        print("No trades today to email.")
        return

    total_premium = df_today["Premium"].sum()
    avg_conviction = df_today["Conviction"].mean()
    avg_ml = df_today["ML Score"].mean()
    realized_pnl = df_today["Actual PnL"].dropna().sum()

    summary = f"""
Daily Trade Summary for {today}

Trades Executed: {len(df_today)}
Total Premium: ${total_premium:.2f}
Avg Conviction: {avg_conviction:.2f}
Avg ML Score: {avg_ml:.2f}
Realized PnL: ${realized_pnl:.2f}
"""

    msg = MIMEText(summary)
    msg["Subject"] = f"Trade Bot Daily Summary - {today}"
    msg["From"] = os.getenv("EMAIL_SENDER")
    msg["To"] = os.getenv("EMAIL_RECIPIENT")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(os.getenv("EMAIL_SENDER"), os.getenv("EMAIL_PASSWORD"))
            server.send_message(msg)
        print("Email sent.")
        send_discord_alert("✅ Daily trade summary email sent successfully.")
    except Exception as e:
        send_discord_alert(f"❌ Failed to send trade summary email: {e}")
        print("Failed to send email:", e)

if __name__ == "__main__":
    send_daily_email_summary()