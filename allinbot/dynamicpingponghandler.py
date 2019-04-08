from asyncio import AbstractEventLoop

import discord

from .handler import Handler
from .database import DatabaseTask, QueryBuilder, perform_database_task


class RetrieveResponseForTriggerTask(DatabaseTask[str]):
    def __init__(self, trigger: str):
        super().__init__()
        self.trigger = trigger

    def execute_with_database(self, db: QueryBuilder) -> str:
        trigger_response_data = db.child("triggers").child(self.trigger).get()
        return trigger_response_data.get("response", "") if trigger_response_data else ""


class RetrieveTriggerHelpTexts(DatabaseTask[str]):
    def execute_with_database(self, db: QueryBuilder) -> str:
        res = []

        data = db.child("triggers").get()
        for _, response_data in data.items():
            help = response_data.get("help", "")
            if help:
                res.append(help)

        return "\n".join(res)


class DynamicPingPongHandler(Handler):
    def can_handle_message(self, message: discord.Message) -> bool:
        text = message.content
        return len(text) > 1 and text.startswith("!") and ' ' not in text

    async def handle_message(self, client: discord.Client, message: discord.Message):
        trigger = message.content[1:]
        response = await self._retrieve_response_for_trigger(client.loop, trigger)

        if response:
            await message.channel.send(response)

    async def description(self, client: discord.Client) -> str:
        return await self._retrieve_help_texts(client.loop)

    async def _retrieve_response_for_trigger(
        self, event_loop: AbstractEventLoop, trigger: str
    ) -> str:
        task = RetrieveResponseForTriggerTask(trigger)
        return await perform_database_task(event_loop, task)

    async def _retrieve_help_texts(self, event_loop: AbstractEventLoop) -> str:
        task = RetrieveTriggerHelpTexts()
        return await perform_database_task(event_loop, task)
