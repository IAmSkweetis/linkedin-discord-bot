import typer

from linkedin_discord_bot.scraper import Scraper

scraper_cli = typer.Typer(help="Commands related to the LinkedIn scraper.", no_args_is_help=True)


@scraper_cli.command(name="start", help="Start the LinkedIn scraper.")
def start_scraper() -> None:
    """Start the LinkedIn scraper."""

    # Placeholder for the actual implementation
    typer.secho("Starting the LinkedIn scraper...", fg=typer.colors.GREEN)

    # Initialize the scraper
    scraper = Scraper()

    # Start the scraper
    scraper.run()
