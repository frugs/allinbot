import tempfile
import re

import aiohttp
import sc2reader
from sc2reader.resources import Replay

CHUNK_SIZE = 1024

SC2REPLAYSTATS_PATTERN = re.compile(r'^http[s]?:\/\/sc2replaystats\.com\/download\/\d+$')
GGTRACKER_PATTERN = re.compile(r'^http[s]?:\/\/ggtracker\.com\/matches\/\d+\/replay$')
SPAWNINGTOOL_PATTERN = re.compile(r'^http[s]?:\/\/lotv\.spawningtool\.com\/\d+\/download[\/]?$')


def is_valid_replay_link(link: str) -> bool:
    return any(pattern.match(link) for pattern in [SC2REPLAYSTATS_PATTERN, GGTRACKER_PATTERN, SPAWNINGTOOL_PATTERN])

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
