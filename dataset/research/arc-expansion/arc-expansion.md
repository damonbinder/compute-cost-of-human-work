# ARC-AGI-2: additional model comparisons

Work unit: one new test grid, with two independent AI responses. Both axes and outcomes use the same distribution of test grids within each row. The source run folders contain different available case sets; these rows are not a controlled comparison on an identical cross-model sample.

Original human observations: https://huggingface.co/datasets/arcprize/arc_agi_2_human_testing . Original puzzles: https://github.com/arcprize/ARC-AGI-2/tree/main/data/evaluation . Include Public Eval task views longer than five seconds, the source rule in https://arxiv.org/html/2505.11831v2#S4.SS3 ; retain failures and no-submission views above that threshold. No upper duration trimming. Humans can revisit, receive feedback and submit more than two answers in a visual editor; AI sees text grids. Recorded duration can include interruptions. These are measured task-view timings, not an estimate from puzzle difficulty.

Match metadata task_id and pair_index, verify all training examples and test inputs against original puzzles, and rescore every answer grid. Include cases with both distinct response slots and human observations. Each case receives its human-view count as weight for AI compute and best-of-two success; human duration and success are ordinary observation means. AI attempt count is not_applicable for this normalized mixture, not equal to the human sample size. Null response slots exclude their cases; additional unlogged retry work is not measured.

Use native total_tokens. Gemini's total equals prompt plus visible completion plus reasoning; other providers' total equals prompt plus completion, which already contains reasoning. A zero reasoning breakdown is not evidence of zero thinking. Retained original benchmark adapters document the Gemini and Anthropic conversions. Anthropic summaries must not be retokenized and added again. Costs in dollars are not used to infer tokens. All rows use the shared model FLOPs/token coefficient; unavailable internal architectures and context-dependent attention are uncertainties in that conversion.

Cache reads are not separated in the retained records. The central recipe treats each reported prompt as newly processed. For the three Fireworks rows, both responses have identical prompts and the second usually starts milliseconds after the first finishes. Full-prefix processing is therefore a material assumption. Native token totals and the input_output category are preserved; cached attention remains outside the coefficient and is added back in `compute_flops` (`research/attention-correction.md`). The reported cost fields do not supply a recoverable cache split.

The source's Sonnet correctness flags are null on all 334 responses, but the answer grids are present. Recomputed exact-grid correctness supplies the result without an unknown classification. Other nonnull correctness flags agree with recomputation.

The publisher labels its GPT-5.4 folder gpt-5-4-high, while every native response calls the model galapagos-alpha and predates public release. The primary model_id follows that publisher identification, using the existing GPT-5.4 coefficient. Exact equivalence to the released revision is not established; this is a prerelease evaluation. The shared dated model record supplies the family coefficient and public release date, not an independently verified snapshot identity for this response. Opus 4.6 was also evaluated before release (February 3–4, 2026, versus February 5), as was Gemini 3 Pro Preview (November 14–15, 2025, versus November 18). Their native names identify the model family, but equivalence to the subsequently released revision is not independently established. Do not interpret model release dates as run dates.

Research folders retain verified-pairs.json and summary.json. Reproduce with standard-library Python: `python3 research/arc-expansion/recompute.py agent-work/sources/arc-expansion --folder FOLDER --model NATIVE_MODEL --output-dir /tmp/arc-recheck`. Per-row native names are below. This reads retained evidence and writes only to the requested output directory. source-hashes.json verifies the retained response files against original Hugging Face git object IDs.


## reas-arcagi-v2-opus46-max

Original run: https://huggingface.co/datasets/arcprize/arc_agi_v2_public_eval/tree/main/claude-opus-4-6-thinking-120K-max . Native model `claude-opus-4-6`.

117 task files; 319 retained responses and 3 null slots. Selected 152 cases, 304 responses and 1179 human views, whose mean is 249.547827820s; 14 brief views excluded. The row records the task-level 255.2105217741936 seconds over 1240 views instead, per [arc.md](../arc/arc.md#task-level-human-time); the success percentages below stay on these 152 cases.

Mean input 15373.134860, completion 107255.098388, reported reasoning breakdown 0.000000, total 122628.233249 tokens. Total includes completion reasoning; do not add the breakdown again. Multiply total by shared coefficient 200000000000 FLOPs/token = 2.45256466497e+16 FLOPs.

AI weighted successes 903/1179 (76.59%); human successes 741/1179 (62.85%). Best estimate: above; the observed gap is large enough to support the direction despite known protocol differences.


## reas-arcagi-v2-sonnet45-32k

Original run: https://huggingface.co/datasets/arcprize/arc_agi_v2_public_eval/tree/main/claude-sonnet-4-5-20250929-thinking-32k . Native model `claude-sonnet-4-5-20250929`.

120 task files; 334 retained responses and 0 null slots. Selected 161 cases, 322 responses and 1240 human views. Human mean 255.210521774s; 20 brief views excluded.

Mean input 15242.488710, completion 36993.770161, reported reasoning breakdown 0.000000, total 52236.258871 tokens. Total includes completion reasoning; do not add the breakdown again. Multiply total by shared coefficient 200000000000 FLOPs/token = 1.04472517742e+16 FLOPs.

AI weighted successes 165/1240 (13.31%); human successes 773/1240 (62.34%). Best estimate: below; the observed gap is large enough to support the direction despite known protocol differences.


## reas-arcagi-v2-gemini3pro

Original run: https://huggingface.co/datasets/arcprize/arc_agi_v2_public_eval/tree/main/gemini-3-pro-preview . Native model `gemini-3-pro-preview`.

116 task files; 324 retained responses and 0 null slots. Selected 156 cases, 312 responses and 1194 human views. Human mean 250.642279732s; 18 brief views excluded.

Mean input 15717.321608, completion 4446.033501, reported reasoning breakdown 43741.832496, total 63905.187605 tokens. Reasoning is additional to completion in this provider schema. Multiply total by shared coefficient 200000000000 FLOPs/token = 1.27810375209e+16 FLOPs.

AI weighted successes 319/1194 (26.72%); human successes 751/1194 (62.90%). Best estimate: below; the observed gap is large enough to support the direction despite known protocol differences.


## reas-arcagi-v2-gpt54-high

Original run: https://huggingface.co/datasets/arcprize/arc_agi_v2_public_eval/tree/main/gpt-5-4-high . Native model `galapagos-alpha`.

120 task files; 334 retained responses and 0 null slots. Selected 161 cases, 322 responses and 1240 human views. Human mean 255.210521774s; 20 brief views excluded. This run covers every public-evaluation case with human views, so its mean is also the task-level figure the other three rows now record, per [arc.md](../arc/arc.md#task-level-human-time).

Mean input 15259.233871, completion 48720.820161, reported reasoning breakdown 46121.241129, total 63980.054032 tokens. Total includes completion reasoning; do not add the breakdown again. Multiply total by shared coefficient 200000000000 FLOPs/token = 1.27960108065e+16 FLOPs.

AI weighted successes 917/1240 (73.95%); human successes 773/1240 (62.34%). Best estimate: above; the observed gap is large enough to support the direction despite known protocol differences.


## reas-arcagi-v2-kimi-k25

Original run: https://huggingface.co/datasets/arcprize/arc_agi_v2_public_eval/tree/main/kimi-k2.5 . Native model `accounts/fireworks/models/kimi-k2p5`.

120 task files; 334 retained responses and 0 null slots. Selected 161 cases, 322 responses and 1240 human views. Human mean 255.210521774s; 20 brief views excluded.

Mean input 15136.188710, completion 68730.641935, reported reasoning breakdown 0.000000, total 83866.830645 tokens. Total includes completion reasoning; do not add the breakdown again. Multiply total by shared coefficient 64000000000 FLOPs/token = 5.36747716129e+15 FLOPs.

AI weighted successes 132/1240 (10.65%); human successes 773/1240 (62.34%). Best estimate: below; the observed gap is large enough to support the direction despite known protocol differences.


## reas-arcagi-v2-dsv32

Original run: https://huggingface.co/datasets/arcprize/arc_agi_v2_public_eval/tree/main/deepseek-v3.2 . Native model `accounts/fireworks/models/deepseek-v3p2`.

120 task files; 332 retained responses and 2 null slots. Selected 159 cases, 318 responses and 1222 human views. Human mean 254.374644026s; 20 brief views excluded.

Mean input 15098.034370, completion 51061.716039, reported reasoning breakdown 0.000000, total 66159.750409 tokens. Total includes completion reasoning; do not add the breakdown again. Multiply total by shared coefficient 74000000000 FLOPs/token = 4.89582153028e+15 FLOPs.

AI weighted successes 45/1222 (3.68%); human successes 760/1222 (62.19%). Best estimate: below; the observed gap is large enough to support the direction despite known protocol differences.


## reas-arcagi-v2-glm5

Original run: https://huggingface.co/datasets/arcprize/arc_agi_v2_public_eval/tree/main/glm-5 . Native model `accounts/fireworks/models/glm-5`.

120 task files; 333 retained responses and 1 null slots. Selected 160 cases, 320 responses and 1231 human views. Human mean 254.142143786s; 20 brief views excluded.

Mean input 15194.411048, completion 60635.898457, reported reasoning breakdown 0.000000, total 75830.309504 tokens. Total includes completion reasoning; do not add the breakdown again. Multiply total by shared coefficient 80000000000 FLOPs/token = 6.06642476036e+15 FLOPs.

AI weighted successes 66/1231 (5.36%); human successes 768/1231 (62.39%). Best estimate: below; the observed gap is large enough to support the direction despite known protocol differences.

[Prompt-cache evidence and sensitivity](../cache-accounting/cache-accounting.md).
