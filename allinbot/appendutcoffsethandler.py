import discord
import pytz
import re
from datetime import datetime
from .handler import Handler

LETTERS_ONLY = r"^\w+$"
PATTERN_TEMPLATE = "(?P<pre>\d\s*)(?P<ampm>AM|PM)?(?P<tz>\s*{})(?P<post>$|\s)"
REPL_TEMPLATE = "\g<pre>\g<ampm>\g<tz> (UTC{:+.1f}) "


class AppendUtcOffsetHandler(Handler):
    def __init__(self):
        self.command_matcher = r"^[^!].*"
        self.timezone_patterns = {}

        for tz_name in pytz.common_timezones:
            tz = pytz.timezone(tz_name)
            tz_abbrev = tz.tzname(datetime.now())
            if not re.match(LETTERS_ONLY, tz_abbrev, flags=re.IGNORECASE):
                continue

            pattern = re.compile(
                PATTERN_TEMPLATE.format(tz_abbrev), flags=re.IGNORECASE)
            self.timezone_patterns[pattern] = tz

    def can_handle_message(self, message: discord.Message) -> bool:
        return re.match(self.command_matcher, message.content)

    async def handle_message(self, client: discord.Client,
                             message: discord.Message):
        result = message.content
        total_subs = 0
        for pattern, tz in self.timezone_patterns.items():
            result, subs = pattern.subn(
                REPL_TEMPLATE.format(
                    tz.utcoffset(datetime.now()).total_seconds() / 3600),
                result)
            total_subs += subs

        if total_subs > 0:
            await client.send_message(message.channel, result)

    async def description(self, client) -> str:
        return ""
