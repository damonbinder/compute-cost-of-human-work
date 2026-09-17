#!/usr/bin/env python3
"""Extract per-call token usage from ARC Prize replay recordings.

The ARC Prize replay viewer streams each recorded run as NDJSON from
`https://arcprize.org/api/recordings/<game_id>/<session_guid>`. One line is
written per environment step. For agent runs the line carries
`data.action_input.reasoning`, a JSON string holding the provider response
envelope, including the `usage` block the provider returned for that model call
(`input_tokens`, `input_tokens_details.cached_tokens`, `output_tokens`,
`output_tokens_details.reasoning_tokens`).

This script streams each recording, keeps only the usage numbers, and writes one
CSV row per run. The recording bodies are not retained: they are 3-60 MB each
and are reproducible from the same URL.

Usage:
    python3 fetch_usage.py <runs.csv> <out-usage.csv> [--limit N] [--filter SUBSTR]

`runs.csv` is the output of fetch_sessions.py and must carry `session_guid`,
`game_id`, `harness`, `effort` and `environment` columns. Rows already present
in an existing <out-usage.csv> are skipped, so the script can be resumed.

Dependencies: Python 3.9+ standard library only. Network access to arcprize.org.
"""
import csv
import io
import json
import os
import sys
import time
import urllib.request

API = 'https://arcprize.org/api/recordings/{game_id}/{guid}'
UA = 'Mozilla/5.0 (compatible; research-archive)'
FIELDS = [
    'session_guid', 'harness', 'effort', 'environment', 'game_id', 'config',
    'actions', 'lines', 'calls', 'usage_calls', 'input_tokens', 'cached_tokens',
    'output_tokens', 'reasoning_tokens', 'total_tokens', 'bytes',
]


def stream_usage(game_id: str, guid: str, tries: int = 4) -> dict:
    url = API.format(game_id=game_id, guid=guid)
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            agg = dict(lines=0, calls=0, usage_calls=0, input_tokens=0,
                       cached_tokens=0, output_tokens=0, reasoning_tokens=0,
                       total_tokens=0, bytes=0)
            with urllib.request.urlopen(req, timeout=300) as resp:
                reader = io.TextIOWrapper(resp, encoding='utf-8')
                for line in reader:
                    agg['bytes'] += len(line)
                    line = line.strip()
                    if not line:
                        continue
                    agg['lines'] += 1
                    rec = json.loads(line)
                    ai = (rec.get('data') or {}).get('action_input') or {}
                    raw = ai.get('reasoning')
                    if not raw:
                        continue
                    agg['calls'] += 1
                    try:
                        env = json.loads(raw)
                    except (ValueError, TypeError):
                        continue
                    usage = env.get('usage') if isinstance(env, dict) else None
                    if not isinstance(usage, dict):
                        continue
                    agg['usage_calls'] += 1
                    agg['input_tokens'] += int(usage.get('input_tokens') or 0)
                    det = usage.get('input_tokens_details') or {}
                    agg['cached_tokens'] += int(det.get('cached_tokens') or 0)
                    agg['output_tokens'] += int(usage.get('output_tokens') or 0)
                    odet = usage.get('output_tokens_details') or {}
                    agg['reasoning_tokens'] += int(odet.get('reasoning_tokens') or 0)
                    agg['total_tokens'] += int(usage.get('total_tokens') or 0)
            return agg
        except Exception as exc:  # noqa: BLE001 - retry any transport error
            last = exc
            if attempt == tries - 1:
                raise
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(last)


def main(argv) -> None:
    runs_csv, out_csv = argv[0], argv[1]
    limit = None
    filt = None
    rest = argv[2:]
    while rest:
        if rest[0] == '--limit':
            limit = int(rest[1])
            rest = rest[2:]
        elif rest[0] == '--filter':
            filt = rest[1]
            rest = rest[2:]
        else:
            raise SystemExit(__doc__)

    runs = list(csv.DictReader(open(runs_csv, newline='', encoding='utf-8')))
    done = set()
    if os.path.exists(out_csv):
        with open(out_csv, newline='', encoding='utf-8') as fh:
            done = {r['session_guid'] for r in csv.DictReader(fh)}
    todo = [r for r in runs if r['session_guid'] not in done]
    if filt:
        todo = [r for r in todo if filt in f"{r['harness']}:{r['effort']}"]
    if limit:
        todo = todo[:limit]

    new = not os.path.exists(out_csv)
    with open(out_csv, 'a', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            w.writeheader()
        for i, r in enumerate(todo, 1):
            agg = stream_usage(r['game_id'], r['session_guid'])
            row = {
                'session_guid': r['session_guid'], 'harness': r['harness'],
                'effort': r['effort'], 'environment': r['environment'],
                'game_id': r['game_id'], 'config': r.get('config', ''),
                'actions': r.get('actions', ''),
            }
            row.update(agg)
            w.writerow(row)
            fh.flush()
            print(f"{i}/{len(todo)} {r['harness']}/{r['effort']}/{r['environment']} "
                  f"calls={agg['usage_calls']} in={agg['input_tokens']} "
                  f"cached={agg['cached_tokens']} out={agg['output_tokens']}",
                  file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    main(sys.argv[1:])
