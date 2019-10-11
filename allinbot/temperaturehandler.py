import re

import discord

from .handler import Handler

FAHRENHEIT_MATCHER = re.compile(
    r"^([+-]?([0-9]*[.])?[0-9]+)\s*(?:degrees|degree)?\s*(?:F|Fahrenheit)$",
    re.IGNORECASE,
)
CELSIUS_MATCHER = re.compile(
    r"^([+-]?([0-9]*[.])?[0-9]+)\s*(?:degrees|degree)?\s*(?:C|Celsius)$",
    re.IGNORECASE,
)


class FahrenheitToCelsiusHandler(Handler):
    def can_handle_message(self, message: discord.Message):
        return "F".casefold() == message.content.casefold() or re.fullmatch(
            FAHRENHEIT_MATCHER, message.content
        )

    async def handle_message(self, client: discord.Client, message: discord.Message):
        if "F".casefold() == message.content.casefold():
            fahrenheit = 0
        else:
            match = re.fullmatch(FAHRENHEIT_MATCHER, message.content)
            group = match.group(1)
            fahrenheit = float(group)
        celsius = (fahrenheit - 32) * 5/9
        reply = "{:.1f} °F is {:.1f} °C".format(fahrenheit, celsius)
        await message.channel.send(reply)

    async def description(self, client):
        return ""


class CelsiusToFahrenheitHandler(Handler):
    def can_handle_message(self, message: discord.Message):
        return "C".casefold() == message.content.casefold() or re.fullmatch(
            CELSIUS_MATCHER, message.content
        )

    async def handle_message(self, client: discord.Client, message: discord.Message):
        if "C".casefold() == message.content.casefold():
            celsius = 0
        else:
            match = re.fullmatch(CELSIUS_MATCHER, message.content)
            group = match.group(1)
            celsius = float(group)
        fahrenheit = (celsius * 9/5) + 32
        reply = "{:.1f} °C is {:.1f} °F".format(celsius, fahrenheit)
        await message.channel.send(reply)

    async def description(self, client):
        return ""
