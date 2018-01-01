from asyncio import AbstractEventLoop

import discord
import pyrebase

from .handler import Handler
from .database import DatabaseTask, perform_database_task


class RetrieveResponseForTriggerTask(DatabaseTask[str]):

    def __init__(self, db_config: dict, trigger: str):
        super().__init__(db_config)
        self.trigger = trigger

    def execute_with_database(self, db: pyrebase.pyrebase.Database) -> str:
        trigger_response_data = db.child("triggers").child(self.trigger).get().val()
        if trigger_response_data:
            return trigger_response_data.get("response", "")


class RetrieveTriggerHelpTexts(DatabaseTask[str]):

    def execute_with_database(self, db: pyrebase.pyrebase.Database) -> str:
        res = []

        data = db.child("triggers").get().val()
        if data:
            for _, response_data in data.items():
                help = response_data.get("help", "")
                if help:
                    res.append(help)

        return "\n".join(res)

class DynamicPingPongHandler(Handler):

    def __init__(self, db_config: dict):
        self.db_config = db_config

    def can_handle_message(self, message: discord.Message) -> bool:
        text = message.content
        return len(text) > 1 and text.startswith("!") and ' ' not in text

    async def handle_message(self, client: discord.Client, message: discord.Message):
        trigger = message.content[1:]
        response = await self._retrieve_response_for_trigger(client.loop, trigger)

        if response:
            await client.send_message(message.channel, response)

    async def description(self, client: discord.Client) -> str:
         return await self._retrieve_help_texts(client.loop)

    async def _retrieve_response_for_trigger(self, event_loop: AbstractEventLoop, trigger: str) -> str:
        task = RetrieveResponseForTriggerTask(self.db_config, trigger)
        return await perform_database_task(event_loop, task)

    async def _retrieve_help_texts(self, event_loop: AbstractEventLoop) -> str:
        task = RetrieveTriggerHelpTexts(self.db_config)
        return await perform_database_task(event_loop, task)