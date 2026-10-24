"""
Application settings — driven by environment variables.

Usage:
    from config.settings import settings
    print(settings.database_url)
"""

import os

from pydantic_settings import BaseSettings
from pydantic import Field

# On Vercel the deployment filesystem is read-only; /tmp is the only writable path.
ON_VERCEL = bool(os.environ.get("VERCEL"))
_DEFAULT_DB = (
    "sqlite+aiosqlite:////tmp/guitar_mastery.db" if ON_VERCEL
    else "sqlite+aiosqlite:///./data/guitar_mastery.db"
)


class Settings(BaseSettings):
    """Global application settings loaded from .env file."""

    # General
    environment: str = Field(default="production" if ON_VERCEL else "development")
    debug: bool = Field(default=not ON_VERCEL)
    app_name: str = Field(default="Guitar Mastery AI")
    app_version: str = Field(default="0.1.0")

    # LLM (Anthropic Claude)
    anthropic_api_key: str = Field(default="")
    default_model: str = Field(default="claude-sonnet-5-5")
    fallback_model: str = Field(default="claude-sonnet-5-5")
    simple_model: str = Field(default="claude-haiku-5-5")

    # Database
    database_url: str = Field(default=_DEFAULT_DB)

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=30)

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    reload: bool = Field(default=not ON_VERCEL)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
