import typer

from linkedin_discord_bot.cli.db import db_cli
from linkedin_discord_bot.cli.jobs import jobs_cli
from linkedin_discord_bot.cli.scraper import scraper_cli
from linkedin_discord_bot.cli.version import version_cli

top_level_cli = typer.Typer(
    help="A Discord bot that posts LinkedIn job postings.", no_args_is_help=True
)

# Add our subcommands to the main CLI
top_level_cli.add_typer(db_cli, name="db")
top_level_cli.add_typer(jobs_cli, name="job")
top_level_cli.add_typer(scraper_cli, name="scraper")
top_level_cli.add_typer(version_cli)
