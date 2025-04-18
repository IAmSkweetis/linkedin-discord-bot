class LinkedInBotBaseException(Exception):
    """Base exception for LinkedIn bot errors."""

    pass


class LinkedInBotConfigError(LinkedInBotBaseException):
    """Exception raised for configuration errors in the LinkedIn bot."""

    pass


class LinkedInBotDatabaseError(LinkedInBotBaseException):
    """Exception raised for database-related errors in the LinkedIn bot."""

    pass


class LinkedInBotAPIError(LinkedInBotBaseException):
    """Exception raised for API-related errors in the LinkedIn bot."""

    pass
