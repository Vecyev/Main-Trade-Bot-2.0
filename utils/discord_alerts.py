
# utils/discord_alerts.py
import os
import logging
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

# Set the Discord webhook URL directly.
# In production, you might load this from an environment variable or config file.
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1354076379746140211/xKKT4dCTRpKt15_Uh3bgJtLDlCukgrGttgPtYF1ZnjYB1mvdjYEl7r_L_ktel5TyWzIn"

async def send_discord_alert_async(message: str):
    """
    Asynchronously sends an alert to Discord via the webhook.
    The message will be posted to the channel (trade_alerts) associated with the webhook,
    and the alert will appear to be sent from 'TradeBot'.
    """
    webhook_url = DISCORD_WEBHOOK_URL or os.environ.get("DISCORD_WEBHOOK_URL", "")
    if not webhook_url:
        logger.warning("Discord webhook URL not configured. Message: " + message)
        return

    payload = {
        "content": message,
        "username": "TradeBot"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload, timeout=10) as response:
                if response.status not in (200, 204):
                    text = await response.text()
                    logger.error(f"Discord alert failed: {response.status} - {text}")
    except Exception as e:
        logger.error(f"Exception sending Discord alert: {e}")

def send_discord_alert(message: str):
    """
    Synchronous wrapper for sending Discord alerts.
    Uses asyncio.run() to execute the asynchronous function.
    """
    asyncio.run(send_discord_alert_async(message))
