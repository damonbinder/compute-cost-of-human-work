# Sabiá learns Portuguese academic and cultural tasks

These two proposed rows compare one continued-training run with one adult's learning from the base model's demonstrated capability to the adapted model's capability. They do not use the old dataset estimates.

## The target is a mixed benchmark, not a proficiency percentage

[Pires et al. (2023)](https://arxiv.org/abs/2304.07880v4) evaluate fourteen datasets. Their normalized preferred metric (NPM) subtracts each dataset's chance floor, divides by its available range, then takes an equally weighted mean. Its ingredients include correlation, F1 and accuracy. An NPM of 48.5 does not mean that a person comprehends 48.5% of Portuguese or answers 48.5% of questions correctly.

| Component metric, percentages unless noted | LLaMA7B | Sabiá7B | LLaMA65B | Sabiá65B |
|---|---:|---:|---:|---:|
| Poeta NPM |33.0|48.5|63.7|69.4|
| ENEM Challenge accuracy |29.04|60.59|75.00|90.39|
| ENEM2022 accuracy |23.73|60.17|62.71|72.03|
| BLUEX exam accuracy |32.02|47.75|53.93|57.87|
| TweetSentBR macro-F1 |44.19|67.17|68.05|72.91|
| ASSIN2 semantic similarity Pearson ×100 |7.39|13.63|62.85|63.29|
| FaQuAD extraction F1 |77.38|77.43|87.25|88.47|

The larger model already extracts factual answers and judges sentence similarity relatively well. Its remaining gains are mostly Brazilian exam and cultural knowledge. The smaller model improves across a broader set but still has a weak semantic-similarity score. Matching only an aggregate permits different subskill profiles; the estimated human target should approximately match this task mix, not merely obtain the same number by exploiting an easier component.

I inspected ENEM2022 records 23,47,58,72 and101 from the [author's exam repository](https://github.com/piresramon/gpt-4-enem/tree/cbba7fdd735845bb45ac80d5090baae1b949d782). They involve copyright inference, migration, Estado Novo press control, Mercosul and coagulation. These are reading plus subject-knowledge tasks. That repository is evidence of task content, not proof that its current question set exactly reproduces the paper's 118 text-only questions. Some retained questions have OCR fragments. The paper's training text predates ENEM2022, which makes that component a useful check against direct question memorization; this does not establish that all fourteen datasets are uncontaminated.

## Human time is a proposed judgment, with existing knowledge credited

The reference `skill-acquisition-human-time.md` Table L maps chance-adjusted **multiple-choice** accuracy to CEFR and class hours. Applying it to this mixed metric would silently equate Pearson correlation and F1 with reading comprehension. I have not done that. The exception uses the already allowed `llm_estimate_judgment` field, and Damon's ruling of 2026-09-15 takes it: a mixed-metric benchmark with no defensible score-to-learning-time calibration carries a researched judgment of study hours rather than the Table L mapping. No schema change is required.

The learner is an ordinary adult with secondary-school subject knowledge and enough existing Portuguese to show the respective baseline profile on fresh comparable tasks. Prior general education and prior Portuguese study are credited, just as LLaMA pretraining is excluded. The target is the adapted profile, not native-level fluency, professional translation or a full Brazilian secondary education. Ordinary learners are not selected for elite ability. Neither this starting population nor the endpoint is a measured human cohort.

Two original curricula constrain the size and content of the route:

* The [IFB 2018 ENEM preparation curriculum](https://www.ifb.edu.br/attachments/article/2877/PPC%20FIC%20Preparat%C3%B3rio%20para%20ENEM%20p%C3%BAblico%20externo.pdf) assumes final-year or completed secondary education. Its 160 clock hours include 24.17 Portuguese,15.83 history,15.83 geography,8.33 sociology,8.33 philosophy and8.33 arts:80.82 clock hours of especially relevant instruction. The remaining hours cover mathematics, sciences and foreign languages. This is a planned course, not measured time to a Poeta gain.
* [PUC-Rio's Brazilian Seminars](https://www.puc-rio.br/ensinopesq/ccci/incoming/brazilian_seminars.html) cover history, media, migration, arts, politics and urbanization. Its main description gives 52 fifty-minute class-hours, about 43 clock hours, plus optional Portuguese modules. Another section gives 54 contact hours; I use the broad forty-hour curriculum scale, not its inconsistent total. It is taught in English and is only a scope comparison for adults with prior education, not a Portuguese learning-time donor.

| Active learning component |7B target, hours|65B target, hours|
|---|---:|---:|
| Structured Portuguese reading and Brazilian humanities review |80|20|
| Fresh exam practice, feedback and targeted subject revision |60|60|
| Varied Brazilian cultural reading and discussion |40|0|
| Informal language, sentiment and inference practice |20|20|
| **Proposed total** |**200**|**100**|

For 7B, the structured block approximates the relevant portion of IFB's review curriculum. The practice block adds active work rather than assuming attendance alone yields the gain. Cultural reading and colloquial interpretation address the native-data gains outside conventional exam preparation. Practice uses unseen questions and feedback, not memorization of benchmark answers. For 65B, the learner already handles most of this material; the route replaces a broad course with diagnostic practice, reading gaps and idiomatic interpretation. The harder high-end exam items prevent simply scaling hours by the smaller NPM difference.

The starting-point credit matters: the smaller base already scores about77 F1 on factual extraction and77% on news classification despite its weak exam scores. This is not a zero-start Portuguese learner. A representative use of the7B practice block is400 varied questions with roughly four minutes answering and five minutes of feedback each; that is60 hours. For65B, roughly600 questions at six minutes of combined attempt and targeted review also fill60 hours. These are proposed study workloads, not measured rates or a fitted learning curve. They make the proposed effort concrete; they do not prove the endpoint. The profile-based rationale favors hundreds rather than thousands of hours, but the evidence cannot distinguish200 from, for example,350 hours.

The allocation and the claim that it reaches these endpoints are judgments. Neither institution measured this gain. Therefore the evidence field is **llm_estimate_judgment**, human attempts and subset are **not_applicable**, and the statistic is **point_estimate**. Performance is **match** by the explicit endpoint construction, not an observed human result. `different_inputs_or_tools` records the human's instruction and feedback versus the model's raw-text continuation. No assessment flag is added merely because the human baseline is estimated.

Human-time scenarios are 50–600 hours for7B and 25–300 for65B. The low ends describe learners whose errors mostly reflect unfamiliar vocabulary, conventions and test format. The high ends require repairing substantial Brazilian subject-knowledge gaps with repeated practice. These are alternative judgments, not confidence intervals. They remain in this note because the current CSV has no human range fields. More precise central values would imply unsupported calibration. A timed cohort assessed on Poeta components before and after instruction would be the relevant improvement in evidence.

## Compute includes training attention and associated evaluation

Training uses 10,000 steps ×512 sequences ×2,048 positions =10,485,760,000 training positions. This explicit product takes precedence over rounded10.4B and the inconsistent1.52 epochs claim. Original Section 3.2 specifies rematerialization, unfactored AdaFactor with momentum and auxiliary z-loss. It does not publish checkpoint boundaries or monitoring logs.

The 7B architecture comes from the original [Sabiá configuration](https://huggingface.co/maritaca-ai/sabia-7b/blob/aa4a5bb34e707ea19effbc2a94876f8f811cf7ed/config.json). The 65B shape is the unchanged LLaMA65B architecture identified in the paper ([Touvron et al. (2023)](https://arxiv.org/abs/2302.13971), Table 2), cross-checked against the [public conversion configuration](https://huggingface.co/huggyllama/llama-65b/blob/main/config.json). For vocabulary V, width H, feed-forward width M and layers L, parameters are `2VH + L(4H² + 3HM + 2H) + H`. This includes both embedding tables and norm parameters, consistently with the reference registry's2P convention.

|Architecture|Parameters|Layers|Width|Feed-forward|
|---|---:|---:|---:|---:|
|7B|6,738,415,616|32|4,096|11,008|
|65B|65,285,660,672|80|8,192|22,016|

The central assumes one extra forward equivalent for full rematerialization: `(8P +16LH C)T`, with mean causal context `C=(2048+1)/2`. This is ordinary training's6P+12LHC plus a recomputed forward pass. Partial rematerialization would be cheaper. The current convention counts causal attended positions; a dense full-square masked implementation would perform more attention arithmetic, retained as a scenario rather than silently altering the project method.

Associated evaluation uses the paper's test counts, mean character lengths and few-shot counts. Per example, estimated processed positions are `min(2032,(shots+1)*mean_characters/3+128)+16`. Three characters per native token,128 framing/label positions and16 answer positions are assumptions; prompts are bounded by the2,048-token context. MKQA uses the6,758 filtered questions. We assume KV reuse within an answer and no reuse across examples. These are workload estimates from this study's own quantities, not a borrowed benchmark average.

The central includes three whole-suite passes: one final evaluation and two intermediate passes. The paper reports observing few-shot improvements beyond one epoch but gives no schedule. Three is an explicit allowance, not a recovered log. The two intermediate suite equivalents proxy unresolved monitoring work, which may actually have been a smaller task subset or language-model validation. Whole-suite checks provide a reproducible allowance from published quantities; they are not asserted as the historical schedule. Eleven passes are a sensitivity case. Each pass totals about 66.18 million processed positions. At the central three passes, evaluation adds less than 0.5% of total FLOPs. The script also includes 20 scalar operations per parameter per training step for the unfactored optimizer, momentum, clipping and decay; that allowance is below 0.001%. Small activation/loss/kernel overhead is not resolved by this analytical method.

|Compute result|7B FLOPs|65B FLOPs|
|---|---:|---:|
|Central|5.905285983539635e20|5.615455400648786e21|
|No rematerialization, one final suite|4.417555415276348e20|4.200661805075142e21|
|Half-forward rematerialization, three suites|5.170550652676941e20|4.916805010617549e21|
|Full rematerialization, eleven suites|5.978325609691230e20|5.685426662693465e21|

The current range columns cover only parameter priors and cache-implied context uncertainty. Neither applies: the architecture is reported, and context is reconstructed from training length and this study's evaluation quantities. The columns are therefore blank even though the recipe has rematerialization and monitoring uncertainty. `compute_evidence=derived_assumed_inputs` captures those assumptions. One complete training run is one AI attempt; evaluation is associated work, not additional training attempts. Training-token cells exclude evaluation positions.

## Dates and costs follow the current conventions

7B takes 2023-11-08, the first original weight/config commit in the retained Hugging Face history. Later February 2024 replacement files are not used for its architecture. The model card identifies the released model with the paper's48.5 NPM, though no hash proves the paper evaluation used these precise tensors. The 65B model has no located public weight release; it takes 2023-04-16, the original paper announcement under the current private-model policy. The original v1 PDF already contains both reported endpoints. Historical repository visibility is not independently established.

The paper's approximate $9,000/$80,000 figures are on-demand TPU price estimates, not reported bills for the fully accounted work. Costs remain blank with `not_available`; no FLOP-to-dollar conversion or invented human payment is used.

## Replay

Run `python3 recompute.py --output /tmp/sabia-new-result.json` from this directory. It uses only the two bundled configurations in `inputs/` and explicit Table 1 inputs; the retained-source archive under `agent-work/sources/sabia-learning/` is not needed for replay. It rejects an existing output path.
