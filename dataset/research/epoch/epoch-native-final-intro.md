# Epoch: remaining native-log runs

These sixteen records use original Epoch `.eval` logs. Workload is total task-solving model work divided by completed evaluations, including incorrect answers. Uncompleted attempts contribute recorded work and the missing-work estimate below. This is an amortized cost per completed evaluation. It is not a mean over successful answers alone.

Human work and timing use the reviewed [SWE-bench](swebench.md), [SimpleQA](simpleqa.md), [GPQA](gpqa.md) and [OTIS](otis.md) definitions. Each SWE run has the same 484 submitted issues. GPQA has 198 questions × eight trials; OTIS has 45 × eight. SimpleQA has 1,000 single trials. Human time retains the full source task mix. Incomplete AI questions are identified below, and the CSV flags selection differences.

## Recorded counters

Counter identities are checked for every summary and every inspected model call. The table uses `I` for source input, `O` for ordinary output, `R` for separately reported reasoning, `CR` for cache reads and `CW` for cache writes.

| Native endpoint | Source total | Included workload |
|---|---|---|
| `google/*` in this tranche | I + O + R | I − CR + O + R |
| `epoch/gemini-3.5-flash` | I + CR + O + R | I + O + R |
| `openai/*` | I + O | I − CR + O |
| Other `epoch/*`, and Anthropic | I + CR + CW + O | I + CW + O |

For Google, reasoning is additional to ordinary output. For the other providers it is included in output, or not separately identified. The `epoch/` adapters normalize cached input differently from `google/` and `openai/`; the native response spotchecks confirm this distinction. Each model's own counters are used, including Opus 4.7's tokenizer; no cross-tokenizer multiplier is applied. Post-answer graders do not help solve the task and are excluded. Their identities and counts are retained in the calculation audit. Cached-token attention is outside the shared parameter-multiplication estimate and is added to `compute_flops` separately (`research/attention-correction.md`).

Gemini 3.1 Pro customtools resumes an earlier run: its header counters cover the final 446 issues. Those counters exactly match that segment; compute uses all 484 summaries.

## Calls without usable counters

Thirteen complete archives were audited, including every incomplete sample and errors inside completed samples. The three larger SWE logs—Gemini 3.1 Pro customtools, Gemini 3 Flash and GPT-5 mini—have complete summary checks plus full event inspection of the first, median-workload and largest-workload samples. That limited event sample cannot exclude additional unreported work elsewhere.

Errors are classified from the original exception and traceback. Explicit quota, rate-limit and overload rejections receive no inference allowance. A response-header/body read failure, connection reset, gateway failure or empty response without usage may have performed work; its amount is unobserved.

For each such send, use half a comparable recorded call as the central allowance. This midpoint spans two scenarios: zero work and one comparable call's workload. For single-question benchmarks the donor is the mean of recorded calls for that same question, across available trials. For SWE it is the same issue's recorded call mean, not the cost of the entire issue. If no same-question call exists, use that run's call mean. These are explicit judgment assumptions; one donor call is a sensitivity case, not a proven upper bound on actual lost compute.

The original Inspect [0.3.174 request hooks](https://github.com/UKGovernmentBEIS/inspect_ai/blob/0.3.174/src/inspect_ai/model/_providers/util/hooks.py) and [active-event counter](https://github.com/UKGovernmentBEIS/inspect_ai/blob/0.3.174/src/inspect_ai/log/_samples.py) show that an event's `retries` count records additional SDK network sends. The same mechanisms were checked at [0.3.239](https://github.com/UKGovernmentBEIS/inspect_ai/blob/0.3.239/src/inspect_ai/model/_providers/util/hooks.py). An exposed failed event therefore represents `1 + retries` sends. SDK retries inside an eventual successful event have no individual error log: their central unresolved share is the run's observed ratio of read/ambiguous sends to all classified failed sends, then the same half-call allowance is applied. Their sensitivity runs from zero to one donor call per send. This mixture transfer is a separate assumption.

GPT-5.4's exposed errors fail while reading response headers. Most otherwise successful records with internal retries have roughly 282 seconds of overhead per retry. This supports treating them as unresolved work, but does not prove that generation completed. The central GPQA and OTIS estimates are dominated by these allowances. Their CSV notes identify that fact and the values below retain the zero-to-one-call scenarios.

## Verification

`expansion-14/usage-reconstruction.json` contains the per-error decisions, SDK counts, same-question donor sizes and scenarios. The sixteen `*-events.json` files reconcile original event counters to summaries. `native-audit-acquisition.json` and `full-log-acquisition.json` identify retained originals and hashes. The audit scripts use only these files; they do not make inference calls.

Performance is independently reconstructed from outcomes: mean correctness within each question, then equal weight across questions having a completed trial, as in the source's reduction. This differs from pooling all completed trials when some questions have fewer returns. Published scores and the individual correct/completed counts are both retained below. Failed API returns do not become correct answers.

Model release dates, parameter sources and shared scenarios are in [model evidence](epoch-native-final-models.md).
