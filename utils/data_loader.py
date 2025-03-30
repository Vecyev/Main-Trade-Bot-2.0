import os
import time
import asyncio
import logging
import yfinance as yf
import numpy as np
from functools import lru_cache, wraps

# -------------------------
# Configuration & Logging
# -------------------------

# Configurable parameters (set via environment variables, with defaults)
DEFAULT_PERIOD = os.environ.get("PRICE_HISTORY_PERIOD", "1y")
DEFAULT_INTERVAL = os.environ.get("PRICE_HISTORY_INTERVAL", "1d")
DEFAULT_DAYS = int(os.environ.get("PRICE_HISTORY_DAYS", "21"))
RETRY_COUNT = int(os.environ.get("PRICE_HISTORY_RETRY_COUNT", "3"))
RETRY_DELAY = float(os.environ.get("PRICE_HISTORY_RETRY_DELAY", "2"))  # seconds

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simple in-memory metrics
metrics = {
    "api_calls": 0,
    "failed_calls": 0,
    "total_latency": 0.0
}

# -------------------------
# Retry Decorator (Async)
# -------------------------

def retry_async(retries=3, delay=2, backoff=2):
    """
    Decorator for asynchronous functions that retries on exception.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Attempt {attempt+1} failed for {func.__name__}: {e}")
                    if attempt < retries - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All retries failed for {func.__name__}")
                        raise
        return wrapper
    return decorator

# -------------------------
# Data Fetching Functions
# -------------------------

def get_price_history_sync(symbol, period, interval):
    """
    Synchronous function to fetch price history using yfinance.
    """
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period, interval=interval)
    if hist.empty or "Close" not in hist:
        raise ValueError(f"No data available for {symbol}")
    return hist

async def async_get_price_history_sync(symbol, period, interval):
    """
    Asynchronous wrapper for the synchronous yfinance call.
    Uses asyncio.to_thread (Python 3.9+) to run blocking code in a thread.
    """
    start_time = time.time()
    data = await asyncio.to_thread(get_price_history_sync, symbol, period, interval)
    latency = time.time() - start_time
    metrics["api_calls"] += 1
    metrics["total_latency"] += latency
    logger.info(f"Fetched data for {symbol} in {latency:.2f} seconds.")
    return data

@retry_async(retries=RETRY_COUNT, delay=RETRY_DELAY)
async def get_price_history_async(symbol, days=DEFAULT_DAYS, period=DEFAULT_PERIOD, interval=DEFAULT_INTERVAL):
    """
    Asynchronous function to fetch and process the closing price history.
    Applies retry logic and basic data validation.
    """
    try:
        hist = await async_get_price_history_sync(symbol, period, interval)
    except Exception as e:
        metrics["failed_calls"] += 1
        logger.error(f"Failed to fetch data for {symbol}: {e}")
        # (Optional: send an alert via Discord here)
        raise

    if len(hist) < days:
        logger.warning(f"Not enough data for {symbol}: requested {days} days, got {len(hist)} days")
        prices = hist['Close'].values  # return what we have
    else:
        prices = hist['Close'].values[-days:]
    
    # Data validation: ensure no negative values
    if np.any(prices < 0):
        logger.error(f"Invalid price data for {symbol}: contains negative values")
        raise ValueError("Invalid price data")

    # (Optional: normalize or further process prices if needed)
    logger.info(f"Retrieved {len(prices)} closing prices for {symbol}.")
    return np.array(prices)

# -------------------------
# Synchronous API (with caching)
# -------------------------

@lru_cache(maxsize=10)
def get_price_history(symbol, days=DEFAULT_DAYS, period=DEFAULT_PERIOD, interval=DEFAULT_INTERVAL):
    """
    Synchronous wrapper that uses an event loop to call the async function.
    Caches results for efficiency.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(get_price_history_async(symbol, days, period, interval))
    finally:
        loop.close()
    return result

# -------------------------
# Performance Metrics & Test Code
# -------------------------

if __name__ == "__main__":
    symbol = "NVDA"
    try:
        prices = get_price_history(symbol)
        logger.info(f"Last {DEFAULT_DAYS} closing prices for {symbol}: {prices}")
        logger.info(f"Metrics: {metrics}")
    except Exception as e:
        logger.error(f"Error retrieving price history: {e}")
