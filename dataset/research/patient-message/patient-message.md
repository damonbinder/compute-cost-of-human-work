# Answering a patient question

One reply uses an estimated **1.833 × 10¹⁴ FLOPs**, including a small moderation allowance. The physician baseline is **120 seconds** for the original short human reply. AI replies were rated better; the human estimate does not target reproducing the longer AI output.

## Work and performance

[Ayers et al. (2023)](https://jamanetwork.com/journals/jamainternalmedicine/fullarticle/2804309) collected 195 public AskDocs question/first-physician-reply pairs from October 2022. Each original question was submitted in a new ChatGPT session on December 22–23, 2022. Mean question length was 180 words, physician reply length 52 words, and AI reply length 211 words. The six published examples show short risk assessments, reassurance and recommendations; their questions are edited summaries rather than the complete original prompts.

Three clinicians assessed each pair, giving 585 judgments. They preferred the AI reply in 78.6% of judgments; mean quality was 4.13/5 for AI and 3.26/5 for physicians. This supports `above` for the assessed reply quality. It is not an observed clinical-outcome comparison. A longer reply may influence ratings, but both participants answered the same question; length alone is not a different-task flag.

## Model and workload

The [original ChatGPT launch](https://openai.com/index/chatgpt/) on November 30, 2022 identifies a GPT-3.5-family model and use of the Moderation API. The [release history](https://help.openai.com/en/articles/6825453-chatgpt-release-notes) includes a December 15 update. The study does not identify its precise backend revision, and the model row preserves that limit. What the row does fix is the size class: these sessions predate the turbo-class backend, which became the ChatGPT default on 13 February 2023, so they ran the davinci lineage. `research/model-priors/openai.md#chatgpt-backend-2022-23` carries the dated timeline.

Neither the launch nor the study discloses parameters. Use **175B active parameters** as an explicitly assumed dense GPT-3-scale proxy, anchored to [Brown et al. Table 2.1](https://arxiv.org/abs/2005.14165). This is not evidence that early ChatGPT actually had 175B parameters. Later GPT-3.5-Turbo size estimates do not establish the size of the December 2022 model, and the record's low bound is 60B rather than the 12B it carried until 2026-09-16, which was read across from that turbo evidence. Sixty billion is what the cost reduction supports: if OpenAI's 90% cut "since December" were entirely size, the December model scales to 120B active against the 12B turbo central and to 70B against the 7B dense reading. The high bound stays at 200B.

`token_estimate.py` extracts the six original table examples from the retained PDF. With cl100k_base, the selected replies total 1,626 tokens / 1,400 words; the question summaries total 255 tokens / 204 words. Applying those ratios to the full-study reported means gives 225 input and 245.0614 output tokens. Add an assumed 50 positions for the unreported system message and wrapper: **520.0614 primary tokens**. This transfers selected-example ratios, not their lengths, to the reported full-sample quantities. The examples were selected for publication and the original tokenizer is unknown. Using p50k_base throughout gives 527.704 primary positions instead.

The launch's moderation helper is included rather than treated as free compute. The [original moderation paper](https://arxiv.org/abs/2208.03274v1), §4.1, describes a lightweight GPT decoder and eight classification heads, without a size. Assume a **1.3B-parameter** small GPT proxy, one scan each of the question and reply, and four special positions in total. Using p50k_base ratios yields **481.704 helper positions**. Neither the size nor the exact number of moderation scans was reported for these sessions.

| Component | Text positions | FLOPs per position | FLOPs |
|---|---:|---:|---:|
| Primary reply model | 520.0614 | 350 billion | 182.0215 trillion |
| Moderation proxy | 481.7040 | 2.6 billion | 1.2524 trillion |
| Total | 1,001.7654 | — | 183.2739 trillion |

The `tokens` field totals both models; applying the primary coefficient to that total would be wrong. The estimate uses twice active parameters per text position, excluding small classification-head costs; context-dependent attention is added in `compute_flops` (`research/attention-correction.md`). There is no evidence of tool use, multi-session retries or additional conversation in this work unit. It is an analytic estimate from reported average lengths, so AI attempts are not applicable rather than 195 invented timing observations.

## Sensitivity

The undisclosed primary model size dominates. At 7B, 44B, 175B and 350B, total compute is respectively 8.53, 47.02, 183.27 and 365.30 trillion FLOPs. These are size scenarios, not measured alternative deployments or confidence limits. At the 175B primary assumption, changing the system/wrapper allowance from 0 to 200 positions gives 165.77–235.77 trillion. Using p50k for the primary gives 185.95 trillion.

Moderation sizes of 0.1B, 1.3B and 6.7B give totals of 182.12, 183.27 and 188.48 trillion. An extreme primary-sized 175B helper gives 350.62 trillion. Five or twenty complete moderation scans at the small proxy size give 188.28 or 207.07 trillion. This makes the low central allowance inspectable without claiming the actual provider execution path is known.

## Human time

`human-time.md` contains the source inspection and calculation. The estimate allocates 40 seconds to reading/interpreting the 180-word question and 80 seconds to composing and checking the 52-word physician reply. It is calibrated against 3,680 pre-AI clinical message replies in [Tai-Seale et al. (2024), Table 1](https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2817615). Reading and reply medians are not added and mislabeled a measured median. The donor EHR event intervals are not continuous-attention measurements, and their clinical workflow differs from the public forum. The estimate adjusts that calibration to the original forum reply; the compared human and AI task is the same question. The 60–240-second scenarios allow faster familiar questions or more deliberation.

The 3,680 human attempts are contributing donor messages, not timed AskDocs replies, unique physicians or the 585 quality judgments. `transferred_timings`, `estimated` and `point_estimate` preserve that distinction. The original human quality remains the target of the human-time estimate, so estimated timing does not imply performance parity.

## Retained evidence and reproduction

The sources directory contains the original study PDF, GPT-3 and moderation papers, both tokenizer rank files, extracted launch/release facts with URLs, and the human calibration XMLs. `source-manifest.json` records hashes. The study PDF has a recoverable cross-reference warning; calculations read it without modifying it.

Run `token_estimate.py --sources /path/to/sources --output /path/to/new-result.json` with Python, pypdf, pdfplumber and tiktoken. It uses official tokenizer definitions with retained rank files and performs no network or model calls. Compare against `token-estimates.json`. The human calculator accepts its own retained human-source directory and a new output path, as documented in `human-time.md`.
