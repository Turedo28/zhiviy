"""Local retry queue for failed meal syncs."""
import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime

import httpx

from bot.config import bot_config

logger = logging.getLogger(__name__)

QUEUE_FILE = Path("/app/data/pending_meals.json")
RETRY_INTERVAL = 60  # seconds between retry attempts


def _ensure_dir():
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)


def enqueue_meal(meal_data: dict):
    """Save a failed meal to the local queue."""
    _ensure_dir()
    queue = load_queue()
    meal_data["queued_at"] = datetime.utcnow().isoformat()
    queue.append(meal_data)
    QUEUE_FILE.write_text(json.dumps(queue, ensure_ascii=False, indent=2))
    logger.info(f"Queued meal '{meal_data.get('name')}' for retry ({len(queue)} pending)")


def load_queue() -> list:
    """Load pending meals from file."""
    _ensure_dir()
    if not QUEUE_FILE.exists():
        return []
    try:
        return json.loads(QUEUE_FILE.read_text())
    except (json.JSONDecodeError, IOError):
        return []


def save_queue(queue: list):
    """Save queue back to file."""
    _ensure_dir()
    QUEUE_FILE.write_text(json.dumps(queue, ensure_ascii=False, indent=2))


async def retry_pending_meals():
    """Try to sync all pending meals. Returns (synced, failed) counts."""
    queue = load_queue()
    if not queue:
        return 0, 0

    synced = 0
    still_pending = []

    async with httpx.AsyncClient() as client:
        for meal in queue:
            try:
                payload = {k: v for k, v in meal.items() if k != "queued_at"}
                response = await client.post(
                    f"{bot_config.API_BASE_URL}/api/v1/meals/bot",
                    json=payload,
                    timeout=10,
                )
                if response.status_code == 200:
                    synced += 1
                    logger.info(f"Synced queued meal: {meal.get('name')}")
                else:
                    still_pending.append(meal)
                    logger.warning(f"Retry failed for '{meal.get('name')}': HTTP {response.status_code}")
            except Exception as e:
                still_pending.append(meal)
                logger.error(f"Retry error for '{meal.get('name')}': {e}")

    save_queue(still_pending)
    return synced, len(still_pending)


async def retry_loop():
    """Background task that periodically retries pending meals."""
    while True:
        await asyncio.sleep(RETRY_INTERVAL)
        queue = load_queue()
        if queue:
            synced, pending = await retry_pending_meals()
            if synced > 0:
                logger.info(f"Retry sync: {synced} synced, {pending} still pending")
