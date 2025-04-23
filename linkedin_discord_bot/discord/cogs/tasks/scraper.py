import datetime

from discord import ApplicationContext, Cog, Color, Embed, SlashCommandGroup
from discord.ext import tasks
from discord.utils import format_dt

from linkedin_discord_bot.discord import LinkedInDiscordBot
from linkedin_discord_bot.logging import LOG
from linkedin_discord_bot.scraper import Scraper
from linkedin_discord_bot.settings import bot_settings


class ScraperCog(Cog, name="scraper"):

    def __init__(self, li_bot: LinkedInDiscordBot) -> None:
        self.li_bot = li_bot

        self.scraper_task_loop.start()

    scraper_commands = SlashCommandGroup(
        name="scraper", desc="Commands related to the LinkedIn scraper."
    )

    # Task Loop and friends
    @tasks.loop(seconds=bot_settings.discord_scraper_frequency)
    async def scraper_task_loop(self) -> None:
        """Scrape LinkedIn for new job postings."""
        LOG.info("Initiating LinkedIn Scraper...")
        scraper = Scraper()
        scraper.run()

    # Commands
    @scraper_commands.command(name="status", desc="Status of the LinkedIn scraper.")
    async def scraper_status(self, ctx: ApplicationContext) -> None:
        """Get the status of the LinkedIn scraper."""
        await ctx.respond("Checking the status of the LinkedIn scraper...", ephemeral=True)
        status_embed = Embed(
            title="LinkedIn Scraper Status",
            description="The LinkedIn scraper is currently running.",
            color=Color.blue(),
        )

        status_embed.add_field(
            name="Status",
            value="```Running```" if self.scraper_task_loop.is_running() else "```Not Running```",
            inline=False,
        )

        if self.scraper_task_loop.next_iteration is not None:
            ni_timestamp = self.scraper_task_loop.next_iteration.timestamp()
            li_timestamp = ni_timestamp - bot_settings.discord_scraper_frequency
            li_datetime = datetime.datetime.fromtimestamp(li_timestamp)

            status_embed.add_field(
                name="Last Run",
                value=f"{format_dt(li_datetime, style='F')}",
                inline=False,
            )

            status_embed.add_field(
                name="Next Run",
                value=f"{format_dt(self.scraper_task_loop.next_iteration, style='F')}",
                inline=False,
            )

        status_embed.add_field(
            name="Total Queries",
            value=f"```{len(self.li_bot.db_client.get_job_queries())}```",
            inline=False,
        )

        status_embed.add_field(
            name="Scraper Frequency",
            value=f"```{bot_settings.discord_scraper_frequency} seconds```",
            inline=False,
        )

        await ctx.send_followup(embed=status_embed, ephemeral=True)

    @scraper_commands.command(name="restart", desc="Restart the LinkedIn scraper.")
    async def restart_scraper(self, ctx: ApplicationContext) -> None:
        """Restart the LinkedIn scraper."""
        LOG.info("Restarting LinkedIn Scraper...")
        await ctx.respond("Restarting the LinkedIn scraper...", ephemeral=True)
        if self.scraper_task_loop.is_running():
            self.scraper_task_loop.restart()
            LOG.info("Scraper restarted.")
            await ctx.send_followup("Scraper restarted.", ephemeral=True)
        else:
            await ctx.send_followup("Scraper was not running. Attempting to start.", ephemeral=True)
            try:
                self.scraper_task_loop.start()
                LOG.info("Scraper started.")
                await ctx.send_followup("Scraper started.", ephemeral=True)
            except Exception as err:
                LOG.error(f"Error starting scraper: {err}")
                await ctx.send_followup("Error starting scraper. Check logs.", ephemeral=True)


def setup(li_bot: LinkedInDiscordBot) -> None:
    """Cog Setup Function"""
    li_bot.add_cog(ScraperCog(li_bot))
