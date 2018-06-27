import os
import typing
import re
import discord
import pyrebase

from .database import perform_database_task, DatabaseTask
from .handler import Handler


class QueryRacePlayerDiscordIdsDatabaseTask(DatabaseTask[typing.List[str]]):
    def __init__(self, race: str, db_config: dict):
        DatabaseTask.__init__(self, db_config)
        self._lower_race = race.lower()

    def execute_with_database(
            self, db: pyrebase.pyrebase.Database) -> typing.List[str]:
        query_result = db.child("members").order_by_child(
            "{}_player".format(self._lower_race)).equal_to(True).get()

        if not query_result.pyres:
            return []
        else:
            return [
                member.key() for member in query_result.each()
                if member.val().get("is_full_member", False)
            ]


class RaceMentionHandler(Handler):
    def __init__(self, race: str, db_config: dict):
        self._race = race
        self._db_config = db_config
        self._matcher = re.compile("^@{}(?:\s+)?(.*)$".format(race.lower()),
                                   re.IGNORECASE)

    async def handle_message(self, client: discord.Client,
                             message: discord.Message):
        ids = await perform_database_task(
            client.loop,
            QueryRacePlayerDiscordIdsDatabaseTask(self._race, self._db_config))

        def mention_if_online_and_idle(discord_id: str) -> str:
            discord_member = message.server.get_member(discord_id)
            if not discord_member:
                return ""

            if discord_member.status in [
                    discord.Status.online, discord.Status.idle
            ]:
                return "<@{}>".format(discord_id)
            else:
                nick = discord_member.nick
                return nick if nick else discord_member.name

        mentions_and_names = list(
            filter(lambda x: x, map(mention_if_online_and_idle, ids)))

        mentions_and_names_str = ", ".join(mentions_and_names)

        match = re.match(self._matcher, message.content)
        message_content = match.group(1) if match else ""

        await client.send_message(
            message.channel, message_content + "\n" + mentions_and_names_str)

    def can_handle_message(self, message: discord.Message) -> bool:
        return message.server and (message.content.casefold() == "@{}".format(
            self._race.lower()).casefold()
                                   or re.match(self._matcher, message.content))

    async def description(self, client) -> str:
        return ("@{} *{{message}}* -"
                "@mention members who play {} with {{message}}").format(
                    self._race.lower(), self._race)


def zerg_mention_handler(db_config: dict) -> Handler:
    return RaceMentionHandler("Zerg", db_config)


def protoss_mention_handler(db_config: dict) -> Handler:
    return RaceMentionHandler("Protoss", db_config)


def terran_mention_handler(db_config: dict) -> Handler:
    return RaceMentionHandler("Terran", db_config)


def random_mention_handler(db_config: dict) -> Handler:
    return RaceMentionHandler("Random", db_config)
