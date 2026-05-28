"""
Signal Generator — sends realistic trading signal payloads to the API.
Used for load testing Redis performance and observability stack validation.
Generates approximately 10 signals per second by default.
"""

import random
import requests
import time
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000"
SYMBOLS = ["AAPL", "GOOGL", "INFY", "TCS", "RELIANCE", "MSFT", "AMZN"]
ACTIONS = ["BUY", "SELL", "HOLD"]
RATE_PER_SECOND = 10


def generate_signal() -> dict:
    return {
        "symbol": random.choice(SYMBOLS),
        "action": random.choice(ACTIONS),
        "confidence": round(random.uniform(0.5, 0.99), 2),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def run(duration_seconds: int = 60):
    logger.info(f"Starting signal generator — {RATE_PER_SECOND} signals/sec for {duration_seconds}s")
    end_time = time.time() + duration_seconds
    sent = 0
    errors = 0

    while time.time() < end_time:
        signal = generate_signal()
        try:
            response = requests.post(f"{API_URL}/signals", json=signal, timeout=2)
            if response.status_code == 200:
                sent += 1
            else:
                errors += 1
        except requests.RequestException as e:
            errors += 1
            logger.warning(f"Request failed: {e}")
        time.sleep(1 / RATE_PER_SECOND)

    logger.info(f"Done — sent: {sent}, errors: {errors}")


if __name__ == "__main__":
    run(duration_seconds=60)
