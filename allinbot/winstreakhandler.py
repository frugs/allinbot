import concurrent.futures
import itertools
import os
import time
from typing import List, Tuple

import discord
import pyrebase

from allinbot.database import DatabaseTask, open_db_connection, perform_database_task
from allinbot.handler import Handler

ALLIN_MEMBER_ROLE_ID = os.getenv("ALLIN_MEMBER_ROLE_ID", "")

_TRIGGER = "!winstreaks"
_ALT_TRIGGER = "!winstreak"
_SECONDS_IN_5_DAYS = 432000


def extract_win_streaks_for_characters(characters: dict):
    characters = itertools.chain.from_iterable(x.values() for x in characters.values())

    characters = list(characters)

    def map_characters_to_win_streaks(character: dict) -> Tuple[int, int]:
        ladder_info = character.get("ladder_info", {})
        sorted_seasons = list(sorted(ladder_info.keys(), reverse=True))
        if sorted_seasons:
            current_season_ladder_info = ladder_info[sorted_seasons[0]]

            race_win_streaks = (
                x.get("current_win_streak", 0)
                for x
                in current_season_ladder_info.values()
                if x.get("last_played_time_stamp", 0) > time.time() - _SECONDS_IN_5_DAYS)

            race_longest_win_streaks = (
                x.get("longest_win_streak", 0)
                for x
                in current_season_ladder_info.values())

            return max(race_win_streaks, default=0), max(race_longest_win_streaks, default=0)
        else:
            return 0, 0

    win_streaks_and_longest_win_streaks = list(map(map_characters_to_win_streaks, characters))
    if win_streaks_and_longest_win_streaks:
        character_win_streaks, character_longest_win_streaks = zip(*win_streaks_and_longest_win_streaks)
        return max(character_win_streaks, default=0), max(character_longest_win_streaks, default=0)
    else:
        return 0, 0


class FetchMemberIdsDatabaseTask(DatabaseTask[List[str]]):

    def execute_with_database(self, db: pyrebase.pyrebase.Database) -> List[str]:
        members = db.child("members").get().val()
        return members if members else []


class FetchWinStreaksDatabaseTask(DatabaseTask[List[Tuple[str, int, int]]]):

    def __init__(self, db_config: dict, member: str):
        super().__init__(db_config)
        self.member = member

    def execute_with_database(self, db: pyrebase.pyrebase.Database) -> Tuple[str, int, int]:
        characters = db.child("members").child(self.member).child("characters").get().val()
        if not characters:
            characters = {}

        current_win_streak, longest_win_streak = extract_win_streaks_for_characters(characters)
        return self.member, current_win_streak, longest_win_streak


class FetchAllMembersDatabaseTask(DatabaseTask[dict]):

    def execute_with_database(self, db: pyrebase.pyrebase.Database) -> dict:
        members = db.child("members").get().val()
        return members if members else {}


class WinStreakHandler(Handler):

    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.rate_limited = False

    def can_handle_message(self, message: discord.Message) -> bool:
        return message.content in [_TRIGGER, _ALT_TRIGGER] and not self.rate_limited

    async def handle_message(self, client: discord.Client, message: discord.Message):
        self.rate_limited = True

        members_ids = await perform_database_task(client.loop, FetchMemberIdsDatabaseTask(self.db_config))

        if len(members_ids) < 300:
            # There aren't too many so just fetch the whole lot, this will be faster
            members = await perform_database_task(client.loop, FetchAllMembersDatabaseTask(self.db_config))
            member_characters = [
                (member_id, member_data.get("characters", {}))
                for member_id, member_data
                in members.items()]
            all_win_streaks = [
                tuple([member_id]) + extract_win_streaks_for_characters(characters)
                for member_id, characters
                in member_characters]
        else:
            def fetch_win_streaks(member: str):
                db_task = FetchWinStreaksDatabaseTask(self.db_config, member)
                return db_task.execute_with_database(open_db_connection(self.db_config))

            with concurrent.futures.ThreadPoolExecutor(32) as pool:
                fs = [pool.submit(fetch_win_streaks, member) for member in members_ids]
                completed_fs, _ = await client.loop.run_in_executor(None, concurrent.futures.wait, fs)
                all_win_streaks = [f.result() for f in completed_fs]

        def is_allin_member(discord_id: str) -> bool:
            member = message.server.get_member(discord_id)
            if not member:
                return False

            return any(role for role in member.roles if role.id == ALLIN_MEMBER_ROLE_ID)

        allin_win_streaks = [x for x in all_win_streaks if is_allin_member(x[0])]

        win_streaks = [
            (discord_id, win_streak)
            for discord_id, win_streak, _
            in allin_win_streaks
            if win_streak > 2]

        win_streaks.sort(key=lambda x: x[1], reverse=True)
        win_streaks = win_streaks[:5]

        def get_name(discord_id: str) -> str:
            member = message.server.get_member(discord_id)
            if member:
                return member.nick if member.nick else member.name
            else:
                return discord_id

        message_lines = []
        if win_streaks:
            message_lines += [
                "{} is currently on a {} win streak!".format(get_name(discord_id), win_streak)
                for discord_id, win_streak
                in win_streaks
            ]
        else:
            message_lines.append("No-one is currently on a win streak.")
    
        longest_win_streaks = [
            (discord_id, longest_win_streak)
            for discord_id, _, longest_win_streak
            in allin_win_streaks
            if longest_win_streak > 1]

        longest_win_streaks.sort(key=lambda x: x[1], reverse=True)
        longest_win_streaks = longest_win_streaks[:3]

        if longest_win_streaks:
            message_lines += ["", "**Longest Win Streaks This Season**"] + [
                "{} went on a {} win streak!".format(get_name(discord_id), longest_win_streak)
                for discord_id, longest_win_streak
                in longest_win_streaks
            ]

        if message_lines:
            await client.send_message(message.channel, "\n".join(message_lines))

        self.rate_limited = False

    async def description(self, client: discord.Client) -> str:
        return _TRIGGER + " - displays the current top five longest ladder win streaks."
