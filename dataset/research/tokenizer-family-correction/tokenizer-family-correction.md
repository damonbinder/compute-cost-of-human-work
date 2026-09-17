# Epoch tokenizer reconstruction

This recount keeps the existing question text, prompt templates, wrapper allowances, source output means and model coefficients. Five Gemma 2 rows change numerically. Four Llama 2/Mixtral rows gain direct vocabulary provenance but have identical counts for every question, so their numerical CSV strings are preserved.

## Vocabulary evidence

The [Gemma 2 paper, §3.1](https://arxiv.org/html/2408.00118v1#S3.SS1) explicitly shares the Gemma 1 tokenizer. We use [Google's original SentencePiece file](https://raw.githubusercontent.com/google/gemma_pytorch/33b652c465537c6158f9a472ea5700e5e770ad3f/tokenizer/tokenizer.model), pinned to `33b652c465537c6158f9a472ea5700e5e770ad3f`, SHA-256 `61a7b147390c64585d6c3543dd6fc636906c9af3865a5548f27f31aee1d4c8e2`. This replaces NeMo for the five older Gemma 2 rows. The newer GPQA 9B row already uses this file. No Gemma 3 vocabulary identity is inferred.

Llama 2 uses the [public NousResearch mirror of the named model's SentencePiece file](https://huggingface.co/NousResearch/Llama-2-70b-chat-hf/resolve/d2b9264/tokenizer.model), SHA-256 `9e556afd44213b6bd1be2b850ebbbd98f5481437a8021afaf58ee7fb1818d347`. It is a publicly mirrored model artifact, not a newly authenticated Meta download. It produces exactly the same per-question MATH counts as the earlier Phi-3 proxy.

Mixtral 8x7B uses its [original v0.1 repository tokenizer](https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1/resolve/eba92302a2861cdc0098cc54bc9f17cb2c47eb61/tokenizer.json). Mixtral 8x22B uses its [original v0.1 repository tokenizer](https://huggingface.co/mistralai/Mixtral-8x22B-Instruct-v0.1/resolve/cc88a6cc19fbd17d9f1c0ee0b0d70a748dce698d/tokenizer.json), downloaded for this audit with its repository metadata and configuration. Both produce exactly the same counts as the former Mistral 7B v0.3 proxy on the affected task inputs. The two vocabularies have different sizes; this task-specific equality is not a claim that every text tokenizes identically. The historical API's chat wrapper remains unrecovered.

`source-manifest.json` records retained originals, public mirrors, immutable URLs and SHA-256 hashes. Existing exact-tokenizer GPQA/OTIS/API rows and the unrelated Swallow training row need no correction.

## Prompt and workload

GPQA uses the retained original evaluator's `SIMPLE_COT_TEMPLATE`, all 198 Diamond questions and four choices, plus 12 assumed wrapper positions. The correct answer is placed first solely for this input-length reconstruction, as before; actual evaluation answer-order permutations are unavailable. MATH uses all 1,324 Level-5 problem statements, including Asymptote source, plus 50 assumed instruction/chat positions. The seven Parquets retain all 5,000 original test problems. OTIS uses all 45 original question texts and the previously recovered later-run instruction, plus 12 assumed chat positions. These are the same inputs as the earlier calculations.

All tokenizers count content without automatic special tokens; wrapper positions are added once. Reported output comes from the exact identifier/benchmark row in [Epoch's original output table](https://epoch.ai/data/charts/output-length/scatter_data.csv). That output is unchanged, with no second reasoning addition. Historical input/cache/retry counters remain absent: all reconstructed input is treated as fresh, not observed zero cache reuse. FLOPs are `(mean input + mean reported output) × unchanged model coefficient`. Context-dependent attention is omitted by that method and added back in `compute_flops` (`research/attention-correction.md`).

Human duration, skill, performance labels, task scope and comparison flags are unchanged. Their task evidence remains in the existing [GPQA](../epoch/gpqa.md), [MATH](../epoch/mathl5.md) and [OTIS](../epoch/otis.md) notes. Current tokenizer counts supersede the older proxy arithmetic for these nine identifiers; original values are retained in the collection audit.

## Reproduction

Python 3.10 or later with `tokenizers`, `sentencepiece` and `pyarrow`. Recorded versions are in `calculations.json`. The script uses explicit paths and retained files only:

```sh
python3 /path/to/research/tokenizer-family-correction/recompute.py --sources /path/to/sources/tokenizer-family-correction --points /path/to/points.csv --models /path/to/models.csv --output /path/to/new-calculations.json
```

The `--points` input may be either the archived or corrected CSV: the script checks that its coordinates match one of those two source-derived calculations. It does not take token inputs from the CSV. The output must be new and outside the source directory. Source hashes and original table joins are checked before writing. The audit proposal separately requires exact old row values before staging any changes. All per-question counts are retained, not only means. No source, CSV or model file is modified by the calculator.

## reas-epoch-gpqa-gemma2-27b

Original table key: `gemma-2-27b-it` × `GPQA diamond`. Input **266.535353535** + unchanged output **330.404040404** = **596.939393939 text tokens**. At 54455436288 FLOPs/token: **3.25065951345e+13 FLOPs**.

The old proxy mean was 268.247474747; 186 question counts differ. The total FLOP change is -0.285996%. A ±50% change in estimated input changes total compute by ±22.3%; the 12-position wrapper remains assumed.

## reas-epoch-gpqa-mixtral8x22b

Original table key: `open-mixtral-8x22b` × `GPQA diamond`. Input **302.101010101** + unchanged output **544.065656566** = **846.166666667 text tokens**. At 78000000000 FLOPs/token: **6.6001e+13 FLOPs**.

The old proxy mean was 302.101010101; 0 question counts differ. The total FLOP change is +0%. A ±50% change in estimated input changes total compute by ±17.9%; the 12-position wrapper remains assumed.

## reas-epoch-mathl5-gemma2-27b

Original table key: `gemma-2-27b-it` × `MATH level 5`. Input **138.867824773** + unchanged output **468.844410876** = **607.71223565 text tokens**. At 54455436288 FLOPs/token: **3.30932349299e+13 FLOPs**.

The old proxy mean was 136.972054381; 1019 question counts differ. The total FLOP change is +0.312928%. A ±50% change in estimated input changes total compute by ±11.4%; the 50-position wrapper remains assumed.

## reas-epoch-mathl5-gemma2-9b

Original table key: `gemma-2-9b-it` × `MATH level 5`. Input **138.867824773** + unchanged output **434.913897281** = **573.781722054 text tokens**. At 18484329472 FLOPs/token: **1.06059703955e+13 FLOPs**.

The old proxy mean was 136.972054381; 1019 question counts differ. The total FLOP change is +0.331494%. A ±50% change in estimated input changes total compute by ±12.1%; the 50-position wrapper remains assumed.

## reas-epoch-mathl5-llama2-70b

Original table key: `Llama-2-70b-chat-hf` × `MATH level 5`. Input **143.668429003** + unchanged output **433.097432024** = **576.765861027 text tokens**. At 140000000000 FLOPs/token: **8.07472205438e+13 FLOPs**.

The old proxy mean was 143.668429003; 0 question counts differ. The total FLOP change is +0%. A ±50% change in estimated input changes total compute by ±12.5%; the 50-position wrapper remains assumed.

## reas-epoch-mathl5-mixtral8x22b

Original table key: `open-mixtral-8x22b` × `MATH level 5`. Input **143.9418429** + unchanged output **689.314199396** = **833.256042296 text tokens**. At 78000000000 FLOPs/token: **6.49939712991e+13 FLOPs**.

The old proxy mean was 143.9418429; 0 question counts differ. The total FLOP change is +0%. A ±50% change in estimated input changes total compute by ±8.64%; the 50-position wrapper remains assumed.

## reas-epoch-mathl5-mixtral8x7b

Original table key: `Mixtral-8x7B-Instruct-v0.1` × `MATH level 5`. Input **143.9418429** + unchanged output **512.561178248** = **656.503021148 text tokens**. At 25800000000 FLOPs/token: **1.69377779456e+13 FLOPs**.

The old proxy mean was 143.9418429; 0 question counts differ. The total FLOP change is +0%. A ±50% change in estimated input changes total compute by ±11%; the 50-position wrapper remains assumed.

## reas-epoch-otis-gemma2-27b

Original table key: `gemma-2-27b-it` × `OTIS Mock AIME 2024-2025`. Input **194.6** + unchanged output **707.377777778** = **901.977777778 text tokens**. At 54455436288 FLOPs/token: **4.9117593411e+13 FLOPs**.

The old proxy mean was 194.533333333; 35 question counts differ. The total FLOP change is +0.00739171%. A ±50% change in estimated input changes total compute by ±10.8%; the 12-position wrapper remains assumed.

## reas-epoch-otis-gemma2-9b

Original table key: `gemma-2-9b-it` × `OTIS Mock AIME 2024-2025`. Input **194.6** + unchanged output **567.6** = **762.2 text tokens**. At 18484329472 FLOPs/token: **1.40887559236e+13 FLOPs**.

The old proxy mean was 194.533333333; 35 question counts differ. The total FLOP change is +0.00874738%. A ±50% change in estimated input changes total compute by ±12.8%; the 12-position wrapper remains assumed.

