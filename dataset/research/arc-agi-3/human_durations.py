#!/usr/bin/env python3
"""Per-session human durations from the ARC-AGI-3 public-demo human testing set.

Input: the directory holding the parquet shards of the released dataset
(`magic-sword/arc_agi_3_public_demo_human_testing` on Hugging Face, a mirror of
the ARC Prize public-demo human dataset announced at
https://arcprize.org/blog/arc-agi-3-human-dataset).

Each row is one first-exposure play session on one public-demo environment. The
`trajectory` field is a JSON list of events, each carrying the timestamp at
which the environment returned the observation for an action. Session duration
is taken as last timestamp minus first timestamp; the session's own
`result_timestamp` is recorded alongside so the alternative end point can be
checked.

Output: one CSV row per session (env, guid, won, actions, resets, duration).

Usage:
    python3 human_durations.py <parquet-dir> <out-sessions.csv>

Dependencies: pandas and pyarrow (for parquet); Python 3.9+.
"""
import csv
import datetime
import glob
import json
import os
import sys

import pandas as pd

FIELDS = ['env', 'game_id', 'guid', 'won', 'state', 'actions', 'resets',
          'events', 'levels_completed', 'duration_s', 'duration_to_result_s',
          'first_timestamp', 'last_timestamp']


def _aslist(value, cast):
    """Parquet list columns arrive as numpy arrays, scalars or None."""
    if value is None:
        return []
    try:
        return [cast(v) for v in value]
    except TypeError:
        return [cast(value)]


def main(parquet_dir: str, out_csv: str) -> None:
    files = sorted(glob.glob(os.path.join(parquet_dir, '*.parquet')))
    if not files:
        raise SystemExit(f'no parquet shards under {parquet_dir}')
    rows = []
    skipped = 0
    for path in files:
        df = pd.read_parquet(path)
        for _, r in df.iterrows():
            traj = json.loads(r['trajectory'])
            stamps = [e.get('timestamp') for e in traj if isinstance(e, dict)]
            stamps = [s for s in stamps if isinstance(s, str)]
            if len(stamps) < 2:
                skipped += 1
                continue
            t0 = datetime.datetime.fromisoformat(stamps[0])
            t1 = datetime.datetime.fromisoformat(stamps[-1])
            try:
                tr = datetime.datetime.fromisoformat(str(r['result_timestamp']))
                to_result = (tr - t0).total_seconds()
            except (TypeError, ValueError):
                to_result = ''
            rows.append({
                'env': r['env'],
                'game_id': r['game_id'],
                'guid': r['guid'],
                'won': int(r['won']),
                'state': json.dumps(_aslist(r['states'], str)),
                'actions': int(r['total_actions']),
                'resets': json.dumps(_aslist(r['resets'], int)),
                'events': len(traj),
                'levels_completed': json.dumps(_aslist(r['levels_completed'], int)),
                'duration_s': round((t1 - t0).total_seconds(), 3),
                'duration_to_result_s': to_result,
                'first_timestamp': stamps[0],
                'last_timestamp': stamps[-1],
            })
        del df
    with open(out_csv, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f'{len(rows)} sessions written, {skipped} skipped -> {out_csv}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
