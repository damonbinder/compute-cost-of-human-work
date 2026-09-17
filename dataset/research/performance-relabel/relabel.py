"""Derive performance_vs_human dispositions under the amended scale.

Usage: python3 relabel.py <folder-root> <out-csv> [<out-json>]

Reads the root points.csv and the two pending candidate CSVs. Writes the override file
(point_id, old_label, new_label, action, reason) holding every row whose label changes or
which is excluded, and optionally a JSON dump of every row examined for the research note.

Rule (DECISIONS.md, "Below means somewhat below; substantially below is removed", which
supersedes the far_below half of the granularity ruling). The scale is
below / match / above / far_above / unknown; there is no far_below.

  ratio = (ai - floor) / (human - floor) on the benchmark's own metric
  below   is kept when the AI basically does the job somewhat worse: it completed the job at
          lower quality, or ratio >= 0.50
  exclude otherwise, into excluded.csv with exclusion_reason, evidence retained

The completion arm is only reachable where the benchmark has a completion criterion the AI
met. On accuracy-scored benchmarks every model "completes" the question set, so the ratio
governs; Damon's ruling names HourVideo among the rows expected to leave, which fixes that
reading.
"""
import csv, json, re, sys, pathlib, collections

root = pathlib.Path(sys.argv[1]); out = pathlib.Path(sys.argv[2])
KEEP_BELOW = 0.50          # ratio at or above which `below` is still the right label
ABOUT_HALF = 0.45          # rows between this and KEEP_BELOW are flagged as "about half"

def num(s, pat):
    m = re.search(pat, s)
    return float(m.group(1)) if m else None

examined = []

def record(pid, batch, old, new, ratio, metric, reason, action='none', flag=''):
    examined.append({'point_id': pid, 'batch': batch, 'old_label': old, 'new_label': new,
                     'ratio': ratio, 'metric': metric, 'reason': reason, 'action': action,
                     'flag': flag})

def judge(pid, batch, old, ai, human, floor, metric, reason_fmt):
    """Apply the kept-below threshold to one chance-adjusted score pair."""
    ratio = (ai - floor) / (human - floor)
    reason = reason_fmt.format(r=ratio)
    if ratio >= KEEP_BELOW:
        record(pid, batch, old, old, ratio, metric, reason)
    else:
        flag = 'about half' if ratio >= ABOUT_HALF else ''
        record(pid, batch, old, old, ratio, metric, reason, 'exclude', flag)

CRAFTER_H, CRAFTER_FLOOR = 63.18, 10.4

# ---- root points.csv, plus any rows already moved to excluded.csv ----------
# Reading both keeps the derivation re-runnable after the overrides have been applied:
# an excluded row is still examined and still reaches the same disposition.
accepted = list(csv.DictReader(open(root / 'points.csv')))
if (root / 'excluded.csv').exists():
    accepted += list(csv.DictReader(open(root / 'excluded.csv')))

for r in accepted:
    pid, old, ev = r['point_id'], r['performance_vs_human'], r['performance_evidence']

    if pid.startswith('game-balrog-crafter-') and old == 'below':
        ai = num(ev, r'progression ([\d.]+)%')
        judge(pid, 'balrog', old, ai, CRAFTER_H, CRAFTER_FLOOR, f'{ai:.2f}% progression',
              f'Crafter progression {ai:.2f}% against the human expert 63.18%, {{r:.2f}} of the '
              f'human above the 10.4% random floor')

    elif pid.startswith('game-vgb-'):
        w = num(ev, r'reached ([\d.]+)% of the walkthrough')
        judge(pid, 'videogamebench', old, w, 100.0, 0.0, f'{w:.2f}% of walkthrough',
              f'criterion is completing the game and the run reached {w:.2f}% of the walkthrough, '
              f'{{r:.2f}} of the completing human')

    elif pid.startswith('work-rli-'):
        a = num(ev, r'\(([\d.]+)%\)')
        judge(pid, 'remote-labor-index', old, a, 100.0, 0.0, f'{a:.2f}% automation rate',
              f'automation rate {a:.2f}% against 100% of the paid human deliverables meeting the '
              f'same bar by construction')

    elif pid.startswith('perc-hourvideo-'):
        ai = num(ev, r'scored ([\d.]+)% on the 570-MCQ')
        judge(pid, 'hourvideo', old, ai, 85.0, 20.0, f'{ai:.1f}% accuracy',
              f'{ai:.1f}% against three human experts at 85.0%, {{r:.2f}} of the human above the '
              f'20% guessing floor')

    elif pid in ('agen-mirrorcode-gotree-py-opus4', 'agen-mirrorcode-gotree-py-opus41',
                 'agen-mirrorcode-gotree-py-opus45'):
        eps = {'agen-mirrorcode-gotree-py-opus4': (1.2, 15.3, 9.8),
               'agen-mirrorcode-gotree-py-opus41': (15.8, 23.5, 7.6),
               'agen-mirrorcode-gotree-py-opus45': (47.3, 3.7, 63.2)}[pid]
        mean = sum(eps) / 3
        judge(pid, 'mirrorcode', old, mean, 100.0, 0.0, f'{mean:.1f}% mean pass rate',
              f"episodes passed {'/'.join(str(e) for e in eps)}% of 2,001 cases, mean {mean:.1f}%, "
              f"against a complete-pass criterion the run never met")

    elif pid in ('agen-mirrorcode-pkl-c-opus46', 'agen-mirrorcode-pkl-rust-opus46'):
        p = num(ev, r'passed [\d,]+ of 770 cases, ([\d.]+)%')
        judge(pid, 'mirrorcode', old, p, 100.0, 0.0, f'{p:.1f}% pass rate',
              f'passed {p:.1f}% of 770 cases against a complete-pass criterion, with pkl reported '
              f'unsolved under the budget')

    elif pid == 'agen-mirrorcode-pkl-py-opus46':
        judge(pid, 'mirrorcode', old, 38.6, 100.0, 0.0, '38.6% transferred pass rate',
              'scoring pass crashed, so the disposition transfers from the same model and budget '
              'in C and Rust at 41.7% and 35.5% against a complete-pass criterion')

    else:
        # Every remaining row keeps its label. The match rows rest on a completion or
        # matched-quality criterion both sides met; LAIT and the three LUMEN `below` rows
        # reach `below` by the completion arm (the job was done at lower quality); the one
        # `above` row is checked for far_above below.
        record(pid, 'unchanged', old, old, None, None, None)

# ---- far_above check on the one `above` row --------------------------------
for e in examined:
    if e['old_label'] == 'above':
        e['reason'] = ('fastest AI heat 16.59 s against the fastest human 19.14 s, a 15% edge, '
                       'so the human side plainly still does the job')
        e['metric'] = 'lap time'
        e['flag'] = 'far_above considered and rejected'

# ---- pending candidates ----------------------------------------------------
for r in csv.DictReader(open(root / 'candidates/apex-agents/points.csv')):
    p = num(r['performance_evidence'], r'Pass@1 ([\d.]+)%')
    judge(r['point_id'], 'apex-agents (candidate)', r['performance_vs_human'], p, 100.0, 0.0,
          f'{p:.1f}% pass@1',
          f'pass@1 {p:.1f}% against an expert-written gold arm passing by construction')

for r in csv.DictReader(open(root / 'candidates/epoch-swebench-bins/points.csv')):
    p = num(r['performance_evidence'], r'in this bin \(([\d.]+)%\)')
    judge(r['point_id'], 'epoch-swebench-bins (candidate)', r['performance_vs_human'], p, 100.0,
          0.0, f'{p:.1f}% bin solve rate',
          f"bin solve rate {p:.1f}% against a complete correct patch by a human given the bin's "
          f"own time estimate")

# ---- emit ------------------------------------------------------------------
acted = [e for e in examined if e['action'] != 'none' or e['old_label'] != e['new_label']]
w = csv.DictWriter(open(out, 'w', newline=''),
                   fieldnames=['point_id', 'old_label', 'new_label', 'action', 'reason'],
                   extrasaction='ignore')
w.writeheader(); w.writerows(acted)
if len(sys.argv) > 3:
    json.dump(examined, open(sys.argv[3], 'w'), indent=1)

print('examined', len(examined), '| in override file', len(acted))
print('actions:', dict(collections.Counter(e['action'] for e in acted)))
print('by batch:')
for b in dict.fromkeys(e['batch'] for e in examined):
    rs = [e for e in examined if e['batch'] == b]
    c = collections.Counter(e['action'] for e in rs)
    print(f"  {b:34s} examined {len(rs):3d}  excluded {c['exclude']:3d}  kept {c['none']:3d}")
print('flagged "about half" (0.45-0.50):',
      [e['point_id'] for e in examined if e['flag'] == 'about half'])
