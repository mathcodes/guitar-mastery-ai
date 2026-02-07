"""
Application settings — driven by environment variables.

Usage:
    from config.settings import settings
    print(settings.database_url)
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Global application settings loaded from .env file."""

    # General
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    app_name: str = Field(default="Guitar Mastery AI")
    app_version: str = Field(default="0.1.0")

    # LLM (Anthropic Claude)
    anthropic_api_key: str = Field(default="")
    default_model: str = Field(default="claude-sonnet-4-20250514")
    fallback_model: str = Field(default="claude-sonnet-4-20250514")
    simple_model: str = Field(default="claude-haiku-4-20250414")

    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///./data/guitar_mastery.db")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=30)

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    reload: bool = Field(default=True)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
