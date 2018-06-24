import os
import typing
import re
import discord
import pyrebase

from .database import perform_database_task, DatabaseTask
from .handler import Handler

ALLIN_MEMBER_ROLE_ID = os.getenv("ALLIN_MEMBER_ROLE_ID")


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
                member["discord_id"] for member in query_result.val().values()
                if 'discord_id' in member
            ]


class RaceMentionHandler(Handler):
    def __init__(self, race: str, db_config: dict):
        self._race = race
        self._db_config = db_config
        self._matcher = re.compile("^@{}\s+(.*)$".format(race.lower()),
                                   re.IGNORECASE)

    async def handle_message(self, client: discord.Client,
                             message: discord.Message):
        ids = await perform_database_task(
            client.loop,
            QueryRacePlayerDiscordIdsDatabaseTask(self._race, self._db_config))
        server_members = filter(
            None,
            [message.server.get_member(discord_id) for discord_id in ids])
        online_server_members = [
            member for member in server_members
            if any(role for role in member.roles
                   if role.id == ALLIN_MEMBER_ROLE_ID) and (
                       member.status == discord.Status.online
                       or member.status == discord.Status.idle)
        ]
        mentions = ", ".join(
            [member.mention for member in online_server_members])

        match = re.match(self._matcher, message.content)
        message_content = match.group(1) if match else ""

        await client.send_message(message.channel,
                                  message_content + "\n" + mentions)

    def can_handle_message(self, message: discord.Message) -> bool:
        return message.server and (message.content.casefold() == "@{}".format(
            self._race.lower()).casefold()
                                   or re.match(self._matcher, message.content))

    async def description(self, client) -> str:
        return "@" + self._race.lower(
        ) + " *{message}* - @mention members who play " + self._race + " with {message}"


def zerg_mention_handler(db_config: dict) -> Handler:
    return RaceMentionHandler("Zerg", db_config)


def protoss_mention_handler(db_config: dict) -> Handler:
    return RaceMentionHandler("Protoss", db_config)


def terran_mention_handler(db_config: dict) -> Handler:
    return RaceMentionHandler("Terran", db_config)


def random_mention_handler(db_config: dict) -> Handler:
    return RaceMentionHandler("Random", db_config)
