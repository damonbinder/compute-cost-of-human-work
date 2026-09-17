# Qwen2.5-Math-1.5B-Instruct: a later GSM8K evaluation

## reas-gsm8k-qwen25math15b-batched

Solve one representative GSM8K test question, giving a numerical answer after step-by-step reasoning, with one sampled response and no calculator or model helper. The original evaluator covers all 1,319 test questions and reports **1,130 correct (85.67%)**. Human comparison: English-native adults with at least a high-school diploma, permitted a calculator, with **84%** accuracy on a separate random 50-question GSM8K sample. Human time is an estimated **60 seconds per question**, transferred from a reported five-minute median five-question batch.

This is the [DrEternity evaluator at commit bf15b2dbbd2f493b65c855e41180082f7acfa353](https://github.com/DrEternity/gsm8k-post-training/tree/bf15b2dbbd2f493b65c855e41180082f7acfa353), retained commit date May 10, 2026. It evaluates the released Qwen model without further tuning it. It is not the original Qwen team's release benchmark. The surrounding repository's SFT/GRPO experiments are separate models and excluded.

### What the output counts mean

The original README lists 301 average output tokens and 4.1% truncation, but the retained native metrics file says 512 average and 1,319 truncated. The source code explains the latter: it measures the returned tensor width minus **padded** input width. It does not find each response's EOS. Thus shorter finished responses are counted with appended padding. The truncation number cannot mean every natural response was cut off, and neither summary is silently treated as an independently verified semantic response length. The two numbers could coexist if 301 describes natural responses and 512 the padded batch tensor, but the README does not release the per-response counts needed to confirm that distinction.

For computation, this padding can still be real work. The evaluator pins **Transformers 5.3.0**, uses ordinary Hugging Face `model.generate`, and passes left-padded batches to an SDPA model. Original `generation/utils.py` `_sample` continues forwarding the full batch until every sequence ends, replacing finished sequences' emitted tokens with padding after the forward. It does not remove their rows from the neural batch. The rounded mean tensor extension of 512, together with the 512 maximum, places the mean returned width between approximately 511.5 and 512. The central estimate therefore uses **512 generation iterations** as source-informed batch work, not an assumed response-length cap. A 511.5-iteration sensitivity changes cost by about 0.08%.

The first iteration uses the prompt prefill to emit its token; only **511 subsequent cached forwards** are required. The last emitted token is not forwarded again. Requirements and native counters strongly support this interpretation, though no individual responses, execution trace or original environment lock beyond requirements are retained. The README's 301 is kept only as a counterfactual processing scenario; natural response length is not established.

### Input order and batches

The exact evaluator system prompt and released Qwen chat template are applied to the [original OpenAI GSM8K test JSONL](https://github.com/openai/grade-school-math/blob/master/grade_school_math/data/test.jsonl), using the original model tokenizer. All 1,319 questions enter the reconstruction. Their unpadded input mean is **96.3078 tokens**, maximum 223.

The loader first looks for local `data/processed/sft_test.jsonl`, then falls back to the original Hugging Face test order. No local test file is released. The retained preprocessing script creates a different training/validation directory and does not establish a shuffled test set. The central assumption is the fallback test order and default batch size 512, also shown without override in the documented example command. This produces three batches: 512 questions padded to 176 tokens, 512 padded to 176, and 295 padded to 223. The input and decoder workload is an estimated reconstruction, not a claim that these were logged batch boundaries.

Twenty seeded shuffled-order scenarios give FLOPs 0.7–2.6% higher. Batch size 32 with the same processing width gives about 4% lower cost; fully compact input about 11.8% lower. Those scenarios isolate prefill grouping while retaining the observed nearly-512 tensor-extension evidence. They are not predictions of how response stopping would change if the evaluation were rerun with different batch sizes.

The calculation retains 12 randomly selected original questions for inspection. They involve ordinary multi-step arithmetic: ticket/popcorn costs, percentages, work rates, division among children, and money needed after contributions. Some require keeping track of leftovers or repeated doubling. A minute for an adult reading and calculating with a calculator is plausible; no special mathematics expertise is assumed.

### Architecture and operations

The original released config specifies 28 decoder layers, width 1536, feed-forward width 8960, 12 query heads, two KV heads, head width 128, vocabulary 151936, and tied embeddings. Q/K/V biases and RMSNorm weights are included in the exact **1,543,714,304-parameter** architecture count. No parameter dimensions are estimated.

For each transformer layer, matrix weights participating in a forward are:

`W = 2*d*d + 2*d*(2*128) + 3*d*8960 = 46,792,704`.

For padded prompt width S and D=511 cached steps, the dominant matrix operations per question are:

- Transformer projections and gated feed-forward: `2*28*W*(S+D)`.
- Vocabulary head: `2*d*151936*512`. The exact 5.3.0 generation code sets `logits_to_keep=1`; the Qwen head consequently runs on only the last prefill position, then each incremental position. The tied input embeddings are lookups, not another dense vocabulary multiplication.
- Prefill attention: `4*28*d*S*S` for both QK and attention-value multiplication.
- Cached attention: `4*28*d*(D*S + D*(D+1)/2)`.

Central prefill attention counts dense masked work. SDPA backend selection may skip causal blocks; a triangular-prefill alternative is retained and changes total by only 0.14%. Small scalar operations such as RMSNorm, softmax, rotary embedding and activation functions are omitted; the estimate is dominated by neural matrix operations, not measured hardware counters.

| Component | Mean FLOPs per question |
|---|---:|
| Transformer linear layers | 1.8277538113e12 |
| Vocabulary head | 2.3897466470e11 |
| Dense prefill attention | 6.0503979161e9 |
| Cached attention | 3.8900478800e10 |
| **Total** | **2.1116793527e12** |

Mean `decoder_processed` positions are **697.5117513**, including prompt padding and finished-sequence forwards. `operation_count` is used because the output-head frequency and attention are calculated separately; simply multiplying every padded position by twice all parameters would charge unused vocabulary-head work in prefill. The model registry's conventional 2P coefficient remains available but is not the row's formula. No training, reward model, tool-integrated reasoning, evaluator-generated solutions, or extra attempts from unrelated repository experiments are included.

### Human timing and performance evidence

The original [GSM-Identity study](https://doi.org/10.1007/s10994-026-07029-7), §6, reports native-English Prolific participants with at least high-school education. Participants answered batches of five; median batch time was five minutes. Section 6.3 and Table 8 isolate the answer test's 50 unmodified GSM8K questions and report 84% accuracy. Figure 5b explicitly allows calculators and forbids ChatGPT or similar AI tools. This is a numerical-answer task, unlike the paper's separate equivalence tests.

The timing sentence covers the paper's three studies and modified as well as original questions; it does not publish a separate median for unmodified GSM8K answer trials. Dividing the reported batch median by five gives a **60-second per-question transfer estimate**, not a measured individual-question median or mean. We keep that central value because task inspection supports the scale and there is no grounded way to subtract time for the transformed expressions. A 30–90-second range is a transfer scenario. Payment per hour is not used to infer time.

`human_time_evidence=transferred_timings`, `human_time_method=estimated`, and `human_time_statistic=point_estimate`. The source does not establish how many recorded trials contribute to its common median, so `human_attempts` is blank; `human_time_subset=all` includes the contributing outcomes rather than selecting successful answers. The 50-question performance sample must not be entered as the timing-donor count.

AI 85.67% and the observed human 84% are classified **match** as a broad performance comparison. They are different sample sets and protocols (`different_assessment`); the human may use a calculator whereas this evaluator has no tool call (`different_inputs_or_tools`). The source's numeric extractor uses boxed/####/last-number fallbacks and tolerance1e-3, so the success claim concerns final numeric answers, not audited reasoning quality. The native metrics report four unextractable answers and 50 last-number fallbacks; absent responses prevent an independent regrade.

### Model identity and reproduction

The [Qwen team's announcement](https://qwenlm.github.io/blog/qwen2.5-math/), dated **September 19, 2024**, explicitly releases Qwen2.5-Math-1.5B-Instruct. Earlier September16–18 upload commits do not by themselves establish public availability; use the original release announcement date. Company: Alibaba. This is the math-specialized instruction model, not Qwen2.5-1.5B-Instruct or a tuned checkpoint from the evaluator.

Run `python research/qwen-gsm8k/recompute.py --sources agent-work/sources/qwen-gsm8k --output /path/to/new.json` after installing `tokenizers`. It reads source config/text and computes arithmetic; it never imports or executes the evaluator, Transformers, torch or a model. Output must be new and outside sources. Retained source manifest and calculation hashes support replay. The original examples, tokenizer and task order are included; no weights or large datasets are required.
