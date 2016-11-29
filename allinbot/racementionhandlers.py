import typing
import re
import discord
import pyrebase

from .database import perform_database_task, DatabaseTask
from .handler import Handler


def _convert_to_mention(id: str) -> str:
    return "<@!{}>".format(id)


class QueryRacePlayersDatabaseTask(DatabaseTask[typing.List[str]]):

    def __init__(self, race: str, db_config: dict):
        DatabaseTask.__init__(self, db_config)
        self._lower_race = race.lower()

    def execute_with_database(self, db: pyrebase.pyrebase.Database) -> typing.List[str]:
        query_result = db.child("members").order_by_child("{}_player".format(self._lower_race)).equal_to(True).get()

        if not query_result.pyres:
            return []
        else:
            return [member["discord_id"] for member in query_result.val().values()]


class RaceMentionHandler(Handler):

    def __init__(self, race: str, db_config: dict):
        self._race = race
        self._db_config = db_config
        self._matcher = re.compile("^!{}\s+(.*)$".format(race.lower()))

    async def handle_message(self, client: discord.Client, message: discord.Message):
        ids = await perform_database_task(client.loop, QueryRacePlayersDatabaseTask(self._race, self._db_config))
        mentions = ", ".join([_convert_to_mention(id) for id in ids])

        match = re.match(self._matcher, message.content)
        message_content = match.group(1) if match else ""

        await client.send_message(message.channel, message_content + "\n" + mentions)

    def can_handle_message(self, message: discord.Message) -> bool:
        return message.content == "!" + self._race.lower() or re.match(self._matcher, message.content)

    def description(self) -> str:
        return "!" + self._race.lower() + " *{message}* - @mention members who play " + self._race + " with {message}"


def zerg_mention_handler(db_config: dict) -> Handler:
    return RaceMentionHandler("Zerg", db_config)


def protoss_mention_handler(db_config: dict) -> Handler:
    return RaceMentionHandler("Protoss", db_config)


def terran_mention_handler(db_config: dict) -> Handler:
    return RaceMentionHandler("Terran", db_config)


def random_mention_handler(db_config: dict) -> Handler:
    return RaceMentionHandler("Random", db_config)

