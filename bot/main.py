import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import bot_config
from bot.handlers import start, meals, stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main bot entry point."""
    # Initialize bot and dispatcher
    bot = Bot(token=bot_config.TELEGRAM_BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register routers
    dp.include_router(start.router)
    dp.include_router(meals.router)
    dp.include_router(stats.router)

    try:
        logger.info("Bot started polling...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
