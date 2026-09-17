# ARC-AGI-2 matched human and AI test cases

## reas-arcagi-v2-gpt52-xhigh

One test grid with two independent GPT-5.2 xhigh responses. Select cases having both retained responses and human task views lasting more than five seconds, following the source protocol. There are 112 such task-test pairs and 849 human observations. Both successful and unsuccessful cases are included. This is a subset comparison, not the official full-benchmark score.

Original AI records: [ARC Prize GPT-5.2 xhigh release](https://huggingface.co/datasets/arcprize/arc_agi_v2_public_eval/tree/main/gpt-5-2-2025-12-11-thinking-xhigh). Original human records: [ARC Prize human testing](https://huggingface.co/datasets/arcprize/arc_agi_2_human_testing). Puzzle definitions: [ARC-AGI-2](https://github.com/arcprize/ARC-AGI-2/tree/main/data/evaluation). Local copies are under agent-work/sources/; the tree inventories retain original file object hashes.

## Matching and weighting

The work unit is a test grid, not a whole task file, which can contain multiple test inputs. Join on task ID and metadata pair_index. Some AI files omit an earlier test case, so array position is not a reliable index. Five responses in four files have shifted positions. The target input in every retained prompt was checked against the metadata-selected original puzzle, and all retained correct flags reproduce against that puzzle's expected output. No score correction was needed after joining correctly.

A comparison samples from the recorded human observations. Each test case's AI token cost and binary best-of-two result therefore receive weight equal to its human observation count. Human time and success are ordinary means across the 849 human observations. Using the same weights on both sides avoids comparing different mixtures of puzzle difficulty. It does not create 849 independent AI runs: only 224 retained responses contribute. AI attempts is not_applicable for this normalized benchmark statistic.

`verified-pairs.json` retains every available pair, its included calls, workload and human summary. `summary.json` gives the selected aggregate. The standalone `recompute.py` verifies the exact test-input grid in each prompt, recomputes scores and derives these results; no old dataset estimate is used. It uses the Python standard library and accepts the retained sources directory as its argument:

```sh
python3 -B recompute.py /path/to/arc/sources
```

Run it from the research directory, or pass the script's full path. It writes `verified-pairs.json` and `summary.json` beside the script; an optional `--output-dir` sends those outputs elsewhere. It does not edit either CSV.

## Human time

Use the source duration_seconds for views lasting **more than five seconds**, following the [technical report, section 4.3](https://arxiv.org/html/2505.11831v2#S4.SS3). Include unsuccessful sessions and sessions with no submitted answer. Among the selected cases, this removes two zero-duration records and nine additional views of at most five seconds; all eleven have no submission. No upper-duration trimming is applied. Over this row's 112 matched cases the mean is 240.2007502944641 seconds across 849 observations. Source successful-submission counts establish human success, not the fraction with any submission.

### Task-level human time

Every row of `solve-an-arc-agi-2-test-grid` records **255.2105217741936 seconds** across **1240** human views. The six rows of the task each pair the same work — one ARC-AGI-2 public-evaluation test grid — against a human duration computed over whichever cases that model returned two complete responses for, so the duration was moving with the AI's response completeness and not with the job: 240.20 s over 112 cases for GPT-5.2 xhigh, 252.79 over 153, 249.55 over 152, 249.70 over 139 and 255.21 over 161. Damon ruled on 2026-09-16 that one task carries one human time.

The figure is the view-weighted mean over every public-evaluation test case with human views longer than five seconds, dropping the response-completeness filter from the human side while keeping it on the AI side. Taking the union of the runs' `verified-pairs.json` records gives 161 such cases and 1,240 views, which is exactly the set the GPT-5.4 run covers — every other run's human-view cases are subsets of it — so the pooled mean is that run's 255.2105217741936 seconds. Each row's AI and human *success* percentages still run over that row's own matched cases, because those are the outcomes that were actually paired; only the duration is task-level.

Two further rows joined the task on 2026-09-16, `reas-arcagi-v2-gemini3dt` and `reas-arcagi-v2-grok420`, which sat under their own `task_id` values from an earlier pass. They are the same benchmark and the same case-mix construction, built from the same ARC-AGI-2 human study and the same five-second view filter, and they now carry this duration too; their derivation is in [arc-modern-remaining.md](../arc-modern/arc-modern-remaining.md).

These are source-recorded task times. Participants sometimes revisited earlier tasks, as described in [section 4.4](https://arxiv.org/html/2505.11831v2#S4.SS4); the released totals do not establish uninterrupted active intervals. Humans may carry an inferred rule between test inputs of the same puzzle, while AI requests start independently. No arbitrary inactivity subtraction is applied to the source timings.

The result concerns the tested ordinary participants using a visual grid editor. They may make several submissions; the source includes counts above two. Do not substitute the benchmark's statement that every retained task was solved by at least two people for an individual human success rate. The [technical report](https://arcprize.org/blog/arc-agi-2-technical-report) explains that task-curation criterion. Our human outcome rate is calculated directly for the matched cases.

## Compute

Cache reads are not separated in the retained records. The central recipe treats each reported prompt as newly processed. A provider cache hit would reduce that parameter-multiplication workload; no cache fraction is imputed.

Each included case has two distinct retained response slots. Sum their prompt_tokens and completion_tokens; the latter already contains reasoning_tokens. Across every downloaded non-null response, total_tokens equals prompt plus completion. Never add reasoning again. The metadata's choices are stored conversation messages, not additional model calls. The source summary's attempts field counts slots, including nulls, and is not a count of executed requests.

The observation-weighted mean is **124,982.54770318021 input-plus-output tokens**: 14,491.674911660777 input plus 110,490.87279151943 completion. The completion count already contains 107,943.59952885748 reasoning tokens. At the shared GPT-5.2 coefficient of 200B FLOPs/token, total compute is **2.499650954063604e16 FLOPs**. The coefficient remains an assumed family size, not a provider disclosure. Context-dependent attention and internal requests without retained usage are not directly measured by this token recipe.

The archive has 107 task files, 146 array entries and 260 retained responses. We omit cases lacking one response rather than assigning an unobserved second attempt a fabricated counter. The selected work unit therefore covers two retained responses only. Its completeness filter can alter the task mix. No source event logs establish additional failed-call work; the central count follows retained executed responses.

## Performance

On the common observation-weighted mixture, AI has at least one correct answer in **561/849 = 66.0777%** of weighted cases and humans succeed in **562/849 = 66.1955%** of timed sessions. Classify match. Humans have interactive feedback and potentially more submissions; AI uses two text-grid requests. Those differences are retained in comparison_issues. This is approximate outcome parity under the two recorded protocols, not identical experimental conditions.
