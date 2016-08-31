from typing import Awaitable
import random
import discord

MAPS = [
    "Frozen Temple",
    "Frost",
    "Dasan Station",
    "Apotheosis",
    "King Sejong Station",
    "New Gettysburg"
]


async def choose_map_handler(client: discord.Client, message: discord.Message) -> Awaitable[bool]:
    if message.content == "!choosemap":
        random.seed()
        random_map = random.choice(MAPS)
        await client.send_message(message.channel, random_map)
        return True

    return False
