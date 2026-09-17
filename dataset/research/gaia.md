# GAIA validation questions against HAL agent traces

*Created 2026-09-13 13:25.*
*Revision 1, 2026-09-13 14:22, on the independent review at `reviews/gaia-independent.md`;
changes logged in `candidates/gaia/REVISION.md`.*

## Summary

Fifty-seven candidate rows pair the GAIA validation set's per-question annotator
solve times with per-question token usage recovered from the Holistic Agent
Leaderboard's published agent traces. One row is one GAIA validation question at
one difficulty level, answered by one (agent, model, reasoning-effort)
configuration. Human time is the arithmetic mean of the annotators' own recorded
solve times for that level: **403.02 s at Level 1, 685.12 s at Level 2, 1232.31 s
at Level 3**. AI compute runs **5.63e14 to 4.91e17 FLOPs per question**, a factor
of 870 across twelve models, twenty-four configurations and two agent scaffolds,
all in 2025.

Both sides are measured rather than estimated. The human times are the values
GAIA's annotators wrote into the `How long did this take?` field of every
validation question; the paper's own Level-1 mean, 6.8 minutes over the full
466-question set, is within 1.3% of the 403.02 s this note computes from the 53
released Level-1 questions. The token counts come from provider usage counters
recorded per LLM call by Weave and keyed to the GAIA task id, so every model call
in a run is attributable to the question that caused it. What is assumed is the
active-parameter count behind each `flops_per_token`, which is grade C for every
closed model here and under separate review.

Three findings shape the compute numbers, and each is stated in the rows it
affects.

**HAL logs every call routed through Weave's OpenAI-client patch twice**, once as
a `litellm.completion` parent span and once as its
`openai.chat.completions.create` child carrying the identical usage block. HAL's
own `total_usage` and `total_cost` sum both, so the leaderboard's published token
and dollar figures are doubled for those runs, and so was the first submission of
these rows. The reduction now counts a span only when no usage-bearing span names
it as parent, which halves every OpenAI, Together and Gemini figure and leaves
the Anthropic-native and OpenRouter records, which are leaves, untouched.

**HAL sets no `cache_control` anywhere in either agent**, so on the Anthropic path
no prompt caching could occur and every call re-processed its whole prefix: those
rows' compute was spent, but harness re-processing rather than task difficulty
sets its size. The OpenAI runs cached automatically, at 11% to 77% of prompt
tokens, and those rows exclude cache reads per the dataset's rule.

**The Open Deep Research scaffold's GPT-4o image tool posts directly to the
OpenAI HTTP API**, outside the traced client, so its tokens are missing from the
nine Open Deep Research configurations. The same helper reaches 0.4% of counted
tokens where it is traced, so the omission is small and one-sided.

Every row is labeled `below`. The best configuration here, Claude Sonnet 4.5 in
the HAL Generalist Agent, answers 81.1% of Level 1 against 93.9% for GAIA's human
annotators; the weakest retained row is at 0.40 of the human rate. Eleven of the
57 are kept under the close-calls ruling rather than by clearing the half-of-human
guide outright, and are named in [Dispositions](#dispositions) along with the 36
cells and six runs that did not become rows.

**A reviewer should look first at**: the close-calls count, which is eleven rather
than the six the independent review enumerated; the retention bar's selection
effect across levels; the claim that the timing sample and the performance sample
are different humans; and the active-parameter priors, which scale every
`compute_flops` linearly.

## The source

[GAIA](https://arxiv.org/abs/2311.12983) (Mialon, Fourrier, Swift, Wolf, LeCun,
Scialom; submitted 2023-11-21) is 466 hand-written questions for a general AI
assistant. Each has a short factual answer that is, by design, absent in plain
text from the web, so answering requires executing a sequence of steps: web
search, page reading, file inspection, arithmetic. The authors release the
answers to one split and hold the rest back for a leaderboard. The released
validation split, used here, is 165 questions: 53 Level 1, 86 Level 2, 26 Level
3, with 38 carrying an attached file.

Levels are assigned from the effort the question's own annotator needed. Level 1
generally took no tool or one tool and at most 5 steps; Level 2 roughly 5 to 10
steps and several tools; Level 3 long step sequences and arbitrary tool
combinations. The paper is explicit that this is a proxy: "we rely as a proxy on
the number of steps and tools used by our annotators when crafting the
questions".

Scoring is a quasi-exact match of the model's final answer against the reference,
normalized by answer type, with a fixed prefix prompt telling the system to end
with `FINAL ANSWER:`. There are no answer options, so the chance floor is zero
and no floor subtraction enters any label decision here.

The validation metadata was downloaded by Damon from the gated
[gaia-benchmark/GAIA](https://huggingface.co/datasets/gaia-benchmark/GAIA)
dataset and placed at `agent-work/sources/inbox/gaia/2023/validation/metadata.parquet`. That
file is read, never modified; `agent-work/sources/gaia/gaia-validation-annotator-times.csv`
is the extract this note uses.

## Human time

### What was recorded

Every validation question carries an `Annotator Metadata` block written by the
person who created it, with the search path they followed, the number of steps,
the tools they used, and a free-text answer to `How long did this take?`. The
annotators were also asked to answer the questions they created, so the recorded
duration is that person's own solve, timed against the path they had just worked
out, with an ordinary web browser and whatever software the question needed.

This is a self-report, not a stopwatch trace, and the free text shows it: 150 of
165 values are a round number of minutes. It is nonetheless a recorded timing for
the stated task and population, so `human_time_evidence = task_timings`, and the
substantive step is averaging raw observations, so `human_time_method =
other_calculation` per `DECISIONS.md`. No attempts are excluded from the average,
so `human_time_subset = all` and `human_attempts` is the level's question count.

`human_skill = typical`. The paper describes the annotators as non-experts and
treats their near-perfect score as evidence that "GAIA is simple for non
experts". They were recruited and instructed for the annotation job, but not
selected for any task-specific skill.

### Parsing the free text

`research/gaia/parse_annotator_times.py` converts all 165 strings to seconds
under six rules, recording the rule in the output CSV so any of them can be
re-decided:

| Rule | Form | Reading | n |
|---|---|---|---:|
| plain | `5 minutes`, `20 Minutes`, `30 minutes.` | the stated number | 150 |
| range | `5-10 minutes` | midpoint of the range | 10 |
| bare | `6`, `10` | read as minutes | 2 |
| seconds | `30 seconds` | the stated number | 1 |
| under | `<1 minute` | 30 s, midpoint of 0–60 | 1 |
| few | `a few minutes at most` | 180 s, "a few" is 3 | 1 |

Fourteen values involve judgment. Pushing every one of them to the low end of its
plausible reading and then to the high end moves the level means by at most 3.5%:
Level 1 389.0 to 417.2 s against a central 403.0, Level 2 671.2 to 699.1 against
685.1, Level 3 unchanged at 1232.3 (its two judgment values are bare numbers,
read as minutes either way). The parse is not a material source of uncertainty.

### The resulting statistics

| Level | n | Mean s | Median s | Min s | Max s | With a file |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 53 | 403.02 | 300 | 30 | 1800 | 11 |
| 2 | 86 | 685.12 | 450 | 60 | 3900 | 20 |
| 3 | 26 | 1232.31 | 900 | 360 | 3600 | 7 |
| all | 165 | 680.73 | 480 | 30 | 3900 | 38 |

The mean is used, per the dataset's stated preference. The distributions are
right-skewed, so the medians are lower throughout.

**Cross-check against the paper.** GAIA's Table 4 reports mean annotator time to
answer over all 466 questions: 6.8, 10.5 and 17.7 minutes for Levels 1, 2 and 3,
that is 408, 630 and 1062 s. The figures above are computed by the same method
over the 165 released questions and land at 403, 685 and 1232 s. Level 1 agrees
to 1%; Levels 2 and 3 are 9% and 16% higher here, which is what a 165-question
subsample of a 466-question pool can do at these sample sizes. The agreement
confirms that the field parsed here is the one the paper averaged.

### One-sided biases in the human number

Two work in opposite directions and neither is corrected.

The annotator was the question's designer. They had just established where the
answer lived and which path reached it, and the recorded time is a solve along
that known path. A fresh solver handed only the question would generally take
longer, so **403/685/1232 s understates a naive human**. This is the larger of
the two and is stated in every row's notes.

Against that, the questions were written under an instruction to "make sure your
question can be answered in a reasonable amount of time by a human annotator",
which truncates the upper tail of the task distribution that GAIA contains at
all. That affects what GAIA is, not what the annotators' times mean.

## Human performance

GAIA's human score is 92% aggregated, and per level 93.9%, 91.8% and 87.3%
(Table 4; Table 3 rounds these to 94/92/87). It is the share of correct answers
given by two fresh validating annotators per question, over 623 newly crafted
questions, computed on their 1,246 annotations and restricted to questions that
passed validation.

Three things follow for the rows.

First, **the timing sample and the performance sample are different people**. The
times come from question designers; the score comes from validators who answered
a finished question they had not written. This is a material asymmetry in the
comparison, flagged as `different_human_baseline`.

Second, **the human score is measured on a different set of questions** than the
165 the rows describe: the 623-question validation pool, not the released split.
Along with the difference between validator agreement and GAIA's automated
quasi-exact-match scorer, this is flagged as `different_assessment`.

Third, **the human tool set is not the agent's**. The annotators used an ordinary
graphical browser with images, video and JavaScript, and whatever application a
given file needed. The agents get a text-mode browser or a page-to-markdown
converter, a search API, a Python interpreter and a file-to-markdown reader. This
cuts both ways: the human browser is richer, and the agent's Python interpreter
is faster than hand arithmetic. Flagged as `different_inputs_or_tools`.

## The compute side

### HAL traces

[HAL](https://hal.cs.princeton.edu), the Holistic Agent Leaderboard, publishes
one encrypted zip per evaluation run at
[agent-evals/hal_traces](https://huggingface.co/datasets/agent-evals/hal_traces),
ungated, last modified 2026-02-01. The repository holds 381 files, 379 of them
`_UPLOAD.zip`, and 37 of those are GAIA runs, 16.1 GB in total. Each decrypts to
a JSON with `config`, `results`, `raw_eval_results` (per-task score),
`raw_logging_results` (every traced span), `total_usage`, `total_cost` and
`git_info`.

The encryption is not a barrier and is not meant to be one: HAL's own harness
publishes the password in
[`hal/utils/decrypt.py`](https://github.com/princeton-pli/hal-harness/blob/main/hal/utils/decrypt.py)
as `JsonEncryption("hal1234", salt=salt_bytes)`, with a PBKDF2-HMAC-SHA256 key
derivation at 480,000 iterations and a Fernet cipher.
`research/gaia/decrypt_hal_zip.py` reimplements exactly that.

Thirty-five runs were retrieved, decrypted and reduced to per-question usage by
`research/gaia/fetch_hal_gaia.py`; the summaries are retained in
`agent-work/sources/gaia/hal-run-summaries/`, one small JSON per run, and are what every
number below is computed from. Two runs were skipped, both 2 GB uploads whose
decrypted plaintext does not fit in memory on the machine used; see
[Dispositions](#dispositions).

### Every OpenAI-path call is logged twice

This is the correction that drove Revision 1, and it is the single most important
thing to understand about these numbers.

A GAIA agent call reaches the provider through litellm. Weave traces the litellm
call as a `litellm.completion` span, and where litellm dispatches through the
OpenAI Python client—which it does for OpenAI itself, for Together, for Gemini's
OpenAI-compatible endpoint, and for the GPT-4o image helper—Weave's client patch
traces the inner request as an `openai.chat.completions.create` child. Both spans
carry the same `weave_task_id` and the **same usage block**, one API response
counted twice. On the Anthropic path, native or through OpenRouter, litellm does
not go through that client, the `litellm.completion` span is a leaf, and the call
is counted once.

`hal/utils/weave_utils.py` aggregates usage over every span without filtering by
op name or deduplicating parent and child, so HAL's published `total_usage` and
`total_cost` carry the same doubling. For the o3-mini high run the span census is
777 `litellm.completion` and 777 `openai.chat.completions.create`, every one of
the latter naming one of the former as parent; HAL reports 6,184,208 prompt
tokens against the 3,092,104 the model actually processed, and $30.37 against
$15.18.

The reduction now applies one rule: **count a span only when no usage-bearing span
names it as parent**. That keeps the leaf record of every call exactly once
without needing a list of which providers double-log. Every run summary carries
the resulting census in `span_breakdown.by_op_name`—spans seen, spans with
usage, spans counted, spans dropped as parents—and
`span_breakdown.gross_undeduplicated_by_model` retains what HAL would have
reported, so the correction is auditable per run without re-downloading.

| Path | Doubled | Spans counted | Evidence |
|---|---|---|---|
| OpenAI native, Together, Gemini | yes | the `openai.chat.completions.create` child | exactly half the spans dropped as parents in every such run |
| GPT-4o image helper, any run | yes | the child | 5 to 82 parents dropped per run |
| Anthropic native and via OpenRouter | no | the `litellm.completion` leaf | no parents dropped beyond the helper's |

The per-run breakdown is in [Span census](#span-census). The effect on the rows is
exactly a factor of two on every OpenAI-path and Together row, and 0.02% to 0.45%
on the Anthropic rows, which pay it only through the helper.

### Per-call counters and the cache rule

Each usage-bearing span carries `weave_task_id`, the GAIA task id, and a
`summary.usage` block keyed by model name. A typical OpenAI record:

```
"o3-mini-2025-01-31": {"prompt_tokens": 9704, "completion_tokens": 4906,
 "requests": 1, "total_tokens": 14610,
 "completion_tokens_details": {"reasoning_tokens": 4736, ...},
 "prompt_tokens_details": {"cached_tokens": 7424, ...}}
```

The two provider conventions are handled separately, as `DECISIONS.md` requires:

- **OpenAI and OpenRouter partition.** `prompt_tokens` *includes*
  `prompt_tokens_details.cached_tokens`, and `completion_tokens` *includes*
  `completion_tokens_details.reasoning_tokens`. Counted input is therefore
  `prompt_tokens - cached_tokens`; reasoning is already inside output. There is
  no separate cache-write counter because OpenAI does not bill one, so the first
  pass over a prefix is counted as ordinary fresh input.
- **Anthropic is additive.** `cache_creation_input_tokens` and
  `cache_read_input_tokens` sit outside `prompt_tokens`. Counted input is
  `prompt_tokens + cache_creation_input_tokens`; cache reads are excluded.

The single formula applied is
`counted = (prompt_tokens - cached_tokens) + cache_creation_input_tokens + completion_tokens`,
which reduces to the right thing under either convention. `tokens_accounting` is
`input_cache_creation_output` on the 25 rows where cached tokens appear and
`input_output` on the 32 where none do.

### What the cache counters do and do not say

No prompt caching happened anywhere in this collection, but the evidence for that
is of three different strengths and the rows say which applies.

- **Anthropic native** (`claude-3-7-sonnet-20250219`, `claude-opus-4-20250514`,
  `claude-haiku-4-5`): the records carry `cache_creation_input_tokens: 0`,
  `cache_read_input_tokens: 0` and `prompt_tokens_details.cached_tokens: 0`. This
  is a measured zero.
- **Together** (`deepseek-ai/DeepSeek-V3`, `DeepSeek-R1`): the usage block is
  `{prompt_tokens, completion_tokens, total_tokens, requests, cached_tokens}` with
  `cached_tokens: 0` on every call. Together does report a counter, and it reports
  zero. This is also a measured zero.
- **OpenRouter** (`anthropic/claude-opus-4`, `-4.1`, `claude-sonnet-4.5`): the
  usage block is `{"prompt_tokens": 45514, "completion_tokens": 485, "requests": 1,
  "total_tokens": 45999, "completion_tokens_details": null, "prompt_tokens_details":
  null}`. Both details blocks are **null**, so the reduction's zero is the absence
  of a counter, not a measurement. On these 16 rows the gross reading rests
  entirely on the harness argument below, and their notes say so.

The harness argument is what actually carries the case, and it is strong. Neither
agent sets `cache_control` anywhere: the HAL Generalist Agent's
[`main.py`](https://github.com/princeton-pli/hal-harness/blob/main/agents/hal_generalist_agent/main.py)
constructs a plain smolagents `LiteLLMModel` and contains no cache directive at
either inspected commit, and the same holds for the Open Deep Research scaffold's
`create_agent`. Anthropic caching requires the directive, so none could occur.
Under the **uncached-harnesses** ruling in `DECISIONS.md` the gross input count is
the compute actually spent and is the central value, and the note must say that
harness re-processing rather than the task drives its size. Those rows carry that
sentence.

One further limitation on the OpenRouter rows: the `prompt_tokens` and
`completion_tokens` returned are OpenRouter's own accounting rather than the
Anthropic tokenizer's native counts, and with both details blocks null there is
nothing in the record to check them against. The size of any discrepancy cannot
be established from this evidence.

The practical consequence of the cache rule is visible in the numbers. Charging
the whole prefix on the OpenAI rows, where caching did happen, multiplies counted
tokens by 1.1x to 3.4x; on every other row the gross and counted figures are
identical, because nothing was cached to begin with. A cache-enabled harness
would have spent far less on the same task, and the Anthropic rows' compute is
not comparable, at equal task difficulty, to a row from a caching harness.

### Helper models

The HAL Generalist Agent exposes `query_vision_language_model`, which calls
`gpt-4o-2024-11-20` through litellm for image questions. Those calls are traced
and their tokens are included in `compute_flops` and in `tokens`, as COLUMNS
requires for helper work. The helper is traced in 30 of the 57 rows and reaches
0.39% of counted tokens at most; in the other 27 it made no call. Part of its
prompt is image positions rather than text, which COLUMNS would keep out of
`tokens`; at this share the composition is immaterial and the rows follow the
accepted Portal convention of including the billed units and saying so.

The Open Deep Research scaffold's equivalent tool, `visualizer` in
`examples/open_deep_research/scripts/visual_qa.py`, posts to
`https://api.openai.com/v1/chat/completions` with `requests`, bypassing the
patched OpenAI client, so Weave never sees it. No Open Deep Research run reports
a second model, and the traced total is therefore short by whatever that tool
spent. Taking the traced agent's share as the scale, this is a sub-percent
one-sided understatement. It is stated in all nine Open Deep Research rows'
configurations.

### Verification

What the checks establish, and what they cannot.

1. **The reduction loses nothing HAL recorded.** Summing the *undeduplicated*
   per-span counters back up matches `total_usage` exactly, model by model, for
   all 34 runs that carry per-call records; the 35th, the slim `o3` upload, has
   none. `span_breakdown.gross_undeduplicated_by_model` retains those sums. This
   check says the reduction is faithful to the log. It **cannot** say the log is
   right, because HAL computes `total_usage` by the same undeduplicated sum—and
   in the first submission it passed while the counts were doubled.
2. **The counters are read with the same convention HAL prices them by.** HAL's
   `total_cost` reproduces from the undeduplicated counters at its published list
   prices: $30.37 against a reported $30.37 for the o3-mini high run, $130.68
   against $130.68 for Claude 3.7 Sonnet, $104.75 against $104.75 for GPT-5. This
   identifies which fields HAL means. It is **not** external corroboration of the
   token counts: the reproduced cost is the doubled one, and HAL's published
   dollar figures for these runs are doubled too.
3. **The span census is the check that catches the doubling.** Per run, the
   op-name breakdown and the parent/child count are retained in every summary and
   tabulated in [Span census](#span-census). A run whose `litellm.completion`
   spans are all dropped as parents is a doubled run; a run with no dropped
   parents beyond the helper's is a single-counted one. This is what the first
   submission lacked.
4. **Accuracy reproduces from the per-task scores.** Counting `score == true`
   over `raw_eval_results` reproduces each run's published `results.accuracy` to
   the last digit, for all 34 runs with per-task records, which confirms the
   task-id join used to split by level. This check is independent of the token
   counters and was sound in the first submission.

Spans that ended in an exception carry no usage and are unrecoverable; they are 1
to 140 per run, and their work is not added back.

### Model coefficients

`flops_per_token` is taken unchanged from
`../AI Compute vs Human Time/dataset/models.csv` for the eleven models that
registry carries, which is read but never written, and from this folder's
`models.csv` for Claude Haiku 4.5, which exists only here. Only records absent
from the canonical root registry are copied into `candidates/gaia/models.csv`,
following the convention every other candidate in this folder uses; that is one
record, `claude-haiku-4-5`, byte-identical to this folder's `models.csv`. Eleven
of the twelve coefficients rest on an estimated active parameter count; only
DeepSeek-V3 and DeepSeek-R1 are reported, at 37B active. Because the traced
GPT-4o helper appears in most rows and its 50B is an estimate, every row here
takes `compute_evidence = derived_assumed_inputs`.

Claude Haiku 4.5 uses the 40B active count Damon ruled on 2026-09-13
(`research/model-priors/accepted-priors.csv`), not the 20B the record previously
carried; its three rows are built at 8e10 FLOPs per token.

**One accepted prior has not yet reached the registry.** The same table moves
`gemini-2.0-flash-001` from 40B to 25B active, and the root registry still
carries 40B. `agen-gaia-hal-gemini20flash-l1`, restored under the close-calls
ruling, is therefore built at the registry's 8e10 FLOPs per token and will need
rebuilding at 5e10—a 0.625x change to that one row—once the registry is
updated. No other model in this block appears in the accepted-priors table.

The priors are the largest single uncertainty in `compute_flops` and they scale
it linearly. They are under separate review per `DECISIONS.md`, and nothing here
proposes a change to any of them.

### Dollar cost

The five cost columns `DECISIONS.md` added on 2026-09-13 are filled for all 57
rows from the shared table at `research/cost/list-prices.csv`, at the sheet in
force for that model and provider on the run date. `ai_cost_basis = list_price`
throughout: the token counts are measured and the rates are published, so nothing
is estimated. Cost is the mean per question over the same denominator as
`compute_flops`, and unlike the FLOP term it **includes** cache reads, priced at
the cached-input rate, and the GPT-4o helper.

Per question the rows run from **$0.0086** (Gemini 2.0 Flash, Level 1) to
**$21.71** (Open Deep Research on Claude Opus 4, Level 3), a spread of 2,500
against the 870 in FLOPs, because price per token varies across providers as much
as active parameters do.

Two provider conventions had to be settled. **OpenRouter publishes no per-token
sheet of its own** and passes the underlying provider's list rates through, so its
three Anthropic models are priced at Anthropic's sheet; the fee OpenRouter takes
is on credit purchase rather than per token. **Together's DeepSeek rates are used
for the two Together runs**, not DeepSeek's own, which are five to fourteen times
cheaper—the run went to Together and that is what the work cost. The DeepSeek-R1 run
(2025-04-15) is priced at Together's split rate of $3.00 input / $7.00 output, in force by
2025-03-26 on the Cost-of-Pass run records; the flat $7.00 rate the price table's earlier window
carried would give $0.197 per question rather than $0.100.

These figures are not HAL's. HAL publishes a doubled cost computed from the
doubled counters at a price table of its own that applies no cache discount. For
the o3-mini high run it reports $30.37 for the whole 165 questions; the
de-duplicated counters at OpenAI's published rates, with cached input at its own
rate, give **$14.18**. Halving accounts for most of the gap and the cache
discount for the rest.

`human_cost_basis = not_available` on every row: GAIA reports neither a payment to
its annotators nor a price for their work. The paper's "two hours of annotator
time" per question is a labour estimate covering creation and validation, not a
dollar figure, and is not a cost.

### Cached-context attention

The 2 × active-parameters convention omits attention over the context. Quantified
with the `4 · layers · d_model · N_context` recipe per processed position that the
dataset's RULER row uses, at each row's mean prefix per call, the omitted term is
**0.03x to 0.60x** the recorded `compute_flops` across the 57 rows. Shapes follow
the tiers in `research/apex-agents.md#cached-context-attention`; DeepSeek uses its
published config, which leaves nothing to bracket and so gives a single figure.

| Primary model | Shape | Attention as a multiple of compute_flops |
|---|---|---|
| claude-opus-4, claude-opus-4-1 | L 80–120, d 10240–16384 | 0.09–0.38 |
| claude-3-7-sonnet, claude-sonnet-4-5, gpt-5 | L 64–96, d 8192–12288 | 0.05–0.60 |
| claude-haiku-4-5 | L 36–56, d 3584–5120 | 0.13–0.43 |
| gpt-4.1 | L 48–72, d 5120–7168 | 0.07–0.20 |
| gemini-2.0-flash-001, o3-mini, o4-mini | L 28–40, d 2880–4096 | 0.03–0.24 |
| deepseek-r1, deepseek-v3 | published: L 61, d 7168 | 0.11 and 0.17 |

Mean prefixes run from 3.6k tokens (o3-mini high, a short-context run) to 29.7k
(Claude Haiku 4.5 at Level 3), so most rows sit in the range where the term is
tens of percent rather than a multiple. The figure is the append-to-a-cached-
prefix form and is the upper of the two readings: where a call re-processes the
whole prefix, as it does on every row here, the mean context over the prefill
positions is half the prefix and the term halves. It is one-sided, it is a ratio
of two quantities that were doubled together and so was unaffected by the
de-duplication, and `research/attention-correction.md` now adds it to
`compute_flops`, at a 12,000-token per-source mean prefix rather than per row.

## Row construction

### Grain

One row is one question at one level for one configuration. The level split is
the informative structure: human time rises 3.1x from Level 1 to Level 3 while
counted tokens rise 1.5x to 3.2x depending on the configuration, so level rows
carry variation that a validation-set aggregate would average away. Aggregate
rows are deliberately **not** built alongside, because they would describe the
same runs and double-count them; the aggregate figures are in
`agent-work/derived/gaia/calculations.json` and in the tables below for reference. This
follows the grain decision the Epoch SWE-bench bin rows in this batch made.

Statistics are per question: `compute_statistic = mean` over the level's
questions, `ai_attempts` the number of questions with logged usage. Accuracy
counts every question in the level, including the few that logged no call,
because those are real failures; the compute mean averages only the questions
that logged usage, because a task with no logged call is missing evidence rather
than a task that cost nothing. On the 51 rows where every question logged a call
the two denominators coincide and `compute_subset = all`; on the six where they
do not it is `positive_tokens`, which is COLUMNS' exact value for this case, and
`ai_attempts` against `human_attempts` shows the gap.

| point_id | level questions | with usage |
|---|---:|---:|
| `agen-gaia-hal-haiku45-l1` | 53 | 50 |
| `agen-gaia-hal-haiku45-l2` | 86 | 80 |
| `agen-gaia-hal-haiku45-l3` | 26 | 25 |
| `agen-gaia-hal-opus4high-l2` | 86 | 85 |
| `agen-gaia-odr-gpt41-l1` | 53 | 52 |
| `agen-gaia-odr-o4minilow-l1` | 53 | 52 |

### Which cells became rows

Two rulings govern retention. Under **uninformative failures are excluded** a
cell is a row where the agent's accuracy is at least half the level's human
score: 46.95% at Level 1, 45.9% at Level 2, 43.65% at Level 3, with no chance
floor to subtract on an open-answer benchmark. Under **close calls at the
exclusion line** a cell within one standard error of that guide is kept as
`below` rather than excluded. A cell is dropped regardless where more than 10% of
its questions logged no model call. Fifty-seven of the 93 (run, level) cells from
the 31 usable runs are rows: 46 clear the guide outright and 11 are close calls.

Every retained row is `performance_vs_human = below`: the agent does the job,
somewhat worse than the human, at 0.40 to 0.86 of the human rate. None reaches
`match`.

**The selection is non-neutral across levels, and only weakly so in compute.**
Level 1 keeps 24 of 31 cells, Level 2 keeps 18, and Level 3 keeps 15—and Level
3 carries the longest human time, so the drop falls hardest where the x-axis is
most informative. Within compute the skew is weak and not uniform in sign: across
the 93 cells the correlation between accuracy and log10 FLOPs per question is
**+0.13**, and at Level 1 the dropped cells have a *higher* geometric-mean compute
(1.71e16) than the kept ones (1.16e16), reversing at Levels 2 and 3 (kept 2.18e16
and 5.21e16 against dropped 1.71e16 and 1.51e16). The full distribution,
including everything dropped, is in `candidates/gaia/dispositions.csv`.

### Fields that are the same in every row

- `task_category = research_analysis`. GAIA is finding and interpreting
  information to reach an answer.
- `compute_scope = inference`, `compute_method = params_tokens`,
  `human_time_scope = task_performance`, `human_skill = typical`.
- `comparison_issues = different_inputs_or_tools; different_assessment;
  different_human_baseline; different_attempt_selection`.
- `source_dataset = GAIA, HAL agent traces`.

The fourth flag is the one Revision 1 added. Every annotator timing is a
successful solve by construction: the annotator wrote the question from a path
they had just walked and recorded how long that walk took, so no failed annotator
attempt exists. The AI side averages compute over all attempts at 35% to 81%
accuracy, and the failed attempts are not cheap—counted tokens on failed
questions run **0.9x to 6.4x** those on solved ones, median 1.7x across the 57
rows. Each row's notes carry its own ratio, and
`agent-work/derived/gaia/calculations.json` carries the underlying per-outcome means and
counts.

### Harness versions

The runs span two harness generations and the difference is material to the token
counts.

| Window | Repository and commit | Search tool | Step cap |
|---|---|---|---:|
| April 2025, HAL Generalist Agent | `benediktstroebl/hal-harness` `3a20717`, 2025-04-14 | DuckDuckGo | 40 |
| April 2025, Open Deep Research | `benediktstroebl/hal-harness` `563dd65`, 2025-04-16 | Google via SerpAPI | 20 and 12 |
| August 2025 onward | `princeton-pli/hal-harness` `5398894`, 2025-07-25 | Google via SerpAPI | 200 |

Each run records its own commit in `git_info`, retained in the summaries. Neither
generation sets `cache_control`. The Open Deep Research scaffold is a submodule of
`benediktstroebl/smolagents` on branch `open_deep_research`: a manager `CodeAgent`
with `max_steps=12` over a `search_agent` with `max_steps=20`,
`planning_interval=4` on both. Each row's `source_record` names its run id and
agent directory so the version is recoverable.

## Dispositions

Six runs are excluded outright and 36 (run, level) cells fail the retention bar.
`candidates/gaia/dispositions.csv` is the machine-readable table of all 53
entries—the 36 failures, the six run exclusions, and the 11 close calls that
were kept—with every ratio, its standard error, its distance from the guide in
standard errors, and the reason. The run-level exclusions are:

| Run | Reason |
|---|---|
| `gaia_hal_generalist_agent_claudeopus420250514_1754344946` | Aborted: 64 of 165 questions logged no model call and 90 calls raised exceptions, so its 30.3% accuracy measures the harness. The same model at high reasoning effort ran completely the same day and is used instead |
| `gaia_hal_generalist_agent_o320250416_1753903002` | Slim upload: run-level usage only, no per-call records, so no per-question compute exists. Its 28.5% would fail the bar anyway |
| `gaia_hal_generalist_agent_claudesonnet45_1760447287` | Ran `agents/hal_generalist_agent_v2`, which is absent from the repository at the commit the run itself records and from the repository today, so the tool set and step cap behind its token counts cannot be verified |
| `gaia_hal_generalist_agent_deepseekchatv30324_1760455632` | The same unverifiable `_v2` agent; 22.4% would fail the bar anyway |
| `gaia_hf_open_deep_research_claudesonnet45_1759311826` | Not retrieved: 2.0 GB upload, decrypted plaintext exceeds available memory. The three HAL Generalist Agent runs of Sonnet 4.5 cover the model |
| `gaia_hf_open_deep_research_claudesonnet45_1759261812` | Not retrieved: 2.4 GB upload, same reason |

Reconciling against the source: 37 GAIA uploads exist, 35 were retrieved, 1 of
those carries no per-call data, 2 more ran an unpublished agent, 1 was aborted.
Thirty-one runs are usable, they yield 93 (run, level) cells, and every one of
those cells appears either as a row or in the disposition table.

### The eleven close calls, and the count the review gave

These cells sit within one standard error of the half-of-human guide and are kept
as `below` under the `DECISIONS.md` close-calls ruling. `standard_errors_below_guide`
in the disposition table is `(0.5 - ratio) / SE(ratio)`, where `SE(ratio)` is the
binomial standard error of the level's accuracy divided by the level's human
score.

| ratio | SE of ratio | SEs under the guide | level | accuracy | n | run |
|---:|---:|---:|:--|---:|---:|---|
| 0.494 | 0.058 | 0.1 | 2 | 0.4535 | 86 | `gaia_hal_generalist_agent_o3mini20250131_high_1744670471` |
| 0.485 | 0.111 | 0.14 | 3 | 0.4231 | 26 | `gaia_hal_generalist_agent_claudeopus41_1758798743` |
| 0.485 | 0.111 | 0.14 | 3 | 0.4231 | 26 | `gaia_hal_generalist_agent_claudeopus420250514_1754374886` |
| 0.485 | 0.111 | 0.14 | 3 | 0.4231 | 26 | `gaia_hf_open_deep_research_claudeopus4_1754425534` |
| 0.485 | 0.111 | 0.14 | 3 | 0.4231 | 26 | `gaia_hf_open_deep_research_o4mini20250416_high_1744923206` |
| 0.482 | 0.073 | 0.24 | 1 | 0.4528 | 53 | `gaia_hf_open_deep_research_claude37sonnet20250219_high_1745539901` |
| 0.462 | 0.073 | 0.52 | 1 | 0.434 | 53 | `gaia_hal_generalist_agent_deepseekaideepseekr1_1744683894` |
| 0.462 | 0.073 | 0.52 | 1 | 0.434 | 53 | `gaia_hal_generalist_agent_gemini20flash_1744828175` |
| 0.442 | 0.072 | 0.8 | 1 | 0.4151 | 53 | `gaia_hf_open_deep_research_claudeopus41_1755030930` |
| 0.441 | 0.109 | 0.54 | 3 | 0.3846 | 26 | `gaia_hf_open_deep_research_gpt520250807_1754605128` |
| 0.397 | 0.107 | 0.97 | 3 | 0.3462 | 26 | `gaia_hf_open_deep_research_gpt4120250414_1744843595` |


**The independent review listed six of these, and the coordinator's instruction
repeated that number.** Its table stops at 0.24 standard errors; the five cells at
0.52 to 0.97 satisfy the same criterion and are not in it. The ruling, not the
enumeration, is the authority, so all eleven are kept and each is marked
`outcome = row, close call`. Reverting to the strict bar is one constant,
`CLOSE_CALL_SE = 0` in `research/gaia/make_rows.py`; restoring only the review's
six has no rule behind it and is not implemented.

**The folder is not internally consistent on this line, which is Damon's call
rather than an agent's.** `DECISIONS.md` records `game-balrog-crafter-deepseekr1`
restored at ratio 0.492 on exactly this reasoning, and that row is in
`points.csv`; but `agen-epoch-swebench-gpt4o1120-lt15m`, also at 0.492, sits in
`excluded.csv`, and `work-apex-agents-gemini35flash` at 0.471 is excluded too.
The GAIA cell at 0.494 is closer to the line than any row the folder has
restored. Four of the eleven rows restored here also bring in configurations that
had no row at all before—HAL DeepSeek-R1, HAL Gemini 2.0 Flash, Open Deep
Research on Claude Opus 4.1, and Open Deep Research on Claude 3.7 Sonnet at high
effort—so reverting the ruling removes four configurations, not just four rows.

## Results

Aggregated over the validation split, for orientation only; these are not rows.
Every configuration that contributed at least one row appears.

| Agent | Model | Effort | Accuracy | FLOPs per question | Tokens per question |
|---|---|---|---:|---:|---:|
| HAL | Claude Sonnet 4.5 | default | 0.745 | 7.11e+16 | 355,770 |
| HAL | Claude Sonnet 4.5 | high | 0.709 | 6.81e+16 | 340,748 |
| HAL | Claude Opus 4.1 | high | 0.685 | 7.56e+16 | 210,223 |
| HAL | Claude Opus 4 | high | 0.648 | 8.70e+16 | 241,755 |
| HAL | Claude 3.7 Sonnet | high | 0.642 | 4.20e+16 | 210,006 |
| HAL | Claude Opus 4.1 | default | 0.642 | 8.65e+16 | 240,392 |
| ODR | GPT-5 | default | 0.624 | 9.93e+16 | 496,688 |
| HAL | GPT-5 | default | 0.594 | 9.22e+15 | 46,145 |
| HAL | o4-mini | low | 0.582 | 3.99e+15 | 99,666 |
| ODR | Claude Opus 4 | default | 0.576 | 2.31e+17 | 641,729 |
| HAL | Claude 3.7 Sonnet | default | 0.564 | 4.90e+16 | 245,298 |
| HAL | Claude Haiku 4.5 | default | 0.564 | 6.41e+16 | 800,605 |
| ODR | o4-mini | high | 0.558 | 1.09e+16 | 272,797 |
| HAL | o4-mini | high | 0.545 | 2.99e+15 | 74,658 |
| ODR | GPT-4.1 | default | 0.503 | 6.03e+15 | 60,259 |
| HAL | GPT-4.1 | default | 0.497 | 3.70e+15 | 36,987 |
| ODR | o4-mini | low | 0.479 | 5.77e+15 | 144,319 |
| HAL | o3-mini | high | 0.467 | 9.57e+14 | 23,893 |
| HAL | DeepSeek-V3 | default | 0.364 | 5.25e+15 | 70,869 |
| ODR | Claude 3.7 Sonnet | high | 0.358 | 2.97e+16 | 148,701 |
| HAL | o3-mini | low | 0.339 | 5.98e+14 | 14,937 |
| HAL | Gemini 2.0 Flash | default | 0.327 | 1.81e+16 | 226,237 |
| HAL | DeepSeek-R1 | default | 0.303 | 4.99e+15 | 67,456 |
| ODR | Claude Opus 4.1 | default | 0.285 | 1.74e+17 | 484,378 |

The scaffold matters more than the model. GPT-5 costs 11x more per question under
Open Deep Research than under the HAL Generalist Agent, for 3 points of accuracy;
o4-mini high costs 3.6x more for 1 point. The Open Deep Research manager delegates
to a sub-agent that re-reads a growing browser transcript, and with no caching on
the Anthropic path that transcript is paid for in full on every call.

Within the HAL Generalist Agent, raising reasoning effort does not reliably buy
accuracy: Claude 3.7 Sonnet gains 8 points and spends 14% fewer tokens, while
Claude Sonnet 4.5 loses 4 points for 4% fewer tokens and o4-mini loses 4 points
for 25% fewer. Two of those comparisons are within sampling error at n=165.

Comparisons within a provider path were unaffected by the de-duplication, since
both sides doubled together. Comparisons across paths were not: before the
correction HAL GPT-5 read as 1.8e16 FLOPs per question against Open Deep Research
Claude Opus 4's 2.3e17, and it is really 9.2e15.

## Span census

Per run: usage-bearing spans, how many were counted, how many were dropped as
usage-bearing parents, and the split by op name. A run whose `litellm.completion`
spans are all dropped is one where Weave's OpenAI-client patch fired inside every
litellm call; a run with no drops beyond the GPT-4o helper's is one where it did
not. The same figures are in each summary's `span_breakdown`.

| Run | usage spans | counted | dropped as parent | op names |
|---|---:|---:|---:|---|
| `gaia_hal_generalist_agent_claude37sonnet20250219_1744772193` | 2573 | 2533 | 40 | litellm.completion 2493 counted, 40 dropped; openai.chat.completions.create 40 counted, 0 dropped |
| `gaia_hal_generalist_agent_claude37sonnet20250219_high_1744730242` | 2714 | 2691 | 23 | litellm.completion 2668 counted, 23 dropped; openai.chat.completions.create 23 counted, 0 dropped |
| `gaia_hal_generalist_agent_claudehaiku45_1760657477` | 4910 | 4835 | 75 | litellm.completion 4760 counted, 75 dropped; openai.chat.completions.create 75 counted, 0 dropped |
| `gaia_hal_generalist_agent_claudeopus41_1758719749` | 2838 | 2807 | 31 | litellm.completion 2776 counted, 31 dropped; openai.chat.completions.create 31 counted, 0 dropped |
| `gaia_hal_generalist_agent_claudeopus41_1758798743` | 3089 | 3055 | 34 | litellm.completion 3021 counted, 34 dropped; openai.chat.completions.create 34 counted, 0 dropped |
| `gaia_hal_generalist_agent_claudeopus420250514_1754344946` | 1361 | 1351 | 10 | litellm.completion 1341 counted, 10 dropped; openai.chat.completions.create 10 counted, 0 dropped |
| `gaia_hal_generalist_agent_claudeopus420250514_1754374886` | 2791 | 2760 | 31 | litellm.completion 2729 counted, 31 dropped; openai.chat.completions.create 31 counted, 0 dropped |
| `gaia_hal_generalist_agent_claudesonnet45_1759265643` | 3281 | 3205 | 76 | litellm.completion 3129 counted, 76 dropped; openai.chat.completions.create 76 counted, 0 dropped |
| `gaia_hal_generalist_agent_claudesonnet45_1759276006` | 3320 | 3238 | 82 | litellm.completion 3156 counted, 82 dropped; openai.chat.completions.create 82 counted, 0 dropped |
| `gaia_hal_generalist_agent_claudesonnet45_1760447287` | 3183 | 3120 | 63 | litellm.completion 3057 counted, 63 dropped; openai.chat.completions.create 63 counted, 0 dropped |
| `gaia_hal_generalist_agent_deepseekaideepseekr1_1744683894` | 2002 | 1001 | 1001 | litellm.completion 0 counted, 1001 dropped; openai.chat.completions.create 1001 counted, 0 dropped |
| `gaia_hal_generalist_agent_deepseekaideepseekv3_1744673872` | 2390 | 1195 | 1195 | litellm.completion 0 counted, 1195 dropped; openai.chat.completions.create 1195 counted, 0 dropped |
| `gaia_hal_generalist_agent_deepseekchatv30324_1760455632` | 840 | 835 | 5 | litellm.completion 830 counted, 5 dropped; openai.chat.completions.create 5 counted, 0 dropped |
| `gaia_hal_generalist_agent_gemini20flash_1744828175` | 4060 | 2030 | 2030 | litellm.completion 0 counted, 2030 dropped; openai.chat.completions.create 2030 counted, 0 dropped |
| `gaia_hal_generalist_agent_gpt4120250414_1744652581` | 3522 | 1761 | 1761 | litellm.completion 0 counted, 1761 dropped; openai.chat.completions.create 1761 counted, 0 dropped |
| `gaia_hal_generalist_agent_gpt520250807_1758875386` | 4198 | 2099 | 2099 | litellm.completion 0 counted, 2099 dropped; openai.chat.completions.create 2099 counted, 0 dropped |
| `gaia_hal_generalist_agent_o320250416_1753903002` | 0 | 0 | 0 |  |
| `gaia_hal_generalist_agent_o3mini20250131_1744609696` | 1866 | 933 | 933 | litellm.completion 0 counted, 933 dropped; openai.chat.completions.create 933 counted, 0 dropped |
| `gaia_hal_generalist_agent_o3mini20250131_high_1744670471` | 1554 | 777 | 777 | litellm.completion 0 counted, 777 dropped; openai.chat.completions.create 777 counted, 0 dropped |
| `gaia_hal_generalist_agent_o4mini20250416_high_1745167285` | 4308 | 2154 | 2154 | litellm.completion 0 counted, 2154 dropped; openai.chat.completions.create 2154 counted, 0 dropped |
| `gaia_hal_generalist_agent_o4mini20250416_low_1745167262` | 4210 | 2105 | 2105 | litellm.completion 0 counted, 2105 dropped; openai.chat.completions.create 2105 counted, 0 dropped |
| `gaia_hf_open_deep_research_claude37sonnet20250219_1745000974` | 7739 | 7739 | 0 | litellm.completion 7739 counted, 0 dropped |
| `gaia_hf_open_deep_research_claude37sonnet20250219_high_1745539901` | 4023 | 4023 | 0 | litellm.completion 4023 counted, 0 dropped |
| `gaia_hf_open_deep_research_claudeopus41_1755030930` | 6090 | 6090 | 0 | litellm.completion 6090 counted, 0 dropped |
| `gaia_hf_open_deep_research_claudeopus41_high_1755092997` | 6826 | 6826 | 0 | litellm.completion 6826 counted, 0 dropped |
| `gaia_hf_open_deep_research_claudeopus4_1754425534` | 7253 | 7253 | 0 | litellm.completion 7253 counted, 0 dropped |
| `gaia_hf_open_deep_research_deepseekaideepseekr1_1744851690` | 6956 | 3478 | 3478 | litellm.completion 0 counted, 3478 dropped; openai.chat.completions.create 3478 counted, 0 dropped |
| `gaia_hf_open_deep_research_deepseekaideepseekv3_1744851680` | 8690 | 4345 | 4345 | litellm.completion 0 counted, 4345 dropped; openai.chat.completions.create 4345 counted, 0 dropped |
| `gaia_hf_open_deep_research_gemini20flash_1744843220` | 14076 | 7038 | 7038 | litellm.completion 0 counted, 7038 dropped; openai.chat.completions.create 7038 counted, 0 dropped |
| `gaia_hf_open_deep_research_gpt4120250414_1744843595` | 5726 | 2863 | 2863 | litellm.completion 0 counted, 2863 dropped; openai.chat.completions.create 2863 counted, 0 dropped |
| `gaia_hf_open_deep_research_gpt520250807_1754605128` | 11530 | 5765 | 5765 | litellm.completion 0 counted, 5765 dropped; openai.chat.completions.create 5765 counted, 0 dropped |
| `gaia_hf_open_deep_research_o320250416_1745876880` | 6814 | 3407 | 3407 | litellm.completion 0 counted, 3407 dropped; openai.chat.completions.create 3407 counted, 0 dropped |
| `gaia_hf_open_deep_research_o3mini20250131_high_1744843485` | 2810 | 1405 | 1405 | litellm.completion 0 counted, 1405 dropped; openai.chat.completions.create 1405 counted, 0 dropped |
| `gaia_hf_open_deep_research_o4mini20250416_high_1744923206` | 8508 | 4254 | 4254 | litellm.completion 0 counted, 4254 dropped; openai.chat.completions.create 4254 counted, 0 dropped |
| `gaia_hf_open_deep_research_o4mini20250416_low_1744921254` | 6614 | 3307 | 3307 | litellm.completion 0 counted, 3307 dropped; openai.chat.completions.create 3307 counted, 0 dropped |
## Reproduction

Scripts take explicit paths and write new outputs; none modifies retained
evidence. `decrypt_hal_zip.py` and `fetch_hal_gaia.py` need network access and
about 16 GB of transfer; everything downstream runs from the retained summaries.

```
cd "AI Compute vs Human Time claude-rows"
python3 research/gaia/parse_annotator_times.py \
  agent-work/sources/gaia/gaia-2023-validation/metadata.parquet \
  /tmp/gaia-times.csv /tmp/gaia-time-stats.json
python3 research/gaia/fetch_hal_gaia.py /tmp/gaia-work /tmp/gaia-summaries 1000
python3 research/gaia/build_gaia_table.py \
  agent-work/sources/gaia/hal-run-summaries \
  agent-work/sources/gaia/gaia-validation-annotator-times.csv \
  "../AI Compute vs Human Time/dataset/models.csv,models.csv" \
  /tmp/gaia-calc.json /tmp/gaia-table.csv
python3 research/gaia/make_rows.py /tmp/gaia-calc.json \
  agent-work/derived/gaia/annotator-time-stats.json \
  "../AI Compute vs Human Time/dataset/models.csv,models.csv" \
  research/cost/list-prices.csv /tmp/gaia-rows
python3 research/gaia/note_tables.py /tmp/gaia-calc.json \
  agent-work/derived/gaia/calculations.json candidates/gaia/points.csv \
  candidates/gaia/dispositions.csv agent-work/sources/gaia/hal-run-summaries
python3 research/gaia/write_note_points.py agent-work/derived/gaia/calculations.json \
  candidates/gaia/points.csv \
  "../AI Compute vs Human Time/dataset/models.csv,models.csv" research/gaia.md
```

Dependencies: `pandas` and `pyarrow` for the parquet, `cryptography` for the
decryption, `ijson` for streaming the multi-GB run files, `huggingface_hub` for
the download. `make_rows.py` rewrites `agent-work/derived/gaia/calculations.json` beside
itself; `build_gaia_table.py`'s JSON output is an intermediate and is not
retained; `note_tables.py` prints the derived tables this note quotes, so they
are not typed by hand; and `write_note_points.py` rewrites everything after the
generated-points marker at the end of the prose in this file, leaving the prose
above it alone. Run end to end from the retained sources on 2026-09-13, this
chain reproduces `agent-work/sources/gaia/gaia-validation-annotator-times.csv`,
`agent-work/derived/gaia/annotator-time-stats.json`, `agent-work/derived/gaia/calculations.json`,
this note's generated tail, and all three files in `candidates/gaia/` byte for
byte.

## What a reviewer should scrutinize first

1. **The close-calls count is eleven, not six.** The independent review's table of
   cells within one standard error of the guide stops at 0.24 standard errors;
   applied as `DECISIONS.md` states it, the rule reaches 0.97 and keeps eleven.
   The five extra cells are the weakest rows in the block, down to 0.40 of the
   human rate, and four of the eleven bring in configurations that would
   otherwise have no row. If the intent was the review's six, the fix is
   `CLOSE_CALL_SE` and a rebuild.
2. **The retention bar's selection effect across levels.** Level 3 keeps 15 of its
   31 cells against Level 1's 24 of 31, and Level 3 carries the longest human
   time. Within a level the compute skew is weak (r = +0.13 overall) and reverses
   in sign at Level 1.
3. **Different humans on the two sides.** The time comes from question designers
   and the 92% from validators. If a reviewer thinks the designers' times are so
   far from a naive solver's that the pairing is unsound, that is an argument
   against the whole block, not against any single row.
4. **The de-duplication rule.** "Count a span only when no usage-bearing span
   names it as parent" is general and does not need a provider list, but it
   assumes a parent and its child never represent two real calls. The span census
   supports that here (the drops are all-or-nothing per run, and the counted
   totals come to exactly half of HAL's on every doubled run) but the rule would
   need rechecking against any future harness that nests genuine sub-calls.
5. **The uncached rows.** Their compute is real spend but reflects a harness
   choice, and on the 16 OpenRouter rows the counters are null rather than zero,
   so the case rests on the absent `cache_control` alone.
6. **The active-parameter priors.** Eleven of twelve are estimated at grade C and
   scale `compute_flops` linearly. `gemini-2.0-flash-001` has an accepted 25B
   prior the root registry has not yet taken up, so its one row is currently 1.6x
   too high.
7. **The Open Deep Research image tool.** Its tokens are missing. The sub-percent
   scale is transferred from the other agent, not measured for this one.
8. **The cost columns are new.** They were added to `COLUMNS.md` mid-revision and
   are filled here from the shared price table; no other candidate in the folder
   carries them yet, so the conventions this block settled (OpenRouter priced at
   Anthropic's sheet, Together priced at Together's) are the first of their kind
   and should be checked before they are copied.

<!-- GENERATED POINTS -->

## agen-gaia-hal-sonnet37-l1

HAL run `gaia_hal_generalist_agent_claude37sonnet20250219_1744772193` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "claude-3-7-sonnet-20250219"}`, run date 2025-04-24), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claude37sonnet20250219_1744772193_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claude37sonnet20250219_1744772193.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 33 solved (0.6226, standard error 0.0666) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `claude-3-7-sonnet-20250219` -> `claude-3-7-sonnet` | primary | 8,543,036 | 0 | 0 | 0 | 189,330 | 0 | 625 | 8,732,366 | 2e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 3,201 | 0 | 0 | 0 | 592 | 0 | 4 | 3,793 | 1e+11 |

Duplicate spans dropped run-wide: 40 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 8,736,159 over the level, that is **164,833.19 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 1.746852e+18 over the level, that is **3.295948e+16 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-04-24, including cache reads and the helper, **$0.5374 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (164,833 tokens per question); generated tokens only as a floor, 0.0217x (3,583 tokens per question); cached-context attention 0.14x to 0.32x at the 13,587-token mean prefix over 11.9 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0004.

Label `below`: 0.66 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 116,878 counted tokens per solved question against 243,960 per failed one over 33 and 20 questions, a ratio of 2.09.

## agen-gaia-hal-sonnet37-l2

HAL run `gaia_hal_generalist_agent_claude37sonnet20250219_1744772193` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "claude-3-7-sonnet-20250219"}`, run date 2025-04-24), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claude37sonnet20250219_1744772193_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claude37sonnet20250219_1744772193.json`. GAIA validation Level 2: 86 questions, 86 with logged usage, 48 solved (0.5581, standard error 0.0536) against 0.918 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `claude-3-7-sonnet-20250219` -> `claude-3-7-sonnet` | primary | 22,002,092 | 0 | 0 | 0 | 380,664 | 0 | 1,346 | 22,382,756 | 2e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 16,767 | 0 | 0 | 0 | 6,362 | 0 | 27 | 23,129 | 1e+11 |

Duplicate spans dropped run-wide: 40 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 22,405,885 over the level, that is **260,533.55 tokens per question** over 86 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 4.478864e+18 over the level, that is **5.207982e+16 FLOPs per question**. Human time 685.12 s, the mean of the 86 annotator self-reports at this level (median 450 s). At list prices on 2025-04-24, including cache reads and the helper, **$0.8351 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (260,534 tokens per question); generated tokens only as a floor, 0.0173x (4,500 tokens per question); cached-context attention 0.17x to 0.38x at the 16,037-token mean prefix over 16.0 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0010.

Label `below`: 0.61 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 166,213 counted tokens per solved question against 379,675 per failed one over 48 and 38 questions, a ratio of 2.28.

## agen-gaia-hal-sonnet37-l3

HAL run `gaia_hal_generalist_agent_claude37sonnet20250219_1744772193` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "claude-3-7-sonnet-20250219"}`, run date 2025-04-24), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claude37sonnet20250219_1744772193_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claude37sonnet20250219_1744772193.json`. GAIA validation Level 3: 26 questions, 26 with logged usage, 12 solved (0.4615, standard error 0.0978) against 0.873 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `claude-3-7-sonnet-20250219` -> `claude-3-7-sonnet` | primary | 9,137,426 | 0 | 0 | 0 | 184,734 | 0 | 522 | 9,322,160 | 2e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 8,648 | 0 | 0 | 0 | 1,374 | 0 | 9 | 10,022 | 1e+11 |

Duplicate spans dropped run-wide: 40 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 9,332,182 over the level, that is **358,930.08 tokens per question** over 26 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 1.865434e+18 over the level, that is **7.174747e+16 FLOPs per question**. Human time 1232.31 s, the mean of the 26 annotator self-reports at this level (median 900 s). At list prices on 2025-04-24, including cache reads and the helper, **$1.1623 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (358,930 tokens per question); generated tokens only as a floor, 0.0199x (7,158 tokens per question); cached-context attention 0.18x to 0.41x at the 17,224-token mean prefix over 20.4 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0011.

Label `below`: 0.53 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 226,348 counted tokens per solved question against 472,572 per failed one over 12 and 14 questions, a ratio of 2.09.

## agen-gaia-hal-sonnet37high-l1

HAL run `gaia_hal_generalist_agent_claude37sonnet20250219_high_1744730242` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "claude-3-7-sonnet-20250219", "reasoning_effort": "high"}`, run date 2025-04-25), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claude37sonnet20250219_high_1744730242_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claude37sonnet20250219_high_1744730242.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 36 solved (0.6792, standard error 0.0641) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `claude-3-7-sonnet-20250219` -> `claude-3-7-sonnet` | primary | 5,940,374 | 0 | 0 | 0 | 366,599 | 170,666 | 692 | 6,306,973 | 2e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 7,275 | 0 | 0 | 0 | 779 | 0 | 6 | 8,054 | 1e+11 |

Duplicate spans dropped run-wide: 23 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 6,315,027 over the level, that is **119,151.45 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 1.262200e+18 over the level, that is **2.381509e+16 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-04-25, including cache reads and the helper, **$0.4405 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (119,151 tokens per question); generated tokens only as a floor, 0.0582x (6,932 tokens per question); cached-context attention 0.09x to 0.20x at the 8,521-token mean prefix over 13.2 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0013.

Label `below`: 0.72 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 93,746 counted tokens per solved question against 172,950 per failed one over 36 and 17 questions, a ratio of 1.84.

## agen-gaia-hal-sonnet37high-l2

HAL run `gaia_hal_generalist_agent_claude37sonnet20250219_high_1744730242` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "claude-3-7-sonnet-20250219", "reasoning_effort": "high"}`, run date 2025-04-25), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claude37sonnet20250219_high_1744730242_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claude37sonnet20250219_high_1744730242.json`. GAIA validation Level 2: 86 questions, 86 with logged usage, 55 solved (0.6395, standard error 0.0518) against 0.918 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `claude-3-7-sonnet-20250219` -> `claude-3-7-sonnet` | primary | 22,447,165 | 0 | 0 | 0 | 869,984 | 354,849 | 1,511 | 23,317,149 | 2e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 6,415 | 0 | 0 | 0 | 4,404 | 0 | 13 | 10,819 | 1e+11 |

Duplicate spans dropped run-wide: 23 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 23,327,968 over the level, that is **271,255.44 tokens per question** over 86 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 4.664512e+18 over the level, that is **5.423851e+16 FLOPs per question**. Human time 685.12 s, the mean of the 86 annotator self-reports at this level (median 450 s). At list prices on 2025-04-25, including cache reads and the helper, **$0.9355 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (271,255 tokens per question); generated tokens only as a floor, 0.0375x (10,167 tokens per question); cached-context attention 0.15x to 0.35x at the 14,733-token mean prefix over 17.7 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0005.

Label `below`: 0.70 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 222,255 counted tokens per solved question against 358,192 per failed one over 55 and 31 questions, a ratio of 1.61.

## agen-gaia-hal-sonnet37high-l3

HAL run `gaia_hal_generalist_agent_claude37sonnet20250219_high_1744730242` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "claude-3-7-sonnet-20250219", "reasoning_effort": "high"}`, run date 2025-04-25), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claude37sonnet20250219_high_1744730242_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claude37sonnet20250219_high_1744730242.json`. GAIA validation Level 3: 26 questions, 26 with logged usage, 15 solved (0.5769, standard error 0.0969) against 0.873 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `claude-3-7-sonnet-20250219` -> `claude-3-7-sonnet` | primary | 4,706,925 | 0 | 0 | 0 | 297,297 | 138,638 | 465 | 5,004,222 | 2e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 3,230 | 0 | 0 | 0 | 519 | 0 | 4 | 3,749 | 1e+11 |

Duplicate spans dropped run-wide: 23 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 5,007,971 over the level, that is **192,614.27 tokens per question** over 26 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 1.001219e+18 over the level, that is **3.850843e+16 FLOPs per question**. Human time 1232.31 s, the mean of the 26 annotator self-reports at this level (median 900 s). At list prices on 2025-04-25, including cache reads and the helper, **$0.7151 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (192,614 tokens per question); generated tokens only as a floor, 0.0595x (11,454 tokens per question); cached-context attention 0.11x to 0.24x at the 10,043-token mean prefix over 18.0 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0007.

Label `below`: 0.66 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 121,119 counted tokens per solved question against 290,108 per failed one over 15 and 11 questions, a ratio of 2.40.

## agen-gaia-hal-haiku45-l1

HAL run `gaia_hal_generalist_agent_claudehaiku45_1760657477` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "max_steps": 40, "model_name": "claude-haiku-4-5"}`, run date 2025-10-16), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claudehaiku45_1760657477_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claudehaiku45_1760657477.json`. GAIA validation Level 1: 53 questions, 50 with logged usage, 33 solved (0.6226, standard error 0.0666) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `claude-haiku-4-5-20251001` -> `claude-haiku-4-5` | primary | 21,657,893 | 0 | 0 | 0 | 418,848 | 0 | 1,062 | 22,076,741 | 8e+10 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 6,124 | 0 | 0 | 0 | 1,109 | 0 | 5 | 7,233 | 1e+11 |

Duplicate spans dropped run-wide: 75 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 22,083,974 over the level, that is **441,679.48 tokens per question** over 50 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 1.766863e+18 over the level, that is **3.533725e+16 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-10-16, including cache reads and the helper, **$0.4756 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (441,679 tokens per question); generated tokens only as a floor, 0.0190x (8,399 tokens per question); cached-context attention 0.13x to 0.29x at the 20,304-token mean prefix over 21.3 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0003.

Label `below`: 0.66 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 271,938 counted tokens per solved question against 771,178 per failed one over 33 and 17 questions, a ratio of 2.84.

## agen-gaia-hal-haiku45-l2

HAL run `gaia_hal_generalist_agent_claudehaiku45_1760657477` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "max_steps": 40, "model_name": "claude-haiku-4-5"}`, run date 2025-10-16), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claudehaiku45_1760657477_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claudehaiku45_1760657477.json`. GAIA validation Level 2: 86 questions, 80 with logged usage, 44 solved (0.5116, standard error 0.0539) against 0.918 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `claude-haiku-4-5-20251001` -> `claude-haiku-4-5` | primary | 65,433,339 | 0 | 0 | 0 | 808,946 | 0 | 2,507 | 66,242,285 | 8e+10 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 22,043 | 0 | 0 | 0 | 6,273 | 0 | 69 | 28,316 | 1e+11 |

Duplicate spans dropped run-wide: 75 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 66,270,601 over the level, that is **828,382.51 tokens per question** over 80 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 5.302214e+18 over the level, that is **6.627768e+16 FLOPs per question**. Human time 685.12 s, the mean of the 86 annotator self-reports at this level (median 450 s). At list prices on 2025-10-16, including cache reads and the helper, **$0.8699 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (828,383 tokens per question); generated tokens only as a floor, 0.0123x (10,190 tokens per question); cached-context attention 0.16x to 0.36x at the 25,410-token mean prefix over 32.2 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0004.

Label `below`: 0.56 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 577,434 counted tokens per solved question against 1,135,098 per failed one over 44 and 36 questions, a ratio of 1.97.

## agen-gaia-hal-haiku45-l3

HAL run `gaia_hal_generalist_agent_claudehaiku45_1760657477` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "max_steps": 40, "model_name": "claude-haiku-4-5"}`, run date 2025-10-16), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claudehaiku45_1760657477_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claudehaiku45_1760657477.json`. GAIA validation Level 3: 26 questions, 25 with logged usage, 16 solved (0.6154, standard error 0.0954) against 0.873 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `claude-haiku-4-5-20251001` -> `claude-haiku-4-5` | primary | 35,351,045 | 0 | 0 | 0 | 387,284 | 0 | 1,191 | 35,738,329 | 8e+10 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 794 | 0 | 0 | 0 | 23 | 0 | 1 | 817 | 1e+11 |

Duplicate spans dropped run-wide: 75 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 35,739,146 over the level, that is **1,429,565.84 tokens per question** over 25 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 2.859148e+18 over the level, that is **1.143659e+17 FLOPs per question**. Human time 1232.31 s, the mean of the 26 annotator self-reports at this level (median 900 s). At list prices on 2025-10-16, including cache reads and the helper, **$1.4916 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (1,429,566 tokens per question); generated tokens only as a floor, 0.0108x (15,492 tokens per question); cached-context attention 0.19x to 0.43x at the 29,658-token mean prefix over 47.7 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0000.

Label `below`: 0.70 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 884,025 counted tokens per solved question against 2,399,416 per failed one over 16 and 9 questions, a ratio of 2.71.

## agen-gaia-hal-opus41high-l1

HAL run `gaia_hal_generalist_agent_claudeopus41_1758719749` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "openrouter/anthropic/claude-opus-4.1", "provider": "anthropic", "reasoning_effort": "high"}`, run date 2025-09-24), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claudeopus41_1758719749_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claudeopus41_1758719749.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 38 solved (0.7170, standard error 0.0619) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `anthropic/claude-opus-4.1` -> `claude-opus-4-1` | primary | 7,178,654 | 0 | 0 | 0 | 176,741 | 0 | 698 | 7,355,395 | 3.6e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 7,257 | 0 | 0 | 0 | 1,556 | 0 | 7 | 8,813 | 1e+11 |

Duplicate spans dropped run-wide: 31 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 7,364,208 over the level, that is **138,947.32 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 2.648824e+18 over the level, that is **4.997780e+16 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-09-24, including cache reads and the helper, **$2.2824 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (138,947 tokens per question); generated tokens only as a floor, 0.0242x (3,364 tokens per question); cached-context attention 0.09x to 0.22x at the 10,193-token mean prefix over 13.3 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0012.

Label `below`: 0.76 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 103,999 counted tokens per solved question against 227,484 per failed one over 38 and 15 questions, a ratio of 2.19.

## agen-gaia-hal-opus41high-l2

HAL run `gaia_hal_generalist_agent_claudeopus41_1758719749` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "openrouter/anthropic/claude-opus-4.1", "provider": "anthropic", "reasoning_effort": "high"}`, run date 2025-09-24), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claudeopus41_1758719749_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claudeopus41_1758719749.json`. GAIA validation Level 2: 86 questions, 86 with logged usage, 61 solved (0.7093, standard error 0.0490) against 0.918 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `anthropic/claude-opus-4.1` -> `claude-opus-4-1` | primary | 16,560,044 | 0 | 0 | 0 | 347,830 | 0 | 1,423 | 16,907,874 | 3.6e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 9,396 | 0 | 0 | 0 | 3,599 | 0 | 21 | 12,995 | 1e+11 |

Duplicate spans dropped run-wide: 31 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 16,920,869 over the level, that is **196,754.29 tokens per question** over 86 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 6.088134e+18 over the level, that is **7.079226e+16 FLOPs per question**. Human time 685.12 s, the mean of the 86 annotator self-reports at this level (median 450 s). At list prices on 2025-09-24, including cache reads and the helper, **$3.1924 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (196,754 tokens per question); generated tokens only as a floor, 0.0208x (4,086 tokens per question); cached-context attention 0.10x to 0.25x at the 11,475-token mean prefix over 16.8 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0008.

Label `below`: 0.77 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 170,900 counted tokens per solved question against 259,839 per failed one over 61 and 25 questions, a ratio of 1.52.

## agen-gaia-hal-opus41high-l3

HAL run `gaia_hal_generalist_agent_claudeopus41_1758719749` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "openrouter/anthropic/claude-opus-4.1", "provider": "anthropic", "reasoning_effort": "high"}`, run date 2025-09-24), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claudeopus41_1758719749_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claudeopus41_1758719749.json`. GAIA validation Level 3: 26 questions, 26 with logged usage, 14 solved (0.5385, standard error 0.0978) against 0.873 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `anthropic/claude-opus-4.1` -> `claude-opus-4-1` | primary | 10,221,915 | 0 | 0 | 0 | 177,083 | 0 | 655 | 10,398,998 | 3.6e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 2,427 | 0 | 0 | 0 | 367 | 0 | 3 | 2,794 | 1e+11 |

Duplicate spans dropped run-wide: 31 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 10,401,792 over the level, that is **400,068.92 tokens per question** over 26 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 3.743919e+18 over the level, that is **1.439969e+17 FLOPs per question**. Human time 1232.31 s, the mean of the 26 annotator self-reports at this level (median 900 s). At list prices on 2025-09-24, including cache reads and the helper, **$6.4084 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (400,069 tokens per question); generated tokens only as a floor, 0.0171x (6,825 tokens per question); cached-context attention 0.14x to 0.34x at the 15,539-token mean prefix over 25.3 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0003.

Label `below`: 0.62 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 326,915 counted tokens per solved question against 485,415 per failed one over 14 and 12 questions, a ratio of 1.48.

## agen-gaia-hal-opus41-l1

HAL run `gaia_hal_generalist_agent_claudeopus41_1758798743` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "openrouter/anthropic/claude-opus-4.1", "provider": "anthropic"}`, run date 2025-09-25), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claudeopus41_1758798743_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claudeopus41_1758798743.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 38 solved (0.7170, standard error 0.0619) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `anthropic/claude-opus-4.1` -> `claude-opus-4-1` | primary | 7,171,161 | 0 | 0 | 0 | 184,719 | 0 | 732 | 7,355,880 | 3.6e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 3,865 | 0 | 0 | 0 | 597 | 0 | 3 | 4,462 | 1e+11 |

Duplicate spans dropped run-wide: 34 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 7,360,342 over the level, that is **138,874.38 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 2.648563e+18 over the level, that is **4.997289e+16 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-09-25, including cache reads and the helper, **$2.2913 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (138,874 tokens per question); generated tokens only as a floor, 0.0252x (3,497 tokens per question); cached-context attention 0.09x to 0.21x at the 9,762-token mean prefix over 13.9 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0006.

Label `below`: 0.76 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 119,427 counted tokens per solved question against 188,141 per failed one over 38 and 15 questions, a ratio of 1.58.

## agen-gaia-hal-opus41-l2

HAL run `gaia_hal_generalist_agent_claudeopus41_1758798743` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "openrouter/anthropic/claude-opus-4.1", "provider": "anthropic"}`, run date 2025-09-25), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claudeopus41_1758798743_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claudeopus41_1758798743.json`. GAIA validation Level 2: 86 questions, 86 with logged usage, 57 solved (0.6628, standard error 0.0510) against 0.918 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `anthropic/claude-opus-4.1` -> `claude-opus-4-1` | primary | 22,056,112 | 0 | 0 | 0 | 413,078 | 0 | 1,639 | 22,469,190 | 3.6e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 14,633 | 0 | 0 | 0 | 7,114 | 0 | 30 | 21,747 | 1e+11 |

Duplicate spans dropped run-wide: 34 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 22,490,937 over the level, that is **261,522.52 tokens per question** over 86 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 8.091083e+18 over the level, that is **9.408236e+16 FLOPs per question**. Human time 685.12 s, the mean of the 86 annotator self-reports at this level (median 450 s). At list prices on 2025-09-25, including cache reads and the helper, **$4.2085 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (261,523 tokens per question); generated tokens only as a floor, 0.0187x (4,886 tokens per question); cached-context attention 0.12x to 0.29x at the 13,224-token mean prefix over 19.4 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0010.

Label `below`: 0.72 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 232,966 counted tokens per solved question against 317,651 per failed one over 57 and 29 questions, a ratio of 1.36.

## agen-gaia-hal-opus41-l3

HAL run `gaia_hal_generalist_agent_claudeopus41_1758798743` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "openrouter/anthropic/claude-opus-4.1", "provider": "anthropic"}`, run date 2025-09-25), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claudeopus41_1758798743_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claudeopus41_1758798743.json`. GAIA validation Level 3: 26 questions, 26 with logged usage, 11 solved (0.4231, standard error 0.0969) against 0.873 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `anthropic/claude-opus-4.1` -> `claude-opus-4-1` | primary | 9,626,274 | 0 | 0 | 0 | 186,226 | 0 | 650 | 9,812,500 | 3.6e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 797 | 0 | 0 | 0 | 39 | 0 | 1 | 836 | 1e+11 |

Duplicate spans dropped run-wide: 34 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 9,813,336 over the level, that is **377,436.00 tokens per question** over 26 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 3.532584e+18 over the level, that is **1.358686e+17 FLOPs per question**. Human time 1232.31 s, the mean of the 26 annotator self-reports at this level (median 900 s). At list prices on 2025-09-25, including cache reads and the helper, **$6.0909 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (377,436 tokens per question); generated tokens only as a floor, 0.0190x (7,164 tokens per question); cached-context attention 0.13x to 0.32x at the 14,788-token mean prefix over 25.0 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0001.

Label `below`: 0.48 of the human rate, kept under the close-calls ruling, 0.14 standard errors under the 0.5 guide on a standard error of 0.111 and short of comparable. Compute averages all attempts: 138,963 counted tokens per solved question against 552,316 per failed one over 11 and 15 questions, a ratio of 3.97.

## agen-gaia-hal-opus4high-l1

HAL run `gaia_hal_generalist_agent_claudeopus420250514_1754374886` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "claude-opus-4-20250514", "provider": "anthropic", "reasoning_effort": "high"}`, run date 2025-08-05), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claudeopus420250514_1754374886_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claudeopus420250514_1754374886.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 38 solved (0.7170, standard error 0.0619) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `claude-opus-4-20250514` -> `claude-opus-4` | primary | 6,246,408 | 0 | 0 | 0 | 285,246 | 99,082 | 663 | 6,531,654 | 3.6e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 8,447 | 0 | 0 | 0 | 1,025 | 0 | 6 | 9,472 | 1e+11 |

Duplicate spans dropped run-wide: 31 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 6,541,126 over the level, that is **123,417.47 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 2.352343e+18 over the level, that is **4.438382e+16 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-08-05, including cache reads and the helper, **$2.1721 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (123,417 tokens per question); generated tokens only as a floor, 0.0438x (5,401 tokens per question); cached-context attention 0.09x to 0.20x at the 9,350-token mean prefix over 12.6 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0014.

Label `below`: 0.76 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 86,288 counted tokens per solved question against 217,480 per failed one over 38 and 15 questions, a ratio of 2.52.

## agen-gaia-hal-opus4high-l2

HAL run `gaia_hal_generalist_agent_claudeopus420250514_1754374886` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "claude-opus-4-20250514", "provider": "anthropic", "reasoning_effort": "high"}`, run date 2025-08-05), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claudeopus420250514_1754374886_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claudeopus420250514_1754374886.json`. GAIA validation Level 2: 86 questions, 85 with logged usage, 58 solved (0.6744, standard error 0.0505) against 0.918 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `claude-opus-4-20250514` -> `claude-opus-4` | primary | 19,822,771 | 0 | 0 | 0 | 582,731 | 198,063 | 1,369 | 20,405,502 | 3.6e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 8,346 | 0 | 0 | 0 | 5,145 | 0 | 18 | 13,491 | 1e+11 |

Duplicate spans dropped run-wide: 31 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 20,418,993 over the level, that is **240,223.45 tokens per question** over 85 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 7.347330e+18 over the level, that is **8.643917e+16 FLOPs per question**. Human time 685.12 s, the mean of the 86 annotator self-reports at this level (median 450 s). At list prices on 2025-08-05, including cache reads and the helper, **$4.0132 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (240,223 tokens per question); generated tokens only as a floor, 0.0288x (6,916 tokens per question); cached-context attention 0.13x to 0.31x at the 14,298-token mean prefix over 16.3 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0007.

Label `below`: 0.73 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 216,515 counted tokens per solved question against 291,152 per failed one over 58 and 27 questions, a ratio of 1.34.

## agen-gaia-hal-opus4high-l3

HAL run `gaia_hal_generalist_agent_claudeopus420250514_1754374886` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "claude-opus-4-20250514", "provider": "anthropic", "reasoning_effort": "high"}`, run date 2025-08-05), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claudeopus420250514_1754374886_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claudeopus420250514_1754374886.json`. GAIA validation Level 3: 26 questions, 26 with logged usage, 11 solved (0.4231, standard error 0.0969) against 0.873 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `claude-opus-4-20250514` -> `claude-opus-4` | primary | 12,358,993 | 0 | 0 | 0 | 321,287 | 115,255 | 697 | 12,680,280 | 3.6e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 5,788 | 0 | 0 | 0 | 1,570 | 0 | 7 | 7,358 | 1e+11 |

Duplicate spans dropped run-wide: 31 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 12,687,638 over the level, that is **487,986.08 tokens per question** over 26 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 4.565637e+18 over the level, that is **1.756014e+17 FLOPs per question**. Human time 1232.31 s, the mean of the 26 annotator self-reports at this level (median 900 s). At list prices on 2025-08-05, including cache reads and the helper, **$8.0581 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (487,986 tokens per question); generated tokens only as a floor, 0.0254x (12,418 tokens per question); cached-context attention 0.16x to 0.38x at the 17,564-token mean prefix over 27.1 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0006.

Label `below`: 0.48 of the human rate, kept under the close-calls ruling, 0.14 standard errors under the 0.5 guide on a standard error of 0.111 and short of comparable. Compute averages all attempts: 305,369 counted tokens per solved question against 621,905 per failed one over 11 and 15 questions, a ratio of 2.04.

## agen-gaia-hal-sonnet45high-l1

HAL run `gaia_hal_generalist_agent_claudesonnet45_1759265643` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "openrouter/anthropic/claude-sonnet-4.5", "provider": "anthropic", "reasoning_effort": "high"}`, run date 2025-09-30), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claudesonnet45_1759265643_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claudesonnet45_1759265643.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 41 solved (0.7736, standard error 0.0575) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `anthropic/claude-sonnet-4.5` -> `claude-sonnet-4-5` | primary | 9,451,556 | 0 | 0 | 0 | 196,795 | 0 | 721 | 9,648,351 | 2e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 8,511 | 0 | 0 | 0 | 1,374 | 0 | 7 | 9,885 | 1e+11 |

Duplicate spans dropped run-wide: 76 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 9,658,236 over the level, that is **182,230.87 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 1.930659e+18 over the level, that is **3.642752e+16 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-09-30, including cache reads and the helper, **$0.5914 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (182,231 tokens per question); generated tokens only as a floor, 0.0205x (3,739 tokens per question); cached-context attention 0.14x to 0.31x at the 12,995-token mean prefix over 13.7 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0010.

Label `below`: 0.82 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 133,736 counted tokens per solved question against 347,920 per failed one over 41 and 12 questions, a ratio of 2.60.

## agen-gaia-hal-sonnet45high-l2

HAL run `gaia_hal_generalist_agent_claudesonnet45_1759265643` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "openrouter/anthropic/claude-sonnet-4.5", "provider": "anthropic", "reasoning_effort": "high"}`, run date 2025-09-30), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claudesonnet45_1759265643_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claudesonnet45_1759265643.json`. GAIA validation Level 2: 86 questions, 86 with logged usage, 64 solved (0.7442, standard error 0.0470) against 0.918 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `anthropic/claude-sonnet-4.5` -> `claude-sonnet-4-5` | primary | 25,745,366 | 0 | 0 | 0 | 435,130 | 0 | 1,558 | 26,180,496 | 2e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 51,451 | 0 | 0 | 0 | 7,513 | 0 | 65 | 58,964 | 1e+11 |

Duplicate spans dropped run-wide: 76 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 26,239,460 over the level, that is **305,110.00 tokens per question** over 86 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 5.241996e+18 over the level, that is **6.095344e+16 FLOPs per question**. Human time 685.12 s, the mean of the 86 annotator self-reports at this level (median 450 s). At list prices on 2025-09-30, including cache reads and the helper, **$0.9764 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (305,110 tokens per question); generated tokens only as a floor, 0.0169x (5,147 tokens per question); cached-context attention 0.17x to 0.37x at the 15,895-token mean prefix over 18.9 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0022.

Label `below`: 0.81 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 229,296 counted tokens per solved question against 525,660 per failed one over 64 and 22 questions, a ratio of 2.29.

## agen-gaia-hal-sonnet45high-l3

HAL run `gaia_hal_generalist_agent_claudesonnet45_1759265643` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "openrouter/anthropic/claude-sonnet-4.5", "provider": "anthropic", "reasoning_effort": "high"}`, run date 2025-09-30), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claudesonnet45_1759265643_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claudesonnet45_1759265643.json`. GAIA validation Level 3: 26 questions, 26 with logged usage, 12 solved (0.4615, standard error 0.0978) against 0.873 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `anthropic/claude-sonnet-4.5` -> `claude-sonnet-4-5` | primary | 20,045,007 | 0 | 0 | 0 | 277,088 | 0 | 850 | 20,322,095 | 2e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 3,267 | 0 | 0 | 0 | 406 | 0 | 4 | 3,673 | 1e+11 |

Duplicate spans dropped run-wide: 76 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 20,325,768 over the level, that is **781,760.31 tokens per question** over 26 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 4.064786e+18 over the level, that is **1.563379e+17 FLOPs per question**. Human time 1232.31 s, the mean of the 26 annotator self-reports at this level (median 900 s). At list prices on 2025-09-30, including cache reads and the helper, **$2.4732 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (781,760 tokens per question); generated tokens only as a floor, 0.0137x (10,673 tokens per question); cached-context attention 0.25x to 0.55x at the 23,476-token mean prefix over 32.8 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0002.

Label `below`: 0.53 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 312,801 counted tokens per solved question against 1,183,725 per failed one over 12 and 14 questions, a ratio of 3.78.

## agen-gaia-hal-sonnet45-l1

HAL run `gaia_hal_generalist_agent_claudesonnet45_1759276006` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "openrouter/anthropic/claude-sonnet-4.5", "provider": "anthropic"}`, run date 2025-10-01), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claudesonnet45_1759276006_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claudesonnet45_1759276006.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 43 solved (0.8113, standard error 0.0537) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `anthropic/claude-sonnet-4.5` -> `claude-sonnet-4-5` | primary | 6,542,513 | 0 | 0 | 0 | 168,415 | 0 | 606 | 6,710,928 | 2e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 7,677 | 0 | 0 | 0 | 1,024 | 0 | 6 | 8,701 | 1e+11 |

Duplicate spans dropped run-wide: 82 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 6,719,629 over the level, that is **126,785.45 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 1.343056e+18 over the level, that is **2.534067e+16 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-10-01, including cache reads and the helper, **$0.4186 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (126,785 tokens per question); generated tokens only as a floor, 0.0252x (3,197 tokens per question); cached-context attention 0.11x to 0.25x at the 10,703-token mean prefix over 11.5 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0013.

Label `below`: 0.86 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 100,032 counted tokens per solved question against 241,827 per failed one over 43 and 10 questions, a ratio of 2.42.

## agen-gaia-hal-sonnet45-l2

HAL run `gaia_hal_generalist_agent_claudesonnet45_1759276006` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "openrouter/anthropic/claude-sonnet-4.5", "provider": "anthropic"}`, run date 2025-10-01), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claudesonnet45_1759276006_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claudesonnet45_1759276006.json`. GAIA validation Level 2: 86 questions, 86 with logged usage, 62 solved (0.7209, standard error 0.0484) against 0.918 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `anthropic/claude-sonnet-4.5` -> `claude-sonnet-4-5` | primary | 29,711,448 | 0 | 0 | 0 | 462,280 | 0 | 1,711 | 30,173,728 | 2e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 51,563 | 0 | 0 | 0 | 14,495 | 0 | 74 | 66,058 | 1e+11 |

Duplicate spans dropped run-wide: 82 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 30,239,786 over the level, that is **351,625.42 tokens per question** over 86 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 6.041351e+18 over the level, that is **7.024827e+16 FLOPs per question**. Human time 685.12 s, the mean of the 86 annotator self-reports at this level (median 450 s). At list prices on 2025-10-01, including cache reads and the helper, **$1.1203 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (351,625 tokens per question); generated tokens only as a floor, 0.0158x (5,544 tokens per question); cached-context attention 0.17x to 0.39x at the 16,674-token mean prefix over 20.8 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0022.

Label `below`: 0.79 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 298,311 counted tokens per solved question against 489,354 per failed one over 62 and 24 questions, a ratio of 1.64.

## agen-gaia-hal-sonnet45-l3

HAL run `gaia_hal_generalist_agent_claudesonnet45_1759276006` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "openrouter/anthropic/claude-sonnet-4.5", "provider": "anthropic"}`, run date 2025-10-01), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_claudesonnet45_1759276006_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_claudesonnet45_1759276006.json`. GAIA validation Level 3: 26 questions, 26 with logged usage, 18 solved (0.6923, standard error 0.0905) against 0.873 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `anthropic/claude-sonnet-4.5` -> `claude-sonnet-4-5` | primary | 21,464,897 | 0 | 0 | 0 | 275,347 | 0 | 839 | 21,740,244 | 2e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 2,007 | 0 | 0 | 0 | 329 | 0 | 2 | 2,336 | 1e+11 |

Duplicate spans dropped run-wide: 82 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 21,742,580 over the level, that is **836,253.08 tokens per question** over 26 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 4.348282e+18 over the level, that is **1.672416e+17 FLOPs per question**. Human time 1232.31 s, the mean of the 26 annotator self-reports at this level (median 900 s). At list prices on 2025-10-01, including cache reads and the helper, **$2.6359 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (836,253 tokens per question); generated tokens only as a floor, 0.0127x (10,603 tokens per question); cached-context attention 0.27x to 0.60x at the 25,525-token mean prefix over 32.3 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0001.

Label `below`: 0.79 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 697,859 counted tokens per solved question against 1,147,640 per failed one over 18 and 8 questions, a ratio of 1.64.

## agen-gaia-hal-dsr1-l1

HAL run `gaia_hal_generalist_agent_deepseekaideepseekr1_1744683894` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "model_name": "together_ai/deepseek-ai/DeepSeek-R1"}`, run date 2025-04-15), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_deepseekaideepseekr1_1744683894_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_deepseekaideepseekr1_1744683894.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 23 solved (0.4340, standard error 0.0681) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `deepseek-ai/DeepSeek-R1` -> `deepseek-r1` | primary | 1,291,562 | 0 | 0 | 0 | 202,482 | 0 | 264 | 1,494,044 | 7.4e+10 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 2,275 | 0 | 0 | 0 | 73 | 0 | 2 | 2,348 | 1e+11 |

Duplicate spans dropped run-wide: 1,001 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 1,496,392 over the level, that is **28,233.81 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 1.107941e+17 over the level, that is **2.090454e+15 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-04-15, including cache reads and the helper, **$0.1974 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (28,234 tokens per question); generated tokens only as a floor, 0.1354x (3,822 tokens per question); cached-context attention 0.11x at the 4,864-token mean prefix over 5.0 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0016.

Label `below`: 0.46 of the human rate, kept under the close-calls ruling, 0.52 standard errors under the 0.5 guide on a standard error of 0.073 and short of comparable. Compute averages all attempts: 22,405 counted tokens per solved question against 32,702 per failed one over 23 and 30 questions, a ratio of 1.46.

## agen-gaia-hal-dsv3-l1

HAL run `gaia_hal_generalist_agent_deepseekaideepseekv3_1744673872` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "model_name": "together_ai/deepseek-ai/DeepSeek-V3"}`, run date 2025-04-15), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_deepseekaideepseekv3_1744673872_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_deepseekaideepseekv3_1744673872.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 27 solved (0.5094, standard error 0.0687) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `deepseek-ai/DeepSeek-V3` -> `deepseek-v3` | primary | 2,243,149 | 0 | 0 | 0 | 50,888 | 0 | 309 | 2,294,037 | 7.4e+10 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 2,297 | 0 | 0 | 0 | 423 | 0 | 2 | 2,720 | 1e+11 |

Duplicate spans dropped run-wide: 1,195 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 2,296,757 over the level, that is **43,335.04 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 1.700307e+17 over the level, that is **3.208127e+15 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-04-15, including cache reads and the helper, **$0.0543 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (43,335 tokens per question); generated tokens only as a floor, 0.0223x (968 tokens per question); cached-context attention 0.17x at the 7,220-token mean prefix over 5.9 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0012.

Label `below`: 0.54 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 42,948 counted tokens per solved question against 43,737 per failed one over 27 and 26 questions, a ratio of 1.02.

## agen-gaia-hal-gemini20flash-l1

HAL run `gaia_hal_generalist_agent_gemini20flash_1744828175` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "model_name": "gemini/gemini-2.0-flash"}`, run date 2025-04-16), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_gemini20flash_1744828175_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_gemini20flash_1744828175.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 23 solved (0.4340, standard error 0.0681) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemini-2.0-flash` -> `gemini-2.0-flash-001` | primary | 4,151,878 | 0 | 0 | 0 | 86,754 | 0 | 456 | 4,238,632 | 8e+10 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 1,490 | 0 | 0 | 0 | 169 | 0 | 1 | 1,659 | 1e+11 |

Duplicate spans dropped run-wide: 2,030 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 4,240,291 over the level, that is **80,005.49 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 3.392565e+17 over the level, that is **6.401065e+15 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-04-16, including cache reads and the helper, **$0.0086 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (80,005 tokens per question); generated tokens only as a floor, 0.0205x (1,640 tokens per question); cached-context attention 0.04x to 0.07x at the 9,088-token mean prefix over 8.6 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0004.

Label `below`: 0.46 of the human rate, kept under the close-calls ruling, 0.52 standard errors under the 0.5 guide on a standard error of 0.073 and short of comparable. Compute averages all attempts: 62,787 counted tokens per solved question against 93,206 per failed one over 23 and 30 questions, a ratio of 1.48.

## agen-gaia-hal-gpt41-l1

HAL run `gaia_hal_generalist_agent_gpt4120250414_1744652581` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "model_name": "openai/gpt-4.1-2025-04-14"}`, run date 2025-04-14), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_gpt4120250414_1744652581_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_gpt4120250414_1744652581.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 28 solved (0.5283, standard error 0.0686) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gpt-4.1-2025-04-14` -> `gpt-4.1-2025-04-14` | primary | 3,231,159 | 1,896,704 | 0 | 0 | 85,614 | 0 | 433 | 1,420,069 | 1e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 3,152 | 0 | 0 | 0 | 484 | 0 | 3 | 3,636 | 1e+11 |

Duplicate spans dropped run-wide: 1,761 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 1,423,705 over the level, that is **26,862.36 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 1.423705e+17 over the level, that is **2.686236e+15 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-04-14, including cache reads and the helper, **$0.0814 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 2.332x (62,649 tokens per question); generated tokens only as a floor, 0.0605x (1,624 tokens per question); cached-context attention 0.07x to 0.15x at the 7,418-token mean prefix over 8.2 calls per question, one-sided upward. Cached share of prompt tokens 0.586; helper share of counted tokens 0.0026.

Label `below`: 0.56 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 20,039 counted tokens per solved question against 34,504 per failed one over 28 and 25 questions, a ratio of 1.72.

## agen-gaia-hal-gpt41-l2

HAL run `gaia_hal_generalist_agent_gpt4120250414_1744652581` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "model_name": "openai/gpt-4.1-2025-04-14"}`, run date 2025-04-14), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_gpt4120250414_1744652581_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_gpt4120250414_1744652581.json`. GAIA validation Level 2: 86 questions, 86 with logged usage, 48 solved (0.5581, standard error 0.0536) against 0.918 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gpt-4.1-2025-04-14` -> `gpt-4.1-2025-04-14` | primary | 10,019,174 | 7,189,760 | 0 | 0 | 201,014 | 0 | 1,006 | 3,030,428 | 1e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 4,148 | 0 | 0 | 0 | 1,070 | 0 | 8 | 5,218 | 1e+11 |

Duplicate spans dropped run-wide: 1,761 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 3,035,646 over the level, that is **35,298.21 tokens per question** over 86 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 3.035646e+17 over the level, that is **3.529821e+15 FLOPs per question**. Human time 685.12 s, the mean of the 86 annotator self-reports at this level (median 450 s). At list prices on 2025-04-14, including cache reads and the helper, **$0.1265 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 3.368x (118,900 tokens per question); generated tokens only as a floor, 0.0666x (2,350 tokens per question); cached-context attention 0.10x to 0.20x at the 9,885-token mean prefix over 11.8 calls per question, one-sided upward. Cached share of prompt tokens 0.717; helper share of counted tokens 0.0017.

Label `below`: 0.61 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 34,595 counted tokens per solved question against 36,187 per failed one over 48 and 38 questions, a ratio of 1.05.

## agen-gaia-hal-gpt5-l1

HAL run `gaia_hal_generalist_agent_gpt520250807_1758875386` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "gpt-5-2025-08-07"}`, run date 2025-09-26), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_gpt520250807_1758875386_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_gpt520250807_1758875386.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 36 solved (0.6792, standard error 0.0641) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gpt-5-2025-08-07` -> `gpt-5` | primary | 5,673,868 | 4,376,192 | 0 | 0 | 845,598 | 641,536 | 642 | 2,143,274 | 2e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 7,884 | 0 | 0 | 0 | 442 | 0 | 7 | 8,326 | 1e+11 |

Duplicate spans dropped run-wide: 2,099 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 2,151,600 over the level, that is **40,596.23 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 4.294874e+17 over the level, that is **8.103536e+15 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-09-26, including cache reads and the helper, **$0.2009 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 3.034x (123,166 tokens per question); generated tokens only as a floor, 0.3932x (15,963 tokens per question); cached-context attention 0.09x to 0.21x at the 8,755-token mean prefix over 12.2 calls per question, one-sided upward. Cached share of prompt tokens 0.770; helper share of counted tokens 0.0039.

Label `below`: 0.72 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 35,066 counted tokens per solved question against 52,308 per failed one over 36 and 17 questions, a ratio of 1.49.

## agen-gaia-hal-gpt5-l2

HAL run `gaia_hal_generalist_agent_gpt520250807_1758875386` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "gpt-5-2025-08-07"}`, run date 2025-09-26), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_gpt520250807_1758875386_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_gpt520250807_1758875386.json`. GAIA validation Level 2: 86 questions, 86 with logged usage, 50 solved (0.5814, standard error 0.0532) against 0.918 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gpt-5-2025-08-07` -> `gpt-5` | primary | 9,307,672 | 6,826,880 | 0 | 0 | 1,406,073 | 1,057,472 | 1,055 | 3,886,865 | 2e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 4,582 | 0 | 0 | 0 | 1,555 | 0 | 9 | 6,137 | 1e+11 |

Duplicate spans dropped run-wide: 2,099 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 3,893,002 over the level, that is **45,267.47 tokens per question** over 86 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 7.779867e+17 over the level, that is **9.046357e+15 FLOPs per question**. Human time 685.12 s, the mean of the 86 annotator self-reports at this level (median 450 s). At list prices on 2025-09-26, including cache reads and the helper, **$0.2098 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 2.754x (124,650 tokens per question); generated tokens only as a floor, 0.3616x (16,368 tokens per question); cached-context attention 0.09x to 0.21x at the 8,752-token mean prefix over 12.4 calls per question, one-sided upward. Cached share of prompt tokens 0.733; helper share of counted tokens 0.0016.

Label `below`: 0.63 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 38,056 counted tokens per solved question against 55,283 per failed one over 50 and 36 questions, a ratio of 1.45.

## agen-gaia-hal-gpt5-l3

HAL run `gaia_hal_generalist_agent_gpt520250807_1758875386` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "gpt-5-2025-08-07"}`, run date 2025-09-26), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_gpt520250807_1758875386_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_gpt520250807_1758875386.json`. GAIA validation Level 3: 26 questions, 26 with logged usage, 12 solved (0.4615, standard error 0.0978) against 0.873 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gpt-5-2025-08-07` -> `gpt-5` | primary | 4,245,353 | 3,253,760 | 0 | 0 | 576,977 | 433,024 | 385 | 1,568,570 | 2e+11 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 800 | 0 | 0 | 0 | 32 | 0 | 1 | 832 | 1e+11 |

Duplicate spans dropped run-wide: 2,099 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 1,569,402 over the level, that is **60,361.62 tokens per question** over 26 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 3.137972e+17 over the level, that is **1.206912e+16 FLOPs per question**. Human time 1232.31 s, the mean of the 26 annotator self-reports at this level (median 900 s). At list prices on 2025-09-26, including cache reads and the helper, **$0.2853 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 3.073x (185,506 tokens per question); generated tokens only as a floor, 0.3677x (22,193 tokens per question); cached-context attention 0.12x to 0.26x at the 11,000-token mean prefix over 14.8 calls per question, one-sided upward. Cached share of prompt tokens 0.766; helper share of counted tokens 0.0005.

Label `below`: 0.53 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 43,339 counted tokens per solved question against 74,953 per failed one over 12 and 14 questions, a ratio of 1.73.

## agen-gaia-hal-o3minilow-l1

HAL run `gaia_hal_generalist_agent_o3mini20250131_1744609696` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "model_name": "o3-mini-2025-01-31", "reasoning_effort": "low"}`, run date 2025-04-14), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_o3mini20250131_1744609696_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_o3mini20250131_1744609696.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 30 solved (0.5660, standard error 0.0681) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `o3-mini-2025-01-31` -> `o3-mini-2025-01-31` | primary | 1,300,666 | 659,712 | 0 | 0 | 100,720 | 45,696 | 282 | 741,674 | 4e+10 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 1,481 | 0 | 0 | 0 | 28 | 0 | 1 | 1,509 | 1e+11 |

Duplicate spans dropped run-wide: 933 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 743,183 over the level, that is **14,022.32 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 2.981786e+16 over the level, that is **5.626011e+14 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-04-14, including cache reads and the helper, **$0.0286 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.888x (26,470 tokens per question); generated tokens only as a floor, 0.1356x (1,901 tokens per question); cached-context attention 0.04x to 0.08x at the 4,601-token mean prefix over 5.3 calls per question, one-sided upward. Cached share of prompt tokens 0.507; helper share of counted tokens 0.0020.

Label `below`: 0.60 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 12,832 counted tokens per solved question against 15,575 per failed one over 30 and 23 questions, a ratio of 1.21.

## agen-gaia-hal-o3minihigh-l1

HAL run `gaia_hal_generalist_agent_o3mini20250131_high_1744670471` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "model_name": "o3-mini-2025-01-31", "reasoning_effort": "high"}`, run date 2025-04-14), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_o3mini20250131_high_1744670471_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_o3mini20250131_high_1744670471.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 31 solved (0.5849, standard error 0.0677) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `o3-mini-2025-01-31` -> `o3-mini-2025-01-31` | primary | 784,705 | 443,648 | 0 | 0 | 720,642 | 671,744 | 216 | 1,061,699 | 4e+10 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 787 | 0 | 0 | 0 | 5 | 0 | 1 | 792 | 1e+11 |

Duplicate spans dropped run-wide: 777 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 1,062,491 over the level, that is **20,047.00 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 4.254716e+16 over the level, that is **8.027766e+14 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-04-14, including cache reads and the helper, **$0.0715 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.418x (28,418 tokens per question); generated tokens only as a floor, 0.6783x (13,597 tokens per question); cached-context attention 0.03x to 0.06x at the 3,620-token mean prefix over 4.1 calls per question, one-sided upward. Cached share of prompt tokens 0.565; helper share of counted tokens 0.0007.

Label `below`: 0.62 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 20,726 counted tokens per solved question against 19,091 per failed one over 31 and 22 questions, a ratio of 0.92.

## agen-gaia-hal-o3minihigh-l2

HAL run `gaia_hal_generalist_agent_o3mini20250131_high_1744670471` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "model_name": "o3-mini-2025-01-31", "reasoning_effort": "high"}`, run date 2025-04-14), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_o3mini20250131_high_1744670471_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_o3mini20250131_high_1744670471.json`. GAIA validation Level 2: 86 questions, 86 with logged usage, 39 solved (0.4535, standard error 0.0537) against 0.918 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `o3-mini-2025-01-31` -> `o3-mini-2025-01-31` | primary | 1,585,155 | 979,968 | 0 | 0 | 1,319,774 | 1,219,584 | 412 | 1,924,961 | 4e+10 |
| `gpt-4o-2024-11-20` -> `gpt-4o-2024-11-20` | helper | 1,561 | 0 | 0 | 0 | 1,052 | 0 | 3 | 2,613 | 1e+11 |

Duplicate spans dropped run-wide: 777 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 1,927,574 over the level, that is **22,413.65 tokens per question** over 86 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 7.725974e+16 over the level, that is **8.983691e+14 FLOPs per question**. Human time 685.12 s, the mean of the 86 annotator self-reports at this level (median 450 s). At list prices on 2025-04-14, including cache reads and the helper, **$0.0817 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.508x (33,809 tokens per question); generated tokens only as a floor, 0.6852x (15,358 tokens per question); cached-context attention 0.03x to 0.06x at the 3,823-token mean prefix over 4.8 calls per question, one-sided upward. Cached share of prompt tokens 0.618; helper share of counted tokens 0.0014.

Label `below`: 0.49 of the human rate, kept under the close-calls ruling, 0.10 standard errors under the 0.5 guide on a standard error of 0.058 and short of comparable. Compute averages all attempts: 21,121 counted tokens per solved question against 23,486 per failed one over 39 and 47 questions, a ratio of 1.11.

## agen-gaia-hal-o4minihigh-l1

HAL run `gaia_hal_generalist_agent_o4mini20250416_high_1745167285` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "model_name": "o4-mini-2025-04-16", "reasoning_effort": "high"}`, run date 2025-04-20), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_o4mini20250416_high_1745167285_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_o4mini20250416_high_1745167285.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 32 solved (0.6038, standard error 0.0672) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `o4-mini-2025-04-16` -> `o4-mini-2025-04-16` | primary | 6,662,818 | 2,820,480 | 0 | 0 | 911,068 | 726,720 | 765 | 4,753,406 | 4e+10 |

Duplicate spans dropped run-wide: 2,154 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 4,753,406 over the level, that is **89,686.91 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 1.901362e+17 over the level, that is **3.587476e+15 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-04-20, including cache reads and the helper, **$0.1700 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.593x (142,904 tokens per question); generated tokens only as a floor, 0.1917x (17,190 tokens per question); cached-context attention 0.07x to 0.14x at the 8,710-token mean prefix over 14.4 calls per question, one-sided upward. Cached share of prompt tokens 0.423; helper share of counted tokens 0.0000.

Label `below`: 0.64 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 44,483 counted tokens per solved question against 158,570 per failed one over 32 and 21 questions, a ratio of 3.56.

## agen-gaia-hal-o4minihigh-l2

HAL run `gaia_hal_generalist_agent_o4mini20250416_high_1745167285` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "model_name": "o4-mini-2025-04-16", "reasoning_effort": "high"}`, run date 2025-04-20), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_o4mini20250416_high_1745167285_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_o4mini20250416_high_1745167285.json`. GAIA validation Level 2: 86 questions, 86 with logged usage, 46 solved (0.5349, standard error 0.0538) against 0.918 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `o4-mini-2025-04-16` -> `o4-mini-2025-04-16` | primary | 7,633,962 | 3,140,736 | 0 | 0 | 1,155,852 | 935,360 | 1,042 | 5,649,078 | 4e+10 |

Duplicate spans dropped run-wide: 2,154 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 5,649,078 over the level, that is **65,686.95 tokens per question** over 86 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 2.259631e+17 over the level, that is **2.627478e+15 FLOPs per question**. Human time 685.12 s, the mean of the 86 annotator self-reports at this level (median 450 s). At list prices on 2025-04-20, including cache reads and the helper, **$0.1267 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.556x (102,207 tokens per question); generated tokens only as a floor, 0.2046x (13,440 tokens per question); cached-context attention 0.06x to 0.12x at the 7,326-token mean prefix over 12.1 calls per question, one-sided upward. Cached share of prompt tokens 0.411; helper share of counted tokens 0.0000.

Label `below`: 0.58 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 58,860 counted tokens per solved question against 73,538 per failed one over 46 and 40 questions, a ratio of 1.25.

## agen-gaia-hal-o4minihigh-l3

HAL run `gaia_hal_generalist_agent_o4mini20250416_high_1745167285` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "model_name": "o4-mini-2025-04-16", "reasoning_effort": "high"}`, run date 2025-04-20), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_o4mini20250416_high_1745167285_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_o4mini20250416_high_1745167285.json`. GAIA validation Level 3: 26 questions, 26 with logged usage, 12 solved (0.4615, standard error 0.0978) against 0.873 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `o4-mini-2025-04-16` -> `o4-mini-2025-04-16` | primary | 2,582,191 | 1,128,448 | 0 | 0 | 462,352 | 376,960 | 347 | 1,916,095 | 4e+10 |

Duplicate spans dropped run-wide: 2,154 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 1,916,095 over the level, that is **73,695.96 tokens per question** over 26 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 7.664380e+16 over the level, that is **2.947838e+15 FLOPs per question**. Human time 1232.31 s, the mean of the 26 annotator self-reports at this level (median 900 s). At list prices on 2025-04-20, including cache reads and the helper, **$0.1517 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.589x (117,098 tokens per question); generated tokens only as a floor, 0.2413x (17,783 tokens per question); cached-context attention 0.06x to 0.12x at the 7,441-token mean prefix over 13.3 calls per question, one-sided upward. Cached share of prompt tokens 0.437; helper share of counted tokens 0.0000.

Label `below`: 0.53 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 33,332 counted tokens per solved question against 108,294 per failed one over 12 and 14 questions, a ratio of 3.25.

## agen-gaia-hal-o4minilow-l1

HAL run `gaia_hal_generalist_agent_o4mini20250416_low_1745167262` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "o4-mini-2025-04-16", "reasoning_effort": "low"}`, run date 2025-04-23), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_o4mini20250416_low_1745167262_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_o4mini20250416_low_1745167262.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 38 solved (0.7170, standard error 0.0619) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `o4-mini-2025-04-16` -> `o4-mini-2025-04-16` | primary | 7,506,853 | 3,183,360 | 0 | 0 | 798,233 | 628,608 | 710 | 5,121,726 | 4e+10 |

Duplicate spans dropped run-wide: 2,105 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 5,121,726 over the level, that is **96,636.34 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 2.048690e+17 over the level, that is **3.865454e+15 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-04-23, including cache reads and the helper, **$0.1725 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.622x (156,700 tokens per question); generated tokens only as a floor, 0.1559x (15,061 tokens per question); cached-context attention 0.09x to 0.17x at the 10,573-token mean prefix over 13.4 calls per question, one-sided upward. Cached share of prompt tokens 0.424; helper share of counted tokens 0.0000.

Label `below`: 0.76 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 80,826 counted tokens per solved question against 136,688 per failed one over 38 and 15 questions, a ratio of 1.69.

## agen-gaia-hal-o4minilow-l2

HAL run `gaia_hal_generalist_agent_o4mini20250416_low_1745167262` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "o4-mini-2025-04-16", "reasoning_effort": "low"}`, run date 2025-04-23), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_o4mini20250416_low_1745167262_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_o4mini20250416_low_1745167262.json`. GAIA validation Level 2: 86 questions, 86 with logged usage, 44 solved (0.5116, standard error 0.0539) against 0.918 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `o4-mini-2025-04-16` -> `o4-mini-2025-04-16` | primary | 10,347,083 | 3,559,168 | 0 | 0 | 1,251,068 | 1,021,760 | 1,030 | 8,038,983 | 4e+10 |

Duplicate spans dropped run-wide: 2,105 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 8,038,983 over the level, that is **93,476.55 tokens per question** over 86 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 3.215593e+17 over the level, that is **3.739062e+15 FLOPs per question**. Human time 685.12 s, the mean of the 86 annotator self-reports at this level (median 450 s). At list prices on 2025-04-23, including cache reads and the helper, **$0.1622 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.443x (134,862 tokens per question); generated tokens only as a floor, 0.1556x (14,547 tokens per question); cached-context attention 0.08x to 0.16x at the 10,046-token mean prefix over 12.0 calls per question, one-sided upward. Cached share of prompt tokens 0.344; helper share of counted tokens 0.0000.

Label `below`: 0.56 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 36,019 counted tokens per solved question against 153,671 per failed one over 44 and 42 questions, a ratio of 4.27.

## agen-gaia-hal-o4minilow-l3

HAL run `gaia_hal_generalist_agent_o4mini20250416_low_1745167262` (HAL Generalist Agent, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "o4-mini-2025-04-16", "reasoning_effort": "low"}`, run date 2025-04-23), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hal_generalist_agent_o4mini20250416_low_1745167262_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hal_generalist_agent_o4mini20250416_low_1745167262.json`. GAIA validation Level 3: 26 questions, 26 with logged usage, 14 solved (0.5385, standard error 0.0978) against 0.873 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `o4-mini-2025-04-16` -> `o4-mini-2025-04-16` | primary | 5,393,611 | 2,572,800 | 0 | 0 | 463,332 | 378,880 | 365 | 3,284,143 | 4e+10 |

Duplicate spans dropped run-wide: 2,105 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 3,284,143 over the level, that is **126,313.19 tokens per question** over 26 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 1.313657e+17 over the level, that is **5.052528e+15 FLOPs per question**. Human time 1232.31 s, the mean of the 26 annotator self-reports at this level (median 900 s). At list prices on 2025-04-23, including cache reads and the helper, **$0.2250 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.783x (225,267 tokens per question); generated tokens only as a floor, 0.1411x (17,820 tokens per question); cached-context attention 0.12x to 0.24x at the 14,777-token mean prefix over 14.0 calls per question, one-sided upward. Cached share of prompt tokens 0.477; helper share of counted tokens 0.0000.

Label `below`: 0.62 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 68,782 counted tokens per solved question against 193,433 per failed one over 14 and 12 questions, a ratio of 2.81.

## agen-gaia-odr-sonnet37high-l1

HAL run `gaia_hf_open_deep_research_claude37sonnet20250219_high_1745539901` (HF Open Deep Research, arguments `{"benchmark_name": "gaia", "model_name": "claude-3-7-sonnet-20250219", "reasoning_effort": "high"}`, run date 2025-04-25), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hf_open_deep_research_claude37sonnet20250219_high_1745539901_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hf_open_deep_research_claude37sonnet20250219_high_1745539901.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 24 solved (0.4528, standard error 0.0684) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `claude-3-7-sonnet-20250219` -> `claude-3-7-sonnet` | primary | 5,243,246 | 0 | 0 | 0 | 836,085 | 358,907 | 1,040 | 6,079,331 | 2e+11 |

Duplicate spans dropped run-wide: 0 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 6,079,331 over the level, that is **114,704.36 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 1.215866e+18 over the level, that is **2.294087e+16 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-04-25, including cache reads and the helper, **$0.5334 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (114,704 tokens per question); generated tokens only as a floor, 0.1375x (15,775 tokens per question); cached-context attention 0.05x to 0.12x at the 5,042-token mean prefix over 19.6 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0000.

Label `below`: 0.48 of the human rate, kept under the close-calls ruling, 0.24 standard errors under the 0.5 guide on a standard error of 0.073 and short of comparable. Compute averages all attempts: 79,092 counted tokens per solved question against 144,176 per failed one over 24 and 29 questions, a ratio of 1.82.

## agen-gaia-odr-opus41-l1

HAL run `gaia_hf_open_deep_research_claudeopus41_1755030930` (HF Open Deep Research, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "openrouter/anthropic/claude-opus-4.1"}`, run date 2025-08-13), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hf_open_deep_research_claudeopus41_1755030930_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hf_open_deep_research_claudeopus41_1755030930.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 22 solved (0.4151, standard error 0.0677) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `anthropic/claude-opus-4.1` -> `claude-opus-4-1` | primary | 12,807,976 | 0 | 0 | 0 | 364,828 | 0 | 1,120 | 13,172,804 | 3.6e+11 |

Duplicate spans dropped run-wide: 0 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 13,172,804 over the level, that is **248,543.47 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 4.742209e+18 over the level, that is **8.947565e+16 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-08-13, including cache reads and the helper, **$4.1412 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (248,543 tokens per question); generated tokens only as a floor, 0.0277x (6,884 tokens per question); cached-context attention 0.10x to 0.25x at the 11,436-token mean prefix over 21.1 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0000.

Label `below`: 0.44 of the human rate, kept under the close-calls ruling, 0.80 standard errors under the 0.5 guide on a standard error of 0.072 and short of comparable. Compute averages all attempts: 244,617 counted tokens per solved question against 251,330 per failed one over 22 and 31 questions, a ratio of 1.03.

## agen-gaia-odr-opus4-l1

HAL run `gaia_hf_open_deep_research_claudeopus4_1754425534` (HF Open Deep Research, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "openrouter/anthropic/claude-opus-4"}`, run date 2025-08-07), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hf_open_deep_research_claudeopus4_1754425534_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hf_open_deep_research_claudeopus4_1754425534.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 35 solved (0.6604, standard error 0.0651) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `anthropic/claude-opus-4` -> `claude-opus-4` | primary | 15,446,800 | 0 | 0 | 0 | 294,679 | 0 | 1,276 | 15,741,479 | 3.6e+11 |

Duplicate spans dropped run-wide: 0 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 15,741,479 over the level, that is **297,009.04 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 5.666932e+18 over the level, that is **1.069233e+17 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-08-07, including cache reads and the helper, **$4.7887 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (297,009 tokens per question); generated tokens only as a floor, 0.0187x (5,560 tokens per question); cached-context attention 0.11x to 0.26x at the 12,106-token mean prefix over 24.1 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0000.

Label `below`: 0.70 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 298,115 counted tokens per solved question against 294,858 per failed one over 35 and 18 questions, a ratio of 0.99.

## agen-gaia-odr-opus4-l2

HAL run `gaia_hf_open_deep_research_claudeopus4_1754425534` (HF Open Deep Research, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "openrouter/anthropic/claude-opus-4"}`, run date 2025-08-07), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hf_open_deep_research_claudeopus4_1754425534_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hf_open_deep_research_claudeopus4_1754425534.json`. GAIA validation Level 2: 86 questions, 86 with logged usage, 49 solved (0.5698, standard error 0.0534) against 0.918 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `anthropic/claude-opus-4` -> `claude-opus-4` | primary | 53,906,779 | 0 | 0 | 0 | 788,857 | 0 | 3,779 | 54,695,636 | 3.6e+11 |

Duplicate spans dropped run-wide: 0 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 54,695,636 over the level, that is **635,995.77 tokens per question** over 86 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 1.969043e+19 over the level, that is **2.289585e+17 FLOPs per question**. Human time 685.12 s, the mean of the 86 annotator self-reports at this level (median 450 s). At list prices on 2025-08-07, including cache reads and the helper, **$10.0903 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (635,996 tokens per question); generated tokens only as a floor, 0.0144x (9,173 tokens per question); cached-context attention 0.13x to 0.31x at the 14,265-token mean prefix over 43.9 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0000.

Label `below`: 0.62 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 524,801 counted tokens per solved question against 783,254 per failed one over 49 and 37 questions, a ratio of 1.49.

## agen-gaia-odr-opus4-l3

HAL run `gaia_hf_open_deep_research_claudeopus4_1754425534` (HF Open Deep Research, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "openrouter/anthropic/claude-opus-4"}`, run date 2025-08-07), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hf_open_deep_research_claudeopus4_1754425534_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hf_open_deep_research_claudeopus4_1754425534.json`. GAIA validation Level 3: 26 questions, 26 with logged usage, 11 solved (0.4231, standard error 0.0969) against 0.873 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `anthropic/claude-opus-4` -> `claude-opus-4` | primary | 34,901,870 | 0 | 0 | 0 | 546,355 | 0 | 2,198 | 35,448,225 | 3.6e+11 |

Duplicate spans dropped run-wide: 0 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 35,448,225 over the level, that is **1,363,393.27 tokens per question** over 26 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 1.276136e+19 over the level, that is **4.908216e+17 FLOPs per question**. Human time 1232.31 s, the mean of the 26 annotator self-reports at this level (median 900 s). At list prices on 2025-08-07, including cache reads and the helper, **$21.7117 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.000x (1,363,393 tokens per question); generated tokens only as a floor, 0.0154x (21,014 tokens per question); cached-context attention 0.14x to 0.35x at the 15,879-token mean prefix over 84.5 calls per question, one-sided upward. Cached share of prompt tokens 0.000; helper share of counted tokens 0.0000.

Label `below`: 0.48 of the human rate, kept under the close-calls ruling, 0.14 standard errors under the 0.5 guide on a standard error of 0.111 and short of comparable. Compute averages all attempts: 927,776 counted tokens per solved question against 1,682,846 per failed one over 11 and 15 questions, a ratio of 1.81.

## agen-gaia-odr-gpt41-l1

HAL run `gaia_hf_open_deep_research_gpt4120250414_1744843595` (HF Open Deep Research, arguments `{"benchmark_name": "gaia", "model_name": "gpt-4.1-2025-04-14"}`, run date 2025-04-17), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hf_open_deep_research_gpt4120250414_1744843595_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hf_open_deep_research_gpt4120250414_1744843595.json`. GAIA validation Level 1: 53 questions, 52 with logged usage, 31 solved (0.5849, standard error 0.0677) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gpt-4.1-2025-04-14` -> `gpt-4.1-2025-04-14` | primary | 5,098,338 | 3,199,232 | 0 | 0 | 139,862 | 0 | 719 | 2,038,968 | 1e+11 |

Duplicate spans dropped run-wide: 2,863 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 2,038,968 over the level, that is **39,210.92 tokens per question** over 52 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 2.038968e+17 over the level, that is **3.921092e+15 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-04-17, including cache reads and the helper, **$0.1253 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 2.569x (100,735 tokens per question); generated tokens only as a floor, 0.0686x (2,690 tokens per question); cached-context attention 0.07x to 0.15x at the 7,091-token mean prefix over 13.8 calls per question, one-sided upward. Cached share of prompt tokens 0.628; helper share of counted tokens 0.0000.

Label `below`: 0.62 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 36,958 counted tokens per solved question against 42,536 per failed one over 31 and 21 questions, a ratio of 1.15.

## agen-gaia-odr-gpt41-l2

HAL run `gaia_hf_open_deep_research_gpt4120250414_1744843595` (HF Open Deep Research, arguments `{"benchmark_name": "gaia", "model_name": "gpt-4.1-2025-04-14"}`, run date 2025-04-17), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hf_open_deep_research_gpt4120250414_1744843595_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hf_open_deep_research_gpt4120250414_1744843595.json`. GAIA validation Level 2: 86 questions, 86 with logged usage, 43 solved (0.5000, standard error 0.0539) against 0.918 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gpt-4.1-2025-04-14` -> `gpt-4.1-2025-04-14` | primary | 15,137,471 | 9,515,520 | 0 | 0 | 300,420 | 0 | 1,550 | 5,922,371 | 1e+11 |

Duplicate spans dropped run-wide: 2,863 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 5,922,371 over the level, that is **68,864.78 tokens per question** over 86 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 5.922371e+17 over the level, that is **6.886478e+15 FLOPs per question**. Human time 685.12 s, the mean of the 86 annotator self-reports at this level (median 450 s). At list prices on 2025-04-17, including cache reads and the helper, **$0.2140 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 2.607x (179,510 tokens per question); generated tokens only as a floor, 0.0507x (3,493 tokens per question); cached-context attention 0.10x to 0.20x at the 9,766-token mean prefix over 18.0 calls per question, one-sided upward. Cached share of prompt tokens 0.629; helper share of counted tokens 0.0000.

Label `below`: 0.54 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 55,624 counted tokens per solved question against 82,106 per failed one over 43 and 43 questions, a ratio of 1.48.

## agen-gaia-odr-gpt41-l3

HAL run `gaia_hf_open_deep_research_gpt4120250414_1744843595` (HF Open Deep Research, arguments `{"benchmark_name": "gaia", "model_name": "gpt-4.1-2025-04-14"}`, run date 2025-04-17), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hf_open_deep_research_gpt4120250414_1744843595_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hf_open_deep_research_gpt4120250414_1744843595.json`. GAIA validation Level 3: 26 questions, 26 with logged usage, 9 solved (0.3462, standard error 0.0933) against 0.873 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gpt-4.1-2025-04-14` -> `gpt-4.1-2025-04-14` | primary | 4,950,110 | 3,159,552 | 0 | 0 | 130,527 | 0 | 594 | 1,921,085 | 1e+11 |

Duplicate spans dropped run-wide: 2,863 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 1,921,085 over the level, that is **73,887.88 tokens per question** over 26 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 1.921085e+17 over the level, that is **7.388788e+15 FLOPs per question**. Human time 1232.31 s, the mean of the 26 annotator self-reports at this level (median 900 s). At list prices on 2025-04-17, including cache reads and the helper, **$0.2387 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 2.645x (195,409 tokens per question); generated tokens only as a floor, 0.0679x (5,020 tokens per question); cached-context attention 0.08x to 0.17x at the 8,334-token mean prefix over 22.8 calls per question, one-sided upward. Cached share of prompt tokens 0.638; helper share of counted tokens 0.0000.

Label `below`: 0.40 of the human rate, kept under the close-calls ruling, 0.97 standard errors under the 0.5 guide on a standard error of 0.107 and short of comparable. Compute averages all attempts: 66,182 counted tokens per solved question against 77,968 per failed one over 9 and 17 questions, a ratio of 1.18.

## agen-gaia-odr-gpt5-l1

HAL run `gaia_hf_open_deep_research_gpt520250807_1754605128` (HF Open Deep Research, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "gpt-5-2025-08-07"}`, run date 2025-08-09), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hf_open_deep_research_gpt520250807_1754605128_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hf_open_deep_research_gpt520250807_1754605128.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 39 solved (0.7358, standard error 0.0606) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gpt-5-2025-08-07` -> `gpt-5` | primary | 11,411,618 | 1,425,024 | 0 | 0 | 1,252,084 | 943,040 | 956 | 11,238,678 | 2e+11 |

Duplicate spans dropped run-wide: 5,765 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 11,238,678 over the level, that is **212,050.53 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 2.247736e+18 over the level, that is **4.241011e+16 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-08-09, including cache reads and the helper, **$0.4751 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.127x (238,938 tokens per question); generated tokens only as a floor, 0.1114x (23,624 tokens per question); cached-context attention 0.13x to 0.28x at the 11,937-token mean prefix over 18.0 calls per question, one-sided upward. Cached share of prompt tokens 0.125; helper share of counted tokens 0.0000.

Label `below`: 0.78 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 204,500 counted tokens per solved question against 233,083 per failed one over 39 and 14 questions, a ratio of 1.14.

## agen-gaia-odr-gpt5-l2

HAL run `gaia_hf_open_deep_research_gpt520250807_1754605128` (HF Open Deep Research, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "gpt-5-2025-08-07"}`, run date 2025-08-09), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hf_open_deep_research_gpt520250807_1754605128_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hf_open_deep_research_gpt520250807_1754605128.json`. GAIA validation Level 2: 86 questions, 86 with logged usage, 54 solved (0.6279, standard error 0.0521) against 0.918 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gpt-5-2025-08-07` -> `gpt-5` | primary | 44,469,559 | 5,151,232 | 0 | 0 | 3,849,511 | 2,807,104 | 3,170 | 43,167,838 | 2e+11 |

Duplicate spans dropped run-wide: 5,765 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 43,167,838 over the level, that is **501,951.60 tokens per question** over 86 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 8.633568e+18 over the level, that is **1.003903e+17 FLOPs per question**. Human time 685.12 s, the mean of the 86 annotator self-reports at this level (median 450 s). At list prices on 2025-08-09, including cache reads and the helper, **$1.0266 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.119x (561,850 tokens per question); generated tokens only as a floor, 0.0892x (44,762 tokens per question); cached-context attention 0.15x to 0.33x at the 14,028-token mean prefix over 36.9 calls per question, one-sided upward. Cached share of prompt tokens 0.116; helper share of counted tokens 0.0000.

Label `below`: 0.68 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 359,881 counted tokens per solved question against 741,696 per failed one over 54 and 32 questions, a ratio of 2.06.

## agen-gaia-odr-gpt5-l3

HAL run `gaia_hf_open_deep_research_gpt520250807_1754605128` (HF Open Deep Research, arguments `{"benchmark_name": "gaia", "budget": 99999, "model_name": "gpt-5-2025-08-07"}`, run date 2025-08-09), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hf_open_deep_research_gpt520250807_1754605128_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hf_open_deep_research_gpt520250807_1754605128.json`. GAIA validation Level 3: 26 questions, 26 with logged usage, 10 solved (0.3846, standard error 0.0954) against 0.873 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gpt-5-2025-08-07` -> `gpt-5` | primary | 28,388,149 | 3,197,184 | 0 | 0 | 2,356,013 | 1,738,880 | 1,639 | 27,546,978 | 2e+11 |

Duplicate spans dropped run-wide: 5,765 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 27,546,978 over the level, that is **1,059,499.15 tokens per question** over 26 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 5.509396e+18 over the level, that is **2.118998e+17 FLOPs per question**. Human time 1232.31 s, the mean of the 26 annotator self-reports at this level (median 900 s). At list prices on 2025-08-09, including cache reads and the helper, **$2.1326 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.116x (1,182,468 tokens per question); generated tokens only as a floor, 0.0855x (90,616 tokens per question); cached-context attention 0.18x to 0.41x at the 17,320-token mean prefix over 63.0 calls per question, one-sided upward. Cached share of prompt tokens 0.113; helper share of counted tokens 0.0000.

Label `below`: 0.44 of the human rate, kept under the close-calls ruling, 0.54 standard errors under the 0.5 guide on a standard error of 0.109 and short of comparable. Compute averages all attempts: 427,558 counted tokens per solved question against 1,454,463 per failed one over 10 and 16 questions, a ratio of 3.40.

## agen-gaia-odr-o4minihigh-l1

HAL run `gaia_hf_open_deep_research_o4mini20250416_high_1744923206` (HF Open Deep Research, arguments `{"benchmark_name": "gaia", "model_name": "o4-mini-2025-04-16", "reasoning_effort": "high"}`, run date 2025-04-18), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hf_open_deep_research_o4mini20250416_high_1744923206_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hf_open_deep_research_o4mini20250416_high_1744923206.json`. GAIA validation Level 1: 53 questions, 53 with logged usage, 37 solved (0.6981, standard error 0.0631) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `o4-mini-2025-04-16` -> `o4-mini-2025-04-16` | primary | 15,086,554 | 4,578,432 | 0 | 0 | 2,025,995 | 1,801,856 | 1,207 | 12,534,117 | 4e+10 |

Duplicate spans dropped run-wide: 4,254 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 12,534,117 over the level, that is **236,492.77 tokens per question** over 53 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 5.013647e+17 over the level, that is **9.459711e+15 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-04-18, including cache reads and the helper, **$0.4100 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.365x (322,878 tokens per question); generated tokens only as a floor, 0.1616x (38,226 tokens per question); cached-context attention 0.10x to 0.20x at the 12,499-token mean prefix over 22.8 calls per question, one-sided upward. Cached share of prompt tokens 0.303; helper share of counted tokens 0.0000.

Label `below`: 0.74 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 199,008 counted tokens per solved question against 323,177 per failed one over 37 and 16 questions, a ratio of 1.62.

## agen-gaia-odr-o4minihigh-l2

HAL run `gaia_hf_open_deep_research_o4mini20250416_high_1744923206` (HF Open Deep Research, arguments `{"benchmark_name": "gaia", "model_name": "o4-mini-2025-04-16", "reasoning_effort": "high"}`, run date 2025-04-18), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hf_open_deep_research_o4mini20250416_high_1744923206_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hf_open_deep_research_o4mini20250416_high_1744923206.json`. GAIA validation Level 2: 86 questions, 86 with logged usage, 44 solved (0.5116, standard error 0.0539) against 0.918 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `o4-mini-2025-04-16` -> `o4-mini-2025-04-16` | primary | 27,141,398 | 8,139,392 | 0 | 0 | 4,114,076 | 3,686,336 | 2,227 | 23,116,082 | 4e+10 |

Duplicate spans dropped run-wide: 4,254 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 23,116,082 over the level, that is **268,791.65 tokens per question** over 86 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 9.246433e+17 over the level, that is **1.075167e+16 FLOPs per question**. Human time 685.12 s, the mean of the 86 annotator self-reports at this level (median 450 s). At list prices on 2025-04-18, including cache reads and the helper, **$0.4796 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.352x (363,436 tokens per question); generated tokens only as a floor, 0.1780x (47,838 tokens per question); cached-context attention 0.10x to 0.20x at the 12,187-token mean prefix over 25.9 calls per question, one-sided upward. Cached share of prompt tokens 0.300; helper share of counted tokens 0.0000.

Label `below`: 0.56 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 229,621 counted tokens per solved question against 309,828 per failed one over 44 and 42 questions, a ratio of 1.35.

## agen-gaia-odr-o4minihigh-l3

HAL run `gaia_hf_open_deep_research_o4mini20250416_high_1744923206` (HF Open Deep Research, arguments `{"benchmark_name": "gaia", "model_name": "o4-mini-2025-04-16", "reasoning_effort": "high"}`, run date 2025-04-18), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hf_open_deep_research_o4mini20250416_high_1744923206_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hf_open_deep_research_o4mini20250416_high_1744923206.json`. GAIA validation Level 3: 26 questions, 26 with logged usage, 11 solved (0.4231, standard error 0.0969) against 0.873 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `o4-mini-2025-04-16` -> `o4-mini-2025-04-16` | primary | 10,575,950 | 2,881,024 | 0 | 0 | 1,666,423 | 1,465,728 | 820 | 9,361,349 | 4e+10 |

Duplicate spans dropped run-wide: 4,254 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 9,361,349 over the level, that is **360,051.88 tokens per question** over 26 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 3.744540e+17 over the level, that is **1.440208e+16 FLOPs per question**. Human time 1232.31 s, the mean of the 26 annotator self-reports at this level (median 900 s). At list prices on 2025-04-18, including cache reads and the helper, **$0.6380 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.308x (470,860 tokens per question); generated tokens only as a floor, 0.1780x (64,093 tokens per question); cached-context attention 0.10x to 0.21x at the 12,898-token mean prefix over 31.5 calls per question, one-sided upward. Cached share of prompt tokens 0.272; helper share of counted tokens 0.0000.

Label `below`: 0.48 of the human rate, kept under the close-calls ruling, 0.14 standard errors under the 0.5 guide on a standard error of 0.111 and short of comparable. Compute averages all attempts: 87,851 counted tokens per solved question against 559,666 per failed one over 11 and 15 questions, a ratio of 6.37.

## agen-gaia-odr-o4minilow-l1

HAL run `gaia_hf_open_deep_research_o4mini20250416_low_1744921254` (HF Open Deep Research, arguments `{"benchmark_name": "gaia", "model_name": "o4-mini-2025-04-16", "reasoning_effort": "low"}`, run date 2025-04-17), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hf_open_deep_research_o4mini20250416_low_1744921254_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hf_open_deep_research_o4mini20250416_low_1744921254.json`. GAIA validation Level 1: 53 questions, 52 with logged usage, 31 solved (0.5849, standard error 0.0677) against 0.939 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `o4-mini-2025-04-16` -> `o4-mini-2025-04-16` | primary | 10,358,163 | 3,157,120 | 0 | 0 | 278,516 | 100,608 | 1,011 | 7,479,559 | 4e+10 |

Duplicate spans dropped run-wide: 3,307 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 7,479,559 over the level, that is **143,837.67 tokens per question** over 52 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 2.991824e+17 over the level, that is **5.753507e+15 FLOPs per question**. Human time 403.02 s, the mean of the 53 annotator self-reports at this level (median 300 s). At list prices on 2025-04-17, including cache reads and the helper, **$0.1926 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.422x (204,552 tokens per question); generated tokens only as a floor, 0.0372x (5,356 tokens per question); cached-context attention 0.08x to 0.17x at the 10,245-token mean prefix over 19.4 calls per question, one-sided upward. Cached share of prompt tokens 0.305; helper share of counted tokens 0.0000.

Label `below`: 0.62 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 106,306 counted tokens per solved question against 199,242 per failed one over 31 and 21 questions, a ratio of 1.87.

## agen-gaia-odr-o4minilow-l2

HAL run `gaia_hf_open_deep_research_o4mini20250416_low_1744921254` (HF Open Deep Research, arguments `{"benchmark_name": "gaia", "model_name": "o4-mini-2025-04-16", "reasoning_effort": "low"}`, run date 2025-04-17), [trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/gaia_hf_open_deep_research_o4mini20250416_low_1744921254_UPLOAD.zip), reduced to `agent-work/sources/gaia/hal-run-summaries/gaia_hf_open_deep_research_o4mini20250416_low_1744921254.json`. GAIA validation Level 2: 86 questions, 86 with logged usage, 41 solved (0.4767, standard error 0.0539) against 0.918 for the human annotators at this level.

| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `o4-mini-2025-04-16` -> `o4-mini-2025-04-16` | primary | 16,517,142 | 5,118,592 | 0 | 0 | 506,879 | 191,104 | 1,712 | 11,905,429 | 4e+10 |

Duplicate spans dropped run-wide: 3,307 usage-bearing parents whose child carries the same block. Counted tokens are `(prompt - cached) + cache write + output`, summing to 11,905,429 over the level, that is **138,435.22 tokens per question** over 86 questions with usage. FLOPs are the per-model counted totals times each model's coefficient, 4.762172e+17 over the level, that is **5.537409e+15 FLOPs per question**. Human time 685.12 s, the mean of the 86 annotator self-reports at this level (median 450 s). At list prices on 2025-04-17, including cache reads and the helper, **$0.1881 per question**.

Scenarios, none of them entering `compute_flops` except the attention term, which `research/attention-correction.md` has since folded in: charging the whole prefix with no cache credit, 1.430x (197,954 tokens per question); generated tokens only as a floor, 0.0426x (5,894 tokens per question); cached-context attention 0.08x to 0.16x at the 9,648-token mean prefix over 19.9 calls per question, one-sided upward. Cached share of prompt tokens 0.310; helper share of counted tokens 0.0000.

Label `below`: 0.52 of the human rate, above the half-of-human retention bar and short of comparable. Compute averages all attempts: 126,890 counted tokens per solved question against 148,954 per failed one over 41 and 45 questions, a ratio of 1.17.
