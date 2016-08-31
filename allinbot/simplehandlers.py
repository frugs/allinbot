from typing import Awaitable
import discord


async def logging_handler(client: discord.Client, message: discord.Message) -> Awaitable[bool]:
    print(message.channel)
    print(message.author)
    print(message.content)
    return True


async def test_handler(client: discord.Client, message: discord.Message) -> Awaitable[bool]:
    if message.content.startswith("!test"):
        await client.send_message(message.channel, "test!")
        return True

    return False
