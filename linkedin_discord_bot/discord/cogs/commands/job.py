from discord import ApplicationContext, Cog, SlashCommandGroup

from linkedin_discord_bot.discord import LinkedInDiscordBot


class JobCog(Cog, name="Job"):

    def __init__(self, li_bot: LinkedInDiscordBot) -> None:
        self.li_bot = li_bot

    job_commands = SlashCommandGroup(name="job", desc="Commands related to job postings.")

    # Job top-level Commands
    @job_commands.command(name="list", help="Returns a list of all jobs.")
    async def job_list(self, ctx: ApplicationContext) -> None:
        await ctx.respond("Here's all the jobs I found!")


def setup(li_bot: LinkedInDiscordBot) -> None:
    """Cog Setup Function"""
    li_bot.add_cog(JobCog(li_bot))
