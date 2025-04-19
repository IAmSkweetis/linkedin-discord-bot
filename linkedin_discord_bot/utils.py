from pydantic.networks import HttpUrl

from linkedin_discord_bot.logging import LOG


def sanitize_url(url: HttpUrl | str) -> HttpUrl:
    """
    Sanitize by removing any query or fragment components from the URL.

    We assume that URL is already well-formed. And that we do not need to
    worry about ports, authentication, etc.

    Args:
        url (HttpUrl | str): The URL to sanitize.

    Returns:
        HttpUrl: The sanitized URL.
    """
    LOG.debug(f"Sanitizing URL: {url}")

    if isinstance(url, str):
        LOG.debug("Converting string to HttpUrl. Consider using HttpUrl directly.")
        url = HttpUrl(url)

    # Remove query and fragment components
    sanitized_url = f"{url.scheme}://{url.host}{url.path}"

    LOG.debug(f"Sanitized URL: {sanitized_url}")

    return HttpUrl(sanitized_url)
