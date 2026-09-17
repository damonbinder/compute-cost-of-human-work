# Epoch AI SWE-bench Verified, resolved by OpenAI difficulty bin

*Created 2026-09-13 12:06.*
*Last revised 2026-09-13 13:04, applying Revision 2: the coordinator's two note-only corrections on the recheck. No CSV changed.*
*Last revised 2026-09-14 12:55, moving attention_context onto the cache-implied mean prefix on all 92 rows.*

## Summary

One hundred and twenty-four candidate rows, one per run per difficulty bin, over 31 of the 32
readable Epoch AI SWE-bench Verified logs. Both sides are per-instance: the AI side is Epoch's
own `model_usage` counters for each of the 484 issues in each run, and the human side is the
`difficulty` label OpenAI's annotators attached to that same issue. The four bins carry human
times of **450, 2,250, 9,000, and 21,600 seconds**; `compute_flops` runs from **2.25e15** (Kimi
K2.5, under 15 minutes) to **1.88e17** (GPT-5.2 high, over 4 hours), on **18,006 to 940,567**
counted tokens per completed evaluation.

The headline is that the two sides scale apart. Human time rises **20×** from the first bin to
the third; measured tokens rise **1.21× to 5.84×**, median **2.27×**. Over the same span the
resolved rate falls from a median of **0.854** to **0.381**. Twenty-five of the 31 runs already
have a benchmark-wide row in the dataset, and all 25 sit at a single human time, 2,267.67
seconds, which is exactly the bin-weighted mean of the four values above; they therefore hide
the only human-time variation this source has.

The 32nd run, `epoch/qwen3.6-plus`, is **held out of the CSV**: Inspect's 2,000,000-token budget
binds on 42.2%, 67.7%, 97.6%, and 66.7% of the instances in its four bins, so its recorded
totals are the harness cap rather than the model's workload. See
[The qwen3.6-plus disposition](#the-qwen36-plus-disposition).

Three assumptions dominate. First, the human times are bin midpoints assigned to annotator
*estimates*: nobody was timed. Second, 24 of the 28 distinct model coefficients here are
estimated active parameter counts, which scale `compute_flops` linearly and are under separate
review. Third, cache reads are excluded from the counted workload, and the attention over them
that the `2 * active_parameters` convention drops is worth **0.05× to 1.09×** of the
parameter-only value and is now inside `compute_flops` (`research/attention-correction.md`); see [Cached-context attention](#cached-context-attention).

**Reviewer's first checks**, in order: the human-time mapping in [Human time bins](#human-time-bins);
the [over-4-hours decision](#the-over-4-hours-bin), which is the only real judgment call here;
and the counted-workload rule table in [Counted token workload](#counted-token-workload), which
differs by provider and is the thing that would silently corrupt every number if wrong.

## What is new, and what these rows replace

The dataset already has 25 rows over 25 of these logs. Each carries
`human_time = 2267.6652892561983` seconds and one benchmark-wide token mean. Nothing about the
compute accounting changes for those: the four bin rows for such a run re-aggregate, to
floating-point precision, to that run's existing token value and to its existing human time.
`build_bin_rows.py` asserts both identities for all 25 and fails if either breaks. What is new
is that the 484 issues are split into the four groups the source itself defines, so a row's
human time and its compute describe the same subset of issues rather than the same benchmark
average.

The other six runs in the CSV have no existing dataset row. Their bin rows say so in `notes` and
are their only representation. They are listed in [Logs read, and logs not read](#logs-read-and-logs-not-read).

### The 24 parent rows to delete at merge, and one to flag

`incorporate.py` appends batch rows to `dataset/points.csv` and asserts that no batch point ID
already exists. It has no remove, replace, or supersede path, so running it on this batch as
written leaves 24 model runs represented twice: once as a parent and once as four bins whose
completed-weighted mean reproduces that parent exactly. The double-count is exact and will not
surface as an inconsistency. Each bin row's `notes` names its parent, but nothing executes that.

**The merge plan must delete these 24 rows from `dataset/points.csv`:**

`agen-epoch-swebench-dsv4promax`, `agen-epoch-swebench-gemini25pro`,
`agen-epoch-swebench-gemini31pro-ct`, `agen-epoch-swebench-gemini35flash`,
`agen-epoch-swebench-gemini3flash`, `agen-epoch-swebench-gemini3pro`,
`agen-epoch-swebench-glm5`, `agen-epoch-swebench-glm52max`, `agen-epoch-swebench-gpt41`,
`agen-epoch-swebench-gpt51high`, `agen-epoch-swebench-gpt52high`,
`agen-epoch-swebench-gpt53codex`, `agen-epoch-swebench-gpt5mini`,
`agen-epoch-swebench-kimik25`, `agen-epoch-swebench-kimik26`, `agen-epoch-swebench-o3med`,
`agen-epoch-swebench-opus4`, `agen-epoch-swebench-opus41`, `agen-epoch-swebench-opus45`,
`agen-epoch-swebench-opus46`, `agen-epoch-swebench-opus47max`,
`agen-epoch-swebench-qwen37max`, `agen-epoch-swebench-sonnet45`,
`agen-epoch-swebench-sonnet46`.

**`agen-epoch-swebench-qwen36plus` is not on that list.** Its four bin rows are held, so deleting
it would drop the run from the dataset entirely, and it is the one parent with no replacement
here. It should be **flagged, not deleted**: the row stays, and it takes the cap statement its
bin rows would have carried, since the parent has the same defect at benchmark grain. Epoch's
2,000,000-token budget binds on 42.2%, 67.7%, 97.6%, and 66.7% of the instances in its four
bins, and on 293 of all 484 instances, so its 1,535,392 tokens per completed evaluation is
substantially the harness budget rather than the model's workload.

**There is nowhere to put either disposition yet.** The current Codex dataset directory holds
`points.csv`, `models.csv`, `COLUMNS.md`, `AGENTS.md`, `README.md`, `inspect.html`, `research/`,
and `agent-work/sources/`, and no quarantine or superseded-rows file of any kind. The pattern to build on is
the legacy pilot's, at `../AI Compute vs Human Time/research/superseded_rows.csv` and its
companion `superseded_rows.md`: when the four candidate blocks were promoted on 2026-08-26, 15
coarse rows were removed from their source files because finer-grain rows built from the same
underlying runs replaced them, and each removed row was preserved in full, with every canonical
column plus a `source_file` and a `reason` field, alongside a note saying what superseded what.
The `.md` states the principle these bin rows also rely on: a superseded row is not invalid, it
was correct at its grain, and keeping both grains would double-count the same evidence in
medians and plots. The merge plan needs the same two artifacts created under `dataset/`, plus a
quarantine entry for the flagged qwen3.6-plus parent, which is a different disposition: not
superseded by anything, held because its measurement is censored.

A second merge-plan item, not a row problem: the `Reproduction` block and the allowance
paragraph below point at `../AI Compute vs Human Time/dataset/...`. `incorporate.py` rewrites
`research/` and `agent-work/sources/` prefixes inside CSV source fields only, not inside notes, so those
relative paths break at the destination. This affects every note in the folder.

## Human time bins

SWE-bench Verified ships a `difficulty` column. It comes from the annotation pass OpenAI ran
over 500 SWE-bench instances, whose instructions are retained at
`agent-work/sources/epoch-swebench-bins/swe-b-annotation-instructions.pdf` (SHA256
`e01984a0b248028ae014fdc07d4c497d473bb71e9a176ddf59385f0ad6b660b9`, downloaded 2026-09-13 from
https://cdn.openai.com/introducing-swe-bench-verified/swe-b-annotation-instructions.pdf).
Section 3, question 3.1, on PDF page 4, asks the annotator:

> How long would it take (for an experienced software engineer who had a few hours to
> familiarize themselves with the codebase) to understand the problem described in the GitHub
> issue, arrive at a solution and write the code for a solution?

with four options: `<15 min fix`, `15 min - 1 hour`, `1-4 hours`, and a fourth whose
greater-than sign the PDF's text layer drops but which the dataset's own label column spells
`>4 hours`. Each option carries an illustrative example; the fourth is "a very esoteric issue
that clearly requires a substantial amount of research to fix, changing >100 lines of code".

Five things follow, and every one of them is load-bearing for how these rows are classified.

- **This is an estimate, not a timing.** No engineer was observed solving any of these issues.
  `human_time_evidence` is `assumed` and `human_time_method` is `estimated` on all 124 rows.
- **The population is hypothetical.** The annotator judges a counterfactual experienced
  software engineer, so `human_skill` is `expert` and `human_attempts` is `not_applicable`.
  There is no sample of recorded human attempts to count, so `human_time_subset` is
  `not_applicable` too.
- **Codebase familiarization is excluded** by the question's own parenthesis, and the row's
  `notes` says so. So is any time spent by the original PR author.
- **The high-level requirements may be assumed clear.** The instruction does not assume
  ambiguity away wholesale: where the issue text was too vague to attempt, the annotator may
  assume the "what" has been clarified, while the "how" is left to the engineer. The model gets
  the raw issue text either way. This is part of why `comparison_issues` carries
  `different_assessment`.
- **A bin is an interval, not a number.** The first three bins are closed, and each row takes
  the arithmetic midpoint: 7.5, 37.5, and 150 minutes. The fourth is open above and takes 6
  hours, argued in the next subsection. These are the same four values the existing 25 rows
  already use, which is what makes the bin rows aggregate back to them.
  `human_time_statistic` is `point_estimate`, because a midpoint over an interval of estimates
  is not a statistic over observed durations.

I did not verify how many annotators OpenAI used, or their selection. The release article that
states it, https://openai.com/index/introducing-swe-bench-verified/, returns HTTP 403 to this
session, and nothing in these rows depends on that count: no human attempt is being counted.

### Six hours for the open top bin

Six hours is 1.5 times the bin's lower bound, where the two closed upper bins sit at 2.5 times
theirs, so the choice is on the conservative side and needs an argument rather than an
assertion. The argument is the Codex parent note's, at
`../AI Compute vs Human Time/dataset/research/epoch/swebench.md`, and I adopt it after
inspecting the same three instances. They "require broad refactoring, parser extensions, and
mathematical distribution support, but are bounded patches rather than an unspecified multiday
project": `pydata__xarray-6992` is an index-refactor inconsistency touching set and reset-index
bookkeeping and the variable, coordinate, and index sets; `sphinx-doc__sphinx-7590` adds C++
user-defined literal support across literal parsing, suffix rules, AST objects, references, and
IDs; `sympy__sympy-13878` implements predefined CDFs for numerous distributions, with support
boundaries, special functions, and symbolic-versus-numeric behavior, and the issue supplies test
examples. Each is a day's work at most for someone who already knows the codebase, not an
open-ended project, so the open bin is bounded well below the "multiday" reading its label
invites.

**Four to ten hours is the sensitivity**, not a measured interval. At 4 hours the 32 top-bin
rows move to 14,400 s and at 10 hours to 36,000 s, with no change to any compute value. The
Codex note also carries a joint sensitivity over all four bins, [5, 20, 90, 240] and
[12, 50, 210, 600] minutes, which moves the benchmark-wide human time from 2,268 s to 1,302 s
and 3,166 s respectively.

### Within-bin distribution

Arithmetic midpoints assume a uniform spread inside each interval. The 500-instance label counts
run 194 / 261 / 42 / 3, strongly right-skewed across bins, which suggests skew toward the lower
end within them as well, so the midpoints probably overstate the bin means. A log-uniform
assumption gives 1,800 s and 7,200 s for the two middle bins, about 20% lower. The central
values are left on the midpoints: they are what makes the reconciliation to the 25 parent rows
exact, and the gradient this note reports survives either mapping, since the log-uniform
alternative compresses the human axis by a similar factor in both bins.

## The join

Epoch runs 484 of the 500 SWE-bench Verified instances, the same 484 in every one of the 32
logs. The 500-instance label counts are 194 / 261 / 42 / 3; Epoch's 484 are
**185 / 254 / 42 / 3**. The 16 absent instances are 9 from the first bin and 7 from the second,
so the omission shifts the benchmark slightly harder; it is identical across all runs, so it
does not affect comparisons between them.

The labels come from the original Parquet,
https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified/resolve/main/data/test-00000-of-00001.parquet,
downloaded fresh on 2026-09-13 (SHA256
`a45b1fe4e2f0c8390b2b2938ac83e92ed5979000856808f3679c07812e9e6dcd`, 2,096,679 bytes). That
hash is identical to the copy the Codex collection retained, so the two passes joined against
the same file. The join is on the exact `instance_id`, and `extract_perinstance.py` raises if
any sample in any log is absent from the label table. All 32 runs contain 484 unique instance
IDs, one epoch each, and every one is labelled.

The three instances in the top bin are `pydata__xarray-6992`, `sphinx-doc__sphinx-7590`, and
`sympy__sympy-13878`.

## Counted token workload

Inspect's `model_usage` block does not mean the same thing on every endpoint, and getting this
wrong is the single largest silent error available here. For each run the identity that
`total_tokens` satisfies determines the convention, and `extract_perinstance.py` asserts that
identity on every one of the 15,488 sample records rather than only on the run header:

| Endpoint family | Source total | Counted workload |
|---|---|---|
| `google/*` | I + O + R | I − CR + CW + O + R |
| `openai/*`, `zhipu/*`, `moonshot/*` | I + O | I − CR + CW + O |
| `epoch/gemini-3.5-flash` | I + CR + O + R | I + CW + O + R |
| `anthropic/*`, other `epoch/*` | I + CR + CW + O | I + CW + O |

I is `input_tokens`, O `output_tokens`, R `reasoning_tokens`, CR `input_tokens_cache_read`, CW
`input_tokens_cache_write`. The CW term is what `counted()` actually adds in every case; it is
zero on every endpoint outside the bottom row except `epoch/qwen3.7-max`, which is already on
the additive rule, so the first three rows reduce to the familiar forms in practice. Reasoning
is a subset of output everywhere except the Google endpoints, where it is reported additionally.
Cache reads are excluded from the counted workload in all four cases, following COLUMNS on
`params_tokens`. This is the same rule set the existing 25 rows use, which is why the run-level
reconciliation below is exact.

The rule table was listed as a reviewer check because an endpoint's source-total identity can
be satisfied by more than one rule. The independent review settled it by testing all four
(cache-read-inside-input, reasoning-additional) combinations against every sample of every run:
twelve runs admit two viable combinations, and in all twelve the two return an identical counted
total, because the second differs only in a reasoning counter that is zero. No run's counted
workload is ambiguous.

One consequence worth stating plainly. Excluding cache reads is not a rounding decision: the
ratio of billed to counted tokens runs from 1.00 on `epoch/qwen3.6-plus`, whose endpoint reports
no cache counters at all, to 34.21 on `anthropic/claude-opus-4-7`, with a median of 10.69.

Everything is computed from the per-sample summaries, never from the run header. Nine of the 32
headers are unreliable, in two distinct ways, and either would have corrupted the numbers.
Seven cover only a trailing segment of their run, reporting between 0.6% and 97.5% of what
their samples sum to: Gemini 3.1 Pro customtools 97.5%, Gemini 3 Pro 42.3%, GPT-4o 11.2%,
GPT-5.2 high 6.2%, Claude Code-harness Opus 4.6 3.4%, Claude 3.7 Sonnet 0.7%, and Codex-harness
GPT-5.1 0.6%. Two more, GPT-5.4 high and GPT-5 high, carry an empty `stats.model_usage` block
entirely while every one of their 484 samples records usage normally. No run has a sample with
zero primary usage, and no run records usage for any model other than its primary endpoint,
including the two CLI-harness runs, where a sub-agent or summarizer call is exactly what a
reader would expect to go unrecorded. Whether a CLI could make calls outside Inspect's
instrumentation is not determinable from the retained members.

`compute_flops` is `tokens x flops_per_token` with the coefficient already in the dataset's
`models.csv`, unchanged. No new model record is created: all 28 model IDs already exist, so
`candidates/epoch-swebench-bins/models.csv` carries only the header.

### The harness token cap

Epoch's Inspect task sets `token_limit = 2000000`, enforced against the same non-cache-read
count these rows record. An instance whose counted workload reaches 1,950,000 is treated here as
censored by that cap. Over the 31 built runs the effect is small: **0.28%, 0.81%, 2.15%, and
1.08%** of instances by bin, or 16, 64, 28, and 1 instances out of 5,735, 7,874, 1,302, and 93.
Pooling the held qwen3.6-plus run back in gives 1.59%, 2.90%, 5.13%, and 3.12%, which is how far
one censored run moves the whole benchmark; those are the figures to quote when the subject is
the 32 logs rather than the 31 built rows. Four bins in the CSV exceed 10%, and each says so in
its own `notes`:

| Bin row | Instances at the cap (%) |
|---|---|
| agen-epoch-swebench-gpt52high-gt4h | 33.3 |
| agen-epoch-swebench-gemini25pro-1h4h | 21.4 |
| agen-epoch-swebench-glm5-1h4h | 14.3 |
| agen-epoch-swebench-gemini25pro-15m1h | 11.4 |

`agen-epoch-swebench-gpt52high-gt4h` is the highest-compute row in the batch at 1.88e17, and one
of its three instances is at the cap, so that value is partly a floor. The independent review did
not flag this bin; it falls out of the same per-instance test and is included for completeness.
`calculations.json` carries the count and percentage for all 128 run-bins.

### The qwen3.6-plus disposition

`agen-epoch-swebench-qwen36plus-lt15m`, `-15m1h`, `-1h4h`, and `-gt4h` were drafted and are
**not** in `points.csv`. Two problems compound in this run, in opposite directions, and neither
is recoverable from the retained members.

The cap binds on 42.2%, 67.7%, 97.6%, and 66.7% of the instances in the four bins. Over the 484
instances the counted median is 2,008,210 and the maximum 2,063,515, so the distribution has a
hard ceiling a few percent above 2,000,000 rather than a tail. The 1-4 hour bin's 2,009,496
tokens is the cap itself. Its `compute_flops` of 6.83e16 is a floor, and the row cannot be read
as a compute observation the way the other runs' rows can. The dataset does not turn a harness
budget into a measurement.

Pushing the other way, `epoch/qwen3.6-plus` is the one endpoint reporting no cache counters at
all, so every re-read prefix is counted as newly processed. The accepted parent row says so:
"Cache usage is unreported; all source input is treated as newly processed." That clause belongs
on any row built from this run, and no row in the CSV now needs it, since every other endpoint
reports cache counters. It is recorded here for the parent row's sake and for anyone who
revisits this run.

The same absence means the [attention scenario](#cached-context-attention) does not apply to
this run unchanged: with no cache counters its counted tokens already include the re-read
prefix, so the recipe would double-count. Its numbers remain in `calculations.json` under
`excluded_from_csv` so the disposition is inspectable, and the bin summary CSV excludes it.

### Missing-work allowance

Five of the 32 runs carry a per-instance allowance for network sends whose response was lost
after processing may have begun. These were classified from the original event tracebacks by
the Codex collection, retained at
`AI Compute vs Human Time/dataset/sources/epoch/native-final-accounting/expansion-14/usage-reconstruction.json`,
and each correction names the instance it belongs to, so the allowance bins exactly rather than
being spread. The run-level shares are deepseek-v4-pro 0.3099%, glm-5.2 0.0181%, kimi-k2.6
0.0024%, qwen3.6-plus 0.0019%, and claude-opus-4-7 0.0018%. The other 27 runs have none, and no
equivalent audit exists for the seven runs added here, so they carry recorded counters alone.

The allowance is included so the bin rows reconcile exactly with the rows they refine. It is an
estimate rather than a measurement, and reproducing its classification would need the full event
data, so every per-point section below also states the value from recorded counters alone, and
`calculations.json` carries both under `tokens_per_completed_evaluation` and
`tokens_per_completed_evaluation_recorded_only`. **The largest difference any row sees is 1.17%,
on `agen-epoch-swebench-dsv4promax-gt4h`**, where recorded counters alone give 159,527.33 tokens
against 161,401.52 with the allowance; the other three deepseek-v4-pro bins are next at 0.30% to
0.32%, and every remaining row is under 0.05%. Bin shares exceed the run-level share because the
lost sends are not spread evenly over the bins.

### Denominator

`compute_statistic` is `total_per_completed_sample`: the numerator is every instance in the
bin, including the ones whose grading did not return, and the denominator is the completed
evaluations in that bin. Six runs have ungraded records, 22 of them in the GLM-5 run alone,
and their model work still counts. `ai_attempts` is `not_applicable` because the value is a
benchmark aggregate normalized per question, not a statistic over defined task runs, matching
the existing rows.

## Cached-context attention

`DECISIONS.md` requires every long-context run to carry a quantified scenario for the attention
term the `2 * active_parameters` convention omits, using the `4 * L * d_model * N_context`
recipe from the dataset's RULER row, with bracketing architectures. These runs qualify: the mean
prefix a position attends over is at least 10,000 tokens in 107 of the 124 bins, median 16,833.

The scenario is **bounded, not derived**. The retained `summaries.json` gives `message_count`
but no per-call prefixes, so a call count is taken as half the transcript length (system plus
assistant-and-tool pairs), and the mean prefix per call is bracketed: below by the run's cache
reads per call, which are prefix positions attended to but not re-processed, and above by all
input-side positions per call, which additionally counts prefix that was re-processed rather
than read from cache. Appended positions are the counted workload. A proper derivation needs the
logs' event records, which are not retained.

Medians over the 31 built runs, at L = 64 and d_model = 8192:

| Bin | Mean prefix, lower (tokens) | Mean prefix, upper (tokens) | Attention / compute, lower | Attention / compute, upper |
|---|---|---|---|---|
| <15 min fix | 12268 | 14174 | 0.20 | 0.22 |
| 15 min - 1 hour | 16482 | 18977 | 0.27 | 0.30 |
| 1-4 hours | 24553 | 27769 | 0.30 | 0.33 |
| >4 hours | 16890 | 20722 | 0.23 | 0.31 |

Across all 124 bins the term runs from **0.045× to 1.005×** the recorded value on the
lower bound and **0.055× to 1.085×** on the upper, median 0.262 and 0.299. At L = 96 and
d_model = 12288 the term is exactly **2.25 times** those, since `4 * L * d_model` scales by
(96 × 12288) / (64 × 8192). The independent review's coarse check put the second shape at about
1.7 times the first; the ratio is 2.25, and the accepted `research/portal-astra.md` uses the same
two shapes with the same 2.25 factor. The review's range for the first shape, 0.08 to 0.63 with
median 0.25, agrees with the lower-bound column here on the median and is narrower at the tails
because it covered fewer runs.

The term is one-sided upward and is now inside `compute_flops`: `research/attention-correction.md`
folds it into every corrected row in the file, so these rows stay comparable with the rest. Per-bin values are in `calculations.json` under
`omitted_cached_context_attention` and in every per-point section below; the values actually
applied are in `research/attention-correction.md`, which uses a per-model attention shape
rather than the two brackets here.

### What `attention_context` actually carries

The bracket above is not what the CSV carries. `attention_context` on all 92 rows is the
**cache-implied mean prefix**, the second tier of the fallback order in
`research/attention-correction.md#cache-implied-context`:

```
N̄ = min( (cache reads per instance / counted tokens per instance) · 2800,
         counted / 2, 200000 )
```

Cache reads are the sum of the per-call prefixes and the counted total is the sum of the new
tokens per call, so their ratio times the new tokens per call is the mean prefix. `n = 2,800`
is the median over the sixteen Terminal-Bench 2.1 official submissions, the constant the METR
rebuild and the Terminal-Bench 4.0 and Terminal-Bench-Science blocks already use. It applies
here because every endpoint in the 31 built runs reports cache counters — the one that does
not, `epoch/qwen3.6-plus`, produced no row.

**The two routes are independent and they agree.** The bracket above fixes the call count from
the run's transcript length; the cache-implied route fixes it from `n`. Across the 92 rows the
bracket's geometric mean has a median of 17,282 positions and the cache-implied value a median
of 20,103, a 16% difference, and the ratio's p10 to p90 spans 0.40 to 1.79. Both sit about
three times below the 64,464 median that half the counted tokens returned, which is what these
rows carried before: an eight-hour agent's whole token budget is not a context it ever held.

The cache-implied value is the one applied, on the coordinator's ruling, because it is the tier
the rest of the file uses and because the bracket's call count is itself a proxy — half the
transcript length — rather than a record. **On 27 of the 92 rows the two disagree by more than
2×**, 18 with the bracket higher and 9 with it lower; each of those rows' `notes` states the
bracket figure so the disagreement is visible in the product. The bracket runs higher on the
OpenAI and Gemini endpoints, whose cache-read multiples are modest, and lower on the Anthropic
and Zhipu ones, whose multiples reach 34.

`N̄` runs from 2,673 to 86,797 across the 92 rows with a median of 20,103. The 200,000 cap
binds on none of them now; the append-only bound `counted / 2` binds on 40, which is why those
rows' values did not move.

## Reconciliation with the existing rows

For each of the 25 runs with an existing row, the four bins' counted tokens plus allowances,
divided by the run's completed evaluations, reproduce the existing row's `tokens` to better
than one part in 10^9, and the instance-weighted mean of the four bin human times reproduces
2267.6652892561983 seconds exactly. Both are assertions in `build_bin_rows.py`, not
observations. The assertions still run for qwen3.6-plus even though its rows are held.

Independently of that, 1,936 per-instance records extracted from four logs the scouting pass
downloaded whole from Epoch's S3 bucket (`claude-opus-4-7`, `glm-5.2`, `qwen3.7-max`,
`gemini-3.5-flash`) agree with the retained `summaries.json` extracts on every counter, the
difficulty label, the resolved flag, and working time, with zero differences. The independent
review repeated the exercise on eight logs, four of them ones the Codex collection never
retained, covering all four counter families, and found zero differences over 3,872 records.

## Results

Tokens are per completed evaluation; resolved is the fraction of completed evaluations in that
bin passing the native fail-to-pass and pass-to-pass suites.

| point_id prefix | model_id | Inspect task | flops_per_token (FLOP) | tokens, under 15 min | tokens, 15 min to 1 h | tokens, 1 to 4 h | tokens, over 4 h | resolved, under 15 min | resolved, 15 min to 1 h | resolved, 1 to 4 h | resolved, over 4 h |
|---|---|---|---|---|---|---|---|---|---|---|---|
| agen-epoch-swebench-sonnet37 | claude-3-7-sonnet | swe_bench_verified | 200000000000 | 28952 | 37491 | 51377 | 50438 | 0.789 | 0.551 | 0.190 | 0.333 |
| agen-epoch-swebench-opus4 | claude-opus-4 | swe_bench_verified | 360000000000 | 37896 | 47345 | 63034 | 61679 | 0.832 | 0.677 | 0.357 | 0.333 |
| agen-epoch-swebench-opus41 | claude-opus-4-1 | swe_bench_verified | 360000000000 | 45157 | 57020 | 68641 | 64751 | 0.822 | 0.717 | 0.476 | 0.333 |
| agen-epoch-swebench-opus45 | claude-opus-4-5 | swe_bench_verified | 200000000000 | 24681 | 34507 | 56441 | 43742 | 0.886 | 0.736 | 0.452 | 0.333 |
| agen-epoch-swebench-opus46 | claude-opus-4-6 | swe_bench_verified | 200000000000 | 21023 | 27774 | 40472 | 39816 | 0.870 | 0.728 | 0.452 | 0.333 |
| agen-epoch-swebench-opus46cc | claude-opus-4-6 | swe_bench_claude_code | 200000000000 | 57696 | 92420 | 150840 | 104721 | 0.886 | 0.764 | 0.524 | 0.333 |
| agen-epoch-swebench-opus47max | claude-opus-4-7 | swe_bench_verified | 200000000000 | 47803 | 87032 | 155979 | 95313 | 0.908 | 0.823 | 0.595 | 0.667 |
| agen-epoch-swebench-sonnet45 | claude-sonnet-4-5 | swe_bench_verified | 200000000000 | 66919 | 80310 | 94944 | 93451 | 0.816 | 0.705 | 0.357 | 0.000 |
| agen-epoch-swebench-sonnet46 | claude-sonnet-4-6 | swe_bench_verified | 200000000000 | 18006 | 31899 | 81331 | 44827 | 0.859 | 0.732 | 0.429 | 0.333 |
| agen-epoch-swebench-dsv4promax | deepseek-v4-pro-preview | swe_bench_verified | 98000000000 | 125627 | 241096 | 444092 | 161402 | 0.881 | 0.776 | 0.366 | 0.000 |
| agen-epoch-swebench-gemini25pro | gemini-2.5-pro | swe_bench_verified | 200000000000 | 219470 | 554108 | 852827 | 660830 | 0.755 | 0.512 | 0.214 | 0.000 |
| agen-epoch-swebench-gemini3flash | gemini-3-flash-preview | swe_bench_verified | 80000000000 | 244917 | 341681 | 496538 | 434022 | 0.886 | 0.748 | 0.238 | 0.333 |
| agen-epoch-swebench-gemini3pro | gemini-3-pro | swe_bench_verified | 200000000000 | 202044 | 280271 | 458349 | 327366 | 0.870 | 0.697 | 0.333 | 0.333 |
| agen-epoch-swebench-gemini31pro-ct | gemini-3.1-pro-preview-customtools | swe_bench_verified | 200000000000 | 237152 | 374191 | 591079 | 720705 | 0.838 | 0.760 | 0.405 | 0.333 |
| agen-epoch-swebench-gemini35flash | gemini-3.5-flash | swe_bench_verified | 80000000000 | 262304 | 306627 | 417055 | 445465 | 0.886 | 0.783 | 0.476 | 0.333 |
| agen-epoch-swebench-glm5 | glm-5 | swe_bench_verified | 80000000000 | 132227 | 241055 | 490289 | 147121 | 0.822 | 0.702 | 0.415 | 0.333 |
| agen-epoch-swebench-glm52max | glm-5.2 | swe_bench_verified | 80000000000 | 55513 | 100418 | 173593 | 118659 | 0.891 | 0.772 | 0.452 | 0.333 |
| agen-epoch-swebench-gpt41 | gpt-4.1-2025-04-14 | swe_bench_verified | 100000000000 | 71277 | 117357 | 123776 | 156697 | 0.668 | 0.417 | 0.122 | 0.000 |
| agen-epoch-swebench-gpt4o1120 | gpt-4o-2024-11-20 | swe_bench_verified | 100000000000 | 42201 | 69210 | 51146 | 28438 | 0.492 | 0.220 | 0.071 | 0.000 |
| agen-epoch-swebench-gpt5high | gpt-5 | swe_bench_verified | 200000000000 | 162945 | 220799 | 357809 | 168734 | 0.870 | 0.705 | 0.357 | 0.333 |
| agen-epoch-swebench-gpt5med | gpt-5 | swe_bench_verified | 200000000000 | 197508 | 255975 | 362712 | 357650 | 0.854 | 0.677 | 0.381 | 0.000 |
| agen-epoch-swebench-gpt53codex | gpt-5-3-codex | swe_bench_verified | 200000000000 | 141324 | 214122 | 414729 | 493042 | 0.832 | 0.736 | 0.476 | 0.333 |
| agen-epoch-swebench-gpt5mini | gpt-5-mini-2025-08-07 | swe_bench_verified | 40000000000 | 239335 | 330828 | 432497 | 465962 | 0.778 | 0.638 | 0.167 | 0.000 |
| agen-epoch-swebench-gpt51codex | gpt-5.1-2025-11-13 | swe_bench_codex | 200000000000 | 75123 | 112677 | 205329 | 191697 | 0.757 | 0.646 | 0.333 | 0.333 |
| agen-epoch-swebench-gpt51high | gpt-5.1-2025-11-13 | swe_bench_verified | 200000000000 | 345690 | 498915 | 708683 | 473027 | 0.811 | 0.657 | 0.286 | 0.000 |
| agen-epoch-swebench-gpt52high | gpt-5.2-2025-12-11 | swe_bench_verified | 200000000000 | 269407 | 404220 | 789393 | 940567 | 0.854 | 0.717 | 0.381 | 0.333 |
| agen-epoch-swebench-gpt54high | gpt-5.4-2026-03-05 | swe_bench_verified | 200000000000 | 86780 | 152396 | 285923 | 357780 | 0.870 | 0.740 | 0.524 | 0.333 |
| agen-epoch-swebench-kimik25 | kimi-k2.5 | swe_bench_verified | 64000000000 | 35090 | 52915 | 75134 | 58840 | 0.870 | 0.713 | 0.333 | 0.333 |
| agen-epoch-swebench-kimik26 | kimi-k2.6 | swe_bench_verified | 64000000000 | 37917 | 65052 | 110376 | 224494 | 0.859 | 0.760 | 0.452 | 0.000 |
| agen-epoch-swebench-o3med | o3-2025-04-16 | swe_bench_verified | 100000000000 | 228792 | 262023 | 392224 | 212485 | 0.755 | 0.602 | 0.214 | 0.000 |
| agen-epoch-swebench-qwen37max | qwen3.7-max | swe_bench_verified | 200000000000 | 103887 | 237708 | 606278 | 232153 | 0.886 | 0.756 | 0.405 | 0.333 |

Read across any row and the compute grows far more slowly than the human estimate. Read across
the resolved columns and the models degrade steeply: the median resolved rate is 0.854, 0.717,
0.381, and 0.333 across the four bins. The two effects point the same way. On the issues a
human would take twenty times longer on, these systems spend a bit more than twice the compute
and succeed less than half as often.

One run breaks the monotone token pattern inside the closed bins. GPT-4o spends 69,210 tokens
on the middle bin and 51,146 on the 1-4 hour bin, and resolves 7.1% of the latter. A model that
cannot get traction stops early, which puts a floor under how far the compute side can track
the human side at the hard end.

Mean AI working time per instance moves with the bin as well, from a median across runs of 339
seconds in the first bin to 772 seconds in the third. It is recorded in `calculations.json` and
in the per-point sections but is not a CSV field.

Two of the runs use a different agent harness on the same 484 issues, and the pair is worth
looking at directly. Claude Opus 4.6 under `swe_bench_claude_code` spends 2.6 to 3.7 times the
tokens per instance of the same model under the bash agent and resolves more in every closed
bin (0.886 against 0.870, 0.764 against 0.728, 0.524 against 0.452). GPT-5.1 high under
`swe_bench_codex` spends 0.22 to 0.41 times the bash agent's tokens and resolves less in the
first two bins and more in the third. The harness is named in each row's `source_record` and in
`task_description`.

## The over-4-hours bin

Three instances. The question is whether to carry 31 rows at 21,600 seconds or fold those three
into the 1-4 hour bin.

**The case against keeping it.** The per-instance token mean over three records has a standard
error of 4% to 81% of the mean, median 37%. Worse, the direction is wrong: in 23 of the 31 runs
the over-4-hours mean is *below* the 1-4 hour mean, median ratio 0.87. Since all runs draw the
same three instances, that is one draw, not 31 pieces of evidence. And the resolved rate over
three trials can only take the values 0, 1/3, 2/3, or 1; it is 1/3 in 20 runs, 0 in 10, and 2/3
in one, which carries no usable information about the bin.

**The driver is one abandoned issue, not noise.** `pydata__xarray-6992` costs far below the
run's own 1-4 hour mean in 31 of the 32 runs, from 9,628 to 508,244 tokens, and **no run
resolves it**. `sphinx-doc__sphinx-7590` resolves in one run. `sympy__sympy-13878` resolves in
21 and carries most of the bin's compute. So the bin's low mean is one issue that every system
gives up on early, which is the same effect GPT-4o shows across its whole 1-4 hour bin, not
sampling noise over three draws.

**The case for keeping it, which is the one I follow.** The human time is not a sampled
quantity. It is a label assigned to the bin, so the x-value of the row is exactly as well
determined at n = 3 as at n = 254. Only the compute mean and the resolved rate are sampled, and
of those only the compute mean enters a row's numbers. A 37% standard error is a factor of
about 1.4, which is small against the factor-of-4 half-to-double parameter scenario that
already sits under every one of these rows, and small against the 80× span of `compute_flops`
across the 124 rows. Folding would replace a stated 21,600-second human time with a blended
9,840-second value that belongs to neither bin, and would lose the longest human time this
source can produce. The performance label does not depend on the noisy rate: it is a comparison
against a complete correct patch, which a 0% to 67% test-pass rate is below on any of these
draws. `DECISIONS.md` already rules that a small bin stays separate with its sampling error
stated.

So all four bins are carried. Each over-4-hours row states in `notes` that only three instances
carry the label, gives that bin's standard error as a percentage of its mean, and gives the
bin's own ratio to the 1-4 hour bin so the non-monotonicity is visible in the row rather than
only in the scatter. And `calculations.json` carries, for every run, a `folded_over_1_hour_bin`
block with the exact 45-instance alternative, human time 9,840 seconds, so the swap needs no
re-derivation if the coordinator or Damon prefers it.

## Performance

`performance_vs_human` is `below` on all 124 rows. The human target is a complete correct
patch, conditional on the engineer being able to solve the issue at all; the annotation source
assumes the engineer arrives at a solution, so it does not establish a human success rate. The
model's observed quantity is passing the original fail-to-pass and pass-to-pass suites. Those
are different criteria, which is what `different_assessment` marks, and the compute covers all
attempts while the human estimate covers eventual correct work, which is what
`different_attempt_selection` marks.

The label is uniform across bins, but the evidence behind it is not, and
`performance_evidence` carries the bin's own numbers so the gradient is visible. The first bin
is the closest to the target, at 0.492 to 0.908 resolved; the third is 0.071 to 0.595. Nothing
here is a measured human solve rate, and a reviewer should not read `below` in the first bin as
the same strength of claim as `below` in the third.

Two known defects in the assessment cut in opposite directions and are carried in every row's
`notes`: some native tests reject valid fixes, and the models may have encountered published
solutions to these issues during training. The bin split does not resolve either.

## Logs read, and logs not read

Epoch's published index, `swe_bench_verified.csv` inside https://epoch.ai/data/benchmark_data.zip
(downloaded 2026-09-13, SHA256 `3c562e5a13cae84133406b80e1ab072ac17ee023aca0cf4c2a5487a1b4bdf781`),
lists 35 SWE-bench Verified runs. A HEAD request was issued against every published log URL on
2026-09-13. Thirty-two return HTTP 200 and are read here; 31 of those produce rows. The three
that are not read:

| Model version | Log id | Why not read |
|---|---|---|
| glm-5.1 | glm-5.1-swe-bench-frankenstein | No log URL in the index; the id is a placeholder, not an object key |
| qwen3.6-max-preview | FkDMVLdEnJDR5PyUCT6BNQ | HTTP 403 |
| gpt-5.5-pre-release_xhigh | LbhPRqUkXrs5KJ7vyT4CR7 | HTTP 403 |

Twenty-five of the 32 are the runs the dataset already covers, and their `header.json` and
`summaries.json` were already retained by the Codex collection. The other seven were read from
the remote archives directly. Their logs are 0.43 to 7.30 GB, so `fetch_log_members.py`
range-reads the ZIP central directory and pulls only the two members needed, about 0.9 MB per
run. They are:

| Run | model_id | Inspect task | Log size (GB) |
|---|---|---|---|
| agen-epoch-swebench-gpt54high | gpt-5.4-2026-03-05 | swe_bench_verified | 1.49 |
| agen-epoch-swebench-gpt5high | gpt-5 | swe_bench_verified | 7.30 |
| agen-epoch-swebench-gpt5med | gpt-5 | swe_bench_verified | 2.20 |
| agen-epoch-swebench-gpt4o1120 | gpt-4o-2024-11-20 | swe_bench_verified | 0.55 |
| agen-epoch-swebench-sonnet37 | claude-3-7-sonnet | swe_bench_verified | 0.43 |
| agen-epoch-swebench-opus46cc | claude-opus-4-6 | swe_bench_claude_code | 0.64 |
| agen-epoch-swebench-gpt51codex | gpt-5.1-2025-11-13 | swe_bench_codex | 1.76 |

GPT-5 high and GPT-5 medium share a `model_id`: reasoning effort is a task configuration, not a
separate weight identity, and the dataset's own GPT-5 model note says so. Opus 4.6 and GPT-5.1
each appear twice, once under the bash agent and once under a CLI harness. All seven model IDs
already exist in the dataset's `models.csv` with settled coefficients, so no new model record is
proposed here; that matters, because closed-model parameter priors are under separate review per
`DECISIONS.md`.

The FrontierMath family, which would have been the other candidate for this treatment,
publishes no readable logs at all: every URL points at a private bucket.

## Evidence classification

`compute_evidence` is `derived_supported_inputs` where the model's active parameter count has
a `reported` basis in the dataset's `models.csv` and the run carries no assumed missing-work
allowance, and `derived_assumed_inputs` otherwise. That leaves eight rows supported, the four
GLM-5 bins and the four Kimi K2.5 bins, and 116 assumed. DeepSeek V4 Pro and Kimi K2.6 also
have reported parameter counts but carry an allowance, so they stay assumed; this is the same
classification the 25 existing rows use.

## Reproduction

Three scripts, all standard library except `pandas`/`pyarrow` to read the Parquet, `zstandard`
and `curl` for the range reader, all taking explicit paths and writing fresh outputs outside
their input trees.

```sh
# Only for the seven runs the Codex collection did not retain; needs network access.
python3 research/epoch-swebench-bins/fetch_log_members.py \
  --url https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/<id>.eval \
  --out-dir /tmp/extra/agen-epoch-swebench-<key>

python3 research/epoch-swebench-bins/extract_perinstance.py \
  --epoch-sources "../AI Compute vs Human Time/dataset/sources/epoch" /tmp/extra \
  --difficulty    /path/to/swebench-verified-test.parquet \
  --allowances    "../AI Compute vs Human Time/dataset/sources/epoch/native-final-accounting/expansion-14/usage-reconstruction.json" \
  --hub           agent-work/sources/epoch-swebench-bins/epoch-hub-swe-bench-verified.csv \
  --points        "../AI Compute vs Human Time/dataset/points.csv" \
  --model-map     agent-work/sources/epoch-swebench-bins/extra-run-model-map.csv \
  --out-perinstance /tmp/perinstance.csv \
  --out-run-links   /tmp/run-links.csv \
  --out-hashes      /tmp/source-hashes.json

python3 research/epoch-swebench-bins/build_bin_rows.py \
  --perinstance   agent-work/sources/epoch-swebench-bins/epoch-swebench-perinstance.csv \
  --run-links     agent-work/sources/epoch-swebench-bins/epoch-swebench-run-links.csv \
  --models        "../AI Compute vs Human Time/dataset/models.csv" \
  --parent-points "../AI Compute vs Human Time/dataset/points.csv" \
  --out-points    /tmp/points.csv \
  --out-bins      /tmp/bin-summary.csv \
  --out-calc      /tmp/calculations.json
```

The first two need remote or Codex-side inputs; the third needs only the retained per-instance
table, so the rows can be rebuilt with no access to any log. `emit_point_sections.py`
regenerates everything after the `<!-- GENERATED POINTS -->` marker below, for diffing against
this file. Input hashes are in `agent-work/sources/epoch-swebench-bins/source-hashes.json` and in each
`agent-work/sources/epoch-swebench-bins/extra-run-members/<run>/fetch.json`; provenance is in
`agent-work/sources/epoch-swebench-bins/MANIFEST.md`.

## What a reviewer should scrutinize first

1. **The 6-hour value for the open top bin, and the decision to keep that bin.** Both are
   judgment calls, both are argued above, and both are cheap to reverse: the 4-to-10-hour
   sensitivity and the fold-in numbers are precomputed.
2. **The attention scenario is bounded, not derived.** The call count is half the transcript
   length and the prefix is bracketed by cache reads and by all input-side positions per call.
   Per-call prefixes would need the logs' event records.
3. **The harness cap.** Four bins in the CSV exceed 10% censoring and say so; one whole run is
   held for it. A reader treating `tokens` as an unconstrained measurement is wrong on those
   four rows.
4. **Whether the 24 parent rows are actually deleted at merge, and the 25th flagged.**
   `incorporate.py` cannot do either, the dataset has no superseded-rows or quarantine file to
   record them in, and the double-count deletion would otherwise leave is exact and therefore
   invisible.
5. **The uniform `below` label.** It is defensible against a complete-correct-patch target, but
   the first bin at 0.908 resolved for Opus 4.7 is the weakest instance of it.
6. **The model coefficients.** 24 of the 28 are estimated, they scale every `compute_flops`
   here linearly, and they are under separate review per `DECISIONS.md`.

<!-- GENERATED POINTS -->

## agen-epoch-swebench-dsv4promax-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/WUk3f44JhxtAJaSxi6gFZR.eval); primary `epoch/deepseek-v4-pro`; reasoning_effort=max; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 163 resolved (88.1081%).
Mean per-instance native counters: input 112,665, cache write 0, cache read 895,968, output 12,566, reasoning 7,528.
Counted workload 23,167,813 + missing-work allowance 73169.557018 = 23240982.557018 tokens / 185 completed evaluations = **125626.932741 tokens** x 98,000,000,000 FLOPs/token = **1.231144e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 184,410, standard error of the mean 13,558 (10.8% of the mean). Mean AI working time 632.5 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). Recorded counters alone give 125231.421622 tokens per completed evaluation.
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 10496 model calls, mean prefix 15,793 to 17,779 positions, 23,167,813 appended positions. At L=64, d_model=8192 that is 7.673e+17 to 8.638e+17 FLOPs, 0.34x to 0.38x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-dsv4promax-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/WUk3f44JhxtAJaSxi6gFZR.eval); primary `epoch/deepseek-v4-pro`; reasoning_effort=max; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 197 resolved (77.5591%).
Mean per-instance native counters: input 218,651, cache write 0, cache read 1,791,841, output 21,716, reasoning 13,685.
Counted workload 61,053,352 + missing-work allowance 185060.846081 = 61238412.846081 tokens / 254 completed evaluations = **241096.113567 tokens** x 98,000,000,000 FLOPs/token = **2.362742e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 318,734, standard error of the mean 19,999 (8.3% of the mean). Mean AI working time 1044.5 s. At the 2,000,000-token harness cap: 3 of 254 instances (1.2%). Recorded counters alone give 240367.527559 tokens per completed evaluation.
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 21184 model calls, mean prefix 21,484 to 24,106 positions, 61,053,352 appended positions. At L=64, d_model=8192 that is 2.751e+18 to 3.087e+18 FLOPs, 0.46x to 0.52x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-dsv4promax-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/WUk3f44JhxtAJaSxi6gFZR.eval); primary `epoch/deepseek-v4-pro`; reasoning_effort=max; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 41 completed evaluations, 15 resolved (36.5854%).
Mean per-instance native counters: input 397,868, cache write 0, cache read 3,531,855, output 34,344, reasoning 22,058.
Counted workload 18,152,914 + missing-work allowance 54867.333382 = 18207781.333382 tokens / 41 completed evaluations = **444092.227643 tokens** x 98,000,000,000 FLOPs/token = **4.352104e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 522,491, standard error of the mean 80,622 (18.6% of the mean). Mean AI working time 1468.8 s. At the 2,000,000-token harness cap: 2 of 42 instances (4.8%). Recorded counters alone give 442754.000000 tokens per completed evaluation.
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 4995 model calls, mean prefix 29,697 to 33,043 positions, 18,152,914 appended positions. At L=64, d_model=8192 that is 1.131e+18 to 1.258e+18 FLOPs, 0.64x to 0.71x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-dsv4promax-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/WUk3f44JhxtAJaSxi6gFZR.eval); primary `epoch/deepseek-v4-pro`; reasoning_effort=max; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 0 resolved (0.0000%).
Mean per-instance native counters: input 134,552, cache write 0, cache read 2,137,941, output 24,975, reasoning 14,983.
Counted workload 478,582 + missing-work allowance 5622.562998 = 484204.562998 tokens / 3 completed evaluations = **161401.520999 tokens** x 98,000,000,000 FLOPs/token = **1.581735e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 122,762, standard error of the mean 70,877 (43.9% of the mean). Mean AI working time 1147.1 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). Recorded counters alone give 159527.333333 tokens per completed evaluation.
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 288 model calls, mean prefix 22,309 to 23,713 positions, 478,582 appended positions. At L=64, d_model=8192 that is 2.239e+16 to 2.380e+16 FLOPs, 0.48x to 0.51x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini25pro-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/KL724uHFGbiXj4o5PHyLn2.eval); primary `google/gemini-2.5-pro`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 184 completed evaluations, 139 resolved (75.5435%).
Mean per-instance native counters: input 658,824, cache write 0, cache read 457,088, output 2,336, reasoning 14,211.
Counted workload 40,382,423 + missing-work allowance 0 = 40382423.000000 tokens / 184 completed evaluations = **219469.690217 tokens** x 200,000,000,000 FLOPs/token = **4.389394e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 369,673, standard error of the mean 27,179 (12.5% of the mean). Mean AI working time 454.3 s. At the 2,000,000-token harness cap: 3 of 185 instances (1.6%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 3677 model calls, mean prefix 22,997 to 33,147 positions, 40,382,423 appended positions. At L=64, d_model=8192 that is 1.948e+18 to 2.807e+18 FLOPs, 0.24x to 0.35x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini25pro-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/KL724uHFGbiXj4o5PHyLn2.eval); primary `google/gemini-2.5-pro`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 130 resolved (51.1811%).
Mean per-instance native counters: input 1,715,393, cache write 0, cache read 1,195,773, output 4,210, reasoning 30,278.
Counted workload 140,743,406 + missing-work allowance 0 = 140743406.000000 tokens / 254 completed evaluations = **554107.897638 tokens** x 200,000,000,000 FLOPs/token = **1.108216e+17 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 702,227, standard error of the mean 44,062 (8.0% of the mean). Mean AI working time 943.6 s. At the 2,000,000-token harness cap: 29 of 254 instances (11.4%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 7346 model calls, mean prefix 41,343 to 59,308 positions, 140,743,406 appended positions. At L=64, d_model=8192 that is 1.220e+19 to 1.751e+19 FLOPs, 0.43x to 0.62x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini25pro-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/KL724uHFGbiXj4o5PHyLn2.eval); primary `google/gemini-2.5-pro`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 9 resolved (21.4286%).
Mean per-instance native counters: input 2,560,786, cache write 0, cache read 1,757,646, output 7,401, reasoning 42,286.
Counted workload 35,818,723 + missing-work allowance 0 = 35818723.000000 tokens / 42 completed evaluations = **852826.738095 tokens** x 200,000,000,000 FLOPs/token = **1.705653e+17 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 881,832, standard error of the mean 136,070 (16.0% of the mean). Mean AI working time 1246.3 s. At the 2,000,000-token harness cap: 9 of 42 instances (21.4%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 1450 model calls, mean prefix 50,894 to 74,149 positions, 35,818,723 appended positions. At L=64, d_model=8192 that is 3.823e+18 to 5.570e+18 FLOPs, 0.53x to 0.78x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini25pro-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/KL724uHFGbiXj4o5PHyLn2.eval); primary `google/gemini-2.5-pro`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 0 resolved (0.0000%).
Mean per-instance native counters: input 2,863,410, cache write 0, cache read 2,236,120, output 7,358, reasoning 26,182.
Counted workload 1,982,489 + missing-work allowance 0 = 1982489.000000 tokens / 3 completed evaluations = **660829.666667 tokens** x 200,000,000,000 FLOPs/token = **1.321659e+17 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 882,766, standard error of the mean 509,665 (77.1% of the mean). Mean AI working time 910.5 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 83 model calls, mean prefix 80,824 to 103,497 positions, 1,982,489 appended positions. At L=64, d_model=8192 that is 3.360e+17 to 4.303e+17 FLOPs, 0.85x to 1.09x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini31pro-ct-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/8QQQWDgmmEsmQVUJWcxx4P.eval); primary `google/gemini-3.1-pro-preview-customtools`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 155 resolved (83.7838%).
Mean per-instance native counters: input 1,365,365, cache write 0, cache read 1,183,593, output 4,777, reasoning 50,604.
Counted workload 43,873,201 + missing-work allowance 0 = 43873201.000000 tokens / 185 completed evaluations = **237152.437838 tokens** x 200,000,000,000 FLOPs/token = **4.743049e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 253,778, standard error of the mean 18,658 (7.9% of the mean). Mean AI working time 1034.2 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 13587 model calls, mean prefix 16,116 to 18,591 positions, 43,873,201 appended positions. At L=64, d_model=8192 that is 1.483e+18 to 1.711e+18 FLOPs, 0.17x to 0.19x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini31pro-ct-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/8QQQWDgmmEsmQVUJWcxx4P.eval); primary `google/gemini-3.1-pro-preview-customtools`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 193 resolved (75.9843%).
Mean per-instance native counters: input 2,621,463, cache write 0, cache read 2,344,495, output 8,320, reasoning 88,903.
Counted workload 95,044,635 + missing-work allowance 0 = 95044635.000000 tokens / 254 completed evaluations = **374191.476378 tokens** x 200,000,000,000 FLOPs/token = **7.483830e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 377,451, standard error of the mean 23,683 (6.3% of the mean). Mean AI working time 1660.8 s. At the 2,000,000-token harness cap: 1 of 254 instances (0.4%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 28778 model calls, mean prefix 20,693 to 23,137 positions, 95,044,635 appended positions. At L=64, d_model=8192 that is 4.125e+18 to 4.612e+18 FLOPs, 0.22x to 0.24x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini31pro-ct-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/8QQQWDgmmEsmQVUJWcxx4P.eval); primary `google/gemini-3.1-pro-preview-customtools`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 17 resolved (40.4762%).
Mean per-instance native counters: input 5,287,140, cache write 0, cache read 4,828,368, output 15,670, reasoning 116,637.
Counted workload 24,825,309 + missing-work allowance 0 = 24825309.000000 tokens / 42 completed evaluations = **591078.785714 tokens** x 200,000,000,000 FLOPs/token = **1.182158e+17 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 514,724, standard error of the mean 79,424 (13.4% of the mean). Mean AI working time 2191.9 s. At the 2,000,000-token harness cap: 1 of 42 instances (2.4%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 6972 model calls, mean prefix 29,084 to 31,848 positions, 24,825,309 appended positions. At L=64, d_model=8192 that is 1.514e+18 to 1.658e+18 FLOPs, 0.30x to 0.33x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini31pro-ct-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/8QQQWDgmmEsmQVUJWcxx4P.eval); primary `google/gemini-3.1-pro-preview-customtools`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 8,166,636, cache write 0, cache read 7,531,872, output 15,823, reasoning 70,118.
Counted workload 2,162,116 + missing-work allowance 0 = 2162116.000000 tokens / 3 completed evaluations = **720705.333333 tokens** x 200,000,000,000 FLOPs/token = **1.441411e+17 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 619,909, standard error of the mean 357,904 (49.7% of the mean). Mean AI working time 2377.8 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 588 model calls, mean prefix 38,395 to 41,631 positions, 2,162,116 appended positions. At L=64, d_model=8192 that is 1.741e+17 to 1.888e+17 FLOPs, 0.40x to 0.44x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini35flash-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/dwRzFGTghYEy4HNZajJXoc.eval); primary `epoch/gemini-3.5-flash`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 164 resolved (88.6486%).
Mean per-instance native counters: input 250,562, cache write 0, cache read 593,003, output 2,762, reasoning 8,980.
Counted workload 48,526,160 + missing-work allowance 0 = 48526160.000000 tokens / 185 completed evaluations = **262303.567568 tokens** x 80,000,000,000 FLOPs/token = **2.098429e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 107,430, standard error of the mean 7,898 (3.0% of the mean). Mean AI working time 208.8 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 8942 model calls, mean prefix 12,268 to 17,451 positions, 48,526,160 appended positions. At L=64, d_model=8192 that is 1.248e+18 to 1.776e+18 FLOPs, 0.32x to 0.46x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini35flash-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/dwRzFGTghYEy4HNZajJXoc.eval); primary `epoch/gemini-3.5-flash`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 199 resolved (78.3465%).
Mean per-instance native counters: input 289,869, cache write 0, cache read 969,193, output 3,739, reasoning 13,019.
Counted workload 77,883,186 + missing-work allowance 0 = 77883186.000000 tokens / 254 completed evaluations = **306626.716535 tokens** x 80,000,000,000 FLOPs/token = **2.453014e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 117,644, standard error of the mean 7,382 (2.4% of the mean). Mean AI working time 274.4 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 14942 model calls, mean prefix 16,475 to 21,402 positions, 77,883,186 appended positions. At L=64, d_model=8192 that is 2.691e+18 to 3.496e+18 FLOPs, 0.43x to 0.56x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini35flash-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/dwRzFGTghYEy4HNZajJXoc.eval); primary `epoch/gemini-3.5-flash`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 20 resolved (47.6190%).
Mean per-instance native counters: input 391,451, cache write 0, cache read 1,815,009, output 5,850, reasoning 19,754.
Counted workload 17,516,316 + missing-work allowance 0 = 17516316.000000 tokens / 42 completed evaluations = **417055.142857 tokens** x 80,000,000,000 FLOPs/token = **3.336441e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 140,595, standard error of the mean 21,694 (5.2% of the mean). Mean AI working time 365.0 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 3316 model calls, mean prefix 22,985 to 27,943 positions, 17,516,316 appended positions. At L=64, d_model=8192 that is 8.443e+17 to 1.026e+18 FLOPs, 0.60x to 0.73x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini35flash-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/dwRzFGTghYEy4HNZajJXoc.eval); primary `epoch/gemini-3.5-flash`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 423,381, cache write 0, cache read 2,001,927, output 7,579, reasoning 14,505.
Counted workload 1,336,394 + missing-work allowance 0 = 1336394.000000 tokens / 3 completed evaluations = **445464.666667 tokens** x 80,000,000,000 FLOPs/token = **3.563717e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 138,353, standard error of the mean 79,878 (17.9% of the mean). Mean AI working time 471.6 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 268 model calls, mean prefix 22,368 to 27,098 positions, 1,336,394 appended positions. At L=64, d_model=8192 that is 6.269e+16 to 7.595e+16 FLOPs, 0.59x to 0.71x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini3flash-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/jxoyMNmTnYirjLJN6wRNmG.eval); primary `google/gemini-3-flash-preview`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 164 resolved (88.6486%).
Mean per-instance native counters: input 641,266, cache write 0, cache read 417,792, output 3,429, reasoning 18,013.
Counted workload 45,309,680 + missing-work allowance 0 = 45309680.000000 tokens / 185 completed evaluations = **244917.189189 tokens** x 80,000,000,000 FLOPs/token = **1.959338e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 204,762, standard error of the mean 15,054 (6.1% of the mean). Mean AI working time 270.8 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 10296 model calls, mean prefix 7,507 to 11,523 positions, 45,309,680 appended positions. At L=64, d_model=8192 that is 7.134e+17 to 1.095e+18 FLOPs, 0.20x to 0.30x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini3flash-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/jxoyMNmTnYirjLJN6wRNmG.eval); primary `google/gemini-3-flash-preview`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 190 resolved (74.8031%).
Mean per-instance native counters: input 1,252,684, cache write 0, cache read 944,341, output 6,014, reasoning 27,325.
Counted workload 86,787,007 + missing-work allowance 0 = 86787007.000000 tokens / 254 completed evaluations = **341681.129921 tokens** x 80,000,000,000 FLOPs/token = **2.733449e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 258,975, standard error of the mean 16,250 (4.8% of the mean). Mean AI working time 415.4 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 19460 model calls, mean prefix 12,326 to 16,350 positions, 86,787,007 appended positions. At L=64, d_model=8192 that is 2.243e+18 to 2.976e+18 FLOPs, 0.32x to 0.43x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini3flash-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/jxoyMNmTnYirjLJN6wRNmG.eval); primary `google/gemini-3-flash-preview`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 10 resolved (23.8095%).
Mean per-instance native counters: input 3,423,578, cache write 0, cache read 2,966,968, output 9,658, reasoning 30,271.
Counted workload 20,854,614 + missing-work allowance 0 = 20854614.000000 tokens / 42 completed evaluations = **496538.428571 tokens** x 80,000,000,000 FLOPs/token = **3.972307e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 415,722, standard error of the mean 64,147 (12.9% of the mean). Mean AI working time 518.9 s. At the 2,000,000-token harness cap: 1 of 42 instances (2.4%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 5178 model calls, mean prefix 24,066 to 27,769 positions, 20,854,614 appended positions. At L=64, d_model=8192 that is 1.053e+18 to 1.215e+18 FLOPs, 0.63x to 0.73x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini3flash-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/jxoyMNmTnYirjLJN6wRNmG.eval); primary `google/gemini-3-flash-preview`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 2,119,709, cache write 0, cache read 1,724,345, output 16,343, reasoning 22,315.
Counted workload 1,302,065 + missing-work allowance 0 = 1302065.000000 tokens / 3 completed evaluations = **434021.666667 tokens** x 80,000,000,000 FLOPs/token = **3.472173e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 249,250, standard error of the mean 143,905 (33.2% of the mean). Mean AI working time 1035.1 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 321 model calls, mean prefix 16,115 to 19,810 positions, 1,302,065 appended positions. At L=64, d_model=8192 that is 4.401e+16 to 5.409e+16 FLOPs, 0.42x to 0.52x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini3pro-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/5XdYZBG5Wy8DUMRqcYv4fn.eval); primary `google/gemini-3-pro-preview`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 161 resolved (87.0270%).
Mean per-instance native counters: input 1,946,002, cache write 0, cache read 1,760,857, output 6,328, reasoning 10,571.
Counted workload 37,378,157 + missing-work allowance 0 = 37378157.000000 tokens / 185 completed evaluations = **202044.091892 tokens** x 200,000,000,000 FLOPs/token = **4.040882e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 186,133, standard error of the mean 13,685 (6.8% of the mean). Mean AI working time 431.5 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 17210 model calls, mean prefix 18,928 to 20,919 positions, 37,378,157 appended positions. At L=64, d_model=8192 that is 1.484e+18 to 1.640e+18 FLOPs, 0.20x to 0.22x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini3pro-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/5XdYZBG5Wy8DUMRqcYv4fn.eval); primary `google/gemini-3-pro-preview`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 177 resolved (69.6850%).
Mean per-instance native counters: input 3,543,485, cache write 0, cache read 3,286,435, output 9,637, reasoning 13,584.
Counted workload 71,188,736 + missing-work allowance 0 = 71188736.000000 tokens / 254 completed evaluations = **280270.614173 tokens** x 200,000,000,000 FLOPs/token = **5.605412e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 254,987, standard error of the mean 15,999 (5.7% of the mean). Mean AI working time 634.3 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 31206 model calls, mean prefix 26,749 to 28,842 positions, 71,188,736 appended positions. At L=64, d_model=8192 that is 3.994e+18 to 4.306e+18 FLOPs, 0.28x to 0.30x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini3pro-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/5XdYZBG5Wy8DUMRqcYv4fn.eval); primary `google/gemini-3-pro-preview`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 14 resolved (33.3333%).
Mean per-instance native counters: input 7,205,893, cache write 0, cache read 6,785,999, output 16,760, reasoning 21,695.
Counted workload 19,250,663 + missing-work allowance 0 = 19250663.000000 tokens / 42 completed evaluations = **458349.119048 tokens** x 200,000,000,000 FLOPs/token = **9.166982e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 337,119, standard error of the mean 52,019 (11.3% of the mean). Mean AI working time 906.5 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 7568 model calls, mean prefix 37,663 to 39,993 positions, 19,250,663 appended positions. At L=64, d_model=8192 that is 1.520e+18 to 1.615e+18 FLOPs, 0.39x to 0.42x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gemini3pro-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/5XdYZBG5Wy8DUMRqcYv4fn.eval); primary `google/gemini-3-pro-preview`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 4,509,921, cache write 0, cache read 4,209,646, output 8,153, reasoning 18,938.
Counted workload 982,097 + missing-work allowance 0 = 982097.000000 tokens / 3 completed evaluations = **327365.666667 tokens** x 200,000,000,000 FLOPs/token = **6.547313e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 271,067, standard error of the mean 156,501 (47.8% of the mean). Mean AI working time 747.8 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 351 model calls, mean prefix 35,980 to 38,546 positions, 982,097 appended positions. At L=64, d_model=8192 that is 7.410e+16 to 7.939e+16 FLOPs, 0.38x to 0.40x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-glm5-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/hKkJEu4ueLiNWsTtrJ78PS.eval); primary `zhipu/glm-5`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 180 completed evaluations, 148 resolved (82.2222%).
Mean per-instance native counters: input 1,645,384, cache write 0, cache read 1,536,218, output 19,487, reasoning 0.
Counted workload 23,800,873 + missing-work allowance 0 = 23800873.000000 tokens / 180 completed evaluations = **132227.072222 tokens** x 80,000,000,000 FLOPs/token = **1.057817e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 252,457, standard error of the mean 18,561 (14.4% of the mean). Mean AI working time 1135.8 s. At the 2,000,000-token harness cap: 3 of 185 instances (1.6%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 19558 model calls, mean prefix 14,531 to 15,564 positions, 23,800,873 appended positions. At L=64, d_model=8192 that is 7.253e+17 to 7.769e+17 FLOPs, 0.38x to 0.41x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-glm5-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/hKkJEu4ueLiNWsTtrJ78PS.eval); primary `zhipu/glm-5`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 238 completed evaluations, 167 resolved (70.1681%).
Mean per-instance native counters: input 2,285,051, cache write 0, cache read 2,084,944, output 25,763, reasoning 0.
Counted workload 57,371,128 + missing-work allowance 0 = 57371128.000000 tokens / 238 completed evaluations = **241055.159664 tokens** x 80,000,000,000 FLOPs/token = **1.928441e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 433,306, standard error of the mean 27,188 (12.0% of the mean). Mean AI working time 1430.2 s. At the 2,000,000-token harness cap: 13 of 254 instances (5.1%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 32130 model calls, mean prefix 16,482 to 18,064 positions, 57,371,128 appended positions. At L=64, d_model=8192 that is 1.983e+18 to 2.173e+18 FLOPs, 0.43x to 0.47x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-glm5-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/hKkJEu4ueLiNWsTtrJ78PS.eval); primary `zhipu/glm-5`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 41 completed evaluations, 17 resolved (41.4634%).
Mean per-instance native counters: input 4,154,562, cache write 0, cache read 3,717,670, output 41,724, reasoning 0.
Counted workload 20,101,853 + missing-work allowance 0 = 20101853.000000 tokens / 41 completed evaluations = **490289.097561 tokens** x 80,000,000,000 FLOPs/token = **3.922313e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 654,573, standard error of the mean 101,003 (21.1% of the mean). Mean AI working time 2332.9 s. At the 2,000,000-token harness cap: 6 of 42 instances (14.3%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 7687 model calls, mean prefix 20,312 to 22,700 positions, 20,101,853 appended positions. At L=64, d_model=8192 that is 8.563e+17 to 9.569e+17 FLOPs, 0.53x to 0.60x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-glm5-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/hKkJEu4ueLiNWsTtrJ78PS.eval); primary `zhipu/glm-5`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 2,114,220, cache write 0, cache read 1,989,952, output 22,853, reasoning 0.
Counted workload 441,362 + missing-work allowance 0 = 441362.000000 tokens / 3 completed evaluations = **147120.666667 tokens** x 80,000,000,000 FLOPs/token = **1.176965e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 39,035, standard error of the mean 22,537 (15.3% of the mean). Mean AI working time 1345.1 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 396 model calls, mean prefix 15,075 to 16,017 positions, 441,362 appended positions. At L=64, d_model=8192 that is 1.395e+16 to 1.483e+16 FLOPs, 0.40x to 0.42x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-glm52max-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/4AfhcmYVNrw6gM5u8CQsyy.eval); primary `epoch/glm-5.2`; reasoning_effort=max; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 184 completed evaluations, 164 resolved (89.1304%).
Mean per-instance native counters: input 34,739, cache write 0, cache read 1,228,106, output 20,461, reasoning 10,477.
Counted workload 10,212,143 + missing-work allowance 2160.209758 = 10214303.209758 tokens / 184 completed evaluations = **55512.517444 tokens** x 80,000,000,000 FLOPs/token = **4.441001e+15 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 62,444, standard error of the mean 4,591 (8.3% of the mean). Mean AI working time 627.2 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). Recorded counters alone give 55500.777174 tokens per completed evaluation.
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 14070 model calls, mean prefix 16,148 to 16,605 positions, 10,212,143 appended positions. At L=64, d_model=8192 that is 3.458e+17 to 3.556e+17 FLOPs, 0.42x to 0.44x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-glm52max-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/4AfhcmYVNrw6gM5u8CQsyy.eval); primary `epoch/glm-5.2`; reasoning_effort=max; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 196 resolved (77.1654%).
Mean per-instance native counters: input 64,804, cache write 0, cache read 2,722,190, output 35,599, reasoning 14,631.
Counted workload 25,502,213 + missing-work allowance 4080.568820 = 25506293.568820 tokens / 254 completed evaluations = **100418.478617 tokens** x 80,000,000,000 FLOPs/token = **8.033478e+15 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 102,052, standard error of the mean 6,403 (6.4% of the mean). Mean AI working time 1035.0 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). Recorded counters alone give 100402.413386 tokens per completed evaluation.
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 29188 model calls, mean prefix 23,689 to 24,253 positions, 25,502,213 appended positions. At L=64, d_model=8192 that is 1.267e+18 to 1.297e+18 FLOPs, 0.62x to 0.64x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-glm52max-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/4AfhcmYVNrw6gM5u8CQsyy.eval); primary `epoch/glm-5.2`; reasoning_effort=max; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 19 resolved (45.2381%).
Mean per-instance native counters: input 117,109, cache write 0, cache read 7,289,155, output 56,446, reasoning 14,864.
Counted workload 7,289,324 + missing-work allowance 1592.553219 = 7290916.553219 tokens / 42 completed evaluations = **173593.251267 tokens** x 80,000,000,000 FLOPs/token = **1.388746e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 118,555, standard error of the mean 18,293 (10.5% of the mean). Mean AI working time 1651.9 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). Recorded counters alone give 173555.333333 tokens per completed evaluation.
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 7988 model calls, mean prefix 38,323 to 38,939 positions, 7,289,324 appended positions. At L=64, d_model=8192 that is 5.858e+17 to 5.953e+17 FLOPs, 1.00x to 1.02x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-glm52max-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/4AfhcmYVNrw6gM5u8CQsyy.eval); primary `epoch/glm-5.2`; reasoning_effort=max; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 74,539, cache write 0, cache read 4,690,304, output 44,120, reasoning 9,301.
Counted workload 355,978 + missing-work allowance 0 = 355978.000000 tokens / 3 completed evaluations = **118659.333333 tokens** x 80,000,000,000 FLOPs/token = **9.492747e+15 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 75,088, standard error of the mean 43,352 (36.5% of the mean). Mean AI working time 1837.6 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 503 model calls, mean prefix 27,974 to 28,419 positions, 355,978 appended positions. At L=64, d_model=8192 that is 2.088e+16 to 2.122e+16 FLOPs, 0.73x to 0.74x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt41-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/SheUt9cNpkSevy4r6Gsr3u.eval); primary `openai/gpt-4.1-2025-04-14`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 184 completed evaluations, 123 resolved (66.8478%).
Mean per-instance native counters: input 367,761, cache write 0, cache read 298,446, output 1,577, reasoning 0.
Counted workload 13,115,012 + missing-work allowance 0 = 13115012.000000 tokens / 184 completed evaluations = **71277.239130 tokens** x 100,000,000,000 FLOPs/token = **7.127724e+15 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 73,177, standard error of the mean 5,380 (7.6% of the mean). Mean AI working time 243.7 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 7720 model calls, mean prefix 7,152 to 8,813 positions, 13,115,012 appended positions. At L=64, d_model=8192 that is 1.967e+17 to 2.424e+17 FLOPs, 0.15x to 0.18x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt41-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/SheUt9cNpkSevy4r6Gsr3u.eval); primary `openai/gpt-4.1-2025-04-14`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 252 completed evaluations, 105 resolved (41.6667%).
Mean per-instance native counters: input 851,317, cache write 0, cache read 737,782, output 2,898, reasoning 0.
Counted workload 29,573,869 + missing-work allowance 0 = 29573869.000000 tokens / 252 completed evaluations = **117356.623016 tokens** x 100,000,000,000 FLOPs/token = **1.173566e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 172,890, standard error of the mean 10,848 (9.3% of the mean). Mean AI working time 362.2 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 14534 model calls, mean prefix 12,893 to 14,877 positions, 29,573,869 appended positions. At L=64, d_model=8192 that is 7.997e+17 to 9.227e+17 FLOPs, 0.27x to 0.31x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt41-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/SheUt9cNpkSevy4r6Gsr3u.eval); primary `openai/gpt-4.1-2025-04-14`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 41 completed evaluations, 5 resolved (12.1951%).
Mean per-instance native counters: input 672,132, cache write 0, cache read 554,398, output 3,096, reasoning 0.
Counted workload 5,074,828 + missing-work allowance 0 = 5074828.000000 tokens / 41 completed evaluations = **123776.292683 tokens** x 100,000,000,000 FLOPs/token = **1.237763e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 91,730, standard error of the mean 14,154 (11.7% of the mean). Mean AI working time 286.4 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 2322 model calls, mean prefix 10,026 to 12,155 positions, 5,074,828 appended positions. At L=64, d_model=8192 that is 1.067e+17 to 1.294e+17 FLOPs, 0.21x to 0.25x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt41-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/SheUt9cNpkSevy4r6Gsr3u.eval); primary `openai/gpt-4.1-2025-04-14`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 0 resolved (0.0000%).
Mean per-instance native counters: input 768,565, cache write 0, cache read 614,741, output 2,874, reasoning 0.
Counted workload 470,091 + missing-work allowance 0 = 470091.000000 tokens / 3 completed evaluations = **156697.000000 tokens** x 100,000,000,000 FLOPs/token = **1.566970e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 183,304, standard error of the mean 105,830 (67.5% of the mean). Mean AI working time 334.3 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 144 model calls, mean prefix 12,852 to 16,068 positions, 470,091 appended positions. At L=64, d_model=8192 that is 1.267e+16 to 1.584e+16 FLOPs, 0.27x to 0.34x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt4o1120-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/PncXWJm7ZCY3qv982pKoRy.eval); primary `openai/gpt-4o-2024-11-20`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 91 resolved (49.1892%).
Mean per-instance native counters: input 526,253, cache write 0, cache read 486,171, output 2,119, reasoning 0.
Counted workload 7,807,158 + missing-work allowance 0 = 7807158.000000 tokens / 185 completed evaluations = **42200.854054 tokens** x 100,000,000,000 FLOPs/token = **4.220085e+15 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 77,798, standard error of the mean 5,720 (13.6% of the mean). Mean AI working time 261.2 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 7406 model calls, mean prefix 12,145 to 13,147 positions, 7,807,158 appended positions. At L=64, d_model=8192 that is 1.989e+17 to 2.152e+17 FLOPs, 0.25x to 0.28x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt4o1120-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/PncXWJm7ZCY3qv982pKoRy.eval); primary `openai/gpt-4o-2024-11-20`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 56 resolved (22.0472%).
Mean per-instance native counters: input 1,008,889, cache write 0, cache read 943,034, output 3,355, reasoning 0.
Counted workload 17,579,342 + missing-work allowance 0 = 17579342.000000 tokens / 254 completed evaluations = **69210.007874 tokens** x 100,000,000,000 FLOPs/token = **6.921001e+15 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 109,509, standard error of the mean 6,871 (9.9% of the mean). Mean AI working time 387.9 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 14278 model calls, mean prefix 16,776 to 17,948 positions, 17,579,342 appended positions. At L=64, d_model=8192 that is 6.185e+17 to 6.617e+17 FLOPs, 0.35x to 0.38x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt4o1120-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/PncXWJm7ZCY3qv982pKoRy.eval); primary `openai/gpt-4o-2024-11-20`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 3 resolved (7.1429%).
Mean per-instance native counters: input 628,112, cache write 0, cache read 579,977, output 3,011, reasoning 0.
Counted workload 2,148,124 + missing-work allowance 0 = 2148124.000000 tokens / 42 completed evaluations = **51145.809524 tokens** x 100,000,000,000 FLOPs/token = **5.114581e+15 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 67,378, standard error of the mean 10,397 (20.3% of the mean). Mean AI working time 312.0 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 2005 model calls, mean prefix 12,149 to 13,157 positions, 2,148,124 appended positions. At L=64, d_model=8192 that is 5.473e+16 to 5.927e+16 FLOPs, 0.25x to 0.28x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt4o1120-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/PncXWJm7ZCY3qv982pKoRy.eval); primary `openai/gpt-4o-2024-11-20`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 0 resolved (0.0000%).
Mean per-instance native counters: input 153,385, cache write 0, cache read 126,421, output 1,474, reasoning 0.
Counted workload 85,314 + missing-work allowance 0 = 85314.000000 tokens / 3 completed evaluations = **28438.000000 tokens** x 100,000,000,000 FLOPs/token = **2.843800e+15 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 18,324, standard error of the mean 10,579 (37.2% of the mean). Mean AI working time 128.4 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 84 model calls, mean prefix 4,515 to 5,478 positions, 85,314 appended positions. At L=64, d_model=8192 that is 8.078e+14 to 9.801e+14 FLOPs, 0.09x to 0.11x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt51codex-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/G5hTYKeE5buuWzwRQK7EgS.eval); primary `openai/gpt-5.1-2025-11-13`; reasoning_effort=high; Inspect task `swe_bench_codex` (the Codex CLI agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 140 resolved (75.6757%).
Mean per-instance native counters: input 862,954, cache write 0, cache read 798,373, output 10,543, reasoning 7,768.
Counted workload 13,897,789 + missing-work allowance 0 = 13897789.000000 tokens / 185 completed evaluations = **75123.183784 tokens** x 200,000,000,000 FLOPs/token = **1.502464e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 53,508, standard error of the mean 3,934 (5.2% of the mean). Mean AI working time 349.8 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 5817 model calls, mean prefix 25,391 to 27,445 positions, 13,897,789 appended positions. At L=64, d_model=8192 that is 7.400e+17 to 7.999e+17 FLOPs, 0.27x to 0.29x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt51codex-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/G5hTYKeE5buuWzwRQK7EgS.eval); primary `openai/gpt-5.1-2025-11-13`; reasoning_effort=high; Inspect task `swe_bench_codex` (the Codex CLI agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 164 resolved (64.5669%).
Mean per-instance native counters: input 1,413,520, cache write 0, cache read 1,316,014, output 15,171, reasoning 11,595.
Counted workload 28,620,075 + missing-work allowance 0 = 28620075.000000 tokens / 254 completed evaluations = **112677.460630 tokens** x 200,000,000,000 FLOPs/token = **2.253549e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 79,042, standard error of the mean 4,960 (4.4% of the mean). Mean AI working time 483.7 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 10128 model calls, mean prefix 33,003 to 35,448 positions, 28,620,075 appended positions. At L=64, d_model=8192 that is 1.981e+18 to 2.128e+18 FLOPs, 0.35x to 0.37x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt51codex-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/G5hTYKeE5buuWzwRQK7EgS.eval); primary `openai/gpt-5.1-2025-11-13`; reasoning_effort=high; Inspect task `swe_bench_codex` (the Codex CLI agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 14 resolved (33.3333%).
Mean per-instance native counters: input 2,721,562, cache write 0, cache read 2,542,171, output 25,939, reasoning 20,366.
Counted workload 8,623,836 + missing-work allowance 0 = 8623836.000000 tokens / 42 completed evaluations = **205329.428571 tokens** x 200,000,000,000 FLOPs/token = **4.106589e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 173,971, standard error of the mean 26,844 (13.1% of the mean). Mean AI working time 771.9 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 2237 model calls, mean prefix 47,730 to 51,098 positions, 8,623,836 appended positions. At L=64, d_model=8192 that is 8.632e+17 to 9.241e+17 FLOPs, 0.50x to 0.54x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt51codex-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/G5hTYKeE5buuWzwRQK7EgS.eval); primary `openai/gpt-5.1-2025-11-13`; reasoning_effort=high; Inspect task `swe_bench_codex` (the Codex CLI agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 2,970,552, cache write 0, cache read 2,807,168, output 28,313, reasoning 19,731.
Counted workload 575,092 + missing-work allowance 0 = 575092.000000 tokens / 3 completed evaluations = **191697.333333 tokens** x 200,000,000,000 FLOPs/token = **3.833947e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 157,957, standard error of the mean 91,196 (47.6% of the mean). Mean AI working time 785.0 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 196 model calls, mean prefix 42,967 to 45,468 positions, 575,092 appended positions. At L=64, d_model=8192 that is 5.182e+16 to 5.484e+16 FLOPs, 0.45x to 0.48x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt51high-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/YoHtZpMNdsRE6qdj2K4Ucj.eval); primary `openai/gpt-5.1-2025-11-13`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 150 resolved (81.0811%).
Mean per-instance native counters: input 1,263,147, cache write 0, cache read 958,281, output 40,823, reasoning 36,844.
Counted workload 63,952,563 + missing-work allowance 0 = 63952563.000000 tokens / 185 completed evaluations = **345689.529730 tokens** x 200,000,000,000 FLOPs/token = **6.913791e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 416,269, standard error of the mean 30,605 (8.9% of the mean). Mean AI working time 970.3 s. At the 2,000,000-token harness cap: 5 of 185 instances (2.7%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 10370 model calls, mean prefix 17,096 to 22,536 positions, 63,952,563 appended positions. At L=64, d_model=8192 that is 2.293e+18 to 3.022e+18 FLOPs, 0.18x to 0.24x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt51high-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/YoHtZpMNdsRE6qdj2K4Ucj.eval); primary `openai/gpt-5.1-2025-11-13`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 167 resolved (65.7480%).
Mean per-instance native counters: input 1,796,204, cache write 0, cache read 1,362,192, output 64,903, reasoning 59,476.
Counted workload 126,724,355 + missing-work allowance 0 = 126724355.000000 tokens / 254 completed evaluations = **498914.783465 tokens** x 200,000,000,000 FLOPs/token = **9.978296e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 502,161, standard error of the mean 31,508 (6.3% of the mean). Mean AI working time 1412.5 s. At the 2,000,000-token harness cap: 14 of 254 instances (5.5%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 17634 model calls, mean prefix 19,622 to 25,873 positions, 126,724,355 appended positions. At L=64, d_model=8192 that is 5.215e+18 to 6.876e+18 FLOPs, 0.21x to 0.27x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt51high-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/YoHtZpMNdsRE6qdj2K4Ucj.eval); primary `openai/gpt-5.1-2025-11-13`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 12 resolved (28.5714%).
Mean per-instance native counters: input 2,856,535, cache write 0, cache read 2,244,852, output 97,000, reasoning 89,473.
Counted workload 29,764,703 + missing-work allowance 0 = 29764703.000000 tokens / 42 completed evaluations = **708683.404762 tokens** x 200,000,000,000 FLOPs/token = **1.417367e+17 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 501,616, standard error of the mean 77,401 (10.9% of the mean). Mean AI working time 2109.4 s. At the 2,000,000-token harness cap: 3 of 42 instances (7.1%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 3840 model calls, mean prefix 24,553 to 31,243 positions, 29,764,703 appended positions. At L=64, d_model=8192 that is 1.533e+18 to 1.950e+18 FLOPs, 0.26x to 0.33x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt51high-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/YoHtZpMNdsRE6qdj2K4Ucj.eval); primary `openai/gpt-5.1-2025-11-13`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 0 resolved (0.0000%).
Mean per-instance native counters: input 1,910,641, cache write 0, cache read 1,501,653, output 64,039, reasoning 55,887.
Counted workload 1,419,080 + missing-work allowance 0 = 1419080.000000 tokens / 3 completed evaluations = **473026.666667 tokens** x 200,000,000,000 FLOPs/token = **9.460533e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 169,312, standard error of the mean 97,752 (20.7% of the mean). Mean AI working time 1861.4 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 220 model calls, mean prefix 20,524 to 26,114 positions, 1,419,080 appended positions. At L=64, d_model=8192 that is 6.108e+16 to 7.771e+16 FLOPs, 0.22x to 0.27x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt52high-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/9owdbpnWJ5pkQQC3GWKP5L.eval); primary `openai/gpt-5.2-2025-12-11`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 158 resolved (85.4054%).
Mean per-instance native counters: input 848,671, cache write 0, cache read 606,730, output 27,465, reasoning 23,985.
Counted workload 49,840,275 + missing-work allowance 0 = 49840275.000000 tokens / 185 completed evaluations = **269406.891892 tokens** x 200,000,000,000 FLOPs/token = **5.388138e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 307,902, standard error of the mean 22,637 (8.4% of the mean). Mean AI working time 839.8 s. At the 2,000,000-token harness cap: 2 of 185 instances (1.1%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 11226 model calls, mean prefix 9,999 to 13,986 positions, 49,840,275 appended positions. At L=64, d_model=8192 that is 1.045e+18 to 1.462e+18 FLOPs, 0.10x to 0.15x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt52high-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/9owdbpnWJ5pkQQC3GWKP5L.eval); primary `openai/gpt-5.2-2025-12-11`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 182 resolved (71.6535%).
Mean per-instance native counters: input 1,427,102, cache write 0, cache read 1,071,330, output 48,447, reasoning 43,486.
Counted workload 102,671,860 + missing-work allowance 0 = 102671860.000000 tokens / 254 completed evaluations = **404219.921260 tokens** x 200,000,000,000 FLOPs/token = **8.084398e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 367,744, standard error of the mean 23,074 (5.7% of the mean). Mean AI working time 1377.7 s. At the 2,000,000-token harness cap: 2 of 254 instances (0.8%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 21335 model calls, mean prefix 12,755 to 16,990 positions, 102,671,860 appended positions. At L=64, d_model=8192 that is 2.746e+18 to 3.658e+18 FLOPs, 0.13x to 0.18x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt52high-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/9owdbpnWJ5pkQQC3GWKP5L.eval); primary `openai/gpt-5.2-2025-12-11`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 16 resolved (38.0952%).
Mean per-instance native counters: input 4,616,199, cache write 0, cache read 3,940,803, output 113,998, reasoning 103,734.
Counted workload 33,154,518 + missing-work allowance 0 = 33154518.000000 tokens / 42 completed evaluations = **789393.285714 tokens** x 200,000,000,000 FLOPs/token = **1.578787e+17 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 579,349, standard error of the mean 89,396 (11.3% of the mean). Mean AI working time 2777.5 s. At the 2,000,000-token harness cap: 2 of 42 instances (4.8%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 6362 model calls, mean prefix 26,018 to 30,477 positions, 33,154,518 appended positions. At L=64, d_model=8192 that is 1.809e+18 to 2.119e+18 FLOPs, 0.27x to 0.32x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt52high-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/9owdbpnWJ5pkQQC3GWKP5L.eval); primary `openai/gpt-5.2-2025-12-11`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 3,390,768, cache write 0, cache read 2,512,725, output 62,524, reasoning 54,539.
Counted workload 2,821,700 + missing-work allowance 0 = 2821700.000000 tokens / 3 completed evaluations = **940566.666667 tokens** x 200,000,000,000 FLOPs/token = **1.881133e+17 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 976,286, standard error of the mean 563,659 (59.9% of the mean). Mean AI working time 2562.7 s. At the 2,000,000-token harness cap: 1 of 3 instances (33.3%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 349 model calls, mean prefix 21,599 to 29,147 positions, 2,821,700 appended positions. At L=64, d_model=8192 that is 1.278e+17 to 1.725e+17 FLOPs, 0.23x to 0.31x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt53codex-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/6w5buMbgeEqtRoE55cLZVv.eval); primary `openai/gpt-5.3-codex`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 154 resolved (83.2432%).
Mean per-instance native counters: input 317,837, cache write 0, cache read 185,249, output 8,736, reasoning 7,106.
Counted workload 26,145,007 + missing-work allowance 0 = 26145007.000000 tokens / 185 completed evaluations = **141324.362162 tokens** x 200,000,000,000 FLOPs/token = **2.826487e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 133,131, standard error of the mean 9,788 (6.9% of the mean). Mean AI working time 214.0 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 6018 model calls, mean prefix 5,695 to 9,771 positions, 26,145,007 appended positions. At L=64, d_model=8192 that is 3.123e+17 to 5.358e+17 FLOPs, 0.06x to 0.10x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt53codex-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/6w5buMbgeEqtRoE55cLZVv.eval); primary `openai/gpt-5.3-codex`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 187 resolved (73.6220%).
Mean per-instance native counters: input 544,161, cache write 0, cache read 345,673, output 15,634, reasoning 13,243.
Counted workload 54,386,971 + missing-work allowance 0 = 54386971.000000 tokens / 254 completed evaluations = **214121.933071 tokens** x 200,000,000,000 FLOPs/token = **4.282439e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 164,305, standard error of the mean 10,309 (4.8% of the mean). Mean AI working time 392.8 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 10971 model calls, mean prefix 8,003 to 12,598 positions, 54,386,971 appended positions. At L=64, d_model=8192 that is 9.128e+17 to 1.437e+18 FLOPs, 0.08x to 0.13x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt53codex-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/6w5buMbgeEqtRoE55cLZVv.eval); primary `openai/gpt-5.3-codex`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 20 resolved (47.6190%).
Mean per-instance native counters: input 1,206,108, cache write 0, cache read 823,854, output 32,474, reasoning 28,724.
Counted workload 17,418,601 + missing-work allowance 0 = 17418601.000000 tokens / 42 completed evaluations = **414728.595238 tokens** x 200,000,000,000 FLOPs/token = **8.294572e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 305,339, standard error of the mean 47,115 (11.4% of the mean). Mean AI working time 721.5 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 2712 model calls, mean prefix 12,756 to 18,675 positions, 17,418,601 appended positions. At L=64, d_model=8192 that is 4.660e+17 to 6.822e+17 FLOPs, 0.13x to 0.20x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt53codex-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/6w5buMbgeEqtRoE55cLZVv.eval); primary `openai/gpt-5.3-codex`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 1,039,287, cache write 0, cache read 565,504, output 19,259, reasoning 15,240.
Counted workload 1,479,125 + missing-work allowance 0 = 1479125.000000 tokens / 3 completed evaluations = **493041.666667 tokens** x 200,000,000,000 FLOPs/token = **9.860833e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 611,011, standard error of the mean 352,768 (71.5% of the mean). Mean AI working time 644.7 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 146 model calls, mean prefix 11,620 to 21,355 positions, 1,479,125 appended positions. At L=64, d_model=8192 that is 3.604e+16 to 6.624e+16 FLOPs, 0.12x to 0.22x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt54high-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/i9HTMbAxcwsrTf2w2FuJ6N.eval); primary `openai/gpt-5.4-2026-03-05`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 161 resolved (87.0270%).
Mean per-instance native counters: input 292,597, cache write 0, cache read 220,098, output 14,281, reasoning 13,132.
Counted workload 16,054,381 + missing-work allowance 0 = 16054381.000000 tokens / 185 completed evaluations = **86780.437838 tokens** x 200,000,000,000 FLOPs/token = **1.735609e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 98,067, standard error of the mean 7,210 (8.3% of the mean). Mean AI working time 293.9 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 3819 model calls, mean prefix 10,662 to 14,174 positions, 16,054,381 appended positions. At L=64, d_model=8192 that is 3.590e+17 to 4.772e+17 FLOPs, 0.11x to 0.15x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt54high-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/i9HTMbAxcwsrTf2w2FuJ6N.eval); primary `openai/gpt-5.4-2026-03-05`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 188 resolved (74.0157%).
Mean per-instance native counters: input 625,839, cache write 0, cache read 500,530, output 27,087, reasoning 25,171.
Counted workload 38,708,589 + missing-work allowance 0 = 38708589.000000 tokens / 254 completed evaluations = **152396.019685 tokens** x 200,000,000,000 FLOPs/token = **3.047920e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 159,116, standard error of the mean 9,984 (6.6% of the mean). Mean AI working time 518.8 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 7470 model calls, mean prefix 17,018 to 21,279 positions, 38,708,589 appended positions. At L=64, d_model=8192 that is 1.382e+18 to 1.727e+18 FLOPs, 0.18x to 0.22x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt54high-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/i9HTMbAxcwsrTf2w2FuJ6N.eval); primary `openai/gpt-5.4-2026-03-05`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 22 resolved (52.3810%).
Mean per-instance native counters: input 1,529,471, cache write 0, cache read 1,305,164, output 61,617, reasoning 57,589.
Counted workload 12,008,765 + missing-work allowance 0 = 12008765.000000 tokens / 42 completed evaluations = **285922.976190 tokens** x 200,000,000,000 FLOPs/token = **5.718460e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 328,587, standard error of the mean 50,702 (17.7% of the mean). Mean AI working time 1124.4 s. At the 2,000,000-token harness cap: 1 of 42 instances (2.4%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 2016 model calls, mean prefix 27,191 to 31,864 positions, 12,008,765 appended positions. At L=64, d_model=8192 that is 6.848e+17 to 8.025e+17 FLOPs, 0.29x to 0.33x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt54high-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/i9HTMbAxcwsrTf2w2FuJ6N.eval); primary `openai/gpt-5.4-2026-03-05`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 1,482,582, cache write 0, cache read 1,213,397, output 88,596, reasoning 83,924.
Counted workload 1,073,341 + missing-work allowance 0 = 1073341.000000 tokens / 3 completed evaluations = **357780.333333 tokens** x 200,000,000,000 FLOPs/token = **7.155607e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 26,996, standard error of the mean 15,586 (4.4% of the mean). Mean AI working time 1625.9 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 164 model calls, mean prefix 22,129 to 27,038 positions, 1,073,341 appended positions. At L=64, d_model=8192 that is 4.981e+16 to 6.086e+16 FLOPs, 0.23x to 0.28x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt5high-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/C85Bnci9xVzq5jmt8zNnbw.eval); primary `openai/gpt-5-2025-08-07`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 161 resolved (87.0270%).
Mean per-instance native counters: input 1,694,204, cache write 0, cache read 1,574,087, output 42,828, reasoning 35,645.
Counted workload 30,144,904 + missing-work allowance 0 = 30144904.000000 tokens / 185 completed evaluations = **162945.427027 tokens** x 200,000,000,000 FLOPs/token = **3.258909e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 211,104, standard error of the mean 15,521 (9.5% of the mean). Mean AI working time 1159.5 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 12518 model calls, mean prefix 23,264 to 25,039 positions, 30,144,904 appended positions. At L=64, d_model=8192 that is 1.471e+18 to 1.583e+18 FLOPs, 0.24x to 0.26x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt5high-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/C85Bnci9xVzq5jmt8zNnbw.eval); primary `openai/gpt-5-2025-08-07`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 179 resolved (70.4724%).
Mean per-instance native counters: input 2,302,285, cache write 0, cache read 2,140,577, output 59,091, reasoning 50,392.
Counted workload 56,082,935 + missing-work allowance 0 = 56082935.000000 tokens / 254 completed evaluations = **220798.956693 tokens** x 200,000,000,000 FLOPs/token = **4.415979e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 244,511, standard error of the mean 15,342 (6.9% of the mean). Mean AI working time 1610.2 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 20984 model calls, mean prefix 25,911 to 27,869 positions, 56,082,935 appended positions. At L=64, d_model=8192 that is 3.048e+18 to 3.278e+18 FLOPs, 0.27x to 0.29x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt5high-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/C85Bnci9xVzq5jmt8zNnbw.eval); primary `openai/gpt-5-2025-08-07`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 15 resolved (35.7143%).
Mean per-instance native counters: input 4,034,518, cache write 0, cache read 3,780,584, output 103,875, reasoning 88,713.
Counted workload 15,027,987 + missing-work allowance 0 = 15027987.000000 tokens / 42 completed evaluations = **357809.214286 tokens** x 200,000,000,000 FLOPs/token = **7.156184e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 323,940, standard error of the mean 49,985 (14.0% of the mean). Mean AI working time 2645.6 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 4972 model calls, mean prefix 31,939 to 34,084 positions, 15,027,987 appended positions. At L=64, d_model=8192 that is 1.007e+18 to 1.074e+18 FLOPs, 0.33x to 0.36x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt5high-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/C85Bnci9xVzq5jmt8zNnbw.eval); primary `openai/gpt-5-2025-08-07`; reasoning_effort=high; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 1,100,633, cache write 0, cache read 970,837, output 38,938, reasoning 33,792.
Counted workload 506,201 + missing-work allowance 0 = 506201.000000 tokens / 3 completed evaluations = **168733.666667 tokens** x 200,000,000,000 FLOPs/token = **3.374673e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 57,093, standard error of the mean 32,963 (19.5% of the mean). Mean AI working time 1065.4 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 186 model calls, mean prefix 15,617 to 17,705 positions, 506,201 appended positions. At L=64, d_model=8192 that is 1.658e+16 to 1.879e+16 FLOPs, 0.16x to 0.19x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt5med-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/FCCkMNVHcjLLUDeNFqTGRL.eval); primary `openai/gpt-5-2025-08-07`; reasoning_effort=medium; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 158 resolved (85.4054%).
Mean per-instance native counters: input 614,352, cache write 0, cache read 433,400, output 16,557, reasoning 13,246.
Counted workload 36,539,060 + missing-work allowance 0 = 36539060.000000 tokens / 185 completed evaluations = **197508.432432 tokens** x 200,000,000,000 FLOPs/token = **3.950169e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 258,541, standard error of the mean 19,008 (9.6% of the mean). Mean AI working time 570.2 s. At the 2,000,000-token harness cap: 2 of 185 instances (1.1%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 7267 model calls, mean prefix 11,033 to 15,640 positions, 36,539,060 appended positions. At L=64, d_model=8192 that is 8.455e+17 to 1.198e+18 FLOPs, 0.12x to 0.16x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt5med-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/FCCkMNVHcjLLUDeNFqTGRL.eval); primary `openai/gpt-5-2025-08-07`; reasoning_effort=medium; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 172 resolved (67.7165%).
Mean per-instance native counters: input 1,079,626, cache write 0, cache read 847,228, output 23,578, reasoning 18,602.
Counted workload 65,017,735 + missing-work allowance 0 = 65017735.000000 tokens / 254 completed evaluations = **255975.334646 tokens** x 200,000,000,000 FLOPs/token = **5.119507e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 259,833, standard error of the mean 16,303 (6.4% of the mean). Mean AI working time 816.8 s. At the 2,000,000-token harness cap: 1 of 254 instances (0.4%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 13171 model calls, mean prefix 16,339 to 20,820 positions, 65,017,735 appended positions. At L=64, d_model=8192 that is 2.228e+18 to 2.839e+18 FLOPs, 0.17x to 0.22x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt5med-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/FCCkMNVHcjLLUDeNFqTGRL.eval); primary `openai/gpt-5-2025-08-07`; reasoning_effort=medium; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 16 resolved (38.0952%).
Mean per-instance native counters: input 1,454,066, cache write 0, cache read 1,130,231, output 38,877, reasoning 32,154.
Counted workload 15,233,924 + missing-work allowance 0 = 15233924.000000 tokens / 42 completed evaluations = **362712.476190 tokens** x 200,000,000,000 FLOPs/token = **7.254250e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 225,420, standard error of the mean 34,783 (9.6% of the mean). Mean AI working time 1235.4 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 2882 model calls, mean prefix 16,474 to 21,194 positions, 15,233,924 appended positions. At L=64, d_model=8192 that is 5.263e+17 to 6.771e+17 FLOPs, 0.17x to 0.22x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt5med-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/FCCkMNVHcjLLUDeNFqTGRL.eval); primary `openai/gpt-5-2025-08-07`; reasoning_effort=medium; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 0 resolved (0.0000%).
Mean per-instance native counters: input 953,206, cache write 0, cache read 618,667, output 23,110, reasoning 17,984.
Counted workload 1,072,950 + missing-work allowance 0 = 1072950.000000 tokens / 3 completed evaluations = **357650.000000 tokens** x 200,000,000,000 FLOPs/token = **7.153000e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 253,309, standard error of the mean 146,248 (40.9% of the mean). Mean AI working time 910.6 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 138 model calls, mean prefix 13,449 to 20,722 positions, 1,072,950 appended positions. At L=64, d_model=8192 that is 3.026e+16 to 4.663e+16 FLOPs, 0.14x to 0.22x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt5mini-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/7nvdQy3AwKtoay2FBvfST5.eval); primary `openai/gpt-5-mini-2025-08-07`; reasoning_effort=medium; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 144 resolved (77.8378%).
Mean per-instance native counters: input 460,846, cache write 0, cache read 228,438, output 6,927, reasoning 4,908.
Counted workload 44,276,996 + missing-work allowance 0 = 44276996.000000 tokens / 185 completed evaluations = **239335.113514 tokens** x 40,000,000,000 FLOPs/token = **9.573405e+15 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 264,998, standard error of the mean 19,483 (8.1% of the mean). Mean AI working time 525.7 s. At the 2,000,000-token harness cap: 1 of 185 instances (0.5%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 6704 model calls, mean prefix 6,304 to 12,718 positions, 44,276,996 appended positions. At L=64, d_model=8192 that is 5.854e+17 to 1.181e+18 FLOPs, 0.33x to 0.67x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt5mini-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/7nvdQy3AwKtoay2FBvfST5.eval); primary `openai/gpt-5-mini-2025-08-07`; reasoning_effort=medium; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 162 resolved (63.7795%).
Mean per-instance native counters: input 640,857, cache write 0, cache read 319,880, output 9,850, reasoning 7,375.
Counted workload 84,030,208 + missing-work allowance 0 = 84030208.000000 tokens / 254 completed evaluations = **330827.590551 tokens** x 40,000,000,000 FLOPs/token = **1.323310e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 287,807, standard error of the mean 18,059 (5.5% of the mean). Mean AI working time 658.5 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 11152 model calls, mean prefix 7,286 to 14,597 positions, 84,030,208 appended positions. At L=64, d_model=8192 that is 1.284e+18 to 2.572e+18 FLOPs, 0.38x to 0.77x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt5mini-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/7nvdQy3AwKtoay2FBvfST5.eval); primary `openai/gpt-5-mini-2025-08-07`; reasoning_effort=medium; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 7 resolved (16.6667%).
Mean per-instance native counters: input 965,609, cache write 0, cache read 545,271, output 12,159, reasoning 8,797.
Counted workload 18,164,879 + missing-work allowance 0 = 18164879.000000 tokens / 42 completed evaluations = **432497.119048 tokens** x 40,000,000,000 FLOPs/token = **1.729988e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 358,485, standard error of the mean 55,315 (12.8% of the mean). Mean AI working time 717.3 s. At the 2,000,000-token harness cap: 1 of 42 instances (2.4%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 2319 model calls, mean prefix 9,876 to 17,488 positions, 18,164,879 appended positions. At L=64, d_model=8192 that is 3.762e+17 to 6.662e+17 FLOPs, 0.52x to 0.92x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-gpt5mini-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/7nvdQy3AwKtoay2FBvfST5.eval); primary `openai/gpt-5-mini-2025-08-07`; reasoning_effort=medium; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 0 resolved (0.0000%).
Mean per-instance native counters: input 705,730, cache write 0, cache read 252,544, output 12,776, reasoning 10,112.
Counted workload 1,397,887 + missing-work allowance 0 = 1397887.000000 tokens / 3 completed evaluations = **465962.333333 tokens** x 40,000,000,000 FLOPs/token = **1.863849e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 363,292, standard error of the mean 209,747 (45.0% of the mean). Mean AI working time 963.4 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 122 model calls, mean prefix 6,236 to 17,425 positions, 1,397,887 appended positions. At L=64, d_model=8192 that is 1.828e+16 to 5.108e+16 FLOPs, 0.33x to 0.91x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-kimik25-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/5wVjUb3yn6bdjPSfPEMuiZ.eval); primary `moonshot/kimi-k2.5`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 161 resolved (87.0270%).
Mean per-instance native counters: input 593,262, cache write 0, cache read 565,053, output 6,881, reasoning 0.
Counted workload 6,491,599 + missing-work allowance 0 = 6491599.000000 tokens / 185 completed evaluations = **35089.724324 tokens** x 64,000,000,000 FLOPs/token = **2.245742e+15 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 17,105, standard error of the mean 1,258 (3.6% of the mean). Mean AI working time 182.1 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 9529 model calls, mean prefix 10,970 to 11,518 positions, 6,491,599 appended positions. At L=64, d_model=8192 that is 1.493e+17 to 1.568e+17 FLOPs, 0.36x to 0.38x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-kimik25-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/5wVjUb3yn6bdjPSfPEMuiZ.eval); primary `moonshot/kimi-k2.5`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 181 resolved (71.2598%).
Mean per-instance native counters: input 1,278,070, cache write 0, cache read 1,236,039, output 10,883, reasoning 0.
Counted workload 13,440,335 + missing-work allowance 0 = 13440335.000000 tokens / 254 completed evaluations = **52914.704724 tokens** x 64,000,000,000 FLOPs/token = **3.386541e+15 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 30,177, standard error of the mean 1,893 (3.6% of the mean). Mean AI working time 283.2 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 19140 model calls, mean prefix 16,403 to 16,961 positions, 13,440,335 appended positions. At L=64, d_model=8192 that is 4.623e+17 to 4.781e+17 FLOPs, 0.54x to 0.56x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-kimik25-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/5wVjUb3yn6bdjPSfPEMuiZ.eval); primary `moonshot/kimi-k2.5`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 14 resolved (33.3333%).
Mean per-instance native counters: input 2,241,292, cache write 0, cache read 2,181,790, output 15,632, reasoning 0.
Counted workload 3,155,623 + missing-work allowance 0 = 3155623.000000 tokens / 42 completed evaluations = **75133.880952 tokens** x 64,000,000,000 FLOPs/token = **4.808568e+15 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 28,582, standard error of the mean 4,410 (5.9% of the mean). Mean AI working time 413.0 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 4382 model calls, mean prefix 20,914 to 21,484 positions, 3,155,623 appended positions. At L=64, d_model=8192 that is 1.384e+17 to 1.422e+17 FLOPs, 0.69x to 0.70x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-kimik25-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/5wVjUb3yn6bdjPSfPEMuiZ.eval); primary `moonshot/kimi-k2.5`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 1,559,370, cache write 0, cache read 1,511,680, output 11,150, reasoning 0.
Counted workload 176,520 + missing-work allowance 0 = 176520.000000 tokens / 3 completed evaluations = **58840.000000 tokens** x 64,000,000,000 FLOPs/token = **3.765760e+15 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 36,984, standard error of the mean 21,353 (36.3% of the mean). Mean AI working time 407.9 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 268 model calls, mean prefix 16,890 to 17,423 positions, 176,520 appended positions. At L=64, d_model=8192 that is 6.253e+15 to 6.450e+15 FLOPs, 0.55x to 0.57x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-kimik26-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/bUPtAK7spEwvmiC8pi6afc.eval); primary `epoch/kimi-k2.6`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 159 resolved (85.9459%).
Mean per-instance native counters: input 29,304, cache write 0, cache read 641,646, output 8,613, reasoning 0.
Counted workload 7,014,581 + missing-work allowance 0 = 7014581.000000 tokens / 185 completed evaluations = **37916.654054 tokens** x 64,000,000,000 FLOPs/token = **2.426666e+15 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 32,470, standard error of the mean 2,387 (6.3% of the mean). Mean AI working time 339.4 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 10078 model calls, mean prefix 11,779 to 12,317 positions, 7,014,581 appended positions. At L=64, d_model=8192 that is 1.733e+17 to 1.812e+17 FLOPs, 0.39x to 0.40x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-kimik26-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/bUPtAK7spEwvmiC8pi6afc.eval); primary `epoch/kimi-k2.6`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 193 resolved (75.9843%).
Mean per-instance native counters: input 47,988, cache write 0, cache read 1,543,195, output 17,061, reasoning 0.
Counted workload 16,522,470 + missing-work allowance 703.229730 = 16523173.229730 tokens / 254 completed evaluations = **65051.863109 tokens** x 64,000,000,000 FLOPs/token = **4.163319e+15 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 49,708, standard error of the mean 3,119 (4.8% of the mean). Mean AI working time 617.7 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). Recorded counters alone give 65049.094488 tokens per completed evaluation.
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 21297 model calls, mean prefix 18,405 to 18,977 positions, 16,522,470 appended positions. At L=64, d_model=8192 that is 6.377e+17 to 6.576e+17 FLOPs, 0.60x to 0.62x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-kimik26-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/bUPtAK7spEwvmiC8pi6afc.eval); primary `epoch/kimi-k2.6`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 19 resolved (45.2381%).
Mean per-instance native counters: input 81,366, cache write 0, cache read 3,430,249, output 29,010, reasoning 0.
Counted workload 4,635,782 + missing-work allowance 0 = 4635782.000000 tokens / 42 completed evaluations = **110375.761905 tokens** x 64,000,000,000 FLOPs/token = **7.064049e+15 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 74,826, standard error of the mean 11,546 (10.5% of the mean). Mean AI working time 999.6 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 5436 model calls, mean prefix 26,501 to 27,129 positions, 4,635,782 appended positions. At L=64, d_model=8192 that is 2.576e+17 to 2.637e+17 FLOPs, 0.87x to 0.89x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-kimik26-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/bUPtAK7spEwvmiC8pi6afc.eval); primary `epoch/kimi-k2.6`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 0 resolved (0.0000%).
Mean per-instance native counters: input 198,977, cache write 0, cache read 3,567,992, output 25,517, reasoning 0.
Counted workload 673,483 + missing-work allowance 0 = 673483.000000 tokens / 3 completed evaluations = **224494.333333 tokens** x 64,000,000,000 FLOPs/token = **1.436764e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 314,082, standard error of the mean 181,335 (80.8% of the mean). Mean AI working time 1400.7 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 368 model calls, mean prefix 29,126 to 30,751 positions, 673,483 appended positions. At L=64, d_model=8192 that is 4.114e+16 to 4.343e+16 FLOPs, 0.95x to 1.01x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-o3med-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/AKt7PcE8LQtoMWVuxwMidk.eval); primary `openai/o3-2025-04-16`; reasoning_effort=medium; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 184 completed evaluations, 139 resolved (75.5435%).
Mean per-instance native counters: input 3,813,694, cache write 0, cache read 3,608,689, output 22,550, reasoning 14,931.
Counted workload 42,097,653 + missing-work allowance 0 = 42097653.000000 tokens / 184 completed evaluations = **228791.592391 tokens** x 100,000,000,000 FLOPs/token = **2.287916e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 243,325, standard error of the mean 17,890 (7.9% of the mean). Mean AI working time 1333.2 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 24874 model calls, mean prefix 26,840 to 28,365 positions, 42,097,653 appended positions. At L=64, d_model=8192 that is 2.370e+18 to 2.504e+18 FLOPs, 0.56x to 0.59x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-o3med-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/AKt7PcE8LQtoMWVuxwMidk.eval); primary `openai/o3-2025-04-16`; reasoning_effort=medium; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 153 resolved (60.2362%).
Mean per-instance native counters: input 4,400,759, cache write 0, cache read 4,163,848, output 25,112, reasoning 15,813.
Counted workload 66,553,717 + missing-work allowance 0 = 66553717.000000 tokens / 254 completed evaluations = **262022.507874 tokens** x 100,000,000,000 FLOPs/token = **2.620225e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 269,473, standard error of the mean 16,908 (6.5% of the mean). Mean AI working time 1510.9 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 38928 model calls, mean prefix 27,168 to 28,714 positions, 66,553,717 appended positions. At L=64, d_model=8192 that is 3.792e+18 to 4.008e+18 FLOPs, 0.57x to 0.60x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-o3med-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/AKt7PcE8LQtoMWVuxwMidk.eval); primary `openai/o3-2025-04-16`; reasoning_effort=medium; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 9 resolved (21.4286%).
Mean per-instance native counters: input 7,556,320, cache write 0, cache read 7,201,435, output 37,339, reasoning 25,984.
Counted workload 16,473,404 + missing-work allowance 0 = 16473404.000000 tokens / 42 completed evaluations = **392223.904762 tokens** x 100,000,000,000 FLOPs/token = **3.922239e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 310,106, standard error of the mean 47,850 (12.2% of the mean). Mean AI working time 2034.3 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 8888 model calls, mean prefix 34,030 to 35,707 positions, 16,473,404 appended positions. At L=64, d_model=8192 that is 1.176e+18 to 1.234e+18 FLOPs, 0.71x to 0.75x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-o3med-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/AKt7PcE8LQtoMWVuxwMidk.eval); primary `openai/o3-2025-04-16`; reasoning_effort=medium; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 0 resolved (0.0000%).
Mean per-instance native counters: input 1,442,828, cache write 0, cache read 1,257,003, output 26,659, reasoning 18,944.
Counted workload 637,454 + missing-work allowance 0 = 637454.000000 tokens / 3 completed evaluations = **212484.666667 tokens** x 100,000,000,000 FLOPs/token = **2.124847e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 111,109, standard error of the mean 64,149 (30.2% of the mean). Mean AI working time 1892.7 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 360 model calls, mean prefix 10,490 to 12,040 positions, 637,454 appended positions. At L=64, d_model=8192 that is 1.402e+16 to 1.610e+16 FLOPs, 0.22x to 0.25x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus4-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/RbcvuVChvxK6SMQbPK8iRn.eval); primary `anthropic/claude-opus-4-20250514`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 154 resolved (83.2432%).
Mean per-instance native counters: input 38, cache write 27,841, cache read 698,874, output 10,018, reasoning 0.
Counted workload 7,010,828 + missing-work allowance 0 = 7010828.000000 tokens / 185 completed evaluations = **37896.367568 tokens** x 360,000,000,000 FLOPs/token = **1.364269e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 16,524, standard error of the mean 1,215 (3.2% of the mean). Mean AI working time 310.7 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 10496 model calls, mean prefix 12,318 to 12,809 positions, 7,010,828 appended positions. At L=64, d_model=8192 that is 1.811e+17 to 1.883e+17 FLOPs, 0.07x to 0.07x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus4-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/RbcvuVChvxK6SMQbPK8iRn.eval); primary `anthropic/claude-opus-4-20250514`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 172 resolved (67.7165%).
Mean per-instance native counters: input 47, cache write 34,642, cache read 1,097,713, output 12,655, reasoning 0.
Counted workload 12,025,504 + missing-work allowance 0 = 12025504.000000 tokens / 254 completed evaluations = **47344.503937 tokens** x 360,000,000,000 FLOPs/token = **1.704402e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 24,997, standard error of the mean 1,568 (3.3% of the mean). Mean AI working time 403.2 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 18055 model calls, mean prefix 15,443 to 15,931 positions, 12,025,504 appended positions. At L=64, d_model=8192 that is 3.895e+17 to 4.018e+17 FLOPs, 0.09x to 0.09x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus4-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/RbcvuVChvxK6SMQbPK8iRn.eval); primary `anthropic/claude-opus-4-20250514`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 15 resolved (35.7143%).
Mean per-instance native counters: input 61, cache write 45,633, cache read 1,837,848, output 17,340, reasoning 0.
Counted workload 2,647,411 + missing-work allowance 0 = 2647411.000000 tokens / 42 completed evaluations = **63033.595238 tokens** x 360,000,000,000 FLOPs/token = **2.269209e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 29,095, standard error of the mean 4,489 (7.1% of the mean). Mean AI working time 512.4 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 3872 model calls, mean prefix 19,938 to 20,434 positions, 2,647,411 appended positions. At L=64, d_model=8192 that is 1.107e+17 to 1.134e+17 FLOPs, 0.12x to 0.12x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus4-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/RbcvuVChvxK6SMQbPK8iRn.eval); primary `anthropic/claude-opus-4-20250514`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 52, cache write 49,516, cache read 1,177,944, output 12,111, reasoning 0.
Counted workload 185,036 + missing-work allowance 0 = 185036.000000 tokens / 3 completed evaluations = **61678.666667 tokens** x 360,000,000,000 FLOPs/token = **2.220432e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 40,667, standard error of the mean 23,479 (38.1% of the mean). Mean AI working time 742.7 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 236 model calls, mean prefix 15,006 to 15,637 positions, 185,036 appended positions. At L=64, d_model=8192 that is 5.823e+15 to 6.068e+15 FLOPs, 0.09x to 0.09x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus41-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/cA6Mq67yaynLhY8F5kes3c.eval); primary `anthropic/claude-opus-4-1-20250805`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 152 resolved (82.1622%).
Mean per-instance native counters: input 44, cache write 31,819, cache read 879,060, output 13,293, reasoning 0.
Counted workload 8,354,108 + missing-work allowance 0 = 8354108.000000 tokens / 185 completed evaluations = **45157.340541 tokens** x 360,000,000,000 FLOPs/token = **1.625664e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 16,075, standard error of the mean 1,182 (2.6% of the mean). Mean AI working time 393.6 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 12434 model calls, mean prefix 13,079 to 13,553 positions, 8,354,108 appended positions. At L=64, d_model=8192 that is 2.291e+17 to 2.374e+17 FLOPs, 0.08x to 0.08x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus41-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/cA6Mq67yaynLhY8F5kes3c.eval); primary `anthropic/claude-opus-4-1-20250805`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 182 resolved (71.6535%).
Mean per-instance native counters: input 54, cache write 40,225, cache read 1,347,392, output 16,741, reasoning 0.
Counted workload 14,483,179 + missing-work allowance 0 = 14483179.000000 tokens / 254 completed evaluations = **57020.389764 tokens** x 360,000,000,000 FLOPs/token = **2.052734e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 24,517, standard error of the mean 1,538 (2.7% of the mean). Mean AI working time 500.9 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 20845 model calls, mean prefix 16,418 to 16,909 positions, 14,483,179 appended positions. At L=64, d_model=8192 that is 4.987e+17 to 5.136e+17 FLOPs, 0.10x to 0.10x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus41-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/cA6Mq67yaynLhY8F5kes3c.eval); primary `anthropic/claude-opus-4-1-20250805`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 20 resolved (47.6190%).
Mean per-instance native counters: input 63, cache write 48,266, cache read 1,840,839, output 20,312, reasoning 0.
Counted workload 2,882,937 + missing-work allowance 0 = 2882937.000000 tokens / 42 completed evaluations = **68641.357143 tokens** x 360,000,000,000 FLOPs/token = **2.471089e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 27,002, standard error of the mean 4,166 (6.1% of the mean). Mean AI working time 568.8 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 4020 model calls, mean prefix 19,233 to 19,738 positions, 2,882,937 appended positions. At L=64, d_model=8192 that is 1.163e+17 to 1.193e+17 FLOPs, 0.11x to 0.11x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus41-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/cA6Mq67yaynLhY8F5kes3c.eval); primary `anthropic/claude-opus-4-1-20250805`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 67, cache write 45,529, cache read 1,854,108, output 19,156, reasoning 0.
Counted workload 194,254 + missing-work allowance 0 = 194254.000000 tokens / 3 completed evaluations = **64751.333333 tokens** x 360,000,000,000 FLOPs/token = **2.331048e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 36,042, standard error of the mean 20,809 (32.1% of the mean). Mean AI working time 639.8 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 302 model calls, mean prefix 18,449 to 18,903 positions, 194,254 appended positions. At L=64, d_model=8192 that is 7.516e+15 to 7.701e+15 FLOPs, 0.11x to 0.11x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus45-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/mKQKxkpGDrFHBPBYR3mBrB.eval); primary `anthropic/claude-opus-4-5-20251101`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 164 resolved (88.6486%).
Mean per-instance native counters: input 7,158, cache write 14,651, cache read 180,012, output 2,872, reasoning 0.
Counted workload 4,566,065 + missing-work allowance 0 = 4566065.000000 tokens / 185 completed evaluations = **24681.432432 tokens** x 200,000,000,000 FLOPs/token = **4.936286e+15 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 10,580, standard error of the mean 778 (3.2% of the mean). Mean AI working time 99.5 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 4684 model calls, mean prefix 7,111 to 7,972 positions, 4,566,065 appended positions. At L=64, d_model=8192 that is 6.809e+16 to 7.634e+16 FLOPs, 0.07x to 0.08x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus45-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/mKQKxkpGDrFHBPBYR3mBrB.eval); primary `anthropic/claude-opus-4-5-20251101`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 187 resolved (73.6220%).
Mean per-instance native counters: input 6,925, cache write 22,223, cache read 448,416, output 5,360, reasoning 0.
Counted workload 8,764,837 + missing-work allowance 0 = 8764837.000000 tokens / 254 completed evaluations = **34507.232283 tokens** x 200,000,000,000 FLOPs/token = **6.901446e+15 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 18,263, standard error of the mean 1,146 (3.3% of the mean). Mean AI working time 168.3 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 10114 model calls, mean prefix 11,261 to 11,993 positions, 8,764,837 appended positions. At L=64, d_model=8192 that is 2.070e+17 to 2.205e+17 FLOPs, 0.12x to 0.13x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus45-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/mKQKxkpGDrFHBPBYR3mBrB.eval); primary `anthropic/claude-opus-4-5-20251101`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 19 resolved (45.2381%).
Mean per-instance native counters: input 6,061, cache write 39,341, cache read 1,301,153, output 11,038, reasoning 0.
Counted workload 2,370,504 + missing-work allowance 0 = 2370504.000000 tokens / 42 completed evaluations = **56440.571429 tokens** x 200,000,000,000 FLOPs/token = **1.128811e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 34,899, standard error of the mean 5,385 (9.5% of the mean). Mean AI working time 287.8 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 2788 model calls, mean prefix 19,598 to 20,282 positions, 2,370,504 appended positions. At L=64, d_model=8192 that is 9.743e+16 to 1.008e+17 FLOPs, 0.21x to 0.21x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus45-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/mKQKxkpGDrFHBPBYR3mBrB.eval); primary `anthropic/claude-opus-4-5-20251101`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 6,421, cache write 29,209, cache read 893,337, output 8,112, reasoning 0.
Counted workload 131,226 + missing-work allowance 0 = 131226.000000 tokens / 3 completed evaluations = **43742.000000 tokens** x 200,000,000,000 FLOPs/token = **8.748400e+15 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 33,293, standard error of the mean 19,222 (43.9% of the mean). Mean AI working time 306.9 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 160 model calls, mean prefix 16,698 to 17,364 positions, 131,226 appended positions. At L=64, d_model=8192 that is 4.595e+15 to 4.779e+15 FLOPs, 0.18x to 0.18x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus46-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/aQiAg6mt8HPHXjKcJvax2d.eval); primary `anthropic/claude-opus-4-6`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 161 resolved (87.0270%).
Mean per-instance native counters: input 10,952, cache write 8,085, cache read 83,624, output 1,986, reasoning 0.
Counted workload 3,889,334 + missing-work allowance 0 = 3889334.000000 tokens / 185 completed evaluations = **21023.427027 tokens** x 200,000,000,000 FLOPs/token = **4.204685e+15 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 9,113, standard error of the mean 670 (3.2% of the mean). Mean AI working time 80.4 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 3623 model calls, mean prefix 4,270 to 5,242 positions, 3,889,334 appended positions. At L=64, d_model=8192 that is 3.483e+16 to 4.276e+16 FLOPs, 0.04x to 0.05x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus46-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/aQiAg6mt8HPHXjKcJvax2d.eval); primary `anthropic/claude-opus-4-6`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 185 resolved (72.8346%).
Mean per-instance native counters: input 9,821, cache write 13,820, cache read 264,974, output 4,133, reasoning 0.
Counted workload 7,054,544 + missing-work allowance 0 = 7054544.000000 tokens / 254 completed evaluations = **27773.795276 tokens** x 200,000,000,000 FLOPs/token = **5.554759e+15 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 19,185, standard error of the mean 1,204 (4.3% of the mean). Mean AI working time 148.0 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 8020 model calls, mean prefix 8,391 to 9,140 positions, 7,054,544 appended positions. At L=64, d_model=8192 that is 1.241e+17 to 1.352e+17 FLOPs, 0.09x to 0.10x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus46-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/aQiAg6mt8HPHXjKcJvax2d.eval); primary `anthropic/claude-opus-4-6`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 19 resolved (45.2381%).
Mean per-instance native counters: input 7,304, cache write 25,519, cache read 666,846, output 7,649, reasoning 0.
Counted workload 1,699,836 + missing-work allowance 0 = 1699836.000000 tokens / 42 completed evaluations = **40472.285714 tokens** x 200,000,000,000 FLOPs/token = **8.094457e+15 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 24,136, standard error of the mean 3,724 (9.2% of the mean). Mean AI working time 237.0 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 2192 model calls, mean prefix 12,777 to 13,406 positions, 1,699,836 appended positions. At L=64, d_model=8192 that is 4.555e+16 to 4.779e+16 FLOPs, 0.13x to 0.14x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus46-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/aQiAg6mt8HPHXjKcJvax2d.eval); primary `anthropic/claude-opus-4-6`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 10,104, cache write 23,868, cache read 366,522, output 5,844, reasoning 0.
Counted workload 119,449 + missing-work allowance 0 = 119449.000000 tokens / 3 completed evaluations = **39816.333333 tokens** x 200,000,000,000 FLOPs/token = **7.963267e+15 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 15,818, standard error of the mean 9,133 (22.9% of the mean). Mean AI working time 322.9 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 120 model calls, mean prefix 9,201 to 10,054 positions, 119,449 appended positions. At L=64, d_model=8192 that is 2.305e+15 to 2.519e+15 FLOPs, 0.10x to 0.11x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus46cc-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/2hH2GAPUFaJR7pfVKhhicg.eval); primary `anthropic/claude-opus-4-6`; reasoning_effort=provider default; Inspect task `swe_bench_claude_code` (the Claude Code CLI agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 164 resolved (88.6486%).
Mean per-instance native counters: input 27,769, cache write 22,995, cache read 727,437, output 6,932, reasoning 0.
Counted workload 10,673,737 + missing-work allowance 0 = 10673737.000000 tokens / 185 completed evaluations = **57695.875676 tokens** x 200,000,000,000 FLOPs/token = **1.153918e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 34,270, standard error of the mean 2,520 (4.4% of the mean). Mean AI working time 306.2 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 4434 model calls, mean prefix 30,354 to 32,473 positions, 10,673,737 appended positions. At L=64, d_model=8192 that is 6.795e+17 to 7.269e+17 FLOPs, 0.32x to 0.34x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus46cc-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/2hH2GAPUFaJR7pfVKhhicg.eval); primary `anthropic/claude-opus-4-6`; reasoning_effort=provider default; Inspect task `swe_bench_claude_code` (the Claude Code CLI agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 194 resolved (76.3780%).
Mean per-instance native counters: input 40,130, cache write 39,692, cache read 1,398,750, output 12,598, reasoning 0.
Counted workload 23,474,769 + missing-work allowance 0 = 23474769.000000 tokens / 254 completed evaluations = **92420.350394 tokens** x 200,000,000,000 FLOPs/token = **1.848407e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 64,697, standard error of the mean 4,059 (4.4% of the mean). Mean AI working time 483.9 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 8832 model calls, mean prefix 40,224 to 42,520 positions, 23,474,769 appended positions. At L=64, d_model=8192 that is 1.980e+18 to 2.093e+18 FLOPs, 0.42x to 0.45x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus46cc-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/2hH2GAPUFaJR7pfVKhhicg.eval); primary `anthropic/claude-opus-4-6`; reasoning_effort=provider default; Inspect task `swe_bench_claude_code` (the Claude Code CLI agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 22 resolved (52.3810%).
Mean per-instance native counters: input 57,230, cache write 70,278, cache read 3,136,483, output 23,332, reasoning 0.
Counted workload 6,335,287 + missing-work allowance 0 = 6335287.000000 tokens / 42 completed evaluations = **150840.166667 tokens** x 200,000,000,000 FLOPs/token = **3.016803e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 89,938, standard error of the mean 13,878 (9.2% of the mean). Mean AI working time 755.8 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 2506 model calls, mean prefix 52,577 to 54,715 positions, 6,335,287 appended positions. At L=64, d_model=8192 that is 6.985e+17 to 7.269e+17 FLOPs, 0.55x to 0.57x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus46cc-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/2hH2GAPUFaJR7pfVKhhicg.eval); primary `anthropic/claude-opus-4-6`; reasoning_effort=provider default; Inspect task `swe_bench_claude_code` (the Claude Code CLI agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 39,006, cache write 51,800, cache read 1,823,455, output 13,915, reasoning 0.
Counted workload 314,163 + missing-work allowance 0 = 314163.000000 tokens / 3 completed evaluations = **104721.000000 tokens** x 200,000,000,000 FLOPs/token = **2.094420e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 60,988, standard error of the mean 35,211 (33.6% of the mean). Mean AI working time 538.6 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 139 model calls, mean prefix 39,355 to 41,315 positions, 314,163 appended positions. At L=64, d_model=8192 that is 2.593e+16 to 2.722e+16 FLOPs, 0.41x to 0.43x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus47max-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/nCmGWWMBip2s9AVEZNYXDX.eval); primary `anthropic/claude-opus-4-7`; reasoning_effort=max; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 168 resolved (90.8108%).
Mean per-instance native counters: input 209, cache write 34,324, cache read 1,091,935, output 13,270, reasoning 1,754.
Counted workload 8,843,546 + missing-work allowance 0 = 8843546.000000 tokens / 185 completed evaluations = **47802.951351 tokens** x 200,000,000,000 FLOPs/token = **9.560590e+15 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 46,162, standard error of the mean 3,394 (7.1% of the mean). Mean AI working time 285.2 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 9784 model calls, mean prefix 20,647 to 21,300 positions, 8,843,546 appended positions. At L=64, d_model=8192 that is 3.829e+17 to 3.950e+17 FLOPs, 0.22x to 0.22x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus47max-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/nCmGWWMBip2s9AVEZNYXDX.eval); primary `anthropic/claude-opus-4-7`; reasoning_effort=max; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 209 resolved (82.2835%).
Mean per-instance native counters: input 345, cache write 60,725, cache read 2,925,885, output 25,959, reasoning 3,103.
Counted workload 22,105,342 + missing-work allowance 662.598361 = 22106004.598361 tokens / 254 completed evaluations = **87031.514167 tokens** x 200,000,000,000 FLOPs/token = **1.740630e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 76,525, standard error of the mean 4,802 (5.5% of the mean). Mean AI working time 541.8 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). Recorded counters alone give 87028.905512 tokens per completed evaluation.
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 22062 model calls, mean prefix 33,685 to 34,388 positions, 22,105,342 appended positions. At L=64, d_model=8192 that is 1.562e+18 to 1.594e+18 FLOPs, 0.35x to 0.36x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus47max-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/nCmGWWMBip2s9AVEZNYXDX.eval); primary `anthropic/claude-opus-4-7`; reasoning_effort=max; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 25 resolved (59.5238%).
Mean per-instance native counters: input 602, cache write 112,216, cache read 7,150,437, output 43,161, reasoning 4,013.
Counted workload 6,551,120 + missing-work allowance 0 = 6551120.000000 tokens / 42 completed evaluations = **155979.047619 tokens** x 200,000,000,000 FLOPs/token = **3.119581e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 100,027, standard error of the mean 15,434 (9.9% of the mean). Mean AI working time 890.8 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 6352 model calls, mean prefix 47,283 to 48,029 positions, 6,551,120 appended positions. At L=64, d_model=8192 that is 6.496e+17 to 6.599e+17 FLOPs, 0.50x to 0.50x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-opus47max-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/nCmGWWMBip2s9AVEZNYXDX.eval); primary `anthropic/claude-opus-4-7`; reasoning_effort=max; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 2 resolved (66.6667%).
Mean per-instance native counters: input 411, cache write 70,451, cache read 3,183,768, output 24,452, reasoning 581.
Counted workload 285,940 + missing-work allowance 0 = 285940.000000 tokens / 3 completed evaluations = **95313.333333 tokens** x 200,000,000,000 FLOPs/token = **1.906267e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 48,145, standard error of the mean 27,797 (29.2% of the mean). Mean AI working time 621.0 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 310 model calls, mean prefix 30,761 to 31,446 positions, 285,940 appended positions. At L=64, d_model=8192 that is 1.845e+16 to 1.886e+16 FLOPs, 0.32x to 0.33x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-qwen37max-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/83hhDhcT9UUrZ2NiUbWSUU.eval); primary `epoch/qwen3.7-max`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 164 resolved (88.6486%).
Mean per-instance native counters: input 80,687, cache write 10,143, cache read 195,061, output 13,056, reasoning 9,558.
Counted workload 19,219,045 + missing-work allowance 0 = 19219045.000000 tokens / 185 completed evaluations = **103886.729730 tokens** x 200,000,000,000 FLOPs/token = **2.077735e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 135,782, standard error of the mean 9,983 (9.6% of the mean). Mean AI working time 330.0 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 7052 model calls, mean prefix 5,118 to 7,501 positions, 19,219,045 appended positions. At L=64, d_model=8192 that is 2.063e+17 to 3.023e+17 FLOPs, 0.05x to 0.08x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-qwen37max-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/83hhDhcT9UUrZ2NiUbWSUU.eval); primary `epoch/qwen3.7-max`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 192 resolved (75.5906%).
Mean per-instance native counters: input 194,739, cache write 14,757, cache read 419,378, output 28,212, reasoning 22,360.
Counted workload 60,377,896 + missing-work allowance 0 = 60377896.000000 tokens / 254 completed evaluations = **237708.251969 tokens** x 200,000,000,000 FLOPs/token = **4.754165e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 299,681, standard error of the mean 18,804 (7.9% of the mean). Mean AI working time 646.6 s. At the 2,000,000-token harness cap: 1 of 254 instances (0.4%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 14699 model calls, mean prefix 7,247 to 10,867 positions, 60,377,896 appended positions. At L=64, d_model=8192 that is 9.176e+17 to 1.376e+18 FLOPs, 0.08x to 0.11x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-qwen37max-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/83hhDhcT9UUrZ2NiUbWSUU.eval); primary `epoch/qwen3.7-max`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 17 resolved (40.4762%).
Mean per-instance native counters: input 520,030, cache write 28,011, cache read 1,044,741, output 58,236, reasoning 47,684.
Counted workload 25,463,658 + missing-work allowance 0 = 25463658.000000 tokens / 42 completed evaluations = **606277.571429 tokens** x 200,000,000,000 FLOPs/token = **1.212555e+17 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 521,513, standard error of the mean 80,471 (13.3% of the mean). Mean AI working time 1294.5 s. At the 2,000,000-token harness cap: 2 of 42 instances (4.8%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 3951 model calls, mean prefix 11,106 to 16,932 positions, 25,463,658 appended positions. At L=64, d_model=8192 that is 5.931e+17 to 9.042e+17 FLOPs, 0.12x to 0.18x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-qwen37max-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/83hhDhcT9UUrZ2NiUbWSUU.eval); primary `epoch/qwen3.7-max`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 201,734, cache write 13,881, cache read 422,518, output 16,538, reasoning 10,334.
Counted workload 696,459 + missing-work allowance 0 = 696459.000000 tokens / 3 completed evaluations = **232153.000000 tokens** x 200,000,000,000 FLOPs/token = **4.643060e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 189,842, standard error of the mean 109,605 (47.2% of the mean). Mean AI working time 505.9 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 200 model calls, mean prefix 6,354 to 9,596 positions, 696,459 appended positions. At L=64, d_model=8192 that is 9.280e+15 to 1.402e+16 FLOPs, 0.07x to 0.10x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-sonnet37-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/cnM8U6moeqrp74wnXRj2Jj.eval); primary `anthropic/claude-3-7-sonnet-20250219`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 146 resolved (78.9189%).
Mean per-instance native counters: input 52, cache write 22,265, cache read 467,146, output 6,635, reasoning 0.
Counted workload 5,356,157 + missing-work allowance 0 = 5356157.000000 tokens / 185 completed evaluations = **28952.200000 tokens** x 200,000,000,000 FLOPs/token = **5.790440e+15 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 19,359, standard error of the mean 1,423 (4.9% of the mean). Mean AI working time 156.0 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 7331 model calls, mean prefix 11,789 to 12,352 positions, 5,356,157 appended positions. At L=64, d_model=8192 that is 1.324e+17 to 1.387e+17 FLOPs, 0.12x to 0.13x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-sonnet37-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/cnM8U6moeqrp74wnXRj2Jj.eval); primary `anthropic/claude-3-7-sonnet-20250219`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 140 resolved (55.1181%).
Mean per-instance native counters: input 68, cache write 28,422, cache read 704,961, output 9,001, reasoning 0.
Counted workload 9,522,706 + missing-work allowance 0 = 9522706.000000 tokens / 254 completed evaluations = **37490.968504 tokens** x 200,000,000,000 FLOPs/token = **7.498194e+15 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 21,080, standard error of the mean 1,323 (3.5% of the mean). Mean AI working time 207.9 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 13006 model calls, mean prefix 13,767 to 14,323 positions, 9,522,706 appended positions. At L=64, d_model=8192 that is 2.749e+17 to 2.860e+17 FLOPs, 0.14x to 0.15x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-sonnet37-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/cnM8U6moeqrp74wnXRj2Jj.eval); primary `anthropic/claude-3-7-sonnet-20250219`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 8 resolved (19.0476%).
Mean per-instance native counters: input 87, cache write 38,207, cache read 1,102,459, output 13,083, reasoning 0.
Counted workload 2,157,848 + missing-work allowance 0 = 2157848.000000 tokens / 42 completed evaluations = **51377.333333 tokens** x 200,000,000,000 FLOPs/token = **1.027547e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 27,141, standard error of the mean 4,188 (8.2% of the mean). Mean AI working time 282.2 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 2766 model calls, mean prefix 16,743 to 17,325 positions, 2,157,848 appended positions. At L=64, d_model=8192 that is 7.577e+16 to 7.840e+16 FLOPs, 0.18x to 0.18x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-sonnet37-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/cnM8U6moeqrp74wnXRj2Jj.eval); primary `anthropic/claude-3-7-sonnet-20250219`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 91, cache write 39,084, cache read 1,032,465, output 11,262, reasoning 0.
Counted workload 151,313 + missing-work allowance 0 = 151313.000000 tokens / 3 completed evaluations = **50437.666667 tokens** x 200,000,000,000 FLOPs/token = **1.008753e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 23,604, standard error of the mean 13,628 (27.0% of the mean). Mean AI working time 396.4 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 207 model calls, mean prefix 14,963 to 15,531 positions, 151,313 appended positions. At L=64, d_model=8192 that is 4.748e+15 to 4.928e+15 FLOPs, 0.16x to 0.16x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-sonnet45-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/Lti64yMEsBWSzgEMFCSVhp.eval); primary `anthropic/claude-sonnet-4-5-20250929`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 151 resolved (81.6216%).
Mean per-instance native counters: input 66, cache write 48,342, cache read 1,875,897, output 18,511, reasoning 0.
Counted workload 12,380,094 + missing-work allowance 0 = 12380094.000000 tokens / 185 completed evaluations = **66919.427027 tokens** x 200,000,000,000 FLOPs/token = **1.338389e+16 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 15,658, standard error of the mean 1,151 (1.7% of the mean). Mean AI working time 511.7 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 18500 model calls, mean prefix 18,758 to 19,243 positions, 12,380,094 appended positions. At L=64, d_model=8192 that is 4.870e+17 to 4.996e+17 FLOPs, 0.20x to 0.20x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-sonnet45-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/Lti64yMEsBWSzgEMFCSVhp.eval); primary `anthropic/claude-sonnet-4-5-20250929`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 179 resolved (70.4724%).
Mean per-instance native counters: input 77, cache write 58,261, cache read 2,576,328, output 21,972, reasoning 0.
Counted workload 20,398,751 + missing-work allowance 0 = 20398751.000000 tokens / 254 completed evaluations = **80310.043307 tokens** x 200,000,000,000 FLOPs/token = **1.606201e+16 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 23,384, standard error of the mean 1,467 (1.8% of the mean). Mean AI working time 611.2 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 29463 model calls, mean prefix 22,210 to 22,713 positions, 20,398,751 appended positions. At L=64, d_model=8192 that is 9.501e+17 to 9.717e+17 FLOPs, 0.23x to 0.24x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-sonnet45-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/Lti64yMEsBWSzgEMFCSVhp.eval); primary `anthropic/claude-sonnet-4-5-20250929`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 15 resolved (35.7143%).
Mean per-instance native counters: input 87, cache write 69,226, cache read 3,371,910, output 25,631, reasoning 0.
Counted workload 3,987,660 + missing-work allowance 0 = 3987660.000000 tokens / 42 completed evaluations = **94944.285714 tokens** x 200,000,000,000 FLOPs/token = **1.898886e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 27,617, standard error of the mean 4,261 (4.5% of the mean). Mean AI working time 686.1 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 5475 model calls, mean prefix 25,867 to 26,398 positions, 3,987,660 appended positions. At L=64, d_model=8192 that is 2.163e+17 to 2.208e+17 FLOPs, 0.27x to 0.28x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-sonnet45-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/Lti64yMEsBWSzgEMFCSVhp.eval); primary `anthropic/claude-sonnet-4-5-20250929`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 0 resolved (0.0000%).
Mean per-instance native counters: input 78, cache write 70,547, cache read 2,616,034, output 22,825, reasoning 0.
Counted workload 280,352 + missing-work allowance 0 = 280352.000000 tokens / 3 completed evaluations = **93450.666667 tokens** x 200,000,000,000 FLOPs/token = **1.869013e+16 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 30,688, standard error of the mean 17,718 (19.0% of the mean). Mean AI working time 835.1 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 352 model calls, mean prefix 22,264 to 22,865 positions, 280,352 appended positions. At L=64, d_model=8192 that is 1.309e+16 to 1.344e+16 FLOPs, 0.23x to 0.24x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-sonnet46-lt15m

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/KEdgiMmtJKHxgGiS82agYj.eval); primary `anthropic/claude-sonnet-4-6`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `<15 min fix`: 185 instances, 185 completed evaluations, 159 resolved (85.9459%).
Mean per-instance native counters: input 50, cache write 13,860, cache read 270,431, output 4,097, reasoning 0.
Counted workload 3,331,184 + missing-work allowance 0 = 3331184.000000 tokens / 185 completed evaluations = **18006.400000 tokens** x 200,000,000,000 FLOPs/token = **3.601280e+15 FLOPs**.
Human time 450 s (bin interval midpoint). Per-instance counted-token standard deviation 22,856, standard error of the mean 1,680 (9.3% of the mean). Mean AI working time 110.6 s. At the 2,000,000-token harness cap: 0 of 185 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 4910 model calls, mean prefix 10,190 to 10,715 positions, 3,331,184 appended positions. At L=64, d_model=8192 that is 7.119e+16 to 7.485e+16 FLOPs, 0.11x to 0.11x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-sonnet46-15m1h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/KEdgiMmtJKHxgGiS82agYj.eval); primary `anthropic/claude-sonnet-4-6`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `15 min - 1 hour`: 254 instances, 254 completed evaluations, 186 resolved (73.2283%).
Mean per-instance native counters: input 83, cache write 23,521, cache read 703,623, output 8,295, reasoning 0.
Counted workload 8,102,446 + missing-work allowance 0 = 8102446.000000 tokens / 254 completed evaluations = **31899.393701 tokens** x 200,000,000,000 FLOPs/token = **6.379879e+15 FLOPs**.
Human time 2250 s (bin interval midpoint). Per-instance counted-token standard deviation 39,118, standard error of the mean 2,454 (7.7% of the mean). Mean AI working time 203.0 s. At the 2,000,000-token harness cap: 0 of 254 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 11130 model calls, mean prefix 16,057 to 16,595 positions, 8,102,446 appended positions. At L=64, d_model=8192 that is 2.728e+17 to 2.820e+17 FLOPs, 0.17x to 0.17x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-sonnet46-1h4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/KEdgiMmtJKHxgGiS82agYj.eval); primary `anthropic/claude-sonnet-4-6`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `1-4 hours`: 42 instances, 42 completed evaluations, 18 resolved (42.8571%).
Mean per-instance native counters: input 167, cache write 58,027, cache read 2,390,689, output 23,137, reasoning 0.
Counted workload 3,415,905 + missing-work allowance 0 = 3415905.000000 tokens / 42 completed evaluations = **81331.071429 tokens** x 200,000,000,000 FLOPs/token = **1.626621e+16 FLOPs**.
Human time 9000 s (bin interval midpoint). Per-instance counted-token standard deviation 95,325, standard error of the mean 14,709 (18.1% of the mean). Mean AI working time 489.6 s. At the 2,000,000-token harness cap: 0 of 42 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 3644 model calls, mean prefix 27,558 to 28,229 positions, 3,415,905 appended positions. At L=64, d_model=8192 that is 1.974e+17 to 2.022e+17 FLOPs, 0.29x to 0.30x the parameter-only value; at L=96, d_model=12288, 2.25 times those.

## agen-epoch-swebench-sonnet46-gt4h

[Original run](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/KEdgiMmtJKHxgGiS82agYj.eval); primary `anthropic/claude-sonnet-4-6`; reasoning_effort=provider default; Inspect task `swe_bench_verified` (a bash shell and editor agent), 2,000,000-token limit. Difficulty label `>4 hours`: 3 instances, 3 completed evaluations, 1 resolved (33.3333%).
Mean per-instance native counters: input 120, cache write 34,126, cache read 1,032,544, output 10,581, reasoning 0.
Counted workload 134,480 + missing-work allowance 0 = 134480.000000 tokens / 3 completed evaluations = **44826.666667 tokens** x 200,000,000,000 FLOPs/token = **8.965333e+15 FLOPs**.
Human time 21600 s (6 h for the open upper bin). Per-instance counted-token standard deviation 29,602, standard error of the mean 17,091 (38.1% of the mean). Mean AI working time 330.9 s. At the 2,000,000-token harness cap: 0 of 3 instances (0.0%). 
Cached-context attention, since folded into compute_flops (research/attention-correction.md), this note's own scenario for it against the parameter-only value: 188 model calls, mean prefix 16,521 to 17,069 positions, 134,480 appended positions. At L=64, d_model=8192 that is 4.659e+15 to 4.814e+15 FLOPs, 0.17x to 0.18x the parameter-only value; at L=96, d_model=12288, 2.25 times those.
