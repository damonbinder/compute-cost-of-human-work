# Performance labelling pass — the amended scale and the excluded rows

*Created 2026-09-13 13:14.*
*Last revised 2026-09-13 14:06, applying the close-calls ruling.*

*Label note, 2026-09-15: `far_above` was merged into `above` across the dataset (Damon's ruling that day), so rows this note calls `far_above` carry `above` in `points.csv`. The reasoning below is unchanged.*

## TL;DR

Applied Damon's amended `performance_vs_human` scale to all 106 accepted rows and pre-decided the
two candidates awaiting acceptance. **No row changed label. 62 of the 106 accepted rows were
excluded** into `excluded.csv`, leaving 44 (31 `match`, 12 `below`, 1 `above`), and **70 of the
133 candidate rows are pre-marked for exclusion on acceptance**. The whole of VideoGameBench (35),
the Remote Labor Index (5), HourVideo (2), 14 of 26 BALROG Crafter rows and 6 of 13 MirrorCode rows
go. MirrorCode is the one batch Damon's ruling did not name in advance. The single `above` row
(MonoRace) was checked for `far_above` and keeps `above`: a 15% edge on lap time is not a step no
human matched. Overrides are in `research/performance-relabel.csv`; `tools/resync.py` re-applies
them idempotently after any candidate re-sync.

**Decide first:** the nine APEX-Agents rows. All nine fall below the ratio line, so the whole
candidate batch is marked for exclusion, but its top row sits at 0.471 — "about half" — and its
metric is an all-or-nothing rubric where a failure means missing one criterion of about four, not
producing nothing. If the completion arm of the test reaches these rows, the top four come back.

## The rule as applied

`DECISIONS.md`, "Below means somewhat below; substantially below is removed" (Damon, 2026-09-13),
supersedes the `far_below` half of the granularity ruling. The scale is
`below / match / above / far_above / unknown`. There is no `far_below`.

A row keeps `below` when the AI basically does the job, somewhat worse than the human. Two routes
qualify, and a row needs only one:

1. **Completion at lower quality.** The benchmark has a completion criterion, the AI met it, and
   the shortfall is in quality or speed. This is the route for LAIT and the three `below` LUMEN
   rows.
2. **Ratio.** On the benchmark's own metric, with the chance floor subtracted from both sides,

   > ratio = (AI − floor) / (human − floor) ≥ 0.50

Anything else is substantially below and leaves `points.csv` for `excluded.csv`, which is the same
30 columns plus `exclusion_reason`. The research note and retained sources for an excluded row stay
where they are, and `tools/resync.py` restores any row whose override action is flipped back to
`relabel`.

Three points of interpretation, since each one moved rows:

- **The completion route does not reach accuracy-scored benchmarks.** Every model "completes" a
  multiple-choice set, so reading route 1 broadly would make route 2 a dead letter. Damon's ruling
  names HourVideo among the rows expected to leave, which fixes the narrow reading: route 1 needs a
  completion criterion the benchmark itself defines and the AI met.
- **Chance floors are the ones already established in this folder.** Crafter's uniform-random floor
  is 10.4% per `DECISIONS.md`; HourVideo's guessing floor is 20%. Where the human target is a
  completed deliverable — a finished game, a paid freelance project, a complete correct patch, a
  full test-suite pass — the floor is 0, because a random policy never produces one.
- **The statistic is the row's own.** Where a row's compute statistic is a mean over episodes, the
  performance ratio is the mean over the same episodes, so the two sides of the row describe one
  set of runs. This is what decides `agen-mirrorcode-gotree-py-opus45`, whose best episode passed
  63.2% but whose three-episode mean is 38.1%.

No numbers were invented. Every ratio is computed from the figures already in the row's
`performance_evidence` by `research/performance-relabel/relabel.py`, which writes both the override
CSV and `agent-work/derived/performance-relabel/examined.json`.

## Summary

| Batch | Examined | Excluded | Kept below | Kept match/above |
|---|---|---|---|---|
| VideoGameBench | 35 | 35 | 0 | 0 |
| BALROG Crafter | 22 | 14 | 8 | 0 |
| MirrorCode | 6 | 6 | 0 | 0 |
| Remote Labor Index | 5 | 5 | 0 | 0 |
| HourVideo | 2 | 2 | 0 | 0 |
| Epoch SWE-bench bins (candidate) | 124 | 61 | 63 | 0 |
| APEX-Agents (candidate) | 9 | 9 | 0 | 0 |
| All other studies | 36 | 0 | 4 | 32 |
| **Total** | **239** | **132** | **75** | **32** |

## Rows excluded

62 accepted rows and 70 candidate rows, each with the score on the benchmark's own metric and the
ratio to the human baseline above the chance floor.

### VideoGameBench — all 35

Damon's own example. The criterion is completing the game; the best run of the 35 reached 5.07% of
the walkthrough and the median reached 0.52%. No run cleared a checkpoint on 28 of the 35. The
entire study leaves `points.csv`.

| point_id | Score | Ratio | Reason |
|---|---|---|---|
| `game-vgb-kirby-sonnet37` | 5.07% of walkthrough | 0.051 | criterion is completing the game and the run reached 5.07% of the walkthrough, 0.05 of the completing human |
| `game-vgb-kirby-gemini25pro` | 5.07% of walkthrough | 0.051 | criterion is completing the game and the run reached 5.07% of the walkthrough, 0.05 of the completing human |
| `game-vgb-kirby-gpt4o` | 2.89% of walkthrough | 0.029 | criterion is completing the game and the run reached 2.89% of the walkthrough, 0.03 of the completing human |
| `game-vgb-kirby-gemini20flash` | 2.89% of walkthrough | 0.029 | criterion is completing the game and the run reached 2.89% of the walkthrough, 0.03 of the completing human |
| `game-vgb-kirby-llama4mav` | 2.45% of walkthrough | 0.025 | criterion is completing the game and the run reached 2.45% of the walkthrough, 0.02 of the completing human |
| `game-vgb-civ1-gpt4o` | 1.99% of walkthrough | 0.020 | criterion is completing the game and the run reached 1.99% of the walkthrough, 0.02 of the completing human |
| `game-vgb-crystal-gpt4o` | 1.04% of walkthrough | 0.010 | criterion is completing the game and the run reached 1.04% of the walkthrough, 0.01 of the completing human |
| `game-vgb-civ1-llama4mav` | 1.02% of walkthrough | 0.010 | criterion is completing the game and the run reached 1.02% of the walkthrough, 0.01 of the completing human |
| `game-vgb-civ1-sonnet37` | 0.91% of walkthrough | 0.009 | criterion is completing the game and the run reached 0.91% of the walkthrough, 0.01 of the completing human |
| `game-vgb-zelda-sonnet37` | 0.85% of walkthrough | 0.009 | criterion is completing the game and the run reached 0.85% of the walkthrough, 0.01 of the completing human |
| `game-vgb-zelda-gemini25pro` | 0.85% of walkthrough | 0.009 | criterion is completing the game and the run reached 0.85% of the walkthrough, 0.01 of the completing human |
| `game-vgb-nfs-gpt4o` | 0.67% of walkthrough | 0.007 | criterion is completing the game and the run reached 0.67% of the walkthrough, 0.01 of the completing human |
| `game-vgb-zelda-gpt4o` | 0.65% of walkthrough | 0.007 | criterion is completing the game and the run reached 0.65% of the walkthrough, 0.01 of the completing human |
| `game-vgb-zelda-llama4mav` | 0.65% of walkthrough | 0.007 | criterion is completing the game and the run reached 0.65% of the walkthrough, 0.01 of the completing human |
| `game-vgb-zelda-gemini20flash` | 0.65% of walkthrough | 0.007 | criterion is completing the game and the run reached 0.65% of the walkthrough, 0.01 of the completing human |
| `game-vgb-nfs-gemini20flash` | 0.52% of walkthrough | 0.005 | criterion is completing the game and the run reached 0.52% of the walkthrough, 0.01 of the completing human |
| `game-vgb-crystal-gemini20flash` | 0.48% of walkthrough | 0.005 | criterion is completing the game and the run reached 0.48% of the walkthrough, 0.00 of the completing human |
| `game-vgb-nfs-gemini25pro` | 0.39% of walkthrough | 0.004 | criterion is completing the game and the run reached 0.39% of the walkthrough, 0.00 of the completing human |
| `game-vgb-crystal-sonnet37` | 0.37% of walkthrough | 0.004 | criterion is completing the game and the run reached 0.37% of the walkthrough, 0.00 of the completing human |
| `game-vgb-crystal-gemini25pro` | 0.37% of walkthrough | 0.004 | criterion is completing the game and the run reached 0.37% of the walkthrough, 0.00 of the completing human |
| `game-vgb-crystal-llama4mav` | 0.37% of walkthrough | 0.004 | criterion is completing the game and the run reached 0.37% of the walkthrough, 0.00 of the completing human |
| `game-vgb-civ1-gemini25pro` | 0.18% of walkthrough | 0.002 | criterion is completing the game and the run reached 0.18% of the walkthrough, 0.00 of the completing human |
| `game-vgb-doom2-gemini25pro` | 0.17% of walkthrough | 0.002 | criterion is completing the game and the run reached 0.17% of the walkthrough, 0.00 of the completing human |
| `game-vgb-doom2-sonnet37` | 0.13% of walkthrough | 0.001 | criterion is completing the game and the run reached 0.13% of the walkthrough, 0.00 of the completing human |
| `game-vgb-doom2-gpt4o` | 0.12% of walkthrough | 0.001 | criterion is completing the game and the run reached 0.12% of the walkthrough, 0.00 of the completing human |
| `game-vgb-doom2-llama4mav` | 0.12% of walkthrough | 0.001 | criterion is completing the game and the run reached 0.12% of the walkthrough, 0.00 of the completing human |
| `game-vgb-doom2-gemini20flash` | 0.12% of walkthrough | 0.001 | criterion is completing the game and the run reached 0.12% of the walkthrough, 0.00 of the completing human |
| `game-vgb-tim-sonnet37` | 0.10% of walkthrough | 0.001 | criterion is completing the game and the run reached 0.10% of the walkthrough, 0.00 of the completing human |
| `game-vgb-nfs-sonnet37` | 0.07% of walkthrough | 0.001 | criterion is completing the game and the run reached 0.07% of the walkthrough, 0.00 of the completing human |
| `game-vgb-nfs-llama4mav` | 0.07% of walkthrough | 0.001 | criterion is completing the game and the run reached 0.07% of the walkthrough, 0.00 of the completing human |
| `game-vgb-civ1-gemini20flash` | 0.00% of walkthrough | 0.000 | criterion is completing the game and the run reached 0.00% of the walkthrough, 0.00 of the completing human |
| `game-vgb-tim-gpt4o` | 0.00% of walkthrough | 0.000 | criterion is completing the game and the run reached 0.00% of the walkthrough, 0.00 of the completing human |
| `game-vgb-tim-gemini25pro` | 0.00% of walkthrough | 0.000 | criterion is completing the game and the run reached 0.00% of the walkthrough, 0.00 of the completing human |
| `game-vgb-tim-llama4mav` | 0.00% of walkthrough | 0.000 | criterion is completing the game and the run reached 0.00% of the walkthrough, 0.00 of the completing human |
| `game-vgb-tim-gemini20flash` | 0.00% of walkthrough | 0.000 | criterion is completing the game and the run reached 0.00% of the walkthrough, 0.00 of the completing human |

### BALROG Crafter — 14 of 26

Against the human expert's 63.18% progression with the 10.4% uniform-random floor removed, so the
line falls at 36.79% progression. The 12 survivors are the 8 `below` rows from 37.27% up and the
4 `match` rows.

| point_id | Score | Ratio | Reason |
|---|---|---|---|
| `game-balrog-crafter-deepseekr1` | 36.36% progression | 0.492 | Crafter progression 36.36% against the human expert 63.18%, 0.49 of the human above the 10.4% random floor |
| `game-balrog-crafter-rekaflash3` | 33.64% progression | 0.440 | Crafter progression 33.64% against the human expert 63.18%, 0.44 of the human above the 10.4% random floor |
| `game-balrog-crafter-claude35sonnet` | 32.73% progression | 0.423 | Crafter progression 32.73% against the human expert 63.18%, 0.42 of the human above the 10.4% random floor |
| `game-balrog-crafter-llama33-70b` | 28.64% progression | 0.346 | Crafter progression 28.64% against the human expert 63.18%, 0.35 of the human above the 10.4% random floor |
| `game-balrog-crafter-mistralnemo` | 27.73% progression | 0.328 | Crafter progression 27.73% against the human expert 63.18%, 0.33 of the human above the 10.4% random floor |
| `game-balrog-crafter-claude35haiku` | 26.36% progression | 0.302 | Crafter progression 26.36% against the human expert 63.18%, 0.30 of the human above the 10.4% random floor |
| `game-balrog-crafter-llama31-8b` | 25.45% progression | 0.285 | Crafter progression 25.45% against the human expert 63.18%, 0.29 of the human above the 10.4% random floor |
| `game-balrog-crafter-grok3` | 25.00% progression | 0.277 | Crafter progression 25.00% against the human expert 63.18%, 0.28 of the human above the 10.4% random floor |
| `game-balrog-crafter-claudehaiku45` | 24.09% progression | 0.259 | Crafter progression 24.09% against the human expert 63.18%, 0.26 of the human above the 10.4% random floor |
| `game-balrog-crafter-llama32-3b` | 17.27% progression | 0.130 | Crafter progression 17.27% against the human expert 63.18%, 0.13 of the human above the 10.4% random floor |
| `game-balrog-crafter-qwen25-7b` | 16.36% progression | 0.113 | Crafter progression 16.36% against the human expert 63.18%, 0.11 of the human above the 10.4% random floor |
| `game-balrog-crafter-r1distillqwen32b` | 15.00% progression | 0.087 | Crafter progression 15.00% against the human expert 63.18%, 0.09 of the human above the 10.4% random floor |
| `game-balrog-crafter-phi4` | 13.64% progression | 0.061 | Crafter progression 13.64% against the human expert 63.18%, 0.06 of the human above the 10.4% random floor |
| `game-balrog-crafter-llama32-1b` | 12.73% progression | 0.044 | Crafter progression 12.73% against the human expert 63.18%, 0.04 of the human above the 10.4% random floor |

**Cross-check.** The five lowest exclusions here — Llama 3.2 1B, Phi-4, R1-Distill-Qwen-32B,
Qwen2.5 7B and Llama 3.2 3B — are exactly the five rows `DECISIONS.md` already flagged as sitting
within 2.5 combined standard errors of the random floor (1.22, 1.23, 2.14, 1.97 and 2.46). The
ratio rule reproduces that flag without being tuned to it.

### MirrorCode — 6 of 13

Not named in Damon's ruling, so worth his eye. The criterion is a complete pass of the test suite,
which these six never approached; the seven survivors all met or effectively met it and stay
`match`.

| point_id | Score | Ratio | Reason |
|---|---|---|---|
| `agen-mirrorcode-pkl-c-opus46` | 41.7% pass rate | 0.417 | passed 41.7% of 770 cases against a complete-pass criterion, with pkl reported unsolved under the budget |
| `agen-mirrorcode-pkl-py-opus46` | 38.6% transferred pass rate | 0.386 | scoring pass crashed, so the disposition transfers from the same model and budget in C and Rust at 41.7% and 35.5% against a complete-pass criterion |
| `agen-mirrorcode-gotree-py-opus45` | 38.1% mean pass rate | 0.381 | episodes passed 47.3/3.7/63.2% of 2,001 cases, mean 38.1%, against a complete-pass criterion the run never met |
| `agen-mirrorcode-pkl-rust-opus46` | 35.5% pass rate | 0.355 | passed 35.5% of 770 cases against a complete-pass criterion, with pkl reported unsolved under the budget |
| `agen-mirrorcode-gotree-py-opus41` | 15.6% mean pass rate | 0.156 | episodes passed 15.8/23.5/7.6% of 2,001 cases, mean 15.6%, against a complete-pass criterion the run never met |
| `agen-mirrorcode-gotree-py-opus4` | 8.8% mean pass rate | 0.088 | episodes passed 1.2/15.3/9.8% of 2,001 cases, mean 8.8%, against a complete-pass criterion the run never met |

### Remote Labor Index — all 5

| point_id | Score | Ratio | Reason |
|---|---|---|---|
| `work-rli-sonnet45` | 2.08% automation rate | 0.021 | automation rate 2.08% against 100% of the paid human deliverables meeting the same bar by construction |
| `work-rli-grok4` | 2.08% automation rate | 0.021 | automation rate 2.08% against 100% of the paid human deliverables meeting the same bar by construction |
| `work-rli-gpt5-cli` | 1.67% automation rate | 0.017 | automation rate 1.67% against 100% of the paid human deliverables meeting the same bar by construction |
| `work-rli-gpt5-cua` | 0.83% automation rate | 0.008 | automation rate 0.83% against 100% of the paid human deliverables meeting the same bar by construction |
| `work-rli-gemini25pro` | 0.83% automation rate | 0.008 | automation rate 0.83% against 100% of the paid human deliverables meeting the same bar by construction |

### HourVideo — both rows

| point_id | Score | Ratio | Reason |
|---|---|---|---|
| `perc-hourvideo-gemini15pro-tasklevel` | 38.9% accuracy | 0.291 | 38.9% against three human experts at 85.0%, 0.29 of the human above the 20% guessing floor |
| `perc-hourvideo-gemini15pro-individual` | 36.8% accuracy | 0.258 | 36.8% against three human experts at 85.0%, 0.26 of the human above the 20% guessing floor |

### Epoch SWE-bench bins (candidate) — 61 of 124

Pre-decided so they take effect on acceptance; `candidates/epoch-swebench-bins/points.csv` is not
edited. The exclusions concentrate in the hard bins, which is the pattern the bin split was built
to show: the `<15 min` bin loses 1 row of 31, `15 min – 1 hour` loses 2, `1–4 hours` loses 28, and
`>4 hours` loses all but one of 31.

| point_id | Score | Ratio | Reason |
|---|---|---|---|
| `agen-epoch-swebench-gpt4o1120-lt15m` | 49.2% bin solve rate | 0.492 | bin solve rate 49.2% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gemini35flash-1h4h` | 47.6% bin solve rate | 0.476 | bin solve rate 47.6% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt53codex-1h4h` | 47.6% bin solve rate | 0.476 | bin solve rate 47.6% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-opus41-1h4h` | 47.6% bin solve rate | 0.476 | bin solve rate 47.6% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-glm52max-1h4h` | 45.2% bin solve rate | 0.452 | bin solve rate 45.2% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-kimik26-1h4h` | 45.2% bin solve rate | 0.452 | bin solve rate 45.2% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-opus45-1h4h` | 45.2% bin solve rate | 0.452 | bin solve rate 45.2% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-opus46-1h4h` | 45.2% bin solve rate | 0.452 | bin solve rate 45.2% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-sonnet46-1h4h` | 42.9% bin solve rate | 0.429 | bin solve rate 42.9% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt41-15m1h` | 41.7% bin solve rate | 0.417 | bin solve rate 41.7% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-glm5-1h4h` | 41.5% bin solve rate | 0.415 | bin solve rate 41.5% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gemini31pro-ct-1h4h` | 40.5% bin solve rate | 0.405 | bin solve rate 40.5% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-qwen37max-1h4h` | 40.5% bin solve rate | 0.405 | bin solve rate 40.5% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt52high-1h4h` | 38.1% bin solve rate | 0.381 | bin solve rate 38.1% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt5med-1h4h` | 38.1% bin solve rate | 0.381 | bin solve rate 38.1% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-dsv4promax-1h4h` | 36.6% bin solve rate | 0.366 | bin solve rate 36.6% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt5high-1h4h` | 35.7% bin solve rate | 0.357 | bin solve rate 35.7% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-opus4-1h4h` | 35.7% bin solve rate | 0.357 | bin solve rate 35.7% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-sonnet45-1h4h` | 35.7% bin solve rate | 0.357 | bin solve rate 35.7% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gemini31pro-ct-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gemini35flash-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gemini3flash-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gemini3pro-1h4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gemini3pro-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-glm5-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-glm52max-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt51codex-1h4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt51codex-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt52high-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt53codex-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt54high-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt5high-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-kimik25-1h4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-kimik25-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-opus4-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-opus41-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-opus45-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-opus46-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-opus46cc-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-qwen37max-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-sonnet37-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-sonnet46-gt4h` | 33.3% bin solve rate | 0.333 | bin solve rate 33.3% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt51high-1h4h` | 28.6% bin solve rate | 0.286 | bin solve rate 28.6% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gemini3flash-1h4h` | 23.8% bin solve rate | 0.238 | bin solve rate 23.8% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt4o1120-15m1h` | 22.0% bin solve rate | 0.220 | bin solve rate 22.0% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gemini25pro-1h4h` | 21.4% bin solve rate | 0.214 | bin solve rate 21.4% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-o3med-1h4h` | 21.4% bin solve rate | 0.214 | bin solve rate 21.4% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-sonnet37-1h4h` | 19.0% bin solve rate | 0.190 | bin solve rate 19.0% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt5mini-1h4h` | 16.7% bin solve rate | 0.167 | bin solve rate 16.7% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt41-1h4h` | 12.2% bin solve rate | 0.122 | bin solve rate 12.2% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt4o1120-1h4h` | 7.1% bin solve rate | 0.071 | bin solve rate 7.1% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-dsv4promax-gt4h` | 0.0% bin solve rate | 0.000 | bin solve rate 0.0% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gemini25pro-gt4h` | 0.0% bin solve rate | 0.000 | bin solve rate 0.0% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt41-gt4h` | 0.0% bin solve rate | 0.000 | bin solve rate 0.0% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt4o1120-gt4h` | 0.0% bin solve rate | 0.000 | bin solve rate 0.0% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt51high-gt4h` | 0.0% bin solve rate | 0.000 | bin solve rate 0.0% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt5med-gt4h` | 0.0% bin solve rate | 0.000 | bin solve rate 0.0% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-gpt5mini-gt4h` | 0.0% bin solve rate | 0.000 | bin solve rate 0.0% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-kimik26-gt4h` | 0.0% bin solve rate | 0.000 | bin solve rate 0.0% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-o3med-gt4h` | 0.0% bin solve rate | 0.000 | bin solve rate 0.0% against a complete correct patch by a human given the bin's own time estimate |
| `agen-epoch-swebench-sonnet45-gt4h` | 0.0% bin solve rate | 0.000 | bin solve rate 0.0% against a complete correct patch by a human given the bin's own time estimate |

### APEX-Agents (candidate) — all 9

| point_id | Score | Ratio | Reason |
|---|---|---|---|
| `work-apex-agents-gemini35flash` | 47.1% pass@1 | 0.471 | pass@1 47.1% against an expert-written gold arm passing by construction |
| `work-apex-agents-kimik3` | 41.3% pass@1 | 0.413 | pass@1 41.3% against an expert-written gold arm passing by construction |
| `work-apex-agents-gpt56terra` | 38.9% pass@1 | 0.389 | pass@1 38.9% against an expert-written gold arm passing by construction |
| `work-apex-agents-gpt55` | 37.7% pass@1 | 0.377 | pass@1 37.7% against an expert-written gold arm passing by construction |
| `work-apex-agents-gpt56luna` | 35.8% pass@1 | 0.358 | pass@1 35.8% against an expert-written gold arm passing by construction |
| `work-apex-agents-glm52` | 33.7% pass@1 | 0.337 | pass@1 33.7% against an expert-written gold arm passing by construction |
| `work-apex-agents-gpt54` | 33.3% pass@1 | 0.333 | pass@1 33.3% against an expert-written gold arm passing by construction |
| `work-apex-agents-opus46` | 33.0% pass@1 | 0.330 | pass@1 33.0% against an expert-written gold arm passing by construction |
| `work-apex-agents-gptoss120b` | 3.1% pass@1 | 0.031 | pass@1 3.1% against an expert-written gold arm passing by construction |

## Rows kept `below`

| point_id | Score | Ratio | Basis |
|---|---|---|---|
| `game-balrog-crafter-gemini25flash` | 40.00% progression | 0.561 | ratio |
| `game-balrog-crafter-gpt5minimal` | 39.09% progression | 0.544 | ratio |
| `game-balrog-crafter-gemini3flash` | 45.00% progression | 0.656 | ratio |
| `game-balrog-crafter-gemini31pro` | 46.82% progression | 0.690 | ratio |
| `game-balrog-crafter-claudeopus45` | 49.55% progression | 0.742 | ratio |
| `game-balrog-crafter-claudeopus45thinking` | 48.64% progression | 0.725 | ratio |
| `game-balrog-crafter-vlm-claude35sonnet` | 37.27% progression | 0.509 | ratio |
| `game-balrog-crafter-vlm-gemini25pro` | 37.27% progression | 0.509 | ratio |
| `agen-lumen-d1-gemini31pro` | — | — | completion at lower quality |
| `agen-lumen-d2-gemini31pro` | — | — | completion at lower quality |
| `agen-lumen-d4-gemini31pro` | — | — | completion at lower quality |
| `lang-lait-novel-opening-gpt54` | — | — | completion at lower quality |
| `agen-epoch-swebench-dsv4promax-lt15m` | 88.1% bin solve rate | 0.881 | ratio |
| `agen-epoch-swebench-dsv4promax-15m1h` | 77.6% bin solve rate | 0.776 | ratio |
| `agen-epoch-swebench-gemini25pro-lt15m` | 75.5% bin solve rate | 0.755 | ratio |
| `agen-epoch-swebench-gemini25pro-15m1h` | 51.2% bin solve rate | 0.512 | ratio |
| `agen-epoch-swebench-gemini31pro-ct-lt15m` | 83.8% bin solve rate | 0.838 | ratio |
| `agen-epoch-swebench-gemini31pro-ct-15m1h` | 76.0% bin solve rate | 0.760 | ratio |
| `agen-epoch-swebench-gemini35flash-lt15m` | 88.6% bin solve rate | 0.886 | ratio |
| `agen-epoch-swebench-gemini35flash-15m1h` | 78.3% bin solve rate | 0.783 | ratio |
| `agen-epoch-swebench-gemini3flash-lt15m` | 88.6% bin solve rate | 0.886 | ratio |
| `agen-epoch-swebench-gemini3flash-15m1h` | 74.8% bin solve rate | 0.748 | ratio |
| `agen-epoch-swebench-gemini3pro-lt15m` | 87.0% bin solve rate | 0.870 | ratio |
| `agen-epoch-swebench-gemini3pro-15m1h` | 69.7% bin solve rate | 0.697 | ratio |
| `agen-epoch-swebench-glm5-lt15m` | 82.2% bin solve rate | 0.822 | ratio |
| `agen-epoch-swebench-glm5-15m1h` | 70.2% bin solve rate | 0.702 | ratio |
| `agen-epoch-swebench-glm52max-lt15m` | 89.1% bin solve rate | 0.891 | ratio |
| `agen-epoch-swebench-glm52max-15m1h` | 77.2% bin solve rate | 0.772 | ratio |
| `agen-epoch-swebench-gpt41-lt15m` | 66.8% bin solve rate | 0.668 | ratio |
| `agen-epoch-swebench-gpt51codex-lt15m` | 75.7% bin solve rate | 0.757 | ratio |
| `agen-epoch-swebench-gpt51codex-15m1h` | 64.6% bin solve rate | 0.646 | ratio |
| `agen-epoch-swebench-gpt51high-lt15m` | 81.1% bin solve rate | 0.811 | ratio |
| `agen-epoch-swebench-gpt51high-15m1h` | 65.7% bin solve rate | 0.657 | ratio |
| `agen-epoch-swebench-gpt52high-lt15m` | 85.4% bin solve rate | 0.854 | ratio |
| `agen-epoch-swebench-gpt52high-15m1h` | 71.7% bin solve rate | 0.717 | ratio |
| `agen-epoch-swebench-gpt53codex-lt15m` | 83.2% bin solve rate | 0.832 | ratio |
| `agen-epoch-swebench-gpt53codex-15m1h` | 73.6% bin solve rate | 0.736 | ratio |
| `agen-epoch-swebench-gpt54high-lt15m` | 87.0% bin solve rate | 0.870 | ratio |
| `agen-epoch-swebench-gpt54high-15m1h` | 74.0% bin solve rate | 0.740 | ratio |
| `agen-epoch-swebench-gpt54high-1h4h` | 52.4% bin solve rate | 0.524 | ratio |
| `agen-epoch-swebench-gpt5high-lt15m` | 87.0% bin solve rate | 0.870 | ratio |
| `agen-epoch-swebench-gpt5high-15m1h` | 70.5% bin solve rate | 0.705 | ratio |
| `agen-epoch-swebench-gpt5med-lt15m` | 85.4% bin solve rate | 0.854 | ratio |
| `agen-epoch-swebench-gpt5med-15m1h` | 67.7% bin solve rate | 0.677 | ratio |
| `agen-epoch-swebench-gpt5mini-lt15m` | 77.8% bin solve rate | 0.778 | ratio |
| `agen-epoch-swebench-gpt5mini-15m1h` | 63.8% bin solve rate | 0.638 | ratio |
| `agen-epoch-swebench-kimik25-lt15m` | 87.0% bin solve rate | 0.870 | ratio |
| `agen-epoch-swebench-kimik25-15m1h` | 71.3% bin solve rate | 0.713 | ratio |
| `agen-epoch-swebench-kimik26-lt15m` | 85.9% bin solve rate | 0.859 | ratio |
| `agen-epoch-swebench-kimik26-15m1h` | 76.0% bin solve rate | 0.760 | ratio |
| `agen-epoch-swebench-o3med-lt15m` | 75.5% bin solve rate | 0.755 | ratio |
| `agen-epoch-swebench-o3med-15m1h` | 60.2% bin solve rate | 0.602 | ratio |
| `agen-epoch-swebench-opus4-lt15m` | 83.2% bin solve rate | 0.832 | ratio |
| `agen-epoch-swebench-opus4-15m1h` | 67.7% bin solve rate | 0.677 | ratio |
| `agen-epoch-swebench-opus41-lt15m` | 82.2% bin solve rate | 0.822 | ratio |
| `agen-epoch-swebench-opus41-15m1h` | 71.7% bin solve rate | 0.717 | ratio |
| `agen-epoch-swebench-opus45-lt15m` | 88.6% bin solve rate | 0.886 | ratio |
| `agen-epoch-swebench-opus45-15m1h` | 73.6% bin solve rate | 0.736 | ratio |
| `agen-epoch-swebench-opus46-lt15m` | 87.0% bin solve rate | 0.870 | ratio |
| `agen-epoch-swebench-opus46-15m1h` | 72.8% bin solve rate | 0.728 | ratio |
| `agen-epoch-swebench-opus46cc-lt15m` | 88.6% bin solve rate | 0.886 | ratio |
| `agen-epoch-swebench-opus46cc-15m1h` | 76.4% bin solve rate | 0.764 | ratio |
| `agen-epoch-swebench-opus46cc-1h4h` | 52.4% bin solve rate | 0.524 | ratio |
| `agen-epoch-swebench-opus47max-lt15m` | 90.8% bin solve rate | 0.908 | ratio |
| `agen-epoch-swebench-opus47max-15m1h` | 82.3% bin solve rate | 0.823 | ratio |
| `agen-epoch-swebench-opus47max-1h4h` | 59.5% bin solve rate | 0.595 | ratio |
| `agen-epoch-swebench-opus47max-gt4h` | 66.7% bin solve rate | 0.667 | ratio |
| `agen-epoch-swebench-qwen37max-lt15m` | 88.6% bin solve rate | 0.886 | ratio |
| `agen-epoch-swebench-qwen37max-15m1h` | 75.6% bin solve rate | 0.756 | ratio |
| `agen-epoch-swebench-sonnet37-lt15m` | 78.9% bin solve rate | 0.789 | ratio |
| `agen-epoch-swebench-sonnet37-15m1h` | 55.1% bin solve rate | 0.551 | ratio |
| `agen-epoch-swebench-sonnet45-lt15m` | 81.6% bin solve rate | 0.816 | ratio |
| `agen-epoch-swebench-sonnet45-15m1h` | 70.5% bin solve rate | 0.705 | ratio |
| `agen-epoch-swebench-sonnet46-lt15m` | 85.9% bin solve rate | 0.859 | ratio |
| `agen-epoch-swebench-sonnet46-15m1h` | 73.2% bin solve rate | 0.732 | ratio |

## Close calls

**Superseded 2026-09-13 by the close-calls ruling.** `DECISIONS.md`, "Close calls at the
exclusion line" (coordinator): a row whose above-chance ratio to the human is within one standard
error of the 0.5 guide is kept as `below`; a row more than one standard error under it is excluded.
This replaces the earlier "about half" band, which was an eyeballed 0.45–0.50 window, with a test
that scales to each row's own evidence.

Each row's standard error is computed on its own sampling unit by
`research/performance-relabel/close_calls.py`:

| Batch | Sampling unit | SE |
|---|---|---|
| SWE-bench bins | one issue in the bin | binomial on the resolved count k of n; the human side is a complete correct patch, exact, so SE(ratio) = SE(p) |
| Crafter | one episode | both sides carry a reported SE, so SE(ratio) = sqrt(se_A² + ratio²·se_H²)/(H − floor) |
| MirrorCode, repeat episodes | one episode | SEM over the episodes |
| MirrorCode, single episode | one test case | binomial over cases, reported as a floor on the true SE |
| RLI, HourVideo | one scored item | binomial, human side included where it is sampled |
| VideoGameBench | — | one funded run per model per game, so no sampling unit and no SE |

**31 rows were restored to `points.csv` as `below`.** 20 of the SWE-bench `>4 hours` bin, 8 of its
`1-4 hours` bin, 1 of its `<15 min` bin, one Crafter row and one MirrorCode row.

| point_id | Ratio | SE | Basis |
|---|---|---|---|
| `agen-epoch-swebench-gpt4o1120-lt15m` | 0.492 | 0.037 | binomial on the bin, 49.2% solved |
| `agen-epoch-swebench-gemini35flash-1h4h` | 0.476 | 0.077 | binomial on the bin, 47.6% solved |
| `agen-epoch-swebench-gpt53codex-1h4h` | 0.476 | 0.077 | binomial on the bin, 47.6% solved |
| `agen-epoch-swebench-opus41-1h4h` | 0.476 | 0.077 | binomial on the bin, 47.6% solved |
| `agen-epoch-swebench-glm52max-1h4h` | 0.452 | 0.077 | binomial on the bin, 45.2% solved |
| `agen-epoch-swebench-kimik26-1h4h` | 0.452 | 0.077 | binomial on the bin, 45.2% solved |
| `agen-epoch-swebench-opus45-1h4h` | 0.452 | 0.077 | binomial on the bin, 45.2% solved |
| `agen-epoch-swebench-opus46-1h4h` | 0.452 | 0.077 | binomial on the bin, 45.2% solved |
| `game-balrog-crafter-rekaflash3` | 0.440 | 0.067 | reported episode SEs on both sides |
| `agen-epoch-swebench-sonnet46-1h4h` | 0.429 | 0.076 | binomial on the bin, 42.9% solved |
| `agen-mirrorcode-gotree-py-opus45` | 0.381 | 0.178 | SEM over 3 episodes (47.3, 3.7, 63.2) |
| `agen-epoch-swebench-gemini31pro-ct-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-gemini35flash-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-gemini3flash-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-gemini3pro-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-glm5-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-glm52max-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-gpt51codex-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-gpt52high-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-gpt53codex-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-gpt54high-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-gpt5high-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-kimik25-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-opus4-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-opus41-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-opus45-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-opus46-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-opus46cc-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-qwen37max-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-sonnet37-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |
| `agen-epoch-swebench-sonnet46-gt4h` | 0.333 | 0.272 | binomial on the bin, 33.3% solved |


Within MirrorCode, the pkl rows are the sharpest contrast: `pkl-c` at ratio 0.417 has a binomial SE
of 0.018 over 770 cases and stays excluded, while `gotree-py-opus45` at the lower ratio 0.381 is
restored on an SEM of 0.178 over three episodes. The difference is the sampling unit, not the
performance.

### Two artifacts of the rule worth Damon's eye

- **The `>4 hours` bin holds 3 issues, and it supplies 20 of the 31 restorations.** At 1/3 the
  binomial SE is 0.272, so every model that resolved one issue is within one SE of 0.5 and comes
  back. At 0/3 the binomial SE is exactly 0, so every model that resolved none is more than one SE
  under and stays out — permanently, since no width of interval can rescue a point estimate whose
  SE is zero by construction. The bin's 31 rows therefore split 20 restored and 10 excluded, plus
  the one row that was never excluded, on the difference between resolving one issue out of three
  and resolving none. That is the least
  reliable evidence in the batch receiving the most generous treatment, and the p = 0 SE is an
  artifact of the binomial rather than a statement about the run. A Wilson or Jeffreys interval
  would give 0/3 a non-zero width and treat the bin consistently.
- **A noisier row earns restoration more easily.** `agen-mirrorcode-gotree-py-opus45` is restored
  at ratio 0.381 only because its three episodes ran 47.3%, 3.7% and 63.2%, giving an SEM of 0.178.
  Had the same mean come from three consistent episodes it would have stayed excluded. This is the
  same property `research/balrog.md` already flagged for the `match` rule, where Gemini 3.1 Pro at
  46.82 ± 4.17 is `below` while the same model with a thinking budget at 55.00 ± 6.44 is `match`.

Neither is a reason to depart from the ruling as written, and neither was departed from. Both are
recorded so the threshold can be revisited with the consequences visible.

### Still excluded, nearest the line

The four rows that came closest without qualifying, for anyone reconsidering the width:

| point_id | Ratio | SE | Gap to 0.5 |
|---|---|---|---|
| `game-balrog-crafter-claude35sonnet` | 0.4231 | 0.0619 | 0.0769 |
| `agen-mirrorcode-pkl-c-opus46` | 0.4169 | 0.0178 | 0.0831 |
| `agen-epoch-swebench-gpt41-15m1h` | 0.4167 | 0.0311 | 0.0833 |
| `agen-epoch-swebench-glm5-1h4h` | 0.4146 | 0.0769 | 0.0854 |

APEX-Agents was out of scope here, decided by its own criterion-level pass; GAIA likewise by its
constructor.

## `far_above` check

The only `above` row in the folder is `robo-drone-monorace`, and it keeps `above`. MonoRace's two
completions at 17.18 s and 16.59 s beat all six human completions, which run 19.14 to 26.01 s, but
the gap to the fastest human is 2.55 s on a 16.59 s run, or 15%. The human side plainly still does
the job — it flies the track — so this is the modest edge `above` describes, not a step no human
matched. The reliability evidence cuts the same way: the deployed policy completed 1 of 4 real
flights against the pilots' 6 of 10. No `match` row has evidence that would support `above` or
`far_above`.

## Text check

Every excluded row's `performance_evidence` and `notes` were scanned for a sentence asserting the
old label. **No edits were needed.** The scan's hits were all incidental: "above the 10.35%
uniform-random floor" in five Crafter rows, "2.1 points below the same model under task-level
batching" in a HourVideo row, and "list prices double above 128k prompt tokens" in an RLI row. None
of these asserts a `performance_vs_human` value, and all remain true. No row's text was changed.

## Tooling

| File | Role |
|---|---|
| `research/performance-relabel.csv` | The override file: point_id, old_label, new_label, action, reason. 132 lines, all `exclude`. |
| `research/performance-relabel/relabel.py` | Derives the overrides from the CSVs. Takes explicit input and output paths; standard library only. |
| `agent-work/derived/performance-relabel/examined.json` | All 239 rows examined with ratio, metric and disposition. |
| `tools/resync.py` | Unchanged in its candidate re-sync behaviour; now calls `apply_overrides()` afterwards. |

`apply_overrides()` rewrites labels for `relabel` rows, moves `exclude` rows out of `points.csv`
into `excluded.csv` with their `exclusion_reason`, and moves rows back when their action is no
longer `exclude`. It is idempotent in both directions: a second run reports 0 changes, and a
candidate re-sync that reintroduces an older label is corrected immediately afterwards. Running
`python3 tools/resync.py` with no argument just re-asserts the overrides. The supported way to
restore a row is to flip its `action` to `relabel`; deleting the line also restores the row, but
the label it carried when excluded travels with it, and the script prints a warning.

## For the merge

`COLUMNS.md` carries the amended enum with a dated note. Two things go to the merge:

- The Codex dataset's `below` rows need the same classification pass from their
  `performance_evidence`, per Damon's ruling. That is a merge-time task and nothing in
  `../AI Compute vs Human Time/` was touched here.
- `incorporate.py` has no concept of `excluded.csv`. The merge plan needs to decide whether the
  excluded rows travel as a parallel file or are dropped, and the batch's research notes still
  describe them, since the notes were deliberately not rewritten.
