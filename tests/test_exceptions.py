import pytest

from linkedin_discord_bot.exceptions import LinkedInBotBaseException, LinkedInBotConfigError


def test_linkedin_bot_base_exception():
    with pytest.raises(LinkedInBotBaseException, match="Base exception test"):
        raise LinkedInBotBaseException("Base exception test")


def test_linkedin_bot_config_error():
    with pytest.raises(LinkedInBotConfigError, match="Config error test"):
        raise LinkedInBotConfigError("Config error test")
