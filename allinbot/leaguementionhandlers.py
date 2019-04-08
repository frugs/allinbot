import typing
import re
import discord

from .database import perform_database_task, DatabaseTask, QueryBuilder
from .handler import Handler

LEAGUE_NAMES = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster"]


class QueryLeaguePlayerDiscordIdsDatabaseTask(DatabaseTask[typing.List[str]]):
    def __init__(self, league_id: int):
        DatabaseTask.__init__()
        self._league_id = league_id

    def execute_with_database(self, db: QueryBuilder) -> typing.List[str]:
        query_result = db.child("members").order_by_child("current_league").equal_to(
            self._league_id
        ).get()

        if not query_result:
            return []
        else:
            return [
                member_id for member_id, member in query_result.items()
                if member.get("is_full_member", False)
            ]


class LeagueMentionHandler(Handler):
    def __init__(self, league_id: int):
        self._league_id = league_id
        self._matcher = re.compile(
            "^@{}(?:\\s+)?(.*)$".format(LEAGUE_NAMES[league_id].casefold()), re.IGNORECASE
        )

    async def handle_message(self, client: discord.Client, message: discord.Message):
        ids = await perform_database_task(
            client.loop, QueryLeaguePlayerDiscordIdsDatabaseTask(self._league_id)
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
        else:
            await message.channel.send("I'm afraid no one in that league is currently available.")

    def can_handle_message(self, message: discord.Message) -> bool:
        return bool(re.match(self._matcher, message.content))

    async def description(self, client) -> str:
        league_name = LEAGUE_NAMES[self._league_id]
        return ("@{} *{{message}}* - "
                "@mention members in {} league with {{message}}"
                ).format(league_name.casefold(), league_name)


def league_mention_handlers() -> typing.List[Handler]:
    return [LeagueMentionHandler(i) for i in range(len(LEAGUE_NAMES))]
