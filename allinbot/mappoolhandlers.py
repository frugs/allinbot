import random
import discord
from .handler import Handler

MAPS = [
    "Daybreak LE",
    "Echo LE",
    "Habitation Station LE",
    "Newkirk Precinct TE",
    "Overgrowth LE",
    "Vaani Research Station",
    "Whirlwind LE"
]


class ChooseMapHandler(Handler):
    """
    Handler which selects a random map from the map pool and messages it
    """

    def can_handle_message(self, message: discord.Message):
        return message.content == "!choosemap"

    async def handle_message(self, client: discord.Client, message: discord.Message):
        random.seed()
        random_map = random.choice(MAPS)
        await client.send_message(message.channel, random_map)

    def description(self):
        return "!choosemap - Suggests a random 1v1 Ladder map"


class MapPoolHandler(Handler):
    """
    Handler which messages the current map pool
    """

    def can_handle_message(self, message: discord.Message):
        return message.content == "!mappool"

    async def handle_message(self, client: discord.Client, message: discord.Message):
        maps = "\n".join(MAPS)
        await client.send_message(message.channel, maps)

    def description(self):
        return "!mappool - Prints the current 1v1 Ladder map pool"
