from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_BOT_USERNAME: str

    # WHOOP
    WHOOP_CLIENT_ID: str
    WHOOP_CLIENT_SECRET: str
    WHOOP_REDIRECT_URI: str

    # Claude API
    ANTHROPIC_API_KEY: str

    # Database
    DATABASE_URL: str
    DATABASE_URL_SYNC: Optional[str] = None

    # Redis
    REDIS_URL: str

    # App
    SECRET_KEY: str
    API_BASE_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def database_url_sync(self) -> str:
        """Return sync database URL for Alembic."""
        if self.DATABASE_URL_SYNC:
            return self.DATABASE_URL_SYNC
        return self.DATABASE_URL.replace("asyncpg", "psycopg2")


settings = Settings()
