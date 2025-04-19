from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import EventData, EventMetrics, Events
from linkedin_jobs_scraper.filters import (
    IndustryFilters,
    OnSiteOrRemoteFilters,
    RelevanceFilters,
    TimeFilters,
    TypeFilters,
)
from linkedin_jobs_scraper.query import Query, QueryFilters, QueryOptions

from linkedin_discord_bot.db import DBClient
from linkedin_discord_bot.logging import LOG
from linkedin_discord_bot.models import Job, JobQuery
from linkedin_discord_bot.utils import sanitize_url

db_client = DBClient()


# Callbacks for events
def on_data(data: EventData) -> None:
    LOG.debug(f"[ON_DATA] Found job: {data.job_id}")

    job_link = sanitize_url(data.link)

    job = Job(
        location=data.location,
        job_id=int(data.job_id),
        link=job_link.encoded_string(),
        apply_link=data.apply_link if data.apply_link else None,
        title=data.title,
        company=data.company,
        company_link=data.company_link if data.company_link else None,
        company_img_link=data.company_img_link if data.company_img_link else None,
        place=data.place,
        description=data.description,
        description_html=data.description_html,
        date=data.date,
        date_text=data.date_text,
    )

    LOG.debug(f"[ON_DATA] Adding job to DB: {job.job_id}")

    db_client.create_job(job)


def on_metrics(metrics: EventMetrics) -> None:
    LOG.info("[ON_METRICS]", str(metrics))


def on_error(error: BaseException) -> None:
    LOG.info("[ON_ERROR]", error)


def on_end() -> None:
    LOG.info("[ON_END]")


class Scraper:
    scraper: LinkedinScraper
    db_client: DBClient

    def __init__(self) -> None:
        LOG.debug("Initializing Scraper...")
        self.scraper = LinkedinScraper(max_workers=1, slow_mo=1.3)

        LOG.debug("Initializing DBClient...")
        self.db_client = DBClient()

        LOG.debug("Adding event listeners to the scraper...")
        self.scraper.on(Events.DATA, on_data)
        self.scraper.on(Events.ERROR, on_error)
        self.scraper.on(Events.END, on_end)

    def __construct_scraper_query(self, job_query: JobQuery) -> Query:
        LOG.debug("Constructing queries from DB...")

        query_filters = QueryFilters(
            relevance=RelevanceFilters.RECENT,
            time=TimeFilters.WEEK,
            type=[TypeFilters.FULL_TIME],
            experience=[job_query.experience],
        )

        if job_query.games_only:
            query_filters.industry = [IndustryFilters.COMPUTER_GAMES]

        if job_query.remote_only:
            query_filters.on_site_or_remote = [OnSiteOrRemoteFilters.REMOTE]

        query = Query(
            query=job_query.query,
            options=QueryOptions(
                locations=job_query.locations.split(","),
                apply_link=True,
                skip_promoted_jobs=True,
                page_offset=2,
                limit=5,
                filters=query_filters,
            ),
        )

        LOG.debug(f"Scraper Query: {query}")

        return query

    def run(self) -> bool:

        LOG.debug("Checking for queries in the db...")
        job_queries = self.db_client.get_job_queries()

        if not job_queries:
            LOG.error("No job queries found.")
            return False

        for job_query in job_queries:
            LOG.debug(f"Preparing to scrape job query: {job_query.id}")
            query = self.__construct_scraper_query(job_query)

            LOG.debug(f"Scraping job query: {query}")
            self.scraper.run(query)

            # NOTE: We assume that any jobs in the DB that do not have a query_id are from the last run.
            LOG.debug(f"Grabbing all the jobs from the query: {query}")
            jobs = self.db_client.get_jobs()
            if not jobs:
                LOG.error("No jobs found.")
                continue

            with db_client.db_session:
                # Filter jobs that do not have a query_id
                for job in jobs:
                    if job.query_id == job_query.id:
                        LOG.debug("Query already has correct query_id")
                        continue
                    LOG.debug(f"Updating job {job.job_id} with query_id {job_query.id}")
                    job.query_id = job_query.id
                    db_client.db_session.add(job)
                    db_client.db_session.commit()
                    db_client.db_session.refresh(job)

        LOG.debug("Scraping completed.")
        return True
