import logging
import os

os.makedirs("logs", exist_ok=True)
log_file = "logs/nvda_trading_log.txt"

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("NVDA_BOT")