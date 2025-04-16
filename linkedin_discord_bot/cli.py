import typer

from linkedin_discord_bot import __version__
from linkedin_discord_bot.linkedin import get_balance

cli = typer.Typer(no_args_is_help=True)


@cli.command()
def version():
    print(__version__)


@cli.command()
def proxycurl_balance():
    balance = get_balance()
    print(balance)
