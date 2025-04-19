import typer
from typing_extensions import Annotated

from linkedin_discord_bot.db import DBClient

jobs_cli = typer.Typer(help="Commands related to job postings.", no_args_is_help=True)


@jobs_cli.command(name="list", help="List all registered job postings.")
def list_jobs() -> None:
    """List all job postings in the database."""

    db_client = DBClient()
    job_postings = db_client.get_jobs()

    if not job_postings:
        typer.secho("No job postings found.", fg=typer.colors.RED)
        return
    for job in job_postings:
        if job.query_id:
            job_query = db_client.get_job_query(job.query_id)

        typer.secho(f"Job ID: {job.job_id}", fg=typer.colors.BLUE)
        if job_query:
            typer.secho(f"Query: {job_query.query}", fg=typer.colors.BLUE)
        typer.secho(f"Title: {job.title}", fg=typer.colors.YELLOW)
        typer.secho(f"Company: {job.company}", fg=typer.colors.YELLOW)
        typer.secho(f"Location: {job.location}", fg=typer.colors.YELLOW)
        typer.secho(f"Link: {job.link}", fg=typer.colors.YELLOW)
        typer.secho("-" * 40, fg=typer.colors.WHITE)


# Job Queries CLI Subcommand
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
        typer.secho(f"Games Only: {job_query.games_only}", fg=typer.colors.YELLOW)
        typer.secho(f"Remote Only: {job_query.remote_only}", fg=typer.colors.YELLOW)
        typer.secho("-" * 40, fg=typer.colors.WHITE)


@job_queries_cli.command(name="create", help="Add a new job search query.")
def create_job_query() -> None:
    query = typer.prompt(
        "Enter the job search query string (e.g., 'Software Engineer'): ",
        default="Software Engineer",
    )
    locations = typer.prompt(
        "Enter the locations to search (comma separated, e.g., 'United States, Canada'): ",
        default="United States",
    )
    games_only = typer.confirm(
        "Do you want to search for games only?",
        default=False,
    )
    remote_only = typer.confirm(
        "Do you want to search for remote jobs only?",
        default=False,
    )

    typer.secho("Creating a new job query...", fg=typer.colors.GREEN)
    typer.secho(f"Query: {query}", fg=typer.colors.YELLOW)
    typer.secho(f"Locations: {locations}", fg=typer.colors.YELLOW)
    typer.secho(f"Games Only: {games_only}", fg=typer.colors.YELLOW)
    typer.secho(f"On-Site or Remote: {remote_only}", fg=typer.colors.YELLOW)

    db_client = DBClient()
    db_client.create_job_query(
        query=query, locations=locations, games_only=games_only, remote_only=remote_only
    )


@job_queries_cli.command(name="search", help="Search for a job search query.")
def search_job_query(
    query: Annotated[str, typer.Option(help="The job search query string. Typically a job title.")],
    locations: Annotated[
        str, typer.Option(help="A comma seperated list of locations to search.")
    ] = "United States",
) -> None:
    """Search for a job query."""
    # Placeholder for the actual implementation
    typer.secho("Searching for job queries...", fg=typer.colors.GREEN)

    db_client = DBClient()
    job_query = db_client.get_job_query_by_query(query=query, locations=locations)

    if not job_query:
        typer.secho("No job queries found.", fg=typer.colors.RED)
        return

    typer.secho(f"Job Query ID: {job_query.id}", fg=typer.colors.BLUE)
    typer.secho(f"Query: {job_query.query}", fg=typer.colors.YELLOW)
    typer.secho(f"Locations: {job_query.locations}", fg=typer.colors.YELLOW)
    typer.secho(f"Games Only: {job_query.games_only}", fg=typer.colors.YELLOW)
    typer.secho(f"Remote Only: {job_query.remote_only}", fg=typer.colors.YELLOW)


# Add our subcommands to the main jobs CLI
jobs_cli.add_typer(job_queries_cli, name="query")
