import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (one level up from bot/) — for local dev
# In Docker, env vars come from docker-compose env_file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class BotConfig:
    """Telegram bot configuration."""

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    API_BASE_URL = os.getenv("API_BASE_URL", "http://healthtrack_backend:8000/api")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    def __post_init__(self):
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")


bot_config = BotConfig()

if not bot_config.TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is not set")
