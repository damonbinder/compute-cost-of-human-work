# MLE-bench: Operand text-classification run

## agen-mlebench-operand-insults

One complete, first chronological released run of Operand on Detecting Insults in Social Commentary: 3,947 labeled comments, 2,647 test comments, a validated classifier notebook and probability submission. The retained grader reports AUC **0.90942**. The estimate is **2.8711070611478e16 FLOPs / 5,400 human seconds**. This is a later GPT-5-based system, not the original paper's o1-preview experiment.

The original MLE-bench 2024 trajectories were not released (author response in issue 28, retained `original-log-issue.json`). The later entrant's complete visible history and notebook make a source-based estimate possible. The missing LLM components are modeled below rather than reported as native usage.

### Source run and work

Source revision `8bcb272c9611cc16c809a191135f696014895b0e`, directory `MLE_Submission/detecting-insults-in-social-commentary/detecting-insults-in-social-commentary-spray-20250909-024523`. Selection is chronological, not best of three: the other seeds score .9128 and .91083, but neither their work nor their results enter this point.

The ten recorded agent turns create a plan, request an expert review, build and run the notebook, and correct the submission schema twice. The actual classifier combines word 1–2-gram and character 3–5-gram TF-IDF with L2 logistic regression (SAGA, C=4). Five stratified folds give OOF AUC .90588; a full-data fit produces final predictions. The initial exception occurs only after fitting and prediction, when the code wrongly looks for `Insult` as a test identifier. The corrections reuse predictions; they do not rerun the fits. Actual notebook outputs report CV 28.08 seconds and full fit 5.48 seconds.

MLE-bench's original preparer retains the original test labels privately and removes them from the agent's inputs. It excludes the later verification-stage public test because of leakage concerns. The source notebook's sample counts agree with this work unit. No training data or model weights were downloaded and no notebook code was executed in this reconstruction.

### Recovered text and reconstructed context

With `o200k_base`, the ten recorded primary outputs contain **4,778 tokens**, including **1,374 tokens** of visible pre-JSON reasoning-like text. Replaying the preceding exported history at each turn contributes **40,351 input tokens**. These are counts of retained text, not API usage counters.

The central input recipe also includes the original 2,490-token task description each turn, the notebook cells only after their recorded insertion, and available cell outputs when execution has completed. By turn 6 the agent explicitly observes the completed CV and submission error, so the final cell-1 output is included from then onward. Each insertion payload is joined with newlines and checked against its original notebook cell. Completed output includes the actual traceback with ANSI styling removed; the rendered error is 589 tokens. This reconstructed notebook-state component totals **16,746 tokens**. The precise IDE prompt representation is unreported; error-summary-only and raw-ANSI alternatives are retained. For turns 9–10, 300 tokens each proxy the opened sample-file preview, whose source content was not exported. The preview matters only to fix three column names.

The architecture describes persistent history, notebook/IDE context and a structured single-tool interface, but does not publish its prompt builder. Central fixed system/tool/IDE overhead is **1,000 tokens per turn**: a compact instruction and schema allowance for the observed edit, execute, wait, open-file and review actions plus run state. This is an assumption, not recovered prompt text. Alternatives use 500 and 4,000. Repeating the notebook separately is also an assumption; a no-repeated-notebook case shows its effect. No compaction is charged for this short history: none appears, and reconstructed calls remain far below context limits.

The primary is GPT-5 with low effort according to the benchmark entry. Because exported prose may not include all internal reasoning, add **512 unexported tokens per primary turn**. This is a modest low-effort allowance for ten mostly short tool decisions, not an asserted provider budget. Zero and 8,192 per turn bracket alternative accounting regimes; the latter is deliberately a much more deliberative agent. Visible reasoning is counted once in the 4,778 retained tokens and is not itself added again as “hidden” work.

### Expert review

The recorded consultation contains an **892-token main review** followed by a **598-token Independent Kaggle Coach Feedback section**. The original architecture §3.2 identifies four reviewers: GPT-5, Claude Opus 4.1, Grok 4 and Gemini 2.5 Pro. The original leaderboard footnote 2 explicitly identifies **Gemini 2.5 Pro as the distiller**. Separate member responses, prompt layouts and native token counters are not exported.

The central recipe distinguishes the observed text from assumed calls:

| Component | Input | Visible output | Assumed additional reasoning |
|---|---|---:|---:|
| Each of four named reviewers | Actual task, plan and request: 3,131 tokens; assumed 500-token wrapper | 892 tokens assumed per reviewer, using the observed main-review length as a proxy | 892 tokens each |
| Gemini synthesis | Common context/wrapper plus four assumed 892-token reviews | Actual 892-token main section | 446 tokens |
| Separate coach | Common context/wrapper plus main synthesis: 4,523 tokens | Actual 598-token suffix | 598 tokens |

A separate coach invocation is an interpretation of the explicitly headed suffix, not an observed helper-call trace. Its model is unidentified, so the primary GPT-5 coefficient is the stated assumption. The no-extra-coach scenario instead treats that text as part of the ensemble's combined synthesis. The central recipe counts the main section once as synthesis output and the suffix once as coach output. Retaining both again when the primary later reads its history represents new input processing, not duplicate output generation.

The individual reviewer lengths are output proxies, not measurements. An alternative uses the full 1,490-token combined response for each reviewer. No reviewer tool use or classifier training is described in this consultation. `o200k_base` is a common counting proxy across the four model families, not native Anthropic, Grok or Gemini tokenization.

Estimated model totals:

| Model | Input tokens | Output including assumed internal reasoning | Active parameters |
|---|---:|---:|---:|
| GPT-5, including its review and assumed coach | 100,751 | 12,878 | 100B |
| Claude Opus 4.1 | 3,631 | 1,784 | 180B |
| Grok 4 | 3,631 | 1,784 | 115B |
| Gemini 2.5 Pro, including review and synthesis | 10,830 | 3,122 | 100B |

The total is **138,411 text tokens** and **2.871105e16 LLM FLOPs** under the shared 2P method. No cache counts are exported, so the central recipe assumes full-prefix processing. The stable-prefix-reuse scenario charges only new primary history and one copy of the fixed task/wrapper, retaining current notebook state and helper work. This is a specified layout/cache alternative, not recovered cache usage. Context-dependent attention is omitted by 2P and added back in `compute_flops` (`research/attention-correction.md`).

### Classifier arithmetic

All six fits and associated transforms/predictions are included. Five four-fifths folds plus the final full fit give exactly 19,735 training examples per epoch-equivalent. Neither sparse feature counts nor actual convergence iterations were printed. Central assumptions are 1,000 nonzeros/comment, 100 passes, and approximately ten operations/nonzero/pass, informed by the sparse dot product, gradient and lazy-average updates in original scikit-learn SAGA source. Add a 100,000-feature dense epoch allowance and transform/prediction work. Result: **2.0611478e10 FLOPs**.

This is an operation estimate, not runtime times CPU peak. The configured 5,000-pass cap is only a sensitivity case. Using 5,000 nonzeros and all 5,000 passes produces approximately **4.965e12 FLOPs**, still only 0.0173% of the central total. Thus the unknown fit iterations cannot materially drive this point. The original SAGA source is explanatory implementation evidence, not proof of the run's precise installed scikit-learn revision.

### Human estimate and comparison

Estimate **90 active minutes** for an experienced ML engineer to independently produce a comparably validated small-data classifier and submission, without generative-AI assistance: inspect schema/examples and target (15m), implement text features and leakage-free CV (35m), assess validation and full fit (15m), and check the submission/notebook (25m). The original low.txt explicitly includes this competition. The two-hour “sensible low-complexity solution” definition in the original benchmark is a contextual check, not a timing measurement or proof of medal-quality speed.

The bounds re-run the four stages. With a reusable linear-text template the implementation drops from 35 to 15 minutes and the submission check from 25 to 15, giving 60 minutes. The high takes the benchmark's own two-hour low-complexity-solution definition and adds a debugging round over the feature and cross-validation code, giving 150 minutes. These are judgment scenarios, not confidence intervals. The work does not require deep-learning architecture search or a competition season. Machine waiting contributes little active work here. Human performance matches by construction: the baseline targets comparable validation and test quality to the inspected artifact, not an independently measured human AUC. No empirical human timing donors exist for this estimate.

The primary model remains frozen; subordinate classifier training is included task work. `compute_scope=inference` describes that primary agent, not an assertion that every downstream algorithm has fixed parameters.

### Sensitivities

| Alternative | Total FLOPs |
|---|---:|
| Central | 2.8711e16 |
| No unexported reasoning, including coach | 2.6595e16 |
| Primary 8,192 hidden tokens/turn; helper hidden allowances ×4 | 4.7347e16 |
| Fixed primary wrapper 500 / 4,000 tokens | 2.7711e16 / 3.4711e16 |
| No separately repeated notebook | 2.5362e16 |
| Stable primary-prefix reuse | 1.5675e16 |
| Coach already within the ensemble | 2.7747e16 |
| Each reviewer uses the full combined 1,490-token output proxy | 3.0374e16 |
| Error summary only / full raw ANSI traceback | 2.8129e16 / 3.0169e16 |
| Separate coach does not receive the main synthesis | 2.8533e16 |

The original small/large-classifier scenarios are also retained in the calculation. Each scenario changes the named choice while retaining other central assumptions. Model-size priors add further uncertainty; these alternatives are not confidence intervals. `assumptions.json` distinguishes source-identified roles from assumed quantities and prompt layouts.

## Model assumptions

GPT-5 uses the existing dataset's 100B active prior from Epoch's original GPT-5 compute analysis, not a disclosed architecture: https://epochai.substack.com/p/notes-on-gpt-5-training-compute . The generic ID avoids confusing low effort with different weights. Public release is 2025-08-07: https://openai.com/index/introducing-gpt-5/ .

Helper coefficients preserve reviewed shared assumptions: Opus 4.1 180B follows the model-specific 24 tokens/s and 4–4.5 TB/s effective-bandwidth FP8 scenario (167–188B), rounded to 180B, in the original throughput/bandwidth analysis at https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus ; Gemini 2.5 Pro 100B is the established frontier-peer transfer; Grok 4 115B is the established Grok 2 active-size family transfer (Grok 4 itself undisclosed). The latter's original released donor is https://huggingface.co/xai-org/grok-2/tree/daf4395a80ad177386cfe39641b64fc12b1d70ed . Its retained configuration has 64 layers, width 8,192, eight experts with two selected and an always-active residual MLP. The shared architecture reconstruction gives about 114.9B active parameters, rounded to 115B. This is a weak family transfer to Grok 4, not a disclosed Grok 4 architecture. The same family prior is used for the later Grok 4.20 record; neither transfer asserts identical weights. These priors are not inferred from this task's performance. Factor-two coefficient sensitivity scales the LLM term approximately twofold. Exact helper API revision strings are not supplied by the entrant. The helper-only `grok-4` model record uses the original [July 9, 2025 public/API release](https://x.ai/news/grok-4), separately from the later 4.20 revision.

## Sources and replay

Original benchmark pin `507f92e1138bb6e40dac5c6ee7a6758e6424bf97`; original entrant pin above. The source trees, architecture report, task preparer/grader, three source seeds and notebook outputs are retained. The original entry is https://github.com/openai/mle-bench/tree/main/runs/operand_group1 ; entrant artifacts are https://github.com/ramgorthi04/OperandLinear-MLE-Bench . The author's architecture paper is https://arxiv.org/abs/2510.11694 .

```sh
python3 research/mlebench/recompute.py --sources agent-work/sources/mlebench --assumptions research/mlebench/assumptions.json --output /absolute/new/calculations.json
```

Requires tiktoken. The calculator reads only source JSON/text, never executes notebooks, and refuses existing output or output under sources. SHA256s bind the numeric reconstruction to the selected original files. The selected run is the first of the three retained directory timestamps; no best-of-three cost or performance selection is used. The full work is a `total` for one run, including its tool retries and classifier fits.
