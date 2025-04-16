from pathlib import Path
from typing import Any, List

from discord import Bot, TextChannel

from linkedin_discord_bot import __version__
from linkedin_discord_bot.core.linkedin import LinkedInClient
from linkedin_discord_bot.core.logging import LOG
from linkedin_discord_bot.core.settings import bot_settings
from linkedin_discord_bot.exceptions import LinkedInBotBaseException, LinkedInBotConfigError


class LinkedInDiscordBot(Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        LOG.info("Initializing LinkedIn Discord Bot")

        super().__init__(*args, **kwargs)  # type: ignore

        # Include a LinkedInClient
        LOG.info("Initializing Poxycurl LinkedIn Client")
        self.linkedin_client = LinkedInClient()

        # Load cogs
        self.__cog_loader()

        LOG.info("LinkedIn Discord Bot initialized")

    def __cog_loader(self) -> None:
        """Internal cog loader.

        This method loads all cogs in the `cogs/commands` directory.
        """
        cogs_path = Path(__file__).parent.parent / "cogs"

        # TODO: Eventually, we'll have different cog types. Such as having a task cog.
        command_cogs = cogs_path / "commands"

        cog_list: List[str] = []

        LOG.info("Loading LinkedIn Discord Bot Cogs")
        LOG.info("Looking for command cogs")

        for path in command_cogs.iterdir():
            LOG.debug(f"Found path: {path}")
            if path.is_file() and path.suffix == ".py" and path.stem != "__init__":
                LOG.debug(f"Adding path: {path.stem}")
                cog_list.append(path.stem)

            else:
                LOG.debug(f"Skipping path: {path}")

        if not cog_list:
            LOG.error("No cogs found")

        LOG.info(f"Found {len(cog_list)} cogs")

        for cog in cog_list:
            try:
                LOG.info(f"Loading cog: {cog}")
                self.load_extension(f"linkedin_discord_bot.cogs.commands.{cog}")
            except Exception as err:
                LOG.error(f"Failed to load cog {cog}: {err}")

    # Discord event handlers
    async def on_ready(self) -> None:

        LOG.info(f"Connected to Discord as {self.user}")
        LOG.debug(f"Discord Token: {bot_settings.discord_token}")
        LOG.info(f"Discord notification channel ID: {bot_settings.notif_channel_id}")

        notif_channel = self.get_channel(bot_settings.notif_channel_id)
        if notif_channel is None:
            LOG.error(f"Notification channel ID {bot_settings.notif_channel_id} not found")
            raise LinkedInBotConfigError(
                f"Notification channel ID {bot_settings.notif_channel_id} not found"
            )

        if not isinstance(notif_channel, TextChannel):
            LOG.error(
                f"Notification channel ID {bot_settings.notif_channel_id} is not a TextChannel"
            )
            raise LinkedInBotBaseException(
                f"Notification channel ID {bot_settings.notif_channel_id} is not a TextChannel"
            )

        await notif_channel.send(f"LinkedIn Discord Bot v{__version__} is online!")
        LOG.info("LinkedIn Discord Bot is online")


def bot_start() -> None:
    """Run the LinkedIn Discord Bot."""
    LOG.info("Starting LinkedIn Discord Bot")
    bot = LinkedInDiscordBot()
    bot.run(bot_settings.discord_token)
    LOG.info("LinkedIn Discord Bot has stopped")
