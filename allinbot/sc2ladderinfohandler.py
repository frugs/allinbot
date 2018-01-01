import datetime
import re
import typing

import discord
import pyrebase

from .database import DatabaseTask, perform_database_task
from .handler import Handler

_TRIGGER = "!ladderinfo"
_PATTERN = re.compile("^" + _TRIGGER + "\s+<@[!]*(\d*)>$")
_RACES = ["Zerg", "Terran", "Protoss", "Random"]
_LEAGUE_EMBLEMS = [
    "<:bronze:230151914812211210>",
    "<:silver:230151947498291211>",
    "<:gold:230151929236291585>",
    "<:platinum:230151940275830795>",
    "<:diamond:230151923276185611>",
    "<:masters:230151935053922305>",
    "<:grandmaster:230152770521399296>"]


class RetrieveLadderInfoDatabaseTask(DatabaseTask[dict]):

    def __init__(self, discord_id: str, db_config: dict):
        super().__init__(db_config)
        self._discord_id = discord_id

    def execute_with_database(self, db: pyrebase.pyrebase.Database) -> dict:
        query_result = db.child("members").child(self._discord_id).get()

        if not query_result.pyres:
            return {}

        return query_result.val()


def order_by_highest_league_then_most_played(regions: typing.Iterable):
    def key(region: tuple):
        region_id, region_data = region

        if "current" not in region_data:
            return 0, 0

        races = region_data["current"].values()
        return max(race.get("league_id", 0) for race in races), sum(race.get("games_played", 0) for race in races)

    region_list = list(regions)
    return sorted(region_list, key=key, reverse=True)


class Sc2LadderInfoHandler(Handler):

    def __init__(self, db_config: dict):
        self._db_config = db_config

    async def handle_message(self, client: discord.Client, message: discord.Message):
        match = _PATTERN.match(message.content)
        discord_id = match.groups(1)[0]

        ladder_info = await perform_database_task(client.loop, RetrieveLadderInfoDatabaseTask(discord_id, self._db_config))

        if not ladder_info:
            message_to_send = "Could not find ladder info for <@{}>.".format(discord_id)
        else:
            message_to_send = "**<@{}>'s StarCraft II ladder info**\n".format(discord_id)

            battle_tag = ladder_info.get("battle_tag", None)
            if battle_tag:
                message_to_send += "Battle Tag: **{}**\n".format(battle_tag)

            last_updated = ladder_info.get("last_updated", None)
            if last_updated:
                last_updated_datetime = datetime.datetime.fromtimestamp(last_updated, datetime.timezone.utc)
                message_to_send += last_updated_datetime.strftime("*last updated at %H:%M %d %b %Y %Z*\n")

            message_to_send += "\n"

            races_played = [race for race in _RACES if ladder_info.get(race.lower() + "_player")]
            if races_played:
                message_to_send += "Highest ranked race(s): " + ", ".join(races_played) + "\n"

            current_league = ladder_info.get("current_league", None)
            if current_league:
                message_to_send += "Current league: {}\n".format(_LEAGUE_EMBLEMS[current_league])

            current_season_games_played = ladder_info.get("current_season_games_played", None)
            if current_season_games_played is not None:
                message_to_send += "Total games played this season: {}\n".format(current_season_games_played)

            previous_season_games_played = ladder_info.get("previous_season_games_played", None)
            if previous_season_games_played is not None:
                message_to_send += "Total games played last season: {}\n".format(previous_season_games_played)

            regions = ladder_info.get("regions")

            # Only show region stats if the player has been active this season. This extra guard ensures we only show
            # region stats for the current season.
            if current_season_games_played and regions:

                current_season_id = -1
                for region_stats in regions.values():
                    current_season_id = max([current_season_id] + list(map(int, region_stats.keys())))

                message_to_send += "\n"

                for region, region_stats in order_by_highest_league_then_most_played(regions.items()):
                    current_season_stats = region_stats.get(str(current_season_id))
                    if current_season_stats:

                        message_to_send += "__{} Region Stats__\n\n".format(region.upper())
                        for race in _RACES:

                            if race in current_season_stats:
                                message_to_send += "*{}*\n".format(race)
                                race_stats = current_season_stats[race]
                                league_emblem = _LEAGUE_EMBLEMS[(race_stats.get("league_id", 0))]
                                message_to_send += "League: {}\n".format(league_emblem)
                                message_to_send += "MMR: {}\n".format(race_stats.get("mmr", 0))
                                message_to_send += "Games played: {}\n".format(race_stats.get("games_played", 0))
                                message_to_send += "Wins: {}\n".format(race_stats.get("wins", 0))
                                message_to_send += "Losses: {}\n".format(race_stats.get("losses", 0))
                                message_to_send += "Ties: {}\n".format(race_stats.get("ties", 0))

                                message_to_send += "\n"

        await client.send_message(message.channel, message_to_send)

    async def description(self, client) -> str:
        return _TRIGGER + " {@mention} - retrieves registered user's sc2 ladder info"

    def can_handle_message(self, message: discord.Message) -> bool:
        return re.match(_PATTERN, message.content)
