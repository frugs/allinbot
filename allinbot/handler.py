from typing import Callable, Awaitable
import discord

Handler = Callable[[discord.Client, discord.Message], Awaitable[bool]]
