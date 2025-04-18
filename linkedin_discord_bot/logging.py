import logging

from linkedin_discord_bot.settings import bot_settings


def get_logger() -> logging.Logger:
    """Create and configure a logger for the LinkedIn Discord Bot.

    Returns:
        logging.Logger: Configured logger instance.
    """

    app_logger = logging.getLogger("linkedin-discord-bot")

    # Set the logging level
    app_logger.setLevel(bot_settings.log_level)

    # Set the logging format
    log_format = "%(asctime)s %(levelname)s [%(name)s] - %(message)s"
    log_formatter = logging.Formatter(log_format)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    app_logger.addHandler(console_handler)

    # Create a file handler if enabled
    if bot_settings.log_file_enabled:
        file_handler = logging.FileHandler(bot_settings.log_file)
        file_handler.setFormatter(log_formatter)
        app_logger.addHandler(file_handler)

    return app_logger


LOG = get_logger()
