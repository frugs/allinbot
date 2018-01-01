import discord
import pyrebase

from .handler import Handler
from .database import DatabaseTask, perform_database_task


class MatchTriggerToResponseTask(DatabaseTask[str]):

    def __init__(self, db_config: dict, trigger: str):
        super().__init__(db_config)
        self.trigger = trigger

    def execute_with_database(self, db: pyrebase.pyrebase.Database) -> str:
        trigger_response_data = db.child("triggers").child(self.trigger).get().val()
        if trigger_response_data:
            return trigger_response_data.get("response", "")


class DynamicPingPongHandler(Handler):

    def __init__(self, db_config: dict):
        self.db_config = db_config

    def can_handle_message(self, message: discord.Message) -> bool:
        text = message.content
        return len(text) > 1 and text.startswith("!") and ' ' not in text

    async def handle_message(self, client: discord.Client, message: discord.Message):
        trigger = message.content[1:]
        response = await self._match_trigger_to_response(client, trigger)

        if response:
            await client.send_message(message.channel, response)

    def description(self) -> str:
        pass

    async def _match_trigger_to_response(self, client: discord.Client, trigger: str) -> str:
        task = MatchTriggerToResponseTask(self.db_config, trigger)
        return await perform_database_task(client.loop, task)