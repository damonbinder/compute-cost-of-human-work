#!/usr/bin/env python3
"""Recompute the Crystal estimate from explicit SOURCE_DIR and NEW_OUTPUT_DIR.

Python 3 standard library only. Reads evidence; never executes downloaded code.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path


def read_json(path):
    return json.loads(path.read_text())


def player_details(path):
    text = path.read_text()
    match = re.search(r'var ytInitialPlayerResponse\s*=\s*({.+?});', text)
    assert match, path
    return json.loads(match.group(1))['videoDetails']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_dir', type=Path)
    parser.add_argument('output_dir', type=Path)
    parser.add_argument('--assumptions', type=Path, default=Path(__file__).with_name('assumptions.json'))
    args = parser.parse_args()
    source, output = args.source_dir.resolve(), args.output_dir.resolve()
    if output.exists() or output == source or source in output.parents:
        raise SystemExit('Output must be a new directory outside the evidence directory.')
    manifest = read_json(source / 'manifest.json')
    for item in manifest['files']:
        assert hashlib.sha256((source / item['path']).read_bytes()).hexdigest() == item['sha256'], item['path']
    a = read_json(args.assumptions)
    blog = (source / 'gemini-crystal.html').read_text()
    assert 'turn 24,178 using 1.88 billion tokens' in blog
    commits = read_json(source / 'gemini3-commit-dec08-03.json')
    finish = [c for c in commits if c['sha'] == a['finish_commit']]
    assert len(finish) == 1 and finish[0]['commit']['message'] == 'Turn 24178'
    assert read_json(source / 'gemini3-start-custom_tools.json') == {}
    assert read_json(source / 'gemini3-red-custom_agents.json') == {}

    history = read_json(source / 'gemini3-agent-history.json')
    history = sorted([c for c in history if c['commit']['author']['date'] >= a['race_start_utc']],
                     key=lambda c: c['commit']['author']['date'])
    assert history[0]['commit']['message'] == 'Turn 0'
    helper_records = []
    for c in history:
        config = read_json(source / 'agent-config-history' / (c['sha'] + '.json'))
        helper_records.append({'turn': int(c['commit']['message'].split()[1]),
                               'date': c['commit']['author']['date'], 'sha': c['sha'],
                               'names': list(config)})
    available_turns = 0
    creation_episodes = 0
    for i, h in enumerate(helper_records):
        end = helper_records[i+1]['turn'] if i+1 < len(helper_records) else a['author_reported_turns']
        assert end >= h['turn']
        if h['names']:
            available_turns += end - h['turn']
            if not i or not helper_records[i-1]['names']:
                creation_episodes += 1

    config = read_json(source / 'clip-proxy-config.json')['vision_config']
    d, ff, layers = config['hidden_size'], config['intermediate_size'], config['num_hidden_layers']
    patch = config['patch_size']
    patches = (config['image_size'] // patch) ** 2
    n = patches + 1
    frontend = {
        'patch_projection': 2 * patches * 3 * patch ** 2 * d,
        'qkv_and_output_projections': layers * 8 * n * d * d,
        'feedforward_projections': layers * 4 * n * d * ff,
        'attention_matrix_products': layers * 4 * n * n * d,
    }
    assert patches == 256
    reported = a['author_reported_total_tokens']
    turns = a['author_reported_turns']
    images = turns * a['images_per_primary_turn']
    image_units = images * a['image_accounting_units_per_image']
    text = reported - image_units
    visual = images * a['physical_visual_positions_per_image']
    vision_flops = images * a['frontend_views_per_image'] * sum(frontend.values())

    def compute(params=None, removed_cache=0, helper_extra=0, image_units_override=None, visual_override=None):
        params = a['active_parameters'] if params is None else params
        text_work = reported - (image_units if image_units_override is None else image_units_override)
        text_work = max(0, text_work - removed_cache) + helper_extra
        visual_work = visual if visual_override is None else visual_override
        return 2 * params * (text_work + visual_work) + vision_flops

    archive = player_details(source / 'human-crystal-longplayarchive.html')
    wol = player_details(source / 'human-crystal-wol.html')
    assert archive['videoId'] == 'mYaoA_EGFjs' and wol['videoId'] == 'eeFFCjdfjYY'
    assert '8:50:47 - Credits #2' in archive['shortDescription']
    assert 'all in one sitting' in wol['shortDescription']
    assert 'ends after I defeat Red' in wol['shortDescription']
    donors = [a['human_longplayarchive_stop_seconds'] - a['human_longplayarchive_first_credits_seconds'],
              int(wol['lengthSeconds']) - a['human_wol_end_credits_allowance_seconds'] - a['human_wol_first_credits_allowance_seconds']]
    donor_mean = sum(donors) / 2
    helper_extra = available_turns * a['missing_helper_scenario_tokens_per_available_turn']
    scenarios = {
        'active_parameters': {str(p): compute(params=p) for p in a['active_parameter_sensitivity']},
        'hypothetical_cache_reads': {str(f): compute(removed_cache=int(reported*f)) for f in a['cache_sensitivity_fractions_of_author_total']},
        'reported_total_excluded_all_helpers_one_call_per_available_turn': compute(helper_extra=helper_extra),
        'extra_completed_retry_work_2pct': compute() * (1 + a['missing_completed_retry_scenario_primary_equivalents']),
        'low_media_280_accounting_units_256_visual_positions': compute(image_units_override=images*280, visual_override=images*256),
        'images_retained_50_5_times_in_history': compute(image_units_override=int(image_units*50.5), visual_override=int(visual*50.5)),
    }
    result = {
        'point_id': a['point_id'], 'source_hashes_verified': len(manifest['files']),
        'author_reported_total_tokens': reported, 'author_reported_turns': turns,
        'finish_commit': a['finish_commit'], 'finish_commit_time_utc': finish[0]['commit']['author']['date'],
        'estimated_image_presentations': images, 'estimated_visual_accounting_units_removed': image_units,
        'text_tokens': text, 'physical_visual_positions_proxy': visual,
        'frontend_per_view_components': frontend, 'frontend_per_view_flops': sum(frontend.values()),
        'frontend_flops': vision_flops, 'compute_flops': compute(),
        'helper_configuration_changes_in_race': len(helper_records),
        'helper_creation_episodes': creation_episodes, 'turn_intervals_with_helper_available': available_turns,
        'helper_scenario_additional_tokens': helper_extra, 'scenarios_flops': scenarios,
        'human_donor_recorded_video_seconds': [int(archive['lengthSeconds']), int(wol['lengthSeconds'])],
        'human_donor_seconds_to_red_after_small_credit_allowances': donors,
        'human_donor_mean_after_allowances': donor_mean,
        'human_estimate_before_rounding_seconds': donor_mean + 3600*(a['human_extra_navigation_and_puzzle_hours']+a['human_extra_team_training_hours']),
        'human_time': a['human_hours']*3600, 'human_time_sensitivity_seconds': [h*3600 for h in a['human_hours_sensitivity']],
    }
    output.mkdir(parents=True)
    for name, obj in [('calculations.json', result), ('helper-history.json', helper_records),
                       ('human-video-descriptions.json', [archive, wol])]:
        (output / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({k: result[k] for k in ['point_id', 'compute_flops', 'text_tokens', 'human_time']}))


if __name__ == '__main__':
    main()
