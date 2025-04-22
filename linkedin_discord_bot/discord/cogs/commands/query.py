from typing import Annotated

from discord import (ApplicationContext, Cog, Color, Embed, Interaction,
                     Option, SlashCommandGroup)
from discord.ui import InputText, Modal
from prettytable import PrettyTable

from linkedin_discord_bot.discord import LinkedInDiscordBot
from linkedin_discord_bot.models import JobQuery


class JobQueryCreateModal(Modal):
    discord_user_id: int

    def __init__(self, discord_user_id: int) -> None:
        super().__init__(title="Create Job Query")

        self.discord_user_id = discord_user_id

        self.add_item(
            InputText(
                custom_id="query",
                label="Query",
                placeholder="Enter the job query",
                required=True,
            )
        )
        self.add_item(
            InputText(
                custom_id="locations",
                label="Locations",
                placeholder="Enter the locations (comma-separated)",
                required=True,
            )
        )
        self.add_item(
            InputText(
                custom_id="games_only",
                label="Games Only",
                placeholder="True/False",
            )
        )
        self.add_item(
            InputText(
                custom_id="remote_only",
                label="Remote Only",
                placeholder="True/False",
            )
        )

    @property
    def job_query(self) -> JobQuery:

        return JobQuery(
            query=self.children[0].value if self.children[0].value else "",
            locations=self.children[1].value if self.children[1].value else "",
            games_only=bool(self.children[2].value.lower()) if self.children[2].value else False,
            remote_only=bool(self.children[3].value.lower()) if self.children[3].value else False,
            creator_discord_id=self.discord_user_id,
        )

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer(ephemeral=True)


class JobQueryEmbed(Embed):
    def __init__(self, job_query: JobQuery) -> None:
        super().__init__(title="Job Query Info", color=Color.blue())

        self.add_field(name="ID", value=f"```{str(job_query.id)}```", inline=False)
        self.add_field(name="Query", value=f"```{job_query.query}```", inline=False)
        self.add_field(name="Locations", value=f"```{job_query.locations}```", inline=False)
        self.add_field(
            name="Games Only",
            value="✅" if job_query.games_only else "❌",
        )
        self.add_field(
            name="Remote Only",
            value="✅" if job_query.remote_only else "❌",
        )
        self.add_field(
            name="Experience Level",
            value=f"```{job_query.experience.name}```",
            inline=False,
        )
        self.add_field(
            name="Created Date",
            value=f"```{job_query.creation_date}```",
            inline=False,
        )
        self.add_field(
            name="Query Owner",
            value=f"```<@{job_query.creator_discord_id}>```",
            inline=False,
        )


class JobQueryCog(Cog, name="JobQuery"):

    def __init__(self, li_bot: LinkedInDiscordBot) -> None:
        self.li_bot = li_bot

    job_query_commands = SlashCommandGroup(name="query", desc="Commands related to job queries.")

    @job_query_commands.command(name="list", help="List all registered job search queries.")
    async def list_job_queries(self, ctx: ApplicationContext) -> None:
        """List all job queries."""
        await ctx.respond("Checking the database for job queries...", ephemeral=True)
        job_queries = self.li_bot.db_client.get_job_queries()

        if not job_queries:
            await ctx.send_followup("No job queries found.")
            return

        # Create a table to display the job queries
        table = PrettyTable()
        table.field_names = ["Query ID", "Query", "Locations", "Games Only", "Remote Only"]
        for job_query in job_queries:
            table.add_row(
                [
                    job_query.id,
                    job_query.query,
                    job_query.locations,
                    "Yes" if job_query.games_only else "No",
                    "Yes" if job_query.remote_only else "No",
                ]
            )

        # Send the table as a follow-up message
        await ctx.send_followup(f"```{table}```", ephemeral=True)

    @job_query_commands.command(name="get", help="Get a job search query by ID.")
    async def get_job_query(
        self,
        ctx: ApplicationContext,
        job_query_id: Annotated[str, Option(description="The Job Query ID to get")],
    ) -> None:
        """Get a job query by ID."""
        await ctx.respond("Fetching the job query...", ephemeral=True)
        job_query = self.li_bot.db_client.get_job_query(job_query_id)

        if not job_query:
            await ctx.send_followup(
                f"Job query with ID '{job_query_id}' not found.", ephemeral=True
            )
            return

        # Create an embed to display the job query
        job_query_embed = JobQueryEmbed(job_query)
        await ctx.send_followup(embed=job_query_embed, ephemeral=True)

    @job_query_commands.command(name="create", help="Add a new job search query.")
    async def create_job_query(self, ctx: ApplicationContext) -> None:
        """Add a new job query."""
        # await ctx.respond("Adding the job query...", ephemeral=True)
        # self.li_bot.db_client.create_job_query(query, locations, games_only, remote_only)
        # await ctx.send_followup(f"Job query '{query}' added successfully.", ephemeral=True)

        create_modal = JobQueryCreateModal(ctx.user.id)
        await ctx.send_modal(create_modal)
        await create_modal.wait()

        job_query_embed = JobQueryEmbed(create_modal.job_query)

        await ctx.send_followup(
            content="Adding new job query:", embed=job_query_embed, ephemeral=True
        )

        self.li_bot.db_client.create_job_query_from_object(create_modal.job_query)

        await ctx.send_followup(
            content="Job query added successfully!",
            embed=job_query_embed,
            ephemeral=True,
        )

    @job_query_commands.command(name="delete", help="Delete a job search query.")
    async def delete_job_query(
        self,
        ctx: ApplicationContext,
        job_query_id: Annotated[str, Option(description="The Job Query ID to delete")],
    ) -> None:
        """Delete a job query."""
        await ctx.respond("Deleting the job query...", ephemeral=True)
        self.li_bot.db_client.delete_job_query(job_query_id)
        await ctx.send_followup(f"Job query '{job_query_id}' deleted successfully.", ephemeral=True)


def setup(li_bot: LinkedInDiscordBot) -> None:
    """Cog Setup Function"""
    li_bot.add_cog(JobQueryCog(li_bot))
