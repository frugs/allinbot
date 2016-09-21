import discord

from .handler import Handler


class PingPongHandler(Handler):
    """
    Handles a message which matches {ping} by messaging {pong}
    """

    def __init__(self, ping: str, pong: str, desc: str=None):
        self.ping = ping
        self.pong = pong

        if desc is not None:
            self.desc = desc
        else:
            self.desc = ping

    def can_handle_message(self, message: discord.Message):
        return message.content == self.ping

    async def handle_message(self, client: discord.Client, message: discord.Message):
        await client.send_message(message.channel, self.pong)

    def description(self):
        return self.desc