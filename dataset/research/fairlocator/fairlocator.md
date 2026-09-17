# FairLocator: one image geolocation judgment

## perc-geolocation-fairlocator-gpt4o

The point estimates **2.84 × 10¹⁴ FLOPs and 45 seconds of human effort** for one independent image judgment in FairLocator's 100-image user study. GPT-4o is **above** the ordinary university-student baseline on the three shared location labels. The model also writes an analysis, street and coordinates; that additional work is included in compute and is a `different_task` qualification.

These are workload and duration estimates. The public release contains neither individual response texts for this experiment, usage counters, retry records nor human clocks. The score comparison is reported by the original study; it is not a rescore of released answers.

## Task and performance

The [final EMNLP paper](https://aclanthology.org/2025.emnlp-main.910.pdf), §4.4 and Table 6 (PDF pages 5–6), defines 100 images arranged in ten questionnaires of ten images. Each questionnaire is assigned to three university students. Participants supply continent, country and city without search engines or VLMs. The AI protocol obtains three independent responses per image (§3.2); these are not a pooled vote. This point is one such judgment, so neither side is multiplied by three.

Table 6 reports GPT-4o continent/country/city accuracy of **86.0% / 74.0% / 63.3%**, against human **33.7% / 9.5% / 1.7%**. The paper says most students were unfamiliar with the images and guessed. This directly supports above on the shared labels. It does not establish the correctness of GPT-4o's explanations, street or coordinates. Human country accuracy is not an integer multiple of 1/300, so the reported percentages are retained without inventing correct-answer counts or an explanation for the denominator discrepancy.

The original [repository](https://github.com/limenlp/FairLocator/tree/f9722e9a3315882933b4414a3567256777c48168) is pinned at `f9722e9a3315882933b4414a3567256777c48168`. `SourceData/Human.xlsx` contains 100 ground-truth label rows, not submitted responses or timings. Its last `Result` row is a footer. The calculator verifies IDs 1–100 and ten groups of ten. The paper describes selection of 100 from a randomly sampled subset; this is the original cohort, not a new sample selected for model success. It does not provide enough retained image identifiers to recover every exact human-study view from the broader coordinate workbook.

The human form (final PDF page 21, Figure 6; original preprint PDF page 15) supplies six continent choices and free-text country/city fields. The AI answers continent freely. This small format advantage to humans does not explain the large country/city gap. The substantive flagged difference is that AI must produce extra deliverables.

## Human effort

The inspected questionnaire example shows a coastal promenade, sea, lamps, a bench and distant apartment blocks, without an obvious readable location sign. It asks for three labels and no justification. The four street-view illustrations on PDF page 20 show ordinary urban streets and a wooded overlook; they help establish the kind of scene but are not asserted to be the exact 100 human-study images.

The **45-second** estimate describes an ordinary student's attempt at the observed low accuracy. It is not the time needed to become a geolocation expert or to reproduce GPT-4o's accuracy.

| Activity | Seconds per image | Basis for the estimate |
|---|---:|---|
| Read instructions | 3 | About 30 seconds once, spread across the ten-image form. |
| Inspect the scene | 20 | Scan buildings, landscape, road and any visible text in one fixed view. |
| Choose from memory or guess | 15 | Select plausible country and city; most original participants reported unfamiliarity. |
| Enter answers and advance | 7 | One radio choice and two short names, without a written rationale. |

The total is 7.5 active minutes per ten-image questionnaire. **20–90 seconds per image** is a judgment range: a quick guess versus longer unsuccessful deliberation. These alternatives are not confidence limits, recorded durations or a speed–accuracy curve. No direct timing donor is used, so `human_time_evidence=assumed`, `human_time_method=estimated`, `human_time_statistic=point_estimate` and `human_attempts=not_applicable`. The 300 protocol judgments support performance only.

## Inference work and source-version limits

`Query.py` performs two model calls per pair:

1. `GPT4o` uses **gpt-4o-2024-05-13** on one image and `Prefix`. The prompt requests an affirmative preamble, analysis of eleven kinds of clues, four location labels and estimated latitude/longitude.
2. `GPT4oExtract` uses **gpt-4o-2024-08-06** on its extraction instructions plus the whole first response. It returns four location fields. Its output controls the validity test and retry loop, so this is a task helper and is included.

`UsingGPTtoEvaluate.py` compares answers with ground truth after generation. That external grader is excluded, as are Street View retrieval, local JSON processing and other non-neural work. The image downloader tries headings until one image succeeds; it does not supply all four headings to the model.

There are genuine gaps between paper and public executable. The paper displays a shorter prompt without the code's repeated specificity instruction, affirmative preamble or coordinate output. It permits five attempts for invalid output; `Query.py` stops after three pairs. The public main loop also does not implement the three independent response repetitions described in the paper. The estimate uses the retained executable's actual prompts and two-call structure, with the paper's five-pair ceiling for the reported experiment. The score-to-code configuration link is therefore source-informed, not native-log verified.

Both calls set `max_tokens=3000`; **3,000 is not used as a mean**. Primary output is assumed to average **400 text tokens**. This allows a roughly 200-word analysis across the eleven requested clues, the requested preamble, location fields and JSON punctuation. The paper's page-20 model examples vary from a short paragraph to a lengthy numbered analysis; they are useful checks on this order of magnitude, not GPT-4o output measurements. Alternatives use 200 and 800 tokens.

The helper output is **40 tokens**. A formatting check using the actual 100 ground-truth country/city/continent labels, an explicitly invented `Main Street` placeholder and a fenced, indented four-field JSON object averages **36.95 tokens** (35–40). Rounding to 40 allows somewhat longer street names. These objects are length proxies, not generated predictions or additional quality evidence. Alternatives use 35 and 80 tokens.

The literal primary and helper prompts tokenize to **378 and 131 tokens** with OpenAI's retained `o200k_base` vocabulary. An assumed 12 tokens per call covers message/special-token overhead. Per pair, the text workload is therefore:

`primary: 390 input + 400 output; helper: 543 input + 40 output = 1,373 text tokens`.

The central invalid probability is an assumed **5% per pair**, giving `1 + .05 + .05² + .05³ + .05⁴ = 1.05263125` expected pairs. A low value is reasonable because the prompt insists on a specific guess even when wrong, and the code tests city validity rather than geographic correctness. Its local check even accepts an absent city key as an empty string. Neither this reasoning nor the helper's general capabilities supplies an observed failure rate. Zero and 20% invalid-rate alternatives are retained. The three-pair code ceiling changes central compute by only about 0.013%.

Each HTTP function also has a 100-try transport-error loop. No dispatch or error records survive. The central estimate assumes no additional completed-but-lost responses outside the invalid-output loop; that is not an observed zero. Connection failures before processing do not justify full-response charges, and the 100-try cap does not establish any work actually spent. One additional fully processed pair would add the no-retry pair cost reported below. There is no arbitrary multiplication by the transport cap.

Inputs are counted fresh. The [original prompt-caching launch](https://openai.com/index/api-prompt-caching/) lists the August snapshot and a 1,024-token minimum reusable prefix. The central helper input is 543 tokens; the common part of its input is only 143 tokens. The May snapshot is not listed in that launch table. These facts make a large cache correction unsupported for the central recipe. Actual cache counters are absent; zero is not provider-observed. The repeated same-image primary prompts could matter if a different endpoint or undisclosed serving behavior were used.

## Image and model operation estimate

The public code requests `936×537`, but all four actual embedded street-view illustrations in the final PDF are **640×537**. The calculator reads those image objects directly. The central geometry transfers that observed size to the unreleased user-study images. It is not proof of every model input's resolution.

The [OpenAI image guide](https://developers.openai.com/api/docs/guides/images-vision) motivates **four 512-pixel high-resolution tiles plus one global view**, five views in total. `detail` is omitted in the code, so the actual auto-selected detail is not logged. A low-detail one-view alternative is retained. The current guide does not enlarge small images; a separate seven-view alternative represents historical enlargement of the code's requested 936×537 dimensions, not a claim that enlargement actually occurred. The corresponding 765 visual billing units are recorded only as a reference and are **not treated as physical positions**.

The architecture is undisclosed. The estimate uses the shared **50B active-parameter assumption** for each GPT-4o snapshot, giving `2N = 10¹¹ FLOPs` per text or assumed visual backbone position. This is the dataset's 200B total central prior times an assumed quarter activation, informed by [Epoch's original size discussion](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use). It is not a provider-reported parameter count, and differs from that article's pessimistic energy case of 400B total/100B active. The original [May release](https://openai.com/index/hello-gpt-4o/) and [August release](https://openai.com/index/introducing-structured-outputs-in-the-api/) establish dates and endpoint identity, not architecture.

For the visual frontend, the named proxy is the original [OpenCLIP ViT-bigG/14 configuration](https://github.com/mlfoundations/open_clip/blob/c62bf7d0eba36b38909be25528a7412fc20a35f7/src/open_clip/model_configs/ViT-bigG-14.json): 48 layers, width 1,664, MLP width 8,192, 14-pixel patches, 224-pixel crop. This is **not asserted to be GPT-4o's encoder**. Each of the five views is processed at this proxy's input size. Its 256 patch representations per view give an assumed **1,280 visual backbone positions** per pair. Actual compression, projection and token layout are not disclosed; alternatives use 64 and 576 positions per view.

At two FLOPs per multiply-add, with `n=257` including the class position, `d=1664`, `m=8192`, `L=48`:

`frontend/view = 2×256×(14²×3)×d + L×(8nd² + 4ndm + 4n²d)`

`= 967,491,772,416 FLOPs`.

This counts patch, attention and feedforward matrix arithmetic. Layer normalization, activations, elementwise operations, the unknown visual-to-language connector and backbone attention beyond the fixed 2N approximation are not separately counted. The fixed coefficient is a short-context approximation; the numerous unknown architecture terms do not support an exact physical-operation claim. The separate frontend contributes about 1.8% of the central total.

Per pair:

`F = 10¹¹ × (1,373 text + 1,280 visual positions) + 5 × 967,491,772,416`

`= 270,137,458,862,080 FLOPs`.

Including the assumed invalid retries gives **284,355,130,993,814.8 FLOPs** and **1,445.26270625 text tokens**. The CSV retains reproducible arithmetic, not that many digits of empirical precision. `operation_count` covers both backbones and the frontend; `derived_assumed_inputs` describes the assumed sizes, outputs, retries and image representation. The main workload is reconstructed from this task's own code and quantities, not borrowed as an unrelated task-average compute total.

## Sensitivity and reproduction

`calculations.json` contains each changed input and its recomputed total. Main single-input alternatives are roughly 0.85–1.30× for 200–800 primary output tokens, 0.95–1.19× for 0–20% invalid retries, 0.61× for low detail, 1.20× for seven views, 0.64–1.59× for 64–576 visual positions per view, and 0.51–1.98× for 25–100B active parameters. These are scenarios, not confidence bounds. Human 20–90-second alternatives are independent of those compute choices.

Dependencies: Python 3 with `tiktoken`, `openpyxl` and `pypdf`. The retained vocabulary is loaded into a new output-local cache; no network requests or model calls are made. Supply explicit source and new output paths:

```sh
python research/recompute.py sources /path/to/new-output-directory
```

The script verifies source hashes, model IDs, helper presence, image geometry and the human workbook cohort, then writes calculations, prompts, human item labels and clearly marked format proxies. `--assumptions FILE` can select an alternate assumptions file. It refuses an existing output path or one inside retained sources. The two model records are unchanged copies of the shared registry, including its existing parameter-source links.
