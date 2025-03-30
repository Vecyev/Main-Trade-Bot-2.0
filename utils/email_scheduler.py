from utils.env_loader import load_env
load_env()


import schedule
import time
from utils.email_summary import send_daily_email_summary

schedule.every().day.at("17:00").do(send_daily_email_summary)

print("Email scheduler running... (Ctrl+C to stop)")
while True:
    schedule.run_pending()
    time.sleep(60)