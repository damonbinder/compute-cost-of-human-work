# ARC-AGI-2: GPT-5.2 inference budgets

Cache reads are not separated in the retained records. The central recipe treats each reported prompt as newly processed. A provider cache hit would reduce that parameter-multiplication workload; no cache fraction is imputed.

One new output grid, with two independent responses at the specified reasoning effort. These four records use the same joining, duration filter and weighting procedure as the reviewed xhigh record. Each setting retains all its own complete-response cases with human observations. Case sets differ, so these are not exact paired estimates of the effect of changing effort. They are valid within-row AI/human mixtures, and the retained per-case data permits a common-case analysis separately.

Original human records: https://huggingface.co/datasets/arcprize/arc_agi_2_human_testing ; original puzzles: https://github.com/arcprize/ARC-AGI-2/tree/main/data/evaluation . AI run folders are linked below. Sources retain all files and tree inventories, not only successful cases.

Human time is the arithmetic mean of source duration_seconds for Public Eval task views >5 seconds, following https://arxiv.org/html/2505.11831v2#S4.SS3 . Include failures and no-submission views above that threshold; apply no upper trimming. The source allows revisits and rule reuse across test inputs, so these recorded task durations need not be uninterrupted work. Humans use a visual editor with feedback and can submit more than two answers. Human skill is typical, not expert by virtue of eventual puzzle success.

Join each non-null AI response by metadata.task_id and pair_index. Parse the actual test grid in the prompt and assert equality with the original puzzle input; recompute correctness from output grids. Require both distinct response slots for each included case. Count prompt_tokens plus completion_tokens once; reasoning is already inside completion. The metadata choices array stores messages, not extra calls. Native totals and reasoning decomposition are verified on every response. Missing response slots exclude the corresponding case; no claim about additional inaccessible retry workload is made.

Each case receives weight equal to its included human-view count. This common weighting is applied to AI cost and AI best-of-two success; the human axes/outcome use ordinary observation means. A normalized benchmark observation does not imply an independently observed AI-attempt count equal to the human sample size: ai_attempts is not_applicable. FLOPs equal the mean tokens times the existing GPT-5.2 coefficient200B. The undisclosed parameter prior, the assumed attention shape behind `research/attention-correction.md` and missing internal-event history remain limitations; derived_assumed_inputs is appropriate.

To reproduce from the dataset directory: `python3 research/arc-settings/recompute.py agent-work/sources/arc-settings --effort low --output-dir /tmp/arc-low`. Replace low with none, medium or high. Only the Python standard library is required. Retained research/<effort>/summary.json and verified-pairs.json give the complete derivation.

## reas-arcagi-v2-gpt52-none

Original run: https://huggingface.co/datasets/arcprize/arc_agi_v2_public_eval/tree/main/gpt-5-2-2025-12-11-thinking-none . 120 task files contain 334 non-null responses and 0 null slots. No metadata/array-index mismatches found; all actual prompt grids and outcome flags checked.

Selected 161 cases, 322 AI responses and 1240 human views. Human mean 255.210521774 seconds; 20 brief/zero views excluded. Input 15132.188709677 + completion 2528.938709677 = 17661.127419355 tokens; completion contains 0.000000000 reasoning tokens. FLOPs 3.53222548387e+15.

AI weighted successes 0/1240 (0.00%); human 773/1240 (62.34%). Classify below: even the high effort result is materially below the selected human baseline. None's zero successes is retained; mostly failing tasks are permitted and still have measured costs.

## reas-arcagi-v2-gpt52-low

Original run: https://huggingface.co/datasets/arcprize/arc_agi_v2_public_eval/tree/main/gpt-5-2-2025-12-11-thinking-low . 120 task files contain 334 non-null responses and 0 null slots. No metadata/array-index mismatches found; all actual prompt grids and outcome flags checked.

Selected 161 cases, 322 AI responses and 1240 human views. Human mean 255.210521774 seconds; 20 brief/zero views excluded. Input 15132.188709677 + completion 12273.114516129 = 27405.303225806 tokens; completion contains 9674.359677419 reasoning tokens. FLOPs 5.48106064516e+15.

AI weighted successes 114/1240 (9.19%); human 773/1240 (62.34%). Classify below: even the high effort result is materially below the selected human baseline. None's zero successes is retained; mostly failing tasks are permitted and still have measured costs.

## reas-arcagi-v2-gpt52-medium

Original run: https://huggingface.co/datasets/arcprize/arc_agi_v2_public_eval/tree/main/gpt-5-2-2025-12-11-thinking-medium . 120 task files contain 333 non-null responses and 1 null slots. No metadata/array-index mismatches found; all actual prompt grids and outcome flags checked.

Selected 160 cases, 320 AI responses and 1231 human views. Human mean 255.471180341 seconds; 20 brief/zero views excluded. Input 15148.508529651 + completion 38855.755483347 = 54004.264012998 tokens; completion contains 36255.069861901 reasoning tokens. FLOPs 1.08008528026e+16.

AI weighted successes 317/1231 (25.75%); human 769/1231 (62.47%). Classify below: even the high effort result is materially below the selected human baseline. None's zero successes is retained; mostly failing tasks are permitted and still have measured costs.

## reas-arcagi-v2-gpt52-high

Original run: https://huggingface.co/datasets/arcprize/arc_agi_v2_public_eval/tree/main/gpt-5-2-2025-12-11-thinking-high . 119 task files contain 322 non-null responses and 8 null slots. No metadata/array-index mismatches found; all actual prompt grids and outcome flags checked.

Selected 153 cases, 306 AI responses and 1178 human views; the mean over those views is 252.788669779 seconds, 19 brief/zero views excluded. The row records the task-level 255.2105217741936 seconds over 1240 views instead, per [arc.md](../arc/arc.md#task-level-human-time); the success percentages below stay on these 153 cases. Input 14939.918505942 + completion 76219.089134126 = 91159.007640068 tokens; completion contains 73650.281833616 reasoning tokens. FLOPs 1.8231801528e+16.

AI weighted successes 442/1178 (37.52%); human 735/1178 (62.39%). Classify below: even the high effort result is materially below the selected human baseline. None's zero successes is retained; mostly failing tasks are permitted and still have measured costs.
