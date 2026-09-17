# SWE-Marathon — evidence and calculations

*Created 2026-09-14 12:03.*

## TL;DR

Two hundred and thirteen rows from SWE-Marathon v1.1 (Abundant AI; benchmark paper arXiv
2606.07682), covering twelve of the suite's twenty ultra-long software tasks against eighteen
models, at task-author expert time estimates of 4 to 380 hours. Every agent-model
configuration that resolves a task in a majority of its trials gets a row, so a task carries
the whole cross-model trend rather than a sample of it. Both halves of each row are published
per task, which is what makes the fine grain possible. The benchmark site carries an
`expert_time_estimate_hours` field for every task — 4 to 400 hours, not the 40 to 400 the
paper's Section 4.4 states — and a v1.1 leaderboard of 7,650 individual rollouts with the
token total, dollar cost, binary verifier reward and trajectory for each. So a row is one
task by one agent-model configuration with that cell's own measured tokens, not a suite
average pushed onto a task.

The counted token total is the whole prefix re-read on every API call plus the output, so it
has to be inverted into processed positions before a weights-pass coefficient is applied.
The API turn count is read off the published trajectories, which makes the inversion
`P = 2C/k` with `k` measured rather than assumed — stronger than the METR rows, which infer
their call cadence. The trajectories also carry the model's own text, so output tokens are
measured too, and that third measurement refutes the inversion outright on 21 cells, mostly
GPT-6 Astra under Codex, where measured output exceeds the processed positions the inversion
rebuilds. Those cells are withheld rather than patched.

Median compute is 2.6e+12 FLOPs per human-second, under the collection's 5.6e12, which is
the direction a set of 4-to-380-hour tasks should move. The longest rows are the two 380-hour
`excel-clone` rows and eleven at 110 to 200 hours.

## Source

Rishi Desai et al., *SWE-Marathon: Can Agents Autonomously Complete Ultra-Long-Horizon
Software Work?*, arXiv 2606.07682, submitted 2026-06-05 (v1 only; the benchmark's own v1.0
and v1.1 are suite versions, not paper versions). Benchmark site
[swe-marathon.org](https://swe-marathon.org). Retained at
`agent-work/sources/swe-marathon/` — the paper PDF and its HTML rendering, the site's
JavaScript bundle, and the extracted tables.

Twenty long-horizon software tasks in four families: library clones and reproductions (8),
product clones (5), ML engineering (5), and algorithmic and optimization (2). Each task is a
unique Docker environment with a human-written reference solution and a multi-layer verifier;
reward is binary, and on the product clones with a UI it is the minimum of a deterministic
stage and a browser-driven UX rubric. Agents run under the Harbor harness in Modal sandboxes
with wall-clock limits of 2 to 10 hours per task, set per task.

The paper reports the v1.0 sweep: 13 agent-model configurations, 5 trials per task, 1,300
rollouts, no configuration above 30% pass@1. The site has since replaced that with v1.1: 48
configurations at 8 trials per task, 7,650 rollouts. The rows are built on v1.1, because it
is the version whose per-trial records are public.

<a id="what-is-published"></a>

## What is published, and where

Nothing in the paper carries a per-task number on either side. Table 2 lists the twenty tasks
with their verification methods and no times; Section 4.4 gives the expert estimates only as
a range; the token statistics in Section 5.2 are corpus medians and four named (model,
scaffold) cells. On the paper alone this source supports suite-level rows at best.

The site carries the rest, but it renders client-side: a plain fetch of any URL returns an
empty shell, and `/tasks` and `/leaderboard` return 404 to a fetch because the routes are
handled in the browser. Every number the site displays is embedded in its single JavaScript
bundle. `research/swe-marathon/extract_leaderboard.py` reads that bundle and writes three
flat tables to `agent-work/derived/swe-marathon/`:

| Table | Rows | What it holds |
|---|---:|---|
| `task-meta.csv` | 20 | `expert_time_estimate_hours`, agent wall-clock limit, GPU allocation |
| `cells.csv` | 958 | one task x one configuration: pass rate, mean tokens, mean cost |
| `trials.csv` | 7650 | one rollout: tokens, cost, binary reward, partial score, duration, start |

The 800 GB trial logs the paper mentions sit behind an S3 bucket whose README asks for an
email to get credentials. Under the no-outreach ruling in `DECISIONS.md` none was sought, and
none is needed: the leaderboard and the trajectory JSONs are public and unauthenticated.

<a id="human-time"></a>

## Human time

Each task carries the author's own estimate of how long a domain expert would need:

| Task | Expert hours | Agent limit (h) | Task | Expert hours | Agent limit (h) |
|---|---:|---:|---|---:|---:|
| nextjs-vite-rewrite | 400 | 10 | rust-c-compiler | 30 | 10 |
| excel-clone | 380 | 6 | find-network-alignments | 20 | 8 |
| kubernetes-rust-rewrite | 200 | 10 | rust-java-lsp | 20 | 10 |
| ruby-rust-port | 110 | 10 | stripe-clone | 14 | 4 |
| biofabric-rust-rewrite | 80 | 10 | wasm-simd | 12 | 5 |
| mastodon-clone | 75 | — | zstd-decoder | 12 | 5 |
| s3-clone | 60 | — | jax-pytorch-rewrite | 8 | 5 |
| slack-clone | 60 | 4 | parameter-golf | 8 | 5 |
| trimul-cuda | 40 | 7 | vliw-kernel-optimization | 8 | 8 |
| post-train-ifeval-gpu | 4.5 | 10 | embedding-eval | 4 | 4 |

**The site's range is 4 to 400 hours; the paper says 40 to 400.** Section 4.4's lower bound
describes neither v1.1 nor, on the evidence available, v1.0: six tasks sit below 40 hours and
two below 10. The site's field is the per-task figure and is what the rows use, with the
paper's range recorded here as the discrepancy it is. A reader who trusts the paper's
sentence would place `embedding-eval` an order of magnitude high.

These are author estimates, never timings. No human attempted a SWE-Marathon task under
measurement. Section 3.3 says candidate authors supplied "the task objective, Docker
environment, visible checks, hidden verifier, reference solution, time estimates, resource
requirements, network policy, and potential reward hack risks" — so the estimate comes from
the person who wrote the reference solution, which is the best available basis and is exactly
`human_time_evidence = source_estimate` under COLUMNS.md, the same shape as the
Terminal-Bench rows. `human_time_statistic = point_estimate`, `human_time_subset` and
`human_attempts` `not_applicable`, `human_skill = expert`.

One thing the estimate does have behind it that a bare guess does not: every task ships a
human-written reference solution that passes the verifier, so the estimate describes work
somebody actually did, even though nobody timed it.

<a id="grain"></a>

## Grain: one task by one configuration

The compute rule in COLUMNS.md — a row's FLOPs must be an estimate for that row's task —
usually forces a benchmark like this to the suite level, because only a suite average is
published. Here it does not: `trials.csv` carries a token total for every one of the 7,650
rollouts, so a cell's compute is measured on the task the row describes.

The paper makes the same point from the other side. Holding the model fixed, median tokens
per trial vary by up to 12x across scaffolds: gpt-5.5 uses 0.40M under Terminus 2 against
4.8M under Codex, and claude-opus-4-7 4.4M against 21.9M under Claude Code. Section 5.2's
conclusion is that "the unit of long-horizon token-use measurement is therefore the (model,
scaffold) cell, not the model". The rows follow that: every row names its agent product, its
model and its reasoning-effort setting, and no row is a per-model average. The 12x spread is
recorded in each row's `notes`.

### Which cells become rows

A binary-reward cell either produced the deliverable or did not, and the pass rate over eight
trials is the whole of its performance evidence. Two filters, applied in
`research/swe-marathon/make_rows.py` and logged cell by cell in
`agent-work/derived/swe-marathon/dispositions.csv`:

- **Pass rate at least 0.5.** 531 of the 958 cells never resolved their task at all. A
  further 144 resolved it in a minority of trials; those are withheld under the
  substantially-below rule, because a configuration that delivers one time in eight has not
  done the job the expert estimate describes. This leaves 283 cells.
- **The compute inversion must survive its own check** (below). 21 cells fail and are
  withheld; 49 more are withheld because the deliverable is a trained model.

There is no cap on configurations per task and no deduplication of reasoning-effort
variants. Every surviving cell becomes a row, on the coordinator's 2026-09-14 ruling that
model-distinct rows on the same task are wanted because they show the trend across models;
an earlier draft kept five configurations per task at 40 hours or more and three below, one
per distinct model, and produced 33 rows.

| Task | Expert hours | Rows |
|---|---:|---:|
| `excel-clone` | 380 | 2 |
| `kubernetes-rust-rewrite` | 200 | 9 |
| `ruby-rust-port` | 110 | 2 |
| `mastodon-clone` | 75 | 1 |
| `trimul-cuda` | 40 | 19 |
| `find-network-alignments` | 20 | 14 |
| `stripe-clone` | 14 | 7 |
| `wasm-simd` | 12 | 34 |
| `zstd-decoder` | 12 | 29 |
| `jax-pytorch-rewrite` | 8 | 32 |
| `vliw-kernel-optimization` | 8 | 26 |
| `embedding-eval` | 4 | 38 |

Thirteen tasks have at least one passing cell, and twelve survive to rows. Seven never do:
`nextjs-vite-rewrite` (400 h), `biofabric-rust-rewrite` (80 h), `s3-clone` and `slack-clone`
(60 h), `rust-c-compiler` (30 h), and `rust-java-lsp` (20 h, best pass rate 0.38);
`parameter-golf` and `post-train-ifeval-gpu` pass but are withheld on compute. The longest
task any configuration finishes is `excel-clone` at 380 hours.

<a id="compute"></a>

## Compute

### What the counted total is

Section 4.2: each run logs `n_input_tokens`, `n_cache_tokens` and `n_output_tokens`, and
"tokens" means `n_input + n_output`, with cached tokens included. Section 5.2 says what that
implies — "cumulative input across API calls reaching millions to hundreds of millions of
tokens, far beyond what any single context window holds" — and gives the corpus split, 36.3B
input against 192.7M output, so model-generated text is about 0.53% of the count. The counted
total is therefore the whole prefix re-read on every call plus the output, summed over calls.
`tokens_accounting = source_total`.

Charging every one of those positions `2 * N_active` would price a cache read as a full
forward pass. `research/attention-correction.md#metr-cache-reads` sets out the correction:
cached prefix positions are keys, not queries, so they raise the context that later positions
attend over and take no weights pass of their own.

### The inversion, with a measured call count

Write `C` for the counted total and `k` for the number of API turns. For an append-only
dialog whose prefix grows linearly, the prefix at turn `i` is `i` times the new tokens per
turn, so `C = P k / 2` for `P` processed positions, and

```
P    = 2C / k          positions that took a weights pass
Nbar = C / k           mean context those positions attended over
```

`Nbar` is the mean per-call prompt-plus-output length, which is what it means: it is a
measurement, not an assumption, and is therefore not subject to the 200,000-token cap in
`research/attention-correction.md#mean-attended-context`. `P` is the assumption.

`k` is measured. Every rollout has a public trajectory JSON at
`swe-marathon.org/trajectories/v1.1/<trial>.json` whose rows carry `step`, the API turn, and
`call`, the tool-call index within that turn; `k` is `max(step)`.
`research/swe-marathon/fetch_turns.py` reads it for all 2,129 passing rollouts. This is where
these rows are on firmer ground than the METR block, which has to take a single assumed
new-tokens-per-call for 283 rows.

Compute is then, per row, the mean over that cell's passing trials of

```
compute_flops = 2 * N_active * P + 4 * L * d_attn * Nbar * P
```

with `N_active`, `L` and `d_attn` from `models.csv`. `attention_context` is the `P`-weighted
mean of the per-trial `Nbar` so that `compute_flops = flops_per_token * P̄ * (1 + r)` holds
exactly for the recorded `attention_ratio`; the script asserts it.

### The check that measures the third quantity

Each trajectory row also carries the model's own text for that call — its message and the
tool arguments it wrote — so summing characters over a trajectory measures the rollout's
output tokens `O`. Output tokens are processed positions by definition, so `O` is a hard
floor on `P`, and the comparison is a real test of the inversion rather than a restatement of
it.

Across all 2,129 passing rollouts the measured output is 0.25% of the counted total at the
median, against the paper's 0.53% for the whole corpus including failures — the same
quantity, the same order, from a completely different route. That is the check that the
trajectory text is in fact the output and that the counted total means what Section 4.2 says.

Against `P` the picture separates by harness. The median `O/P` is 0.16 overall, leaving fresh
tool-result input as the rest, which is what a tool-using agent should look like. But 169 of
312 GPT-6 Astra rollouts under Codex have `O > P`, which is impossible: that harness is not
append-only, it is holding a rolling or compacted context, and the inversion gives no
estimate for it. Four built cells fail the test and are withheld with their ratios:

| Cell | O/P |
|---|---:|
| kubernetes-rust-rewrite, GPT-6-astra (xhigh) under Codex | 10.90 |
| kubernetes-rust-rewrite, GPT-6-astra (medium) under Codex | 6.31 |
| vliw-kernel-optimization, Grok 4.5 under Grok Build | 5.94 |
| kubernetes-rust-rewrite, GLM 5.3 Flash (max) under Claude Code | 3.94 |
| kubernetes-rust-rewrite, GPT-6-astra (low) under Codex | 3.32 |
| excel-clone, GPT-6-astra (medium) under Codex | 2.93 |
| excel-clone, GPT-6-astra (low) under Codex | 2.76 |
| zstd-decoder, GPT-6-astra (high) under Codex | 1.71 |
| find-network-alignments, GPT-6-astra (xhigh) under Codex | 1.67 |
| zstd-decoder, GPT-6-astra (medium) under Codex | 1.58 |
| ruby-rust-port, GPT-6-astra (high) under Codex | 1.55 |
| zstd-decoder, Grok 4.5 under Grok Build | 1.55 |
| kubernetes-rust-rewrite, Claude Fable 5.1 (max) under Claude Code | 1.51 |
| ruby-rust-port, GPT-6-astra (low) under Codex | 1.47 |
| ruby-rust-port, GPT-6-astra (xhigh) under Codex | 1.43 |
| zstd-decoder, GPT-6-astra (low) under Codex | 1.36 |
| find-network-alignments, GPT-6-astra (high) under Codex | 1.27 |
| jax-pytorch-rewrite, GPT-6-astra (medium) under Codex | 1.27 |
| find-network-alignments, GPT-6-astra (max) under Codex | 1.09 |
| jax-pytorch-rewrite, GPT-6-astra (high) under Codex | 1.08 |
| find-network-alignments, GPT-6-astra (medium) under Codex | 1.04 |

25 built rows sit between 0.5 and 1, most of them GPT-6 Astra and GPT-5.6 cells under
Codex. Fresh tool-result input smaller than output is implausible for an agent running
hundreds of shell commands, so on those rows the rebuilt count is near its floor and
`compute_flops` reads as a lower bound. Each says so in `notes`. They are kept rather than
withheld because several are the only surviving rows on their tasks, including the 380-hour
`excel-clone` GPT-6 Astra row. `row-arithmetic.csv` carries the ratio for every row, so the
set is one filter away if a reviewer wants it cut.

### The second consistency check: context windows

If the inversion holds, `2C/k` is the final trajectory length, which cannot exceed the
context window without compaction. It fits for 184 of the 213 rows, which is a non-trivial pass:
the implied lengths run from 20k to 1,094k and the windows from 203k to 2,000k, and nothing in
the arithmetic was fitted to make them agree. 29 rows exceed their window, the worst at
2.7 times, and on those the run compacted, which raises `P` by roughly the number of
compactions and makes `compute_flops` a lower bound in the other direction from the output
check. Each row states which case it is in, and `row-arithmetic.csv` carries the ratio.
Window figures for the v1.1 models are carried forward from the paper's Table 3 where the
model appears there and from the provider's published figure otherwise, so the check is
loose at the edges; Kimi K3's 262k is the value most likely stale.

### Compute deliberately excluded

**The environment's GPUs, where they are a checking cost.** `trimul-cuda` has an H100,
`jax-pytorch-rewrite` an A100, `embedding-eval` an H100. In all three the GPU runs the agent's
own code to check it — correctness cases and latency benchmarks on the first two, MiniLM over
37 datasets on the third — which is the same role a test suite plays and the same tool the
human reference author used. Excluded, following the RE-Bench treatment in
`research/rebench.md`, and stated in each row's `notes`.

**Two tasks where the GPU is not a checking cost, and their cells are withheld.**
`parameter-golf` asks the agent to train a compact GPT on one H100 under a 32 MB checkpoint
cap, and `post-train-ifeval-gpu` asks it to post-train Llama-3.2-1B through the Tinker API to
an IFEval target. In both the deliverable *is* a trained model, the agent chooses the recipe
and how long to run it, and the training compute is neither published nor bounded by a fixed
grant. Five hours of one H100 at 30% utilization is about 5e18 FLOPs, one to two orders above
the token compute on those cells, so a row built from tokens alone would not be an estimate
of the task's compute. 49 cells withheld; they are in `dispositions.csv` with their
pass rates, so the call is cheap to reverse.

This is the same question `research/rebench.md` logged for Damon as a cross-batch item. The
RE-Bench ruling excluded environment GPU work on the grounds that the allocation is a fixed
grant that does not vary with the agent. That reasoning does not reach `parameter-golf`,
where the agent picks the training run, which is why those cells are withheld rather than
built with the term excluded.

**Nothing else.** No task in the suite calls a second model, except the verifier-side
computer-use grader on the product clones, which is assessment rather than task work.

### Cost

`ai_cost_usd` is the mean over the cell's passing trials of the leaderboard's own per-trial
dollar figure, `ai_cost_basis = reported`, `ai_cost_date` the earliest passing trial's start
date. Rows whose passing trials carry no published cost, which is most of the OpenRouter-served
configurations, take `not_available`. Human cost is not published.

<a id="labels"></a>

## Labels

Every built row is `match`. Reward is binary and the verifier is multi-layer: a resolved trial
means the agent handed over a deliverable that passes the same checks the human reference
solution passes, and the expert estimate is an estimate of producing that deliverable. Nothing
in the record supports grading the AI's work above or below the reference once both pass, so
`match` by completion is the only defensible label. The pass rate is the reliability of the
configuration, not the quality of the work it hands over, and it sits in
`performance_evidence` along with the mean partial score.

No row is `above` or `far_above`. Agents finish inside a 4-to-10-hour wall clock against
estimates of 4 to 380 hours, which is a large speed advantage, but `performance_vs_human`
grades the work, not the elapsed time, and the dataset's speed comparison is the ratio of
`compute_flops` to `human_time` rather than a label.

`comparison_issues` is `none_identified` except on `excel-clone` and `mastodon-clone`, whose
reward is the minimum of a deterministic stage and a browser-driven UX rubric graded by a
computer-use agent with an LLM judge. That is a different assessment protocol from a test
suite and is flagged as `different_assessment`.

Two facts about the comparison that are not `comparison_issues` under COLUMNS.md but belong
on the record. Agents are not told the task time limit (Section 6), so pacing is not matched
to the wall clock they have. And 13.8% of v1.0 rollouts contained an exploit-shaped action
and 10.2% shipped a verifier bypass, none of which earned reward: the anti-cheat layers
caught all 132 shipped bypasses in the audited corpus, so the binary reward behind these rows
is doing the work the label needs it to.

## Models

Seventeen of the eighteen models these rows use are already in `models.csv`: `claude-opus-5`,
`claude-sonnet-5`, `claude-opus-4-8`, `claude-fable-5`, `claude-fable-5-1`, `gpt-6-astra`,
`gpt-5-6-sol`, `gpt-5-6-terra`, `gpt-5-6-luna`, `kimi-k3`, `glm-5.3`, `glm-5.3-flash`,
`glm-5.2`, `grok-4-5`, `grok-4-6`, `muse-spark-1-3` and `deepseek-v4-pro-0813`.

`gemini-3-7-flash`, needed by four `OpenCode` rows, was new when this batch was built and a
parallel collector landed it in `models.csv` before submission, with the same release date,
the same 40B-active Flash-tier prior with a 15-90B range, and the same 59 layers at 7,552
wide. Nothing in these rows changes, and `candidates/swe-marathon-models.csv` carries only
its header.

Reasoning-effort variants map to the base model id. Effort changes how many tokens a run
spends, which these rows measure, not the FLOPs a token costs; the setting is in the
`point_id` and in `source_record`.

## Files

| Path | What it is |
|---|---|
| `research/swe-marathon/extract_leaderboard.py` | reads the retained site bundle, writes the three flat tables |
| `research/swe-marathon/fetch_turns.py` | fetches the public trajectories, writes turn counts and measured output |
| `research/swe-marathon/make_rows.py` | selects cells, does the arithmetic, writes the rows |
| `agent-work/derived/swe-marathon/cells.csv` | 958 task x configuration cells |
| `agent-work/derived/swe-marathon/trials.csv` | 7,650 rollouts |
| `agent-work/derived/swe-marathon/turns.csv` | API turns and measured output for 2,129 passing rollouts |
| `agent-work/derived/swe-marathon/row-arithmetic.csv` | per row: C, k, P, Nbar, r, output shares, window ratio |
| `agent-work/derived/swe-marathon/dispositions.csv` | every cell not built, with its reason |
| `agent-work/derived/swe-marathon/models-swe-marathon.csv` | the one new model record |
| `agent-work/derived/swe-marathon/points-merged.csv` | points.csv with these rows appended, for validation |

## Per-row record

`agent-work/derived/swe-marathon/row-arithmetic.csv` carries every input and intermediate for
each row: the mean counted tokens `C`, the mean API turn count `k`, the rebuilt processed
positions `P`, the mean attended context `Nbar`, the attention ratio `r`, the measured output
and its two shares, the implied trajectory length against the context window, and FLOPs per
human-second. The anchors below name each row so `compute_source` resolves, and the table
repeats the arithmetic in reading order, longest task first.

<a id="agen-swemar-embedeval-astra-high"></a>
<a id="agen-swemar-embedeval-astra-low"></a>
<a id="agen-swemar-embedeval-astra-max"></a>
<a id="agen-swemar-embedeval-astra-medium"></a>
<a id="agen-swemar-embedeval-astra-xhigh"></a>
<a id="agen-swemar-embedeval-fable5"></a>
<a id="agen-swemar-embedeval-fable51-max"></a>
<a id="agen-swemar-embedeval-gem37flash"></a>
<a id="agen-swemar-embedeval-glm52"></a>
<a id="agen-swemar-embedeval-glm53-high"></a>
<a id="agen-swemar-embedeval-glm53-max"></a>
<a id="agen-swemar-embedeval-glm53flash-max"></a>
<a id="agen-swemar-embedeval-grok45"></a>
<a id="agen-swemar-embedeval-grok46-high"></a>
<a id="agen-swemar-embedeval-kimik3"></a>
<a id="agen-swemar-embedeval-luna-high"></a>
<a id="agen-swemar-embedeval-luna-max"></a>
<a id="agen-swemar-embedeval-luna-xhigh"></a>
<a id="agen-swemar-embedeval-muse13-max"></a>
<a id="agen-swemar-embedeval-muse13-xhigh"></a>
<a id="agen-swemar-embedeval-opus48"></a>
<a id="agen-swemar-embedeval-opus5"></a>
<a id="agen-swemar-embedeval-opus5-high"></a>
<a id="agen-swemar-embedeval-opus5-low"></a>
<a id="agen-swemar-embedeval-opus5-medium"></a>
<a id="agen-swemar-embedeval-sol-high"></a>
<a id="agen-swemar-embedeval-sol-low"></a>
<a id="agen-swemar-embedeval-sol-max"></a>
<a id="agen-swemar-embedeval-sol-medium"></a>
<a id="agen-swemar-embedeval-sol-xhigh"></a>
<a id="agen-swemar-embedeval-sonnet5-high"></a>
<a id="agen-swemar-embedeval-sonnet5-max"></a>
<a id="agen-swemar-embedeval-sonnet5-medium"></a>
<a id="agen-swemar-embedeval-sonnet5-xhigh"></a>
<a id="agen-swemar-embedeval-terra-high"></a>
<a id="agen-swemar-embedeval-terra-max"></a>
<a id="agen-swemar-embedeval-terra-medium"></a>
<a id="agen-swemar-embedeval-terra-xhigh"></a>
<a id="agen-swemar-excel-astra-max"></a>
<a id="agen-swemar-excel-fable51-max"></a>
<a id="agen-swemar-jaxtorch-astra-low"></a>
<a id="agen-swemar-jaxtorch-astra-max"></a>
<a id="agen-swemar-jaxtorch-astra-xhigh"></a>
<a id="agen-swemar-jaxtorch-fable5"></a>
<a id="agen-swemar-jaxtorch-fable51-max"></a>
<a id="agen-swemar-jaxtorch-gem37flash"></a>
<a id="agen-swemar-jaxtorch-glm53-high"></a>
<a id="agen-swemar-jaxtorch-glm53-max"></a>
<a id="agen-swemar-jaxtorch-glm53flash-max"></a>
<a id="agen-swemar-jaxtorch-grok45"></a>
<a id="agen-swemar-jaxtorch-grok46-high"></a>
<a id="agen-swemar-jaxtorch-kimik3"></a>
<a id="agen-swemar-jaxtorch-muse13-max"></a>
<a id="agen-swemar-jaxtorch-muse13-xhigh"></a>
<a id="agen-swemar-jaxtorch-opus48"></a>
<a id="agen-swemar-jaxtorch-opus5"></a>
<a id="agen-swemar-jaxtorch-opus5-high"></a>
<a id="agen-swemar-jaxtorch-opus5-low"></a>
<a id="agen-swemar-jaxtorch-opus5-medium"></a>
<a id="agen-swemar-jaxtorch-opus5-xhigh"></a>
<a id="agen-swemar-jaxtorch-sol-high"></a>
<a id="agen-swemar-jaxtorch-sol-low"></a>
<a id="agen-swemar-jaxtorch-sol-max"></a>
<a id="agen-swemar-jaxtorch-sol-medium"></a>
<a id="agen-swemar-jaxtorch-sol-xhigh"></a>
<a id="agen-swemar-jaxtorch-sonnet5-high"></a>
<a id="agen-swemar-jaxtorch-sonnet5-max"></a>
<a id="agen-swemar-jaxtorch-sonnet5-medium"></a>
<a id="agen-swemar-jaxtorch-sonnet5-xhigh"></a>
<a id="agen-swemar-jaxtorch-terra-high"></a>
<a id="agen-swemar-jaxtorch-terra-max"></a>
<a id="agen-swemar-jaxtorch-terra-xhigh"></a>
<a id="agen-swemar-k8srust-kimik3"></a>
<a id="agen-swemar-k8srust-opus48"></a>
<a id="agen-swemar-k8srust-opus5"></a>
<a id="agen-swemar-k8srust-opus5-high"></a>
<a id="agen-swemar-k8srust-opus5-low"></a>
<a id="agen-swemar-k8srust-opus5-medium"></a>
<a id="agen-swemar-k8srust-opus5-xhigh"></a>
<a id="agen-swemar-k8srust-sol-max"></a>
<a id="agen-swemar-k8srust-sol-xhigh"></a>
<a id="agen-swemar-mastodon-sol-xhigh"></a>
<a id="agen-swemar-ppialign-astra-low"></a>
<a id="agen-swemar-ppialign-fable5"></a>
<a id="agen-swemar-ppialign-fable51-max"></a>
<a id="agen-swemar-ppialign-gem37flash"></a>
<a id="agen-swemar-ppialign-glm53-max"></a>
<a id="agen-swemar-ppialign-glm53flash-max"></a>
<a id="agen-swemar-ppialign-kimik3"></a>
<a id="agen-swemar-ppialign-opus48"></a>
<a id="agen-swemar-ppialign-opus5"></a>
<a id="agen-swemar-ppialign-opus5-high"></a>
<a id="agen-swemar-ppialign-opus5-low"></a>
<a id="agen-swemar-ppialign-opus5-medium"></a>
<a id="agen-swemar-ppialign-opus5-xhigh"></a>
<a id="agen-swemar-ppialign-sonnet5-max"></a>
<a id="agen-swemar-rubyrust-opus5-high"></a>
<a id="agen-swemar-rubyrust-sol-max"></a>
<a id="agen-swemar-stripe-glm53-high"></a>
<a id="agen-swemar-stripe-glm53flash-max"></a>
<a id="agen-swemar-stripe-muse13-max"></a>
<a id="agen-swemar-stripe-muse13-xhigh"></a>
<a id="agen-swemar-stripe-opus48"></a>
<a id="agen-swemar-stripe-sol-medium"></a>
<a id="agen-swemar-stripe-sol-none"></a>
<a id="agen-swemar-trimul-fable5"></a>
<a id="agen-swemar-trimul-fable51-max"></a>
<a id="agen-swemar-trimul-gem37flash"></a>
<a id="agen-swemar-trimul-glm53-low"></a>
<a id="agen-swemar-trimul-glm53-max"></a>
<a id="agen-swemar-trimul-glm53flash-max"></a>
<a id="agen-swemar-trimul-kimik3"></a>
<a id="agen-swemar-trimul-muse13-max"></a>
<a id="agen-swemar-trimul-muse13-xhigh"></a>
<a id="agen-swemar-trimul-opus48"></a>
<a id="agen-swemar-trimul-opus5"></a>
<a id="agen-swemar-trimul-opus5-high"></a>
<a id="agen-swemar-trimul-opus5-low"></a>
<a id="agen-swemar-trimul-opus5-medium"></a>
<a id="agen-swemar-trimul-opus5-xhigh"></a>
<a id="agen-swemar-trimul-sol-high"></a>
<a id="agen-swemar-trimul-sol-max"></a>
<a id="agen-swemar-trimul-sol-medium"></a>
<a id="agen-swemar-trimul-sonnet5-max"></a>
<a id="agen-swemar-vliw-astra-high"></a>
<a id="agen-swemar-vliw-astra-low"></a>
<a id="agen-swemar-vliw-astra-max"></a>
<a id="agen-swemar-vliw-astra-medium"></a>
<a id="agen-swemar-vliw-astra-xhigh"></a>
<a id="agen-swemar-vliw-fable5"></a>
<a id="agen-swemar-vliw-fable51-max"></a>
<a id="agen-swemar-vliw-glm53-high"></a>
<a id="agen-swemar-vliw-glm53-low"></a>
<a id="agen-swemar-vliw-glm53-max"></a>
<a id="agen-swemar-vliw-glm53flash-max"></a>
<a id="agen-swemar-vliw-grok46-high"></a>
<a id="agen-swemar-vliw-kimik3"></a>
<a id="agen-swemar-vliw-luna-max"></a>
<a id="agen-swemar-vliw-opus48"></a>
<a id="agen-swemar-vliw-opus5"></a>
<a id="agen-swemar-vliw-opus5-high"></a>
<a id="agen-swemar-vliw-opus5-low"></a>
<a id="agen-swemar-vliw-opus5-medium"></a>
<a id="agen-swemar-vliw-opus5-xhigh"></a>
<a id="agen-swemar-vliw-sol-high"></a>
<a id="agen-swemar-vliw-sol-max"></a>
<a id="agen-swemar-vliw-sol-medium"></a>
<a id="agen-swemar-vliw-sol-xhigh"></a>
<a id="agen-swemar-vliw-sonnet5-xhigh"></a>
<a id="agen-swemar-vliw-terra-max"></a>
<a id="agen-swemar-wasmsimd-dsv4pro"></a>
<a id="agen-swemar-wasmsimd-fable5"></a>
<a id="agen-swemar-wasmsimd-fable51-max"></a>
<a id="agen-swemar-wasmsimd-glm52"></a>
<a id="agen-swemar-wasmsimd-glm53-high"></a>
<a id="agen-swemar-wasmsimd-glm53-low"></a>
<a id="agen-swemar-wasmsimd-glm53-max"></a>
<a id="agen-swemar-wasmsimd-glm53flash-max"></a>
<a id="agen-swemar-wasmsimd-grok45"></a>
<a id="agen-swemar-wasmsimd-grok46-high"></a>
<a id="agen-swemar-wasmsimd-kimik3"></a>
<a id="agen-swemar-wasmsimd-luna-high"></a>
<a id="agen-swemar-wasmsimd-luna-max"></a>
<a id="agen-swemar-wasmsimd-luna-xhigh"></a>
<a id="agen-swemar-wasmsimd-muse13-max"></a>
<a id="agen-swemar-wasmsimd-muse13-xhigh"></a>
<a id="agen-swemar-wasmsimd-opus48"></a>
<a id="agen-swemar-wasmsimd-opus5"></a>
<a id="agen-swemar-wasmsimd-opus5-high"></a>
<a id="agen-swemar-wasmsimd-opus5-low"></a>
<a id="agen-swemar-wasmsimd-opus5-medium"></a>
<a id="agen-swemar-wasmsimd-opus5-xhigh"></a>
<a id="agen-swemar-wasmsimd-sol-high"></a>
<a id="agen-swemar-wasmsimd-sol-low"></a>
<a id="agen-swemar-wasmsimd-sol-max"></a>
<a id="agen-swemar-wasmsimd-sol-medium"></a>
<a id="agen-swemar-wasmsimd-sol-xhigh"></a>
<a id="agen-swemar-wasmsimd-sonnet5-high"></a>
<a id="agen-swemar-wasmsimd-sonnet5-low"></a>
<a id="agen-swemar-wasmsimd-sonnet5-max"></a>
<a id="agen-swemar-wasmsimd-sonnet5-medium"></a>
<a id="agen-swemar-wasmsimd-sonnet5-xhigh"></a>
<a id="agen-swemar-wasmsimd-terra-max"></a>
<a id="agen-swemar-wasmsimd-terra-xhigh"></a>
<a id="agen-swemar-zstd-astra-max"></a>
<a id="agen-swemar-zstd-astra-xhigh"></a>
<a id="agen-swemar-zstd-fable5"></a>
<a id="agen-swemar-zstd-fable51-max"></a>
<a id="agen-swemar-zstd-glm52"></a>
<a id="agen-swemar-zstd-glm53-high"></a>
<a id="agen-swemar-zstd-glm53-low"></a>
<a id="agen-swemar-zstd-glm53-max"></a>
<a id="agen-swemar-zstd-glm53flash-max"></a>
<a id="agen-swemar-zstd-grok46-high"></a>
<a id="agen-swemar-zstd-kimik3"></a>
<a id="agen-swemar-zstd-luna-max"></a>
<a id="agen-swemar-zstd-muse13-max"></a>
<a id="agen-swemar-zstd-muse13-xhigh"></a>
<a id="agen-swemar-zstd-opus48"></a>
<a id="agen-swemar-zstd-opus5"></a>
<a id="agen-swemar-zstd-opus5-high"></a>
<a id="agen-swemar-zstd-opus5-low"></a>
<a id="agen-swemar-zstd-opus5-medium"></a>
<a id="agen-swemar-zstd-opus5-xhigh"></a>
<a id="agen-swemar-zstd-sol-high"></a>
<a id="agen-swemar-zstd-sol-max"></a>
<a id="agen-swemar-zstd-sol-xhigh"></a>
<a id="agen-swemar-zstd-sonnet5-high"></a>
<a id="agen-swemar-zstd-sonnet5-low"></a>
<a id="agen-swemar-zstd-sonnet5-max"></a>
<a id="agen-swemar-zstd-sonnet5-medium"></a>
<a id="agen-swemar-zstd-sonnet5-xhigh"></a>
<a id="agen-swemar-zstd-terra-max"></a>

| point_id | Task | Expert h | Model | C (M) | k | P (k) | Nbar (k) | r | O/P | FLOPs | FLOPs per human-second |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `agen-swemar-excel-astra-max` | excel-clone | 380 | gpt-6-astra | 7.2 | 173 | 83 | 42 | 0.47 | 0.99 | 7.32e+16 | 5.35e+10 |
| `agen-swemar-excel-fable51-max` | excel-clone | 380 | claude-fable-5-1 | 22.7 | 105 | 458 | 242 | 3.42 | 0.36 | 6.07e+17 | 4.44e+11 |
| `agen-swemar-k8srust-kimik3` | kubernetes-rust-rewrite | 200 | kimi-k3 | 294.8 | 1215 | 499 | 265 | 0.88 | 0.93 | 1.95e+17 | 2.70e+11 |
| `agen-swemar-k8srust-opus48` | kubernetes-rust-rewrite | 200 | claude-opus-4-8 | 257.1 | 804 | 637 | 330 | 5.40 | 0.52 | 8.16e+17 | 1.13e+12 |
| `agen-swemar-k8srust-opus5` | kubernetes-rust-rewrite | 200 | claude-opus-5 | 211.0 | 384 | 1094 | 549 | 8.99 | 0.26 | 2.19e+18 | 3.04e+12 |
| `agen-swemar-k8srust-opus5-high` | kubernetes-rust-rewrite | 200 | claude-opus-5 | 191.6 | 362 | 1056 | 530 | 8.68 | 0.24 | 2.05e+18 | 2.84e+12 |
| `agen-swemar-k8srust-opus5-low` | kubernetes-rust-rewrite | 200 | claude-opus-5 | 187.8 | 377 | 996 | 498 | 8.17 | 0.25 | 1.83e+18 | 2.54e+12 |
| `agen-swemar-k8srust-opus5-medium` | kubernetes-rust-rewrite | 200 | claude-opus-5 | 197.8 | 384 | 1023 | 516 | 8.45 | 0.25 | 1.93e+18 | 2.69e+12 |
| `agen-swemar-k8srust-opus5-xhigh` | kubernetes-rust-rewrite | 200 | claude-opus-5 | 213.7 | 494 | 972 | 501 | 8.21 | 0.32 | 1.79e+18 | 2.49e+12 |
| `agen-swemar-k8srust-sol-max` | kubernetes-rust-rewrite | 200 | gpt-5-6-sol | 161.4 | 1480 | 217 | 109 | 1.54 | 0.86 | 1.65e+17 | 2.29e+11 |
| `agen-swemar-k8srust-sol-xhigh` | kubernetes-rust-rewrite | 200 | gpt-5-6-sol | 87.8 | 740 | 238 | 119 | 1.68 | 0.36 | 1.91e+17 | 2.65e+11 |
| `agen-swemar-rubyrust-opus5-high` | ruby-rust-port | 110 | claude-opus-5 | 97.8 | 229 | 847 | 427 | 7.00 | 0.18 | 1.35e+18 | 3.42e+12 |
| `agen-swemar-rubyrust-sol-max` | ruby-rust-port | 110 | gpt-5-6-sol | 53.7 | 606 | 178 | 89 | 1.26 | 0.86 | 1.20e+17 | 3.04e+11 |
| `agen-swemar-mastodon-sol-xhigh` | mastodon-clone | 75 | gpt-5-6-sol | 8.6 | 102 | 167 | 84 | 1.19 | 0.28 | 1.09e+17 | 4.05e+11 |
| `agen-swemar-trimul-fable5` | trimul-cuda | 40 | claude-fable-5 | 51.1 | 179 | 559 | 282 | 3.99 | 0.11 | 8.38e+17 | 5.82e+12 |
| `agen-swemar-trimul-fable51-max` | trimul-cuda | 40 | claude-fable-5-1 | 18.3 | 72 | 509 | 256 | 3.62 | 0.11 | 7.06e+17 | 4.90e+12 |
| `agen-swemar-trimul-gem37flash` | trimul-cuda | 40 | gemini-3-7-flash | 23.6 | 166 | 265 | 142 | 3.17 | 0.37 | 8.84e+16 | 6.14e+11 |
| `agen-swemar-trimul-glm53-low` | trimul-cuda | 40 | glm-5.3 | 14.9 | 140 | 204 | 105 | 2.33 | 0.21 | 5.45e+16 | 3.78e+11 |
| `agen-swemar-trimul-glm53-max` | trimul-cuda | 40 | glm-5.3 | 41.5 | 188 | 442 | 222 | 4.95 | 0.14 | 2.10e+17 | 1.46e+12 |
| `agen-swemar-trimul-glm53flash-max` | trimul-cuda | 40 | glm-5.3-flash | 23.7 | 240 | 198 | 99 | 2.85 | 0.43 | 2.74e+16 | 1.90e+11 |
| `agen-swemar-trimul-kimik3` | trimul-cuda | 40 | kimi-k3 | 40.7 | 191 | 417 | 211 | 0.70 | 0.18 | 1.47e+17 | 1.02e+12 |
| `agen-swemar-trimul-muse13-max` | trimul-cuda | 40 | muse-spark-1-3 | 56.9 | 480 | 232 | 117 | 1.92 | 0.40 | 1.35e+17 | 9.40e+11 |
| `agen-swemar-trimul-muse13-xhigh` | trimul-cuda | 40 | muse-spark-1-3 | 49.5 | 443 | 222 | 111 | 1.82 | 0.44 | 1.25e+17 | 8.70e+11 |
| `agen-swemar-trimul-opus48` | trimul-cuda | 40 | claude-opus-4-8 | 73.9 | 222 | 646 | 337 | 5.52 | 0.11 | 8.43e+17 | 5.86e+12 |
| `agen-swemar-trimul-opus5` | trimul-cuda | 40 | claude-opus-5 | 42.7 | 142 | 597 | 300 | 4.92 | 0.10 | 7.06e+17 | 4.90e+12 |
| `agen-swemar-trimul-opus5-high` | trimul-cuda | 40 | claude-opus-5 | 29.1 | 139 | 414 | 209 | 3.43 | 0.11 | 3.67e+17 | 2.55e+12 |
| `agen-swemar-trimul-opus5-low` | trimul-cuda | 40 | claude-opus-5 | 19.2 | 131 | 286 | 149 | 2.44 | 0.13 | 1.97e+17 | 1.36e+12 |
| `agen-swemar-trimul-opus5-medium` | trimul-cuda | 40 | claude-opus-5 | 20.1 | 125 | 318 | 160 | 2.63 | 0.12 | 2.31e+17 | 1.60e+12 |
| `agen-swemar-trimul-opus5-xhigh` | trimul-cuda | 40 | claude-opus-5 | 27.5 | 122 | 444 | 224 | 3.68 | 0.10 | 4.16e+17 | 2.89e+12 |
| `agen-swemar-trimul-sol-high` | trimul-cuda | 40 | gpt-5-6-sol | 10.5 | 172 | 118 | 61 | 0.86 | 0.40 | 6.58e+16 | 4.57e+11 |
| `agen-swemar-trimul-sol-max` | trimul-cuda | 40 | gpt-5-6-sol | 10.6 | 171 | 120 | 63 | 0.90 | 0.66 | 6.85e+16 | 4.76e+11 |
| `agen-swemar-trimul-sol-medium` | trimul-cuda | 40 | gpt-5-6-sol | 9.3 | 176 | 107 | 54 | 0.77 | 0.65 | 5.67e+16 | 3.93e+11 |
| `agen-swemar-trimul-sonnet5-max` | trimul-cuda | 40 | claude-sonnet-5 | 108.2 | 302 | 715 | 358 | 5.87 | 0.10 | 9.81e+17 | 6.81e+12 |
| `agen-swemar-ppialign-astra-low` | find-network-alignments | 20 | gpt-6-astra | 7.4 | 254 | 55 | 29 | 0.33 | 0.89 | 4.43e+16 | 6.15e+11 |
| `agen-swemar-ppialign-fable5` | find-network-alignments | 20 | claude-fable-5 | 22.5 | 146 | 301 | 154 | 2.17 | 0.11 | 2.87e+17 | 3.98e+12 |
| `agen-swemar-ppialign-fable51-max` | find-network-alignments | 20 | claude-fable-5-1 | 8.3 | 80 | 206 | 104 | 1.47 | 0.09 | 1.52e+17 | 2.12e+12 |
| `agen-swemar-ppialign-gem37flash` | find-network-alignments | 20 | gemini-3-7-flash | 21.3 | 103 | 323 | 243 | 5.41 | 0.35 | 1.66e+17 | 2.30e+12 |
| `agen-swemar-ppialign-glm53-max` | find-network-alignments | 20 | glm-5.3 | 13.2 | 126 | 205 | 106 | 2.37 | 0.17 | 5.52e+16 | 7.67e+11 |
| `agen-swemar-ppialign-glm53flash-max` | find-network-alignments | 20 | glm-5.3-flash | 24.7 | 251 | 194 | 98 | 2.81 | 0.27 | 2.67e+16 | 3.70e+11 |
| `agen-swemar-ppialign-kimik3` | find-network-alignments | 20 | kimi-k3 | 12.5 | 130 | 190 | 96 | 0.32 | 0.14 | 5.20e+16 | 7.22e+11 |
| `agen-swemar-ppialign-opus48` | find-network-alignments | 20 | claude-opus-4-8 | 44.3 | 191 | 434 | 233 | 3.82 | 0.10 | 4.19e+17 | 5.81e+12 |
| `agen-swemar-ppialign-opus5` | find-network-alignments | 20 | claude-opus-5 | 19.8 | 130 | 284 | 150 | 2.45 | 0.12 | 1.96e+17 | 2.72e+12 |
| `agen-swemar-ppialign-opus5-high` | find-network-alignments | 20 | claude-opus-5 | 7.5 | 93 | 159 | 81 | 1.33 | 0.10 | 7.38e+16 | 1.02e+12 |
| `agen-swemar-ppialign-opus5-low` | find-network-alignments | 20 | claude-opus-5 | 3.7 | 75 | 100 | 50 | 0.82 | 0.08 | 3.63e+16 | 5.04e+11 |
| `agen-swemar-ppialign-opus5-medium` | find-network-alignments | 20 | claude-opus-5 | 6.5 | 99 | 111 | 60 | 0.97 | 0.09 | 4.39e+16 | 6.09e+11 |
| `agen-swemar-ppialign-opus5-xhigh` | find-network-alignments | 20 | claude-opus-5 | 10.4 | 105 | 195 | 99 | 1.62 | 0.11 | 1.02e+17 | 1.42e+12 |
| `agen-swemar-ppialign-sonnet5-max` | find-network-alignments | 20 | claude-sonnet-5 | 83.0 | 305 | 525 | 268 | 4.39 | 0.08 | 5.65e+17 | 7.85e+12 |
| `agen-swemar-stripe-glm53-high` | stripe-clone | 14 | glm-5.3 | 22.7 | 221 | 204 | 104 | 2.31 | 0.47 | 5.41e+16 | 1.07e+12 |
| `agen-swemar-stripe-glm53flash-max` | stripe-clone | 14 | glm-5.3-flash | 21.8 | 266 | 165 | 83 | 2.39 | 0.62 | 2.02e+16 | 4.00e+11 |
| `agen-swemar-stripe-muse13-max` | stripe-clone | 14 | muse-spark-1-3 | 12.2 | 156 | 154 | 77 | 1.27 | 0.13 | 7.00e+16 | 1.39e+12 |
| `agen-swemar-stripe-muse13-xhigh` | stripe-clone | 14 | muse-spark-1-3 | 12.6 | 160 | 156 | 79 | 1.30 | 0.13 | 7.18e+16 | 1.42e+12 |
| `agen-swemar-stripe-opus48` | stripe-clone | 14 | claude-opus-4-8 | 14.1 | 102 | 264 | 134 | 2.19 | 0.16 | 1.69e+17 | 3.35e+12 |
| `agen-swemar-stripe-sol-medium` | stripe-clone | 14 | gpt-5-6-sol | 1.2 | 48 | 50 | 25 | 0.35 | 0.34 | 2.02e+16 | 4.00e+11 |
| `agen-swemar-stripe-sol-none` | stripe-clone | 14 | gpt-5-6-sol | 0.4 | 27 | 28 | 15 | 0.21 | 0.31 | 1.01e+16 | 2.00e+11 |
| `agen-swemar-wasmsimd-dsv4pro` | wasm-simd | 12 | deepseek-v4-pro-0813 | 35.3 | 189 | 371 | 186 | 3.87 | 0.16 | 1.77e+17 | 4.09e+12 |
| `agen-swemar-wasmsimd-fable5` | wasm-simd | 12 | claude-fable-5 | 5.3 | 44 | 243 | 121 | 1.72 | 0.12 | 1.98e+17 | 4.58e+12 |
| `agen-swemar-wasmsimd-fable51-max` | wasm-simd | 12 | claude-fable-5-1 | 7.1 | 52 | 273 | 138 | 1.94 | 0.19 | 2.41e+17 | 5.58e+12 |
| `agen-swemar-wasmsimd-glm52` | wasm-simd | 12 | glm-5.2 | 27.8 | 279 | 199 | 100 | 2.23 | 0.33 | 5.15e+16 | 1.19e+12 |
| `agen-swemar-wasmsimd-glm53-high` | wasm-simd | 12 | glm-5.3 | 19.0 | 142 | 267 | 142 | 3.17 | 0.23 | 8.92e+16 | 2.06e+12 |
| `agen-swemar-wasmsimd-glm53-low` | wasm-simd | 12 | glm-5.3 | 15.2 | 116 | 263 | 134 | 2.98 | 0.20 | 8.39e+16 | 1.94e+12 |
| `agen-swemar-wasmsimd-glm53-max` | wasm-simd | 12 | glm-5.3 | 25.2 | 171 | 299 | 156 | 3.48 | 0.26 | 1.07e+17 | 2.48e+12 |
| `agen-swemar-wasmsimd-glm53flash-max` | wasm-simd | 12 | glm-5.3-flash | 17.6 | 172 | 205 | 104 | 2.98 | 0.37 | 2.94e+16 | 6.81e+11 |
| `agen-swemar-wasmsimd-grok45` | wasm-simd | 12 | grok-4-5 | 4.5 | 125 | 72 | 36 | 0.60 | 0.80 | 2.31e+16 | 5.35e+11 |
| `agen-swemar-wasmsimd-grok46-high` | wasm-simd | 12 | grok-4-6 | 4.8 | 79 | 123 | 61 | 1.01 | 0.34 | 4.92e+16 | 1.14e+12 |
| `agen-swemar-wasmsimd-kimik3` | wasm-simd | 12 | kimi-k3 | 14.2 | 99 | 274 | 139 | 0.46 | 0.18 | 8.30e+16 | 1.92e+12 |
| `agen-swemar-wasmsimd-luna-high` | wasm-simd | 12 | gpt-5-6-luna | 35.0 | 347 | 204 | 104 | 3.86 | 0.25 | 1.59e+16 | 3.67e+11 |
| `agen-swemar-wasmsimd-luna-max` | wasm-simd | 12 | gpt-5-6-luna | 22.3 | 560 | 108 | 72 | 2.67 | 0.63 | 6.31e+15 | 1.46e+11 |
| `agen-swemar-wasmsimd-luna-xhigh` | wasm-simd | 12 | gpt-5-6-luna | 26.4 | 337 | 157 | 80 | 2.96 | 0.27 | 9.97e+15 | 2.31e+11 |
| `agen-swemar-wasmsimd-muse13-max` | wasm-simd | 12 | muse-spark-1-3 | 39.8 | 302 | 257 | 131 | 2.14 | 0.07 | 1.62e+17 | 3.74e+12 |
| `agen-swemar-wasmsimd-muse13-xhigh` | wasm-simd | 12 | muse-spark-1-3 | 40.8 | 304 | 266 | 134 | 2.20 | 0.08 | 1.70e+17 | 3.94e+12 |
| `agen-swemar-wasmsimd-opus48` | wasm-simd | 12 | claude-opus-4-8 | 13.6 | 80 | 337 | 169 | 2.77 | 0.11 | 2.54e+17 | 5.89e+12 |
| `agen-swemar-wasmsimd-opus5` | wasm-simd | 12 | claude-opus-5 | 16.5 | 86 | 374 | 189 | 3.09 | 0.12 | 3.06e+17 | 7.08e+12 |
| `agen-swemar-wasmsimd-opus5-high` | wasm-simd | 12 | claude-opus-5 | 5.2 | 40 | 257 | 129 | 2.11 | 0.11 | 1.60e+17 | 3.70e+12 |
| `agen-swemar-wasmsimd-opus5-low` | wasm-simd | 12 | claude-opus-5 | 4.4 | 42 | 207 | 104 | 1.70 | 0.13 | 1.12e+17 | 2.59e+12 |
| `agen-swemar-wasmsimd-opus5-medium` | wasm-simd | 12 | claude-opus-5 | 5.3 | 43 | 241 | 122 | 2.00 | 0.12 | 1.45e+17 | 3.35e+12 |
| `agen-swemar-wasmsimd-opus5-xhigh` | wasm-simd | 12 | claude-opus-5 | 5.3 | 41 | 260 | 130 | 2.14 | 0.12 | 1.63e+17 | 3.78e+12 |
| `agen-swemar-wasmsimd-sol-high` | wasm-simd | 12 | gpt-5-6-sol | 4.7 | 70 | 135 | 70 | 0.99 | 0.08 | 8.06e+16 | 1.87e+12 |
| `agen-swemar-wasmsimd-sol-low` | wasm-simd | 12 | gpt-5-6-sol | 5.0 | 78 | 131 | 67 | 0.94 | 0.11 | 7.61e+16 | 1.76e+12 |
| `agen-swemar-wasmsimd-sol-max` | wasm-simd | 12 | gpt-5-6-sol | 5.2 | 85 | 129 | 68 | 0.95 | 0.10 | 7.56e+16 | 1.75e+12 |
| `agen-swemar-wasmsimd-sol-medium` | wasm-simd | 12 | gpt-5-6-sol | 4.5 | 70 | 130 | 68 | 0.95 | 0.08 | 7.59e+16 | 1.76e+12 |
| `agen-swemar-wasmsimd-sol-xhigh` | wasm-simd | 12 | gpt-5-6-sol | 4.4 | 86 | 115 | 61 | 0.86 | 0.10 | 6.42e+16 | 1.49e+12 |
| `agen-swemar-wasmsimd-sonnet5-high` | wasm-simd | 12 | claude-sonnet-5 | 25.3 | 126 | 400 | 201 | 3.30 | 0.11 | 3.44e+17 | 7.97e+12 |
| `agen-swemar-wasmsimd-sonnet5-low` | wasm-simd | 12 | claude-sonnet-5 | 19.2 | 117 | 329 | 165 | 2.71 | 0.13 | 2.44e+17 | 5.65e+12 |
| `agen-swemar-wasmsimd-sonnet5-max` | wasm-simd | 12 | claude-sonnet-5 | 61.4 | 202 | 588 | 298 | 4.89 | 0.10 | 6.92e+17 | 1.60e+13 |
| `agen-swemar-wasmsimd-sonnet5-medium` | wasm-simd | 12 | claude-sonnet-5 | 20.0 | 107 | 370 | 186 | 3.04 | 0.11 | 2.99e+17 | 6.92e+12 |
| `agen-swemar-wasmsimd-sonnet5-xhigh` | wasm-simd | 12 | claude-sonnet-5 | 24.3 | 110 | 437 | 220 | 3.60 | 0.10 | 4.02e+17 | 9.31e+12 |
| `agen-swemar-wasmsimd-terra-max` | wasm-simd | 12 | gpt-5-6-terra | 14.2 | 127 | 225 | 113 | 3.20 | 0.09 | 3.77e+16 | 8.73e+11 |
| `agen-swemar-wasmsimd-terra-xhigh` | wasm-simd | 12 | gpt-5-6-terra | 14.2 | 135 | 210 | 107 | 3.01 | 0.09 | 3.37e+16 | 7.79e+11 |
| `agen-swemar-zstd-astra-max` | zstd-decoder | 12 | gpt-6-astra | 1.4 | 72 | 38 | 20 | 0.22 | 0.15 | 2.81e+16 | 6.50e+11 |
| `agen-swemar-zstd-astra-xhigh` | zstd-decoder | 12 | gpt-6-astra | 1.4 | 68 | 40 | 20 | 0.23 | 1.00 | 2.92e+16 | 6.76e+11 |
| `agen-swemar-zstd-fable5` | zstd-decoder | 12 | claude-fable-5 | 7.2 | 49 | 282 | 143 | 2.03 | 0.08 | 2.56e+17 | 5.93e+12 |
| `agen-swemar-zstd-fable51-max` | zstd-decoder | 12 | claude-fable-5-1 | 6.6 | 36 | 366 | 185 | 2.62 | 0.08 | 3.97e+17 | 9.19e+12 |
| `agen-swemar-zstd-glm52` | zstd-decoder | 12 | glm-5.2 | 25.7 | 279 | 184 | 93 | 2.07 | 0.35 | 4.52e+16 | 1.05e+12 |
| `agen-swemar-zstd-glm53-high` | zstd-decoder | 12 | glm-5.3 | 76.7 | 301 | 495 | 254 | 5.65 | 0.17 | 2.63e+17 | 6.09e+12 |
| `agen-swemar-zstd-glm53-low` | zstd-decoder | 12 | glm-5.3 | 49.2 | 252 | 358 | 191 | 4.26 | 0.16 | 1.50e+17 | 3.48e+12 |
| `agen-swemar-zstd-glm53-max` | zstd-decoder | 12 | glm-5.3 | 63.2 | 271 | 476 | 240 | 5.35 | 0.18 | 2.42e+17 | 5.60e+12 |
| `agen-swemar-zstd-glm53flash-max` | zstd-decoder | 12 | glm-5.3-flash | 36.7 | 322 | 228 | 114 | 3.29 | 0.40 | 3.52e+16 | 8.14e+11 |
| `agen-swemar-zstd-grok46-high` | zstd-decoder | 12 | grok-4-6 | 7.1 | 81 | 165 | 86 | 1.42 | 0.19 | 7.99e+16 | 1.85e+12 |
| `agen-swemar-zstd-kimik3` | zstd-decoder | 12 | kimi-k3 | 102.1 | 290 | 612 | 329 | 1.09 | 0.15 | 2.66e+17 | 6.15e+12 |
| `agen-swemar-zstd-luna-max` | zstd-decoder | 12 | gpt-5-6-luna | 98.6 | 1228 | 175 | 95 | 3.51 | 0.93 | 1.26e+16 | 2.91e+11 |
| `agen-swemar-zstd-muse13-max` | zstd-decoder | 12 | muse-spark-1-3 | 53.6 | 413 | 256 | 129 | 2.11 | 0.21 | 1.59e+17 | 3.69e+12 |
| `agen-swemar-zstd-muse13-xhigh` | zstd-decoder | 12 | muse-spark-1-3 | 74.3 | 623 | 235 | 118 | 1.93 | 0.31 | 1.37e+17 | 3.18e+12 |
| `agen-swemar-zstd-opus48` | zstd-decoder | 12 | claude-opus-4-8 | 18.5 | 72 | 494 | 255 | 4.17 | 0.06 | 5.11e+17 | 1.18e+13 |
| `agen-swemar-zstd-opus5` | zstd-decoder | 12 | claude-opus-5 | 23.3 | 100 | 464 | 233 | 3.82 | 0.11 | 4.47e+17 | 1.04e+13 |
| `agen-swemar-zstd-opus5-high` | zstd-decoder | 12 | claude-opus-5 | 15.1 | 77 | 387 | 195 | 3.20 | 0.12 | 3.25e+17 | 7.52e+12 |
| `agen-swemar-zstd-opus5-low` | zstd-decoder | 12 | claude-opus-5 | 7.8 | 69 | 217 | 111 | 1.81 | 0.13 | 1.22e+17 | 2.82e+12 |
| `agen-swemar-zstd-opus5-medium` | zstd-decoder | 12 | claude-opus-5 | 11.0 | 75 | 280 | 143 | 2.35 | 0.13 | 1.87e+17 | 4.33e+12 |
| `agen-swemar-zstd-opus5-xhigh` | zstd-decoder | 12 | claude-opus-5 | 19.0 | 89 | 422 | 212 | 3.48 | 0.11 | 3.78e+17 | 8.75e+12 |
| `agen-swemar-zstd-sol-high` | zstd-decoder | 12 | gpt-5-6-sol | 4.2 | 97 | 85 | 44 | 0.63 | 0.17 | 4.17e+16 | 9.65e+11 |
| `agen-swemar-zstd-sol-max` | zstd-decoder | 12 | gpt-5-6-sol | 7.1 | 106 | 136 | 70 | 0.99 | 0.11 | 8.11e+16 | 1.88e+12 |
| `agen-swemar-zstd-sol-xhigh` | zstd-decoder | 12 | gpt-5-6-sol | 5.7 | 99 | 115 | 62 | 0.87 | 0.12 | 6.45e+16 | 1.49e+12 |
| `agen-swemar-zstd-sonnet5-high` | zstd-decoder | 12 | claude-sonnet-5 | 57.0 | 193 | 538 | 284 | 4.66 | 0.07 | 6.09e+17 | 1.41e+13 |
| `agen-swemar-zstd-sonnet5-low` | zstd-decoder | 12 | claude-sonnet-5 | 132.3 | 363 | 607 | 351 | 5.75 | 0.10 | 8.19e+17 | 1.90e+13 |
| `agen-swemar-zstd-sonnet5-max` | zstd-decoder | 12 | claude-sonnet-5 | 75.1 | 212 | 678 | 353 | 5.78 | 0.07 | 9.19e+17 | 2.13e+13 |
| `agen-swemar-zstd-sonnet5-medium` | zstd-decoder | 12 | claude-sonnet-5 | 95.3 | 295 | 600 | 316 | 5.17 | 0.08 | 7.41e+17 | 1.71e+13 |
| `agen-swemar-zstd-sonnet5-xhigh` | zstd-decoder | 12 | claude-sonnet-5 | 99.6 | 268 | 634 | 360 | 5.90 | 0.07 | 8.75e+17 | 2.03e+13 |
| `agen-swemar-zstd-terra-max` | zstd-decoder | 12 | gpt-5-6-terra | 19.0 | 186 | 192 | 98 | 2.76 | 0.14 | 2.89e+16 | 6.69e+11 |
| `agen-swemar-jaxtorch-astra-low` | jax-pytorch-rewrite | 8 | gpt-6-astra | 20.9 | 369 | 110 | 58 | 0.65 | 0.87 | 1.09e+17 | 3.79e+12 |
| `agen-swemar-jaxtorch-astra-max` | jax-pytorch-rewrite | 8 | gpt-6-astra | 16.4 | 408 | 82 | 42 | 0.47 | 0.72 | 7.29e+16 | 2.53e+12 |
| `agen-swemar-jaxtorch-astra-xhigh` | jax-pytorch-rewrite | 8 | gpt-6-astra | 15.5 | 332 | 92 | 49 | 0.56 | 0.71 | 8.60e+16 | 2.98e+12 |
| `agen-swemar-jaxtorch-fable5` | jax-pytorch-rewrite | 8 | claude-fable-5 | 12.5 | 84 | 296 | 149 | 2.10 | 0.15 | 2.76e+17 | 9.58e+12 |
| `agen-swemar-jaxtorch-fable51-max` | jax-pytorch-rewrite | 8 | claude-fable-5-1 | 17.3 | 60 | 553 | 279 | 3.95 | 0.15 | 8.21e+17 | 2.85e+13 |
| `agen-swemar-jaxtorch-gem37flash` | jax-pytorch-rewrite | 8 | gemini-3-7-flash | 27.9 | 164 | 337 | 172 | 3.84 | 0.22 | 1.31e+17 | 4.53e+12 |
| `agen-swemar-jaxtorch-glm53-high` | jax-pytorch-rewrite | 8 | glm-5.3 | 23.6 | 164 | 288 | 145 | 3.23 | 0.25 | 9.76e+16 | 3.39e+12 |
| `agen-swemar-jaxtorch-glm53-max` | jax-pytorch-rewrite | 8 | glm-5.3 | 35.7 | 194 | 368 | 185 | 4.12 | 0.25 | 1.50e+17 | 5.22e+12 |
| `agen-swemar-jaxtorch-glm53flash-max` | jax-pytorch-rewrite | 8 | glm-5.3-flash | 22.5 | 215 | 209 | 105 | 3.01 | 0.39 | 3.01e+16 | 1.05e+12 |
| `agen-swemar-jaxtorch-grok45` | jax-pytorch-rewrite | 8 | grok-4-5 | 7.4 | 206 | 70 | 37 | 0.60 | 0.60 | 2.24e+16 | 7.79e+11 |
| `agen-swemar-jaxtorch-grok46-high` | jax-pytorch-rewrite | 8 | grok-4-6 | 7.8 | 133 | 116 | 59 | 0.97 | 0.29 | 4.58e+16 | 1.59e+12 |
| `agen-swemar-jaxtorch-kimik3` | jax-pytorch-rewrite | 8 | kimi-k3 | 15.7 | 107 | 292 | 148 | 0.49 | 0.23 | 9.07e+16 | 3.15e+12 |
| `agen-swemar-jaxtorch-muse13-max` | jax-pytorch-rewrite | 8 | muse-spark-1-3 | 25.8 | 276 | 186 | 94 | 1.54 | 0.18 | 9.42e+16 | 3.27e+12 |
| `agen-swemar-jaxtorch-muse13-xhigh` | jax-pytorch-rewrite | 8 | muse-spark-1-3 | 24.3 | 251 | 192 | 97 | 1.58 | 0.14 | 9.94e+16 | 3.45e+12 |
| `agen-swemar-jaxtorch-opus48` | jax-pytorch-rewrite | 8 | claude-opus-4-8 | 19.6 | 93 | 421 | 212 | 3.48 | 0.09 | 3.78e+17 | 1.31e+13 |
| `agen-swemar-jaxtorch-opus5` | jax-pytorch-rewrite | 8 | claude-opus-5 | 41.4 | 148 | 557 | 281 | 4.60 | 0.15 | 6.24e+17 | 2.17e+13 |
| `agen-swemar-jaxtorch-opus5-high` | jax-pytorch-rewrite | 8 | claude-opus-5 | 23.9 | 115 | 412 | 207 | 3.38 | 0.15 | 3.61e+17 | 1.25e+13 |
| `agen-swemar-jaxtorch-opus5-low` | jax-pytorch-rewrite | 8 | claude-opus-5 | 9.5 | 80 | 238 | 120 | 1.97 | 0.15 | 1.41e+17 | 4.91e+12 |
| `agen-swemar-jaxtorch-opus5-medium` | jax-pytorch-rewrite | 8 | claude-opus-5 | 18.0 | 107 | 332 | 167 | 2.74 | 0.15 | 2.49e+17 | 8.64e+12 |
| `agen-swemar-jaxtorch-opus5-xhigh` | jax-pytorch-rewrite | 8 | claude-opus-5 | 28.4 | 121 | 467 | 234 | 3.83 | 0.15 | 4.51e+17 | 1.57e+13 |
| `agen-swemar-jaxtorch-sol-high` | jax-pytorch-rewrite | 8 | gpt-5-6-sol | 5.0 | 85 | 114 | 59 | 0.83 | 0.18 | 6.27e+16 | 2.18e+12 |
| `agen-swemar-jaxtorch-sol-low` | jax-pytorch-rewrite | 8 | gpt-5-6-sol | 5.1 | 105 | 94 | 48 | 0.68 | 0.18 | 4.71e+16 | 1.64e+12 |
| `agen-swemar-jaxtorch-sol-max` | jax-pytorch-rewrite | 8 | gpt-5-6-sol | 9.0 | 144 | 121 | 63 | 0.89 | 0.21 | 6.87e+16 | 2.39e+12 |
| `agen-swemar-jaxtorch-sol-medium` | jax-pytorch-rewrite | 8 | gpt-5-6-sol | 8.8 | 144 | 116 | 59 | 0.84 | 0.19 | 6.39e+16 | 2.22e+12 |
| `agen-swemar-jaxtorch-sol-xhigh` | jax-pytorch-rewrite | 8 | gpt-5-6-sol | 8.6 | 133 | 125 | 66 | 0.93 | 0.18 | 7.25e+16 | 2.52e+12 |
| `agen-swemar-jaxtorch-sonnet5-high` | jax-pytorch-rewrite | 8 | claude-sonnet-5 | 21.9 | 113 | 388 | 195 | 3.20 | 0.07 | 3.25e+17 | 1.13e+13 |
| `agen-swemar-jaxtorch-sonnet5-max` | jax-pytorch-rewrite | 8 | claude-sonnet-5 | 54.4 | 181 | 604 | 303 | 4.97 | 0.08 | 7.20e+17 | 2.50e+13 |
| `agen-swemar-jaxtorch-sonnet5-medium` | jax-pytorch-rewrite | 8 | claude-sonnet-5 | 14.1 | 86 | 319 | 164 | 2.68 | 0.08 | 2.35e+17 | 8.15e+12 |
| `agen-swemar-jaxtorch-sonnet5-xhigh` | jax-pytorch-rewrite | 8 | claude-sonnet-5 | 32.1 | 138 | 450 | 229 | 3.76 | 0.07 | 4.28e+17 | 1.49e+13 |
| `agen-swemar-jaxtorch-terra-high` | jax-pytorch-rewrite | 8 | gpt-5-6-terra | 5.3 | 102 | 102 | 52 | 1.46 | 0.23 | 1.00e+16 | 3.47e+11 |
| `agen-swemar-jaxtorch-terra-max` | jax-pytorch-rewrite | 8 | gpt-5-6-terra | 15.8 | 195 | 159 | 81 | 2.29 | 0.25 | 2.09e+16 | 7.26e+11 |
| `agen-swemar-jaxtorch-terra-xhigh` | jax-pytorch-rewrite | 8 | gpt-5-6-terra | 8.8 | 134 | 129 | 68 | 1.91 | 0.25 | 1.50e+16 | 5.22e+11 |
| `agen-swemar-vliw-astra-high` | vliw-kernel-optimization | 8 | gpt-6-astra | 0.4 | 33 | 21 | 11 | 0.12 | 0.66 | 1.44e+16 | 4.99e+11 |
| `agen-swemar-vliw-astra-low` | vliw-kernel-optimization | 8 | gpt-6-astra | 0.4 | 32 | 26 | 14 | 0.16 | 0.65 | 1.79e+16 | 6.21e+11 |
| `agen-swemar-vliw-astra-max` | vliw-kernel-optimization | 8 | gpt-6-astra | 0.5 | 39 | 25 | 13 | 0.15 | 0.35 | 1.71e+16 | 5.94e+11 |
| `agen-swemar-vliw-astra-medium` | vliw-kernel-optimization | 8 | gpt-6-astra | 0.3 | 32 | 20 | 10 | 0.11 | 0.79 | 1.33e+16 | 4.61e+11 |
| `agen-swemar-vliw-astra-xhigh` | vliw-kernel-optimization | 8 | gpt-6-astra | 0.4 | 36 | 20 | 10 | 0.12 | 0.75 | 1.33e+16 | 4.63e+11 |
| `agen-swemar-vliw-fable5` | vliw-kernel-optimization | 8 | claude-fable-5 | 19.2 | 86 | 436 | 222 | 3.14 | 0.07 | 5.42e+17 | 1.88e+13 |
| `agen-swemar-vliw-fable51-max` | vliw-kernel-optimization | 8 | claude-fable-5-1 | 21.5 | 78 | 544 | 273 | 3.86 | 0.08 | 7.94e+17 | 2.76e+13 |
| `agen-swemar-vliw-glm53-high` | vliw-kernel-optimization | 8 | glm-5.3 | 43.9 | 169 | 518 | 260 | 5.80 | 0.12 | 2.82e+17 | 9.79e+12 |
| `agen-swemar-vliw-glm53-low` | vliw-kernel-optimization | 8 | glm-5.3 | 45.3 | 190 | 446 | 233 | 5.19 | 0.14 | 2.21e+17 | 7.67e+12 |
| `agen-swemar-vliw-glm53-max` | vliw-kernel-optimization | 8 | glm-5.3 | 40.2 | 154 | 510 | 261 | 5.81 | 0.10 | 2.78e+17 | 9.65e+12 |
| `agen-swemar-vliw-glm53flash-max` | vliw-kernel-optimization | 8 | glm-5.3-flash | 30.2 | 284 | 212 | 106 | 3.06 | 0.34 | 3.10e+16 | 1.08e+12 |
| `agen-swemar-vliw-grok46-high` | vliw-kernel-optimization | 8 | grok-4-6 | 33.7 | 232 | 247 | 133 | 2.17 | 0.25 | 1.57e+17 | 5.44e+12 |
| `agen-swemar-vliw-kimik3` | vliw-kernel-optimization | 8 | kimi-k3 | 82.5 | 255 | 622 | 322 | 1.06 | 0.14 | 2.67e+17 | 9.27e+12 |
| `agen-swemar-vliw-luna-max` | vliw-kernel-optimization | 8 | gpt-5-6-luna | 165.1 | 1411 | 456 | 575 | 21.27 | 0.78 | 1.62e+17 | 5.64e+12 |
| `agen-swemar-vliw-opus48` | vliw-kernel-optimization | 8 | claude-opus-4-8 | 57.8 | 145 | 707 | 391 | 6.40 | 0.06 | 1.05e+18 | 3.63e+13 |
| `agen-swemar-vliw-opus5` | vliw-kernel-optimization | 8 | claude-opus-5 | 35.1 | 108 | 623 | 324 | 5.31 | 0.07 | 7.86e+17 | 2.73e+13 |
| `agen-swemar-vliw-opus5-high` | vliw-kernel-optimization | 8 | claude-opus-5 | 22.2 | 86 | 507 | 260 | 4.26 | 0.06 | 5.33e+17 | 1.85e+13 |
| `agen-swemar-vliw-opus5-low` | vliw-kernel-optimization | 8 | claude-opus-5 | 9.1 | 55 | 296 | 159 | 2.60 | 0.06 | 2.13e+17 | 7.41e+12 |
| `agen-swemar-vliw-opus5-medium` | vliw-kernel-optimization | 8 | claude-opus-5 | 23.5 | 101 | 439 | 228 | 3.73 | 0.07 | 4.16e+17 | 1.44e+13 |
| `agen-swemar-vliw-opus5-xhigh` | vliw-kernel-optimization | 8 | claude-opus-5 | 24.7 | 92 | 538 | 271 | 4.45 | 0.06 | 5.86e+17 | 2.03e+13 |
| `agen-swemar-vliw-sol-high` | vliw-kernel-optimization | 8 | gpt-5-6-sol | 13.4 | 883 | 105 | 68 | 0.96 | 0.94 | 6.19e+16 | 2.15e+12 |
| `agen-swemar-vliw-sol-max` | vliw-kernel-optimization | 8 | gpt-5-6-sol | 3.5 | 77 | 85 | 46 | 0.65 | 0.21 | 4.23e+16 | 1.47e+12 |
| `agen-swemar-vliw-sol-medium` | vliw-kernel-optimization | 8 | gpt-5-6-sol | 22.3 | 269 | 129 | 76 | 1.07 | 0.32 | 8.03e+16 | 2.79e+12 |
| `agen-swemar-vliw-sol-xhigh` | vliw-kernel-optimization | 8 | gpt-5-6-sol | 3.5 | 88 | 78 | 40 | 0.57 | 0.22 | 3.65e+16 | 1.27e+12 |
| `agen-swemar-vliw-sonnet5-xhigh` | vliw-kernel-optimization | 8 | claude-sonnet-5 | 323.7 | 614 | 1067 | 535 | 8.76 | 0.13 | 2.08e+18 | 7.24e+13 |
| `agen-swemar-vliw-terra-max` | vliw-kernel-optimization | 8 | gpt-5-6-terra | 46.5 | 355 | 251 | 129 | 3.65 | 0.42 | 4.66e+16 | 1.62e+12 |
| `agen-swemar-embedeval-astra-high` | embedding-eval | 4 | gpt-6-astra | 2.8 | 115 | 48 | 25 | 0.28 | 0.37 | 3.69e+16 | 2.56e+12 |
| `agen-swemar-embedeval-astra-low` | embedding-eval | 4 | gpt-6-astra | 2.5 | 108 | 46 | 23 | 0.26 | 0.80 | 3.49e+16 | 2.42e+12 |
| `agen-swemar-embedeval-astra-max` | embedding-eval | 4 | gpt-6-astra | 3.3 | 147 | 45 | 23 | 0.26 | 0.46 | 3.40e+16 | 2.36e+12 |
| `agen-swemar-embedeval-astra-medium` | embedding-eval | 4 | gpt-6-astra | 2.7 | 131 | 42 | 22 | 0.24 | 0.76 | 3.13e+16 | 2.17e+12 |
| `agen-swemar-embedeval-astra-xhigh` | embedding-eval | 4 | gpt-6-astra | 2.6 | 124 | 41 | 21 | 0.24 | 0.36 | 3.08e+16 | 2.14e+12 |
| `agen-swemar-embedeval-fable5` | embedding-eval | 4 | claude-fable-5 | 6.3 | 50 | 248 | 125 | 1.76 | 0.07 | 2.05e+17 | 1.43e+13 |
| `agen-swemar-embedeval-fable51-max` | embedding-eval | 4 | claude-fable-5-1 | 4.6 | 37 | 245 | 123 | 1.74 | 0.07 | 2.01e+17 | 1.40e+13 |
| `agen-swemar-embedeval-gem37flash` | embedding-eval | 4 | gemini-3-7-flash | 6.9 | 91 | 149 | 80 | 1.78 | 0.15 | 3.32e+16 | 2.30e+12 |
| `agen-swemar-embedeval-glm52` | embedding-eval | 4 | glm-5.2 | 8.3 | 90 | 188 | 95 | 2.12 | 0.13 | 4.71e+16 | 3.27e+12 |
| `agen-swemar-embedeval-glm53-high` | embedding-eval | 4 | glm-5.3 | 3.5 | 50 | 137 | 69 | 1.54 | 0.10 | 2.79e+16 | 1.94e+12 |
| `agen-swemar-embedeval-glm53-max` | embedding-eval | 4 | glm-5.3 | 5.5 | 58 | 187 | 94 | 2.08 | 0.10 | 4.60e+16 | 3.20e+12 |
| `agen-swemar-embedeval-glm53flash-max` | embedding-eval | 4 | glm-5.3-flash | 7.1 | 81 | 173 | 87 | 2.51 | 0.13 | 2.20e+16 | 1.52e+12 |
| `agen-swemar-embedeval-grok45` | embedding-eval | 4 | grok-4-5 | 2.8 | 107 | 50 | 26 | 0.42 | 0.37 | 1.41e+16 | 9.79e+11 |
| `agen-swemar-embedeval-grok46-high` | embedding-eval | 4 | grok-4-6 | 4.2 | 71 | 118 | 60 | 0.98 | 0.13 | 4.69e+16 | 3.25e+12 |
| `agen-swemar-embedeval-kimik3` | embedding-eval | 4 | kimi-k3 | 4.7 | 57 | 163 | 82 | 0.27 | 0.11 | 4.30e+16 | 2.98e+12 |
| `agen-swemar-embedeval-luna-high` | embedding-eval | 4 | gpt-5-6-luna | 13.5 | 190 | 132 | 68 | 2.51 | 0.13 | 7.40e+15 | 5.14e+11 |
| `agen-swemar-embedeval-luna-max` | embedding-eval | 4 | gpt-5-6-luna | 20.4 | 231 | 171 | 92 | 3.42 | 0.19 | 1.21e+16 | 8.41e+11 |
| `agen-swemar-embedeval-luna-xhigh` | embedding-eval | 4 | gpt-5-6-luna | 9.6 | 125 | 151 | 77 | 2.85 | 0.11 | 9.32e+15 | 6.47e+11 |
| `agen-swemar-embedeval-muse13-max` | embedding-eval | 4 | muse-spark-1-3 | 3.6 | 89 | 79 | 40 | 0.66 | 0.11 | 2.63e+16 | 1.83e+12 |
| `agen-swemar-embedeval-muse13-xhigh` | embedding-eval | 4 | muse-spark-1-3 | 4.8 | 102 | 93 | 47 | 0.78 | 0.11 | 3.32e+16 | 2.31e+12 |
| `agen-swemar-embedeval-opus48` | embedding-eval | 4 | claude-opus-4-8 | 7.3 | 53 | 274 | 138 | 2.26 | 0.06 | 1.79e+17 | 1.24e+13 |
| `agen-swemar-embedeval-opus5` | embedding-eval | 4 | claude-opus-5 | 9.0 | 64 | 275 | 139 | 2.28 | 0.07 | 1.81e+17 | 1.26e+13 |
| `agen-swemar-embedeval-opus5-high` | embedding-eval | 4 | claude-opus-5 | 4.3 | 44 | 192 | 96 | 1.58 | 0.06 | 9.89e+16 | 6.87e+12 |
| `agen-swemar-embedeval-opus5-low` | embedding-eval | 4 | claude-opus-5 | 2.2 | 36 | 124 | 63 | 1.03 | 0.07 | 5.04e+16 | 3.50e+12 |
| `agen-swemar-embedeval-opus5-medium` | embedding-eval | 4 | claude-opus-5 | 3.4 | 43 | 159 | 80 | 1.31 | 0.06 | 7.37e+16 | 5.12e+12 |
| `agen-swemar-embedeval-sol-high` | embedding-eval | 4 | gpt-5-6-sol | 6.1 | 105 | 113 | 58 | 0.82 | 0.12 | 6.19e+16 | 4.30e+12 |
| `agen-swemar-embedeval-sol-low` | embedding-eval | 4 | gpt-5-6-sol | 7.3 | 158 | 91 | 46 | 0.65 | 0.14 | 4.51e+16 | 3.13e+12 |
| `agen-swemar-embedeval-sol-max` | embedding-eval | 4 | gpt-5-6-sol | 7.5 | 104 | 146 | 75 | 1.06 | 0.10 | 9.03e+16 | 6.27e+12 |
| `agen-swemar-embedeval-sol-medium` | embedding-eval | 4 | gpt-5-6-sol | 5.4 | 107 | 101 | 51 | 0.72 | 0.12 | 5.23e+16 | 3.63e+12 |
| `agen-swemar-embedeval-sol-xhigh` | embedding-eval | 4 | gpt-5-6-sol | 5.7 | 90 | 121 | 63 | 0.88 | 0.11 | 6.84e+16 | 4.75e+12 |
| `agen-swemar-embedeval-sonnet5-high` | embedding-eval | 4 | claude-sonnet-5 | 6.3 | 62 | 201 | 101 | 1.66 | 0.06 | 1.07e+17 | 7.43e+12 |
| `agen-swemar-embedeval-sonnet5-max` | embedding-eval | 4 | claude-sonnet-5 | 16.8 | 99 | 339 | 171 | 2.81 | 0.07 | 2.59e+17 | 1.80e+13 |
| `agen-swemar-embedeval-sonnet5-medium` | embedding-eval | 4 | claude-sonnet-5 | 3.3 | 41 | 160 | 81 | 1.32 | 0.06 | 7.43e+16 | 5.16e+12 |
| `agen-swemar-embedeval-sonnet5-xhigh` | embedding-eval | 4 | claude-sonnet-5 | 8.9 | 80 | 222 | 112 | 1.84 | 0.07 | 1.26e+17 | 8.77e+12 |
| `agen-swemar-embedeval-terra-high` | embedding-eval | 4 | gpt-5-6-terra | 7.1 | 171 | 82 | 42 | 1.18 | 0.21 | 7.13e+15 | 4.95e+11 |
| `agen-swemar-embedeval-terra-max` | embedding-eval | 4 | gpt-5-6-terra | 13.1 | 198 | 132 | 66 | 1.88 | 0.20 | 1.52e+16 | 1.06e+12 |
| `agen-swemar-embedeval-terra-medium` | embedding-eval | 4 | gpt-5-6-terra | 4.5 | 122 | 73 | 37 | 1.03 | 0.16 | 5.93e+15 | 4.12e+11 |
| `agen-swemar-embedeval-terra-xhigh` | embedding-eval | 4 | gpt-5-6-terra | 8.9 | 172 | 101 | 51 | 1.44 | 0.22 | 9.85e+15 | 6.84e+11 |
