# Epoch native GPT, Claude and Gemini runs

Fourteen original native evaluations extend the reviewed SWE-bench, SimpleQA-Verified, GPQA Diamond and OTIS recipes. There are ten SWE runs over the exact same 484 submitted issue IDs. Human estimates are unchanged. All recorded failed work remains included. The denominator is the source completed-evaluation count, including incorrect answers; uncompleted tasks' work is allocated across completed evaluations. This is not compute per successful patch. For multi-epoch question benchmarks the native reduced accuracy is preserved rather than substituted with a differently weighted raw fraction.

## Model assumptions

Every coefficient here is estimated; none is a provider-disclosed parameter count. These uncertainties are correlated across points using the same model. Half-to-double parameter scenarios directly scale all FLOP estimates and are not confidence intervals.

- **GPT-5.1/5.2, 100B active:** [Epoch's original GPT-5 estimate](https://epochai.substack.com/p/notes-on-gpt-5-training-compute), “Pre-training,” uses approximately 100B active parameters. We transfer this model-family anchor to later 5.x snapshots, without asserting identical architecture. Coefficient 200B FLOPs/token; scenario 50–200B active.
- **GPT-4.1, 50B active:** [Epoch's GPT-4o analysis](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use) supplies a 200B central total estimate and quarter-active assumption;200B/4=50B. Transfer to the later GPT-4.1 general-purpose API model is explicitly assumed, not a source report about 4.1. Scenario 25–100B. Public o3 retains the canonical 50B assumed coefficient. The original [Epoch GPT-4o energy analysis](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use) supplies the 200B-total/quarter-active basis; [fresh-five-models.md](../fresh-five-models.md) explains the transfer to the early o3 checkpoint, and this is explicitly transferred again to public o3. No independent public-o3 architecture measurement is claimed; the canonical public model identity remains distinct from that checkpoint.
- **Opus 4/4.1, 180B active; Opus 4.5, 100B:** the original [bandwidth analysis](https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus), “Active Parameter Count,” calibrates effective Google Vertex bandwidth at 4–4.5TB/s using open models, then divides by observed token throughput. Its FP 8 scenarios give 174–196B for Opus 4 at 23tokens/s, 167–188B for 4.1 at 24tokens/s, and 100–112.5B for 4.5 at 40tokens/s. Adopt rounded 180B/180B/100B. Precision and cross-model serving comparability are assumptions: BF 16 approximately halves inferred parameters, whereas mixedFP 8/FP 4 increases them. Speculative decoding, batching and attention can also disturb the calibration. Thus this is suggestive model-specific evidence, not a hardware measurement of closed model weights. Scenarios 90–360B for 4/4.1, 50–200B for 4.5.
- **Sonnet 4.5/4.6, 100B active:** [Epoch's earlier Sonnet analysis](https://epoch.ai/gradient-updates/frontier-language-models-have-become-much-smaller) estimates 400B total for Sonnet 3.5. Applying the explicitly transferred quarter-active assumption above gives 100B. The newer [bandwidth study](https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus) gives FP 8 ranges 97.6–109.8B for 4.5 and 78.4–88.2B for 4.6; alternate precision widens these.100B remains a deliberately rounded family prior, with 50–200B sensitivity, not a claim that the central FP 8 estimate for 4.6 was 100B.
- **Gemini 2.5Pro stable, 100B active:** no original public size estimate is asserted. This is explicitly a frontier-peer prior from the GPT-5/Opus anchors, consistent with the existing Gemini 3Pro assumption. Scenario 50–200B. The observed run uses the stable `gemini-2.5-pro` endpoint, first generally available June 17, 2025; Google states that the stable model is unchanged from the June 5 preview; the date identifies the stable endpoint, not a separately developed architecture. See the [June 17 API changelog](https://ai.google.dev/gemini-api/docs/changelog#june-17-2025) and [same-day developer announcement](https://developers.googleblog.com/en/gemini-2-5-thinking-model-updates/).

Public dates below come from original announcements. In particular Opus 4 became public May 22 despite the internal May 14 snapshot name; Opus 4.5 became public Nov 24 despite the Nov 1 snapshot name. GPT-5.1 uses the Nov 13 API release, distinct from the earlier ChatGPT product announcement. These dates do not establish parameter counts.

## Native accounting and error audit

Source summary totals are checked sample by sample. Google uses total=input+output+reasoning; its cached reads are a subset of input. OpenAI uses total=input+output, including reasoning once. Anthropic SWE uses total=uncached input+cache-write+cache-read+output; exclude only cache reads. Anthropic question runs have no cached traffic. External Gemini answer grading is assessment work and excluded from solving. Header aggregate counters reconcile exactly except GPT-5.2 SWE: its header contains the final five-task segment only, identified by started_at>=2026-02-12T 14:26:01+00:00 and exact matching counters. All 484 summaries are used for compute.

`native-next-audit-plan.json` records a deterministic random sample (seed 20260913) of five counter-bearing samples per provider across this tranche, in addition to all four zero-total records. All 15 random samples have no failed or pending primary-model calls. SWE examples naturally have multiple successful agent calls; these are already included in counters. This bounded spot check does not establish exhaustive retry coverage. Original full samples are retained in each run's native-next-audit folder.

`recover_native_next.py` reproduces the two corrections in expansion-09/usage-recovery.json:

- **GPT-5.2 SimpleQA:** ten raw API responses violate reasoning<=output. Nine have nonzero totals, and each total independently reconciles exactly to o 200k-tokenized prompt+visible answer+native reasoning+12 wrapper positions. Their raw API input/output allocation is inconsistent, but the total is correct and is retained, without adding reasoning twice. The tenth sample 343 is content-filtered: input/output/total are all zero despite 285 explicitly recorded reasoning tokens. Its 15-token prompt and the corroborated 12-position wrapper yield 312 recovered tokens. Encrypted reasoning content is not tokenized. The retained native fields and exact per-sample reconciliation are in the recovery file.
- **Sonnet 4.6 OTIS:** a full audit of all 360 samples found three streamed-content parser failures and two incomplete-chunked-response read failures, including one before an otherwise successful sample. These five response-phase failures receive the observed run mean, 14, 705.341737 tokens per call. All 367 explicitly rate-limited retries receive zero. No connection-establishment failure is charged. Added work is 73, 526.708683 tokens, with a zero-to-one-mean-per-lost-call sensitivity; a lost response could be partial or longer than average, so this is not a hard bound. The 357 responses with usage supply the mean. Event UUIDs/timestamps prevent double counting. `audit_native_sonnet.py` reproduces the complete event audit from the retained original `full.eval`; `runwide-error-audit.json` retains tracebacks.

The five Claude samples with reasoning subcounts above native output were individually checked: GPQA IDs `reco8WSc71p8zAv4q`, `recWxGU8Q4YReJ1tb`, `recqGD3fxPCI59vPQ`, and OTIS 2025-II Problems 07 and 15. Original Anthropic responses report input/output usage but no reasoning-token field. The exact evaluation's [Inspect provider code, commit 5a 6979113, lines 1873–1880](https://github.com/UKGovernmentBEIS/inspect_ai/blob/5a6979113/src/inspect_ai/model/_providers/anthropic.py#L1873) recounts visible thinking through a separate count-tokens request; [lines 2714–2737](https://github.com/UKGovernmentBEIS/inspect_ai/blob/5a6979113/src/inspect_ai/model/_providers/anthropic.py#L2714) fall back to characters divided by four if that request fails. This auxiliary subcount is not generation usage. [Lines 1911–1917](https://github.com/UKGovernmentBEIS/inspect_ai/blob/5a6979113/src/inspect_ai/model/_providers/anthropic.py#L1911) explicitly include reasoning in native output and sum input, cache creation, cache reads and output. Native totals are therefore retained; these oversized auxiliary reasoning counts are not added.

The SWE quality judgment remains below the assumed complete correct-patch target. Native test defects, potential contamination, and the contrast between human conditional-correct effort and AI all-attempt effort remain the limitations documented in swebench.md. Counter corrections do not alter native performance scores.



Future SWE text states the work once, reports correct/completed test counts against the conditional correct-patch human target, and identifies concrete limitations: codebase familiarity, clarified requirements, false test rejections, and possible exposure to published solutions. Provider accounting, incomplete-evaluation normalization and explicit reasoning settings are retained where applicable. Empty default-settings boilerplate is omitted.

<!-- GENERATED -->

## Model gemini-2.5-pro

Public release 2025-06-17: [original release](https://ai.google.dev/gemini-api/docs/changelog#june-17-2025). Estimated active coefficient 1e+11 × 2 = 2e+11 FLOPs/token; [original anchor](https://epochai.substack.com/p/notes-on-gpt-5-training-compute), interpreted as specified under [model assumptions](#model-assumptions).

## Model gpt-4.1-2025-04-14

Public release 2025-04-14: [original release](https://openai.com/index/gpt-4-1/). Estimated active coefficient 5e+10 × 2 = 1e+11 FLOPs/token; [original anchor](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use), interpreted as specified under [model assumptions](#model-assumptions).

## Model gpt-5.1-2025-11-13

Public release 2025-11-13: [original release](https://openai.com/index/gpt-5-1-for-developers/). Estimated active coefficient 1e+11 × 2 = 2e+11 FLOPs/token; [original anchor](https://epochai.substack.com/p/notes-on-gpt-5-training-compute), interpreted as specified under [model assumptions](#model-assumptions).

## Model gpt-5.2-2025-12-11

Public release 2025-12-11: [original release](https://openai.com/index/introducing-gpt-5-2/). Estimated active coefficient 1e+11 × 2 = 2e+11 FLOPs/token; [original anchor](https://epochai.substack.com/p/notes-on-gpt-5-training-compute), interpreted as specified under [model assumptions](#model-assumptions).

## Model o3-2025-04-16

Public release 2025-04-16: [original release](https://openai.com/index/introducing-o3-and-o4-mini/). Estimated active coefficient 5e+10 × 2 = 1e+11 FLOPs/token; [original anchor](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use), interpreted as specified under [model assumptions](#model-assumptions).

## Model claude-opus-4

Public release 2025-05-22: [original release](https://www.anthropic.com/news/claude-4). Estimated active coefficient 1.8e+11 × 2 = 3.6e+11 FLOPs/token; [original anchor](https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus), interpreted as specified under [model assumptions](#model-assumptions).

## Model claude-opus-4-1

Public release 2025-08-05: [original release](https://www.anthropic.com/news/claude-opus-4-1). Estimated active coefficient 1.8e+11 × 2 = 3.6e+11 FLOPs/token; [original anchor](https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus), interpreted as specified under [model assumptions](#model-assumptions).

## Model claude-opus-4-5

Public release 2025-11-24: [original release](https://www.anthropic.com/news/claude-opus-4-5). Estimated active coefficient 1e+11 × 2 = 2e+11 FLOPs/token; [original anchor](https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus), interpreted as specified under [model assumptions](#model-assumptions).

## Model claude-sonnet-4-5

Public release 2025-09-29: [original release](https://www.anthropic.com/news/claude-sonnet-4-5). Estimated active coefficient 1e+11 × 2 = 2e+11 FLOPs/token; [original anchor](https://epoch.ai/gradient-updates/frontier-language-models-have-become-much-smaller), interpreted as specified under [model assumptions](#model-assumptions).

## Model claude-sonnet-4-6

Public release 2026-02-17: [original release](https://www.anthropic.com/news/claude-sonnet-4-6). Estimated active coefficient 1e+11 × 2 = 2e+11 FLOPs/token; [original anchor](https://epoch.ai/gradient-updates/frontier-language-models-have-become-much-smaller), interpreted as specified under [model assumptions](#model-assumptions).

## agen-epoch-swebench-gemini25pro

[Original log](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/KL724uHFGbiXj4o5PHyLn2.eval); primary `google/gemini-2.5-pro`; Source default generation settings. Dataset `davidowen-epoch/SWE-bench_Verified_epoch`. 484 submitted summaries, 483 completed evaluations. Recorded included workload 218,927,041; correction 0.000000; divide corrected total by 483 = **453265.095238 tokens** × 200000000000 = **9.06530190476e+16 FLOPs**. Native score 0.575569358178. full summaries equal header Human baseline and judgment: [swebench](swebench.md). Full native counters and plan in expansion-09/calculations.json; all repeated trials contribute workload, without best-of-N answer selection.

## agen-epoch-swebench-gpt41

[Original log](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/SheUt9cNpkSevy4r6Gsr3u.eval); primary `openai/gpt-4.1-2025-04-14`; Source default generation settings. Dataset `davidowen-epoch/SWE-bench_Verified_epoch`. 484 submitted summaries, 480 completed evaluations. Recorded included workload 48,233,800; correction 0.000000; divide corrected total by 480 = **100487.083333 tokens** × 100000000000 = **1.00487083333e+16 FLOPs**. Native score 0.485416666667. full summaries equal header Human baseline and judgment: [swebench](swebench.md). Full native counters and plan in expansion-09/calculations.json; all repeated trials contribute workload, without best-of-N answer selection.

## agen-epoch-swebench-gpt51high

[Original log](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/YoHtZpMNdsRE6qdj2K4Ucj.eval); primary `openai/gpt-5.1-2025-11-13`; reasoning_effort=high. Dataset `davidowen-epoch/SWE-bench_Verified_epoch`. 484 submitted summaries, 484 completed evaluations. Recorded included workload 221,860,701; correction 0.000000; divide corrected total by 484 = **458389.878099 tokens** × 200000000000 = **9.16779756198e+16 FLOPs**. Native score 0.679752066116. full summaries equal header Human baseline and judgment: [swebench](swebench.md). Full native counters and plan in expansion-09/calculations.json; all repeated trials contribute workload, without best-of-N answer selection.

## agen-epoch-swebench-gpt52high

[Original log](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/9owdbpnWJ5pkQQC3GWKP5L.eval); primary `openai/gpt-5.2-2025-12-11`; reasoning_effort=high. Dataset `davidowen-epoch/SWE-bench_Verified_epoch`. 484 submitted summaries, 484 completed evaluations. Recorded included workload 188,488,353; correction 0.000000; divide corrected total by 484 = **389438.745868 tokens** × 200000000000 = **7.78877491736e+16 FLOPs**. Native score 0.737603305785. Header exactly matches final five-task segment; full 484 summaries retained. Human baseline and judgment: [swebench](swebench.md). Full native counters and plan in expansion-09/calculations.json; all repeated trials contribute workload, without best-of-N answer selection.

## agen-epoch-swebench-o3med

[Original log](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/AKt7PcE8LQtoMWVuxwMidk.eval); primary `openai/o3-2025-04-16`; reasoning_effort=medium. Dataset `davidowen-epoch/SWE-bench_Verified_epoch`. 484 submitted summaries, 483 completed evaluations. Recorded included workload 125,762,228; correction 0.000000; divide corrected total by 483 = **260377.283644 tokens** × 100000000000 = **2.60377283644e+16 FLOPs**. Native score 0.623188405797. full summaries equal header Human baseline and judgment: [swebench](swebench.md). Full native counters and plan in expansion-09/calculations.json; all repeated trials contribute workload, without best-of-N answer selection.

## agen-epoch-swebench-opus4

[Original log](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/RbcvuVChvxK6SMQbPK8iRn.eval); primary `anthropic/claude-opus-4-20250514`; Source default generation settings. Dataset `davidowen-epoch/SWE-bench_Verified_epoch`. 484 submitted summaries, 484 completed evaluations. Recorded included workload 21,868,779; correction 0.000000; divide corrected total by 484 = **45183.427686 tokens** × 360000000000 = **1.62660339669e+16 FLOPs**. Native score 0.706611570248. full summaries equal header Human baseline and judgment: [swebench](swebench.md). Full native counters and plan in expansion-09/calculations.json; all repeated trials contribute workload, without best-of-N answer selection.

## agen-epoch-swebench-opus41

[Original log](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/cA6Mq67yaynLhY8F5kes3c.eval); primary `anthropic/claude-opus-4-1-20250805`; Source default generation settings. Dataset `davidowen-epoch/SWE-bench_Verified_epoch`. 484 submitted summaries, 484 completed evaluations. Recorded included workload 25,914,478; correction 0.000000; divide corrected total by 484 = **53542.3099174 tokens** × 360000000000 = **1.92752315702e+16 FLOPs**. Native score 0.73347107438. full summaries equal header Human baseline and judgment: [swebench](swebench.md). Full native counters and plan in expansion-09/calculations.json; all repeated trials contribute workload, without best-of-N answer selection.

## agen-epoch-swebench-opus45

[Original log](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/mKQKxkpGDrFHBPBYR3mBrB.eval); primary `anthropic/claude-opus-4-5-20251101`; Source default generation settings. Dataset `davidowen-epoch/SWE-bench_Verified_epoch`. 484 submitted summaries, 484 completed evaluations. Recorded included workload 15,832,632; correction 0.000000; divide corrected total by 484 = **32712.0495868 tokens** × 200000000000 = **6.54240991736e+15 FLOPs**. Native score 0.76652892562. full summaries equal header Human baseline and judgment: [swebench](swebench.md). Full native counters and plan in expansion-09/calculations.json; all repeated trials contribute workload, without best-of-N answer selection.

## agen-epoch-swebench-sonnet45

[Original log](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/Lti64yMEsBWSzgEMFCSVhp.eval); primary `anthropic/claude-sonnet-4-5-20250929`; Source default generation settings. Dataset `davidowen-epoch/SWE-bench_Verified_epoch`. 484 submitted summaries, 484 completed evaluations. Recorded included workload 37,046,857; correction 0.000000; divide corrected total by 484 = **76543.0929752 tokens** × 200000000000 = **1.5308618595e+16 FLOPs**. Native score 0.712809917355. full summaries equal header Human baseline and judgment: [swebench](swebench.md). Full native counters and plan in expansion-09/calculations.json; all repeated trials contribute workload, without best-of-N answer selection.

## agen-epoch-swebench-sonnet46

[Original log](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/KEdgiMmtJKHxgGiS82agYj.eval); primary `anthropic/claude-sonnet-4-6`; Source default generation settings. Dataset `davidowen-epoch/SWE-bench_Verified_epoch`. 484 submitted summaries, 484 completed evaluations. Recorded included workload 14,984,015; correction 0.000000; divide corrected total by 484 = **30958.7086777 tokens** × 200000000000 = **6.19174173554e+15 FLOPs**. Native score 0.752066115702. full summaries equal header Human baseline and judgment: [swebench](swebench.md). Full native counters and plan in expansion-09/calculations.json; all repeated trials contribute workload, without best-of-N answer selection.

## lang-epoch-simpleqa-gpt52xhigh

[Original log](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/UYhgwCjfRSMMPG4hCSRa2G.eval); primary `openai/gpt-5.2-2025-12-11`; reasoning_effort=xhigh. Dataset `codelion/SimpleQA-Verified`. 1000 submitted summaries, 1000 completed evaluations. Recorded included workload 6,934,114; correction 312.000000; divide corrected total by 1000 = **6934.426 tokens** × 200000000000 = **1.3868852e+15 FLOPs**. Native score 0.389. full summaries equal header Human baseline and judgment: [simpleqa](simpleqa.md). Full native counters and plan in expansion-09/calculations.json; all repeated trials contribute workload, without best-of-N answer selection.

## lang-epoch-simpleqa-sonnet46-32k

[Original log](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/nuGnwVYCXGVUAgxrqkVKbc.eval); primary `anthropic/claude-sonnet-4-6`; 32000-token thinking budget; actual recorded output used. Dataset `codelion/SimpleQA-Verified`. 1000 submitted summaries, 1000 completed evaluations. Recorded included workload 453,763; correction 0.000000; divide corrected total by 1000 = **453.763 tokens** × 200000000000 = **9.07526e+13 FLOPs**. Native score 0.29. full summaries equal header Human baseline and judgment: [simpleqa](simpleqa.md). Full native counters and plan in expansion-09/calculations.json; all repeated trials contribute workload, without best-of-N answer selection.

## reas-epoch-gpqa-sonnet46-32k

[Original log](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/58eQmyCfPa3FufhXJFvAL2.eval); primary `anthropic/claude-sonnet-4-6`; 32000-token thinking budget; actual recorded output used. Dataset `Idavidrein/gpqa`. 1584 submitted summaries, 1584 completed evaluations. Recorded included workload 10,029,004; correction 0.000000; divide corrected total by 1584 = **6331.44191919 tokens** × 200000000000 = **1.26628838384e+15 FLOPs**. Native score 0.873737373737. full summaries equal header Human baseline and judgment: [gpqa](gpqa.md). Full native counters and plan in expansion-09/calculations.json; all repeated trials contribute workload, without best-of-N answer selection.

## reas-epoch-otis-sonnet46-32k

[Original log](https://epoch-benchmarks-staging-public.s3.us-east-2.amazonaws.com/inspect_ai_logs/9LWdzVN5w4ihNvncsaCWMu.eval); primary `anthropic/claude-sonnet-4-6`; 32000-token thinking budget; actual recorded output used. Dataset `EpochAI/otis-mock-aime-24-25`. 360 submitted summaries, 357 completed evaluations. Recorded included workload 5,249,807; correction 73,526.708683; divide corrected total by 357 = **14911.2989039 tokens** × 200000000000 = **2.98225978078e+15 FLOPs**. Native score 0.857936507937. full summaries equal header Human baseline and judgment: [otis](otis.md). Full native counters and plan in expansion-09/calculations.json; all repeated trials contribute workload, without best-of-N answer selection.