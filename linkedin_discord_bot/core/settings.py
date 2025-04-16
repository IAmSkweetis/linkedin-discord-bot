from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Base settings for the LinkedIn Discord Bot
    env: str = Field(default="dev-local")
    app_name: str = Field(default="linkedin-discord-bot")

    # Logging Config
    logging_level: str = Field(default="INFO")
    log_file: str = Field(default="linkedin-discord-bot.log")
    log_file_enabled: bool = Field(default=False)

    # Discord settings
    discord_token: str = Field(default="")
    notif_channel_id: int = Field(default=0)

    # Proxycurl settings
    proxycurl_api_key: str = Field(default="")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="LINKEDIN_DISCORD_BOT_",
        env_nested_delimiter="__",
        extra="ignore",
    )


bot_settings = Settings()
