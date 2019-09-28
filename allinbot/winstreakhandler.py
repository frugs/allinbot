import itertools
import os
import time
from typing import List, Tuple

import discord

from allinbot.database import DatabaseTask, QueryBuilder, perform_database_task
from allinbot.handler import Handler

ALLIN_MEMBER_ROLE_ID = os.getenv("ALLIN_MEMBER_ROLE_ID", "")

_TRIGGER = "!winstreaks"
_ALT_TRIGGER = "!winstreak"
_SECONDS_IN_5_DAYS = 432000


def extract_win_streaks_for_characters(characters: dict):
    characters = itertools.chain.from_iterable(x.values() for x in characters.values())

    characters = list(characters)

    def map_characters_to_win_streaks(character: dict) -> Tuple[int, int, int]:
        ladder_info = character.get("ladder_info", {})
        sorted_seasons = list(sorted(ladder_info.keys(), reverse=True))
        if sorted_seasons:
            latest_season_ladder_info = ladder_info[sorted_seasons[0]]
            character_latest_season = int(sorted_seasons[0])

            race_win_streaks = (
                x.get("current_win_streak", 0)
                for x in latest_season_ladder_info.values()
                if x.get("last_played_time_stamp", 0) > time.time() - _SECONDS_IN_5_DAYS
            )

            race_longest_win_streaks = (
                x.get("longest_win_streak", 0)
                for x in latest_season_ladder_info.values()
            )

            return (
                character_latest_season,
                max(race_win_streaks, default=0),
                max(race_longest_win_streaks, default=0),
            )
        else:
            return 0, 0, 0

    win_streaks_and_longest_win_streaks = list(
        map(map_characters_to_win_streaks, characters)
    )

    if win_streaks_and_longest_win_streaks:
        seasons, _, _ = zip(*win_streaks_and_longest_win_streaks)
        latest_season = max(seasons, default=0)

        win_streaks_and_longest_win_streaks = [
            (season, character_win_streaks, character_longest_win_streaks)
            for season, character_win_streaks, character_longest_win_streaks in win_streaks_and_longest_win_streaks
            if season == latest_season
        ]
        if win_streaks_and_longest_win_streaks:
            _, character_win_streaks, character_longest_win_streaks = zip(
                *win_streaks_and_longest_win_streaks
            )

            return (
                latest_season,
                max(character_win_streaks, default=0),
                max(character_longest_win_streaks, default=0),
            )

    return 0, 0, 0


class FetchAllinMembersDatabaseTask(DatabaseTask[dict]):
    def execute_with_database(self, db: QueryBuilder) -> dict:
        return db.child("members").order_by_child("is_full_member").equal_to(True).get()


class WinStreakHandler(Handler):
    def __init__(self):
        self.rate_limited = False

    def can_handle_message(self, message: discord.Message) -> bool:
        return message.content in [_TRIGGER, _ALT_TRIGGER] and not self.rate_limited

    async def handle_message(self, client: discord.Client, message: discord.Message):
        self.rate_limited = True

        members = await perform_database_task(
            client.loop, FetchAllinMembersDatabaseTask()
        )
        member_characters = [
            (int(member_id), member_data.get("characters", {}))
            for member_id, member_data in members.items()
        ]

        allin_win_streaks = [
            tuple([member_id]) + extract_win_streaks_for_characters(characters)
            for member_id, characters in member_characters
        ]

        _, seasons, _, _ = zip(*allin_win_streaks)
        latest_season = max(seasons, default=0)

        win_streaks = [
            (discord_id, win_streak)
            for discord_id, season, win_streak, _ in allin_win_streaks
            if win_streak > 2 and season == latest_season
        ]

        win_streaks.sort(key=lambda x: x[1], reverse=True)
        win_streaks = win_streaks[:5]

        def get_name(discord_id: int) -> str:
            member = message.guild.get_member(discord_id)
            if member:
                return member.nick if member.nick else member.name
            else:
                return str(discord_id)

        message_lines = []
        if win_streaks:
            message_lines += [
                "{} is currently on a {} win streak!".format(
                    get_name(discord_id), win_streak
                )
                for discord_id, win_streak in win_streaks
            ]
        else:
            message_lines.append("No-one is currently on a win streak.")

        longest_win_streaks = [
            (discord_id, longest_win_streak)
            for discord_id, season, _, longest_win_streak in allin_win_streaks
            if longest_win_streak > 1 and season == latest_season
        ]

        longest_win_streaks.sort(key=lambda x: x[1], reverse=True)
        longest_win_streaks = longest_win_streaks[:3]

        if longest_win_streaks:
            message_lines += ["", "**Longest Win Streaks This Season**"] + [
                "{} went on a {} win streak!".format(
                    get_name(discord_id), longest_win_streak
                )
                for discord_id, longest_win_streak in longest_win_streaks
            ]

        if message_lines:
            await message.channel.send("\n".join(message_lines))

        self.rate_limited = False

    async def description(self, client: discord.Client) -> str:
        return _TRIGGER + " - displays the current top five longest ladder win streaks."
