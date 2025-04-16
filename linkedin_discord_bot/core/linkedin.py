from typing import Dict

from proxycurl.asyncio import Proxycurl  # type: ignore

from linkedin_discord_bot.exceptions import LinkedInBotBaseException


class LinkedInClient:
    def __init__(self) -> None:
        self.client = Proxycurl()

    async def get_balance(self) -> int:
        """Retrieves the balance of the Proxycurl account.

        Raises:
            LinkedInBotBaseException: If the response is not a dictionary or does not contain the expected key.

        Returns:
            int: The credit balance of the Proxycurl account.
        """
        credit_balance: int = 0
        resp = await self.client.get_balance()

        if not isinstance(resp, Dict) or "credit_balance" not in resp:
            raise LinkedInBotBaseException("Failed to get balance")

        credit_balance = resp["credit_balance"]

        return credit_balance
