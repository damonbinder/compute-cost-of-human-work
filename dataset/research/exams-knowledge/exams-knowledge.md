# Exam and knowledge questions

Each row is the cost of answering one question. The MMLU rows average an identified benchmark; the other rows identify their exam or subtask. These are inference comparisons, not estimates of the cost of acquiring an education. None of the human durations below is a measured completion-time mean.

**The three allotment-pace centrals stand, and the rows assert no bounds**
(2026-09-17). `lang-exam-gre-verbal-gpt4` at 90 s, `lang-exam-mbe-gpt4` at 108 s and
`lang-exam-usmle-gpt4` at 90 s each divide an exam's time allowance by its question
count, so each central sits exactly at the elapsed ceiling. The standing rule allows
that where there is an argument that people use the whole allowance, and on a
proctored multiple-choice licensing or admissions exam there is one, of two parts.

The first is structural. An examinee in a test centre with the clock running and an
item on the screen has nothing else to do, so the gap between elapsed and active time
that the rule exists to catch is close to zero; time not spent on one item is spent on
another in the same block, and the whole block divides across its items. The National
Board of Medical Examiners builds its own item statistics on exactly that accounting:
in the [BEA 2024 shared-task data](https://sig-edu.org/sharedtask/2024) an item's
response time is "arithmetic mean response time, measured in seconds, across all
examinees who attempted a given item on a live exam", counting every second from the
item appearing until the examinee moves on, revisits included.

The second is measured, and it is that the allowance binds. On Step 2 CK,
[Ouyang et al. (2019)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6806526/) tracked 27,830
examinees and found a mean of 16.0 items revisited per block of 40 to 45, at 44.0 to
58.2 seconds per revisit by change type, so roughly a fifth of each 60-minute block
goes on second looks. Examinees who had spare time would not be spending it that way.
On the GRE, [Bridgeman et al. (2004)](https://doi.org/10.1207/s15324818ame1701_2)
gave 15,948 examinees extra time and verbal scores rose by about seven points on the
200-800 scale, which is only possible if the standard allowance was being consumed.
On the MBE the exam's own publisher sets the same pace it allows: the NCBE sample
booklet recommends 38 minutes for 21 questions, 108.6 s, against the exam's 108 s.

No bounds follow. Each allowance is a ceiling that the central sits on, so the high
bound would be the central, and no source here argues a scenario below it: every
alternative the three exams publish sits at or above the pace, the NCBE's 108.6 s and
the USMLE block's "no more than 40 questions" included, which makes 90 s the tightest
the pace gets rather than the loosest. Half a range is not a range, so the three rows
stay blank. The MMLU rows are unaffected: their 90 s is a judgment anchored on these
paces and their 45-to-125-second bounds are derived above.

## Reproduction

Run `python3 -B recompute_exams.py --sources /path/to/sources/exams-knowledge --models /path/to/models.csv --output /new/audit.json`. Install Python packages `tiktoken`, `tokenizers`, `numpy` and `pyarrow`, and Poppler's `pdftotext`. The calculator accepts either the candidate or full model registry, reads retained evidence, and refuses to overwrite evidence or an existing output. `audit.json` retains intermediate counts and inspected question text. `source-manifest.json` gives original URLs and hashes; the PDFs are the retained originals. The script takes no API credentials and does not call models.

All FLOPs use the registry's `2 × active_parameters × tokens` convention. Historical usage logs are absent for these runs. Counts below reconstruct the specified procedure; a source output cap is identified whenever it substitutes for an observed completion length. Prompt caching and context-dependent attention are not inferred from prices or latency. The GRE and PaLM central estimates count repeated full prefixes; their shared-prefix alternatives are in the audit.

The two original MMLU parity leads described interpolated model sizes. These entries instead use real GPT-3 and Llama configurations and their reported quality. The PaLM lead has been narrowed from a heterogeneous collection average to the complete 46-item `known_unknowns` task.

## Models

- **GPT-4 variants:** [Epoch's original inference analysis](https://epoch.ai/gradient-updates/moe-vs-dense-models-inference), “Estimating the MoE inference edge,” estimates arithmetic equivalent to a dense 275B model: 550B FLOPs/token. This is an architecture estimate, not a vendor disclosure. Its memory-bandwidth equivalent is a different quantity and is not used. All four GPT-4 records share this coefficient. An illustrative 175–400B active-parameter scenario multiplies every corresponding point by 0.636–1.455.
- **GPT-4 model identity:** the [technical report](https://arxiv.org/abs/2303.08774), Appendix A.7, identifies the multiple-choice exam snapshot as March 1, 2023; this is the GRE model. Section 3 and Table 2 identify the MMLU result as a pretraining-only base model. The [bar study repository](https://github.com/mjbommar/gpt4-passes-the-bar/tree/90997f740c7197f3f300b013e4345e2ad5621f96) records a hidden preliminary endpoint. These three records have no established public-release date. The [medical study](https://arxiv.org/abs/2303.13375) explicitly uses the publicly released text-only model, without an API revision; [OpenAI's original release](https://openai.com/index/gpt-4-research/) establishes March 14, 2023 for that public family. No internal snapshot date is substituted for a public-release date.
- **GPT-3:** [Brown et al.](https://arxiv.org/abs/2005.14165), Table 2.1, reports the 175B dense model; the original MMLU evaluator calls `davinci`. [OpenAI's API announcement](https://openai.com/index/openai-api/) dates its public beta to June 11, 2020. The later lifting of the API waitlist is not the initial launch.
- **Llama:** the [original model card](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/MODEL_CARD.md) and [Meta report](https://arxiv.org/abs/2407.21783) identify dense 405B base and instruction-tuned versions, both released July 23, 2024. The instruction-tuned registry record is copied unchanged; TriviaQA uses a separate base-model record.
- **PaLM:** [Chowdhery et al.](https://arxiv.org/abs/2204.02311), Table 1, reports 540.35B parameters, including embeddings. The benchmark file's `PaLM_535b` is the corresponding non-embedding-scale label, not a different 535B model. Use 540.35B × 2 = 1.0807T FLOPs/token. Public availability of these research weights is not established by the paper publication date; the release date is blank.

The cl100k and r50k vocabularies and official OpenAI tokenizer definitions are retained. GPT-3 uses r50k; GPT-4 uses cl100k. The retained Llama-family tokenizer JSON has 128,000 regular tokens and the same split expression as [Meta's original implementation](https://github.com/meta-llama/llama3/blob/main/llama/tokenizer.py). Its exact 3.1 snapshot provenance was not retained in the earlier collection, so it is explicitly a family tokenizer proxy here. PaLM's 256k SentencePiece vocabulary is described in its paper but was not released; cl100k is a text-length proxy, with ±25% token-count sensitivity. Meta's detailed evaluation files were located but require gated access; their contents and native token counts are not claimed as evidence.

## lang-exam-mmlu-gpt4

Task: choose one of four answers across MMLU's 57 subjects, with five labeled demonstrations. [GPT-4 Table 2](https://arxiv.org/abs/2303.08774) reports 86.4%. [The original MMLU paper](https://arxiv.org/abs/2009.03300), section 3, estimates 89.8% for subject experts from high-scoring exam takers and author judgments; this was not a directly tested universal expert pool. Those results are broadly comparable, so the row is `match`. The 89.8% is an estimate for the MMLU target itself, not a separate observed assessment; external calibration alone does not justify a `different_assessment` flag. Both specialist MMLU rows therefore use `none_identified`.

The calculator reads all 14,042 test questions and 285 demonstrations in the [authors' retained data archive](https://people.eecs.berkeley.edu/~hendrycks/data.tar), formats the original evaluator's five-shot prompt, counts cl100k input, and adds one answer token. The resulting 685.612875659 tokens is question-weighted. This accessible archive differs from the original paper's stated 14,079 tests by 37 questions; it is a reconstruction of the current original-author archive, not an assertion that the 2023 byte sequence is known.

Human time is estimated at 90 seconds per question for the relevant subject-qualified specialist. Inputs average 78.53 words including choices, ranging from short factual questions to legal vignettes and mathematical problems. The estimate is anchored to the 90-second USMLE and 108-second MBE paces documented below, with shorter factual items offsetting longer calculations. It targets the source's roughly 90%-correct expert performance, not four-option guessing. The bounds come from the same documented paces. MMLU's items average 78.53 words including choices against the roughly 200-word MBE stems, so the 108-second MBE pace scaled by item length puts the floor near 45 seconds. The ceiling takes the MBE pace whole and charges the one subject in five that needs calculation at three minutes: 125 seconds. No claim is made that one individual is expert in all 57 subjects.

## lang-mmlu-parity-typical

This is the original **175B davinci**, not a hypothetical 45B model. [MMLU Table 1](https://arxiv.org/abs/2009.03300) reports 43.9% five-shot accuracy. The baseline is the same subject-qualified specialist the other two MMLU rows use: the paper's section 3 estimate of **89.8%** for subject experts. The paper's unspecialized Mechanical Turk workers scored 34.5% against 25% four-choice guessing — 9.5 points above chance — so labelling an AI against them turned on noise in a weak crowdworker figure rather than on whether the AI did the job. Re-anchored 2026-09-14, matching the GPQA ruling. Under the `../COLUMNS.md` rule the expert is 64.8 points above chance, putting the floor at **57.4%**; 43.9% is 0.29 of the expert margin, so the row is withheld to `agent-work/removed/excluded.csv`.

The same original-author question archive and evaluator template are used, with r50k tokens. The evaluator removes demonstrations until the prompt fits 2,048 input tokens, then predicts one answer token. Reproducing that rule gives 689.241703461 tokens/question. Probabilities of A–D come from one next-token distribution; the prompt is not run four times. The code allows retries, but released records do not establish any actual retry workload; the estimate is one completed evaluation call.

Human time is **90 seconds**, the same specialist estimate derived for `lang-exam-mmlu-gpt4` above and used by `lang-mmlu-parity-expert`, with the 45–125-second bounds derived above. It is the dataset builder's judgment anchored to the 90-second USMLE and 108-second MBE paces, and it targets the roughly 90%-correct expert performance the baseline now names, so `human_time_evidence` stays `llm_estimate_judgment` and the statistic stays a point estimate. It replaces an earlier 60-second estimate built for the unspecialized Mechanical Turk cohort, which is no longer the human in the comparison. No measured expert MMLU timing exists in the paper or its released data.

## lang-mmlu-parity-expert

[Meta's evaluation details](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/eval_details.md) give **87.3%** macro-average accuracy for Llama 3.1 405B Instruct with five shots and no CoT. The 88.6% figure uses zero-shot CoT and is not this configuration. Use `match` against the source-estimated 89.8% MMLU expert baseline, with the same 90-second specialist duration and 45–125-second bounds described above.

The reconstructed input is the original MMLU five-shot template, plus an assumed 12 chat-format positions and the full documented 10-token generation cap. The exact Meta wrapper and mean output length were not recovered. Count each subject equally, then each question equally within subject, matching the reported macro-average. This gives 618.636852058 tokens/question. Removing nine unused output positions changes it by only 1.45%; allow ±20% for tokenizer and prompt-format differences. This is not a measured token statistic or an extrapolated trillion-parameter model.

## lang-exam-gre-verbal-gpt4

[GPT-4 Table 1](https://arxiv.org/abs/2303.08774) reports **165/170, about the 96th percentile**, for the text-only GRE Verbal evaluation. This exceeds ordinary GRE examinees. Appendix C instead lists 166 for the unfiltered text-only run; the row uses the headline table and does not reconcile these source figures into an invented score. The 169 score includes the vision condition and is not used.

The exact purchased GRE test and its few-shot examples were not released. Input length is transferred from all 35 verbal questions in [ETS's accessible Practice Test 1](https://www.ets.org/content/dam/ets-org/pdfs/gre/gre-practice-test-1-verbal-18-point.pdf), repeating each shared reading passage for every question that refers to it. They average 177.257142857 cl100k tokens. The five fully printed example explanations in GPT-4 Appendix A.8 average 166.6 tokens. The reconstruction assumes five GRE examples of this length, 15 formatting positions per demonstration, and 25 for the final wrapper: input = 5 × (177.257142857 + 166.6 + 15) + 177.257142857 + 25 = 1,996.542857143 tokens.

Appendix A.2 says the text-only GRE first samples an explanation and then samples answer letters using it. Count a fresh prefix for that second call: total = 2 × input + 2 × explanation + 8 extraction positions + 2 answer tokens = **4,336.285714286**. Reusing all prefix state would reduce this to 2,173.142857143; the central does not assume undocumented reuse. The 166.6-token explanation is a transfer, not observed GRE output; 80–350 explanation tokens gives a useful additional workload scenario.

[ETS's historical structure](https://www.ets.org/gre/test-takers/general-test/prepare/test-structure.html) specifies two 20-question, 30-minute verbal sections before September 22, 2023. Allocate the 60-minute allowance across 40 questions: **90 seconds**. This is an assumed full-allotment pace, not recorded active time. The later shorter practice booklet only supplies a workload proxy; it does not change the historical human denominator. Source percentile conversion is approximate and the paper identified training overlap in 25% of GRE verbal items.

## lang-exam-mbe-gpt4

[Katz et al.](https://michaelbommarito.com/papers/2024_GPT-4_passes_the_bar_exam_ssrn.pdf), Table 3, compares **75.7% GPT-4** with **68.0% approximate human examinee accuracy**. The [original answer file](https://github.com/mjbommar/gpt4-passes-the-bar/blob/90997f740c7197f3f300b013e4345e2ad5621f96/results/mbe/ncbe-pdf-002/experiment-001/all_results.csv) independently gives **2,726/3,600 = 75.7222%**. It contains 200 questions × two prompts × three temperatures × three runs. The recorded score uses each first-ranked answer; second/third choices do not turn this into pass@3 or a majority vote. `above` refers to that approximate national examinee baseline, not a percentile claim about all lawyers.

The exact 200 paid questions and completion strings are absent. Input length is transferred from all 21 questions in the [NCBE's official 2016 sample](https://www.ncbex.org/sites/default/files/2025-06/MBE%20Sample%20Test%20Questions.pdf), whose publisher recommends approximately 38 minutes. The calculator extracts columns in reading order, separates stem and four choices, and applies the two original prompt templates. Prompt 006 requests ranked choices and explanation; its central output uses the recorded 64-token cap. Prompt 007 only requests ranked choices; its three-line answer template has 14 tokens. Their equal-weight output estimate is 39 tokens. Mean formatted input is 275.761904762 tokens; adding the 39-token output estimate gives **314.761904762 tokens/question**. A 200–350-token question-length scenario and 14–64 output tokens show the main uncertainty; no unavailable usage counter is invented.

The human task is answering one question at ordinary bar-examinee quality, not writing a model rationale. [The study's exam format](https://michaelbommarito.com/papers/2024_GPT-4_passes_the_bar_exam_ssrn.pdf), Table 1 and Appendix I, allocates six hours for all 200 questions: **108 seconds/question**. Human_skill is expert because examinees have legal training. This is an assumed exam pace. The AI compute is averaged per response across the 18 source configurations/runs, not the sum of all 18 responses for one decision.

## lang-exam-usmle-gpt4

[Nori et al.](https://arxiv.org/abs/2303.13375), Table 2, reports **80.67%** for zero-shot GPT-4 on the official Step 1 sample exam. The prompt requests a single answer token with an A–D/etc. logit bias; no generated rationale or five-shot demonstration belongs to this configuration. Images were withheld from the text-only model.

The official URL cited in the 2023 paper now serves an April 2026 booklet. It is retained with that edition label. The calculator uses all 119 current question texts as a **workload transfer**, retaining image references but adding no visual positions: average 193.277310924 question tokens, the source's medical prompt wrapper, 12 assumed chat positions, and one output token = **228.184873950 tokens**. A ±30% workload scenario covers changes in question lengths and formatting. The current booklet is not claimed to be the historical evaluation set and its question count is not presented as the number of 2023 attempts.

The assumed human baseline is a well-prepared medical examinee achieving approximately the same 81% accuracy; `match` is by that target, not an observed national human average. The [2022 USMLE bulletin](https://www.usmle.org/sites/default/files/2021-08/2022bulletin.pdf), p.14, supplies seven 60-minute blocks for approximately 280 questions. Allocate the testing time, excluding breaks/tutorials: **90 seconds/question**. Humans normally receive the visual material; that input difference remains explicit even though the target accuracy is matched.

## lang-bigbench-parity-palm

This row covers **all 46 `known_unknowns` questions**, not BIG-bench as a whole. The task asks whether a proposed factual answer is available or the answer is unknowable: e.g. a documented birth date versus a private person's unrecorded habits. [The original PaLM score file](https://github.com/google/BIG-bench/blob/092b196c1f8f14a54bbc62f24759d43bde46dd3b/bigbench/benchmark_tasks/known_unknowns/results/scores_PaLM_535b.json) gives **73.9130% at five shots**. [The original human baseline object](https://github.com/google/BIG-bench/blob/092b196c1f8f14a54bbc62f24759d43bde46dd3b/bigbench/benchmark_tasks/task_human_eval.pkl) gives **80.2526% mean human accuracy**. The row is `below`; there is no general parity claim.

The calculator follows [BIG-bench's default prompt formatting](https://github.com/google/BIG-bench/blob/092b196c1f8f14a54bbc62f24759d43bde46dd3b/bigbench/api/json_task.py): both choices appear in each question; five other questions with correct answers form demonstrations. It calculates expected input length under uniform demonstration selection, not a claimed historical seed. With cl100k as a proxy, mean prefix = 201.369565217 tokens. Evaluating likelihood for both candidate strings with separate full prefixes gives **407.695652174 tokens**. Shared-prefix evaluation would use 206.326086957. No four-letter-choice shortcut applies: answers are full strings, and both are scored.

Human time is an assumed **30 seconds/question**, with 15–90 seconds as a scenario. The items are short and choices are supplied; recognizing unknowable personal details is usually quick, whereas some documented facts may require lookup. The [BIG-bench protocol](https://github.com/google/BIG-bench/blob/092b196c1f8f14a54bbc62f24759d43bde46dd3b/docs/paper/BIG-bench.tex), human-rater section, permits internet search. Its 30-minute to two-hour sessions do not establish per-question timings. The baseline is the mean individual rater score, not pooled best answers. `typical` represents nonspecialist knowledge workers for this common-knowledge task; the paper's generic label “expert raters” does not establish subject expertise in this task.

## lang-trivia-question-llm

The [Meta base-model card](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/MODEL_CARD.md) reports **91.8% exact match** on TriviaQA-Wiki. [Evaluation details](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/eval_details.md#triviaqa-wiki) specify the Wiki validation split, five shots, generation, and a 24-token output cap. The instruction-tuned model is not the source of this result.

The [public TriviaQA mirror](https://huggingface.co/datasets/mandarjoshi/trivia_qa/tree/0f7faf33a3908546c6fd5b73a660e0f8ff173c2f/rc.wikipedia.nocontext), pinned at `0f7faf33a3908546c6fd5b73a660e0f8ff173c2f`, retains the original Wiki QA records: **7,993 validation questions and 61,888 training question–answer pairs**, with unique question IDs. The retained [pre-conversion loader](https://huggingface.co/datasets/mandarjoshi/trivia_qa/blob/d63a76f01c8226449f76b437dd512cf8b17adf5d/trivia_qa.py) reads the original RC archive's Wikipedia QA JSON. Its no-context mode omits documents, preserving question and canonical answer text apart from stripping surrounding whitespace. Each validation question is counted once; multiple evidence pages and answer aliases do not duplicate work.

Tokenize all actual records with the Llama-family proxy, without padding, truncation or automatically added special tokens. Validation questions average **18.558363568 tokens** and canonical answers **3.198298511**; training questions average **18.496396717** and answers **3.208230998**. Assume the wrapper `Question: {question}\nAnswer: {answer}\n\n` and five demonstrations drawn uniformly from training. Tokenizing each complete demonstration gives **26.504039555** positions on average. The final unanswered query `Question: {question}\nAnswer:` averages **22.630176404** positions. Add one beginning-of-text position and an assumed eight generated positions: **5 × 26.504039555 + 22.630176404 + 1 + 8 = 164.150374181 tokens**, or **1.329618030866e14 FLOPs** at the 405B coefficient.

The eight-output-token allowance accommodates short answers and formatting beyond the 3.198-token canonical answer; it is not a measured response length. Using canonical answer length plus one stop position gives **160.348672692 tokens**, while the source's full 24-token cap gives **180.150374181**. Uniform validation demonstrations would give **164.431377455**, a 0.17% change. Allow ±20% around the central workload for the unknown exact Meta wrapper, demonstration selection and tokenizer revision. These are explicitly reconstructed inputs from the stated collection, so `compute_evidence` is `derived_assumed_inputs`. Original Meta prompts and outputs remain unavailable; access to their gated files was not required to recover the public questions.


The human target is an ordinary person using web search to answer these questions at approximately 92% exact-match quality. Assume **90 seconds/question**, including checking a source and entering the short answer, with 30–180 seconds as a scenario. The inspected examples involve specific dates, names, cultural works and multi-clue facts; many are simple lookups, while ambiguous names or dates require checking. This is a matched-quality estimate, not the original TriviaQA human reading-comprehension result: that experiment supplied documents and allowed abstention when evidence was absent. Human lookup tools differ from the model's closed-book input, so the row flags that difference.
