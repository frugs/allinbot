import base64
import json
import gzip
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

    overall_inject_efficiency = techlabreactor.calculate_overall_inject_efficiency(inject_states)
    overall_inject_efficiency_str = "{0:.2f}".format(overall_inject_efficiency * 100)

    inject_efficiency_from_first_queen_completed = techlabreactor.calculate_inject_efficiency_from_frame(
        techlabreactor.find_first_queen_completed_frame_for_player(player, replay),
        inject_states)
    inject_efficiency_from_first_queen_completed_str = "{0:.2f}".format(inject_efficiency_from_first_queen_completed * 100)

    inject_pops = techlabreactor.get_inject_pops_for_player(player, replay)

    json_string = json.dumps({
        "chartData": chart_data,
        "overallInjectEfficiency": overall_inject_efficiency_str,
        "injectEfficiencyFromFirstQueenCompleted": inject_efficiency_from_first_queen_completed_str,
        "playerName": player.name,
        "inject_pops": inject_pops
    })

    compressed_and_encoded_json_string = base64.b64encode(gzip.compress(json_string.encode())).decode()

    return urllib.parse.quote(compressed_and_encoded_json_string)
