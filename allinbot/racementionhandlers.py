import re
import typing

import discord

from .database import perform_database_task, QueryBuilder, DatabaseTask
from .handler import Handler


class QueryRacePlayerDiscordIdsDatabaseTask(DatabaseTask[typing.List[str]]):
    def __init__(self, race: str):
        DatabaseTask.__init__(self)
        self._lower_race = race.lower()

    def execute_with_database(self, db: QueryBuilder) -> typing.List[str]:
        query_result = db.child("members").order_by_child("{}_player".format(self._lower_race)
                                                          ).equal_to(True).get()

        if not query_result:
            return []
        else:
            return [
                member_id for member_id, member in query_result.items()
                if member.get("is_full_member", False)
            ]


class RaceMentionHandler(Handler):
    def __init__(self, race: str):
        self._race = race
        self._matcher = re.compile("^@{}(?:\\s+)?(.*)$".format(race.lower()), re.IGNORECASE)

    async def handle_message(self, client: discord.Client, message: discord.Message):
        ids = await perform_database_task(
            client.loop, QueryRacePlayerDiscordIdsDatabaseTask(self._race)
        )

        def mention_if_online_and_idle(discord_id: str) -> str:
            discord_member = message.guild.get_member(int(discord_id))
            if not discord_member:
                return ""

            if discord_member.status in [discord.Status.online, discord.Status.idle]:
                return "<@{}>".format(discord_id)
            else:
                nick = discord_member.nick
                return nick if nick else discord_member.name

        mentions_and_names = list(filter(lambda x: x, map(mention_if_online_and_idle, ids)))

        if mentions_and_names:
            mentions_and_names_str = ", ".join(mentions_and_names)

            match = re.match(self._matcher, message.content)
            message_content = match.group(1) if match else ""

            await message.channel.send(message_content + "\n" + mentions_and_names_str)

    def can_handle_message(self, message: discord.Message) -> bool:
        return message.guild and (
            message.content.casefold() == "@{}".format(self._race.lower()).casefold()
            or re.match(self._matcher, message.content)
        )

    async def description(self, client) -> str:
        return ("@{} *{{message}}* -"
                "@mention members who play {} with {{message}}"
                ).format(self._race.lower(), self._race)


def zerg_mention_handler() -> Handler:
    return RaceMentionHandler("Zerg")


def protoss_mention_handler() -> Handler:
    return RaceMentionHandler("Protoss")


def terran_mention_handler() -> Handler:
    return RaceMentionHandler("Terran")


def random_mention_handler() -> Handler:
    return RaceMentionHandler("Random")
