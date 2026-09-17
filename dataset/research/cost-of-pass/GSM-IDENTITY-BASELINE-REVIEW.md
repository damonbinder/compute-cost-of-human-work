# Independent GSM-Identity baseline check

Recommendation: replace the current 180-second GSM8K attempt estimate with **60 seconds**, using `transferred_timings`, `estimated` and `point_estimate`. Specify a high-school-educated adult permitted a calculator; add `different_inputs_or_tools`. This is a stronger direct task-family anchor, but not a measured GSM8K per-question mean.

Sources retained: `agent-work/sources/cost-of-pass/gsm-identity.pdf`, extracted `.txt`, and `gsm-identity-tree.json`. Original paper: https://link.springer.com/article/10.1007/s10994-026-07029-7 ; author-hosted PDF: https://iris.cnr.it/bitstream/20.500.14243/575001/1/s10994-026-07029-7.pdf . Figure 5b on PDF page 18 was rendered and inspected, because its tool instructions were missing from text extraction.

## What the study establishes

Section 6 (PDF p17) describes native-English speakers with at least a high-school diploma. It reports five-question batches and a five-minute median batch duration, without separate timing statistics for each study or question condition. Section 6.3 (p19) uses 50 randomly sampled original GSM8K questions and their three transformed versions. Table 8 (p20) gives **84.0% human accuracy on the original questions**; the lower transformed-question scores are not the original baseline.

Figure 5b explicitly permits a calculator for basic operations and prohibits ChatGPT or similar AI. Participants give numeric answers after an example and a warning about numerical transformations. They are not selected as teachers or mathematical experts. The publication does not identify total unique participants, per-item response counts, individual response times, or whether the batch median includes instruction-reading overhead. The repository tree exposes model evaluation and generated datasets, but no identifiable human timing release.

## Interpretation and proposed fields

300 seconds / 5 questions = 60 seconds is a median-batch allocation, not the median or mean of individual question times. The timing statement spans the studies, including equivalence judgments and transformed math, so the transfer should remain an estimate. It nevertheless puts an empirical anchor close to the actual answer-production task, with a known performance result. The current 180 seconds rests on correct-answer throughput from a separate study plus a discretionary attempt-time adjustment. Replace that weaker adjustment instead of averaging the two incompatible quantities.

Recommended human fields: `human_skill=typical`, `human_time=60`, `human_time_evidence=transferred_timings`, `human_time_method=estimated`, `human_time_statistic=point_estimate`, `human_time_subset=all`, `human_attempts` blank (contributing timing count unreported). Do not enter 50 as a timing-attempt count: it is the accuracy sample's question count, not a known contributing sample behind a per-question timing statistic.

The task description should explicitly permit human calculator use; the CoP LLM has no calculator tool. The notes should say that human time allocates the reported median batch duration and that human accuracy comes from a different 50-item sample. Sources belong in source_record and human_time_source, not performance_evidence.

## Performance implications

The 84% observation should replace the unsupported generic high-accuracy adult assumption. It supports reconsidering the 91.9–94.4% CoP models as above; GPT4o-mini at 88.6% is plausibly broadly comparable. Llama3.1-8B at 75.8% is lower, but the eight-point difference should be judged with the small 50-item human sample and different prompts in mind. A simple binomial interval around 42/50 is roughly 71.5–91.7%, illustrating uncertainty rather than imposing a formal equivalence rule. The paper does not explicitly state one response per original item, so do not invent 42 successful human attempts in the CSV.

The study's own Llama3.1-8B generic score is also 84%, versus 75.8% in CoP. That demonstrates potentially consequential sample/prompt differences; it does not justify mechanically subtracting 8.2 points from the human baseline. Its Llama3.3-70B generic score is 98%, consistent with stronger models exceeding the human sample. Use these as context for the broad transfer, not task-specific human measurements.

No candidate or production fields changed during this check.
