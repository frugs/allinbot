import discord
import pytz
import re
from datetime import datetime
from .handler import Handler

LETTERS_ONLY = r"^\w+$"
PATTERN_TEMPLATE = "(\d\s*(?:AM|PM)?\s*{}(?:$|[^\w])|^{}$)"


class AppendUtcOffsetHandler(Handler):
    def __init__(self):
        self.command_matcher = r"^[^!].*"
        self.timezone_patterns = {}

        for tz_name in pytz.common_timezones:
            tz = pytz.timezone(tz_name)
            tz_abbrev = tz.tzname(datetime.now())
            if not re.match(
                    LETTERS_ONLY, tz_abbrev,
                    flags=re.IGNORECASE) or tz_abbrev in [
                        'EAT', 'CAT', 'WEST'
                    ]:
                continue

            pattern = re.compile(
                PATTERN_TEMPLATE.format(tz_abbrev, tz_abbrev),
                flags=re.IGNORECASE)
            self.timezone_patterns[pattern] = tz

    def can_handle_message(self, message: discord.Message) -> bool:
        return re.match(self.command_matcher, message.content)

    async def handle_message(self, client: discord.Client,
                             message: discord.Message):
        result = []
        now = datetime.now()
        for pattern, tz in self.timezone_patterns.items():
            match = pattern.search(message.content)
            if match:
                result.append("{} is UTC{:+.1f}".format(
                    tz.tzname(now),
                    tz.utcoffset(now).total_seconds() / 3600))

        if result:
            await message.channel.send("\n".join(result))

    async def description(self, client) -> str:
        return ""
