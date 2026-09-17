"""Recompute AlphaGo Zero operation and human-time recipes.

Python 3 standard library only. Usage: calculate.py SOURCE_DIR OUTPUT_JSON
Reads retained inputs and SGFs; never changes source evidence or candidate CSVs.
"""
import argparse
import json
import math
import re
from pathlib import Path


def forward(a, residual_blocks):
    s, c = a['board_side'] ** 2, a['width']
    k = a['kernel_side'] ** 2
    tower_convs = 1 + 2 * residual_blocks
    mac = {
        'stem': s * a['input_planes'] * c * k,
        'residual_convolutions': 2 * residual_blocks * s * c * c * k,
        'policy_convolution': s * c * a['policy_conv_channels'],
        'policy_linear': s * a['policy_conv_channels'] * a['policy_outputs'],
        'value_convolution': s * c * a['value_conv_channels'],
        'value_hidden': s * a['value_conv_channels'] * a['value_hidden'],
        'value_output': a['value_hidden'],
    }
    head_conv_positions = s * (a['policy_conv_channels'] + a['value_conv_channels'])
    flops = {
        'matrix_and_convolution': 2 * sum(mac.values()),
        'batch_normalization_affine': 2 * (tower_convs * s * c + head_conv_positions),
        'rectifiers': tower_convs * s * c + head_conv_positions + a['value_hidden'],
        'residual_additions': residual_blocks * s * c,
        'linear_biases': a['policy_outputs'] + a['value_hidden'] + 1,
        # exp each logit, reduction, division each logit, and scalar tanh.
        'softmax_and_tanh': a['policy_outputs'] * 3,
    }
    value_head_flops = (2 * (mac['value_convolution'] + mac['value_hidden'] +
                            mac['value_output']) + 3 * s * a['value_conv_channels'] +
                        a['value_hidden'] + a['value_hidden'] + 1 + 1)
    return {'residual_blocks': residual_blocks, 'macs': mac,
            'flops_components': flops, 'total_flops': sum(flops.values()),
            'value_head_flops': value_head_flops,
            'pruned_value_head_flops': sum(flops.values()) - value_head_flops}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_dir', type=Path)
    parser.add_argument('output_json', type=Path)
    args = parser.parse_args()
    inputs = json.loads((args.source_dir / 'inputs.json').read_text())
    f20, f40 = [forward(inputs['architecture'], r) for r in [19, 39]]
    sims = inputs['search']['evaluation_simulations']
    clocks = inputs['human_clock']
    timings = []
    for row in clocks['prefixes']:
        moves = math.ceil(row['move'] / 2)
        own = (clocks['initial_minutes'] - row['lee_minutes_left']) * 60
        other = (clocks['initial_minutes'] - row['opponent_minutes_left']) * 60
        timings.append({**row, 'lee_moves': moves,
                        'own_clock_seconds': own, 'opponent_clock_seconds': other,
                        'active_seconds_per_move_scenarios': {
                            str(frac): (own + frac * other) / moves
                            for frac in inputs['analyst_assumptions'][
                                'human_opponent_clock_engagement_scenarios']}})
    games = []
    for path in sorted((args.source_dir / 'games').rglob('*.sgf')):
        text = path.read_text()
        games.append({'file': str(path.relative_to(args.source_dir)),
                      'plies': len(re.findall(r';[BW]\[', text)),
                      'main_clock': re.findall(r'TM\[([^]]+)\]', text),
                      'byoyomi': re.findall(r'OT\[([^]]+)\]', text),
                      'per_move_clock_records': len(re.findall(r'[BW]L\[', text)),
                      'has_search_visit_annotations': bool(re.search(
                          r'simulations|visits|[NV]\[', text, re.I))})
    n5 = sims * inputs['search']['final_tournament_seconds_per_move'] / inputs['search']['approx_search_seconds']
    result = {
        'forward_20block': f20, 'forward_40block': f40,
        'nominal_1600_20block_flops': f20['total_flops'] * sims,
        'nominal_1600_40block_flops': f40['total_flops'] * sims,
        'nominal_1600_40block_half_or_quarter_call_reduction_scenarios': {
            str(fraction): f40['total_flops'] * sims * fraction
            for fraction in [1, 0.75, 0.5]},
        'human_prefixes': timings,
        'human_selected_seconds': inputs['analyst_assumptions']['human_selected_seconds'],
        'unincorporated_5_second_linear_extrapolation': {
            'nominal_calls': n5,
            'flops': f40['total_flops'] * n5,
            'warning': 'Not a measured final tournament workload; excluded from candidate CSV.'},
        'supplementary_games': games,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
