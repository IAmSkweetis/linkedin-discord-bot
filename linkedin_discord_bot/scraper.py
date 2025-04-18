from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import EventData, EventMetrics, Events
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters
from linkedin_jobs_scraper.query import Query, QueryFilters, QueryOptions

from linkedin_discord_bot.db import DBClient
from linkedin_discord_bot.logging import LOG
from linkedin_discord_bot.models import JobQuery


# Callbacks for events
def on_data(data: EventData) -> None:
    LOG.debug(
        "[ON_DATA]",
        data.title,
        data.company,
        data.company_link,
        data.date,
        data.date_text,
        data.link,
        data.insights,
        len(data.description),
    )


def on_metrics(metrics: EventMetrics) -> None:
    LOG.info("[ON_METRICS]", str(metrics))


def on_error(error: BaseException) -> None:
    LOG.error("[ON_ERROR]", error)


def on_end() -> None:
    LOG.info("[ON_END]")


class Scraper:
    scraper: LinkedinScraper
    db_client: DBClient

    def __init__(self) -> None:
        LOG.debug("Initializing Scraper...")
        self.scraper = LinkedinScraper()

        LOG.debug("Initializing DBClient...")
        self.db_client = DBClient()

        LOG.debug("Adding event listeners to the scraper...")
        self.scraper.on(Events.DATA, on_data)
        self.scraper.on(Events.ERROR, on_error)
        self.scraper.on(Events.END, on_end)

    def __construct_scraper_query(self, job_query: JobQuery) -> Query:
        LOG.debug("Constructing queries from DB...")

        query = Query(
            query=job_query.query,
            options=QueryOptions(
                locations=job_query.locations.split(","),
                apply_link=True,
                skip_promoted_jobs=True,
                page_offset=2,
                limit=5,
                filters=QueryFilters(
                    relevance=RelevanceFilters.RECENT,
                    time=TimeFilters.DAY,
                    type=[TypeFilters.FULL_TIME],
                    on_site_or_remote=job_query.on_site_or_remote,
                    experience=job_query.experience,
                ),
            ),
        )

        return query

    def run(self) -> None:

        LOG.debug("Checking for queries in the db...")
        job_queries = self.db_client.get_job_queries()

        if not job_queries:
            LOG.error("No job queries found.")
            return

        for job_query in job_queries:
            LOG.debug(f"Preparing to scrape job query: {job_query.id}")
            query = self.__construct_scraper_query(job_query)

            LOG.debug(f"Scraping job query: {query}")
            self.scraper.run(query)
