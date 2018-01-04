import concurrent.futures
import itertools
from typing import List, Tuple

import discord
import pyrebase

from allinbot.database import DatabaseTask, open_db_connection, perform_database_task
from allinbot.handler import Handler

_TRIGGER = "!winstreaks"
_ALT_TRIGGER = "!winstreak"


class FetchMembersDatabaseTask(DatabaseTask[List[str]]):

    def execute_with_database(self, db: pyrebase.pyrebase.Database) -> List[str]:
        members = db.child("members").shallow().get().val()
        return members if members else []


class FetchWinStreaksDatabaseTask(DatabaseTask[List[Tuple[str, int]]]):

    def __init__(self, db_config: dict, member: str):
        super().__init__(db_config)
        self.member = member

    def execute_with_database(self, db: pyrebase.pyrebase.Database) -> Tuple[str, int]:
        regions = db.child("members").child(self.member).child("characters").get().val()
        if not regions:
            regions = {}

        characters = itertools.chain.from_iterable(x.values() for x in regions.values())

        def map_characters_to_win_streaks(character: dict) -> int:
            ladder_info = character.get("ladder_info", {})
            sorted_seasons = list(sorted(ladder_info.keys(), reverse=True))
            if sorted_seasons:
                race_win_streaks = (x.get("current_win_streak", 0) for x in ladder_info[sorted_seasons[0]].values())
                return max(race_win_streaks, default=0)
            else:
                return 0

        character_win_streaks = list(map(map_characters_to_win_streaks, characters))
        return self.member, max(character_win_streaks, default=0)


class WinStreakHandler(Handler):

    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.rate_limited = False

    def can_handle_message(self, message: discord.Message) -> bool:
        return message.content in [_TRIGGER, _ALT_TRIGGER] and not self.rate_limited

    async def handle_message(self, client: discord.Client, message: discord.Message):
        self.rate_limited = True

        members = await perform_database_task(client.loop, FetchMembersDatabaseTask(self.db_config))

        def fetch_win_streaks(member: str):
            db_task = FetchWinStreaksDatabaseTask(self.db_config, member)
            return db_task.execute_with_database(open_db_connection(self.db_config))

        with concurrent.futures.ThreadPoolExecutor(32) as pool:
            fs = [pool.submit(fetch_win_streaks, member) for member in members]
            completed_fs, _ = await client.loop.run_in_executor(None, concurrent.futures.wait, fs)
            win_streaks = [f.result() for f in completed_fs]

        win_streaks.sort(key=lambda x: x[1], reverse=True)
        win_streaks = win_streaks[:5]

        if win_streaks:
            message_lines = [
                "<@{}> is currently on a {} win streak!".format(discord_id, win_streak)
                for discord_id, win_streak
                in win_streaks
            ]
            await client.send_message(message.channel, "\n".join(message_lines))
        else:
            await client.send_message(message.channel, "No-one is currently on a win streak.")

        self.rate_limited = False

    async def description(self, client: discord.Client) -> str:
        return _TRIGGER + " - displays the current top five longest ladder win streaks."
