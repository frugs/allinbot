import discord
import asyncio
from typing import Iterable
from .handler import Handler
from .task import Task


class Bot:
    def __init__(self, token: str, client: discord.Client):
        self.token = token
        self.client = client
        self.event_loop = client.loop
        self.handlers = []

        @client.event
        async def on_ready():
            print('Logged in as')
            print(self.client.user.name)
            print(self.client.user.id)
            print('------')

        @client.event
        async def on_message(message: discord.Message):
            if message.content == "!help":
                print(message.channel.id)
                await Bot._describe_handlers(self.client, message,
                                             self.handlers)
            else:
                await Bot._dispatch_message_to_handlers(
                    self.client, message, self.handlers)

    async def start(self):
        await self.client.start(self.token)

    async def stop(self):
        await self.client.logout()
        await self.client.close()

    def register_handler(self, handler: Handler):
        self.handlers.append(handler)

    def unregister_handler(self, handler: Handler):
        self.handlers.remove(handler)

    def schedule_task(self, task: Task):
        asyncio.ensure_future(
            task.perform_task(self.client), loop=self.event_loop)

    @staticmethod
    async def _describe_handlers(client: discord.Client,
                                 message: discord.Message,
                                 handlers: Iterable[Handler]):
        descriptions = []
        for handler in handlers:
            descriptions.append(await handler.description(client))
        combined_description = "\n".join(descriptions)
        await client.send_message(message.channel, combined_description)

    @staticmethod
    async def _dispatch_message_to_handlers(client: discord.Client,
                                            message: discord.Message,
                                            handlers: Iterable[Handler]):
        for handler in handlers:
            if handler.can_handle_message(message):
                await handler.handle_message(client, message)
