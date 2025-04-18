import typer

from linkedin_discord_bot import __version__
from linkedin_discord_bot.cli.jobs import jobs_cli
from linkedin_discord_bot.cli.scraper import scraper_cli

top_level_cli = typer.Typer(
    help="A Discord bot that posts LinkedIn job postings.", no_args_is_help=True
)


@top_level_cli.command()
def version() -> None:
    """Print the version of the package."""
    typer.secho(message=f"LinkedIn Discord Bot version: {__version__}", fg=typer.colors.GREEN)


# Add our subcommands to the main CLI
top_level_cli.add_typer(jobs_cli, name="jobs")
top_level_cli.add_typer(scraper_cli, name="scraper")
