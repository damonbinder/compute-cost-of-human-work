# The frontier row of a task

*Created 2026-09-16 06:56.*

`points.csv` carries one row per task × AI system, so most tasks appear several
times over and a count of rows counts models. `task_id` says which rows are the
same task, and `frontier` marks the one row per task that reaches the human
baseline most cheaply. Filtering to `frontier == yes` gives the one-row-per-task
view: 395 rows out of 1,684, over 484 tasks.

The rule, ruled by Damon on 2026-09-16:

- The frontier row is the cheapest `match` row of the task. Match is the target
  and not a ceiling, so a cheaper `below` row does not win the tag, and neither
  does an `above` row when the task has a `match` row.
- A task with no `match` row takes its cheapest `above` row.
- A task all of whose rows sit `below` has no frontier row at all. Every row is
  tagged `no`.
- A task whose rows disagree on `human_time` is not eligible. Every row is left
  blank pending a separate ruling. No task is in that position now; the
  twenty-two that were are settled, and the section below records them.

The script is `research/frontier/frontier.py`. Its run summary and per-task
record, including the winner and the row count of every task, is
`agent-work/derived/frontier/run.json`.

## Where the tag lands

| Quantity | Count |
|---|---|
| Rows | 1683 |
| Tasks | 483 |
| Rows tagged `yes` | 394 |
| Rows tagged `no` | 1289 |
| Rows left blank | 0 |
| Tasks with a frontier row | 394 |
| Tasks whose frontier is a `match` row | 331 |
| Tasks whose frontier is an `above` row | 63 |
| Tasks with no frontier row, every row `below` | 89 |
| Tasks left out, `human_time` varies | 0 |

The 89 tasks with no frontier row are the ones no model has yet done to human
standard, and they belong in a count of tasks as much as the 394 do. Reading
`frontier == no` as "beaten" is therefore wrong on those rows; the status per
task is in `run.json`.

## How a task is keyed

`task_id` is asserted in the CSV rather than computed from the task name,
because the name is not a reliable key in either direction. Some rows name the
model or its configuration in `task` — "Learn to read written Basque (Latxa
70B)", "Create a low-poly cabin scene (gpt-5.6-sol ultra)" — which would split
one task into as many tasks as there are configurations, against Damon's ruling
that different scaffolds, effort levels and other configurations compete for the
one tag. Stripping a trailing parenthetical instead would merge the four
`Resolve a SWE-bench Verified issue` rows, which are four human-fix-time bins of
the benchmark and four different units of work. Neither transformation is
mechanical, so the grouping is in the data where it can be read and reviewed.

The seeded values are the slugified task name, with four families merged where
the parenthetical named a model or a configuration of one:

| Task | Rows | Merged variants |
|---|---|---|
| Annotate coherence errors in a book summary | 2 | 2 |
| Check concatenated parentheses | 2 | 2 |
| Solve an ARC-AGI-2 test grid | 6 | 6 |
| Solve one unseen ARC-AGI-3 environment on first exposure | 9 | 9 |

The ARC-AGI-3 grid of nine harness × reasoning-level configurations resolves to
one row, `game-arcagi3-astra-pa-max`, and the parentheses-checking pair to
`code-function-parentheses-qwen25coder7b`. The summary-annotation pair,
hierarchical against incremental, sits `below` on both rows and so has no
frontier row. The ARC-AGI-2 family took one human duration on 2026-09-16 and
gained two more rows the same day, `reas-arcagi-v2-gemini3dt` and
`reas-arcagi-v2-grok420`, which had been sitting under their own `task_id`
values from an earlier pass over the same benchmark and the same case-mix
construction; four of its six rows therefore come from the name merge and two
from that later ruling. Its frontier over the six is
`reas-arcagi-v2-gpt52-xhigh`, the cheapest `match` row at 4.16e16 FLOPs against
the Grok row's 5.71e16.

## A human time the AI's own level defines is its own task

Six families were merged in the first pass and then unmerged on 2026-09-16, on
Damon's ruling: the five skill-acquisition families and the cabin scene. A
seventh case, the two personal-website rows, was split the same day under the
same rule. Their rows do not share a job. Each training run reached a different level, and each
row's human time is the time to learn to *that* level, so a human learning to
the proficiency of Latxa 13B is not doing the work a human learning to Latxa
70B's proficiency does. The cabin-scene rows work the same way, one step
removed: each row's human time estimates reproducing that configuration's own
output at comparable quality, which is why all ten sit at `match` by
construction and why they spread over seven durations.

**The rule this establishes.** Where a row's `human_time` is defined by the
level the AI itself reached, the row is its own task and is never merged with
another configuration's row. A configuration that competes for one tag has to
be competing against one human duration; these rows are not. The twenty-seven
rows below are therefore twenty-seven single-row tasks, each its own frontier
row:

| Family | Rows, now tasks |
|---|---|
| Acquire English grammatical discrimination | 4 |
| Build and hand off a personal website | 2 |
| Create a low-poly cabin scene | 10 |
| Improve Portuguese academic and cultural task performance | 2 |
| Learn to read written Basque | 2 |
| Learn to write short OCaml functions | 2 |
| Learn to write short Python functions | 5 |

All twenty-seven sit at `match`, so each is tagged `yes`. The two website rows
are the cabin situation without the parenthetical: each row's human time is an
expert's time to reproduce what that model itself delivered, a 221-line page
against a 433-line one, so 8,400 and 10,800 seconds are two jobs and not two
estimates of one. Their `task_id` values take the model from `model_id`, which
is where the configuration lives when the task name does not carry it:
`build-and-hand-off-a-personal-website-opus-4-1` and
`build-and-hand-off-a-personal-website-sonnet-4-5`.

The validator's name-stem reminder now fires on all seven families, which is
the correct behaviour and not a finding: the reminder asks whether rows sharing
a task name up to a trailing parenthetical are one task split by configuration,
and the answer here is no, recorded by this section. Those seven and the
SWE-bench Verified duration bins are the eight standing reminders.

The validator reports any further pair of `task_id` values whose task names
agree up to a trailing parenthetical as a review reminder, so a new row that
names its configuration in `task` surfaces rather than silently becoming its own
task. The eight standing reminders are listed in the section above.

## Tasks left out because human_time varies

No task is left out. A task whose rows pair the same named work against
different human durations gives a frontier row nothing to be cheapest against,
so every row is left blank, neither tagged nor beaten. Twenty-two tasks were in
that position and all twenty-two were settled on 2026-09-16.

Seven were unmerged under the rule above. Fifteen were given one human time per
task, and the
reasoning for each is in its own research note: the eleven HCAST tasks adopt
METR's Time Horizon 1.1 human rating on every row, including the rows whose AI
runs came from the 1.0 export, because the two ratings are a retiming of one
baseline; `classify-an-imagenet-image` takes Shankar et al.'s measured 26-second
median over Karpathy's approximate one-image-per-minute pace;
`choose-a-chess-move-from-a-text-board` takes the rating-pooled 7.1-second move
time rather than the bin matching each model's Estimated Human Elo;
`negotiate-a-three-item-allocation` takes 74.22 seconds, the recipe at the mean
of the two published dialogue lengths; and `solve-an-arc-agi-2-test-grid` takes
255.21 seconds over every human-viewed case rather than each run's
response-complete subset, on all six of its rows. The record of that pass is
`agent-work/reviews/human-time-unification-2026-09-16.md`.

The table the earlier version of this section carried, listing all 22, is
superseded by that review.

| Task | Rows | Distinct human_time values | human_time low (s) | human_time high (s) |
|---|---|---|---|---|
| `acquire-english-grammatical-discrimination` | 4 | 4 | 9000000 | 25560000 |
| `answer-a-question-from-latex-sources-hcast` | 8 | 2 | 959.16 | 1420.68 |
| `answer-a-question-from-local-papers-hcast` | 9 | 2 | 107.04 | 383.58 |
| `build-and-hand-off-a-personal-website` | 2 | 2 | 8400 | 10800 |
| `check-a-model-comparison-claim-in-a-paper-hcast` | 7 | 2 | 726.66 | 1456.8 |
| `choose-a-chess-move-from-a-text-board` | 9 | 3 | 6.9 | 7.6 |
| `classify-an-imagenet-image` | 4 | 2 | 26 | 60 |
| `compute-days-since-a-fixed-date-hcast` | 11 | 2 | 119.7 | 119.76 |
| `create-a-low-poly-cabin-scene` | 10 | 7 | 5400 | 21600 |
| `exploit-a-command-injection-hcast` | 9 | 2 | 561.66 | 1965.3 |
| `find-the-biggest-order-in-a-dataset-hcast` | 11 | 2 | 644.1 | 746.1 |
| `fix-all-bugs-in-a-small-orm-library-hcast` | 10 | 2 | 5713.08 | 5727.12 |
| `fix-an-oxdna-simulation-config-hcast` | 9 | 2 | 520.68 | 674.04 |
| `fix-some-bugs-in-a-small-orm-library-hcast` | 10 | 2 | 4992.9 | 5066.22 |
| `improve-portuguese-academic-and-cultural-task-performance` | 2 | 2 | 360000 | 720000 |
| `learn-to-read-written-basque` | 2 | 2 | 2016000 | 4320000 |
| `learn-to-write-short-ocaml-functions` | 2 | 2 | 39600 | 108000 |
| `learn-to-write-short-python-functions` | 5 | 5 | 349200 | 1944000 |
| `negotiate-a-three-item-allocation` | 2 | 2 | 66.36 | 82.08 |
| `reverse-a-hash-by-brute-force-hcast` | 8 | 2 | 143.34 | 231 |
| `solve-a-picoctf-challenge-hcast` | 11 | 2 | 365.22 | 391.68 |
| `solve-an-arc-agi-2-test-grid` | 4 | 4 | 240.2 | 255.21 |

The human_time figures above are as they stood on 2026-09-16. One has since
moved: `lang-xfer-eu-latxa13b` went from 2,016,000 to 2,088,000 seconds on
2026-09-17 when the Cambridge A1 and A2 midpoints behind Table L of
[the skill-acquisition note](../skill-acquisition-human-time.md) were corrected.

## Keeping the tag current

`frontier` is derived, never edited. After rows are added or a
`performance_vs_human`, `compute_flops` or `human_time` value changes:

```
python3 dataset/research/frontier/frontier.py --seed-task-ids   # fills blank task_id from the task name
python3 dataset/research/frontier/frontier.py --write           # rewrites the frontier column
python3 agent-work/tools/validate.py
```

A new row on a task already in the file must take that task's existing
`task_id`; the seeding step only fills blanks, and a slug minted from a name
carrying a configuration would make a new task out of an old one. The validator
recomputes the tag on every run and errors on any row whose recorded value
differs, so a stale tag cannot be committed, and it imports the rule from this
folder rather than restating it.
