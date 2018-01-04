import aiohttp
import re

import discord
import pyrebase

from allinbot.database import DatabaseTask, perform_database_task
from allinbot.handler import Handler


_TRIGGER = "!islive"
_PATTERN = re.compile("^" + _TRIGGER + "\s+<@[!]*(\d*)>$")


class FetchTwitchConnectionDatabaseTask(DatabaseTask[dict]):

    def __init__(self, db_config: dict, member: str):
        super().__init__(db_config)
        self.member = member

    def execute_with_database(self, db: pyrebase.pyrebase.Database) -> dict:
        twitch_connection = db.child("members").child(self.member).child("connections").child("twitch").get().val()
        if not twitch_connection:
            twitch_connection = {}

        return twitch_connection


class IsTwitchStreamLiveHandler(Handler):

    def __init__(self, db_config: dict, twitch_client_id: str):
        self.db_config = db_config
        self.twitch_client_id = twitch_client_id

    def can_handle_message(self, message: discord.Message) -> bool:
        return bool(re.match(_PATTERN, message.content))

    async def handle_message(self, client: discord.Client, message: discord.Message):
        match = _PATTERN.match(message.content)
        discord_id = match.groups(1)[0]

        twitch_connection = await perform_database_task(
            client.loop,
            FetchTwitchConnectionDatabaseTask(self.db_config, discord_id))

        if not twitch_connection.get("id", "") or not twitch_connection.get("name", ""):
            await client.send_message(message.channel, "<@{}> has no registered Twitch account.".format(discord_id))
            return

        url = "https://api.twitch.tv/helix/streams?first=1&user_id={}".format(twitch_connection["id"])
        resp = await aiohttp.request("GET", url, headers={"Client-ID": self.twitch_client_id})

        if resp.status != 200:
            await client.send_message(message.channel, "Unknown error occurred.")
            return

        data = await resp.json()
        if data.get("data", []) and data["data"][0].get("type", "") == "live":
            is_live_message = \
                "<@{}> is currently live! Tune in at https://www.twitch.tv/{}".format(
                    discord_id,
                    twitch_connection["name"])
            await client.send_message(message.channel, is_live_message)
        else:
            await client.send_message(message.channel, "<@{}> is not currently live right now.".format(discord_id))

    async def description(self, client: discord.Client) -> str:
        return _TRIGGER + " {@mention} - checks if the mentioned member is currently live on Twitch."