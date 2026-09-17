# ARC modern: remaining five configurations

## Work unit and original sources

These are fixed benchmark test outputs, not a whole benchmark run or a reasoning-token limit. Sum both available model attempts; compare their either-answer success with the human success criterion described below. Average AI compute, AI success and human success using the same number of eligible human observations per test. Include unsuccessful human observations and unsuccessful AI responses. Require a complete two-response AI pair; incomplete pairs have their recoverable tokens and reasons retained separately, not treated as zero-cost attempts or assigned a score from one answer. These observations describe the available complete-pair subset, not full leaderboard scores.

Native v1 pin: `3e9c9d1a8402aff82356815c106cecaea65cb7d9`; v2 pin: `026789c1c12a4c34580a32e84dcaf5630d7e8f31`, in the two [ARC Prize public-evaluation repositories](https://huggingface.co/arcprize). Exact per-file URLs, Git blob identity, SHA256 and byte lengths are retained in agent-work/sources/arc-modern/native-manifest.json. agent-work/sources/arc-modern/remaining-source-manifest.json fixes the later tranche's evidence separately from the immutable first-tranche source-manifest.json. Repository progress records are not usage records: they report completed tasks while attempts_completed and cost are zero. Read actual response files instead. No prompts, programs or grid solutions were executed.

## Human clocks and scores

H-ARC v1 uses the original raw action logs, summary and task grids (agent-work/sources/arc-modern/shared-human-manifest.json identifies the three shared files). Start at the initial reset and stop at the last available of the first two submissions. Score the actual submitted grid, not a later reset or the summary's final grid. The inseparable first written explanation is included; final after-task descriptions are excluded. Of 4101 sessions, 4091 have usable timestamps; no success filter and no exclusion of participants who did not finish the study. The H-ARC study does not apply ARC2's five-second view filter. Human third-submission, full-task and native-summary-label alternatives remain in the calculation JSON. The first explanation is extra work (different_task); editor and feedback versus two independent text answers also justify different_inputs_or_tools and different_assessment.

ARC-AGI-2 uses the original public human-attempts.csv and all 120 source task grids. The [technical report, §4.3](https://arxiv.org/html/2505.11831v2) defines an attempt as a test view longer than five seconds. Apply duration_seconds > 5, no success filter, no upper-duration trim; include views with zero submissions. human_time averages their source-recorded duration_seconds. Human success is correct_submissions > 0. These are source summary outcomes; the ARC2 release does not provide submitted human grids here, so they are not claimed to have been rescored. A test view can include revisits and more than two submissions. Those assessment differences and the editor/feedback justify two comparison flags, without asserting extra explanation work as in H-ARC. All retained human view identities are unique. Raw examples and submission-count histograms for every included pair remain in calculations-v2.json. On 2026-09-16 Damon merged the two ARC-AGI-2 rows into `solve-an-arc-agi-2-test-grid`, so both record that task's one human duration, 255.2105217741936 seconds over 1240 views, rather than the mean over the cases their own model returned complete pairs for; the derivation is in [arc.md](../arc/arc.md#task-level-human-time). Their AI and human success percentages are unchanged and still run over each row's own matched pairs.

For all five rows, `ai_attempts=not_applicable` follows the benchmark-per-question normalization definition; native response and test counts are recorded in research. human_attempts counts the actual timed human observations contributing to the mean, not unique people or model calls. Human duration method is other_calculation, from raw task_timings.

## Native workload accounting

Every available response's actual demonstrations and test grid are checked against the original task. Outputs are compared exactly with the expected grid and native correctness. ARC2 Deep Think has four responses whose array position differs from the actual test index; they are joined by the prompt's test grid. Both attempts must have the same prompt. File duplication is not used to create additional work. All original response counters are retained, including responses omitted from this point's complete-pair subset.

Use native prompt + completion tokens. Native total equals their sum. Explicit reasoning counts, where populated, are already inside completion and are not added again. No cache-read component or nonempty error/status/helper-usage record is exported for the included responses. GPT-5.2 task 4ff4c9da has 38,203 characters of assistant text despite zero exported usage: its usage is missing, not its output. Its pair is excluded because attempt_1 is absent; it is not an observed zero-cost failure. No recovery log identifies what happened to missing requests; there is no basis to assign them a fabricated full response. The rows do not claim to cover absent dispatches.

Central compute is 2 × assumed active parameters × total native tokens. Full-prefix processing is an assumption when cache counts are missing. Calculation JSON retains alternatives removing the second input prefix, and removing all input processing. The latter is only an extreme sensitivity, not a plausible declaration that every input position was cached. KV-cache attention work and long-context overhead are not separately measured by the parameter-token proxy. This is derived_assumed_inputs, never measured FLOPs. Model assumptions and parameter scenarios are in arc-modern-models-remaining.md.

## Deep Think aggregate semantics

Native provider `curlgemini` exposes aggregate prompt/completion usage, with completion counts often exceeding the 64,000 max_output_tokens setting and prompt counts much larger than the visible prompt. For v1 task 4cd1b7b2, the two completion counters total 138,849. The [ARC Prize 2025 analysis](https://arcprize.org/blog/arc-prize-2025-results-analysis) independently describes approximately 138,000 Deep Think reasoning tokens on that exact task, strongly corroborating aggregate reasoning accounting. The auxiliary reasoning field being zero does not establish no reasoning. Do not multiply by a speculative parallel branch count or replace counters with visible answer length.

The public pinned harness has no curlgemini provider implementation. Native input/output totals therefore do not reveal the internal cache fraction, component-model allocation or exact export implementation. The central estimate processes those aggregate positions once using the assumed 100B backbone. Cache scenarios are particularly consequential: the native input is roughly 84–87% of total positions. Counts retain their native input_output meaning; missing internal allocation is not the same as an unspecified input/output decomposition.

The native request allows code_execution. Code transcripts and CPU arithmetic counts are not exported. Central compute assumes small grid manipulation and checking contribute negligibly beside roughly 10^18 neural FLOPs; that is a scale judgment, not a measured zero or a rigorous upper bound. No additional neural helper is documented beyond the aggregate reasoning work. This pair of observations has much weaker compute calibration than a direct dense-model token counter.

### Cache scenario magnitudes

| Configuration | Full-input central FLOPs | Remove second-attempt input | Remove all input |
|---|---:|---:|---:|
| Deep Think v1 | 5.550e17 | 3.201e17 | 8.721e16 |
| GPT-5.2 v1 | 1.013e16 | 9.202e15 | 8.274e15 |
| Grok 4.20 v1 | 9.925e15 | 8.810e15 | 7.694e15 |
| Deep Think v2 | 1.290e18 | 7.254e17 | 1.736e17 |
| Grok 4.20 v2 | 2.880e16 | 2.703e16 | 2.526e16 |

For Deep Think, removing second-attempt aggregate input is not a claim that the first response generated every internal prefix needed by the second. It is a workload sensitivity only. Removing all input lowers its estimate by 84.3% (v1) or 86.5% (v2); this is a major limitation, not a rounding issue. No known cache count is subtracted twice because none is exported. The source's zero cost fields are not used to infer cache hits or free computation.

## Point summaries

### reas-arcagi-v1-gemini3dt

Human mean 348.702014 seconds from 3923 timed observations. AI/human success 94.2646% / 60.9737%. Counted native positions 2774869.553658; compute 5.54973910732e+17 FLOPs. Complete first-test tasks: 382/400. The classification is above on this matched available subset.

### reas-arcagi-v1-gpt52-xhigh

Human mean 347.689054 seconds from 3901 timed observations. AI/human success 96.9495% / 61.7021%. Counted native positions 50650.928480; compute 1.0130185696e+16 FLOPs. Complete first-test tasks: 379/400. The classification is above on this matched available subset.

### reas-arcagi-v1-grok420

Human mean 350.347103 seconds from 4091 timed observations. AI/human success 96.0401% / 60.9142%. Counted native positions 43154.085065; compute 9.9254395649e+15 FLOPs. Complete first-test tasks: 400/400. The classification is above on this matched available subset.

### reas-arcagi-v2-gemini3dt

Human mean over this row's own matched pairs 249.702977 seconds from 1066 timed observations; the row records the task-level 255.2105217741936 seconds over 1240 views instead, per [arc.md](../arc/arc.md#task-level-human-time). AI/human success 48.8743% / 62.7580%. Counted native positions 6451075.567542; compute 1.29021511351e+18 FLOPs. Complete human-matched test pairs: 139/167, from 104 tasks. Omitted short views within the selected pairs: 17. Classification is below: about fourteen percentage points lower.

### reas-arcagi-v2-grok420

Human mean 255.210522 seconds from 1240 timed observations, which is also the task-level figure the row records at full precision, 255.2105217741936, per [arc.md](../arc/arc.md#task-level-human-time). AI/human success 62.8226% / 62.3387%. Counted native positions 125203.092742; compute 2.87967113306e+16 FLOPs. Complete human-matched test pairs: 161/167, from 115 tasks. Omitted short views within the selected pairs: 20. Classification is match: the approximately half-percentage-point difference is substantively small for this cohort, without claiming a formal equivalence test.

## Reproduction

Python 3 standard library only. Keep recompute-v2.py and recompute-v1-remaining.py together. Supply the original shared H-ARC and ARC2 source directories explicitly; no copied 475MB human log or temporary library is required. The scripts verify retained source hashes, require a new output path outside every evidence directory, and do not change sources or CSVs.

```sh
python research/recompute-v1-remaining.py --sources SOURCE_DIR --human-sources HARC_SOURCE_DIR --selection research/selection-v1-remaining.json --models research/models-remaining-input.csv --manifest SOURCE_DIR/remaining-source-manifest.json --output NEW_V1_JSON
python research/recompute-v2.py --sources SOURCE_DIR --human-sources ARC2_SOURCE_DIR --models research/models-remaining-input.csv --manifest SOURCE_DIR/remaining-source-manifest.json --human-manifest SOURCE_DIR/shared-v2-human-manifest.json --output NEW_V2_JSON
```

After publication, models.csv may be supplied instead: unchanged model coefficients reproduce values, but the full registry file hash differs from the candidate's three-record file hash. Exact candidate-hash replay uses retained research/models-remaining-input.csv. HARC_SOURCE_DIR is dataset/sources/arc-v1; ARC2_SOURCE_DIR is dataset/sources/arc-expansion. SOURCE_DIR is the published arc-modern source directory. Calculations include source and model input hashes; these are integrity checks, not evidence of a model's disclosed parameter count.
