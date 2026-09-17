# Human-time provenance relabel

*Created 2026-09-13 17:35.*

## TL;DR

Every former `assumed` and `transferred_timings` row in this folder now carries one of the three
new `human_time_evidence` values. In root, 193 rows changed: 97 `source_estimate`, 69
`llm_estimate_judgment`, and 27 `llm_estimate_from_data`. The same 193 point IDs were updated in
the twelve first-tranche candidate copies so a resync will not revert them. For the Codex dataset,
831 rows are classified in `codex-relabel.csv` for application at merge: 29 `source_estimate`, 721
`llm_estimate_judgment`, and 81 `llm_estimate_from_data`. Both root files validate with zero
errors. **Two counts in the ruling are low**: this folder holds 166 `assumed` rows, not 140 (the
26 Balrog rows are the difference), and the Codex dataset holds 750, not 743.

The single largest call is the SWE-bench Verified split. OpenAI's annotators set the three closed
difficulty bins, so those rows are `source_estimate`; the open `>4 hours` bin has only a
source-set lower bound and takes a 6-hour value chosen here, so those rows are
`llm_estimate_judgment`. That splits one source's 124 rows 93/31.

## What changed, by file

| File | Rows changed | source_estimate | llm_estimate_judgment | llm_estimate_from_data |
|---|---|---|---|---|
| points.csv | 138 | 73 | 44 | 21 |
| excluded.csv | 55 | 24 | 25 | 6 |
| Root total | 193 | 97 | 69 | 27 |
| Codex points.csv (merge file) | 831 | 29 | 721 | 81 |

Candidate copies updated, same 193 point IDs: apex-agents 9, balrog 26, epoch-swebench-bins 124,
flt-anthropic 1, game-arena 9, hourvideo 2, lait 1, lumen 5, meta-textbook 1, mirrorcode 13,
navier-stokes-openai 1, srt-h 1. The eight directories belonging to constructors working now were
not touched; of those, ale-bench and bankertoolbench had no row in scope anyway, and the other six
have no `points.csv` yet.

Per-row detail is in `relabel.csv` (point_id, file, old_value, new_value, basis) and
`codex-relabel.csv` (point_id, old_value, new_value, basis).

## The rule applied to each root block

Former `transferred_timings` rows take `llm_estimate_from_data` mechanically, per the ruling. For
former `assumed` rows the question is which party made the judgment step that set the number.

| Block | Rows | New value | Why |
|---|---|---|---|
| epoch-swebench-bins, closed bins | 93 | source_estimate | The annotators OpenAI recruited chose each issue's difficulty bin. The row value is the arithmetic midpoint of a source-defined closed interval, which is arithmetic on the source's estimate, not a second judgment. |
| epoch-swebench-bins, `>4 hours` bin | 31 | llm_estimate_judgment | The source sets only an open lower bound. The 6-hour value comes from inspecting the three instances here, and the note calls it the block's only real judgment call. |
| balrog | 26 | llm_estimate_judgment | The Crafter human release publishes step counts and no durations. Seconds come from a 5 fps rate inferred here from `run_gui.py`'s default, so the conversion that produced a duration was made here. |
| mirrorcode, gotree | 4 | source_estimate | Epoch published four MirrorCode contributors' estimates (blog footnote 20, paper section 4). The value is their mean on the folder's 40-hour week. |
| mirrorcode, cal/choose/pkl | 9 | llm_estimate_judgment | The source publishes no estimate for these targets. The value is gotree's implied rate, 19.5 active hours per 1,000 reference lines, transferred here by line count. |
| meta-textbook | 1 | llm_estimate_judgment | The paper publishes no duration, headcount, or hours. The value is a construction here from 90,000 human-equivalent Lean lines at 15,000 lines per person-year. |
| navier-stokes-openai | 1 | llm_estimate_judgment | The note states no published expert estimate of the duration exists, and builds the number from discovery, write-up, and formalization components. |
| flt-anthropic | 1 | llm_estimate_judgment | The note says explicitly that the figure is reasoning rather than a citation. |

## The rule applied to each Codex block

| Block | Rows | New value | Why |
|---|---|---|---|
| gdpval, all tranches | 440 | llm_estimate_judgment | GDPval publishes no task durations, and the tranche notes state no inherited estimates were used. Each value is a minute-by-minute decomposition of the inspected prompt made by the builder. |
| epoch/mathl5 | 83 | llm_estimate_judgment | An explicitly assumed 600-second effort budget for an IMO-gold-level solver. The note rejects the MATH paper's timed session as a bad transfer. |
| epoch/otis | 68 | llm_estimate_judgment | The source defines a 3-hour exam allowance but publishes no completion-time estimate. The 720-second value rests on the assumption that a participant works the full allowance. |
| epoch/swebench, parent rows | 25 | source_estimate | The bin-weighted mean over the same OpenAI annotator estimates. The three closed bins supply 94.1% of the 2,267.67-second value. |
| epoch/simpleqa | 13 | llm_estimate_judgment | Three minutes from inspecting the first 20 questions, explicitly not a measured annotation average. |
| Tail, 65 notes | 117 | llm_estimate_judgment | Each note states the duration is its own estimate with no measured timing donor and no source-published duration. |
| Tail: book-coherence | 2 | source_estimate | The study reports roughly 30 minutes per summary for its own proofreaders. The 1,800-second value is that figure unchanged. |
| Tail: news-summarization | 1 | source_estimate | Zhang et al. report the authors' pilot estimate of 12 to 15 minutes per summary. The 810-second value is that range's midpoint. |
| Tail: anymal | 1 | source_estimate | The route planner the paper cites publishes 76 minutes for human hikers on that route, converted to seconds. |
| Former transferred_timings | 81 | llm_estimate_from_data | Mechanical rename. |

## Judgment calls

These are the places where a reader could reasonably rule the other way. Nothing here is a defect
in the rows; each is a boundary the ruling does not settle on its own.

- **The SWE-bench split itself, 124 root rows and 25 Codex rows.** One source produces both
  values. A reader who holds that a midpoint over any interval is the builder's step would make
  all 149 `llm_estimate_judgment`; a reader who holds that the annotator's bin is the estimate in
  every case would make all 149 `source_estimate`. The split follows the hybrid rule literally:
  for the closed bins the source's estimate fixes the interval and only arithmetic remains, and
  for the open bin it does not.
- **The Codex SWE-bench parent rows, 25.** These take the bin-weighted mean, so the builder's
  6-hour top-bin value is inside the number. It contributes 64,800 of 1,097,550 seconds, 5.9%.
  Called `source_estimate` because the annotators' estimates set the rest and define every bin.
- **Balrog, 26 rows.** The step count is a real 100-episode measurement and only the rate is
  inferred, so the number is not judgment alone. It is `llm_estimate_judgment` because the source
  published no duration and the seconds were produced here. If a later pass prefers a
  measurement-backed value for this shape, this is the block to revisit.
- **MirrorCode's transferred targets, 9 rows.** The donor is the source's own published estimate,
  but the transfer to a different program by line count was made here. The parallel Codex rows
  with a measured donor sit in `llm_estimate_from_data`; these do not, because their donor is an
  estimate.
- **MirrorCode gotree, 4 rows.** The contributors estimated in weeks; the 40-hour week that turns
  weeks into 1,188,000 seconds is the folder's convention, not theirs.
- **Codex OTIS, 68 rows, and Minerva, 2 rows.** Both convert a source-defined exam window into a
  per-question active time by assuming the participant uses it fully. Under COLUMNS.md's current
  wording, `defined_duration` names "a four-hour contest window" as its own example, so these two
  blocks may belong there rather than in either estimate value. They stay in scope here because
  they were `assumed`, and the full-use assumption was made by the builder.
- **Codex anymal, 1 row.** The 76 minutes come from a route planner, a third party the paper
  cites, not from the paper's authors. Called `source_estimate` on the reading that the estimate
  was published by someone other than the builder and adopted unchanged.
- **Codex cost-of-pass, 10 rows.** A source estimate does exist here: the BBQ authors' up-to-two-
  minutes-per-task allowance, about 24 seconds per example. The rows do not use it. The note sets
  20 seconds from a reading-rate argument and says so, which makes the operative number the
  builder's.
- **Codex negotiation, 2 rows, and games-training, 1 row.** Both draw on measured rates from other
  studies, a typing-speed paper and a typical-game-length study. They were `assumed`, so under the
  ruling's mechanical mapping they become `llm_estimate_judgment` rather than
  `llm_estimate_from_data`.

## Count discrepancies against the ruling

The ruling's entry says 140 rows in this folder and 743 in the Codex dataset. The files hold 166
and 750. The 26-row difference in this folder is exactly the Balrog block: 124 + 13 + 3 = 140 is
every other `assumed` row, so the Balrog rows appear to have been missed when the ruling's count
was taken. All 166 were classified, since the instruction is to classify every `assumed` row. The
7-row difference on the Codex side is not attributable to a single block; the file was last
written 2026-09-13 03:20 and all 750 are classified.

## Validation

Both root files validate with zero errors against
`../AI Compute vs Human Time/collection-work/tools/validate.py`, staged in the scratchpad with
COLUMNS.md, a models.csv of this folder's 19 rows plus the Codex registry rows for the shared
model IDs used (parameter_source replaced by a placeholder), and symlinks to `research/` and
`agent-work/sources/`.

| Stage | Rows | Model rows | Errors | Review reminders |
|---|---|---|---|---|
| points.csv | 201 | 57 | 0 | 199 |
| excluded.csv, exclusion_reason dropped | 95 | 54 | 0 | 63 |

The validator rule requiring donor sample fields on `transferred_timings` no longer fires, since
no row carries that value. No relabelled row pairs `human_time_method` `reported` or
`unit_conversion` with a non-`task_timings` evidence value, so that rule does not newly fire
either. `human_time_method` was left untouched throughout, as were all other columns: a
field-by-field diff against a pre-change copy of every file confirms `human_time_evidence` is the
only column that differs, with row sets and column order unchanged and CRLF line endings
preserved.
