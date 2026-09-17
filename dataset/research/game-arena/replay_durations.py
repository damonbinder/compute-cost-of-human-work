"""Realized per-move wall-clock durations and call_details coverage in the chess replay archive.

Dependencies: Python 3.9+ standard library only.

Usage:
    python3 replay_durations.py --archive /abs/path/to/chess-text-gameplay.zip \
        --output /abs/path/to/new-output.json [--sources /abs/path/to/sources/game-arena]

--output must not already exist, and if --sources is given it must not sit inside that directory, so
reproduction writes new outputs rather than modifying retained evidence.

The archive is the unauthenticated download from
https://www.kaggle.com/api/v1/datasets/download/kaggle/chess-text-gameplay (384,331,069 bytes, dataset
version 11 when pulled 2026-09-13). Duration is summed over a move's call_details entries, so it is only
available on moves that carry that optional field; the output also reports how often the field is absent.
"""
import argparse, zipfile, json, collections, statistics
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--archive', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--sources', type=Path, default=None)
args = parser.parse_args()
out_path = args.output.resolve()
assert not out_path.exists(), f'output already exists: {out_path}'
if args.sources:
    src = args.sources.resolve()
    assert src not in out_path.parents and src != out_path, \
        'output must not be written inside the retained sources'

z = zipfile.ZipFile(args.archive)
agg = collections.defaultdict(list)
cd_present = cd_absent = moves = 0
eps_with_absent = set()
for name in z.namelist():
    if not name.endswith('.json'):
        continue
    d = json.loads(z.read(name))
    agents = [x.get('Name') for x in d['info']['Agents']]
    for step in d['steps']:
        for pi, player in enumerate(step):
            act = player.get('action')
            if not (isinstance(act, dict) and act.get('generate_returns')):
                continue
            moves += 1
            cd = act.get('call_details')
            if isinstance(cd, list):
                cd_present += 1
                agg[agents[pi] if pi < len(agents) else None].append(
                    sum((c.get('duration_secs') or 0) for c in cd))
            else:
                cd_absent += 1
                eps_with_absent.add(name)

by_agent = {}
for k, v in agg.items():
    if len(v) >= 1000:
        by_agent[k] = {'n_moves_with_duration': len(v), 'mean_seconds_per_move': statistics.mean(v),
                       'median_seconds_per_move': statistics.median(v)}
res = {'moves_total': moves, 'moves_with_call_details': cd_present, 'moves_without_call_details': cd_absent,
       'episodes_with_any_missing_call_details': len(eps_with_absent),
       'fraction_missing': cd_absent / moves, 'by_agent': dict(sorted(by_agent.items()))}
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(res, indent=2) + '\n')
print('moves', moves, 'call_details present', cd_present, 'absent', cd_absent,
      '= %.1f%%' % (100 * cd_absent / moves), '| episodes affected', len(eps_with_absent))
