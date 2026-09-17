# Cost-of-Pass: single-attempt arithmetic and contextual QA

Thirty points cover three source task samples and ten models. Original sources: https://github.com/mhamzaerol/Cost-of-Pass and https://huggingface.co/datasets/CostOfPass/benchmark. Paper v2 is retained in `agent-work/sources/cost-of-pass/paper.pdf`. Per-model directories were queried directly, avoiding the truncated root listing. All VanillaPromptMethod full_records, matching scores and metadata are retained under `agent-work/sources/cost-of-pass/runs/`; manifests identify original HF paths. `agent-work/sources/cost-of-pass/summary.json` gives exact aggregate inputs. The 128 unique question records inspected for each task are retained in `agent-work/sources/*-items.json`.

## Scope and compute

Each coordinate describes one question attempt. Each native result set has exactly 128 question indices repeated eight times, 1024 completed records, one prompt/response per record and a unique matching score uid. We average all attempts, including incorrect answers and parsing failures. We do not divide token use by accuracy, compute a cost-of-pass, choose the cheapest successful run or include eight attempts in a one-attempt total.

Retained `litellm.py` reads `response.usage.prompt_tokens` and `completion_tokens`, falling back to tokenization only if the usage attribute is absent. Records preserve the unified input/completion totals, not the underlying provider response object. We use num_prompt_tokens + num_completion_tokens, not num_input_tokens (question text only) or num_answer_tokens (extracted short answer). OpenAI completion totals include hidden reasoning in their completion breakdown; see https://github.com/openai/openai-python/blob/main/src/openai/types/completion_usage.py, retained as `openai-completion-usage.py`. Do not add reasoning a second time. Together R1 reasoning is included in the source generation log, and native completion use is retained rather than retokenizing only the final short answer. Source records do not retain a cache breakdown. Vanilla prompting does not request reuse of the experiment's cached generation records, unlike its self-refinement/majority-voting implementations. The short prompts also do not support inventing a large prompt-cache correction.

Shared model coefficients are reused as authorized, with exact revision matching. In particular the endpoint is o1-2024-12-17, not a December 5 product alias; GPT-4o is the May 13 snapshot and Sonnet the June 20 snapshot. Together's named Llama Turbo endpoints map to the corresponding instruct weights; execution precision does not change two-operations-per-multiply-add counting. DeepSeek-R1 is the January model, not the later 0528 version. All ten matching records already exist in production. The included models.csv is an unchanged dependency copy, not proposed replacements. Closed-model parameter assumptions remain derived_assumed_inputs; open reported-size recipes are derived_supported_inputs.

## Scoring

VanillaPromptMethod extracts the last <answer>...</answer> span. MathExpressionMatch or MultipleChoiceMatch then scores that extracted value. Explanations are optional, but all generated explanation/reasoning tokens cost compute. Human baselines concern a correct numerical or choice answer, not XML-tag compliance, hence different_assessment. For example, Llama3.1-8B has 31 blank extracted addition answers among its 108 scored failures, but also clear numerical mistakes such as 36+4=76; the below classification is not solely a parsing artifact. Scores are retained rather than repaired after inspecting text.

## twodigitaddition-human-time

Task inspection finds 128 operands pairs in 0–98, only 104 with both operands at least 10. Exactly 64 require a units carry; one contains zero. Mean sum is 97.484375, range 11–193. The name TwoDigitAddition is therefore broader than literal two-two-digit addition. Generic elementary single-digit fact fluency does not establish this task's duration.

Original adult production evidence: Ashkenazi and Najjar (2018), https://www.nature.com/articles/s41598-018-27763-w, Results / Reaction time and Methods / Complex calculations; Table 1 at https://www.nature.com/articles/s41598-018-27763-w/tables/1. Retained HTML includes the table. Low-anxiety participants averaged 5.964 seconds and high-anxiety participants 8.916 seconds. All their sums were 104–169, with no zero digits, fives, repeated operands or easy ties, so that study is harder than this mixed CoP sample. Its response time excludes the subsequent strategy interview. It is not a direct timed observation of these 128 questions.

Best estimate: 6 seconds to read, mentally add and enter a short answer. This transfers the production timing scale while allowing the easier operands to offset a modest entry/check step. The exact 6-second selection is judgment, not a measured mean. Study groups were selected by anxiety and had only about 73–84% accuracy on their harder items; we do not transfer that rate unchanged to this easier sample. The intended numerate-adult baseline is broadly reliable routine addition.

**Range: 5.61 to 8.92 seconds.** Both bounds are the donor study's own two group
means, adjusted only for what separates its problem set from this one. Its
low-anxiety mean, 5.964 s, is oral production on an all-carry set; exactly 64 of
these 128 items need no units carry, and
[Klein et al. (2010)](https://link.springer.com/article/10.1186/1744-9081-6-70)
measure the carry premium at 247 ms on 1,855 ms, 13.3%, so an evenly split set runs
at 0.5 + 0.5/1.133 = 0.941 of an all-carry mean: 5.964 x 0.941 = **5.61 s**. That is
the floor and it is a conservative one, because it prices only the carry share of
the easier mix and not the 24 items with an operand below 10. The ceiling is the
high-anxiety mean taken whole, **8.92 s**: that group's items are harder than these,
and the read-and-enter step the oral protocol excludes is what the central assumes
the easier operands offset. The 6-second central sits near the bottom of that band,
which is the note's own position that the two adjustments cancel. AI near 100% is judged broadly comparable; Llama3.1-8B's 89.45% with numerous real calculation mistakes is below. This broad performance judgment is a reviewable assumption, not a fabricated human success count.

## gsm8k-human-time

The source loader uses GSM8K test and extracts the answer after ####. Actual sampled questions average 47.8047 whitespace words. Inspected examples span simple repeated multiplication, halving a budget then subtracting, rounding three prices before multiplying quantities, a 24-month changing subscription price, and a score difference with three components. The output is a number; long written explanations are optional.

The strongest human anchor is Negi, Puccetti and Esuli (2026), GSM-Identity: https://link.springer.com/article/10.1007/s10994-026-07029-7. Original PDF and extracted text are retained as `agent-work/sources/gsm-identity.pdf/txt`; Figure 5b was visually inspected. Section 6 requires native English and at least a high-school diploma, not professional mathematics credentials. It reports a median five minutes per five-question batch across its human studies. Section 6.3 randomly samples 50 original GSM8K questions and their three modified versions. Table 8 gives 84.0% human accuracy on the original questions. Figure 5b permits calculators for basic operations and prohibits AI assistance. The baseline is therefore typical high-school-educated adults with calculator access, not an expert tutor and not unassisted mental arithmetic.

Best estimate: **60 seconds** per attempt, from 300 seconds divided across five questions. This is a transfer of a reported batch timing, not a measured per-question median or mean: the paper does not separate timing by original/modified question or study, and it reports no per-item timing data. Set transferred_timings / estimated / point_estimate, with no invented timing-attempt sample. The human-accuracy question count of 50 does not establish the number of attempts underlying this timing summary. Known calculator access and nonidentical assessment samples are flagged in the CSV.

The earlier Zhang et al. (2024) lead, https://arxiv.org/abs/2405.00332 section 3.2.2, reports 14 annotators averaging 4.07 correct answers in 15 minutes. Its 900/4.07 = 221.13 seconds is session effort per correct completion, including possible failed or unfinished work, not single-attempt time. It is retained as context but does not determine the chosen value. The initial 180-second judgment based on this throughput has been superseded by the more directly relevant batch-timing study.

**Range: 60 to 186 seconds, with the central as the floor.** Zhang's throughput is
not a different quantity once the accuracy is divided out. Fourteen annotators
averaged 4.07 correct in 900 seconds; at GSM-Identity's measured 84.0% human
accuracy on original GSM8K that is 4.07/0.840 = 4.845 attempts, and 900/4.845 =
**185.8 s per attempt**, the same single-attempt quantity the central estimates.
Both published anchors for this quantity therefore sit at or above 60 seconds, the
batch pace is the lower of the two, and nothing in either study times a faster
attempt, so 60 seconds is the floor rather than the midpoint. The gap between the
two is a population and protocol gap: GSM-Identity's readers were native English
speakers with a diploma and a calculator working five-question batches, Zhang's
annotators worked a fifteen-minute session that includes whatever they abandoned.

Performance uses the observed 84% as a broad transfer. CoP GPT4o-mini at 88.6% is broadly comparable; Llama3.1-8B at 75.8% is below; the other models at roughly 91.9–94.4% are above. These are judgments about this evidence, not universal numerical cutoffs. The human sample is small and different from CoP's 128 questions; the same paper's Llama3.1-8B scores 84% under its generic prompt rather than CoP's 75.8%, showing that prompt/sample variation matters. We do not mechanically adjust human accuracy by that model difference. The source's stronger Llama3.3-70B at 98% is consistent with larger models exceeding this human baseline. Full audit: `research/GSM-IDENTITY-BASELINE-REVIEW.md`.

## bbq-human-time

Actual CoP questions average 39.5 words including choices. Of 128 gold answers, 126 are insufficient-information choices; two are supported named-person answers. This is not a balanced summary of all BBQ contexts. The two informative items ask which passenger needed more room and which person cried. The dominant task is reading a short vignette and declining an unsupported inference, not assessing whether the vignette itself is ethically acceptable.

Original BBQ paper: https://aclanthology.org/2022.findings-acl.165/, section 4 and Appendix D; retained `bbq-original.pdf/txt`. Its validation workers answered five multiple-choice examples per task. The authors estimate each task took up to two minutes, yielding an approximate upper allocation of 24 seconds per example. This is an author estimate, not a measured timing statistic; validation here is still answering the question, not authoring or revising five templates. Initial instruction reading adds a minute to the first task only.

Best estimate: 20 seconds per CoP question. About 10 seconds reads the 39.5 words at 240 words/minute, with another 10 seconds to identify whether information supports an answer, choose and check. This lies below the original author's up-to-24-second allowance and fits the shorter overwhelmingly under-informative sample. Reading rate and decision allowance are assumptions; method estimated and evidence assumed. There is no measured human timing sample to count.

**Range: 13 to 24 seconds.** The ceiling is the BBQ authors' own allowance, up to
two minutes for a five-example validation task, **24 s** per example. The floor
re-runs the same two-component budget at the decision term's end and leaves the
reading term alone: 39.5 words at 240 words/minute is 9.9 s, and 126 of the 128 gold
answers are the insufficient-information choice with all three options supplied, so
a reader who recognizes an under-informative vignette spends about three seconds
choosing and checking rather than ten: 9.9 + 3 = **13 s**. The reading term carries
no bound, because the word count is counted and the rate is the one the central
uses.

Original individual human accuracy was 95.7% on a different 300-item sample; 99.7% is majority vote and is not the single-human baseline. This supports match for o1 (95.0%) and Sonnet (92.6%), below for GPT4o (90.0%) and the 21–86% others. The five-point gap for GPT4o is a broad judgment, not a formal threshold test; the small task sample and asymmetric context mix limit precision. Both the answer-parser difference and the broader human assessment mix are identified in the row notes.

## lang-bbq-sonnet35

Native endpoint `claude-3-5-sonnet-20240620`, linked to `claude-3-5-sonnet-20240620`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 948/1024. Mean input 165.109375, completion 164.4404296875, total 329.5498046875 tokens. FLOPs = 329.5498046875 × 2e+11 = 6.590996094e+13. Local original: `agent-work/sources/cost-of-pass/runs/BBQ/claude-3-5-sonnet-20240620/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## lang-bbq-gpt4o

Native endpoint `gpt-4o-2024-05-13`, linked to `gpt-4o-2024-05-13`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 922/1024. Mean input 139.4375, completion 134.0439453125, total 273.4814453125 tokens. FLOPs = 273.4814453125 × 1e+11 = 2.734814453e+13. Local original: `agent-work/sources/cost-of-pass/runs/BBQ/gpt-4o-2024-05-13/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## lang-bbq-gpt4omini

Native endpoint `gpt-4o-mini-2024-07-18`, linked to `gpt-4o-mini-2024-07-18`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 546/1024. Mean input 139.4375, completion 136.71875, total 276.15625 tokens. FLOPs = 276.15625 × 1.6e+10 = 4.4185e+12. Local original: `agent-work/sources/cost-of-pass/runs/BBQ/gpt-4o-mini-2024-07-18/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## lang-bbq-o1

Native endpoint `o1-2024-12-17`, linked to `o1-2024-12-17`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 973/1024. Mean input 138.4375, completion 649.623046875, total 788.060546875 tokens. FLOPs = 788.060546875 × 1e+11 = 7.880605469e+13. Local original: `agent-work/sources/cost-of-pass/runs/BBQ/o1-2024-12-17/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## lang-bbq-o1mini

Native endpoint `o1-mini-2024-09-12`, linked to `o1-mini-2024-09-12`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 878/1024. Mean input 161.3984375, completion 588.92578125, total 750.32421875 tokens. FLOPs = 750.32421875 × 4e+10 = 3.001296875e+13. Local original: `agent-work/sources/cost-of-pass/runs/BBQ/o1-mini-2024-09-12/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## lang-bbq-o3mini

Native endpoint `o3-mini-2025-01-31`, linked to `o3-mini-2025-01-31`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 858/1024. Mean input 138.4375, completion 550.78515625, total 689.22265625 tokens. FLOPs = 689.22265625 × 4e+10 = 2.756890625e+13. Local original: `agent-work/sources/cost-of-pass/runs/BBQ/o3-mini-2025-01-31/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## lang-bbq-r1

Native endpoint `together_ai/deepseek-ai/DeepSeek-R1`, linked to `deepseek-r1`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 857/1024. Mean input 136.0546875, completion 591.8740234375, total 727.9287109375 tokens. FLOPs = 727.9287109375 × 7.4e+10 = 5.386672461e+13. Local original: `agent-work/sources/cost-of-pass/runs/BBQ/together_ai/deepseek-ai/DeepSeek-R1/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## lang-bbq-llama33-70b

Native endpoint `together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo`, linked to `llama-3.3-70b-instruct`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 871/1024. Mean input 167.0703125, completion 182.0400390625, total 349.1103515625 tokens. FLOPs = 349.1103515625 × 1.4e+11 = 4.887544922e+13. Local original: `agent-work/sources/cost-of-pass/runs/BBQ/together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## lang-bbq-llama31-405b

Native endpoint `together_ai/meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo`, linked to `llama-3.1-405b-instruct`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 878/1024. Mean input 167.0703125, completion 126.6240234375, total 293.6943359375 tokens. FLOPs = 293.6943359375 × 8.1e+11 = 2.378924121e+14. Local original: `agent-work/sources/cost-of-pass/runs/BBQ/together_ai/meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## lang-bbq-llama31-8b

Native endpoint `together_ai/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo`, linked to `llama-3.1-8b-instruct`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 220/1024. Mean input 167.0703125, completion 123.599609375, total 290.669921875 tokens. FLOPs = 290.669921875 × 1.6e+10 = 4.65071875e+12. Local original: `agent-work/sources/cost-of-pass/runs/BBQ/together_ai/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## reas-gsm8k-cop-sonnet35

Native endpoint `claude-3-5-sonnet-20240620`, linked to `claude-3-5-sonnet-20240620`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 967/1024. Mean input 171.4140625, completion 212.876953125, total 384.291015625 tokens. FLOPs = 384.291015625 × 2e+11 = 7.685820312e+13. Local original: `agent-work/sources/cost-of-pass/runs/GSM8K/claude-3-5-sonnet-20240620/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## reas-gsm8k-cop-gpt4o

Native endpoint `gpt-4o-2024-05-13`, linked to `gpt-4o-2024-05-13`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 942/1024. Mean input 146.984375, completion 253.8916015625, total 400.8759765625 tokens. FLOPs = 400.8759765625 × 1e+11 = 4.008759766e+13. Local original: `agent-work/sources/cost-of-pass/runs/GSM8K/gpt-4o-2024-05-13/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## reas-gsm8k-cop-gpt4omini

Native endpoint `gpt-4o-mini-2024-07-18`, linked to `gpt-4o-mini-2024-07-18`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 907/1024. Mean input 146.984375, completion 286.7333984375, total 433.7177734375 tokens. FLOPs = 433.7177734375 × 1.6e+10 = 6.939484375e+12. Local original: `agent-work/sources/cost-of-pass/runs/GSM8K/gpt-4o-mini-2024-07-18/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## reas-gsm8k-cop-o1

Native endpoint `o1-2024-12-17`, linked to `o1-2024-12-17`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 963/1024. Mean input 145.984375, completion 521.4228515625, total 667.4072265625 tokens. FLOPs = 667.4072265625 × 1e+11 = 6.674072266e+13. Local original: `agent-work/sources/cost-of-pass/runs/GSM8K/o1-2024-12-17/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## reas-gsm8k-cop-o1mini

Native endpoint `o1-mini-2024-09-12`, linked to `o1-mini-2024-09-12`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 948/1024. Mean input 162.7890625, completion 662.3662109375, total 825.1552734375 tokens. FLOPs = 825.1552734375 × 4e+10 = 3.300621094e+13. Local original: `agent-work/sources/cost-of-pass/runs/GSM8K/o1-mini-2024-09-12/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## reas-gsm8k-cop-o3mini

Native endpoint `o3-mini-2025-01-31`, linked to `o3-mini-2025-01-31`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 950/1024. Mean input 145.984375, completion 448.6064453125, total 594.5908203125 tokens. FLOPs = 594.5908203125 × 4e+10 = 2.378363281e+13. Local original: `agent-work/sources/cost-of-pass/runs/GSM8K/o3-mini-2025-01-31/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## reas-gsm8k-cop-r1

Native endpoint `together_ai/deepseek-ai/DeepSeek-R1`, linked to `deepseek-r1`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 956/1024. Mean input 143.265625, completion 667.5341796875, total 810.7998046875 tokens. FLOPs = 810.7998046875 × 7.4e+10 = 5.999918555e+13. Local original: `agent-work/sources/cost-of-pass/runs/GSM8K/together_ai/deepseek-ai/DeepSeek-R1/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## reas-gsm8k-cop-llama33-70b

Native endpoint `together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo`, linked to `llama-3.3-70b-instruct`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 943/1024. Mean input 174.40625, completion 201.64453125, total 376.05078125 tokens. FLOPs = 376.05078125 × 1.4e+11 = 5.264710938e+13. Local original: `agent-work/sources/cost-of-pass/runs/GSM8K/together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## reas-gsm8k-cop-llama31-405b

Native endpoint `together_ai/meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo`, linked to `llama-3.1-405b-instruct`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 962/1024. Mean input 174.40625, completion 211.736328125, total 386.142578125 tokens. FLOPs = 386.142578125 × 8.1e+11 = 3.127754883e+14. Local original: `agent-work/sources/cost-of-pass/runs/GSM8K/together_ai/meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## reas-gsm8k-cop-llama31-8b

Native endpoint `together_ai/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo`, linked to `llama-3.1-8b-instruct`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 776/1024. Mean input 174.40625, completion 237.240234375, total 411.646484375 tokens. FLOPs = 411.646484375 × 1.6e+10 = 6.58634375e+12. Local original: `agent-work/sources/cost-of-pass/runs/GSM8K/together_ai/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## extr-2digitadd-sonnet35

Native endpoint `claude-3-5-sonnet-20240620`, linked to `claude-3-5-sonnet-20240620`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 1024/1024. Mean input 114, completion 120.3291015625, total 234.3291015625 tokens. FLOPs = 234.3291015625 × 2e+11 = 4.686582031e+13. Local original: `agent-work/sources/cost-of-pass/runs/TwoDigitAddition/claude-3-5-sonnet-20240620/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## extr-2digitadd-gpt4o

Native endpoint `gpt-4o-2024-05-13`, linked to `gpt-4o-2024-05-13`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 1021/1024. Mean input 95, completion 121.1259765625, total 216.1259765625 tokens. FLOPs = 216.1259765625 × 1e+11 = 2.161259766e+13. Local original: `agent-work/sources/cost-of-pass/runs/TwoDigitAddition/gpt-4o-2024-05-13/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## extr-2digitadd-gpt4omini

Native endpoint `gpt-4o-mini-2024-07-18`, linked to `gpt-4o-mini-2024-07-18`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 1023/1024. Mean input 95, completion 66.8564453125, total 161.8564453125 tokens. FLOPs = 161.8564453125 × 1.6e+10 = 2.589703125e+12. Local original: `agent-work/sources/cost-of-pass/runs/TwoDigitAddition/gpt-4o-mini-2024-07-18/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## extr-2digitadd-o1

Native endpoint `o1-2024-12-17`, linked to `o1-2024-12-17`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 1024/1024. Mean input 94, completion 292.64453125, total 386.64453125 tokens. FLOPs = 386.64453125 × 1e+11 = 3.866445312e+13. Local original: `agent-work/sources/cost-of-pass/runs/TwoDigitAddition/o1-2024-12-17/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## extr-2digitadd-o1mini

Native endpoint `o1-mini-2024-09-12`, linked to `o1-mini-2024-09-12`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 1019/1024. Mean input 111, completion 419.1552734375, total 530.1552734375 tokens. FLOPs = 530.1552734375 × 4e+10 = 2.120621094e+13. Local original: `agent-work/sources/cost-of-pass/runs/TwoDigitAddition/o1-mini-2024-09-12/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## extr-2digitadd-o3mini

Native endpoint `o3-mini-2025-01-31`, linked to `o3-mini-2025-01-31`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 1024/1024. Mean input 94, completion 229.26953125, total 323.26953125 tokens. FLOPs = 323.26953125 × 4e+10 = 1.293078125e+13. Local original: `agent-work/sources/cost-of-pass/runs/TwoDigitAddition/o3-mini-2025-01-31/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## extr-2digitadd-r1

Native endpoint `together_ai/deepseek-ai/DeepSeek-R1`, linked to `deepseek-r1`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 1024/1024. Mean input 91, completion 216.4560546875, total 307.4560546875 tokens. FLOPs = 307.4560546875 × 7.4e+10 = 2.275174805e+13. Local original: `agent-work/sources/cost-of-pass/runs/TwoDigitAddition/together_ai/deepseek-ai/DeepSeek-R1/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## extr-2digitadd-llama33-70b

Native endpoint `together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo`, linked to `llama-3.3-70b-instruct`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 1023/1024. Mean input 122, completion 59.5185546875, total 181.5185546875 tokens. FLOPs = 181.5185546875 × 1.4e+11 = 2.541259766e+13. Local original: `agent-work/sources/cost-of-pass/runs/TwoDigitAddition/together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## extr-2digitadd-llama31-405b

Native endpoint `together_ai/meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo`, linked to `llama-3.1-405b-instruct`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 1021/1024. Mean input 122, completion 75.1845703125, total 197.1845703125 tokens. FLOPs = 197.1845703125 × 8.1e+11 = 1.59719502e+14. Local original: `agent-work/sources/cost-of-pass/runs/TwoDigitAddition/together_ai/meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## extr-2digitadd-llama31-8b

Native endpoint `together_ai/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo`, linked to `llama-3.1-8b-instruct`. 128 items × 8 runs = 1024 completed one-call attempts; all are included. Correct: 916/1024. Mean input 122, completion 110.1220703125, total 232.1220703125 tokens. FLOPs = 232.1220703125 × 1.6e+10 = 3.713953125e+12. Local original: `agent-work/sources/cost-of-pass/runs/TwoDigitAddition/together_ai/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo/full_records/dataset.parquet` and its sibling score directory; linked by uid.

## Reproduction

With pyarrow installed, run `python research/cost-of-pass/recompute.py agent-work/sources/cost-of-pass --output /tmp/cop-summary.json` from the published dataset directory. The source directory is explicit; the script does not modify retained inputs.

## Contributing timing samples

GSM-Identity reports five-question batch timings across its studies without the number of contributing attempts. The count is blank; the subset is all, since no successful-only timing restriction is stated. Its separate 50-question accuracy sample does not establish a timing count.

For the oral-addition donor, Ashkenazi–Najjar report 48 recruits and 48 problems per person, but the exclusions and analysis degrees of freedom do not reconcile. The count is blank rather than an assumed 2,160 or 2,304 attempts; the analyzed timings are not described as correct-only. The original article XML and text are retained in agent-work/sources/cost-of-pass/addition-original.xml and addition-original-extract.txt. The earlier addition-study.html request returned a browser challenge.
