# Learning one random binary string

## memo-binary-1024-llama2-13b

The point estimates the cost of learning one new, uniformly random 1,024-symbol a/b string. The assessment asks for each next symbol with its entire correct prefix supplied. It does not ask for one uninterrupted recitation. A human 0/1 string is equivalent under a fixed a/0, b/1 substitution.

The AI starts from pretrained Llama-2-13B and uses the published fixed training recipe for 100 epochs. The human starts with world-class binary-memory techniques already learned. Both values cover acquisition of this particular string, including learning checks, and exclude a separate later performance attempt. `memory_recall` and `human_time_scope=task_performance` follow Damon's 2026-09-14 ruling that learning 1,024 random bits is memorization, not skill acquisition; this is not an estimate of acquiring general memory skill. The compute scope stays `additional_training`, which describes the run rather than the kind of work.

### Original experiment and model

[Speicher et al., version 1](https://arxiv.org/abs/2407.19262v1), sections 2–3 and Appendix A.1–A.2, specify one individually tokenized character per position, five independently sampled strings, and 100 one-string epochs. Figure 1(c)'s blue curve ends at approximately **96% correct next symbols**; this is a visual reading, not an exported exact score. The uniform binary guessing baseline is 50%. The human target is assumed to be the same approximately 96% prefix-cued accuracy. `match` is therefore a matched-quality estimate, not an observed human comparison.

The original authors' [released repository](https://github.com/tillspeicher/llm_memorization/tree/ae5d63d791d903f7dc4f2b63ba9a80185b2b6be4) maps `llama2-13b` to the base `Llama-2-13b-hf`, separately from its chat variant (`agent-work/sources/memorization-leads/code/src/defs.py`). Meta's [July 18, 2023 announcement](https://about.fb.com/news/2023/07/llama-2/) establishes public availability. The [original Llama 2 paper](https://arxiv.org/abs/2307.09288), Table 1, reports the dense 13B size. We use that rounded count and 26 billion FLOPs per forward token, not a purported exact tensor count.

### Operation count

**Central: 94,040,128,000,000,000 FLOPs**, consisting of 8,049,600,000,000,000 training FLOPs and 85,990,528,000,000,000 monitoring FLOPs. The monitoring schedule is a substantial assumption: it follows the authors' public code released **December 20, 2024**, five months after the July paper. The repository has no historical run trace proving that the July run used every retained callback. `compute_evidence=derived_assumed_inputs` reflects this implementation transfer.

The retained implementation supplies the most concrete available operation recipe. Its exact source locators are:

| Component | Original retained locator | Positions in one learning run |
|---|---|---:|
| Character tokens and beginning-of-string token | `code/src/data/synthetic_strings/utils.py`, `alphabet_encoding`, `SyntheticStringData.token_ids` | 1,025 before padding |
| Training collator pads to a multiple of 8 | `code/src/lib_llm/lib_llm/training/train.py`, `_train` | 100 × 1,032 = 103,200 |
| Ten held-out random strings | `code/src/data/synthetic_strings/random.py`, `default_num_test_strings`; `utils.py`, `to_test_config` | 10 strings |
| Initial callbacks and callbacks at each epoch | `training/train.py`; `code/src/utils/memorization/memorization.py` | 101 evaluations per split |
| Both training and held-out split callbacks | `code/src/experiments/memorization_dynamics/experiment.py`, `memorization_eval_tasks` | 11 sequences per evaluation |
| Separate loss and correctness forwards | `code/src/lib_llm/lib_llm/eval/metrics/eval_tasks.py`, `_produce_metric_args` | 2 × 101 × 11 × 1,024 = 2,275,328 |
| Trainer's own held-out validation | `training/train.py`, `eval_dataset`; epoch evaluation setting above | 100 × 10 × 1,032 = 1,032,000 |

The metric callback trims the last input position (`inference/_batch_mapping.py`), hence 1,024 processed positions per sequence. `LossMetric` requests logits; `CorrectnessMetric` requests token probabilities. The released argument cache calls `predict` again for the latter key even though an output is already stored. This is not a second autoregressive generation. All forwards process their supplied sequence; no retained KV cache is reused between evaluations. The callback's within-batch deduplication does not materially reduce ten independent random 1,024-bit sequences.

With P = 13 billion, the recipe is:

`6P × 103,200 + 2P × (2,275,328 + 1,032,000) = 9.4040128e16 FLOPs`.

Only **103,200 training positions** go in the CSV's `tokens` field. The separate 3,307,328 monitoring positions enter FLOPs here. There are no other model helpers in this recipe. The 6P/2P approximation omits context-dependent attention and small optimizer/scalar costs; a +5% arithmetic-overhead scenario is 9.87421344e16 FLOPs. BF16 execution does not halve the operation count. The released setup does not request gradient checkpointing.

The historical monitoring uncertainty is larger:

| Monitoring scenario | Total FLOPs |
|---|---:|
| Released two-forward callbacks, central | 9.4040128e16 |
| One forward per callback, same held-out and Trainer evaluations | 6.4460864e16 |
| One training-string forward initially and per epoch, no held-out or Trainer evaluations | 1.0738624e16 |
| Weight-update training alone, excluding required monitoring | 8.0496e15 |

The third row is a minimal-monitoring scenario, not a claim that the authors ran this stripped-down implementation. No search over epochs or selection of a successful seed is assumed. The paper's five runs establish the performance mean; this point counts a single run of the fixed recipe. Its research-wide learning-rate search and other ablations are excluded. The input learning rate is already fixed at 1e-5; the point does not measure the cost of discovering it.

### Human learning time

**Central: 270 seconds**, estimated for an already trained world-class binary-memory competitor. The donor observations are the three medallists' study rounds in the [2019 World Memory Championships binary event](https://www.worldmemorychampionships.com/wp-content/uploads/2019/12/Binary.pdf): Ryu Song I, Kim Su Rim and Jon Kum Phyong, with 7,485, 6,805 and 6,585 credited digits. The [record certifier](https://www.guinnessworldrecords.com/world-records/360573-most-binary-digits-memorised-in-30-minutes) identifies the event's 30-minute memorization period. We treat that prescribed period as active study; individual early-finish clocks are unavailable.

Quantity-scaling each study rate to 1,024 digits gives 246.25, 270.86 and 279.91 seconds. Their mean is 265.67 seconds, rounded to the 270-second target estimate. The source's [chief-arbiter explanation](https://www.worldmemorychampionships.com/the-binary-digits-discipline/) describes encoding six bits into a mnemonic image and placing successive images on a route. A 1,024-bit target takes about 171 such six-bit units; the donor rates imply roughly 1.56 seconds per unit. This is a transfer of a relevant encoding process, not an estimate from ordinary reading speed.

Three differences prevent treating 270 seconds as a measured target-task time. The competition requires later recall without a supplied correct prefix; our target is cued and permits approximately 4% errors. The shorter target may also be easier to learn than the several-thousand-digit competition load. Finally, credited digits are penalized by row errors: they are not a raw count of correct independent predictions or an observed 96% score. We retain the undiscounted encoding rate as a conservative central calibration because these sources do not establish an exact cueing benefit. The human next-bit assessment itself is an assumed target, not the competition test copied unchanged.

The bounds are the donors' own dispersion: the three quantity-scaled medallist rates are 246.25, 270.86 and 279.91 seconds, so the bar runs **246 to 280 seconds**. It carries only the spread among the three recorded study rounds. The prefix cueing, the shorter list and the 4% error allowance all point below that band, and repeated checking or a less efficient transfer points above it; none of those is quantified here, so none of them is in the bar. The separate competition recall phase is not added: its allowed time is not an observed active duration, and the point concerns learning rather than subsequent recall execution. Prior training in mnemonic methods is excluded, just as the model's prior pretraining is excluded.

Use `transferred_timings`, `estimated`, `point_estimate`, `world_class`, `human_attempts=3` and `human_time_subset=all`. The three contributing records are all recorded study rounds within the selected medallist population, not a target-task sample of three. Medals select the skill group; no successful-attempt threshold is applied to the rounds. `none_identified` compares the explicitly constructed human target with the AI's prefix-cued target; the donor task's different test is a limitation of the timing transfer, not a second actual assessment used to establish human performance.

### Reproduction

`source-inputs.json` separates reported quantities and assumed transfers. `source-manifest.json` hashes the retained sources and extracts. The source tree and code-blob manifests retain original Git identities. Run with Python 3.9+ standard library:

```sh
python3 -B /absolute/path/to/research/recompute.py --sources /absolute/path/to/sources --output /tmp/new-memorization-calculation.json
```

The calculator verifies retained hashes and the medal-score extraction, reads relevant released code constants, and writes a new output without running a model or changing evidence. Its output should equal `research/calculations.json`.
