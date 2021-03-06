import datetime
import re
import typing

import discord

from .database import DatabaseTask, QueryBuilder, perform_database_task
from .handler import Handler

_TRIGGER = "!ladderinfo"
_PATTERN = re.compile("^" + _TRIGGER + "\\s+<@[!]*(\\d*)>$")
_RACES = ["Zerg", "Terran", "Protoss", "Random"]
_LEAGUE_EMBLEMS = [
    "<:bronze:230151914812211210>",
    "<:silver:230151947498291211>",
    "<:gold:230151929236291585>",
    "<:platinum:230151940275830795>",
    "<:diamond:230151923276185611>",
    "<:masters:230151935053922305>",
    "<:grandmaster:230152770521399296>",
]


class RetrieveLadderInfoDatabaseTask(DatabaseTask[dict]):
    def __init__(self, discord_id: str):
        super().__init__()
        self._discord_id = discord_id

    def execute_with_database(self, db: QueryBuilder) -> dict:
        return db.child("members").child(self._discord_id).get()


class Sc2LadderInfoHandler(Handler):
    async def handle_message(self, client: discord.Client, message: discord.Message):
        match = _PATTERN.match(message.content)
        discord_id = match.groups(1)[0]

        ladder_info = await perform_database_task(
            client.loop, RetrieveLadderInfoDatabaseTask(discord_id)
        )

        if not ladder_info:
            message_to_send = "Could not find ladder info for <@{}>.".format(discord_id)
        else:
            message_to_send = "**<@{}>'s StarCraft II ladder info**\n".format(
                discord_id
            )

            battle_tag = ladder_info.get("battle_tag", None)
            if battle_tag:
                message_to_send += "Battle Tag: **{}**\n".format(battle_tag)

            last_updated = ladder_info.get("last_updated", None)
            if last_updated:
                last_updated_datetime = datetime.datetime.fromtimestamp(
                    last_updated, datetime.timezone.utc
                )
                message_to_send += last_updated_datetime.strftime(
                    "*last updated at %H:%M %d %b %Y %Z*\n"
                )

            message_to_send += "\n"

            races_played = [
                race for race in _RACES if ladder_info.get(race.lower() + "_player")
            ]
            if races_played:
                message_to_send += (
                    "Highest ranked race(s): " + ", ".join(races_played) + "\n"
                )

            current_league = ladder_info.get("current_league", None)
            if current_league:
                message_to_send += "Current league: {}\n".format(
                    _LEAGUE_EMBLEMS[current_league]
                )

            current_season_games_played = ladder_info.get(
                "current_season_games_played", None
            )
            if current_season_games_played is not None:
                message_to_send += "Total games played this season: {}\n".format(
                    current_season_games_played
                )

            previous_season_games_played = ladder_info.get(
                "previous_season_games_played", None
            )
            if previous_season_games_played is not None:
                message_to_send += "Total games played last season: {}\n".format(
                    previous_season_games_played
                )

            message_to_send += (
                "\nFurther information at: https://all-inspiration-apps.appspot.com/ladderinfo/"
                + discord_id
            )

        await message.channel.send(message_to_send)

    async def description(self, client) -> str:
        return _TRIGGER + " {@mention} - retrieves registered user's sc2 ladder info"

    def can_handle_message(self, message: discord.Message) -> bool:
        return bool(re.match(_PATTERN, message.content))
