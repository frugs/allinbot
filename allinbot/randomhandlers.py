from typing import Iterable, Tuple
import random
import bisect
import discord
from .handler import Handler
from .simplehandlers import PingPongHandler


class PingRandomPongHandler(Handler):
    """
    Handler which responds to {ping} with a randomly selected message {pong}. Supports weighting.
    """

    def __init__(
        self, ping: str, pong_choices: Iterable[Tuple[float, str]], desc: str = None
    ):
        self.ping = ping

        self.cumulative_weights = []
        self.delegate_handlers = []
        self.weight_sum = 0.0

        for probability, pong in pong_choices:
            self.weight_sum += probability
            self.cumulative_weights.append(self.weight_sum)
            self.delegate_handlers.append(PingPongHandler(ping, pong))

        if desc is not None:
            self.desc = desc
        else:
            self.desc = ping

    def can_handle_message(self, message: discord.Message):
        return message.content == self.ping

    async def handle_message(self, client: discord.Client, message: discord.Message):
        random_result = random.uniform(0.0, self.weight_sum)

        handler_index = bisect.bisect_left(self.cumulative_weights, random_result)
        selected_handler = self.delegate_handlers[handler_index]

        await selected_handler.handle_message(client, message)

    async def description(self, client):
        return self.desc
