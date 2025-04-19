import typer

from linkedin_discord_bot import __version__

version_cli = typer.Typer(help="Commands related to the version.")


@version_cli.command()
def version() -> None:
    """Print the version of the LinkedIn Discord Bot."""
    typer.secho(f"LinkedIn Discord Bot v{__version__}", fg=typer.colors.BLUE)
