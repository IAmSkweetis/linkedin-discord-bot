from pathlib import Path
from typing import Any, List

from discord import Bot, Color, Embed, TextChannel

from linkedin_discord_bot import __version__
from linkedin_discord_bot.db import DBClient
from linkedin_discord_bot.exceptions import LinkedInBotBaseException, LinkedInBotConfigError
from linkedin_discord_bot.logging import LOG
from linkedin_discord_bot.settings import bot_settings


class LinkedInDiscordBot(Bot):

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        # Init the bot
        LOG.info("Initializing LinkedIn Discord Bot")
        super().__init__(*args, **kwargs)  # type: ignore

        # Attempt to initialize the database
        LOG.info("Initializing database")
        DBClient()

        # Load cogs
        LOG.info("Loading cogs")
        loaded_cogs = self.__cog_loader()
        LOG.info(f"Loaded {len(loaded_cogs)} cogs: {', '.join(loaded_cogs)}")

        LOG.info("LinkedIn Discord Bot initialized")

    def __cog_loader(self) -> List[str]:
        """Internal cog loader.

        This method loads all cogs in the `cogs/commands` directory.
        """
        cogs_path = Path(__file__).parent / "cogs"

        # TODO: Eventually, we'll have different cog types. Such as having a task cog.
        command_cogs = cogs_path / "commands"

        cog_list: List[str] = []

        for path in command_cogs.iterdir():
            LOG.debug(f"Found path: {path}")
            if path.is_file() and path.suffix == ".py" and path.stem != "__init__":
                LOG.debug(f"Adding path: {path.stem}")
                cog_list.append(path.stem)

            else:
                LOG.debug(f"Skipping path: {path}")

        if not cog_list:
            LOG.error("No cogs found")

        for cog in cog_list:
            LOG.debug(f"Loading cog: {cog}")
            self.load_extension(f"linkedin_discord_bot.discord.cogs.commands.{cog}")

        return cog_list

    # Discord event handlers
    async def on_ready(self) -> None:

        LOG.info(f"Connected to Discord as {self.user}")
        LOG.debug(f"Discord Token: {bot_settings.discord_token}")
        LOG.info(f"Discord notification channel ID: {bot_settings.discord_notif_channel_id}")

        notif_channel = self.get_channel(bot_settings.discord_notif_channel_id)
        if notif_channel is None:
            LOG.error(f"Notification channel ID {bot_settings.discord_notif_channel_id} not found")
            raise LinkedInBotConfigError(
                f"Notification channel ID {bot_settings.discord_notif_channel_id} not found"
            )

        if not isinstance(notif_channel, TextChannel):
            LOG.error(
                f"Notification channel ID {bot_settings.discord_notif_channel_id} is not a TextChannel"
            )
            raise LinkedInBotBaseException(
                f"Notification channel ID {bot_settings.discord_notif_channel_id} is not a TextChannel"
            )

        # Create our startup embed
        startup_embed = Embed(
            title="LinkedIn Discord Bot",
            description="LinkedIn Discord Bot is online!",
            color=Color.blue(),
        )

        startup_embed.add_field(
            name="Version",
            value=f"```{__version__}```",
            inline=False,
        )

        await notif_channel.send(embed=startup_embed)
        LOG.info("LinkedIn Discord Bot is online")


def bot_start() -> None:
    """Run the LinkedIn Discord Bot."""
    LOG.info("Starting LinkedIn Discord Bot")
    bot = LinkedInDiscordBot()
    bot.run(bot_settings.discord_token)
    LOG.info("LinkedIn Discord Bot has stopped")
