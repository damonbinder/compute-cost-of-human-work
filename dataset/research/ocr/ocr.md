# Tesseract on a clear printed test image

## perc-ocr-tesseract

The work unit is one complete transcription of the original 640 × 480 `phototest.tif`: 60 words, 286 raw characters, or 284 characters after collapsing whitespace. Text content and punctuation must match; page layout and line wrapping are not part of the human target. The source is a small, clear test image, not a representative full document page or an OCR benchmark average.

The [original image](https://github.com/tesseract-ocr/test/blob/232ff181c66516116ec0e84c4963f70de15050fd/testing/phototest.tif) and [gold transcription](https://github.com/tesseract-ocr/test/blob/232ff181c66516116ec0e84c4963f70de15050fd/testing/phototest.gold.txt) are retained. Their git object hashes match the source repository tree. The local inference run uses the original English float `tessdata_best` weights, Tesseract 5.5.1, `--oem 1`, `--psm 3` and no orientation-detection model. Its output equals the raw gold byte-for-byte, including whitespace.

### Neural operations

We instrumented the original [Tesseract 5.5.1 source](https://github.com/tesseract-ocr/tesseract/tree/5.5.1), retained as a source archive. The counter measures actual executed logical neural arithmetic, including any network passes made by recognition; it does not estimate GPU utilization, multiply latency by hardware throughput, or infer cost from the number of output characters.

| Component | Counted operations |
|---|---:|
| Weight dot products: 2,131,653,952 multiply-adds × 2 | 4,263,307,904 |
| Bias additions | 9,701,993 |
| Tanh/logistic lookup interpolation and sign arithmetic | 72,118,822 |
| Recurrent elementwise state/output arithmetic | 7,389,440 |
| Softmax subtraction, accumulation and division | 417,915 |
| Softmax exponential evaluations, counted once each | 139,305 |
| Total | 4,353,075,379 |

`weightmatrix.cpp` covers the LSTM gate matrices and fully connected layers. Convolution in this engine is implemented by rearranging neighborhoods in `convolve.cpp` followed by a fully connected layer; its weight arithmetic is therefore already counted. It is not a missing separate convolution. Both directions and all actually executed recurrent timesteps pass through the counter.

The extended counter records 1,847,360 hidden-state positions, giving exactly four elementwise operations per position. There are no true 2D-LSTM timesteps in this run. Fully connected activations include 2,173,248 tanh positions and 139,305 softmax positions; four gate biases per hidden position plus these fully connected outputs reproduce all 9,701,993 bias additions. Tanh and logistic functions use lookup-table interpolation, with arithmetic counted along the actual branches. Recursive negative-argument calls appear in diagnostic invocation counts; their arithmetic is counted once per executed instruction in the source.

Comparisons, indexing, memory copies, integer bookkeeping, classical image/page analysis and beam decoding are outside this neural arithmetic count. An exponential is counted as one nonlinear operation, not as an asserted number of machine instructions. Even assigning 100 operations per exponential would give 4,366,866,574 operations, only 0.32% above the central convention. No arbitrary overhead factor is added. The extra neural arithmetic raises the earlier matrix-and-bias subtotal by 1.87%.

Builds disable OpenMP so the simple counters cannot race. The extended instrumentation leaves the original dot-product and bias counts unchanged, and output stays identical to the unextended instrumented run. `complete-audit.log` contains the counters; `calculate.py` checks arithmetic, source hashes, and transcript equality.

### Human estimate

The image is legible and contains the same 45-character sentence four times. A normal text editor allows the human to type the introduction and that sentence once, then copy and paste the three repeats. This leaves 146 characters of fresh text entry.

[Dhakal et al.](https://userinterfaces.aalto.fi/136Mkeystrokes/) report 51.56 standard five-character words per minute. Applying that rate gives 33.98 seconds of fresh entry. Add 15 seconds for initial reading, 10 seconds for selecting/pasting the repeats and 20 seconds for final comparison and correction: 78.98 seconds, rounded to **80 seconds**. These additions are estimates for this inspected source, not measured human work on the image. A [reading-rate meta-analysis](https://biblio.ugent.be/publication/8647789) reports 238 words/minute for adult English nonfiction; 60 words at that rate takes 15.13 seconds. It calibrates initial reading, not proofreading.

The typing study starts timing at the first keypress after participants have read the sentence. Its WPM already includes corrections during typing, so no additional keystrokes-per-character multiplier is applied. The original uncorrected error rate, 1.167%, is not a post-proofreading accuracy measurement. Our human target is checked text at quality comparable to the inspected AI output; `match` describes that estimated target, not a measured human-AI trial.

Typing everything afresh at the same rate, then reading/checking, gives about 101 seconds. Inverting a mean rate does not establish the mean of completion times. A second-order speed-dispersion sensitivity increases the copying workflow to 84.2 seconds and the fresh-typing workflow to 111.2 seconds; neither is a recovered empirical mean. Thus the human statistic is a point estimate and its evidence is transferred timings.

The 60–170-second sensitivity spans faster copying and slower fresh typing, using the source's approximate 78/26 WPM upper/lower decile speeds plus stated checking allowances. It is a workflow/population sensitivity, not a confidence interval. The source participants were self-selected and mainly young people interested in typing. The typing donor contains 2,534,400 sentence trials (168,960 included participants × 15), after the source's participant-level quality and technical exclusions. The initial-reading component also uses a reading-rate meta-analysis whose passage-attempt count is not established here. Human_attempts is blank for the combined donors, rather than presenting the known typing count as the complete sample; subset all describes the included timing cohorts. [Detailed human arithmetic](human-review.md) and `human-review-calculations.json` retain the derivation.

## tesseract-eng-best-2017-09-14

The model record identifies the original English `tessdata_best` weights, not the release date of the later engine executable. The [initial public import](https://github.com/tesseract-ocr/tessdata_best/commit/9ddc24e750eec0994223a9edc3fcb434a2244f3b) is dated September 14, 2017, and credits Ray Smith; the retained file history is `eng-commit.json`. The retained weights' git object hash matches `eng.traineddata` in the original import tree, verified using `eng-original-tree.json`. These English weights are credited to Google. The loaded network reports **1,461,007 stored weights**, including biases. Their total alone does not determine inference compute because different layers process different image/recurrent positions. Shared text-token and separate encoder/decoder parameter fields are not applicable to this directly instrumented network recipe.

## Reproduction

From the published dataset root:

```sh
sh research/ocr/reproduce.sh agent-work/sources/ocr /tmp/ocr-new-reproduction
```

The output directory must not exist. Required tools are Python 3, CMake, a C++ compiler, pkg-config and Leptonica development libraries. The script unpacks the retained original source into the new directory, applies `instrument.py`, builds without OpenMP, runs recognition and writes the arithmetic and human-estimate checks. `instrumentation.patch` is a readable diff of the same changes. No download or production write is required. A fresh-source rebuild reproduced the counter log, transcript, TSV and both calculation outputs byte-for-byte.

To recompute from retained counters without compiling:

```sh
python3 research/ocr/calculate.py agent-work/sources/ocr agent-work/derived/ocr/complete-audit.log agent-work/derived/ocr/complete-audit.txt /tmp/ocr-new-calculations.json
python3 research/ocr/review_human.py agent-work/sources/ocr /tmp/ocr-new-human-calculations.json
```
