# Natural Plan calendar scheduling

## reas-work-calendar-naturalplan-gemini15pro-5shot

One calendar question, averaged over all **1,000 original five-shot Gemini 1.5 Pro predictions**: **4.593538 × 10¹⁴ FLOPs** and an estimated **110 active human seconds**. The task is to propose a meeting slot from supplied schedules and preferences. It does not include gathering availability, email exchanges, invitations or entering an event in a calendar.

The AI satisfies the actual constraints in **534/1,000 questions**. The original exact-match score is **489/1,000**. Below is the best comparison with an experienced human scheduler, whose valid-slot accuracy is assumed around 90% (85–95% scenario), not measured in this study. The human estimate targets careful, generally correct scheduling; it does not copy the model's errors.

## Original records and work unit

The [original paper](https://arxiv.org/abs/2406.04520v1), §2.2.3, constructs 30-minute or one-hour meetings during 09:00–17:00. It varies two to seven attendees on one day, or two attendees across one to five weekdays. The shared two-attendee/one-day cell appears once: ten cells of 100 questions each.

The [original repository](https://github.com/google-deepmind/natural-plan/tree/ca76db336072ff8931db43bc1ca8d381038cf073) supplies all `prompt_5shot`, `prompt_0shot`, `golden_plan` and `pred_5shot_pro` strings. `data/README.md` directs inference on `prompt_5shot`. Its description of `duration` as a number of meetings is a documentation error: actual values 0.5 and 1 are meeting hours, as both prompts and the paper specify.

Every retained five-shot prompt contains five complete task/solution examples followed by the target question. There are ten shared exemplar prefixes, one per complexity cell. The calculator verifies that the final question agrees exactly with the zero-shot target. All 1,000 released responses, including wrong answers and claims that no slot exists, enter the compute mean. No successful-only selection, self-correction pass or separate model helper is added to this five-shot setting.

## Validity and the exact-match problem

The original evaluator extracts the first `Day, HH:MM - HH:MM` sequence and compares it with the reference. Replaying its pure parsing/scoring functions gives the published **48.9%** exactly. It does not independently test calendar constraints.

`calendar_constraints.py` reconstructs busy intervals and negative preferences from the task templates. Busy blocks are half-open: a meeting may start when a previous meeting ends. A negative `before` preference imposes a minimum start; `after` imposes a maximum end. A bare day following a negative preference inherits that exclusion, for example “Monday. Tuesday after 15:00. Wednesday.” Earliest availability is enforced only when explicitly requested. All supplied times and parsed first proposals use half-hour boundaries; the parser asserts that rather than rounding other minutes.

The parser finds that **all 1,000 gold slots are feasible**, but **166 tasks still admit multiple valid answers**. Example727 allows both the AI's Tuesday10:00–10:30 and the reference Tuesday14:00–14:30. Both people are free, the other days and Tuesday after 15:00 are excluded, and no earliest rule appears. An experienced scheduler should not be penalized for choosing the first of those slots.

Accepting any slot satisfying the actual conditions credits **45 additional predictions**, for **53.4%** valid. This is the point's main quality criterion; the original exact match remains a distinct reported result. The remaining failures are 393 overlaps or excluded periods, 48 failures to choose the required earliest slot, 12 meetings extending beyond work hours, and 13 no-slot responses. These categories use the first proposed answer and are not a search for a correct time somewhere in an explanation.

Fourteen responses fail the original regex. Thirteen claim no solution; one uses bold markup around its time. Removing Markdown emphasis recovers that time but it collides with Jesse's calendar in example 117. Formatting tolerance therefore changes neither the exact-correct nor valid-correct total. Optional explanations are not scored: example 384 gives a valid slot but describes two participants' calendars inaccurately.

Manual checks cover two outcome-independent examples per complexity cell and targeted cases for valid alternatives, earliest choice, overlaps, workday boundaries, no-solution claims, Markdown and shorthand preferences. IDs and concrete adjudications are retained in `inspection-selection.json`, `inspected-tasks.json` and `manual-adjudications.json`. The source-wide parser is a reproducible interpretation of these fixed templates, not a newly observed human study.

## Human estimate

The baseline is an **experienced office scheduler** with the complete text in front of them, using scratch notes or a simple time grid. They identify one valid slot and check it, treating the supplied avoidance preferences as constraints. The same five exemplars may be visible, but a familiar scheduler does not reread them on every question. Initial format familiarization can be amortized over the repeated work; it is not five extra meetings to solve per question.

The twenty inspected target questions show why the work is short but not instantaneous. A free-all-week participant can be dismissed quickly; dense half-hour lists require marking and checking. Example968 requires carrying negative preferences across several short day fragments. Earliest-choice cases need a chronological scan, while seven-attendee cases need more cross-checks on a single day. The sample was selected by SHA256 order, two records per source cell, independently of AI outcome.

There are no clocks in Natural Plan. The retained [Faulring/Myers calendar visualization paper](https://www.cs.cmu.edu/~faulring/papers/cal-sched-infovis06.pdf) and [groupTime study](https://www.robotics.stanford.edu/~ang/papers/chi06-groupscheduling.pdf) concern broader scheduling interfaces and coordination; they do not supply a suitable numerical timing for this exact text-to-slot task. Study duration and a participant's account of time spent discussing availability are not used as completion times here.

The estimate uses actual interval and preference counts with task-inspected rates:

| Activity | Assumption | Mean seconds |
|---|---|---:|
| Orient to target, duration and working hours | 12 seconds | 12.0 |
| Read and mark busy intervals | 2.5 seconds per interval | 40.4 |
| Keep participant/day context straight | 2 seconds per participant-day | 11.0 |
| Interpret negative preferences | 6 seconds per fragment | 4.5 |
| Find a candidate or earliest gap | 10 seconds + 4 per day | 18.0 |
| Verify duration, people and preferences | 5 seconds + 3 per person + 2 per fragment | 17.0 |
| Write the day and time | 6 seconds | 6.0 |

The mean target has 129.5 whitespace-separated words, 16.156 busy intervals and 0.752 preference fragments. A 2.5-second interval allowance covers recognizing two endpoints and marking the blocked span; participant/day context is counted separately, not rereading every time string. The central total is **108.906 seconds**, rounded to **110**. Faster and slower rates give **66.494 and 175.4 seconds**. These are independent effort scenarios, not confidence limits or a measured speed–accuracy curve. The fixed candidate scan includes interpreting any earliest requirement; it does not assume a human enumerates all 80 possible half-hour starts.

An experienced scheduler with this reading and verification allowance should solve these bounded problems substantially more reliably than 53.4%, although awkward prose and missed boundaries preclude a perfect-score assumption. The roughly 90% human baseline is a judgment, not an empirical cohort result. `human_time_evidence=assumed`, `human_time_method=estimated`, `human_time_statistic=point_estimate` and `human_attempts=not_applicable`. The 1,000 task records and twenty inspected examples are not timing attempts.

## Model

The paper names **Gemini 1.5 Pro** without an API revision. The model record `gemini-1.5-pro-naturalplan` preserves that uncertainty. Its release date is blank; stable 001's release is not silently assigned. The family was introduced in a [February 15, 2024 preview](https://blog.google/innovation-and-ai/products/google-gemini-next-generation-model-february-2024/), and the paper appeared June 6, 2024, but neither fact dates the unspecified build used in the experiment.

The retained [original Gemini 1.5 report](https://storage.googleapis.com/deepmind-media/gemini/gemini_v1_5_report.pdf), §3.1, identifies Pro as sparse MoE without publishing expert dimensions or active size. The **100B active** value is the shared coarse prior for this family. Its numerical anchor is [Epoch's original GPT-5 estimate](https://epochai.substack.com/p/notes-on-gpt-5-training-compute), “Pre-training,” which places roughly 100B active in a medium-sized frontier-model class. Transferring that scale across provider and model generation is weak evidence, not a disclosed Gemini parameter count. Retain the established **30–300B** scenarios rather than guessing a study-specific expert configuration. No pricing or hardware utilization is used to calculate this task's workload.

## Token and FLOP accounting

Google's own [Vertex tokenizer loader](https://github.com/googleapis/python-aiplatform/blob/44766a094f50d03093197027327d0ac2ec641829/vertexai/tokenization/_tokenizer_loading.py) maps `gemini-1.5-pro` and the001/002 identifiers to the public Gemma tokenizer. The retained original tokenizer has the SDK's expected SHA256, `61a7b147390c64585d6c3543dd6fc636906c9af3865a5548f27f31aee1d4c8e2`. Its accompanying `_tokenizers.py` counts text by applying SentencePiece to each supplied string. This is a provider-supported local text count, not an arbitrary substitute vocabulary; it still does not recover historical response metadata or hidden message packaging.

Tokenizing all actual five-shot prompts and responses yields means of **2,237.257 input** and **47.512 output** tokens. Add an explicit **12-token allowance** per single call for unlogged role, boundary and stopping positions: total **2,296.769**. No output cap or guessed response length enters this estimate. Optional explanations and failed responses are counted as they actually appear.

Every input prefix is counted fresh. The [original Gemini API changelog](https://ai.google.dev/gemini-api/docs/changelog#june-18-2024) dates public context-caching support to June 18, after the June 6 paper. That supports a fresh-input central treatment for the original five-shot experiment. Released predictions do not carry native cache counters; this is not provider-observed zero. Reusing ten exemplar prefixes is real, but is not evidence that an earlier explicit cache API was used. The exact inference runner and any additional failed dispatches are not released. Central work is one retained generation per question, with no invented generic retry fraction; an additional fully processed call would add its own prompt and output workload.

Use the shared approximation `F = tokens × 2 × active_parameters`:

`2,296.769 × 2 × 100,000,000,000 = 459,353,800,000,000 FLOPs`.

`compute_method=params_tokens`, `compute_evidence=derived_assumed_inputs`, `compute_statistic=mean`, `compute_subset=all`, `ai_attempts=1000` and `tokens_accounting=input_output`. The assumption label reflects model size and unlogged packaging/accounting, not invented prompt or response texts. The fixed coefficient omits context-dependent attention, normalization and other small operations; it is not a profiler measurement. The attention term is added back in `compute_flops` (`research/attention-correction.md`). No image/audio positions or helper models enter this text-only setting. The 30–300B parameter alternatives are 1.3780614×10¹⁴–1.3780614×10¹⁵ FLOPs; removing the 12-token allowance gives 4.569538×10¹⁴.

## Reproduction

Python3 plus `sentencepiece` is sufficient. Run with explicit source and new output paths:

```sh
python research/recompute.py sources /path/to/new-output-directory
```

The program verifies retained source hashes, extracts only the original evaluator's three pure functions, checks all 1,000 target/prompt pairs, tokenizes the actual strings and reconstructs feasible slots. It writes `calculations.json`, `attempts.json` and the outcome-independent inspected task texts. It refuses an existing output directory or a path inside the source evidence. `--assumptions FILE` supports deliberate parameter/time scenarios. Original source files are never executed as a whole and no model, calendar API or network call is made.
