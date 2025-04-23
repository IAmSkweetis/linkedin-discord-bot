from unittest.mock import MagicMock, patch

import pytest

from linkedin_discord_bot.cli.main import top_level_cli  # noqa: F401


@pytest.fixture
def mock_top_level_cli():
    """Fixture to patch the top_level_cli function."""
    with patch("linkedin_discord_bot.cli.main.top_level_cli") as mock_cli:
        yield mock_cli


def test_main_calls_top_level_cli(mock_top_level_cli: MagicMock):
    """Test that __main__.py calls top_level_cli with the correct arguments."""
    # Import the module which will trigger the call to top_level_cli
    import linkedin_discord_bot.cli.__main__  # noqa: F401

    # Verify that top_level_cli was called once with the expected arguments
    mock_top_level_cli.assert_called_once_with(prog_name="Linkedin Discord Bot CLI")
