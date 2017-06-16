from typing import List

from sc2reader.resources import Replay
from sc2reader.objects import Player


def list_zerg_players(replay: Replay) -> List[Player]:
    return [player for player in replay.players if player.play_race == "Zerg"]
