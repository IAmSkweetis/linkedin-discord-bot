from linkedin_jobs_scraper.events import EventData, EventMetrics

from linkedin_discord_bot.db import DBClient
from linkedin_discord_bot.logging import LOG
from linkedin_discord_bot.models import Job
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
