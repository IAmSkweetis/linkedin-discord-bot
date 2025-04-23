import discord.ext.test as testcord
import pytest
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from typer.testing import CliRunner

from linkedin_discord_bot.cli.main import top_level_cli  # noqa: F401
from linkedin_discord_bot.db import DBClient
from linkedin_discord_bot.discord import LinkedInDiscordBot


@pytest.fixture(scope="session")
def cli_runner_fixture():
    runner = CliRunner()
    yield runner


@pytest.fixture(scope="session")
def database_engine_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine


@pytest.fixture(scope="session")
def database_session_fixture(database_engine_fixture: Engine):
    with Session(database_engine_fixture) as session:
        yield session


@pytest.fixture(scope="session")
def database_client_fixture(database_engine_fixture: Engine, database_session_fixture: Session):
    db_client = DBClient(db_engine=database_engine_fixture, db_session=database_session_fixture)
    yield db_client


@pytest.fixture(scope="session")
def discord_bot_fixture(event_loop, database_engine_fixture: Engine):
    bot = LinkedInDiscordBot(event_loop=event_loop)
    testcord.configure(bot)
    yield bot
