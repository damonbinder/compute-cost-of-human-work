"""Apply the close-calls ruling to already-excluded rows.

Usage: python3 close_calls.py <folder-root> [--apply]

DECISIONS.md, "Close calls at the exclusion line" (coordinator, 2026-09-13): a row whose
above-chance ratio to the human is within one standard error of the 0.5 guide is kept as
`below`; a row more than one standard error under it is excluded.

  restore when (0.50 - ratio) <= SE(ratio)

Standard errors use each row's own sampling unit:
  SWE-bench bin   binomial on the bin's resolved count k of n completed evaluations; the
                  human side is a complete correct patch, exact, so SE(ratio) = SE(p).
  Crafter         both sides carry a reported standard error over episodes, so
                  SE(ratio) = sqrt(se_A^2 + ratio^2 * se_H^2) / (H - floor).
  MirrorCode      where a row has repeat episodes the episode is the sampling unit and the
                  SE is the SEM over them: test cases within one episode are decided by a
                  single submitted program, so a binomial over cases would understate it by
                  an order of magnitude. Single-episode rows fall back to the binomial over
                  cases, which is reported as a floor on the true SE.
  RLI, HourVideo  binomial on the scored items, human side included where it is sampled.

APEX-Agents and GAIA are out of scope: both were decided by their own passes.
"""
import csv, re, sys, math, pathlib

root = pathlib.Path(sys.argv[1]); apply_it = '--apply' in sys.argv
GUIDE = 0.50
SKIP_PREFIX = ('work-apex-agents-', 'perc-gaia-', 'agen-gaia-', 'gaia-')

def binom_se(k, n):
    p = k / n
    return p, math.sqrt(p * (1 - p) / n)

def sem(vals):
    m = sum(vals) / len(vals)
    var = sum((v - m) ** 2 for v in vals) / (len(vals) - 1)
    return m, math.sqrt(var / len(vals))

rows = []
for r in csv.DictReader(open(root / 'excluded.csv')):
    pid, ev = r['point_id'], r['performance_evidence']
    if pid.startswith(SKIP_PREFIX):
        continue
    ratio = se = None; unit = ''

    if 'swebench' in pid:
        m = re.search(r'on (\d+)/(\d+) completed evaluations', ev)
        k, n = int(m.group(1)), int(m.group(2))
        ratio, se = binom_se(k, n)
        unit = f'{k}/{n} binomial'

    elif 'balrog-crafter' in pid:
        a, sa = (float(x) for x in re.search(r'progression ([\d.]+)% \+/- ([\d.]+)', ev).groups())
        h, sh = (float(x) for x in re.search(r'episodes is ([\d.]+)% \+/- ([\d.]+)', ev).groups())
        f = 10.4
        ratio = (a - f) / (h - f)
        se = math.sqrt(sa ** 2 + (ratio * sh) ** 2) / (h - f)
        unit = f'{a}%+/-{sa} vs {h}%+/-{sh}'

    elif 'mirrorcode-gotree' in pid:
        eps = {'agen-mirrorcode-gotree-py-opus4': (1.2, 15.3, 9.8),
               'agen-mirrorcode-gotree-py-opus41': (15.8, 23.5, 7.6),
               'agen-mirrorcode-gotree-py-opus45': (47.3, 3.7, 63.2)}[pid]
        m, s = sem(eps)
        ratio, se = m / 100, s / 100
        unit = f'SEM over 3 episodes {eps}'

    elif 'mirrorcode-pkl' in pid:
        m = re.search(r'passed ([\d,]+) of (\d+) cases', ev)
        if not m:
            rows.append((pid, None, None, 'transferred label, no own score', 'keep excluded'))
            continue
        k, n = int(m.group(1).replace(',', '')), int(m.group(2))
        ratio, se = binom_se(k, n)
        unit = f'{k}/{n} binomial, single episode, SE is a floor'

    elif pid.startswith('work-rli-'):
        m = re.search(r'(\d+) of 240', ev)
        ratio, se = binom_se(int(m.group(1)), 240)
        unit = f'{m.group(1)}/240 binomial'

    elif pid.startswith('perc-hourvideo-'):
        a = float(re.search(r'scored ([\d.]+)% on the 570-MCQ', ev).group(1)) / 100
        sa = math.sqrt(a * (1 - a) / 570)
        h, sh = 0.85, math.sqrt(0.85 * 0.15 / 213)
        f = 0.20
        ratio = (a - f) / (h - f)
        se = math.sqrt(sa ** 2 + (ratio * sh) ** 2) / (h - f)
        unit = '570 MCQ binomial vs 213 MCQ expert sample'

    elif pid.startswith('game-vgb-'):
        rows.append((pid, None, None, 'single funded run, no sampling unit', 'keep excluded'))
        continue

    gap = GUIDE - ratio
    rows.append((pid, ratio, se, unit, 'RESTORE' if gap <= se else 'keep excluded'))

restore = [r for r in rows if r[4] == 'RESTORE']
print(f'{len(rows)} excluded rows in scope | {len(restore)} within one SE of 0.50\n')
for pid, ratio, se, unit, verdict in sorted(
        (r for r in rows if r[1] is not None), key=lambda r: -r[1]):
    mark = '<<<' if verdict == 'RESTORE' else '   '
    print(f'{mark} {pid:44s} ratio {ratio:.4f}  SE {se:.4f}  gap {GUIDE-ratio:+.4f}  [{unit}]')
for pid, ratio, se, unit, verdict in rows:
    if ratio is None:
        print(f'    {pid:44s} not computable: {unit}')

if apply_it:
    f = root / 'research' / 'performance-relabel.csv'
    ovr = list(csv.DictReader(open(f)))
    ids = {r[0] for r in restore}
    n = 0
    for r in ovr:
        if r['point_id'] in ids and r['action'] == 'exclude':
            ratio, se = next((x[1], x[2]) for x in restore if x[0] == r['point_id'])
            r['action'] = 'relabel'; r['new_label'] = 'below'
            r['reason'] = (f'Coordinator ruling 2026-09-13, close call at the exclusion line: '
                           f'ratio {ratio:.3f} is within one standard error ({se:.3f}) of the 0.5 '
                           f'guide. ' + r['reason'])
            n += 1
    w = csv.DictWriter(open(f, 'w', newline=''),
                       fieldnames=['point_id', 'old_label', 'new_label', 'action', 'reason'])
    w.writeheader(); w.writerows(ovr)
    print(f'\nflipped {n} override rows to relabel/below')
