# APEX-Agents, Artificial Analysis implementation

*Created 2026-09-13 12:40.*
*Last revised 2026-09-13 17:07 (Revision 4). Revision 1 answered the independent review at `reviews/apex-agents-independent.md`; Revision 2 applied three text corrections; Revision 3 added the criterion-level score for the substantially-below rule; Revision 4 re-checked the baselining correction at the source on Damon's ruling.*

## Summary

Nine candidate rows, one per model, on the 452-task subset of Mercor's APEX-Agents that Artificial Analysis evaluates at 3 repeats per task. Human time is 5,353 s (1.49 h) on every row: the task-weighted mean of the dataset card's three domain estimates over the subset, 1.845 h, rescaled by the ratio between the estimated and measured times for the 96 tasks the paper's baselining study had executed from scratch by experts who had not written them (1.37/1.70). Compute runs **2.6e15 to 1.2e17 FLOPs**, from Artificial Analysis's provider-reported token totals with cache reads removed on the seven rows where the provider caches by default and retained in full on the one row where the published harness cannot cache. Every model is `below`: pass@1 runs 3.1% to 47.1% against rubrics whose author is the professional who would otherwise do the work.

The consequential judgment is the cache treatment, and Revision 1 changed it. Artificial Analysis publishes a `cacheableInput` count for ten of its agentic evaluations and publishes none for APEX-Agents, so the cache structure is transferred from the same model's other runs on the same harness. What the first submission got wrong was bracketing every row between no reuse and full reuse: OpenAI, Google, Moonshot and Z.ai all cache by default, so no reuse is not a live possibility on seven rows, while the published Stirrup harness sets no Anthropic cache breakpoints, so full reuse is not a live possibility on the Anthropic row. Section [The caching construction](#the-caching-construction) sets out the per-row rule.

Two further sources assessed under this brief yield no rows here: Mercor APEX-Accounting fails on both axes, and the Vals Finance Agent pairing named in the brief fails, though a different and better pairing on the same source is buildable. Both dispositions are at [Dispositions](#dispositions).

### What Revisions 1 to 4 changed

| | First submission | Revision 1 |
|---|---|---|
| `ai_attempts` | 452 | 1,356 (452 tasks x 3 repeats) |
| `performance_evidence` | "one run per task" | 3 runs per task, pass@1 aggregated across repeats |
| Criteria per task | 4.06 (480-task figure) | 4.16 in Revision 2, on the export's IB mean |
| Criterion-level score | absent | Mercor-board mean criteria met, added in Revision 3 for six of nine |
| Cache central | Geometric mean of no reuse and full reuse, all nine rows | Per-row rule from provider caching evidence |
| `compute_flops` range | 3.3e15 to 5.3e16 | 2.6e15 to 1.2e17 |
| `gpt-5-5` active parameters | 1.0e11 (family prior) | 1.73e11 (serving ladder) |
| `cacheHitRate` scenario | Applied as s x h x input | Applied as h x input, with the decisive exclusion argument |

`tokens`, `human_time` and every classification other than `ai_attempts` are unchanged. Revision 4 changes no number at all: it re-checked the human-time correction against the paper and the released export after a scouting pass reported it missing, and rewrote one clause of `notes` on all nine rows. See [Revision 4](#revision-4-the-correction-re-checked-at-the-source).

## What the source is

Mercor's APEX-Agents ([arXiv 2601.14242](https://arxiv.org/abs/2601.14242) v3, Vidgen et al.; [dataset card](https://huggingface.co/datasets/mercor/apex-agents), CC-BY 4.0, evaluation only) is 480 tasks across 33 simulated firm worlds, 160 tasks each for investment banking analysts, corporate lawyers and management consultants. Worlds average 166 files. The agent gets a single-turn instruction and a toolbelt over a file system, documents, spreadsheets, PDFs, email, chat, calendar and code execution; web search is off "to keep evaluations reproducible". Rubrics carry 1–10 binary criteria, mean 4.06 over the 480 tasks and 4.16 weighted over the 452-task subset, and a task passes only when every criterion is met. Trajectories are capped at 250 steps and a trajectory that exceeds the cap is scored a failure. 422 tasks want a console answer and 58 want a created or edited file. Tasks were built and cross-reviewed by professionals averaging 12.9 years of experience at firms the paper names.

Artificial Analysis runs its own implementation on its open-source Stirrup harness, three repeats per task, over 452 of the 480 tasks, "excluding two 'worlds' which have dependencies on external APIs (Investment Banking World 244 and Investment Banking World 246)". Both excluded worlds are investment banking, so the subset is 132 IB + 160 law + 160 consulting; 480 − 452 = 28 confirms that the two worlds held 28 tasks between them. Its headline score is pass@1, "the share of tasks where a model fully satisfies the grading rubric", and for a multi-repeat evaluation "pass@1 is calculated by aggregating results across all repeats", so the published score is over 1,356 runs.

The repeat count is the correction Revision 1 turned on. APEX-Agents-AA sits in the Additional Evaluations table, which carries its own repeat column reading 3; the Intelligence Index table, whose agentic entries are 1-repeat, does not contain this benchmark. `ai_attempts` is 1,356 on every row.

**Three boards exist and they do not agree.** Mercor's own leaderboard (Archipelago harness, 480 tasks, 8 runs per task) tops out at 24.0% pass@1 for Gemini 3 Flash; Epoch's `apex_agents_external.csv` carries a third set of numbers across 65 model-configurations; Artificial Analysis tops out at 47.1% on a different model. Different harnesses, different subsets, different model sets. Every row here names the Artificial Analysis board in `source_record`, and no number is mixed across boards.

## Human time

The card publishes an average estimated completion time per job and nothing finer. It also lists "estimated completion time" among the metadata fields of a task record, which the first submission read as a per-task field sitting behind the `auto` gate. **It is not there.** The export carries no per-task time field at all, so the three domain means and the paper's baselining study are not a fallback for a gated number — they are the whole of the published human-time evidence, and clearing the gate would add nothing. The gate was tested and not worked around; that test is recorded in the manifest, but it was never the binding constraint.

| Job | Tasks in the AA subset | Card mean estimate (h) |
|---|---:|---:|
| Investment banking | 132 | 1.36 |
| Corporate law | 160 | 2.40 |
| Management consulting | 160 | 1.69 |

Task-weighted over the subset: (132 × 1.36 + 160 × 2.40 + 160 × 1.69) / 452 = **1.8450 h = 6,642 s**. The same weighting applied to rubric criteria gives (132 × 3.038 + 160 × 4.57 + 160 × 4.68) / 452 = 4.16 per task, using the mean over the 132 retained IB tasks from the export rather than the card's 160-task IB figure of 2.93; that is the number the rows quote. The whole 480-task benchmark averages 1.8167 h by the same arithmetic, which reproduces the card's and the paper's 1.82; the subset is slightly longer because the excluded worlds are in the shortest job. The weighting assumes the 28 excluded IB tasks are typical of IB. They are 6% of the benchmark and 21% of its estimated hours sit in IB, so even a severe assumption — the excluded tasks averaging 1.5x the IB mean — moves the subset mean only to 1.803 h, −2.3%.

**The estimates are expert judgments, and the source measured how far off they are.** Section 3.5 of the paper, v3 verbatim:

> For 20% of the tasks (n=96), experts who had not created or reviewed them independently executed them from scratch. This checks (1) whether the tasks can actually be completed, (2) the fairness of the rubric, and (3) the time estimates provided by the experts. ... For these sample tasks, experts estimated the time to complete the tasks at 1.70 hours (note that the estimate for the whole benchmark is 1.82 hours) whereas the true time was 1.37 hours. This is an over-estimate of 0.45 hours or 33%.

So the quantity the dataset wants — active time a qualified professional takes — was measured on 96 of these tasks. Four readings follow from those numbers and the rows use the first:

| Calibration | Arithmetic | Result |
|---|---|---:|
| Matched-task ratio, used | 1.845 × (1.37 / 1.70) | 5,353 s |
| Paper's v3 headline ratio | 1.845 × (1.37 / 1.82) | 5,000 s |
| Paper's v3 headline difference | (1.845 − 0.45) h | 5,022 s |
| Measured mean, transferred unadjusted | 1.37 h | 4,932 s |
| No calibration | 1.845 h | 6,642 s |

**The paper's own headline is not the right transfer, and the 24% figure is not the paper's.** v3 computes its 0.45 h and 33% against the *benchmark-wide* 1.82 h estimate rather than against the 1.70 h estimate for the same 96 tasks, which mixes the estimation bias with the fact that the sampled tasks were estimated shorter than average. Since the ratio is then applied to a third estimate — the 452-task subset's 1.845 h — the matched-task ratio 1.37/1.70 = 0.806 is the comparison that isolates the bias. Its 24% is a derivation from the paper's 1.70 and 1.37, not a number the paper states in v3. It is what v1 and v2 stated, before the headline was recomputed; `agent-work/sources/apex-agents/apex-agents-paper-extracts.md` records the version difference.

Every reading that uses the measured time falls between 4,932 and 5,454 s, an 11% spread, and the row takes 5,353 s. The unadjusted measured mean is the floor of that band because it ignores the subset being estimated 8.5% longer than the baselined sample. Against the uncalibrated 6,642 s the correction lowers the human number and so makes the AI look relatively worse. The choice within the band is not load-bearing, since 4,932 to 5,454 s is a small spread next to everything else in the row.

**Field classifications.** `human_time_evidence = transferred_timings`: the central rests on recorded timings for 96 tasks of this benchmark, transferred as a ratio onto the 452-task subset. It is not `assumed`, because a timing sample exists and does the work of setting the level; it is not `task_timings`, because the timings cover a different 96-task selection than the row's stated work unit. `human_time_method = estimated`, because the substantive derivation is a judgment-based transfer, which COLUMNS classifies as estimated regardless of the final arithmetic. `human_time_statistic = mean`. `human_time_subset = all` and `human_attempts = 96`: the paper describes no selection among the 96 executions, and the selection rule applies to the donor attempts. `human_skill = expert`: contributors averaged 12.9 years at top-tier firms, and the baselining executions were done by professionals of the same population.

Two limits of the transfer, stated rather than adjusted for. `human_attempts = 96` is not an effective sample for the 452-task mean, and the 96 tasks are not known to lie inside the 452: 20% of 480 is 96, the excluded worlds hold 28 tasks, so up to 6 of the 96 may sit outside the subset. And the transfer crosses a task-length gradient — the baselined tasks are estimated shorter than the benchmark (1.70 against 1.82 h) while the subset is longer (1.845 h) — so it assumes the proportional bias holds across task length rather than an absolute offset. The absolute-offset reading of the same matched numbers gives 1.845 − 0.33 = 1.515 h = 5,454 s, 2% above the ratio reading.

### Revision 4: the correction re-checked at the source

*2026-09-13 17:07.* A later scouting pass (`research/scouting/legal-finance-deep.md`) reported that these rows carry 6,642 s and are about a third too high, and Damon ruled that the baselining correction should be applied. **The rows already carry it.** `human_time` has been 5,353 s since the first submission; 6,642 s appears only as the uncalibrated intermediate in the table above, which is the line the scouting pass read. No number in the rows changes in this revision.

The re-check went back to the paper and the released data rather than to this note. What it establishes:

- **Section 3.5 is the whole of the baselining study.** The paragraph quoted above is all of it, and no appendix extends it: the appendices cover Archipelago, the survey's time tables, the workflow distribution, the agent setup, the model configs, the significance tests and the tools agents used. The paper therefore publishes no count of experts in the baselining arm, no statement of how the execution time was recorded, no split of the measured 1.37 h by domain or by task, and no expert pass rate against the rubrics.
- **The three arXiv versions were re-fetched and match the retained extract.** v1 and v2 read 1.81 h and 24%, v3 reads 1.82 h and 33%, and the sentence carrying 1.70 and 1.37 hours is identical in all three. The matched pair the transfer rests on is stable across versions; only the headline comparator moved.
- **No per-task time exists in the released data.** The 1.1.0 export retained at `agent-work/sources/inbox/apex-agents` carries all 480 task records, and a record's keys are task_id, task_name, world_id, domain, prompt, task_input_files, expected_output, gold_response, gold_response_type and rubric. `world_descriptions.json` and `metadata.json` carry no time field either. There is no measured value for any individual task in the 452-task subset, so a per-task correction is not available at any effort. Revision 2's finding that nothing sits behind the Hugging Face gate is now confirmed against the export itself rather than inferred.
- **No third party adds to it.** Epoch's benchmark page repeats the estimate ("Tasks are estimated to take a human professional 1.8 hours on average") and Mercor's launch post carries no baselining figures.
- **The arithmetic reproduces.** `research/apex-agents/build_rows.py`, re-run from the retained extracts, reproduces `agent-work/derived/apex-agents/calculations.json` field for field, human time at 5,352.5 s among them.

The matched-task ratio stands as the central. It is the only reading that compares an estimate against a measurement over the same tasks, and a proportional bias extrapolates across task length more sensibly than a fixed offset, which would drive the shortest tasks toward zero. Two limits are unchanged and stated above: the transfer rests on a single aggregate pair with no published dispersion, and it assumes the proportional bias holds at the subset's longer task length. The published evidence supports no finer correction than this.

One CSV field moves. `notes` on all nine rows now reads "readings 4932-5454 s" where it read "uncalibrated 6642 s". The uncalibrated figure is what the scouting pass mistook for the row's value, and under Damon's ruling it is not a live reading, so the field carries the band of readings that use the measured time instead: 4,932 s from the measured mean transferred unadjusted, up to 5,454 s from the absolute-offset reading.

## Compute

### What Artificial Analysis publishes

`canonicalEvalTokenCounts.apexAgents` gives four fields per model: `input`, `answer`, `reasoning` and `cacheableInput`. The methodology page states the counts are "the token counts reported by each model's API provider where available". Output is `answer + reasoning`: both are generated positions and both are counted.

**The totals are per-repeat normalised, so dividing by 452 gives the per-run figure.** This matters now that the repeat count is 3. AA documents AA-LCR v1.1 as "~100k tokens (measured using cl100k_base tokenizer) of input per question" over 100 questions at 3 repeats; the median `lcr.input` across these nine models divided by 100 is 95,217, and divided by 300 is 31,739. Four further checks agree, with the 1-repeat evaluations fixing the scale: GPQA Diamond (198 × 3) gives 267 input tokens per question, matching HLE's 268 at 1 repeat, against 89 if divided by 594; IFBench (294 × 5) gives 91 per prompt against 18, and 18 tokens is not a prompt. The table is in `agent-work/sources/apex-agents/artificialanalysis-extracts.md`. So `tokens` and `compute_flops` are per task run, `compute_statistic = mean` over runs, and `ai_attempts = 1356`.

**Input is the provider's gross prompt count, including positions served from cache.** Two pieces of evidence, both needed because `DECISIONS.md` flags the OpenAI-versus-Anthropic counter difference as a live hazard. OpenAI documents cached tokens as part of the input count rather than additional to it. And the published Stirrup harness reads `usage.prompt_tokens` (LiteLLM and chat-completions clients) or `usage.input_tokens` (responses client) and subtracts nothing: its `TokenUsage` model has exactly three fields, `input`, `answer` and `reasoning`.

**`cacheableInput` is null for APEX-Agents on all nine models**, and null for every model on the non-agentic evaluations. It is populated on ten other agentic evaluations — analystAgent, automationBench, briefcase, enterpriseOpsGym, gdpval, harveyLab, itBench, tauBanking, terminalbenchV21, terminalbenchV40 — for every model that appears on them. The gap is benchmark-level instrumentation, not evidence that caching was absent: eight of these nine models appear on those evaluations, across 68 model-benchmark pairs whose cacheable share runs 0.675 to 0.991 with a median of 0.953, and the APEX-Agents page's own cost chart breaks cost into input, cache hit, cache write, reasoning and answer components. Only four of the 68 pairs fall below 0.86, and two of those four are gpt-oss-120b (automationBench 0.675, terminalbenchV21 0.776). The ninth model, Claude Opus 4.6, appears on none of them and is handled below.

**`cacheableInput` is eligibility, not service.** Three independent arguments. gpt-oss-120b is 0.96–0.99 cacheable on its other evaluations while its `cacheHitRate` is 0, which cannot both be true of served tokens. The published harness stores no cached-token field at all, so the number cannot be a provider counter it read. And the field's own name says so. It is AA's own offline computation over the trajectory prefix.

### The caching construction

COLUMNS excludes cache reads from the parameter-multiplication term, so the count needs a cache-read share and no source states one for this benchmark. COLUMNS also conditions the fallback: "If cache counts are unavailable, use a documented processing estimate **supported by the implementation evidence**; otherwise state the source-total or full-prefix assumption." The implementation evidence exists, it differs by provider, and Revision 1 uses it. It is set out in full in `agent-work/sources/apex-agents/harness-and-provider-caching.md`.

| Provider | Rows | Default caching | Consequence |
|---|---|---|---|
| OpenAI | gpt-5-4, gpt-5-5, gpt-5-6-terra, gpt-5-6-luna | "Prompt caching is enabled by default for supported OpenAI models", 1,024-token minimum on GPT-5.6+, 30-minute TTL, best-effort | No reuse is not live |
| Google | gemini-3-5-flash | "Implicit caching is enabled by default for all Gemini 2.5 and newer models", 4,096-token minimum | No reuse is not live |
| Moonshot | kimi-k3 | "Context Caching is automatically enabled for all model requests" | No reuse is not live |
| Z.ai | glm-5-2 | "Implicit caching ... without manual configuration"; its published $0.26 cached against $1.40 input matches AA's price fields exactly | No reuse is not live |
| Anthropic | claude-opus-4-6 | Explicit only: "You must actively add `cache_control` parameters — nothing is cached without them" | Full reuse is not live |
| gpt-oss-120b serving path | gpt-oss-120b | Not established; AA names no provider | Both branches stay live |

Three rules follow.

**Seven rows, provider caches by default.** The bracket is on the achieved share of the eligible prefix, not on whether caching happened. Lower edge of compute: every eligible token served, cache reads = s × input, with s the median cacheable share AA measures for that model across the ten instrumented evaluations. Upper edge: the eligible prefix served at a floor rate of 0.60, cache reads = 0.60 × s × input. The central is the geometric mean of the two counted totals. The floor is inverted from the weakest provider-default result in Lumer et al.'s agentic caching study — Gemini 2.5 Pro saving 38.3% of cost under Full Context caching, which at a 0.25x cache price and input at roughly 85% of the invoice needs about 60% of input served. The same inversion on GPT-5.2's 79.3% gives about 1.0, so the OpenAI rows' own evidence sits at the ceiling and the floor is conservative for them.

**One row, uncached harness.** `work-apex-agents-opus46` takes gross input as the central, under the `DECISIONS.md` ruling that "when the implementation evidence shows no prompt caching could occur ... the gross input count is the compute actually spent and is the central value". The evidence is the published Stirrup tree: no `cache_control`, `ephemeral`, `cache_read` or `cache_creation` anywhere in it, and Anthropic caches nothing without a breakpoint. This is the same shape as the dataset's Meta RepoProver precedent, and it moves the row 3.7x, from 3.16e16 to 1.17e17 — the largest single change in Revision 1. What would overturn it is evidence that AA's production runs used something other than the published harness; the cached reading is carried as a 0.07x scenario.

**One row, undetermined.** `work-apex-agents-gptoss120b` keeps the original two-branch bracket between no reuse and full eligible reuse, because AA names no serving provider for it. Two weak signals point at the no-reuse edge: its `cacheHitRate` is 0, and its `cacheHitPrice` of 0.125 against a 0.15 input price is a 17% discount rather than the roughly 10x discount a prompt cache carries. Neither is strong enough to move the central alone; the no-reuse edge is 3.84x.

| point_id | Model | Pass@1 % | Input/run | Output/run | s | Rule | Counted/run | Implied cache read | FLOPs/token | compute_flops |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| work-apex-agents-gemini35flash | Gemini 3.5 Flash (high) | 47.1 | 2541811 | 49252 | 0.9603 | provider default | 411442 | 0.858 | 8.0e10 | 3.292e16 |
| work-apex-agents-kimik3 | Kimi K3 (max) | 41.3 | 618196 | 19658 | 0.9493 | provider default | 120715 | 0.837 | 2.08e11 | 2.511e16 |
| work-apex-agents-gpt56terra | GPT-5.6 Terra (max) | 38.9 | 959389 | 17299 | 0.9596 | provider default | 154299 | 0.857 | 4.0e10 | 6.172e15 |
| work-apex-agents-gpt55 | GPT-5.5 (xhigh) | 37.7 | 559044 | 10538 | 0.9447 | provider default | 102352 | 0.836 | 3.46e11 | 3.541e16 |
| work-apex-agents-gpt56luna | GPT-5.6 Luna (max) | 35.8 | 1113342 | 16522 | 0.9670 | provider default | 160578 | 0.871 | 1.6e10 | 2.569e15 |
| work-apex-agents-glm52 | GLM-5.2 (max) | 33.7 | 922412 | 67258 | 0.9388 | provider default | 241125 | 0.812 | 8.0e10 | 1.929e16 |
| work-apex-agents-gpt54 | GPT-5.4 (xhigh) | 33.3 | 776710 | 34205 | 0.9315 | provider default | 181462 | 0.810 | 2.0e11 | 3.629e16 |
| work-apex-agents-opus46 | Claude Opus 4.6 (Adaptive, Max Effort) | 33.0 | 565079 | 19840 | 0.9597 | uncached harness | 584919 | 0.000 | 2.0e11 | 1.170e17 |
| work-apex-agents-gptoss120b | gpt-oss-120b (high) | 3.1 | 1209858 | 25502 | 0.9518 | undetermined | 321874 | 0.755 | 1.02e10 | 3.283e15 |

`tokens_accounting = input_cache_creation_output`: the counted total is fresh input plus cache creation plus output, with cache reads excluded, and cache creation is not separable from fresh input in these counters. `compute_method = params_tokens`. `compute_evidence = derived_assumed_inputs`: the token totals are measured for this work unit, but the cache split and six of nine active-parameter counts are substantial assumed inputs. `compute_statistic = mean`, `compute_subset = all`, `ai_attempts = 1356`.

Claude Opus 4.6 is the one model with no donor of its own: Artificial Analysis instruments none of the evaluations it appears on. Its s is the median of the per-model medians for the other ten Anthropic records in the same payload, 0.9597, recorded in `calculations.json` as `cacheable_share_donor_basis = same_company`. It sets only a scenario on that row, not the central.

### Scenario grid, as multiples of each row's own central

| Model | No reuse | Hit-share floor | Central | Full eligible reuse | Long-horizon donor | Mercor step floor | AA rate direct | AA `cacheHitRate` | Rate > eligible? |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Gemini 3.5 Flash (high) | 6.30 | 2.74 | 1.00 | 0.37 | 0.33 | 0.74 | 0.79 | 0.8921 | no |
| Kimi K3 (max) | 5.28 | 2.37 | 1.00 | 0.42 | 0.31 | 0.67 | 0.29 | 0.9744 | **yes** |
| GPT-5.6 Terra (max) | 6.33 | 2.75 | 1.00 | 0.36 | 0.28 | 0.73 | 0.15 | 0.9934 | **yes** |
| GPT-5.5 (xhigh) | 5.56 | 2.47 | 1.00 | 0.41 | 0.41 | 0.65 | 1.10 | 0.8171 | no |
| GPT-5.6 Luna (max) | 7.04 | 3.01 | 1.00 | 0.33 | 0.24 | 0.80 | 0.15 | 0.9934 | **yes** |
| GLM-5.2 (max) | 4.10 | 1.95 | 1.00 | 0.51 | 0.48 | 0.66 | 0.47 | 0.9500 | **yes** |
| GPT-5.4 (xhigh) | 4.47 | 2.08 | 1.00 | 0.48 | 0.41 | 0.62 | 0.82 | 0.8514 | no |
| Claude Opus 4.6 (Adaptive, Max Effort) | 1.00 | 0.44 | 1.00 | 0.07 | 0.06 | 0.13 | 0.20 | 0.8233 | no |
| gpt-oss-120b (high) | 3.84 | 1.69 | 1.00 | 0.26 | 0.14 | 0.46 | 3.84 | 0.0000 | no |

"No reuse" and "hit-share floor" coincide with the central on the Anthropic and provider-default rows respectively where the rule makes them the bracket edge. "Long-horizon donor" restricts the donor set to harveyLab, briefcase, gdpval and analystAgent, the four instrumented evaluations closest in shape to APEX-Agents; those donors give higher eligible shares, so it sits below full reuse. "Mercor step floor" applies the lowest step-implied eligibility in the next section, 0.900.

### Why `cacheHitRate` does not set the central

The first submission treated this field as the physically motivated point estimate held back only by presentation doubts. That was too generous, and the scenario column also mis-applied it. `cacheHitRate` is a share of input tokens — it pairs with `cacheHitPrice` in a cost model, and Muse Glimmer at exactly 1 and gpt-oss-120b at 0 are coherent only on that reading — so the direct application is cache reads = h × input, which is the "AA rate direct" column above. Four arguments exclude it from the central, in order of force.

1. **For four of the nine it exceeds that model's own eligibility share, which is impossible on the same traffic.** GPT-5.6 Terra 0.9934 against 0.9596, GPT-5.6 Luna 0.9934 against 0.9670, Kimi K3 0.9744 against 0.9493, GLM-5.2 0.9500 against 0.9388. A hit rate cannot exceed the eligible share.
2. **AA's own sentence is the disclaimer.** "When reporting cache hit rates and cost, we combine these token counts with live measurements of the model's typical cache hit rate, rather than relying on the one-off measurement when the evaluation was run." By AA's words it is a model-level typical rate from live traffic, explicitly not a measurement of this evaluation.
3. **It is shared by family and serving path, not measured per model.** Across the 49 retained records, seven OpenAI entries (GPT-6 Astra and its three effort variants, GPT-5.6 Sol, Terra and Luna) carry 0.99339067738 identically; four Claude Opus records carry 0.996663404781368; five Claude Fable records carry 0.994524976; three Gemini Flash generations carry 0.892089776686994.
4. **Round placeholders appear where no measurement is plausible.** GLM-5.2 and both Muse Spark 1.3 records at exactly 0.95, two Qwen3-8-27B records at 0.83, qwen3-8-flash-next at 0.99, Agnes 3.0 Flash at 0.9996, Muse Glimmer at exactly 1, gpt-oss-120b at 0.

Applied directly it would move the rows to 0.15x–1.10x of their centrals, and 3.84x on gpt-oss-120b. Against the first submission's centrals the same direct application ran 0.10x–0.76x.

### Corroboration from Mercor's own step counts

Table 4 of the paper reports mean steps per run on the Archipelago harness for the same 480 tasks. Under the linear-prefix-growth recipe the RLI rows use, a trajectory of N calls has a repeated-prefix share of at least 1 − 2/(N+1); a fixed system-and-world prefix present from the first call pushes the real share higher, so this is a lower bound.

| Model (Mercor run) | Steps | Implied cacheable share, lower bound |
|---|---:|---:|
| Claude Opus 4.5 | 19 | 0.900 |
| Gemini 3 Pro | 24 | 0.920 |
| Grok 4 | 31 | 0.938 |
| GPT-5 | 34 | 0.943 |
| GPT-5.2 | 35 | 0.944 |
| GPT-OSS-120B | 43 | 0.955 |
| Gemini 3 Flash | 54 | 0.964 |
| Kimi K2 Thinking | 92 | 0.979 |

Steps are capped at 250 and an over-cap trajectory is scored a failure, so the top of this range is bounded by the cap rather than by the task. The 0.93–0.97 transferred shares used above sit inside the range, derived independently on this benchmark and on a different harness. The same table cross-checks the token magnitudes: Mercor's gpt-oss-120b run processes 1.60M trajectory tokens per run against Artificial Analysis's 1.21M input tokens per task, and 36,000 completion tokens against 25,502 — the same scale on a different scaffold.

### Cached-context attention

`DECISIONS.md` requires a quantified scenario for the term the 2 × active-parameters convention omits, using `4 · L · d_model · N_context` per processed position. L here counts only layers carrying quadratic attention. Two of the nine models disclose their architecture and are used at their disclosed shapes; the rest are bracketed by tier, anchored on those two. Values are multiples of each row's recorded `compute_flops`, at the mid shape:

| Model | Shape used | 10k context | 20k | 50k | 100k |
|---|---|---:|---:|---:|---:|
| Kimi K3 | disclosed, 24 full-attention layers of 93, d 7168 | 0.03 | 0.07 | 0.17 | 0.33 |
| GPT-5.5 | bracket L 64–96, d 8192–12288 | 0.09 | 0.19 | 0.47 | 0.95 |
| GPT-5.4, Claude Opus 4.6 | bracket L 64–96, d 8192–12288 | 0.16 | 0.33 | 0.82 | 1.64 |
| Gemini 3.5 Flash, GLM-5.2 | bracket L 48–72, d 5120–7168 | 0.18 | 0.37 | 0.92 | 1.84 |
| gpt-oss-120b | disclosed, 18 full-attention layers of 36, d 2880 | 0.20 | 0.41 | 1.02 | 2.03 |
| GPT-5.6 Terra | bracket L 36–56, d 3584–5120 | 0.20 | 0.40 | 1.00 | 2.00 |
| GPT-5.6 Luna | bracket L 28–40, d 2880–4096 | 0.30 | 0.59 | 1.48 | 2.96 |

GPT-5.5 separates from GPT-5.4 and Claude Opus 4.6 only because its coefficient changed to 3.46e11 in Revision 1. Kimi K3's public config is what makes its column small: 69 of its 93 layers are KDA linear-attention layers whose state does not grow with context. The relevant context length is the mean prefix per call, which is input tokens per run divided by the number of calls; at 40 calls that is 14k–64k across these rows, so the 20k–50k columns are the operative ones. The term is one-sided, and it is now added: `research/attention-correction.md` folds it into `compute_flops`, using Kimi K3's disclosed shape and a 90,731-token mean prefix.

## Performance

`performance_vs_human = below` on all nine. Pass@1 runs 3.1% to 47.1%: the share of runs where the model satisfies every binary criterion of a rubric written by the professional whose job the task is, aggregated across the three repeats of each of the 452 tasks. No human was scored on the rubric, so the human arm is an assumed baseline with two supports — the gold outputs are expert-written and pass by construction, and the baselining study had 96 tasks executed from scratch by experts who had not authored them, with problems found in the prompt, rubric or metadata on 10% and no reported execution failures. A qualified professional failing the required-criteria check on more than half their own deliverables is not the baseline these rubrics describe, so even 47.1% is `below` rather than `match`.

### Criterion-level performance, for the substantially-below rule

`DECISIONS.md`'s rule excluding rows whose above-chance score is under about half the human's needs a metric that reflects how much of the job was done. Pass@1 does not: a task fails for missing any one of a mean 4.16 binary criteria, so a deliverable that satisfies three of four scores zero.

**Artificial Analysis publishes no criterion-level score for this benchmark.** Its page says so directly — the headline is pass@1 "rather than the mean rubric score across criteria" — and the payload carries no `apexAgentsBreakdown`, unlike `harveyLabBreakdown`, which does expose a `criteriaPass` field. So the metric has to come from the other board.

**Mercor publishes it and Epoch republishes it per model.** The paper's Metrics section: "Finally, we report the mean percentage of criteria passed per task. For training, this percentage can be more informative than Pass@1 because it provides a dense signal that rewards partial progress." That is the `Mean score` column of Epoch's `apex_agents_external.csv`, which carries 65 model-configurations. Six of the nine models here appear in it; three do not.

| point_id | AA pass@1 | Mercor-board pass@1 | Difference | **Criteria met per task** | SE (pp) |
|---|---:|---:|---:|---:|---:|
| work-apex-agents-gpt55 | 0.377 | 0.385 | 0.008 | **0.555** | 3.6 |
| work-apex-agents-kimik3 | 0.413 | 0.393 | 0.020 | **0.554** | 3.3 |
| work-apex-agents-gpt54 | 0.333 | 0.360 | 0.027 | **0.527** | 3.4 |
| work-apex-agents-glm52 | 0.337 | 0.356 | 0.019 | **0.522** | 3.5 |
| work-apex-agents-opus46 | 0.330 | 0.321 | 0.009 | **0.484** | 3.4 |
| work-apex-agents-gptoss120b | 0.031 | 0.047 | 0.016 | **0.145** | 1.9 |
| work-apex-agents-gemini35flash | 0.471 | — | — | **not published** | — |
| work-apex-agents-gpt56terra | 0.389 | — | — | **not published** | — |
| work-apex-agents-gpt56luna | 0.358 | — | — | **not published** | — |

The three without are absent from Epoch's export entirely: it carries no Gemini 3.5 entry at any tier, and of the GPT-5.6 family only Sol. Mercor's own leaderboard predates all three.

**The transfer across boards is tight but is a transfer.** The criterion score is Mercor's harness, 480 tasks at 8 repeats; the row's pass@1 is AA's Stirrup, 452 tasks at 3 repeats. What licenses reading them together is that the two boards' pass@1 agree to within 0.027 on all six, a mean absolute difference of 0.017, inside Epoch's own 1.4–4.0 percentage-point standard errors. Every row's `performance_evidence` and `notes` say which board the criterion score is from, and the per-row pass@1 difference is in `notes`. This is the one place in the study where a number crosses boards, and it is labelled at every appearance.

**Reading it against the rule.** The human arm meets every criterion by construction, so the human baseline on this metric is 1.0, and the chance floor is near zero rather than near 0.5 — these are open-ended file and console deliverables, and the weakest entries in Epoch's 65 land at 0.054 (GPT-4o) and 0.055 (o1). Four of the six clear 0.5: GPT-5.5 at 0.555, Kimi K3 at 0.554, GPT-5.4 at 0.527, GLM-5.2 at 0.522. Claude Opus 4.6 at 0.484 is just under, within half a standard error of the line. gpt-oss-120b at 0.145 is far under on any reading. The keep-versus-exclude decision is the coordinator's; the rows carry the numbers either way, and `performance_vs_human` stays `below` on all nine because the metric does not change the direction of the comparison.

`comparison_issues = different_inputs_or_tools; different_assessment`.

- **Inputs and tools.** The agent works a frozen simulated world through a fixed toolbelt with web search disabled. The professional whose time is being estimated works their real environment, with search, colleagues and the ability to ask a question. The task content is the same; the working conditions are not.
- **Assessment.** The AI is graded by an automated judge against binary all-criteria rubrics. The human side carries no scored assessment at all, only a completion-time measurement. The two arms are not scored the same way, because only one of them is scored.

Not flagged: the 452-of-480 subset is not `different_task`, because the human time is computed over the same subset.

## Model records

Six of the nine models already have registry records and are reused unchanged, with the reasoning-effort suffix in AA's configuration name treated as a task configuration rather than model identity.

| AA slug | model_id | Registry | Active params | Basis |
|---|---|---|---:|---|
| gemini-3-5-flash | gemini-3.5-flash | project dataset | 4.0e10 | estimated |
| glm-5-2 | glm-5.2 | project dataset | 4.0e10 | estimated |
| gpt-5-4 | gpt-5.4-2026-03-05 | project dataset | 1.0e11 | estimated |
| claude-opus-4-6-adaptive | claude-opus-4-6 | project dataset | 1.0e11 | estimated |
| gpt-oss-120b | gpt-oss-120b | project dataset | 5.1e9 | reported |
| gpt-5-6-luna | gpt-5-6-luna | this folder | 8.0e9 | estimated |
| kimi-k3 | kimi-k3 | **new** | 1.04e11 | estimated |
| gpt-5-6-terra | gpt-5-6-terra | **new** | 2.0e10 | estimated |
| gpt-5-5 | gpt-5-5 | **new** | 1.73e11 | estimated |

Artificial Analysis's own `activeParams` field agrees with the registry where both exist: 40 for GLM-5.2, 5.1 for gpt-oss-120b, both in billions. Nothing in `../AI Compute vs Human Time/dataset/models.csv` was modified.

**Kimi K3.** Open weights. The safetensors index at `moonshotai/Kimi-K3` reports 2,779,931,837,184 total parameters, matching the 2.8T that both Artificial Analysis and Epoch publish. Both also publish 104B active, Epoch at Speculative confidence. A direct three-matrix expert count from the public config gives 6.4T total against the actual 2.78T, so the latent-MoE expert parameterisation is not the standard gate/up/down form and 104B was not reproduced here; it is recorded as the published estimate. Release 2026-07-16 per Artificial Analysis and Epoch; the Hugging Face repository was created 2026-06-13, which is not treated as public availability.

**GPT-5.6 Terra.** OpenAI's model page: "It roughly corresponds to the mini model tier used in earlier GPT-5 families." That is OpenAI's own tier statement, so the registry's 20B mini prior applies — the one carried by o1-mini, o3-mini, o4-mini, gpt-5-mini and grok-3-mini-beta. Scenario range 8–60B. The same serving ladder applied against o4-mini's $1.10/$4.40 would give 20B × √2.7 = 33B; it is not applied because the report holds the nano tier at 8B in exactly this situation, on IKP evidence. Released 2026-07-09 with Sol and Luna.

**GPT-5.5.** No tier statement relating it to an earlier family; OpenAI's page places it in the GPT-5 family alongside GPT-5.4 and GPT-5.4 Mini and calls it "a flagship model for the most complex professional work", at $5/$30 per million tokens. Revision 1 moved it from 1.0e11 to **1.73e11**, on the coordinator's ruling that a new ID minted in this batch has no inherited prior to preserve and must be priced by the folder's own method.

That method is the serving ladder in `research/model-priors/openai.md`, which prices GPT-5.6 Sol by square-root shrinkage on the output-price ratio against the GPT-5 anchor: $20 against $10 gives 100B × √2 = 141B. GPT-5.5 is $30 against $10, so 100B × √3 = 173B. The same report independently reads GPT-5.5 as the GPT-5 family's genuine scale-up, which points the same way; `openai-proposals.csv` has no row for it. Range 70–400B. The first submission held 100B for comparability with `gpt-5.4-2026-03-05`, which was not a reason — the block already spans 8B to 173B. The change moves `work-apex-agents-gpt55` by 1.73x.

## Per-point notes

Each row differs only in model, tokens, FLOPs, pass@1 and the cache parameters in the tables above. The shared evidence is everything above.

### work-apex-agents-gemini35flash

3.29e16. Highest scorer on the AA board at 47.1%, and the heaviest input workload at 2.54M tokens per run — 4.1x Kimi K3's, on a model estimated at 40B active. Mercor's own run shows the same pattern on the previous Flash generation: 5.27M trajectory tokens per run against 1.01M for GPT-5, at 54 steps against 34. Its provider's implicit caching carries a 4,096-token minimum, the highest of the four automatic providers here, which is the one reason to think the achieved share sits toward the floor rather than the ceiling.

### work-apex-agents-kimik3

2.51e16, and the only row where both the active-parameter count and the attention correction rest on a published architecture. Its 104B active is the largest coefficient in the block, and its attention correction the smallest at 0.07x–0.17x, because 69 of its 93 layers use linear attention.

### work-apex-agents-gpt56terra

6.17e15. The value is driven by the 20B mini-tier prior, which is OpenAI's statement of tier and not of size; at the top of the 8–60B range the row would read 1.9e16.

### work-apex-agents-gpt55

3.54e16, the second largest, and the row Revision 1 moved most on the model side: 1.73x, from the 100B family prior to the 173B serving-ladder estimate. It has the lowest input workload of the nine at 559k tokens per run and the lowest output at 10.5k, against 37.7% pass@1 — the most token-efficient row in the block on both sides.

### work-apex-agents-gpt56luna

2.57e15, the smallest in the block, on the 8B nano-tier prior. It processes 1.11M input tokens per run, twice GPT-5.5's, to reach 35.8% against 37.7%. At the top of its 3–20B range the row would read 6.4e15.

### work-apex-agents-glm52

1.93e16. Its 67.3k output tokens per run are the highest of the nine and 6.4x GPT-5.5's, almost all of it reasoning: 26.0M reasoning against 4.4M answer tokens over the benchmark. Its provider's published cached and uncached input prices match AA's price fields exactly, which is the tightest confirmation in the block that AA is pricing a provider that caches by default.

### work-apex-agents-gpt54

3.63e16, on 100B active and 777k input tokens per run.

### work-apex-agents-opus46

1.17e17, the largest in the block by 3.2x, and the row Revision 1 moved most: 3.7x upward, from 3.16e16. It is the only row whose central is gross input, because the published Stirrup harness sets no Anthropic cache breakpoints and Anthropic caches nothing without them. It is also the one row whose cacheable share is transferred from other models of the same company rather than from its own runs, since Artificial Analysis instruments none of the nine evaluations this configuration appears on — but that share now sets only the 0.07x scenario, not the central. If AA's production runs used a modified harness with breakpoints, this row belongs near 8e15 instead, and the whole block's ordering changes.

### work-apex-agents-gptoss120b

3.28e15, unchanged from the first submission and the only row whose construction Revision 1 left alone, because no provider default is established for AA's serving path. Two weak signals push upward — an AA live cache-hit rate of 0 and a cache-hit price only 17% below input — and the no-reuse edge is 3.84x, or 1.26e16. At 3.1% pass@1 it is also the only model in the block that is not in the same league as the others; Mercor's board puts the previous-generation open models at 4.0–4.7% on the same tasks.

## Dispositions

### Mercor APEX-Accounting — no rows

Both axes fail, for different reasons.

- **Human side.** `metadata.estimated_completion_hours` is present on all ten public dev tasks (mean 2.375 h, median 2.25, range 0.75–4.0), but all ten share one `world_id` and one `world_entity_type` (`legal_services`). They are one company's month-end close, not a sample of the 160-task benchmark, and the paper reports no hours statistics for the 160. Transferring a single world's mean to the benchmark the leaderboard scores would be a transfer with nothing behind it.
- **Compute side.** The paper publishes no per-model token count and no dollar cost at the canonical setting. It publishes a 500-step / 5M-token cap, a budget ablation at $1/$5/$10/$50 with a 90:10 dollars-to-tokens conversion, and wall-clock time per run. A cost-only row under the folder's ruling would have to use a budget-ablation figure, which prices a different run configuration than the scored one.

Either failure alone would be survivable; together they would make a row whose human time comes from ten tasks in one world and whose compute comes from a different run configuration. What would unblock it: the hours distribution over the 160, or per-model tokens at the canonical setting. One of the two suffices, not neither.

### Vals AI Finance Agent — no rows here, but buildable, and not the way the brief frames it

The pairing named in the brief does not work. The public 50 questions carry `Expert time (mins)` (mean 12.6, median 10, range 2–60), but no per-model cost or score exists for those 50 — the leaderboard is published over all 537 — and the Hugging Face card calls the file only "a sample", with no claim of randomness. Pairing a 50-question time with a 537-question cost needs a representativeness claim nobody makes.

A different pairing on the same source does work, and it is the finding worth carrying forward. [arXiv 2508.00828](https://arxiv.org/abs/2508.00828) publishes a benchmark-wide human expert time in its **main results table**: Table 2's final row reads "Expert | - | - | 1010.5s (16.8m) | $25.66", beside every model's own time and cost per query. The main text repeats it, and a footnote on that sentence defines the quantity — "These calculations only account for time spent directly answering the question, and exclude the time to create the question, review the answer, etc." — which is the active-time definition COLUMNS asks for. Appendix E.1.1 carries the same values in Figures 9 and 10, where $25.66 at a stated $91.4/h is 16.84 minutes and confirms the alignment. That is a whole-benchmark number on the same 537 questions the current `finance_agent` board scores, so the representativeness gap closes. The public-50 mean of 12.6 min is consistent with it: the public sample skews to the shorter questions.

The board then supplies `cost_per_test` for 51 models over 537 tasks, roughly twenty of which already have registry records, including `gpt-5-5` added by this study. What it does not supply is any token count — `avg_input_tokens` and `avg_output_tokens` are null on all 878 model-board rows across all eleven Vals boards — so every row would be a cost inversion needing a per-model price sheet at the board's run date and a transferred cache structure, exactly the RLI construction. That is a study of its own, not a tail on this one, and it is the recommended next block in this domain. Note also that the paper's own human time is presented without a collection method, and the public-50 column's values are plainly round judgments rather than stopwatch readings, so the human axis there would be `assumed`, weaker than APEX-Agents' calibrated number — but better defined, since Vals states what the time covers and Mercor does not.

## What a reviewer should check first

Revision 1 answered the first submission's five open calls. What is now most exposed:

1. **`work-apex-agents-opus46` at gross input.** It is 3.7x the first submission's value and 3.2x the next-largest row, and it turns entirely on the published Stirrup tree having no Anthropic cache breakpoints. If AA runs a modified harness in production, the row belongs near 8e15. This is the single largest unverified inference in the block.
2. **The 0.60 achieved-share floor on the seven provider-default rows.** It is inverted from one cost measurement in one external study, on a different benchmark, assuming input is 85% of the invoice. The bracket it opens is 3.8x–9.1x wide across the seven rows and the central is its geometric mean, so moving the floor to 0.8 would lower those rows by about 1.3x and moving it to 0.4 would raise them by about 1.2x. Nothing in the source measures it.
3. **Whether the per-repeat normalisation holds for this benchmark specifically.** The calibration is solid across eight other AA evaluations, but it is inference from AA's documentation of AA-LCR rather than a statement about APEX-Agents. If the totals were instead over all three repeats, every `tokens` and `compute_flops` value falls by 3x.
4. **`gpt-5-5` at 173B.** Square-root shrinkage on a list-price ratio is the folder's method, not a measurement, and list prices carry margin that varies across a lineup.
5. **The criterion-level score is Mercor's board, not AA's**, and three of nine rows have none at all. It is the only number in the study that crosses boards.
6. **`human_time_evidence = transferred_timings` with `human_attempts = 96`**, and the ratio-versus-difference choice within the matched pair (5,353 s against 5,454 s) and against the paper's own headline (5,000 s). Revision 4 re-read the study at the source and found nothing finer to use: the paper publishes one aggregate pair and no per-task, per-domain or per-expert detail, and the released export carries no time field.

## Files

- `research/apex-agents/build_rows.py` — token workload, cache branches, FLOPs, human time and the scenario grids. Takes explicit `--aa-models`, `--cacheable` and `--out` paths; standard library only.
- `research/apex-agents/emit_rows.py` — emits the candidate CSVs from `calculations.json`, enforcing the `DECISIONS.md` field-length limits. Takes explicit `--calculations`, `--points-out` and `--models-out` paths.
- `agent-work/derived/apex-agents/calculations.json` — every derived number quoted above.
- `agent-work/sources/apex-agents/` — retained extracts and `MANIFEST.md`, including `harness-and-provider-caching.md`, added in Revision 1.
- `candidates/apex-agents/REVISION.md` — the revision log, and `first-submission/` the pre-revision CSVs.

Reproduce with:

```
python3 research/apex-agents/build_rows.py \
  --aa-models agent-work/sources/apex-agents/aa-apex-agents-model-records.json \
  --cacheable agent-work/sources/apex-agents/aa-cacheable-input-shares.csv \
  --out       agent-work/derived/apex-agents/calculations.json
python3 research/apex-agents/emit_rows.py \
  --calculations agent-work/derived/apex-agents/calculations.json \
  --points-out   candidates/apex-agents/points.csv \
  --models-out   candidates/apex-agents/models.csv
```
