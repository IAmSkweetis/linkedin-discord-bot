import typer
from typing_extensions import Annotated

from linkedin_discord_bot.db import DBClient

jobs_cli = typer.Typer(help="Commands related to job postings.", no_args_is_help=True)
job_queries_cli = typer.Typer(help="Commands related to job queries.", no_args_is_help=True)


@job_queries_cli.command(name="list", help="List all registered job search queries.")
def list_job_queries() -> None:
    """List all job queries."""
    # Placeholder for the actual implementation
    typer.secho("Querying for job searches...", fg=typer.colors.GREEN)

    db_client = DBClient()
    job_queries = db_client.get_job_queries()

    if not job_queries:
        typer.secho("No job queries found.", fg=typer.colors.RED)
        return

    for job_query in job_queries:
        typer.secho(f"Job Query ID: {job_query.id}", fg=typer.colors.BLUE)
        typer.secho(f"Query: {job_query.query}", fg=typer.colors.YELLOW)
        typer.secho(f"Locations: {job_query.locations}", fg=typer.colors.YELLOW)
        typer.secho(f"Location Type: {job_query.on_site_or_remote.name}", fg=typer.colors.YELLOW)
        typer.secho(f"Experience Level: {job_query.experience.name}", fg=typer.colors.YELLOW)
        typer.secho("-" * 40, fg=typer.colors.WHITE)


@job_queries_cli.command(name="create", help="Add a new job search query.")
def create_job_query(
    query: Annotated[str, typer.Option(help="The job search query string. Typically a job title.")],
    locations: Annotated[
        str, typer.Option(help="A comma seperated list of locations to search.")
    ] = "United States",
) -> None:
    typer.secho("Creating a new job query...", fg=typer.colors.GREEN)
    typer.secho(f"Query: {query}", fg=typer.colors.YELLOW)
    typer.secho(f"Locations: {locations}", fg=typer.colors.YELLOW)

    db_client = DBClient()
    db_client.create_job_query(query=query, locations=locations)


# Add our subcommands to the main jobs CLI
jobs_cli.add_typer(job_queries_cli, name="queries")
