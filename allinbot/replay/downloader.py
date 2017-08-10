import re

CHUNK_SIZE = 1024

SC2REPLAYSTATS_PATTERN = re.compile(r'^http[s]?:\/\/sc2replaystats\.com\/download\/\d+$')
GGTRACKER_PATTERN = re.compile(r'^http[s]?:\/\/ggtracker\.com\/matches\/\d+\/replay$')
SPAWNINGTOOL_PATTERN = re.compile(r'^http[s]?:\/\/lotv\.spawningtool\.com\/\d+\/download[\/]?$')


def is_valid_replay_link(link: str) -> bool:
    return any(pattern.match(link) for pattern in [SC2REPLAYSTATS_PATTERN, GGTRACKER_PATTERN, SPAWNINGTOOL_PATTERN])
