class LinkedInBotBaseException(Exception):
    """Base exception for LinkedIn bot errors."""

    pass


class LinkedInBotConfigError(LinkedInBotBaseException):
    """Exception raised for configuration errors in the LinkedIn bot."""

    pass
