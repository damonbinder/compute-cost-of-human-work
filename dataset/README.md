# AI compute vs human time — dataset

For a given task, how much compute does an AI system spend on it, and how much
active time does a human spend on the same task? Each row pairs the two and says
how the AI's performance compared with the human's.

This is the frozen snapshot of 2026-09-17, tagged `v1-2026-09-17`. Later
commits on `main` may revise it; cite the tag for the version described here.

## The files

| File | What it holds |
|---|---|
| `points.csv` | 1,684 rows, 42 columns. One row is one task × one AI system; 484 tasks, of which 395 have a frontier row. |
| `models.csv` | 329 rows, 20 columns. The model registry: release date, parameters, FLOPs per token, attention shape. |
| `COLUMNS.md` | The field definitions and allowed values for both files. |
| `research/` | 563 derivation notes, one per study, plus the calculation scripts and the hand-made inputs they read. What those scripts wrote is not shipped here; the notes link to it in `agent-work/derived/`. |

## How to read a row

Three numbers and a label carry the comparison:

- `compute_flops` — the AI's compute for the unit of work described in
  `task_description`, in FLOPs.
- `human_time` — a human's active time on the same unit of work, in seconds.
- `performance_vs_human` — `below`, `match` or `above`. There is no `unknown`
  and no `far_below`: a row whose evidence does not support a comparison, or
  where the AI does not do the job, is withheld rather than labelled.
- `compute_scope` and `human_time_scope` say what is inside each figure, and
  `compute_evidence` and `human_time_evidence` say how good the evidence for it
  is. Read both before comparing rows.

`model_id` joins to `models.csv`. Rows are not independent: one task often appears
under several models, and rows sharing a `source_dataset` usually share their
human timings and their model assumptions.

## One row per task

Because a task appears once per model, and sometimes once per configuration of a
model, a count over the rows counts models rather than tasks. Two columns give
the task-level view:

- `task_id` — the task itself. Rows sharing it cover the same unit of work,
  including rows that differ only in the model's scaffold or effort level.
- `frontier` — `yes` on the one row per task that reaches the human baseline
  most cheaply: the cheapest `match` row, or the cheapest `above` row where the
  task has no `match` row. It is `no` on the rows that row beat, and `no` on
  every row of a task where nothing has reached the baseline yet.

Filtering to `frontier == yes` is the recommended view for a question about
tasks: 395 rows, one per task, each the cheapest compute at which that task has
been done to human standard. No row is left blank. A task whose rows disagree on
`human_time` is left untagged until the disagreement is settled, and the
twenty-two tasks that were in that position are recorded in
`research/frontier/frontier.md`. The tag is derived from the data by
`research/frontier/frontier.py`, so it stays correct as rows are added.

## Provenance

Every value is derivable. The citation columns — `human_time_source`,
`compute_source`, `source_record`, `parameter_source`, `model_release_source` —
carry public URLs and paths into `research/`, and every one of those paths
resolves to a file in this folder. The retained copies of the sources themselves
are not shipped here; the notes describe where each came from.
