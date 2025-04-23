import uuid
from unittest.mock import Mock, patch

import pytest
from linkedin_jobs_scraper.filters.filters import ExperienceLevelFilters
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from linkedin_discord_bot.db import DBClient
from linkedin_discord_bot.exceptions import LinkedInBotDatabaseError
from linkedin_discord_bot.models import Job, JobQuery


def test_init_with_engine_and_session(
    database_engine_fixture: Engine, database_session_fixture: Session
):
    """Test that DBClient can be initialized with an engine and session."""
    client = DBClient(db_engine=database_engine_fixture, db_session=database_session_fixture)
    assert client.db_engine == database_engine_fixture
    assert client.db_session == database_session_fixture


def test_init_without_arguments():
    """Test that DBClient raises an exception when initialized without arguments."""
    with pytest.raises(LinkedInBotDatabaseError):
        DBClient(db_connection_string=None, db_connection_args=None, db_engine=None)


def test_init_without_engine():
    """Test that DBClient raises an exception when initialized without an engine or connection details."""
    with pytest.raises(LinkedInBotDatabaseError):
        DBClient(db_connection_string=None, db_connection_args=None)


@patch("linkedin_discord_bot.db.create_engine")
def test_init_with_connection_details(mock_create_engine, monkeypatch: pytest.MonkeyPatch):
    """Test that DBClient can be initialized with connection details."""
    # Set up mocks
    mock_engine = Mock()
    mock_create_engine.return_value = mock_engine
    monkeypatch.setattr("linkedin_discord_bot.db.SQLModel.metadata.create_all", Mock())

    # Mock verify_db to return True
    monkeypatch.setattr(DBClient, "verify_db", lambda self: True)
    monkeypatch.setattr(DBClient, "get_db_session", lambda self: Mock())

    # Initialize client
    client = DBClient(db_connection_string="sqlite:///test.db", db_connection_args={})

    # Verify
    mock_create_engine.assert_called_once_with("sqlite:///test.db", connect_args={})
    assert client.db_engine == mock_engine


def test_verify_db_success(database_client_fixture: DBClient):
    """Test verify_db success path."""
    assert database_client_fixture.verify_db() is True


@patch("linkedin_discord_bot.db.Session")
def test_verify_db_failure(mock_session):
    """Test verify_db failure path."""
    # Create a mock engine
    mock_engine = Mock()

    # Set up our client with the mock engine
    client = DBClient(db_engine=mock_engine)

    # Replace the get_db_session method to return our mock session
    original_get_db_session = client.get_db_session

    def mock_get_db_session():
        session = mock_session()
        session.__enter__.return_value.exec.side_effect = Exception("DB error")
        return session

    client.get_db_session = mock_get_db_session

    # Test the verify_db method
    result = client.verify_db()

    # Restore the original method
    client.get_db_session = original_get_db_session

    assert result is False


def test_get_job_queries(database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch):
    """Test get_job_queries returns all job queries."""
    # Create a test job query
    job_query = JobQuery(
        query="test query", locations="test location", creator_discord_id=123456789
    )

    # Mock the session exec method to return our test job query
    mock_exec = Mock()
    mock_exec.all.return_value = [job_query]
    monkeypatch.setattr(database_client_fixture.db_session, "exec", lambda _: mock_exec)

    # Call the method
    result = database_client_fixture.get_job_queries()

    # Verify
    assert len(result) == 1
    assert result[0].query == "test query"
    assert result[0].locations == "test location"


def test_get_job_queries_exception(
    database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch
):
    """Test exception handling in get_job_queries."""
    # Mock db_session with a session that raises an exception
    mock_exception = Exception("Test exception")

    def mock_exec_with_exception(query):
        raise mock_exception

    monkeypatch.setattr(database_client_fixture.db_session, "exec", mock_exec_with_exception)

    # Execute the method, it should handle the exception and return an empty list
    result = database_client_fixture.get_job_queries()

    # Verify we got an empty list back
    assert isinstance(result, list)
    assert len(result) == 0


def test_get_job_query_by_id(database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch):
    """Test get_job_query returns a job query by ID."""
    # Create a test job query
    test_id = uuid.uuid4()
    job_query = JobQuery(
        id=test_id, query="test query", locations="test location", creator_discord_id=123456789
    )

    # Mock the session exec method to return our test job query
    mock_exec = Mock()
    mock_exec.first.return_value = job_query
    monkeypatch.setattr(database_client_fixture.db_session, "exec", lambda _: mock_exec)

    # Call the method
    result = database_client_fixture.get_job_query(test_id)

    # Verify
    assert result == job_query
    assert result is not None and result.id == test_id


def test_get_job_query_by_string_id(
    database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch
):
    """Test get_job_query can handle string UUID."""
    # Create a test job query
    test_id = uuid.uuid4()
    job_query = JobQuery(
        id=test_id, query="test query", locations="test location", creator_discord_id=123456789
    )

    # Mock the session exec method to return our test job query
    mock_exec = Mock()
    mock_exec.first.return_value = job_query
    monkeypatch.setattr(database_client_fixture.db_session, "exec", lambda _: mock_exec)

    # Call the method with string UUID
    result = database_client_fixture.get_job_query(str(test_id))

    # Verify
    assert result == job_query
    assert result is not None and result.id == test_id


def test_get_job_query_invalid_uuid(database_client_fixture: DBClient):
    """Test get_job_query returns None for invalid UUID string."""
    result = database_client_fixture.get_job_query("not-a-uuid")
    assert result is None


def test_get_job_query_by_query(database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch):
    """Test get_job_query_by_query returns a job query by query parameters."""
    # Create a test job query
    job_query = JobQuery(
        query="python developer",
        locations="New York",
        games_only=True,
        remote_only=True,
        experience=ExperienceLevelFilters.ENTRY_LEVEL,
        creator_discord_id=123456789,
    )

    # Mock the session exec method to return our test job query
    mock_exec = Mock()
    mock_exec.first.return_value = job_query
    monkeypatch.setattr(database_client_fixture.db_session, "exec", lambda _: mock_exec)

    # Call the method
    result = database_client_fixture.get_job_query_by_query(
        query="python developer",
        locations="New York",
        games_only=True,
        remote_only=True,
        experience=ExperienceLevelFilters.ENTRY_LEVEL,
    )

    # Verify
    assert result == job_query
    assert result is not None
    assert result.query == "python developer"
    assert result.locations == "New York"
    assert result.games_only is True
    assert result.remote_only is True
    assert result.experience == ExperienceLevelFilters.ENTRY_LEVEL


def test_create_job_query(database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch):
    """Test create_job_query successfully creates a job query."""
    # Mock session methods to avoid actual DB operations
    mock_add = Mock()
    mock_commit = Mock()
    mock_refresh = Mock()
    mock_close = Mock()
    monkeypatch.setattr(database_client_fixture.db_session, "add", mock_add)
    monkeypatch.setattr(database_client_fixture.db_session, "commit", mock_commit)
    monkeypatch.setattr(database_client_fixture.db_session, "refresh", mock_refresh)
    monkeypatch.setattr(database_client_fixture.db_session, "close", mock_close)

    # Call the method
    database_client_fixture.create_job_query(
        query="python developer",
        locations="New York",
        games_only=True,
        remote_only=True,
        experience=ExperienceLevelFilters.ENTRY_LEVEL,
        creator_discord_id=123456789,
    )

    # Verify session methods were called
    assert mock_add.called
    assert mock_commit.called
    assert mock_refresh.called
    assert mock_close.called


def test_create_job_query_integrity_error(
    database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch
):
    """Test create_job_query handles IntegrityError."""
    # Mock add to raise IntegrityError
    mock_add = Mock(side_effect=IntegrityError("statement", "params", Exception("original error")))
    mock_rollback = Mock()
    mock_close = Mock()
    monkeypatch.setattr(database_client_fixture.db_session, "add", mock_add)
    monkeypatch.setattr(database_client_fixture.db_session, "rollback", mock_rollback)
    monkeypatch.setattr(database_client_fixture.db_session, "close", mock_close)

    # Call the method
    database_client_fixture.create_job_query(
        query="python developer", locations="New York", creator_discord_id=123456789
    )

    # Verify rollback was called
    assert mock_rollback.called
    assert mock_close.called


def test_create_job_query_from_object(
    database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch
):
    """Test create_job_query_from_object successfully creates a job query."""
    # Create a test job query object
    job_query = JobQuery(
        query="python developer",
        locations="New York",
        games_only=True,
        remote_only=True,
        experience=ExperienceLevelFilters.ENTRY_LEVEL,
        creator_discord_id=123456789,
    )

    # Mock session methods to avoid actual DB operations
    mock_add = Mock()
    mock_commit = Mock()
    mock_refresh = Mock()
    mock_close = Mock()
    monkeypatch.setattr(database_client_fixture.db_session, "add", mock_add)
    monkeypatch.setattr(database_client_fixture.db_session, "commit", mock_commit)
    monkeypatch.setattr(database_client_fixture.db_session, "refresh", mock_refresh)
    monkeypatch.setattr(database_client_fixture.db_session, "close", mock_close)

    # Call the method
    database_client_fixture.create_job_query_from_object(job_query)

    # Verify session methods were called
    assert mock_add.called
    assert mock_commit.called
    assert mock_refresh.called
    assert mock_close.called


def test_delete_job_query(database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch):
    """Test delete_job_query successfully deletes a job query."""
    # Create a test job query
    test_id = uuid.uuid4()
    job_query = JobQuery(
        id=test_id, query="test query", locations="test location", creator_discord_id=123456789
    )

    # Mock the session exec method to return our test job query
    mock_exec = Mock()
    mock_exec.first.return_value = job_query
    monkeypatch.setattr(database_client_fixture.db_session, "exec", lambda _: mock_exec)

    # Mock delete and commit methods
    mock_delete = Mock()
    mock_commit = Mock()
    mock_close = Mock()
    monkeypatch.setattr(database_client_fixture.db_session, "delete", mock_delete)
    monkeypatch.setattr(database_client_fixture.db_session, "commit", mock_commit)
    monkeypatch.setattr(database_client_fixture.db_session, "close", mock_close)

    # Call the method
    database_client_fixture.delete_job_query(test_id)

    # Verify
    assert mock_delete.called
    assert mock_commit.called
    assert mock_close.called


def test_delete_job_query_not_found(
    database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch
):
    """Test delete_job_query handles case when job query is not found."""
    # Mock the session exec method to return None
    mock_exec = Mock()
    mock_exec.first.return_value = None
    monkeypatch.setattr(database_client_fixture.db_session, "exec", lambda _: mock_exec)

    # Mock delete and close methods
    mock_delete = Mock()
    mock_close = Mock()
    monkeypatch.setattr(database_client_fixture.db_session, "delete", mock_delete)
    monkeypatch.setattr(database_client_fixture.db_session, "close", mock_close)

    # Call the method
    database_client_fixture.delete_job_query(uuid.uuid4())

    # Verify delete was not called
    assert not mock_delete.called
    assert mock_close.called


def test_delete_job_query_invalid_uuid(
    database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch
):
    """Test delete_job_query handles invalid UUID string."""
    # Mock close method
    mock_close = Mock()
    monkeypatch.setattr(database_client_fixture.db_session, "close", mock_close)

    # Call the method with invalid UUID
    database_client_fixture.delete_job_query("not-a-uuid")

    # Verify close was called
    assert mock_close.called


def test_get_job(database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch):
    """Test get_job returns a job by ID."""
    # Create a test job
    job = Job(
        job_id=12345,
        location="New York",
        link="https://linkedin.com/jobs/12345",
        title="Python Developer",
        company="Test Company",
        place="New York, NY",
        description="Job description",
        description_html="<p>Job description</p>",
        date="2023-04-22",
        date_text="1 day ago",
    )

    # Mock the session exec method to return our test job
    mock_exec = Mock()
    mock_exec.first.return_value = job
    monkeypatch.setattr(database_client_fixture.db_session, "exec", lambda _: mock_exec)

    # Call the method
    result = database_client_fixture.get_job(12345)

    # Verify
    assert result == job
    assert result is not None
    assert result.job_id == 12345
    assert result.title == "Python Developer"


def test_get_jobs_all(database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch):
    """Test get_jobs returns all jobs when no query ID is provided."""
    # Create test jobs
    jobs = [
        Job(
            job_id=12345,
            location="New York",
            link="https://linkedin.com/jobs/12345",
            title="Python Developer",
            company="Test Company",
            place="New York, NY",
            description="Job description",
            description_html="<p>Job description</p>",
            date="2023-04-22",
            date_text="1 day ago",
        ),
        Job(
            job_id=67890,
            location="San Francisco",
            link="https://linkedin.com/jobs/67890",
            title="Data Scientist",
            company="Another Company",
            place="San Francisco, CA",
            description="Another job description",
            description_html="<p>Another job description</p>",
            date="2023-04-21",
            date_text="2 days ago",
        ),
    ]

    # Mock the session exec method to return our test jobs
    mock_exec = Mock()
    mock_exec.all.return_value = jobs
    monkeypatch.setattr(database_client_fixture.db_session, "exec", lambda _: mock_exec)

    # Call the method
    result = database_client_fixture.get_jobs()

    # Verify
    assert len(result) == 2
    assert result[0].job_id == 12345
    assert result[1].job_id == 67890


def test_get_jobs_by_query_id(database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch):
    """Test get_jobs returns jobs filtered by query ID."""
    # Create a test job query ID
    test_query_id = uuid.uuid4()

    # Create test jobs
    jobs = [
        Job(
            job_id=12345,
            location="New York",
            link="https://linkedin.com/jobs/12345",
            title="Python Developer",
            company="Test Company",
            place="New York, NY",
            description="Job description",
            description_html="<p>Job description</p>",
            date="2023-04-22",
            date_text="1 day ago",
            job_query_id=test_query_id,
        )
    ]

    # Mock the session exec method to return our test jobs
    mock_exec = Mock()
    mock_exec.all.return_value = jobs
    monkeypatch.setattr(database_client_fixture.db_session, "exec", lambda _: mock_exec)

    # Call the method
    result = database_client_fixture.get_jobs(job_query_id=test_query_id)

    # Verify
    assert len(result) == 1
    assert result[0].job_id == 12345
    assert result[0].job_query_id == test_query_id


def test_get_jobs_by_string_query_id(
    database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch
):
    """Test get_jobs handles string UUID for query ID."""
    # Create a test job query ID
    test_query_id = uuid.uuid4()

    # Create test jobs
    jobs = [
        Job(
            job_id=12345,
            location="New York",
            link="https://linkedin.com/jobs/12345",
            title="Python Developer",
            company="Test Company",
            place="New York, NY",
            description="Job description",
            description_html="<p>Job description</p>",
            date="2023-04-22",
            date_text="1 day ago",
            job_query_id=test_query_id,
        )
    ]

    # Mock the session exec method to return our test jobs
    mock_exec = Mock()
    mock_exec.all.return_value = jobs
    monkeypatch.setattr(database_client_fixture.db_session, "exec", lambda _: mock_exec)

    # Call the method with string UUID
    result = database_client_fixture.get_jobs(job_query_id=str(test_query_id))

    # Verify
    assert len(result) == 1
    assert result[0].job_id == 12345
    assert result[0].job_query_id == test_query_id


def test_get_jobs_by_invalid_string_query_id(database_client_fixture: DBClient):
    """Test get_jobs raises ValueError when given an invalid string UUID."""
    # Call the method with invalid UUID string and expect ValueError
    with pytest.raises(ValueError):
        database_client_fixture.get_jobs(job_query_id="not-a-uuid")


def test_create_job(database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch):
    """Test create_job successfully creates a job."""
    # Create a test job
    job = Job(
        job_id=12345,
        location="New York",
        link="https://linkedin.com/jobs/12345",
        title="Python Developer",
        company="Test Company",
        place="New York, NY",
        description="Job description",
        description_html="<p>Job description</p>",
        date="2023-04-22",
        date_text="1 day ago",
    )

    # Mock session methods to avoid actual DB operations
    mock_add = Mock()
    mock_commit = Mock()
    mock_refresh = Mock()
    mock_close = Mock()
    monkeypatch.setattr(database_client_fixture.db_session, "add", mock_add)
    monkeypatch.setattr(database_client_fixture.db_session, "commit", mock_commit)
    monkeypatch.setattr(database_client_fixture.db_session, "refresh", mock_refresh)
    monkeypatch.setattr(database_client_fixture.db_session, "close", mock_close)

    # Call the method
    database_client_fixture.create_job(job)

    # Verify session methods were called
    assert mock_add.called
    assert mock_commit.called
    assert mock_refresh.called
    assert mock_close.called


def test_create_job_integrity_error(
    database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch
):
    """Test create_job handles IntegrityError."""
    # Create a test job
    job = Job(
        job_id=12345,
        location="New York",
        link="https://linkedin.com/jobs/12345",
        title="Python Developer",
        company="Test Company",
        place="New York, NY",
        description="Job description",
        description_html="<p>Job description</p>",
        date="2023-04-22",
        date_text="1 day ago",
    )

    # Mock add to raise IntegrityError
    mock_add = Mock(side_effect=IntegrityError("statement", "params", Exception("original error")))
    mock_rollback = Mock()
    mock_close = Mock()
    monkeypatch.setattr(database_client_fixture.db_session, "add", mock_add)
    monkeypatch.setattr(database_client_fixture.db_session, "rollback", mock_rollback)
    monkeypatch.setattr(database_client_fixture.db_session, "close", mock_close)

    # Call the method and expect exception
    with pytest.raises(LinkedInBotDatabaseError):
        database_client_fixture.create_job(job)

    # Verify rollback was called
    assert mock_rollback.called
    assert mock_close.called


def test_delete_job(database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch):
    """Test delete_job successfully deletes a job."""
    # Create a test job
    job = Job(
        job_id=12345,
        location="New York",
        link="https://linkedin.com/jobs/12345",
        title="Python Developer",
        company="Test Company",
        place="New York, NY",
        description="Job description",
        description_html="<p>Job description</p>",
        date="2023-04-22",
        date_text="1 day ago",
    )

    # Mock the session exec method to return our test job
    mock_exec = Mock()
    mock_exec.first.return_value = job
    monkeypatch.setattr(database_client_fixture.db_session, "exec", lambda _: mock_exec)

    # Mock delete and commit methods
    mock_delete = Mock()
    mock_commit = Mock()
    mock_close = Mock()
    monkeypatch.setattr(database_client_fixture.db_session, "delete", mock_delete)
    monkeypatch.setattr(database_client_fixture.db_session, "commit", mock_commit)
    monkeypatch.setattr(database_client_fixture.db_session, "close", mock_close)

    # Call the method
    database_client_fixture.delete_job(12345)

    # Verify
    assert mock_delete.called
    assert mock_commit.called
    assert mock_close.called


def test_delete_job_not_found(database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch):
    """Test delete_job handles case when job is not found."""
    # Mock the session exec method to return None
    mock_exec = Mock()
    mock_exec.first.return_value = None
    monkeypatch.setattr(database_client_fixture.db_session, "exec", lambda _: mock_exec)

    # Mock delete and close methods
    mock_delete = Mock()
    mock_close = Mock()
    monkeypatch.setattr(database_client_fixture.db_session, "delete", mock_delete)
    monkeypatch.setattr(database_client_fixture.db_session, "close", mock_close)

    # Call the method
    database_client_fixture.delete_job(12345)

    # Verify delete was not called
    assert not mock_delete.called
    assert mock_close.called


def test_delete_job_error(database_client_fixture: DBClient, monkeypatch: pytest.MonkeyPatch):
    """Test delete_job handles exceptions."""
    # Create a test job
    job = Job(
        job_id=12345,
        location="New York",
        link="https://linkedin.com/jobs/12345",
        title="Python Developer",
        company="Test Company",
        place="New York, NY",
        description="Job description",
        description_html="<p>Job description</p>",
        date="2023-04-22",
        date_text="1 day ago",
    )

    # Mock the session exec method to return our test job
    mock_exec = Mock()
    mock_exec.first.return_value = job
    monkeypatch.setattr(database_client_fixture.db_session, "exec", lambda _: mock_exec)

    # Mock delete to raise an exception
    mock_delete = Mock(side_effect=Exception("Delete error"))
    mock_rollback = Mock()
    mock_close = Mock()
    monkeypatch.setattr(database_client_fixture.db_session, "delete", mock_delete)
    monkeypatch.setattr(database_client_fixture.db_session, "rollback", mock_rollback)
    monkeypatch.setattr(database_client_fixture.db_session, "close", mock_close)

    # Call the method and expect exception
    with pytest.raises(LinkedInBotDatabaseError):
        database_client_fixture.delete_job(12345)

    # Verify rollback was called
    assert mock_rollback.called
    assert mock_close.called
