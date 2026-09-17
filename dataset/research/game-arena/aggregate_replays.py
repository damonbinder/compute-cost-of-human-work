"""Aggregate per-call token counters from the Kaggle Game Arena chess replay archive.

Purpose: establish what the leaderboard column "Avg. Tokens/Turn" counts, by
comparing per-model replay means against the published board values.

Dependencies: Python 3.9+ standard library only.

Input  --archive : the zip served by
    https://www.kaggle.com/api/v1/datasets/download/kaggle/chess-text-gameplay
    (unauthenticated; 384,331,069 bytes / 5,686 episode JSON files when pulled
    2026-09-13, dataset version 11, lastUpdated 2026-09-08T21:07:21Z).
Input  --leaderboard : agent-work/sources/game-arena/kaggle-chess-text-v2-leaderboard.json
Output --output : a new JSON file (must not already exist).

Each move record carries generate_returns, one JSON string per LLM call for that
move (retries included). Counters used: prompt_tokens, generation_tokens,
reasoning_tokens, total_tokens. The optional call_details field carries the same per-call records but is
absent on about 29% of moves, so a length check against it corroborates nothing where it is missing; its
presence, absence and any length disagreement are all counted rather than assumed.
"""
import argparse, collections, json, zipfile
from pathlib import Path

TOK_TASK_V2 = 1892  # "Average Tokens per Turn" child task on chess-text v2
SCORE_TASK_V2 = 1446

p = argparse.ArgumentParser()
p.add_argument('--archive', type=Path, required=True)
p.add_argument('--leaderboard', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
assert not out.exists(), f'output already exists: {out}'

lb = json.loads(a.leaderboard.read_text())
published = {}
for r in lb['rows']:
    res = {x.get('taskVersionId'): x.get('numericResult', {}).get('value') for x in r['results']}
    published[r['modelVersion']['displayName']] = {
        'avg_tokens_per_turn': res.get(TOK_TASK_V2),
        'game_arena_elo': res.get(SCORE_TASK_V2),
        'model_proxy_slug': r['modelVersion'].get('modelProxySlug'),
    }

agg = collections.defaultdict(lambda: collections.Counter())
episodes = 0
with zipfile.ZipFile(a.archive) as z:
    for name in z.namelist():
        if not name.endswith('.json'):
            continue
        d = json.loads(z.read(name))
        agents = [x.get('Name') for x in d['info']['Agents']]
        episodes += 1
        for step in d['steps']:
            for pi, player in enumerate(step):
                act = player.get('action')
                if not (isinstance(act, dict) and act.get('generate_returns')):
                    continue
                agent = agents[pi] if pi < len(agents) else None
                s = agg[agent]
                s['moves'] += 1
                s['episodes_seen'] += 0
                calls = act['generate_returns']
                cd = act.get('call_details')
                if isinstance(cd, list):
                    s['call_details_present'] += 1
                    if len(cd) != len(calls):
                        s['call_details_mismatch'] += 1
                else:
                    s['call_details_absent'] += 1
                for g in calls:
                    o = json.loads(g) if isinstance(g, str) else g
                    pt = o.get('prompt_tokens') or 0
                    gt = o.get('generation_tokens') or 0
                    rt = o.get('reasoning_tokens') or 0
                    tt = o.get('total_tokens') or 0
                    s['calls'] += 1
                    s['prompt_tokens'] += pt
                    s['generation_tokens'] += gt
                    s['reasoning_tokens'] += rt
                    s['total_tokens'] += tt
                    if tt == pt + gt:
                        s['calls_total_eq_prompt_plus_generation'] += 1
                    if tt == 0:
                        s['calls_total_zero'] += 1
                    if gt == 0:
                        s['calls_generation_zero'] += 1

models = {}
for agent, s in agg.items():
    n = s['moves']
    if not n:
        continue
    consistent = (s['calls_total_eq_prompt_plus_generation'] == s['calls'])
    rec = {
        'moves': n, 'calls': s['calls'],
        'calls_per_move': s['calls'] / n,
        'mean_prompt_tokens_per_move': s['prompt_tokens'] / n,
        'mean_generation_tokens_per_move': s['generation_tokens'] / n,
        'mean_reasoning_tokens_per_move': s['reasoning_tokens'] / n,
        'mean_total_tokens_field_per_move': s['total_tokens'] / n,
        'mean_prompt_plus_generation_per_move': (s['prompt_tokens'] + s['generation_tokens']) / n,
        'counters_internally_consistent': consistent,
        'calls_total_zero': s['calls_total_zero'],
        'calls_generation_zero': s['calls_generation_zero'],
        'call_details_present_moves': s['call_details_present'],
        'call_details_absent_moves': s['call_details_absent'],
        'call_details_count_mismatches_where_present': s['call_details_mismatch'],
    }
    pub = published.get(agent)
    if pub and pub['avg_tokens_per_turn']:
        t = pub['avg_tokens_per_turn']
        rec['published_avg_tokens_per_turn'] = t
        rec['ratio_prompt_plus_generation_to_published'] = rec['mean_prompt_plus_generation_per_move'] / t
        rec['ratio_generation_only_to_published'] = rec['mean_generation_tokens_per_move'] / t
    models[agent] = rec

verify = {k: v for k, v in models.items()
          if v.get('counters_internally_consistent') and v['calls_total_zero'] == 0
          and 'published_avg_tokens_per_turn' in v and v['moves'] >= 1000}
result = {
    'archive': a.archive.name,
    'episodes_parsed': episodes,
    'note': ('Verification subset = models whose per-call counters satisfy '
             'total_tokens == prompt_tokens + generation_tokens on every call, with at least '
             '1,000 recorded moves and a published Avg. Tokens/Turn on chess-text v2.'),
    'verification_subset_ratio_prompt_plus_generation': {
        k: v['ratio_prompt_plus_generation_to_published'] for k, v in sorted(verify.items())},
    'verification_subset_ratio_generation_only': {
        k: v['ratio_generation_only_to_published'] for k, v in sorted(verify.items())},
    'by_agent': dict(sorted(models.items())),
}
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, indent=2) + '\n')
print('episodes', episodes, 'agents', len(models), 'verification subset', len(verify))
