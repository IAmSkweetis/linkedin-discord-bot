from typing import Any

from discord import Bot, Color, Embed, TextChannel

from linkedin_discord_bot import __version__
from linkedin_discord_bot.db import DBClient
from linkedin_discord_bot.exceptions import LinkedInBotBaseException, LinkedInBotConfigError
from linkedin_discord_bot.logging import LOG
from linkedin_discord_bot.settings import bot_settings


class LinkedInDiscordBot(Bot):

    def __init__(self, *args: Any, db_client: DBClient | None = None, **kwargs: Any) -> None:

        # Init the bot
        LOG.info("Initializing LinkedIn Discord Bot")
        super().__init__(*args, **kwargs)  # type: ignore

        # Attempt to initialize the database
        if db_client is None:
            LOG.info("Initializing database")
            self.db_client = DBClient()
        else:
            LOG.info("Using provided database client")
            self.db_client = db_client

        # Load cogs
        active_cogs = [
            "linkedin_discord_bot.discord.cogs.commands.job",
            "linkedin_discord_bot.discord.cogs.commands.query",
        ]

        LOG.info("Loading cogs")
        for cog in active_cogs:
            try:
                self.load_extension(cog)
                LOG.info(f"Loaded cog: {cog}")
            except Exception as err:
                LOG.error(f"Failed to load cog {cog}: {err}")

        LOG.info("LinkedIn Discord Bot initialized")

    # Discord event handlers
    async def on_ready(self) -> None:

        LOG.info(f"Connected to Discord as {self.user}")
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


def start_linkedin_discord_bot() -> None:
    """Run the LinkedIn Discord Bot."""
    LOG.info("Starting LinkedIn Discord Bot")
    bot = LinkedInDiscordBot()
    bot.run(bot_settings.discord_token)
    LOG.info("LinkedIn Discord Bot has stopped")
