import os
import tempfile

import aiohttp
import discord
import sc2reader

from allinbot.handler import Handler
from .replay import is_valid_replay_link, list_zerg_players

TRIGGER = "!injects "
TRIGGER_ALT = "!injectefficiency "
TRIM_API_KEY = os.getenv("TRIM_API_KEY", "")
CHUNK_SIZE = 1024


class QueenInjectEfficiencyHandler(Handler):
    def description(self) -> str:
        return TRIGGER + "{link_to_replay} - show queen inject efficiency diagram for replay."

    def can_handle_message(self, message: discord.Message) -> bool:
        return message.content.startswith(TRIGGER) or message.content.startswith(TRIGGER_ALT)

    async def handle_message(self, client: discord.Client, message: discord.Message):
        replay_url = message.content[len(TRIGGER):]

        if not is_valid_replay_link(replay_url):
            await client.send_message(message.channel, "Invalid replay link.")
            return

        _, replay_path = tempfile.mkstemp(suffix=".SC2Replay")

        replay_file = open(replay_path, mode="w+b")

        async with aiohttp.ClientSession() as session:
            async with session.get(replay_url) as resp:
                while True:
                    chunk = await resp.content.read(CHUNK_SIZE)
                    if not chunk:
                        break

                    replay_file.write(chunk)

        replay = sc2reader.load_replay(replay_file)

        if replay.build < 53644 or replay.expansion != "LotV":
            await client.send_message(message.channel, "Replay unsupported.")
            return

        zerg_players = list_zerg_players(replay)

        if not zerg_players:
            await client.send_message(message.channel, "No Zerg players in replay!")
            return

        replay_file.seek(0)

        async with aiohttp.ClientSession() as session:
            post_url = "http://allinbot.cloudapp.net/inject-plot/upload"
            form_data = aiohttp.FormData()
            form_data.add_field(
                "file",
                replay_file,
                filename=replay_url,
                content_type="application/octet-stream")
            async with session.post(post_url, data=form_data) as resp:
                if resp.status == 200:
                    inject_plot_url = str(resp.url)
                    await client.send_message(message.channel, "Queen Inject Efficiency Visualiser - " + inject_plot_url)

        replay_file.close()
        os.remove(replay_path)


