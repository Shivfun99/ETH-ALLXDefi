"""
Simple scheduler script for periodic monitoring.
This is a demo asyncio loop. For production use APScheduler or Celery.
"""

import asyncio
import logging
from app.services.data_fetcher import fetch_aave_position, fetch_market_volatility, fetch_market_trend
from app.services.risk_model import predict
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scheduler")

async def monitor_user(user_address: str):
    while True:
        try:
            # fetch position and market data
            pos_task = fetch_aave_position(user_address)
            vol_task = fetch_market_volatility()
            trend_task = fetch_market_trend()

            pos, vol, trend = await asyncio.gather(pos_task, vol_task, trend_task)
            features = {
                "volatility": vol,
                "collateral_ratio": pos.get("collateral_ratio"),
                "leverage": pos.get("leverage"),
                "asset_price": pos.get("asset_price"),
                "market_trend": trend,
                "protocol": "Aave",
                "user_wallet": user_address
            }

            res = await predict(features)
            logger.info("User %s prediction: %s", user_address, res)

            # If above threshold, log/alert (alerting not implemented here)
            if float(res.get("risk_probability", 0)) >= settings.ALERT_THRESHOLD:
                logger.warning("ALERT: user %s risk >= %s : %s", user_address, settings.ALERT_THRESHOLD, res)

        except Exception as e:
            logger.exception("monitor_user error: %s", e)

        await asyncio.sleep(settings.SCHED_INTERVAL_SECONDS)

if __name__ == "__main__":
    # Example usage: python app/tasks/scheduler.py
    # Replace with your watched wallet address(es)
    user_wallet = "0xExampleUserWallet"
    asyncio.run(monitor_user(user_wallet))
