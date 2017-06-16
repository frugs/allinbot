import json
import urllib.parse

import techlabreactor

from sc2reader.objects import Player
from sc2reader.resources import Replay


def _convert_inject_states_to_data_set(inject_states: list, fps: int) -> list:
    return [[
                {"x": int((frame * 1000) / (1.4 * fps)), "y": (offset * 10) + (9 if state else 0)}
                for frame, state
                in states
                ]
            for offset, states
            in enumerate(inject_states)]


def generate_inject_efficiency_page_data_for_player(player: Player, replay: Replay) -> str:
    inject_states = techlabreactor.get_hatchery_inject_states_for_player(player, replay)
    chart_data = _convert_inject_states_to_data_set(inject_states, int(replay.game_fps))
    inject_efficiency = techlabreactor.calculate_inject_efficiency(inject_states)
    inject_efficiency_str = "{0:.2f}".format(inject_efficiency * 100)

    json_string = json.dumps({
        "chartData": chart_data,
        "injectEfficiency": inject_efficiency_str,
        "playerName": player.name
    })
    return urllib.parse.quote(json_string)