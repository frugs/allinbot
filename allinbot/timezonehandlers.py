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
            to_timezone = match.group(2).upper()

            if len(from_time_args) >= 2:
                time = " ".join(from_time_args[0:-1])
                from_tz_str = from_time_args[-1].upper()

                for time_format in ["%H:%M", "%H%M", "%I:%M %p", "%I:%M%p", "%I%p", "%I %p"]:
                    try:
                        naive_time_only = datetime.strptime(time, time_format)
                        break
                    except ValueError:
                        pass
                else:
                    raise ValueError("Invalid from_time")

                now = datetime.now()

                naive_from_datetime = now.replace(hour=naive_time_only.hour, minute=naive_time_only.minute)
            else:
                raise ValueError("Invalid from_time")

            from_datetimes = timezone.localise_to_possible_timezones_from_name(naive_from_datetime, from_tz_str)

            if not from_datetimes:
                raise ValueError("from_timezone unrecognised")

            replies = []
            for from_datetime in from_datetimes:
                to_datetimes = timezone.normalise_to_possible_timezones_from_name(from_datetime, to_timezone)

                if not to_datetimes:
                    raise ValueError("to_timezone unrecognised")

                for to_datetime in to_datetimes:
                    from_time_str = from_datetime.strftime("%H:%M %Z%z")
                    from_zone = from_datetime.tzinfo.zone

                    to_time_str = to_datetime.strftime("**%H:%M** %Z%z")
                    to_zone = to_datetime.tzinfo.zone

                    replies.append("_{} {}_\n{} **{}**".format(from_time_str, from_zone, to_time_str, to_zone))

            await client.send_message(message.channel, "\n------\n".join(replies))

        except ValueError as e:
            await client.send_message(
                message.channel, str(e) + "\nUsage: !timezone {time} {from_timezone} to {to_timezone}")

    async def description(self, client) -> str:
        return "!timezone {time} {from_timezone} to {to_timezone}"
