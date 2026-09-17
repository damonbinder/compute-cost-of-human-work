# Swallow-70B: continued learning for Japanese commonsense questions

**The human-learning estimate in this note is superseded.** On 2026-09-14 the
human side of every row it covers was re-estimated as the active hours to reach the
capability the run bought, read off a published hours-to-proficiency table, rather
than the hours to move a benchmark score. The current figures, the method and the
per-row arithmetic are in [skill-acquisition human learning time](../skill-acquisition-human-time.md).
Everything else here — the endpoints, the task inspection and the compute
reconstruction — still stands.

## lang-xfer-ja-swallow70b

The work is one complete 100-billion-token continued-pretraining run, from Llama 2-70B to vocabulary-expanded Swallow-70b-hf, evaluated on Japanese five-choice commonsense questions. JCommonsenseQA accuracy rises from 86.9% to 93.5%. The human target is an ordinary adult who already reads Japanese and achieves approximately the starting score, improving to the ending score on comparable unseen questions. This is not learning Japanese from scratch. All continued-training compute is charged; none is allocated away because other skills also improve.

JCommonsenseQA is chosen because it is an original, source-native Japanese comprehension/knowledge assessment with an interpretable correct-answer target and independent human results. The source's composite mixes accuracy, character F1, BLEU and ROUGE; its seven-point increase does not define a coherent human learning endpoint. JEMHopQA and NIILC additionally require retrieving particular facts. JCommonsenseQA still includes cultural knowledge, but ordinary adults can usually supply the underlying everyday concepts already. This point does not claim to summarize every consequence of Swallow training.

### Original evidence and inspected task

[Fujii et al., arXiv:2404.17790](https://arxiv.org/abs/2404.17790), retained `paper.pdf`, Table 2: 1,119 development questions, four demonstrations, exact-match answer accuracy; Table 4: 86.9→93.5. Appendix D.4 reports approximately 5.0e22 training FLOPs, calculated with an adaptation of Narayanan's formula to Llama. Section 4.3 evaluates Japanese benchmarks at approximately 20B-token intervals. These are the base models, not the separately instruction-tuned or no-vocabulary-expansion variants.

Original [JGLUE v1.1.0 data](https://github.com/yahoojapan/JGLUE/tree/v1.1.0/datasets/jcommonsenseqa-v1.1) are retained as `jcqa-valid.jsonl`. `question-inspection.json` preserves 60 questions selected with seed 70, not selected for ease. They include everyday nouns and actions, definitional descriptions, loanwords, written lexical distinctions, idioms and Japanese cultural associations. Examples:

- q9087 defines a shore using transported/deposited sand; answer 砂浜.
- q9090 asks what unrecoverable loan debt is called; answer 焦げ付き, a nonliteral usage.
- q9214 asks about a rakugo name; answer 古今亭, requiring cultural lexical recognition.
- q9407 distinguishes returning to one's hometown (帰郷) from home/other returns.
- q9757 asks for the homophone of an anchor; selecting 怒り requires pronunciation as well as character recognition.
- q9821 distinguishes a seam from a join or patch.

Many distractors are plainly unrelated. Some prompts are awkward or underspecified: q10057 offers several body-related things that could be used in experiments, while the gold answer is 人体. Targeting 93.5% does not require resolving every questionable item. Five-way guessing gives 20%, far below both endpoints. There are no released per-item starting/ending predictions here, so we cannot identify which errors improved or assume the six-point gain is exclusively vocabulary learning.

The [original JGLUE paper](https://aclanthology.org/2022.lrec-1.317/) Table 9 reports human development accuracy 98.6%, obtained by crowdsourcing (§4.2). It supports attainability by Japanese-proficient humans, not a measured score for the proposed L2 learners. Its raters are not timing donors. The human baseline in this row is expressly defined to reach the AI endpoint, hence `match`.

The benchmark was publicly released before the continued-pretraining corpus. The retained Swallow paper does not establish item-level decontamination. Consequently the observed gain may partly reflect prior exposure; the proposed human route targets unseen questions. We do not claim demonstrated contamination or add a known-difference flag for a possibility. A confirmed overlap finding would warrant revising that comparison.

### Human duration: 60 active hours, with 20–200-hour scenarios

The assumed learner is an adult learning Japanese as an additional language, already reading well enough to score about 86.9% on these questions, with remaining vocabulary, idiom and cultural-knowledge gaps. We do not map this starting score to a JLPT/CEFR level or charge prior language learning. People with the same accuracy can have different weaknesses; the estimate applies to this specified learner, not every Japanese reader scoring 86.9%. The model's unrecovered individual errors do not establish that it has the same weaknesses.

The proposed route comprises 30 hours of varied contextual reading, 20 hours of focused vocabulary and expression practice with spaced retrieval, and 10 hours of mixed unseen commonsense questions with feedback. These are selected study budgets. Reading expands usage beyond memorizing evaluation answers. Focused practice addresses the inspected nonliteral meanings, homophones, lexical near-neighbors and cultural terms. Final practice checks applying those distinctions to new five-choice questions. The total includes unsuccessful practice and review, without generative-AI assistance.

[Peterson (2022), Japanese Extensive Reading](https://www.readingmatrix.com/files/27-sld3j1b6.pdf), retained as `human-reading.pdf`, provides context for the reading block. Table 5 records eight active-reading totals: 25:16, 23:28, 33:30, 26:26, 21:37, 46:52, 17:06 and 19:17 hours:minutes, averaging 26.69 hours. Participants read approximately 152,000–317,000 characters. Tables 6–7 concern reading speed, not JCommonsenseQA accuracy. Five learners had substantial prior immersion; two concurrently took classes and one also studied independently. Recorded times exclude choosing books and conversation. These observations demonstrate feasible reading-program durations but do not establish how much reading produces the target accuracy gain. They are contextual observations, not contributing timing attempts for this estimate.

The [Peterson and Warnick study](https://jalt-publications.org/content/index.php/jer/article/download/petersonandwarnick/124), retained as `human-modes.pdf`, provides a further qualification. Its 144 course-enrolled learners were assigned 14 monitored 50-minute activities. Reading and control groups had similar vocabulary gains; other coursework or repeated testing could explain the result. Neither its activity duration nor its vocabulary gain supplies a learning rate for this target.

Sixty hours is a coarse judgment about a focused route for someone already answering most questions correctly. The reading studies support its practical scale, not a conversion from accuracy gain to hours. Improving unfamiliar-expression recognition and discriminating nearby meanings requires more than rehearsing the benchmark answers. Reducing the remaining error rate by roughly half may nevertheless take substantially longer. The 20-hour scenario assumes concentrated, readily correctable gaps; the 200-hour scenario assumes dispersed unfamiliar vocabulary or cultural knowledge and slower retention. These are alternative assumptions, not statistical bounds or observed outcomes. No measured learning curve connects the specified endpoints.

Fields are `assumed` / `estimated` / `point_estimate`, with `human_time_subset` and `human_attempts` both `not_applicable`. The eight recorded reading programs remain in the calculation as context, without implying eight observations or calibration attempts for the 60-hour transition. Human targeted instruction, retrieval practice and feedback differ from the AI's next-token corpus training, recorded as `different_inputs_or_tools`. The proposed endpoint uses the same question format and unseen-task criterion; the contextual studies do not establish an additional assessment or human-baseline difference. The AI's full continued-training cost is retained, without allocating it to this single capability or requiring the human to read the AI's corpus.

### Training and associated evaluation computation

The architecture is independently verified against release revision `edfae4884797a424a92d017a256f043e1694d693`: 80 layers, width 8,192, FF width 28,672, 64 query heads/8 KV heads, vocabulary 43,176, untied embedding/output. Current and release configurations differ only in the architecture class spelling (`LLaMAForCausalLM` versus `LlamaForCausalLM`), not dimensions. Direct count is 69,159,755,776 parameters, including both embedding matrices and norms; its basis is `reported` under COLUMNS.

For a cross-check, let D=8192, K=1024, F=28672, L=80, V=43176 and S=4096. Linear weight count used in each forward pass is L(2D²+2DK+3DF)+DV. Causal attention adds 2LD(S+1) FLOPs per token, in addition to twice that linear count. Forward cost is 142,979,497,984 FLOPs/token. Three/four forward equivalents over 100B tokens give 4.29e22/5.72e22 FLOPs. The source's 5.0e22 lies between these; its precise activation-recomputation recipe is not published. We retain the authors' explicit Llama-adjusted training computation rather than asserting either reconstructed extreme is a measurement. FlashAttention2 is explicitly reported. AdamW and scalar nonlinear overhead are not separately recovered; the rounded source figure is an approximate neural arithmetic budget, not hardware measurement.

Associated benchmark work is included separately. Original Japanese/English dataset counts are in Tables 2/3. The central estimate charges six Japanese evaluations (initial plus five trained checkpoints) and two English evaluations (initial/final), with explicit four-way branches for OpenBookQA/HellaSwag and two for XWinograd. Mean 2,048 processed positions per sequence is an assumption; native prompts and output counters were not recovered for all benchmarks. This gives 428,515,328 positions. It uses full-prefix matrix processing with no cache reduction; the attention allowance uses S=4096. As a small allowance for unreported loss validation, add 24 full global-batch equivalents (1024×4096 tokens), corresponding roughly to one per thousand of the approximately 23,842 updates. This is an accounting assumption, not a recovered configuration.

Associated work adds 7.57e19 FLOPs (0.151% of reported training). Charging all checkpoints in English, twice the evaluation length, and ten times the loss monitoring still adds under 0.9%. Rounded to the original two-significant-figure precision, the full estimate remains **5.0e22 FLOPs**. `operation_count` reflects adding this operation-based allowance to reported training, with `derived_assumed_inputs`. The 100B `tokens` field contains training tokens only. No unrelated 7B/13B models, initial Llama2 pretraining, no-vocabulary ablations or instruction tuning are included.

### Model identity and release

[Original AIST announcement, 19 December 2023](https://www.aist.go.jp/aist_j/press_release/pr2023/pr20231219/pr20231219.html) establishes public release; retain this date. HF commit history contains November uploads, but upload dates do not establish that a then-private repository was public. Model ID `swallow-70b-base` distinguishes the base model from instruction-tuned variants. Company names follow the contemporary Tokyo Institute of Technology/AIST collaboration.

### Reproduction

Python standard library only:

```
python research/swallow/recompute.py --sources agent-work/sources/swallow --output /path/to/new-calculations.json
```

Use the actual published source and script paths if the collection is nested differently. The script rejects overwriting an output or writing beneath the source directory. `calculations.json` retains source hashes, parameter arithmetic, associated work, contextual reading times and assumed learning scenarios. `question-inspection.json` retains the exact seeded sample. No model execution is required.
