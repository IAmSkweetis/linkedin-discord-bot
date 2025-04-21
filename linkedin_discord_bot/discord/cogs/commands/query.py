from discord import ApplicationContext, Cog, SlashCommandGroup
from prettytable import PrettyTable

from linkedin_discord_bot.discord import LinkedInDiscordBot


class JobQueryCog(Cog, name="JobQuery"):

    def __init__(self, li_bot: LinkedInDiscordBot) -> None:
        self.li_bot = li_bot

    job_query_commands = SlashCommandGroup(name="query", desc="Commands related to job queries.")

    @job_query_commands.command(name="list", help="List all registered job search queries.")
    async def job_query_list(self, ctx: ApplicationContext) -> None:
        """List all job queries."""
        await ctx.respond("Checking the database for job queries...", ephemeral=True)
        job_queries = self.li_bot.db_client.get_job_queries()

        if not job_queries:
            await ctx.send_followup("No job queries found.")
            return

        # Create a table to display the job queries
        table = PrettyTable()
        table.field_names = ["Query", "Locations", "Games Only", "Remote Only"]
        for job_query in job_queries:
            table.add_row(
                [
                    job_query.query,
                    job_query.locations,
                    "Yes" if job_query.games_only else "No",
                    "Yes" if job_query.remote_only else "No",
                ]
            )

        # Send the table as a follow-up message
        await ctx.send_followup(f"```{table}```", ephemeral=True)


def setup(li_bot: LinkedInDiscordBot) -> None:
    """Cog Setup Function"""
    li_bot.add_cog(JobQueryCog(li_bot))
