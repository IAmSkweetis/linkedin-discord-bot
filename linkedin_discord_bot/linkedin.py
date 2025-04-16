import asyncio
from proxycurl.asyncio import Proxycurl


client = Proxycurl()

def get_balance():
    return asyncio.run(client.get_balance())
