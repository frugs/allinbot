import tempfile
import re

import aiohttp
import sc2reader
from sc2reader.resources import Replay

CHUNK_SIZE = 1024

SC2REPLAYSTATS_PATTERN = re.compile(r'http[s]?:\/\/sc2replaystats\.com\/download\/\d+')


def is_valid_replay_link(link: str) -> bool:
    return SC2REPLAYSTATS_PATTERN.match(link)

async def download_and_load_replay(link: str) -> Replay:
    with tempfile.TemporaryFile() as replay_file:
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                while True:
                    chunk = await resp.content.read(CHUNK_SIZE)
                    if not chunk:
                        break

                    replay_file.write(chunk)

        return sc2reader.load_replay(replay_file, level=4)
