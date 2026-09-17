# GPQA Diamond: original reconstruction

Work unit is one uniformly weighted Diamond question. The baseline is the second expert validator: a contractor holding or pursuing a PhD in the question's own scientific domain, who answered the revised question and scored **81.31%**. This replaces the earlier non-expert-validator baseline, which scored 22.05% — below the 25% four-choice guessing rate, so that human did not do the task and no comparison against them was meaningful. Re-anchored 2026-09-14.

## Human evidence

[The original paper, §2.1, §2.3, §3.1 and Appendix A.5.2](https://arxiv.org/html/2311.12022v1) describes the pipeline: a question writer drafts a question, a first expert validator in the same domain answers it and gives feedback, the writer revises, and a **second expert validator** answers the revised question. Expert validators are hired only if they hold or are pursuing a PhD; they may use Google provided they say so, must write an explanation of their reasoning, and after the correct answer is revealed must give feedback and suggest revisions. On the Diamond subset they reported sufficient expertise on 97.0% of validations. There is no minimum-time instruction for experts, unlike the 15 minutes required of non-experts.

The second expert validator is the right human for these rows on three counts. They answered the **revised** question, which is the text the AI is scored on. Their accuracy is measured on the same 198 questions. Their self-reported time is recorded per question in the released data.

The [public GPQA Diamond CSV distributed by OpenAI's evaluation authors](https://openaipublic.blob.core.windows.net/simple-evals/gpqa_diamond.csv), saved as `agent-work/sources/epoch/gpqa_diamond.csv`, retains the validation columns for both experts and all three non-experts. Using `Validator Answered Correctly_EV_2` and `Self-reported time (minutes)_EV_2` across all 198 records, with no filtering of slow times or incorrect answers:

| Quantity | Unit | Value |
|---|---|---|
| Second-expert accuracy | fraction correct | 0.8131 |
| Second-expert correct | count | 161 |
| Second-expert attempts | count | 198 |
| Second-expert mean time | s | 1560.91 |
| Second-expert median time | s | 1200 |
| Distinct second-expert validators | count | 32 |

161/198 = 81.3131% reproduces the paper's Table 2 figure of 81.3% for the Diamond set exactly. `human_time` is 1,560.909090909091 seconds (26.02 minutes), the mean over all 198 attempts, matching the accuracy denominator. 48 of the 198 reports are under 15 minutes; the range is 2 to 360 minutes.

**The 81.31% is biased upward and the paper says so.** Diamond admits a question only when the first expert validator answered it correctly, and either the second expert also answered correctly or the second expert's error was a mistake they clearly described after seeing the answer. `Validator Answered Correctly_EV_1` is therefore 1 on all 198 records, so pooling both experts (359/396 = 90.66%) measures the selection rule, not expert skill; do not use that number. The second expert's 81.31% is the only expert measurement on this question set that the selection does not force. The paper's own guidance (§3.2) is that true expert accuracy on Diamond lies between the unselected extended-set figure of **64.8%** and Diamond's 81.3%. Within Diamond, removing the single question the second expert judged flawed rather than mis-answered moves 81.31% to 81.73%; the paper's analogous "discounting clear mistakes" adjustment gives 73.6–76.4% on the extended set, and inside Diamond it is definitionally near 100% (99.5%) because clear-mistake questions are exactly what the selection admits, so it carries no information here.

Two things the time measures that the AI's work does not: the expert also writes an answer explanation and, after the answer is revealed, feedback and suggested revisions. The 26-minute mean is therefore an upper bound on time-to-answer. It is self-reported, not instrumented. `comparison_issues` carries `different_task`, `different_inputs_or_tools` (the expert may use Google) and `different_assessment`.

`human_cost_usd` is 25.1313: the paper's §2.2 schedule pays the second expert validator a $10 base, a $10 bonus per correct answer, and a $7 flat bonus for every expert validation after revision, so $10 + $10 x 0.813131 + $7. The $10 useful-feedback and $5 difficulty bonuses go to the first expert validator, not the second.

### Labelling against this baseline

Under the `performance_vs_human` rule in `../COLUMNS.md` — half the better side's score above the chance floor — the expert sits 56.31 points above the 25% four-choice floor, so an AI needs **53.16%** to have basically done the job. Rows below that are withheld to `agent-work/removed/excluded.csv`. `far_above` would need the AI more than 112.6 points above chance, which a four-choice benchmark cannot reach, so no GPQA row can carry it. Between the floor and the expert score, a difference within five percentage points of 81.31% is treated as broadly comparable (`match`, 76.31-86.31%), as in the earlier GPQA entries; below that band is `below` and above it is `above`.

## AI workload

[Epoch's original output-length release](https://epoch.ai/data-insights/output-length), linked `scatter_data.csv`, reports mean output, including any reasoning, and best accuracy across scorers. It does not report input. We reconstruct the 198 input questions and four choices using the [Epoch researcher's evaluator](https://gist.github.com/tadamcz/a61515465e34a3c66f3a78673502bc3f), dated February 3, 2025 in the downloaded GitHub API history. It supplies a short step-by-step multiple-choice instruction. We count text with each model family's tokenizer, then add **12 assumed chat-wrapper positions**. Exact random choice ordering, spacing and hosted-provider wrappers are not recovered. Thus compute is `derived_assumed_inputs`, not a claim to exact logged token totals.

Tokenizer sources: [original Qwen tokenizer](https://huggingface.co/Qwen/Qwen2.5-32B-Instruct/resolve/main/tokenizer.json), [original DeepSeek tokenizer](https://huggingface.co/deepseek-ai/DeepSeek-V3-0324/resolve/main/tokenizer.json), and [public unmodified Llama distribution](https://huggingface.co/NousResearch/Meta-Llama-3-70B-Instruct/resolve/main/tokenizer.json). We did not accept a gated model agreement. These tokenizer copies are retained locally. Input means are Qwen273.8081, DeepSeek256.5202 and Llama269.7071. Changing the wrapper by 20 tokens changes total compute by at most 3.5% in these rows.

FLOPs = (reconstructed input + reported mean output) × twice reported active parameters. It omits context-dependent attention, which `compute_flops` carries separately (`research/attention-correction.md`), and counts no external scorer as a task-solving helper. The evaluator is a single generation followed by answer-choice scoring. No raw attempt count is inferred from decimal scores; `ai_attempts=not_applicable` for these normalized benchmark aggregates. The per-point input means, source outputs and coefficients are listed below.

Individual arithmetic and source identifiers follow in the generated appendix.

<!-- generated-point-appendix -->

## reas-epoch-gpqa-llama3-70b

Model: Meta-Llama-3-70B-Instruct. Source: https://epoch.ai/data-insights/output-length; scatter_data.csv Identifier=Meta-Llama-3-70B-Instruct, Benchmark=GPQA diamond; performance: Best score (across scorers).

Inputs/accounting: `{"accuracy": 0.4056186868686868, "input": 269.7070707070707, "output": 306.3787878787879}`.

Counted tokens per work unit = 576.0858586; coefficient = 1.4e+11 FLOPs/token; product = **8.0652020202e+13 FLOPs**. Human = 1560.909090909091 seconds. AI accuracy 40.5619%; second expert validators answered 161/198 correctly (81.31%). Diamond selection forces the first expert to be correct, so 81.31% is biased upward; four-choice guessing is 25%.

## reas-epoch-gpqa-qwen25-32b

Model: Qwen2.5-32B-Instruct. Source: https://epoch.ai/data-insights/output-length; scatter_data.csv Identifier=qwen2.5-32b-instruct, Benchmark=GPQA diamond; performance: Best score (across scorers).

Inputs/accounting: `{"accuracy": 0.4608585858585858, "input": 273.80808080808083, "output": 560.4191919191919}`.

Counted tokens per work unit = 834.2272727; coefficient = 6.5e+10 FLOPs/token; product = **5.42247727273e+13 FLOPs**. Human = 1560.909090909091 seconds. AI accuracy 46.0859%; second expert validators answered 161/198 correctly (81.31%). Diamond selection forces the first expert to be correct, so 81.31% is biased upward; four-choice guessing is 25%.

## reas-epoch-gpqa-v3-0324

Model: DeepSeek-V3-0324. Source: https://epoch.ai/data-insights/output-length; scatter_data.csv Identifier=DeepSeek-V3-0324, Benchmark=GPQA diamond; performance: Best score (across scorers).

Inputs/accounting: `{"accuracy": 0.6761363636363636, "input": 256.520202020202, "output": 1162.767676767677}`.

Counted tokens per work unit = 1419.287879; coefficient = 7.4e+10 FLOPs/token; product = **1.0502730303e+14 FLOPs**. Human = 1560.909090909091 seconds. AI accuracy 67.6136%; second expert validators answered 161/198 correctly (81.31%). Diamond selection forces the first expert to be correct, so 81.31% is biased upward; four-choice guessing is 25%.
