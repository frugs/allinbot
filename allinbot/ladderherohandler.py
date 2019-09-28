import discord

from allinbot.database import perform_database_task
from allinbot.handler import Handler

from .fetchmembersdatabasetask import FetchAllinMembersDatabaseTask

_TRIGGER = "!ladderheroes"
_ALT_TRIGGER = "!ladderhero"


class LadderHeroHandler(Handler):
    def __init__(self):
        self.rate_limited = False

    def can_handle_message(self, message: discord.Message) -> bool:
        return message.content in [_TRIGGER, _ALT_TRIGGER] and not self.rate_limited

    async def handle_message(self, client: discord.Client, message: discord.Message):
        self.rate_limited = True

        members = await perform_database_task(
            client.loop, FetchAllinMembersDatabaseTask()
        )
        member_games_played = [
            (int(member_id), member_data.get("current_season_games_played", 0))
            for member_id, member_data in members.items()
        ]
        member_games_played.sort(key=lambda x: x[1], reverse=True)
        member_games_played = member_games_played[:5]

        def get_name(discord_id: int) -> str:
            member = message.guild.get_member(discord_id)
            if member:
                return member.nick if member.nick else member.name
            else:
                return str(discord_id)

        message_lines = ["**Our Greatest Ladder Heroes This Season**"]
        if member_games_played:
            message_lines += [
                "{} has played {} games!".format(get_name(discord_id), games_played)
                for discord_id, games_played in member_games_played
            ]
        else:
            message_lines.append("We have no ladder heroes this season.")

        if message_lines:
            await message.channel.send("\n".join(message_lines))

        self.rate_limited = False

    async def description(self, client: discord.Client) -> str:
        return _TRIGGER + " - displays the current top five longest ladder win streaks."
