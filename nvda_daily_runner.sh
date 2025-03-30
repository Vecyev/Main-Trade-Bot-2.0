#!/bin/bash
cd "$(dirname "$0")"
source ~/.bashrc
echo "[SCHEDULER] Running NVDA strategy bot"
python3 main.py >> logs/nvda_trading_log.txt 2>&1