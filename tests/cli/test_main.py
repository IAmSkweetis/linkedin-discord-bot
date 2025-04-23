from typer.testing import CliRunner

from linkedin_discord_bot.cli.main import top_level_cli


def test_top_level_cli(cli_runner_fixture: CliRunner):
    """Tests the top level CLI command."""
    result = cli_runner_fixture.invoke(top_level_cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "Options" in result.output
    assert "Commands" in result.output
    assert "A Discord bot that posts LinkedIn job postings." in result.output
