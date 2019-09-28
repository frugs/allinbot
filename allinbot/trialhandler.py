import datetime
import os

import discord

from allinbot.handler import Handler

ALLIN_TRIAL_MEMBER_ROLE_ID = int(os.getenv("ALLIN_TRIAL_MEMBER_ROLE_ID", "0"))
ALLIN_RECRUITMENT_CHANNEL_ID = int(os.getenv("ALLIN_RECRUITMENT_CHANNEL_ID", "0"))

TRIGGERS = ["!trial", "!trials"]


def format_time_delta(delta: datetime.timedelta) -> str:
    weeks, days = divmod(delta.days, 7)
    hours = delta.seconds // 3600

    result = []

    if weeks:
        result.append("{} week(s)".format(weeks))

    if days:
        result.append("{} day(s)".format(days))

    if result:
        return " and ".join(result) + " ago"

    if hours:
        return "{} hours ago"

    return "just now"


def format_datetime(date_time: datetime.datetime) -> str:
    return date_time.strftime("%Y-%b-%d")


class TrialHandler(Handler):
    def can_handle_message(self, message: discord.Message) -> bool:
        return (
            message.channel.id == ALLIN_RECRUITMENT_CHANNEL_ID
            and message.content in TRIGGERS
        )

    async def handle_message(self, client: discord.Client, message: discord.Message):
        if not client.is_ready():
            return

        trial_role = message.guild.get_role(ALLIN_TRIAL_MEMBER_ROLE_ID)
        trial_members = [
            member for member in message.guild.members if trial_role in member.roles
        ]

        if not trial_members:
            return

        trial_members.sort(key=lambda member: member.joined_at)

        line_data = [
            (
                member.mention,
                format_time_delta(datetime.datetime.utcnow() - member.joined_at),
                format_datetime(member.joined_at),
            )
            for member in trial_members
        ]

        lines = [
            "{} - joined {} ({})".format(*single_line_data)
            for single_line_data in line_data
        ]

        recruitment_channel = message.guild.get_channel(ALLIN_RECRUITMENT_CHANNEL_ID)
        await recruitment_channel.send("\n".join(lines))

    async def description(self, client: discord.Client) -> str:
        return ""
