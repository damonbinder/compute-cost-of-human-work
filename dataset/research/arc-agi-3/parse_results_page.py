#!/usr/bin/env python3
"""Parse the ARC Prize per-model results page into the public-demo cell index.

Input: the saved HTML of https://arcprize.org/results/<model-slug>.
Output: CSV with one row per (harness, environment, reasoning effort) cell,
carrying the printed RHAE score and the replay session GUID the cell links to.

Usage:
    python3 parse_results_page.py <results-page.html> <out.csv>

Dependencies: Python 3.9+ standard library only.
"""
import csv
import html
import re
import sys

CELL_RE = re.compile(
    r'<a href="https://arcprize\.org/replay/([0-9a-f-]{36})"[^>]*'
    r'title="View ([^"]*?) scorecard for ([A-Z0-9]+)"[^>]*>'
    r'<span[^>]*>([0-9.]+)<!-- -->%</span></a>'
)
TABLE_RE = re.compile(r'<table.*?</table>', re.S)


def harness_of(table_html: str) -> str:
    # The harness caption precedes the table in the same section; fall back to
    # the order the page renders them in (Standard first, Provider Adapter
    # second) when the caption is not inside the table element.
    if 'Provider Adapter' in table_html:
        return 'provider_adapter'
    return 'standard'


def main(src: str, dst: str) -> None:
    page = open(src, encoding='utf-8', errors='replace').read()
    # The two ARC-AGI-3 tables are the ones whose cells link to /replay/.
    tables = [t for t in TABLE_RE.findall(page) if '/replay/' in t]
    if len(tables) != 2:
        raise SystemExit(f'expected 2 replay tables, found {len(tables)}')
    rows = []
    for order, table in enumerate(tables):
        harness = 'standard' if order == 0 else 'provider_adapter'
        for guid, title, env, score in CELL_RE.findall(table):
            title = html.unescape(title)
            # Titles read "<model> (<Effort>)" on the Standard table and
            # "<model> (<Effort> (Provider Adapter))" on the adapter table.
            m = re.search(r'\((\w+)(?: \(Provider Adapter\))?\)\s*$', title)
            effort = m.group(1).lower() if m else ''
            model = re.sub(r'\s*\(.*\)\s*$', '', title).strip()
            rows.append({
                'harness': harness,
                'environment': env,
                'effort': effort,
                'model_display': model,
                'rhae_pct': float(score),
                'session_guid': guid,
            })
    if not rows:
        raise SystemExit('no cells parsed')
    with open(dst, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f'{len(rows)} cells -> {dst}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
