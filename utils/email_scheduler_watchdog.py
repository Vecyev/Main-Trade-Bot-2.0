from utils.env_loader import load_env
load_env()

import os
import time

print("Starting watchdog for email scheduler...")
while True:
    exit_code = os.system("python utils/email_scheduler.py")
    print(f"Scheduler exited with code {exit_code}. Restarting in 30 seconds...")
    time.sleep(30)