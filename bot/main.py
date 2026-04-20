import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import bot_config
from bot.handlers import start, meals, stats, settings, water
from bot.services.sync_queue import retry_loop
from bot.services.reminders import reminder_loop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RETRY_DELAY = 5  # seconds between retries


async def main():
    """Main bot entry point with automatic restart on network errors."""
    bot = Bot(token=bot_config.TELEGRAM_BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register routers
    dp.include_router(start.router)
    dp.include_router(meals.router)
    dp.include_router(water.router)
    dp.include_router(stats.router)
    dp.include_router(settings.router)

    # Background tasks
    asyncio.create_task(retry_loop())
    asyncio.create_task(reminder_loop(bot))

    retry_count = 0
    while True:
        try:
            logger.info("Bot started polling...")
            await dp.start_polling(bot)
            break  # Normal shutdown
        except Exception as e:
            retry_count += 1
            logger.error(f"Polling crashed (attempt {retry_count}): {e}")
            logger.info(f"Restarting polling in {RETRY_DELAY}s...")
            await asyncio.sleep(RETRY_DELAY)
        finally:
            try:
                await bot.session.close()
            except Exception:
                pass


if __name__ == "__main__":
    asyncio.run(main())
