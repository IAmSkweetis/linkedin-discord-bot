from discord import ApplicationContext, Cog, slash_command

from linkedin_discord_bot.core.discord import LinkedInDiscordBot
from linkedin_discord_bot.core.linkedin import LinkedInClient


class UtilsCog(Cog):

    # Commands
    @slash_command(name="balance", help="Returns the Proxycurl API Credit Balance.")
    async def proxycurl_balance(self, ctx: ApplicationContext) -> None:
        await ctx.respond("Fetching your Proxycurl API Credit Balance...", ephemeral=True)
        balance = await LinkedInClient().get_balance()
        await ctx.send(content=f"Proxycurl credit balance: ```{balance}```")


def setup(li_bot: LinkedInDiscordBot) -> None:
    """Cog Setup Function"""
    li_bot.add_cog(UtilsCog())
