from typing import Any, Dict

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Base settings for the LinkedIn Discord Bot
    env: str = Field(default="dev-local")
    app_name: str = Field(default="linkedin-discord-bot")

    # Logging Config
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="linkedin-discord-bot.log")
    log_file_enabled: bool = Field(default=False)

    # DB Config
    db_connection_string: str = Field(default="sqlite:///")
    db_connection_args: Dict[Any, Any] = Field(default={})

    # Discord Config
    discord_token: str = Field(default="")
    discord_notif_channel_id: int = Field(default=0)
    discord_scraper_frequency: int = Field(default=86400)

    # NOTE: The following settings are commented out because they are not used in the current implementation.
    # LinkedIn Config
    # linkedin_username: str = Field(default="")
    # linkedin_password: str = Field(default="")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="LINKEDIN_DISCORD_BOT_",
        env_nested_delimiter="__",
        extra="ignore",
    )


bot_settings = Settings()
