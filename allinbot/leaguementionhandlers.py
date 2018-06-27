import typing
import re
import discord
import pyrebase

from .database import perform_database_task, DatabaseTask
from .handler import Handler

LEAGUE_NAMES = [
    "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster"
]


class QueryLeaguePlayerDiscordIdsDatabaseTask(DatabaseTask[typing.List[str]]):
    def __init__(self, league_id: int, db_config: dict):
        DatabaseTask.__init__(self, db_config)
        self._league_id = league_id

    def execute_with_database(
            self, db: pyrebase.pyrebase.Database) -> typing.List[str]:
        query_result = db.child("members").order_by_child(
            "current_league").equal_to(self._league_id).get()

        if not query_result.pyres:
            return []
        else:
            return [
                member["discord_id"] for member in query_result.val().values()
                if 'discord_id' in member
                and member.get("is_full_member", False)
            ]


class LeagueMentionHandler(Handler):
    def __init__(self, league_id: int, db_config: dict):
        self._league_id = league_id
        self._db_config = db_config
        self._matcher = re.compile("^@{}(?:\s+)?(.*)$".format(
            LEAGUE_NAMES[league_id].casefold(), re.IGNORECASE))

    async def handle_message(self, client: discord.Client,
                             message: discord.Message):
        ids = await perform_database_task(
            client.loop,
            QueryLeaguePlayerDiscordIdsDatabaseTask(self._league_id,
                                                    self._db_config))

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

        if mentions_and_names:
            mentions_and_names_str = ", ".join(mentions_and_names)

            match = re.match(self._matcher, message.content)
            message_content = match.group(1) if match else ""

            await client.send_message(
                message.channel,
                message_content + "\n" + mentions_and_names_str)
        else:
            await client.send_message(
                message.channel,
                "I'm afraid no one in that league is currently available.")

    def can_handle_message(self, message: discord.Message) -> bool:
        return re.match(self._matcher, message.content)

    async def description(self, client) -> str:
        league_name = LEAGUE_NAMES[self._league_id]
        return ("@{} *{{message}}* - "
                "@mention members in {} league with {{message}}").format(
                    league_name.casefold(), league_name)


def league_mention_handlers(db_config: dict) -> typing.List[Handler]:
    return [
        LeagueMentionHandler(i, db_config) for i in range(len(LEAGUE_NAMES))
    ]
