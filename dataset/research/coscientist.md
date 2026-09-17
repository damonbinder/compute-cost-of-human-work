# Coscientist reaction optimisation

These three points describe sequential scientific decisions with an archived-yield oracle. They do not measure laboratory work, model training, or the time required to discover a new reaction.

## Evidence and work unit

Boiko et al., [Autonomous chemical research with large language models](https://doi.org/10.1038/s41586-023-06792-0), published 20 December 2023. An [open manuscript](https://par.nsf.gov/servlets/purl/10490898) is retained by NSF. Figure 6 and its accompanying section describe the 20-step optimisation game, distinct from Figure 5's physical apparatus demonstration. The actual yields were collected previously; they are returned immediately in these dialogues. The source's comparator is Bayesian optimisation, not measured human chemists.

Original messages: [author repository, commit 417e82b85743f88719ba7cf8838220fcb872e2ae](https://github.com/gomesgroup/coscientist/tree/417e82b85743f88719ba7cf8838220fcb872e2ae). The retained files in `coscientist/` are byte-for-byte copies, with SHA-256 hashes in `inputs.json`. Each row represents the mean of all retained GPT-4 runs in one source condition. No success filter was applied. The number of runs is not a human sample count. The source conditions have different substrate mixes; the prior/no-prior comparison is not a controlled estimate of the benefit of prior information.

| Retained file | Original location | Included GPT-4 runs | Other runs retained but not proposed |
|---|---|---:|---:|
| buchwald-hartwig.csv | optimization/Buchwald-Hartwig/all_logs.csv | 141 | 43 GPT-3.5 |
| suzuki-no-prior.csv | optimization/Suzuki/no_prior_information.csv | 165 | 70 GPT-3.5 |
| suzuki-prior.csv | optimization/Suzuki/prior_information.csv | 150 | 78 GPT-3.5 |

All included dialogues contain 42 ordered messages: system, task, and 20 assistant proposals alternating with feedback. Invalid choices consume a proposal. The final feedback is not passed through another model call. The Buchwald-Hartwig file's `smiles` field is False throughout, despite a SMILES condition discussed in the paper; no missing SMILES results are inferred. Source IDs are unique within each retained file, but must be qualified by source file across files.

## Compute reconstruction

`coscientist/recompute.py` accepts explicit input/output paths and writes a new JSON. Dependencies: Python 3 and `tiktoken==0.14.0`; the `cl100k_base` encoding may download on first use. Example from the research directory:

```sh
python coscientist/recompute.py --input-dir coscientist --output-json /tmp/coscientist-check.json
```

For each assistant message, input is every previous message's content token count plus role tokens and three framing tokens per message, then three assistant-priming tokens. Output is the retained assistant content plus one assumed terminator token. Tokenization uses `cl100k_base`; these are reconstructed processed counts, not API usage counters. Exact hidden formatting and API snapshot are unavailable. The framing approximation is the standard GPT-4 chat-count convention; token counts should not be interpreted as exact provider bills.

The [author's simple implementation](https://github.com/gomesgroup/coscientist/blob/417e82b85743f88719ba7cf8838220fcb872e2ae/simple_implementation/coscientist.py) sends accumulated history on each call. It is not the exact optimisation harness. Full-prefix reprocessing is an explicit assumption, supported by the complete short dialogues and the lack of any retained compaction. All reconstructed calls fit within 4,005 positions, below the original GPT-4 8k window. No cache-read saving, hidden retries, helper calls or hidden reasoning tokens are invented. This bounded game has one assistant stream and deterministic yield feedback; the multi-agent web-search system used for other demonstrations is not part of this work unit. Calls that generate invalid selections are retained.

For a call processing `p` positions, attended position pairs are `p*(p+1)/2`. Sum across its 20 calls, then average both positions and pairs across the group. `attention_context` is mean pairs divided by mean processed positions. FLOPs are `2*N*mean_positions + 4*L*W*mean_pairs`. The model dependency is existing `gpt-4-original-unspecified`: N=275 billion, L=73, W=14,336. This is a frozen copy of the current shared registry in `model-inputs.csv`, not a new architecture claim. Exact run snapshot remains unspecified.

For low/high, use N=200/350 billion and recompute the current estimated architecture: D=round((N/196608)^(1/3)), L=round(0.65*D), W=128*D. Per-call context is fixed at both ends. No cache-implied context band applies. These bounds do not cover the full-prefix assumption, hidden formatting or human-time uncertainty. No dollar amount is inferred from reconstructed tokens.

| Point | Mean processed tokens | Mean attended context | FLOPs | Parameter-range FLOPs |
|---|---:|---:|---:|---:|
| Buchwald-Hartwig | 30,988.81 | 883.91 | 1.71585e16 | 1.24890e16–2.18262e16 |
| Suzuki without prior | 22,221.24 | 649.97 | 1.22821e16 | 8.93779e15–1.56256e16 |
| Suzuki with prior | 32,526.06 | 898.63 | 1.80117e16 | 1.31102e16–2.29113e16 |

## Human-time assessment

The target is an expert organic chemist doing this constrained decision task, unaided by an LLM, with the same menu, initial records and instant feedback. It includes choosing conditions and recording short reasons; it excludes acquiring reagents, preparation, experiments, analysis instruments and waiting. It does not give the human the AI's answers in advance. The estimate targets comparable search behaviour and attained yields rather than optimal experiment design. Thus `match` is a stated target, not evidence that human and AI performance were measured as equal.

Full low-, middle- and high-best-yield dialogues were selected deterministically by sorting `(best_yield, run_id)`. The selected messages are retained in the three `*-inspected-dialogues.md` files. The rationales are generally one sentence; the common pattern is swapping a condition, reverting after a worse yield, or exploring another listed choice. Some high-yield runs repeatedly resubmit the same choice after reaching 100%. This is neither a literature review nor detailed mechanistic research. Those observations put the task closer to a short interactive analysis exercise than a day-long research assignment.

All durations below are builder judgments, not transferred measured rates. The 1.5 minutes per proposal allowance covers reading feedback, comparing with a small history, choosing from menus and entering a brief reason. Many repeat choices take less; difficult early choices take more. It is a coarse average, not a claim that every step needs 90 seconds. Repeated choices are retained for both parties because the work unit requires 20 proposals. Sensitivity of roughly 20–90 active minutes per dialogue is reasonable; this is not a statistical interval and is not entered into the model-parameter FLOP bounds. A timing study could move the y-coordinate substantially. The three central durations differ only by initial information load; they should not be read as precise measured differences.

### research-coscientist-buchwald-hartwig-gpt4

45 minutes (2,700 seconds): about 10 minutes to understand the reaction and the longer additive menu, 30 minutes for 20 choices and feedback, and 5 minutes to check the resulting record. The menu has four ligands, 24 additives and three bases. Inspected runs 69, 40 and 93 reach best yields of 2%, 66% and 100%, respectively. Run 40 repeatedly switches combinations; run 93 holds a productive combination and explores additives. Average best yield across all 141 runs is 65.96%, with 17.74 distinct proposals on average. There are 14 invalid-choice feedback messages across the group. The estimate reproduces this mixed quality, not a guarantee of high yield for difficult substrates.

### research-coscientist-suzuki-no-prior-gpt4

40 minutes (2,400 seconds): 5 minutes to inspect the task and three menus, 30 minutes for sequential decisions and short reasons, and 5 minutes to check the record. Inspected runs 56, 36 and 181 reach best yields of 24%, 86% and 100%. Run 36 illustrates local changes and reversion; run 181 revisits its strongest combination. Across 165 runs, mean best yield is 81.22%, mean distinct proposals 17.90, and 11 feedback messages reject a choice. The expert target is the same kind of constrained search, including lower-yield instances.

### research-coscientist-suzuki-prior-gpt4

45 minutes (2,700 seconds): the same 35-minute decision/record allowance plus 10 minutes to inspect the task, menus and ten supplied reaction records. Those records can include other substrate pairs and are not simply ten earlier trials of the exact target reaction. Inspected runs 7, 22 and 51 reach best yields of 28%, 85% and 100%. Run 51 reaches 100% at proposal eight and then mostly repeats it. Run 22 makes a disallowed final proposal; its cost remains counted. Across 150 runs, mean best yield is 80.94%, mean distinct proposals 16.43, and 24 feedback messages reject choices.

## Uncollected work from the study

GPT-3.5 runs are retained as raw evidence but not proposed in this first collection. The paper's SMILES condition is not represented by the inspected BH file. Synthesis planning, large-library selection and Figure 5's laboratory execution are separate tasks, not extra copies of these average compute values. The public repository's laboratory-choice summary tables do not contain complete planner/search/documentation histories. Figure 5 used manual plate movement; a future row would have to restrict the human comparator to autonomous planning/programming or separately account for that physical assistance. The colour-identification demonstration used a human hint and is not proposed as autonomous work. Those dispositions account for the study's other demonstrations without claiming they were processed into released rows.
