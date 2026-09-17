# LAIT — agentic literary translation of novel openings (arXiv 2606.26040)

*Created 2026-09-13 12:00.*
*Last revised 2026-09-13 12:58 — Revision 1, applying the three required corrections in
`reviews/lait-independent.md`; see `candidates/lait/REVISION.md`.*

## Summary

**One candidate row, `lang-lait-novel-opening-gpt54`: 3.47e17 FLOPs against 72,744 human
active seconds (20.2 hours), i.e. 4.8e12 FLOPs per human-second, labelled `below`.** The
work unit is one ~7,600-word opening excerpt of a recently published novel translated
from French, Polish or Japanese into publishable English; the aggregate row stands for
all 15 evaluation books, which is the only unit the evidence supports (see
[One row or fifteen](#one-row-or-fifteen)). The pipeline's *workload structure* is
measured — 217 source chunks and 1,449 agent jobs across the 15 evaluation runs, recovered
from the repository's own withheld-file manifest — but the *tokens per job* are modelled,
so the honest range is **1.9e17 to 5.9e17**. Human time is a transfer of Toral, Wieling &
Way's (2018) keystroke-logged 503 words per hour for professional literary translation
from scratch, with revision scenarios reaching 22.7 hours.

**TransLaw (arXiv 2507.00875v2) gets no row.** Its US$0.35 API figure cannot be converted
to tokens: no snapshot, no price date, no input/output split, and the figure is smaller
than the arithmetic floor for the deliverable it claims to have produced. See
[TransLaw disposition](#translaw-disposition).

Three things a reviewer should look at first:

1. **The compute estimate is mostly a model of agent-harness overhead, not of
   translation.** A `translate` job carries about 1,350 tokens of actual task content —
   the source chunk plus two boundary contexts — inside a modelled 6,800-token prefix.
   Harness prefix size and reasoning volume move the answer 1.44x and 1.65x across their
   declared bands and are the two assumptions worth arguing about. Everything structural
   is now measured.
2. **The scout's note was wrong about the usage counters, and the repository proves it
   twice.** `agents_pipeline/core/executor.py` writes `input_tokens`, `output_tokens`,
   `cached_input_tokens` and `total_cost_usd` per job into
   `<run_dir>/metrics/run_summary.json`, and `docs/release/withheld-files.tsv` lists
   exactly 31 such files as withheld — the same 31 the paper says have job metrics. The
   measurement exists and one email would replace this whole derivation.
3. **`below` versus `match` is a real call.** Readers could not tell MT from HT (17/30,
   p=.585) and split 19–11 at excerpt level (p=.148), but preferred HT 522–250 at chunk
   level (p=.011) with 4.0x odds on acceptability as a published translation (p=.0069).
   The reasoning is in [Performance](#performance).

Point ID: `lang-lait-novel-opening-gpt54`. No new model records: `claude-opus-4-6` and
`gpt-5.4-2026-03-05` both already exist in `../AI Compute vs Human Time/dataset/models.csv`
at 2.0e11 FLOPs per token, and `candidates/lait/models.csv` is headers only.

---

## Source and what it actually publishes

Ferstler Y, Podoxin A, Brassington T, Grundkiewicz R, Taboada M, Karpinska M. *AI
translation of literary texts is 'fine', but readers still prefer human translations.*
arXiv:2606.26040v1 [cs.CL], 24 June 2026. Code and artifacts at
`https://github.com/Yves575/lait`. Retained text at
`agent-work/sources/lait/lait-2606.26040v1-text.txt`, key passages and tables at
`agent-work/sources/lait/lait-paper-extracts.md`, every value used transcribed into
`agent-work/sources/lait/lait-source-values.json`, and provenance for all retained files in
`agent-work/sources/lait/MANIFEST.md`.

Reported, and used here:

- **Table 1** — evaluation-set summary statistics over 15 books: source, human-translation
  and machine-translation token counts (`tiktoken` `o200k_base`) and whitespace word
  counts.
- **Table 7** — per-book word and token counts of each of the five candidate pipelines'
  output over the 16 development books. Context only: nothing in the row depends on it now
  that the run inventory is measured.
- **Tables 8 and 9** — run counts by group, language and gate verdict; 35 completed runs,
  441 source chunks, 1,059 chunk-cycle artifacts, 31 runs with job-metric logs, 2,930
  logged agent jobs including 19 failures, 74 final-gate flagged chunks.
- **Appendix A** — the book list, which identifies the 15 main-evaluation books.
- **Sections 3.1 and 3.3 and Table 38** — the reader results.
- **The public pipeline** — `agents_pipeline/`: the chunker, the eight prompt templates,
  the stage-to-model mapping, the executor that shells out to the two agent CLIs, and the
  runner that drives the two loops.
- **`docs/release/withheld-files.tsv`** — the manifest of the 8,066 files removed from the
  public branch. It withholds the files but publishes their paths, which turns out to be
  the single most useful artifact in the release. See
  [Pipeline structure](#pipeline-structure).

Not reported, and therefore modelled here:

- **Any token, call or cost figure for any run.** Footnote 8: *"Both agents were accessed
  via a monthly subscription at the cost of $400 USD for the entire experiment."*
  Appendix B footnote 29: *"Because agents make many model calls, running them via API is
  prohibitively expensive; instead we used subscription services, which cap our
  translation count."*
- **Per-book source and output token counts.** Table 1 gives means and dispersion, not 15
  rows.
- **Translator hours for these books.** Nothing exists; the human side is a transfer.

### The measurement exists and is withheld

The scouting note (`research/scouting/book-length-text.md`) concluded that `runner.py`
records only `duration_seconds` and that the withheld run workspaces "almost certainly
hold wall-clock, not tokens". That is wrong. `agents_pipeline/core/executor.py`, retained
at `agent-work/sources/lait/repo/agents_pipeline-core-executor.py`, builds a per-job metric record
containing `input_tokens`, `output_tokens`, `cached_input_tokens` and `total_cost_usd`
(lines 111–135), populated by `_extract_usage_summary` from the Claude `result` event and
the Codex `turn.completed` event (lines 773–809), and appends it to
`<run_dir>/metrics/run_summary.json`. `runner.py` only ever reads `duration_seconds` back
out of that file, which is why grepping the runner alone misses it.

`docs/release/withheld-files.tsv` confirms it from the other side: it lists exactly 31
paths matching `runs/*/metrics/run_summary.json`, one per run, against Table 9's *"Runs
with job-metric logs 31"*.

Per `DECISIONS.md` no outreach is made at this stage. The row is
`derived_assumed_inputs` reconstructing a quantity that was measured, not one that was
never recorded.

### The README contradicts the config, and the config wins

`agents_pipeline/README.md` prints a stage table putting `translate` and `revise` on
Claude and naming the Codex model `gpt-5-codex`. The checked-in
`agents_pipeline/config.json` puts `translate`, `litrans_review`, `revise`, `book_review`
and `cross_chunk_audit` on `codex`/`gpt-5.4`, and `style_analysis`,
`chunk_literary_review` and `final_revise` on `claude`/`claude-opus-4-6`. The paper's own
prose settles it: *"Codex translated each chunk"*, *"literary quality review (e.g., voice,
style) adapted from AutoFiction (Claude Code)"*, and *"reviewed for (1) global literary
quality and (2) cross-chunk consistency (Codex)"*. The README table is stale. This row
follows the config and the paper.

That decides `model_id`. GPT-5.4 runs five of the eight stages, produces every draft and
every revision that is not a final revision, and carries 62% of the modelled tokens, so
`gpt-5.4-2026-03-05` is the primary model and Claude Opus 4.6 is the helper whose tokens
are included in `compute_flops` at its own coefficient.

---

## The work unit

One book-opening excerpt, selected from the published English human translation at
~8,000 whitespace words (mean 7,623, SD 449, range 6,747–7,995), with the corresponding
source excerpt identified manually. The source excerpt is 13,026 `o200k_base` tokens on
average (SD 1,527, range 11,155–15,967). The machine translation produced from it is
9,582 tokens / 7,676 words on average; the published human translation of the same
passage is 9,680 tokens / 7,623 words.

The completion criterion on the AI side is the pipeline's own final acceptance gate. It is
not a success filter: 22 of 35 runs ended FAIL, and the authors state that *"even when the
final translation failed to pass within the enforced limits we observe that increasing the
limits did not show justifiable improvements, while the 'failed' translation was often
acceptable"*. Every run produced a delivered translation and all 15 evaluation
translations went to readers, so `compute_subset` is `all` and there is no
attempt-selection asymmetry from the gate.

The books are critically acclaimed fiction originally in French, Polish and Japanese whose
professional English translations were published in 2025–2026, chosen that way to limit
contamination. The human side is therefore a real trade deliverable, not a
study-commissioned translation. The runs themselves are dated by their workspace
directory names: **15 April to 4 May 2026**, with the four multilingual runs last.

### One row or fifteen

**One aggregate row.** The case for 15:

- The evaluation is per book, and MT preference varies from 4% to 88% across books with
  book identity strongly associated with chunk-level preference (p<.001).
- Per-book chunk counts *are* now recoverable (12 to 17), and per-book MT outputs are in
  the repository under `books/MT/pipeline3/`.

Per-book compute is **not** constant, and it is not a function of chunk count either. The
manifest gives job totals per run, and they span 80 to 116, a factor of 1.45, driven by the
local cycle count, the global cycle count and the `final_revise` count. The book with the
fewest chunks has the most jobs:

| Run | Source chunks | Agent jobs | Jobs per chunk | `final_revise` jobs |
|---|---:|---:|---:|---:|
| make_me_famous_fr | 12 | 116 | 9.67 | 3 |
| sisters_in_yellow_ja | 17 | 110 | 6.47 | 3 |
| kokun_the_girl_from_the_west_ja | 17 | 105 | 6.18 | 0 |
| the_empusium_pl | 17 | 105 | 6.18 | 0 |
| inner_space_pl | 16 | 99 | 6.19 | 0 |
| my_grandfather_the_master_detective_ja | 15 | 99 | 6.60 | 4 |
| needle_s_eye_pl | 15 | 99 | 6.60 | 4 |
| mona_s_eyes_fr | 15 | 97 | 6.47 | 2 |
| the_witcher_crossroads_of_ravens_pl | 14 | 95 | 6.79 | 6 |
| hooked_a_novel_of_obsession_ja | 14 | 92 | 6.57 | 3 |
| the_ark_ja | 14 | 91 | 6.50 | 2 |
| my_name_is_stramer_pl | 14 | 91 | 6.50 | 2 |
| watching_over_her_fr | 13 | 87 | 6.69 | 4 |
| the_story_of_marceau_miller_fr | 12 | 83 | 6.92 | 6 |
| symphony_of_monsters_fr | 12 | 80 | 6.67 | 3 |

`make_me_famous_fr` is the only evaluation run to use three local cycles, which is what puts
a 12-chunk book at the top. So the x axis would carry real per-book variation. The case
against building fifteen rows is entirely about the other axis and the labels:

- **Per-book human time would be identical.** Table 1 publishes only the 7,623-word mean, so
  the transfer — a rate times a word count — returns the same 72,744 seconds for every book. Fifteen
  points stacked at one y value, with x spread 1.45x, is a scatter artifact, not information.
- **Per-book performance rests on two readers.** A 4%-MT book and an 88%-MT book differ by
  two people's chunk judgments over roughly 26 chunk pairs each. Fifteen
  `performance_vs_human` labels at that sample size would be noise presented as fifteen
  findings.

So: one row, work unit "one excerpt", `compute_statistic = mean` over the 15 evaluation
runs, `ai_attempts = 15`. The aggregate over all 15 books, if it is ever wanted, is
5.21e18 FLOPs against 818,374 human seconds; it is in
`agent-work/derived/lait/lait-calculations.json` under `aggregate_15_books` and is not a row.

The four multilingual case-study runs (Japanese→French/Polish/Spanish and
Polish→Japanese) are **not drafted**. Same pipeline, but one reader each, no aligned close
reading, and a result different in kind: 4 of 5 readers identified the MT correctly with
mean confidence 4.4/5, and HT was strongly preferred. They would need their own
performance treatment and their own output geometry, and neither is supported by what the
paper publishes about them.

---

## Pipeline structure

### The stage graph

From `agents_pipeline/README.md` and `runner.py`, retained under `agent-work/sources/lait/repo/`:

1. **`style_analysis`** — once per run. Reads the full source excerpt, writes
   `outputs/style_bible.json`.
2. **Local chunk loop**, `max_cycles` 2 or 3 (Table 8: 18 runs at 2, 17 at 3). Cycle 1
   runs `translate` on every chunk; later cycles run `revise` on failing chunks only.
   Every cycle then runs `litrans_review` (25 yes/no/maybe questions; pass needs zero NO
   and at most five MAYBE) and `chunk_literary_review` (four lenses, pass needs no MEDIUM+
   finding) on that chunk. `master_chunk_gate` combines them and is code, not an agent job.
3. **Global excerpt loop**, `max_global_cycles` 2. Each cycle reconstructs the draft and
   runs `book_review` and `cross_chunk_audit`. If MEDIUM+ findings remain and a cycle is
   left, `final_revise` runs on the affected chunks and the loop repeats; if the cycle
   limit is reached the run is written FAIL and stops, so no `final_revise` follows the
   last global review.

Chunking is `tiktoken` `o200k_base`, paragraph-preserving, 1,000-token target, with an
oversized paragraph kept whole. Boundary context is ~200 tokens per side, taken as whole
paragraphs (`_BOUNDARY_CONTEXT_TOKENS = 200` in `runner.py`).

### The run inventory is public even though the runs are not

`docs/release/withheld-files.tsv` lists the path of every one of the 8,066 files removed
from the public branch, including the entire contents of the 35 run workspaces. Two path
families are directly countable:

- `runs/<run>/inputs/source_chunk_NNNN.txt` — one per source chunk entering the pipeline.
- `runs/<run>/manifests/<stage>_<book>[_chunk_NNNN]_cycle_NN.json` — one per agent job,
  written by `_write_manifest` in `core/executor.py`, carrying stage, chunk and cycle in
  the filename.

So the workload structure does not have to be inferred. `research/lait/compute_lait.py`
counts it from the retained copy at
`agent-work/sources/lait/repo/docs-release-withheld-files.tsv`, and the corpus totals reproduce
Table 9 exactly:

| Check | From the manifest | Published |
|---|---:|---:|
| Completed runs | 35 | 35 |
| Source chunks | 441 | 441 |
| Runs with `metrics/run_summary.json` | 31 | 31 |

The 15 main-evaluation runs are identified by matching Appendix A's book list to run
directories; the same 15 slugs are the only files in `books/MT_chunks/`.

### Measured workload, 15 evaluation runs

| Stage | Model | Jobs, 15 runs | Per book |
|---|---|---:|---:|
| `style_analysis` | Opus 4.6 | 15 | 1.00 |
| `translate` | GPT-5.4 | 217 | 14.47 |
| `litrans_review` | GPT-5.4 | 446 | 29.73 |
| `chunk_literary_review` | Opus 4.6 | 446 | 29.73 |
| `revise` | GPT-5.4 | 229 | 15.27 |
| `book_review` | GPT-5.4 | 27 | 1.80 |
| `cross_chunk_audit` | GPT-5.4 | 27 | 1.80 |
| `final_revise` | Opus 4.6 | 42 | 2.80 |
| **Total** | | **1,449** | **96.60** |

217 source chunks over 15 books, **14.47 per book**, range 12 to 17, which at 13,026
source tokens is 900 tokens per chunk — a 90% fill of the 1,000-token limit under
paragraph-preserving packing.

Three things fall out of the cycle breakdown that the paper does not state:

- **Every chunk failed the first local gate.** `translate` runs 217 times at cycle 1 and
  `revise` runs 217 times at cycle 2 — all of them. Only 12 chunks reached a third cycle.
  The chunk-level acceptance gate essentially never passes on the first attempt, so
  "up to three local cycles" is in practice exactly two.
- **12 of the 15 evaluation runs used both global cycles**; 3 passed at the first.
- **Re-executions are quantified, and they are not retries.** The 31 logged runs hold 2,723
  distinct job manifests against the 2,930 job-metric records the paper reports: **207
  excess records, 7.07% of records and 7.60% of distinct jobs.** They cannot be in-loop
  retries. `_run_job` in `core/executor.py` calls `_write_manifest` once *before* its
  `while True` loop and calls `append_job_metric` exactly once, at whichever of its three
  terminal points it reaches — success, quota-pause abort, or a non-retryable or
  retries-exhausted `PipelineError`. A retry `continue`s the loop without writing anything
  and survives only as `attempt_count` and `quota_pause_count` on that single record. The
  19 failed jobs likewise each have one manifest and one record. So every excess record is
  a **second full `_run_job` invocation under the same `job_id`**, overwriting the same
  manifest filename — the `ResumePoint` restart path in `core/job_spec.py`. Each one cost a
  full job's compute, which fixes the retry uplift at 7.60% rather than leaving it a guess.

One discrepancy, with a lead rather than a resolution: `translate` + `revise` + `final_revise`
manifests across all 35 runs is 1,078, against Table 9's 1,059 chunk-cycle artifacts. The
difference is 19, which is exactly Table 9's count of failed agent jobs — and
`_write_manifest` runs before execution, so a job that fails leaves a manifest and no
artifact, which is the shape of a manifest-minus-artifact gap. It cannot be proved from
public files because the failures are not stage-attributed. It is consistent with the
re-execution finding above: the 19 failures sit inside the 2,723 manifests, which is why
they cannot be part of the 207 excess records. Nothing in this row depends on the 1,059.

---

## Compute

`compute_method` is `params_tokens`: tokens times each model's `flops_per_token`, with the
per-model split in `compute_source`. `compute_evidence` is `derived_assumed_inputs` —
structure measured, tokens per job modelled. The full derivation is
`research/lait/compute_lait.py`, whose output is `agent-work/derived/lait/lait-calculations.json`;
it takes explicit source, prompt, model-CSV, withheld-manifest and output paths and reads
nothing else.

### What an agent job costs

Each job is one invocation of a coding-agent CLI, not one API call.
`_build_claude_exec_cmd` in `executor.py` runs `claude --effort max --bare --output-format
stream-json --verbose --no-session-persistence --tools Read,Write --allowedTools
Read,Write`; `_build_codex_exec_cmd` runs `codex exec
--dangerously-bypass-approvals-and-sandbox --skip-git-repo-check --json` at `xhigh`. The
agent then reads files, reasons, and writes a JSON output file, so one job is a short
multi-turn conversation.

Four components per job, three of them modelled:

| Component | Basis |
|---|---|
| Harness prefix (system prompt plus tool schemas) | Assumed, 3,500 tokens central, 1,500–8,000 |
| Prompt template | **Measured** from the retained prompt files with `o200k_base` |
| Substituted content and file reads | Derived from Table 1 quantities and the prompt and runner code |
| Reasoning and written output | Assumed per stage, swept 0.5x to 2x |

Measured template sizes, placeholders removed: `style_analysis` 580, `translate` 394,
`litrans_review` 1,020, `chunk_literary_review` 1,051, `revise` 387, `book_review` 822,
`cross_chunk_audit` 799, `final_revise` 454.

The substituted content follows the templates exactly. `translate` carries the source
chunk (900) plus both source boundary contexts inline and reads the style bible.
`litrans_review` carries source chunk, translation (662) and four boundary contexts inline
and reads nothing. `chunk_literary_review` is the same plus the style bible. `revise` adds
the failed questions and the literary findings. `book_review` and `cross_chunk_audit` read
the reconstructed draft (9,582), the style bible and the source chunks. `final_revise`
reads the full source (13,026), the full draft and the style bible.

**Cache accounting.** Both CLIs use provider prompt caching, so within a job each token of
the conversation is written to cache about once and read many times; the dataset counts
fresh input and cache creation and excludes cache reads. Counted tokens per job are
therefore the distinct conversation content once on the input side, plus the generated
tokens twice — once as generation and once as the re-entry of the assistant's own output
into the next turn's prefix, which is `DECISIONS.md`'s rule and the accepted Portal
convention. `tokens_accounting` is `input_cache_creation_output`.

### Result

Counted tokens before the retry uplift, per evaluation book:

| Stage | Model | Jobs | Distinct input per job | Generated per job | Counted tokens | Share |
|---|---|---:|---:|---:|---:|---:|
| style_analysis | Opus 4.6 | 1.00 | 17166 | 7560 | 32300 | 2.0 |
| translate | GPT-5.4 | 14.47 | 6794 | 3222 | 191500 | 11.9 |
| litrans_review | GPT-5.4 | 29.73 | 6963 | 3760 | 430600 | 26.7 |
| chunk_literary_review | Opus 4.6 | 29.73 | 8554 | 3660 | 472000 | 29.2 |
| revise | GPT-5.4 | 15.27 | 8640 | 3222 | 230300 | 14.3 |
| book_review | GPT-5.4 | 1.80 | 29390 | 6960 | 78000 | 4.8 |
| cross_chunk_audit | GPT-5.4 | 1.80 | 29367 | 5760 | 73600 | 4.6 |
| final_revise | Opus 4.6 | 2.80 | 30305 | 3812 | 106200 | 6.6 |
| **Subtotal** | | **96.60** | | | **1614500** | |

The 7.60% re-execution uplift brings that to **1,737,000 counted tokens per evaluation
book**, of which Claude Opus 4.6 657,000 and GPT-5.4 1,080,000. Both coefficients are
2.0e11 FLOPs per token, so

**compute_flops = 1.737e6 x 2.0e11 = 3.474e17 FLOPs per evaluation book.**

The two chunk-level review stages are 54% of it. All four review and audit stages together
are 63%, against 31% for the three stages that draft and revise the translation. That is
the shape of the result worth remembering: **this pipeline spends twice as much compute
judging its translation as producing it**, and the single largest line is the literary
review of chunks that have already been reviewed once.

### Range and scenarios

Every assumption is swept over its declared low/central/high levels, 729 grid points:

| | FLOPs |
|---|---|
| Grid minimum | 1.92e17 |
| 10th percentile | 2.32e17 |
| Central | 3.47e17 |
| 90th percentile | 4.71e17 |
| Grid maximum | 5.86e17 |

One-at-a-time sensitivity, high over low: reasoning volume 1.65x, harness prefix size
1.44x, harness cache reuse across jobs 1.24x, style-bible size 1.10x, re-execution uplift
1.04x, how much of the source the global reviews read 1.02x. **The answer is driven by two
assumptions about the agent scaffold and one about reasoning effort, not by anything
specific to translation.**

Two of those deserve a sentence each rather than a number.

- **`harness_cache_reuse` is set to the conservative side on purpose.** The central charges
  the harness prefix to every job. The implementation evidence points the other way —
  `runner.py`'s documented invocation uses `--max_parallel_jobs 4` and dispatches same-stage
  jobs in back-to-back batches, comfortably inside a five-minute provider cache TTL, so
  identical prefixes after the first batch should be cache reads. What is not observable
  from public code is whether subscription-mode access caches the same way as API access,
  and the excess-record finding above shows runs were restarted, which breaks TTL
  continuity. The low leg, 2.81e17 (0.81x), is the reuse case and the range carries it.
- **Reasoning tokens are counted twice**, like every other generated token: once as
  generation and once as re-entry. That is 309,000 of the 1,737,000 counted tokens, 17.8%.
  It is deliberate — Codex passes reasoning items back through the Responses API across
  tool calls within a turn sequence, and Claude preserves thinking blocks when tool results
  follow inside one job — but a reader who assumed reasoning is dropped between turns would
  read 2.86e17 (0.82x), which is inside the range.

Named scenarios outside the grid:

| Scenario | FLOPs | Ratio to central |
|---|---|---|
| Output-only floor: generated tokens alone | 7.70e16 | 0.22 |
| No prefix caching: every turn re-processes the prefix | 5.94e17 | 1.71 |
| 30B active parameters instead of 100B | 1.04e17 | 0.30 |
| 300B active parameters instead of 100B | 1.04e18 | 3.00 |

The no-caching scenario sits just above the grid's upper end, so the stated range **1.9e17
to 5.9e17** is a parameter range and the no-caching case is 1.3% outside it. The active-parameter prior is a dataset-wide assumption under separate
review and is not folded into the range.

**Cached-context attention.** The parameter term stays on the `2 x active_parameters`
convention and the attention term, since folded into `compute_flops` by
`research/attention-correction.md`, is priced here. At
`4 x layers x d_model x context_positions` per position, summed as a causal triangle over
each job's own conversation, with a token-weighted mean context of 15,852:

| Assumed shape | Attention FLOPs | Ratio to 3.47e17 |
|---|---|---|
| L=64, d_model=8192 | 2.25e16 | 0.065 |
| L=80, d_model=10240 | 3.51e16 | 0.101 |
| L=96, d_model=12288 | 5.06e16 | 0.146 |

A 6.5–15% one-sided understatement, far smaller than the Portal row's 1.4–3.1x, because
LAIT's jobs are 97 short conversations rather than one long one. It does not change the
row.

### Two independent checks

**The transfer anchor.** `DECISIONS.md` sets k = 1 + r = 5.2 total counted tokens per
generated token (band 4.5–6.3), transferred from Meta FAIR's textbook run, and notes that
the anchor is an upper one for long-output harnesses because Meta's agents were
short-output and file-read-heavy. This reconstruction gives **k = 4.52**, at the bottom of
the band, in the direction the decision predicts: LAIT's jobs write literary prose and
structured review JSON rather than reading many files. Applying k = 5.2 to the modelled
output instead would give 2.00e6 tokens and 4.00e17 FLOPs, 1.15x central and inside the
range. This is the check that carries weight.

**List prices against the subscription — a weak check, offered as one.** Nothing in the
token model uses the $400. Pricing the modelled workload at the two models' list rates —
Opus 4.6 at $5/$25 per MTok, GPT-5.4 at $2.50/$15, from
`agent-work/sources/lait/model-list-prices-2026-09-13.md`, with re-entered output billed as input —
gives **$11.82 per evaluation book and $360 for all 35 runs, against the $400 the authors
paid**. Do not read that as agreement. A subscription is not a budget constraint on token
value: it exists to deliver list-price tokens worth several times its fee, so the $400
bounds nothing tighter than an order of magnitude, and it also covered the five-way
development comparison and the GPT-5.4 comment coding. The check rules out a model that is
10x too large or 10x too small, and nothing finer. In particular it does not license any
claim about what the authors' API bill would have been, and it does not sit in tension with
their "prohibitively expensive" — a reconstruction is not a measurement.

---

## Human time

No timing evidence exists for these books or these translators. The transfer donor is
Toral A, Wieling M, Way A, *Post-editing Effort of a Novel With Statistical and Neural
Machine Translation*, Frontiers in Digital Humanities 5:9, 2018, retained at
`agent-work/sources/lait/toral-2018-frontiers-text.txt` with the checked extracts at
`agent-work/sources/lait/toral-2018-extract.md`. It is the one keystroke-logged study of literary
translation productivity.

What it measured, verified against the text:

- Chapter 1 of *Warbreaker*, 3,743 English words in 330 sentences, split into 33 jobs of
  10 consecutive sentences, translated into Catalan.
- Six professional translators with previous experience in literary translation. Each
  translated 11 jobs from scratch (HT), 11 post-editing PBMT and 11 post-editing NMT, so
  the from-scratch condition has **66 job-level attempts** over 660 timed sentences.
- Per-sentence time and keystrokes logged in a CAT environment.
- **503 words per hour from scratch**, against 594 post-editing PBMT and 685 post-editing
  NMT. Per-translator spread 402 (T3, from scratch) to 1,140 (T2, post-editing NMT).
- The guidelines *"state that the aim is to achieve publishable professional quality
  translations, both for translations from scratch and for post-editing"*.

**7,623 words / 503 words per hour = 15.16 h = 54,558 seconds is the first pass.** The
deliverable is a publishable translation, so `human_time` adds one self-revision pass at
three times drafting speed: **20.2 h = 72,744 seconds**, with the 54,558 s first pass as
`human_time_low`. The reasoning is in the scenarios table below.

### What the rate covers and what it does not

The rate covers first-pass production of a publishable-quality translation, sentence by
sentence in a CAT tool, and nothing else. A published literary translation adds at least:
the translator's own revision passes over a full draft; reading the whole book before and
during translation; correspondence with author, editor and copy-editor; and a copy-editing
and proofreading round the AI side has no counterpart for. It also subtracts something: the
experimental translators had no whole-book context and were working sentence-locked, which
is slower per word than a translator with the book in hand.

Two further transfer gaps. The direction is English→Catalan, closely related languages,
against LAIT's French, Polish and Japanese→English; Japanese in particular is typologically
distant and slower per delivered word. And the paper reports "words per hour" following
Plitt & Masselot, i.e. source words, while LAIT's 7,623 is target words; for
English→Catalan the two differ by under ~10%, so this moves the answer less than the other
gaps.

Scenarios, all in `lait-calculations.json`:

| Scenario | Hours | Seconds |
|---|---:|---:|
| Slowest donor translator from scratch, 402 words/hour | 19.0 | 68266 |
| Low: donor mean 503 words/hour, first pass only | 15.2 | 54558 |
| **Central: plus one self-revision pass at 3x drafting speed** | **20.2** | **72744** |
| Plus revision and editorial response at 2x drafting speed | 22.7 | 81837 |
| Trade guidance for creative work, 250 words/hour | 30.5 | 109771 |
| Trade guidance for creative work, 125 words/hour | 61.0 | 219542 |

The deliverable is a publishable literary translation, and a first pass at the donor mean is
a draft rather than that. The central therefore moves up one row of this table, to the donor
mean plus one self-revision pass at three times drafting speed: **20.2 hours, 72,744 s**.
`human_time_low` is the first-pass-only transfer, 54,558 s, which is what the donor timings
actually measure and is the case where the first pass needs no revision. `human_time_high`
stays at the 219,542 s of the 125-words-an-hour trade guidance. A reviewer who thinks the row should also carry the
editorial response should read 22.7 hours instead, which moves FLOPs per human-second from
4.8e12 to about 4.2e12.

### Field values

`human_time_evidence = transferred_timings`; `human_time_method = estimated`, following
both `AGENTS.md` ("transfers to a different population are estimated") and the dataset's
own practice, where 81 `transferred_timings` rows never use `work_rate` and 69 use
`estimated` with `point_estimate` and `all`. `human_time_statistic = point_estimate`;
`human_time_subset = all` (all 66 donor from-scratch jobs, none excluded);
`human_attempts = 66`. `human_skill = expert`; `human_time_scope = task_performance`.

The reader-side timing in the paper — $110 per book for *"approximately 4h per book"* of
reading and annotation — is not a candidate donor. It is the cost of *evaluating* two
translations, not of producing one.

---

## Performance

| Measure | HT | MT | n | p |
|---|---:|---:|---:|---:|
| Excerpt-level preference | 19 | 11 | 30 | .148 |
| Excerpt-level clear preference | 16 | 7 | 30 | — |
| Chunk-level preference | 522 | 250 | 772 | .011 |
| Chunk-level strong preference | 205 | 54 | 772 | — |
| Acceptability as a published translation, odds ratio | 4.0 | — | 60 | .0069 |
| Smoothness, odds ratio | 4.3 | — | 60 | .0029 |
| Immersion and willingness to continue, odds ratio | favours HT | — | 60 | n.s. |
| Positive highlighted words per 1K | 107.8 | 68.5 | 772 | <.001 |
| Negative highlighted words per 1K | 42.9 | 100.7 | 772 | <.001 |
| MT identified correctly, direct comparison | — | 17 | 30 | .585 |
| MT identified correctly, single reading | — | 34 | 60 | .413 |

### `below`, and why not `match`

The case for `match` is real and should be stated first. Readers could not identify the
machine translation above chance, either after reading one version (34/60) or after
reading both (17/30). The excerpt-level preference, which is the condition closest to
reading a book, was 19–11 and not significant. 54% of MT readings drew a 4 or 5 for
willingness to keep reading, against 66% for HT. A third of chunk judgments went to MT,
stable across all three source languages. One book's MT was preferred 88% of the time. And
every automatic metric tested — MetricX-QE, COMETKiwi and LiTransProQA with Gemini 3.1 Pro
as judge — preferred MT to the published human translation.

It still fails `match`, and not because one condition is picked over another. **Every
preference measure in the study points the same way.** Excerpt level: 19–11, order-adjusted
HT probability 63.4%. Chunk level: 522–250, 76.2%, p=.011. Acceptability as a published
translation: 4.0x odds, p=.0069. Smoothness: 4.3x, p=.0029. Immersion and
willingness-to-continue: favour HT, not significant. Span annotations: HT nets more positive
and less negative evidence, and the net span score predicts the stated preference in 691 of
755 non-tied judgments. The excerpt-level result is directionally identical to the
chunk-level one and merely underpowered at n=30; "broadly comparable" would require some
measure that does not favour the human translation, and there is none.

Undetectability is a different construct. Readers preferred whichever version they believed
was human in 28 of 30 comparisons, so the detection null says they had no reliable cue for
*origin*, not that the two are equal in quality.

`performance_vs_human = below`. The margin is narrow, and the paper designates no primary
condition — it reports both and calls close reading the clearer one.

### Comparison issues

`different_inputs_or_tools; different_human_baseline`.

- **`different_inputs_or_tools`.** The pipeline saw only the ~8,000-word excerpt. The
  professional translator had the whole novel, and produced this passage as part of
  translating all of it, with whole-book knowledge of voice, foreshadowing and terminology
  available from the first page. The authors flag the same asymmetry from the other side
  under "Excerpt scope": *"book-spanning context and background may be lost by LLM
  translations of full books"*. The published translation also passed through editorial
  revision and copy-editing; the MT was delivered unedited.
- **`different_human_baseline`.** The performance baseline is the work of the books'
  published translators (Bill Johnston, Antonia Lloyd-Jones, Tina Kover, Jim Rion, Polly
  Barton and others). The timing baseline is six Catalan literary translators on an English
  fantasy novel in 2018. Different people, different language pairs, different decade.

Not flagged, and why:

- **`different_assessment`** does not apply: both versions were judged by the same 15
  readers under the same protocol, in a counterbalanced within-subjects design. That the
  readers are avid readers rather than professional reviewers or translators is a property
  of the assessment as a whole, not a difference between the two sides, and it belongs in
  `notes` — which it gets.
- **`different_task`** does not apply: both sides rendered the same source passage into the
  same target language at the same length.
- **`different_attempt_selection`** does not apply: all 15 evaluation runs were evaluated
  regardless of gate verdict.

---

## Row

`lang-lait-novel-opening-gpt54`, in `candidates/lait/points.csv`. Checked against the 1,495
existing point IDs across `../AI Compute vs Human Time/dataset/points.csv` and this
folder's `points.csv`; the `lang-` prefix follows `lang-translate-zhen-microsoft-combo6`
and `lang-translate-chat-nllb33b-en-nl`.

| Field | Value |
|---|---|
| `task_category` | `writing_media` (COLUMNS: "includes translation and summarization of supplied material") |
| `model_id` | `gpt-5.4-2026-03-05` |
| `compute_scope` | `inference` |
| `compute_flops` | 3.474e17 |
| `tokens` | 1737000 |
| `tokens_accounting` | `input_cache_creation_output` |
| `compute_method` | `params_tokens` |
| `compute_evidence` | `derived_assumed_inputs` |
| `compute_statistic` | `mean` |
| `compute_subset` | `all` |
| `ai_attempts` | 15 |
| `human_skill` | `expert` |
| `human_time_scope` | `task_performance` |
| `human_time` | 72744 |
| `human_time_evidence` | `transferred_timings` |
| `human_time_method` | `estimated` |
| `human_time_statistic` | `point_estimate` |
| `human_time_subset` | `all` |
| `human_attempts` | 66 |
| `performance_vs_human` | `below` |
| `comparison_issues` | `different_inputs_or_tools; different_human_baseline` |

Implied ratio: **6.4e12 FLOPs per human-second**, range 3.5e12 to 1.1e13 on the compute
grid alone, or 2.3e12 to 1.1e13 once the human revision scenarios are allowed.

`candidates/lait/models.csv` is headers only: both models already exist canonically in
`../AI Compute vs Human Time/dataset/models.csv` with `flops_per_token` 2.0e11 and
`active_parameters` 1.0e11 `estimated`, and this row uses them unchanged.

---

## TransLaw disposition

Xuan H, Kit C, *TransLaw*, arXiv:2507.00875v2, 29 January 2026. Retained at
`agent-work/sources/lait/translaw-2507.00875v2-text.txt`, with the cost passage and the floor
arithmetic at `agent-work/sources/lait/translaw-cost-extract.md`. **No row drafted.**

The study is otherwise attractive: one real deliverable (HKCFA judgment FACC No. 1 of 2021,
11,585 English words / 12,029 English tokens → 19,478 Chinese tokens, 200 paragraph
pairs), a genuine professional baseline (the official Hong Kong government bilingual
translation), and 10 certified professional legal translators scoring both on accuracy,
coherence and cohesion, and style. Seven role-based GPT-4o agents.

The compute evidence fails `DECISIONS.md`'s cost-only test, which requires an explicit
cost-to-token conversion using documented prices at the run date. All three parts fail, and
the third is disqualifying on its own:

1. **No price date and no snapshot.** The paper never dates its runs and Table 6 records
   GPT-4o only as `Size N/A, Seq_len 8192, API`, with no snapshot string anywhere in the
   paper. The same table lists DeepSeek-V3 as 16B and DeepSeek-R1 as 32B against their
   published 671B MoE, so the model metadata is not reliable enough to pin a price. (The
   8,192 is a uniform run setting across every row of that table, not a claimed context
   window, so it carries no weight on its own.) Between `gpt-4o-2024-05-13` ($5/$15 per
   MTok) and `gpt-4o-2024-08-06` ($2.50/$10) the conversion moves 2x.
2. **No input/output split** for a seven-agent pipeline, which is the parameter the
   conversion turns on.
3. **The figure is below the arithmetic floor for its own deliverable.** At
   `gpt-4o-2024-08-06` prices the cheapest possible run that emits the 19,478 Chinese
   tokens once and reads the 12,029 English tokens once costs 19,478 x $10/MTok + 12,029 x
   $2.50/MTok = **$0.225**. The reported US$0.35 leaves $0.125 for a legal-terminology
   parsing agent, a semantic-alignment reviewer, a terminology reviewer, a citation
   reviewer, a style reviewer and a command module. At the earlier snapshot's prices the
   floor alone is $0.352, above the reported total. And the paper reports the seven-agent
   system as *cheaper* than a single-agent GPT-4o pass on the same text ($0.35 against
   $0.39, "10.26%" saving), which cannot be true of a strict superset of the work.

The human side is a **price, not a duration**: US$1,390.20 at the ATA's recommended
US$0.12-per-word minimum. Converting it to active hours needs an hourly rate the paper does
not state, and a per-word agency price includes overhead and margin, so the conversion is
unanchored. It could be avoided — applying a throughput rate directly to 11,585 words gives
23 hours at the Toral 503 words/hour transfer or 39 hours at a 300-words/hour
legal-translation rate — but the compute side fails regardless, so the question is moot.

**Reconsider if** the authors publish token counts or a dated per-agent cost breakdown. The
performance and human-baseline sides are strong enough that the row would be worth
building.

---

## Other leads from the scouting inventory

Reconciled against `research/scouting/book-length-text.md` so the source collection is not
re-searched:

| Lead | Disposition |
|---|---|
| LAIT 15 evaluation books | **One aggregate row**, above |
| LAIT 4 multilingual case-study runs | Not drafted; one reader each, no aligned close reading, different output geometry |
| LAIT 16 development books | Not drafted; no reader evaluation, and the five-way rater comparison is a pipeline selection, not a human baseline |
| TransLaw | **No row**; compute fails the cost-only test |
| TransLaw single-agent GPT-4o configuration | No row; same failure, and the $0.39 is subject to the same floor argument |
| AutoFiction, GlobeScribe, Nuanxed, HarperCollins France | No published methodology or quality data |
| SwiLTra-Bench, SEGALE, LITEVAL-CORPUS, DITING, WebNovelBench | Wrong work unit (paragraph, chapter or sentence), or no matched human deliverable |
| "Towards Human-Level Book-Writing Capability" | No token counts, no human evaluation |
