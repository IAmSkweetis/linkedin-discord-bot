from unittest.mock import patch

from typer.testing import CliRunner

from linkedin_discord_bot.cli.main import top_level_cli


def test_get_bot_status(cli_runner_fixture: CliRunner):
    """Tests the get_bot_status command."""
    result = cli_runner_fixture.invoke(top_level_cli, ["bot", "status"])
    assert result.exit_code == 0
    assert "Status is not currently implemented." in result.output


def test_start_bot(cli_runner_fixture: CliRunner):
    """Tests the start_bot command."""
    with patch("linkedin_discord_bot.cli.bot.start_linkedin_discord_bot") as mock_start:
        result = cli_runner_fixture.invoke(top_level_cli, ["bot", "start"])
        assert result.exit_code == 0
        print(result.output)
        # assert "Starting LinkedIn Discord Bot..." in result.output
        # Verify that the function was actually called
        mock_start.assert_called_once()
