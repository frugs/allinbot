import discord
import pyrebase
import re

from .handler import Handler
from .database import DatabaseTask, perform_database_task

_TRIGGER = "!register"
_PATTERN = r'^!register\s+([^\s]+#\d+)'


class BattleTagRegistrationDatabaseTask(DatabaseTask[None]):

    def __init__(self, discord_id: str, battle_tag: str, discord_display_name: str, db_config: dict):
        super().__init__(db_config)
        self._discord_id = discord_id
        self._battle_tag = battle_tag
        self._discord_display_name = discord_display_name

    def execute_with_database(self, db: pyrebase.pyrebase.Database) -> None:
        data = {
            "discord_id": self._discord_id,
            "battle_tag": self._battle_tag,
            "discord_display_name": self._discord_display_name
        }
        db.child("members").child(self._discord_id).update(data)
        return None


class BattleTagRegistrationHandler(Handler):

    def __init__(self, db_config: dict):
        self._db_config = db_config

    def description(self) -> str:
        return _TRIGGER + " {battle_tag} - register your battle tag for further functionality. Battle tags look like BobTheZealot#2812"

    def can_handle_message(self, message: discord.Message) -> bool:
        return re.match(_PATTERN, message.content)

    async def handle_message(self, client: discord.Client, message: discord.Message):
        discord_id = message.author.id

        match = re.match(_PATTERN, message.content)
        battle_tag = match.group(1)

        discord_display_name = message.author.display_name

        task = BattleTagRegistrationDatabaseTask(discord_id, battle_tag, discord_display_name, self._db_config)
        await perform_database_task(client.loop, task)
        await client.send_message(message.channel, message.author.mention + ": Battle tag registered.")
