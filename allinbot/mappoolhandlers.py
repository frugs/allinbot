import random
import discord
from .handler import Handler

MAPS = [
    "Frozen Temple",
    "Frost",
    "Dasan Station",
    "Apotheosis",
    "King Sejong Station",
    "New Gettysburg"
]


class ChooseMapHandler(Handler):

    def can_handle_message(self, message: discord.Message):
        return message.content == "!choosemap"

    async def handle_message(self, client: discord.Client, message: discord.Message):
        random.seed()
        random_map = random.choice(MAPS)
        await client.send_message(message.channel, random_map)

    def description(self):
        return "!choosemap - Suggests a random 1v1 Ladder map"


class MapPoolHandler(Handler):

    def can_handle_message(self, message: discord.Message):
        return message.content == "!mappool"

    async def handle_message(self, client: discord.Client, message: discord.Message):
        maps = "\n".join(MAPS)
        await client.send_message(message.channel, maps)

    def description(self):
        return "!mappool - Prints the current 1v1 Ladder map pool"
