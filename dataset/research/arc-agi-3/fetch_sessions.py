#!/usr/bin/env python3
"""Fetch ARC Prize session metadata for a list of replay session GUIDs.

Input:  the cell index produced by parse_results_page.py (needs a
        `session_guid` column).
Output: one JSON file holding the raw `/api/sessions/<guid>` payload for every
        GUID, keyed by GUID, plus a CSV of the flattened per-run fields.

The endpoint is unauthenticated and returns, per environment run: the RHAE
score, levels completed, total actions, per-level scores, per-level actions and
the per-level human baseline action counts, plus session open/last-update
timestamps and the model config id that produced the run.

Usage:
    python3 fetch_sessions.py <cells.csv> <out-sessions.json> <out-runs.csv>

Dependencies: Python 3.9+ standard library only. Network access to arcprize.org.
"""
import csv
import json
import sys
import time
import urllib.request

API = 'https://arcprize.org/api/sessions/{}'
UA = 'Mozilla/5.0 (compatible; research-archive)'


def fetch(guid: str, tries: int = 4) -> dict:
    for attempt in range(tries):
        try:
            req = urllib.request.Request(API.format(guid), headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as exc:  # noqa: BLE001 - retry any transport error
            if attempt == tries - 1:
                raise
            time.sleep(2 * (attempt + 1))
            last = exc
    raise RuntimeError(last)


def main(cells_csv: str, out_json: str, out_csv: str) -> None:
    cells = list(csv.DictReader(open(cells_csv, newline='', encoding='utf-8')))
    guids = []
    seen = set()
    for row in cells:
        g = row['session_guid']
        if g not in seen:
            seen.add(g)
            guids.append(g)
    payloads = {}
    for i, guid in enumerate(guids, 1):
        payloads[guid] = fetch(guid)
        if i % 25 == 0:
            print(f'{i}/{len(guids)}', file=sys.stderr)
    with open(out_json, 'w', encoding='utf-8') as fh:
        json.dump(payloads, fh, indent=1, sort_keys=True)

    index = {row['session_guid']: row for row in cells}
    out = []
    for guid, payload in payloads.items():
        cell = index[guid]
        for env in payload.get('environments', []):
            for run in env.get('runs', []):
                out.append({
                    'session_guid': guid,
                    'harness': cell['harness'],
                    'effort': cell['effort'],
                    'environment': cell['environment'],
                    'page_rhae_pct': cell['rhae_pct'],
                    'config': payload.get('config'),
                    'model': payload.get('model'),
                    'game_id': run.get('id'),
                    'api_score': run.get('score'),
                    'levels_completed': run.get('levels_completed'),
                    'level_count': env.get('level_count'),
                    'actions': run.get('actions'),
                    'resets': run.get('resets'),
                    'state': run.get('state'),
                    'level_scores': json.dumps(run.get('level_scores')),
                    'level_actions': json.dumps(run.get('level_actions')),
                    'level_baseline_actions': json.dumps(run.get('level_baseline_actions')),
                    'open_at': payload.get('open_at'),
                    'last_update': payload.get('last_update'),
                })
    with open(out_csv, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(f'{len(payloads)} sessions, {len(out)} runs -> {out_json}, {out_csv}')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
