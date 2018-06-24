import discord

from allinbot import Task


class GeneralAnnouncementTask(Task):
    def __init__(self, channel_id: str, message: str):
        self.channel_id = channel_id
        self.message = message

    async def perform_task(self, client: discord.Client):
        channel = client.get_channel(self.channel_id)
        await client.send_message(channel, self.message)
