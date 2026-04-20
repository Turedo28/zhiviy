"""
Background scheduler for periodic WHOOP data synchronization.
Runs as an asyncio background task inside FastAPI.
Syncs sleep, recovery, and workout data for all connected users.
"""
import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.whoop import WhoopToken
from app.services.whoop_service import get_valid_token, sync_whoop_data

logger = logging.getLogger(__name__)

# Sync interval in seconds (1 hour for intraday updates)
SYNC_INTERVAL_SECONDS = 1 * 60 * 60

# How many days back to sync each run (2 days covers yesterday + today)
SYNC_DAYS_BACK = 2

_scheduler_task: asyncio.Task | None = None


async def _sync_all_users() -> dict:
    """
    Iterate over all users with a WHOOP token,
    refresh token if needed, and sync recent data.
    Returns summary of results.
    """
    results = {"total_users": 0, "synced": 0, "errors": 0, "details": []}

    async with AsyncSessionLocal() as db:
        stmt = select(WhoopToken)
        result = await db.execute(stmt)
        tokens = result.scalars().all()
        results["total_users"] = len(tokens)

        for whoop_token in tokens:
            user_id = whoop_token.user_id
            try:
                # Refresh token if expired
                access_token = await get_valid_token(whoop_token, db)

                # Sync last N days
                counts = await sync_whoop_data(
                    user_id=user_id,
                    access_token=access_token,
                    db=db,
                    days_back=SYNC_DAYS_BACK,
                )
                results["synced"] += 1
                results["details"].append({
                    "user_id": user_id,
                    "status": "ok",
                    "counts": counts,
                })
                logger.info(
                    f"WHOOP sync OK for user {user_id}: "
                    f"sleep={counts['sleep']}, recovery={counts['recovery']}, "
                    f"workouts={counts['workouts']}, cycles={counts.get('cycles', 0)}"
                )
            except Exception as e:
                results["errors"] += 1
                results["details"].append({
                    "user_id": user_id,
                    "status": "error",
                    "error": str(e),
                })
                logger.error(f"WHOOP sync FAILED for user {user_id}: {e}")

    return results


async def _scheduler_loop():
    """
    Background loop that runs sync every SYNC_INTERVAL_SECONDS.
    First run happens 60 seconds after startup (let the app fully boot),
    then repeats every interval.
    """
    # Short delay to let the app fully initialize
    await asyncio.sleep(5)

    while True:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        logger.info(f"[WHOOP Scheduler] Starting periodic sync at {now}")

        try:
            results = await _sync_all_users()
            logger.info(
                f"[WHOOP Scheduler] Done: "
                f"{results['synced']}/{results['total_users']} users synced, "
                f"{results['errors']} errors"
            )
        except Exception as e:
            logger.error(f"[WHOOP Scheduler] Unexpected error: {e}")

        # Sleep until next sync
        logger.info(
            f"[WHOOP Scheduler] Next sync in {SYNC_INTERVAL_SECONDS // 3600} hours"
        )
        await asyncio.sleep(SYNC_INTERVAL_SECONDS)


def start_whoop_scheduler():
    """Start the background WHOOP sync scheduler."""
    global _scheduler_task
    if _scheduler_task is None or _scheduler_task.done():
        _scheduler_task = asyncio.create_task(_scheduler_loop())
        logger.info("[WHOOP Scheduler] Background sync scheduler started")


def stop_whoop_scheduler():
    """Stop the background WHOOP sync scheduler."""
    global _scheduler_task
    if _scheduler_task and not _scheduler_task.done():
        _scheduler_task.cancel()
        logger.info("[WHOOP Scheduler] Background sync scheduler stopped")
        _scheduler_task = None
