import uuid
from typing import Any, Dict, List

from linkedin_jobs_scraper.filters.filters import ExperienceLevelFilters, OnSiteOrRemoteFilters
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, create_engine, select

from linkedin_discord_bot.exceptions import LinkedInBotDatabaseError
from linkedin_discord_bot.logging import LOG
from linkedin_discord_bot.models import Job, JobQuery
from linkedin_discord_bot.settings import bot_settings


class DBClient:
    db_connection_string: str
    db_connection_args: Dict[Any, Any]
    db_engine: Engine
    db_session: Session

    def __init__(
        self,
        db_connection_string: str = bot_settings.db_connection_string,
        db_connection_args: Dict[Any, Any] = bot_settings.db_connection_args,
    ) -> None:
        LOG.debug(f"Database connection string: {db_connection_string}")
        LOG.debug(f"Database connection args: {db_connection_args}")

        self.db_connection_string = db_connection_string
        self.db_connection_args = db_connection_args
        self.db_engine = create_engine(db_connection_string, connect_args=db_connection_args)

        SQLModel.metadata.create_all(self.db_engine)

        # Verify that the database is created and accessible
        if not self.verify_db():
            LOG.error("Database initialization failed.")
            raise LinkedInBotDatabaseError("Database initialization failed.")

        LOG.debug("Database initialized successfully.")

        self.db_session = self.get_db_session()

    def get_db_session(self) -> Session:
        return Session(self.db_engine)

    def verify_db(self) -> bool:
        try:
            with self.get_db_session() as session:
                # Perform a simple query to check if the database is accessible
                statement = select(1)
                test_query = session.exec(statement).all()

                LOG.debug(f"Test query result: {test_query}")

                if not test_query:
                    LOG.error("Database verification failed: No results returned.")
                    return False

                LOG.debug("Database verification successful.")
                return True

        except Exception as err:
            LOG.error(f"Database verification failed: {err}")
            LOG.error(type(err))
            return False

    def get_job_queries(self) -> List[JobQuery]:
        LOG.debug("Fetching all job queries from the database.")
        with self.db_session:
            job_queries = self.db_session.exec(select(JobQuery)).all()
        return list(job_queries)

    def get_job_query(self, job_query_id: str | uuid.UUID) -> JobQuery | None:
        """Get a job query by its ID."""
        if isinstance(job_query_id, str):
            try:
                job_query_id = uuid.UUID(job_query_id)
            except ValueError:
                LOG.error(f"Invalid UUID string: {job_query_id}")
                return None

        LOG.debug(f"Searching for job query with ID: {job_query_id}")
        with self.db_session:
            job_query = self.db_session.exec(
                select(JobQuery).where(JobQuery.id == job_query_id)
            ).first()
        return job_query

    def get_job_query_by_query(
        self,
        query: str,
        locations: str = "United States",
        on_site_or_remote: OnSiteOrRemoteFilters = OnSiteOrRemoteFilters.REMOTE,
        experience: ExperienceLevelFilters = ExperienceLevelFilters.MID_SENIOR,
    ) -> JobQuery | None:
        """Get a job query by its query string."""
        LOG.debug(f"Searching for job query with query: {query}")
        with self.db_session:
            job_query = self.db_session.exec(
                select(JobQuery)
                .where(JobQuery.query == query)
                .where(JobQuery.locations == locations)
                .where(JobQuery.remote_only == on_site_or_remote)
                .where(JobQuery.experience == experience)
            ).first()
        return job_query

    def create_job_query(
        self,
        query: str,
        locations: str = "United States",
        games_only: bool = False,
        remote_only: bool = False,
        experience: ExperienceLevelFilters = ExperienceLevelFilters.MID_SENIOR,
    ) -> None:
        """Create a job query for the given locations."""

        job_query = JobQuery(
            query=query,
            locations=locations,
            games_only=games_only,
            remote_only=remote_only,
            experience=experience,
        )

        LOG.debug(f"Creating job query: {job_query}")
        try:
            self.db_session.add(job_query)
            self.db_session.commit()
            self.db_session.refresh(job_query)
        except IntegrityError as err:
            LOG.warning(f"Job query already exists: {err}")
            LOG.debug(err)
            self.db_session.rollback()
            raise LinkedInBotDatabaseError(f"Job query already exists: {err}")
        finally:
            self.db_session.close()

    def job_exists_in_db(self, job_id: int) -> bool:
        """Check if a job query exists in the database."""
        LOG.debug(f"Checking if job with ID {job_id} exists in the database.")
        with self.db_session:
            job = self.db_session.exec(select(Job).where(Job.job_id == job_id)).first()
        return job is not None

    def get_job(self, job_id: int) -> Job | None:
        """Get a job query by its ID."""
        LOG.debug(f"Searching for job with ID: {job_id}")
        with self.db_session:
            job = self.db_session.exec(select(Job).where(Job.job_id == job_id)).first()
        return job

    def get_jobs(self, query_id: uuid.UUID | None = None) -> List[Job]:
        """Get all job queries."""
        LOG.debug("Fetching all jobs from the database.")
        with self.db_session:
            if query_id is None:
                job_queries = self.db_session.exec(select(Job)).all()
            else:
                job_queries = self.db_session.exec(
                    select(Job).where(Job.query_id == query_id)
                ).all()
        return list(job_queries)

    def create_job(self, job: Job) -> None:
        """Create a job query for the given locations."""
        LOG.debug(f"Creating job: {job.job_id}")

        if self.job_exists_in_db(job.job_id):
            LOG.debug(f"Job {job.job_id} already exists in the database.")
            return

        try:
            self.db_session.add(job)
            self.db_session.commit()
            self.db_session.refresh(job)
        except IntegrityError as err:
            LOG.warning(f"Job already exists: {err}")
            LOG.debug(err)
            self.db_session.rollback()
            raise LinkedInBotDatabaseError(f"Job already exists: {err}")
        finally:
            self.db_session.close()

    def delete_job(self, job_id: int) -> None:
        """Delete a job query by its ID."""
        LOG.debug(f"Deleting job with ID: {job_id}")
        try:
            job = self.db_session.exec(select(Job).where(Job.job_id == job_id)).first()
            if job:
                self.db_session.delete(job)
                self.db_session.commit()
            else:
                LOG.warning(f"Job with ID {job_id} not found.")
        except Exception as err:
            LOG.error(f"Error deleting job with ID {job_id}: {err}")
            self.db_session.rollback()
            raise LinkedInBotDatabaseError(f"Error deleting job with ID {job_id}: {err}")
        finally:
            self.db_session.close()
