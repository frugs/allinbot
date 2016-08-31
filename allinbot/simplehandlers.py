from typing import Awaitable
from .handler import Handler
import discord


async def logging_handler(client: discord.Client, message: discord.Message) -> Awaitable[bool]:
    print(message.channel)
    print(message.author)
    print(message.content)
    return True


def create_ping_pong_handler(ping: str, pong: str) -> Handler:

    async def handler(client: discord.Client, message: discord.Message) -> Awaitable[bool]:
        if message.content == ping:
            await client.send_message(message.channel, pong)
            return True

        return False

    return handler