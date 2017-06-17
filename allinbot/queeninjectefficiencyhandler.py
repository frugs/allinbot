import os

import discord
import aiohttp

from allinbot.handler import Handler
from .replay import is_valid_replay_link, download_and_load_replay, list_zerg_players, generate_inject_efficiency_page_data_for_player

TRIGGER = "!injects "
TRIGGER_ALT = "!injectefficiency "
TRIM_API_KEY = os.getenv("TRIM_API_KEY", "")


class QueenInjectEfficiencyHandler(Handler):
    def description(self) -> str:
        return TRIGGER + "{link_to_replay} - show queen inject efficiency diagram for replay."

    def can_handle_message(self, message: discord.Message) -> bool:
        return message.content.startswith(TRIGGER) or message.content.startswith(TRIGGER_ALT)

    async def handle_message(self, client: discord.Client, message: discord.Message):
        link = message.content[len(TRIGGER):]

        if not is_valid_replay_link(link):
            await client.send_message(message.channel, "Invalid replay link.")
            return

        replay = await download_and_load_replay(link)

        if replay.build < 53644 or replay.expansion != "LotV":
            await client.send_message(message.channel, "Replay unsupported.")
            return

        zerg_players = list_zerg_players(replay)

        if not zerg_players:
            await client.send_message(message.channel, "No Zerg players in replay!")
            return

        for player in zerg_players:
            page_data = generate_inject_efficiency_page_data_for_player(player, replay)
            inject_plot_link = "http://allinbot.cloudapp.net/inject-plot/?data=" + page_data

            async with aiohttp.ClientSession() as session:
                headers = {
                    "x-api-key": TRIM_API_KEY
                }
                data = {
                    "longUrl": inject_plot_link,
                }
                async with session.post("https://tr.im/links", data=data, headers=headers) as resp:
                    response_content = await resp.json()

            await client.send_message(message.channel, player.name + " - " + response_content["url"])


