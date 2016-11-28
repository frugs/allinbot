import discord


class Task:
    async def perform_task(self, client: discord.Client):
        raise NotImplementedError("This must be implemented!")