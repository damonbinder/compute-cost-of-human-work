# VCT: one text-only multiple-response question

## sci-virology-vct-o3

Use [the original April 2025 VCT paper](https://arxiv.org/html/2504.16137v1), Sections 3.3–5.2, Appendix A2 and public examples in A8. The retained PDF/text are `agent-work/sources/vct-v1.*`. Define one representative question from the 101-question text-only subset, answered once in the multiple-response format: read a technical scenario and select every true statement among four to ten choices. Exclude physical laboratory work and subsequent implementation of advice. No question is answered or operational troubleshooting reproduced in this collection note.

The full shared set is not publicly released, and the paper's public examples are deliberately outside the evaluated set. They can anchor length and task structure, but cannot establish measured performance on a chosen example. Accordingly this row represents an assumed average question workload, with performance from the source-defined text-only subset.

## Outcome evidence and comparison

Appendix A2 reports **48.5% exact-set accuracy for o3 and 22.6% for expert virologists** on the text-only subset. The evaluation averages independent model runs; it does not select a majority-vote answer. Count one answer-generation workload rather than multiplying by three. All-or-nothing multiple-response scoring has chance probability 1/(2^n−1), not the 25% chance rate of four-option multiple choice. Both results are above that relevant guessing baseline.

Humans were matched to areas of expertise, allowed external references but not LLMs or colleagues, and had not authored/reviewed their questions. Only 303 of the full 322-question set received human answers; the text-only coverage count is not separately reported. Thus flag different_assessment for unequal expert coverage/topic assignment, and different_inputs_or_tools for human reference access versus the zero-shot model setup. The substantial text-subset score difference supports above without pretending identical assessment coverage.

## Human active time

The stated **15–30 minutes is an allowed answering budget**, not a recorded completion-time average. Appendix A4's comment that many reviewers spent under fifteen minutes concerns earlier review, not the final expert baselining population. Neither is silently relabeled task_timings.

Estimate **18 active minutes (1,080 seconds)** for a domain-matched expert trying to answer this type of question at the source's baseline conditions. Public A8 examples have a detailed scenario and several technically distinct explanations to assess; one has six statements and roughly a hundred-word stem. This is more than fact recall, but it is not a fresh research project or execution of an experiment. Allocate two minutes to parse the scenario and measurements, six to examine the individual alternatives, eight for focused reference/manual checks of unfamiliar assay or measurement details, and two to reconcile the selected set. The reference time matters because the benchmark deliberately includes tacit or hard-to-search methodological knowledge. A ten-to-thirty-minute range is appropriate. This does not assume that extra time guarantees a correct set; the human quality remains the observed expert baseline.

## Model workload and coefficient

The source reports the April 2025 public o3 but does not publish token logs, reasoning effort or a per-question token limit for that model. The 4,096-token footnote in Table 1 applies to asterisk-marked other models; it is not an o3 usage measurement.

Estimate **500 input tokens + 4,000 reasoning tokens + 50 final-answer tokens = 4,550 input/output tokens**. The prompt allowance fits the public examples' short technical scenario plus multiple statements and instruction framing. The reasoning allowance represents evaluating about seven statements with a few hundred tokens each, then checking dependencies and revisiting uncertain alternatives. It is a first-principles allowance, not an observed hidden reasoning trace. A 1,500–10,000 total-token range captures considerable uncertainty. Count reasoning once within output, and do not add a second hidden-reasoning budget. No inference helper or tool workload is established by the reported custom zero-shot evaluation.

Use **50B active parameters, estimated**, as an explicit transfer of the independently reviewed o3-family central coefficient in the shared model registry to public April o3. The public architecture is undisclosed. The registry's early Codeforces checkpoint is a different model identity and is not used as the point's model_id; the shared numerical assumption is carried across the same family rather than inventing an independent unsupported parameter count. This proposed model transfer needs review. At 2×50B, **compute = 4,550×100B = 455,000,000,000,000 FLOPs**. Parameter uncertainty and token uncertainty both matter.

The exact public release date is **2025-04-16**, established by [OpenAI's release announcement](https://openai.com/index/introducing-o3-and-o4-mini/), which explicitly makes o3 available that day. The source calls its evaluated model o3 (Apr '25); no later o3-pro revision is substituted.
