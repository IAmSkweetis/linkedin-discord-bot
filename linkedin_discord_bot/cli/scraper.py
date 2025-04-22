import typer

from linkedin_discord_bot.scraper import Scraper

scraper_cli = typer.Typer(help="Commands related to the LinkedIn scraper.", no_args_is_help=True)


@scraper_cli.command(name="run", help="Start the LinkedIn scraper.")
def run_linkedin_scraper() -> None:
    """Start the LinkedIn scraper."""

    # Placeholder for the actual implementation
    typer.secho("Starting the LinkedIn scraper...", fg=typer.colors.GREEN)

    # Initialize the scraper
    scraper = Scraper()

    # Start the scraper
    if not scraper.run():
        typer.secho(
            "Scraper failed to run. Check to make sure the DB is functional.", fg=typer.colors.RED
        )

    typer.secho("Scraper has finished running.", fg=typer.colors.GREEN)
