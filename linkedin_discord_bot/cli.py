import asyncio

import typer

from linkedin_discord_bot import __version__
from linkedin_discord_bot.core.linkedin import LinkedInClient

cli = typer.Typer(help="A Discord bot that posts LinkedIn job postings.", no_args_is_help=True)


@cli.command()
def version() -> None:
    """Print the version of the package."""
    typer.secho(message=f"LinkedIn Discord Bot version: {__version__}", fg=typer.colors.GREEN)


@cli.command(name="balance")
def proxycurl_balance() -> None:
    """Print the Proxycurl balance."""
    balance = asyncio.run(LinkedInClient().get_balance())
    typer.secho(message=f"Proxycurl credit balance: {balance}", fg=typer.colors.GREEN)
