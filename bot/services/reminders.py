"""Meal reminder scheduler — sends reminders at 8:00, 13:00, 19:00 Kyiv time."""
import asyncio
import json
import logging
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

KYIV_TZ = ZoneInfo("Europe/Kyiv")
USERS_FILE = Path("/app/data/reminder_users.json")
REMINDER_TIMES = [time(8, 0), time(13, 0), time(19, 0)]
REMINDER_LABELS = {time(8, 0): "сніданку", time(13, 0): "обіду", time(19, 0): "вечері"}


def _load() -> dict:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not USERS_FILE.exists():
        return {}
    try:
        return json.loads(USERS_FILE.read_text())
    except Exception:
        return {}


def _save(data: dict):
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def register_user(telegram_id: int):
    data = _load()
    uid = str(telegram_id)
    if uid not in data:
        data[uid] = {"reminders_enabled": True}
        _save(data)


def set_reminders(telegram_id: int, enabled: bool):
    data = _load()
    uid = str(telegram_id)
    if uid not in data:
        data[uid] = {}
    data[uid]["reminders_enabled"] = enabled
    _save(data)


def _seconds_until(t: time) -> float:
    now = datetime.now(KYIV_TZ)
    target = now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
    if target <= now:
        target = target.replace(day=target.day + 1)
    return (target - now).total_seconds()


async def reminder_loop(bot):
    """Background task: fires reminders at each scheduled time."""
    while True:
        now = datetime.now(KYIV_TZ).time().replace(second=0, microsecond=0)

        for t in REMINDER_TIMES:
            if now.hour == t.hour and now.minute == t.minute:
                label = REMINDER_LABELS[t]
                data = _load()
                for uid, prefs in data.items():
                    if prefs.get("reminders_enabled", True):
                        try:
                            await bot.send_message(
                                int(uid),
                                f"🍽 Час {label}! Не забудьте записати прийом їжі.",
                            )
                        except Exception as e:
                            logger.debug(f"Reminder failed for {uid}: {e}")
                break

        await asyncio.sleep(60)
