import logging

from linkedin_discord_bot.core.logging import get_logger
from linkedin_discord_bot.core.settings import bot_settings


def test_get_logger_with_console_handler(mocker):
    """Test logger creation with console handler."""
    mocker.patch.object(bot_settings, "log_file_enabled", False)
    mocker.patch.object(bot_settings, "logging_level", "DEBUG")

    logger = get_logger()

    assert logger.level == logging.DEBUG
    assert any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers)


def test_get_logger_with_file_handler(mocker, tmp_path):
    """Test logger creation with file handler enabled."""
    log_file = tmp_path / "test.log"
    mocker.patch.object(bot_settings, "log_file_enabled", True)
    mocker.patch.object(bot_settings, "log_file", str(log_file))

    logger = get_logger()

    assert any(isinstance(handler, logging.FileHandler) for handler in logger.handlers)
    assert log_file.exists()
