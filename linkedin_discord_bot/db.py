from typing import Any, Dict, List

from linkedin_jobs_scraper.filters.filters import ExperienceLevelFilters, OnSiteOrRemoteFilters
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, create_engine, select

from linkedin_discord_bot.exceptions import LinkedInBotDatabaseError
from linkedin_discord_bot.logging import LOG
from linkedin_discord_bot.models import JobQuery
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
        job_queries = self.db_session.exec(select(JobQuery)).all()
        return list(job_queries)

    def create_job_query(
        self,
        query: str,
        locations: str = "United States",
        on_site_or_remote: OnSiteOrRemoteFilters = OnSiteOrRemoteFilters.REMOTE,
        experience: ExperienceLevelFilters = ExperienceLevelFilters.MID_SENIOR,
    ) -> None:
        """Create a job query for the given locations."""

        job_query = JobQuery(
            query=query,
            locations=locations,
            on_site_or_remote=on_site_or_remote,
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
