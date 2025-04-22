import typer

from linkedin_discord_bot.discord import start_linkedin_discord_bot

bot_cli = typer.Typer(help="Commands to manage the discord bot.", no_args_is_help=True)


@bot_cli.command(name="status", help="Current status of the Discord bot.")
def get_bot_status() -> None:
    """Current status of the discord bot."""
    pass


@bot_cli.command(name="start", help="Start the Discord Bot.")
def start_bot() -> None:
    """Starts the Discord via the CLI."""

    start_linkedin_discord_bot()
