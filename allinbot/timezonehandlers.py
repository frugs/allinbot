import re
from datetime import datetime
import discord
from .handler import Handler
from . import timezone


class TimeZoneConversionHandler(Handler):

    def __init__(self):
        self.matcher = r'^!timezone\s+(.+)\sto\s([^\s]+)$'

    def can_handle_message(self, message: discord.Message) -> bool:
        return re.match(self.matcher, message.content)

    async def handle_message(self, client: discord.Client, message: discord.Message):
        try:

            match = re.match(self.matcher, message.content)
            from_time_args = match.group(1).split(' ')
            to_timezone = match.group(2)

            if len(from_time_args) == 3:
                date = from_time_args[0]
                time = from_time_args[1]
                from_tz_str = from_time_args[2]

                naive_from_datetime = datetime.strptime(date + " " + time, "%d/%m %H:%M")
            elif len(from_time_args) == 2:
                time = from_time_args[0]
                from_tz_str = from_time_args[1]

                naive_time_only = datetime.strptime(time, "%H:%M")
                now = datetime.now()

                naive_from_datetime = now.replace(hour=naive_time_only.hour, minute=naive_time_only.minute)
            else:
                raise ValueError("Invalid remote date")

            from_datetimes = timezone.localise_to_possible_timezones_from_name(naive_from_datetime, from_tz_str)

            if not from_datetimes:
                raise ValueError("from_timezone unrecognised")

            for from_datetime in from_datetimes:
                to_datetimes = timezone.normalise_to_possible_timezones_from_name(from_datetime, to_timezone)

                if not to_datetimes:
                    raise ValueError("to_timezone unrecognised")

                for to_datetime in to_datetimes:
                    datetime_format = "%d %b %H:%M %Z%z"
                    from_time_str = from_datetime.strftime(datetime_format)
                    to_time_str = to_datetime.strftime(datetime_format)

                    await client.send_message(message.channel, "{} is {}".format(from_time_str, to_time_str))

        except ValueError:
            await client.send_message("Usage: !timezone {date} {time} {from_timezone} to {to_timezone}")



    def description(self) -> str:
        return ("!timezone {day}/{month} {time} {from_timezone} to {to_timezone}\n"
                "!timezone {time} {from_timezone} to {to_timezone}")