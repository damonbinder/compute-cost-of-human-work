# Short questions: LRM Token Economy

Four points pair a single typed question with GPT-5 or o3-mini at high reasoning effort. The [original collection](https://github.com/cpldcpu/LRMTokenEconomy/tree/11c9a66fb6c8745f765a176c3e2651e235c759b9) records five calls per selected question/model. These are repeated runs of two fixed questions, not a representative sample of arithmetic or logic problems. The two tasks were selected for their distinct reading and reasoning requirements before checking the answers.

The first question is “How much is 1+1?” The other gives four bridge-crossing times of 1, 3, 5 and 10 minutes, says the bridge supports four people, and asks how everyone can cross with one torch within ten minutes. All four can cross together. The bridge capacity differs from the familiar two-person puzzle; importing that puzzle's shuttle procedure would answer a different question.

## Original records and configuration

`output-gpt5.json` retains the author's August 23, 2025 runs; `output-o3m-o1m.json` retains the July 23 o3-mini runs. Each selected record contains five final answers, generation IDs, provider names, finish reasons, native completion-token counts and reasoning-token details. All twenty retained completed calls ended normally through the OpenAI provider. The result records do not retain retry histories. All ten arithmetic answers are 2, and all ten bridge answers explicitly send the four together in ten minutes. No LLM judge is needed to check those answers. Evaluation/judging calls elsewhere in the source are outside the answer-generation work unit.

GPT-5's original configuration is retained from `f0f1daa551f7d7712377ac9cf2a68f32fdffc32e`, the same day as the data; the source script is from `a938405c5b25d814af6d3f1c0fdd6c542cd9536e`. The o3-mini result was first committed at `c243c2df0bcc6481be643e6319c6513d7d639450`; its full configuration and querying script are retained. Both name high reasoning effort and a 30,000-token cap. Recorded usage, not that cap, determines compute. The configurations specify temperature0.7, but actual provider handling and any command-line override are not established by these result records. No temperature-dependent adjustment is made to recorded usage.

## Token accounting

The source records native `completion_tokens`, with reasoning already included. `completion_tokens_details.reasoning_tokens` is a breakdown, not additional usage. The displayed thinking text is not tokenized as a substitute for those counters.

The script wraps each task as `Please answer the following question: {question}\nAnswer:` in one user message, without an application system prompt for these configurations. Native input counters were not retained. We reconstruct the supplied text with `o200k_base` and add seven assumed message/framing positions. This is an input estimate; unknown provider-internal framing is not observed. Zero and64framing-position alternatives are included in the calculation. Full input processing is assumed; the source does not report cache usage. The prompt is short, so generated reasoning dominates all four estimates.

Multiply input plus native completion tokens by the existing model coefficient. GPT-5 uses the shared100B active-parameter estimate and o3-mini uses20B. Both are assumptions already identified in models.csv; they are not measurements inferred from these runs. Standard parameter-token arithmetic omits attention and small scalar operations; `compute_flops` carries the attention term separately (`research/attention-correction.md`). Mean/all/five attempts refers to the actual repeated-call cohort. All recorded attempts are included.

## Human time

Human time estimates a fresh reading and a brief correct typed answer from an ordinary numerate adult, without an AI assistant. It does not charge for copying a model's verbose explanation. Quality is the correct answer or sufficient crossing plan. The estimate targets the same quality as the recorded outputs, so performance is match by construction. There is no measured human comparison in this source.

For 1+1, use **three seconds**: about1–1.5seconds to read/recognize the short question and about1–1.5seconds to retrieve, type and submit the digit. The arithmetic is familiar; this is not a three-second mental-addition latency claim. The bounds are the same two components at their ends: one second to recognize the question and one to type the digit gives two seconds, while the full reading and retrieval allowance plus locating the field and submitting gives six.

For the bridge question, use **25seconds**: roughly15seconds to read its short paragraph, about5seconds to check the four-person capacity and slowest crossing time, and about5seconds to type a brief plan. These are task-inspection judgments, not measured subtotals or an empirical reading-speed transfer. A12–60second scenario allows faster reading or an initial distraction by the familiar two-person variant. Extended reproduction of the model's several-paragraph explanation is not required. Human evidence is assumed, method estimated, statistic point_estimate, and attempts/subset not_applicable.

## short-one-plus-one-gpt-5

GPT-5 high: native completions135,135,455,71,71tokens. Estimated mean total196.4tokens; **3.928e13FLOPs /3humanseconds**.

## short-bridge-torch-easy-10m-gpt-5

GPT-5 high: native completions1188,1517,3509,1196,5036tokens. Estimated mean total2576.2tokens; **5.1524e14FLOPs /25humanseconds**.

## short-one-plus-one-o3-mini-high

o3-mini high: native completions137,137,73,135,135tokens. Estimated mean total146.4tokens; **5.856e12FLOPs /3humanseconds**.

## short-bridge-torch-easy-10m-o3-mini-high

o3-mini high: native completions1432,1725,2029,942,1931tokens. Estimated mean total1698.8tokens; **6.7952e13FLOPs /25humanseconds**.

## Reproduction

With Python and tiktoken, run from the collection folder:

```sh
python research/lrm-token-economy/recompute.py --sources agent-work/sources/lrm-token-economy --models research/lrm-token-economy/model-inputs.csv --output /absolute/path/to/new-calculations.json
```

The script reads retained sources and frozen shared model inputs. It makes no API calls and requires a new output path outside sources. `calculations.json` retains per-call counters, response texts, original generation IDs, arithmetic and framing/human-time scenarios.
