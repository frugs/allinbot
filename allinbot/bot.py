from typing import Iterable
import discord
from .handler import Handler


class Bot:

    def __init__(self, token: str, client: discord.Client):
        self.token = token
        self.client = client
        self.handlers = []

        @client.event
        async def on_ready():
            print('Logged in as')
            print(self.client.user.name)
            print(self.client.user.id)
            print('------')

        @client.event
        async def on_message(message: discord.Message):
            await Bot._dispatch_message_to_handlers(self.client, message, self.handlers)

    def start(self):
        self.client.run(self.token)

    def stop(self):
        self.client.close()

    def register_handler(self, handler: Handler):
        self.handlers.append(handler)

    def unregister_handler(self, handler: Handler):
        self.handlers.remove(handler)

    @staticmethod
    async def _dispatch_message_to_handlers(
            client: discord.Client, message: discord.Message, handlers: Iterable[Handler]):
        for handler in handlers:
            await handler(client, message)