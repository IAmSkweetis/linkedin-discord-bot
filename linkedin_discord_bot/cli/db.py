import typer

from linkedin_discord_bot.db import DBClient
from linkedin_discord_bot.settings import bot_settings

db_cli = typer.Typer(help="Commands related to the database.", no_args_is_help=True)


@db_cli.command(name="init", help="Initialize the database.")
def initialize_database() -> None:
    """Initialize the database."""
    typer.secho(
        f"Initializing the database at {bot_settings.db_connection_string}", fg=typer.colors.GREEN
    )
    db_client = DBClient()
    if not db_client.verify_db():
        typer.secho("Database initialization failed.", fg=typer.colors.RED)

    typer.secho("Database initialized successfully.", fg=typer.colors.GREEN)
