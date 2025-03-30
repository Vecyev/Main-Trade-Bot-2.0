# NVDA Covered Call + CSP Trade Bot

This automated trading bot executes a JEPQ-style covered call and cash-secured put strategy on NVDA using Interactive Brokers.

## Features
- Covered call + CSP routing logic
- Volatility + earnings-aware filters
- IBKR smart order routing via `ib_insync`
- Streamlit dashboard with auto-tuner
- Slack integration with alerts and summaries
- Trade scoring + ML feature logging

## Setup
1. Install requirements:
   ```
   pip install -r requirements.txt
   ```

2. Start IBKR TWS or IB Gateway (port 7497)

3. Run the bot:
   ```
   python3 main.py
   ```

4. Launch the dashboard:
   ```
   streamlit run dashboard/app.py
   ```

## Slack Commands
- `/nvda summary` — Show total trades + premium
- `/nvda score` — Avg trade score
- `/nvda last trade` — Most recent trade

## Scheduling
Use `nvda_daily_runner.sh` to automate daily runs via cron or Task Scheduler.