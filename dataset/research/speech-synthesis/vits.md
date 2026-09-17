# VITS: five short narrated excerpts

The work unit is one synthesis of each of the five texts in the original [single-speaker demo](https://jaywalnut310.github.io/vits-demo/index.html#ss). The output is natural-sounding narration, not voice identity matching. No new speech was generated. Retained WAV headers establish output lengths; the original code, configuration and cleaned test strings establish input dimensions.

## Model identity

Use original VITS with its stochastic duration predictor, LJ Speech single-speaker configuration. Code is pinned to `2e561ba58618d021b5b8323d3765880f7e0ecfdb`. It is not the deterministic-duration ablation, the multi-speaker model or voice-conversion path. The first [README commit](https://github.com/jaywalnut310/vits/blob/2b91ceff252082644bd507d13476a49ea260cadf/README.md) on June 10, 2021 links pretrained models; the following same-day README moves that link nearer the top and changes its Drive folder. The retained commit history and README bytes support June 10 availability, instead of imputing June 11 from the paper's submission date. The model files themselves were not needed to count inference operations. The retained initial-to-pinned commit comparison changes only README and figures; configuration, cleaned strings, symbols and model code are unchanged from the June 10 release.

The [original paper](https://arxiv.org/abs/2106.06103) identifies the authors' Kakao Enterprise affiliation. The model registry has no common token coefficient: text positions, latent acoustic frames and waveform samples drive different layers.

## Exact work quantities

| Demo | Original test ID | Cleaned symbols | Text positions including blanks | Latent frames | Output samples | Seconds |
|---|---|---:|---:|---:|---:|---:|
| 1 | LJ003-0011 | 167 | 335 | 853 | 218368 | 9.9033 |
| 2 | LJ016-0117 | 131 | 263 | 674 | 172544 | 7.8251 |
| 3 | LJ001-0096 | 169 | 339 | 797 | 204032 | 9.2532 |
| 4 | LJ031-0189 | 156 | 313 | 844 | 216064 | 9.7988 |
| 5 | LJ002-0171 | 97 | 195 | 484 | 123904 | 5.6192 |
| Total | | 720 | 1445 | 3652 | 934912 | 42.3996 |

The texts concern historical liquor allowances, a prison escape through wooden panels, printing type, Lyndon Johnson's oath of office and a boy passing a toll. They are short prose excerpts with ordinary narration requirements; the date/time and names merit a brief preview.

Each demo text matches the original `ljs_audio_text_test_filelist.txt` and its `.cleaned` counterpart by LJ ID. The latter supplies phonetic symbols, including punctuation, stress and spacing; 720 is a symbol count, not a claim of 720 linguistic phonemes. Source `cleaned_text_to_sequence` maps every symbol and `add_blank` inserts one blank before/between/after, yielding `2 × symbols + 1` per excerpt. The CSV's 1,445 tokens are these encoder input positions only.

Read the original WAV `fmt` and `data` headers: mono PCM16, 22,050 Hz. No duration is inferred from words-per-minute or synthesis latency. All sample counts divide exactly by the configuration's 256-fold waveform upsampling, giving the latent frame counts above. Headers were obtained with 4,096-byte range requests; the files are intentionally `.wav.header`, not complete playable audio. These lengths define the synthesis recipe; they do not reconstruct how many candidates the authors might have generated when selecting a demo.

## Inference arithmetic

Reproduce with `python recompute_vits.py --sources SOURCE_DIR --output NEW_JSON`. Standard-library Python only; the program neither imports downloaded executable code nor needs trained weights. It refuses output overwrite. `vits-audit.json` records each excerpt, component and waveform-decoder stage.

Count a multiply and addition as two FLOPs. The operation estimate covers all inference networks' dense/convolution arithmetic and the explicit alignment matrix multiplications. Lookup, data movement, padding allocation, scalar nonlinearities, normalization and random-number generation are not individually tallied. These are small beside the waveform convolution total; this is an architecture operation estimate, not a hardware profiler count. Weight normalization is treated as folded into its effective convolution weights.

For text length N and latent frame length T:

- **Text encoder:** six layers of width 192, two attention heads and convolutional feed-forward width 768 with kernel 3. Count four attention projections, both feed-forward convolutions and dense attention products. Original relative attention pads its relative embedding to length `2N−1`: include both additional relative matrix products, not merely the nine learned relative embeddings. Add the 192→384 mean/log-scale projection. Embedding lookup is not a dense vocabulary multiplication.
- **Stochastic duration:** initial 192→192 pre/projection layers plus one three-layer depthwise-separable block. Reverse inference executes **three**, not four, ConvFlow blocks: the code removes the useless final flow in the reversed list. Each remaining block has a 1→192 pre-convolution, three depthwise kernel-3/pointwise convolutions, and a 192→29 projection for the ten-bin rational quadratic spline. No posterior duration flow runs during inference.
- **Alignment:** source `infer` explicitly performs two `[T,N] × [N,192]` products for mean and log-scale expansion, totaling `4TN192`. Do not assume a sparse gather that the source does not implement.
- **Prior flow:** four mean-only coupling layers. Each splits 192 channels into 96/96, projects 96→192, runs four WaveNet layers with kernel 5 and gated 192→384 convolutions, then projects 192→96. The first three residual/skip projections are 192→384 and the fourth is 192→192. This path runs at T, not at waveform sample count.
- **Waveform decoder:** 192→512 kernel-7 pre-convolution, then upsampling strides 8,8,2,2 with kernels 16,16,4,4 and channels 256,128,64,32. A transposed convolution costs `2 × input_length × input_channels × output_channels × kernel`; using output length here would overcount by the stride. Each stage also has three residual blocks with kernels 3,7,11; each block has six ordinary convolutions, three dilated and three undilated, evaluated at that stage's output length. Finish with a 32→1 kernel-7 convolution.

The training posterior encoder, adversarial discriminator and monotonic-alignment search do not run in `infer`, and are excluded. There is no speaker embedding in this single-speaker configuration.

| Component | FLOPs for all five excerpts |
|---|---:|
| Text encoder | 24,080,864,256 |
| Stochastic duration network | 1,561,432,320 |
| Alignment products | 838,465,536 |
| Prior flow | 51,696,893,952 |
| Waveform decoder | 2,245,643,665,408 |
| Total | **2,323,821,321,472** |

The waveform decoder contributes 96.64%. Encoder/decoder registry counts are calculated from these source shapes, including biases and text embedding, with folded weight-normalization parameters: 6,326,784 for the text encoder and 14,327,424 for the waveform generator. These are not the total VITS training parameter count. Duration and prior networks are separately counted above. Parameters are labeled reported under COLUMNS.md because they are calculated from published architecture without assumed dimensions. The folded-weight component scope remains explicit; `compute_evidence=derived_supported_inputs` reflects the source-supported dimensions and work quantities.

## Human recording time

Estimate **180 active seconds** for a practiced narrator recording all five excerpts in an already available quiet recording setup. Match naturalness and correct prose delivery; do not require the narrator to mimic the LJ Speech speaker or exactly reproduce the waveform's prosody.

[ACX's producer guidance](https://help.acx.com/s/article/manage-your-offers) gives roughly two hours of reading/recording and two hours of editing per finished audiobook hour. This is professional guidance, not a recorded timing sample. Use its two-times-output recording allowance as a starting estimate for preview, pauses and occasional retakes. For these short excerpts, add one real-time playback to check them and 60 seconds total for script preview, starting/stopping, light trimming and saving the five clips. Arithmetic: `2 × 42.3996 + 42.3996 + 60 = 187.2 seconds`, rounded to three minutes. This is a judgment-based short-clip estimate (`assumed`, `estimated`), not a unit conversion of measured audiobook timings.

There is no whole-book mastering, chapter packaging, rights-holder review or setup of a recording studio. A fluent first take with minimal checking could take about two minutes; awkward takes or additional repairs could take five. That 2–5-minute scenario is more informative than claiming a measured completion-time mean. Retakes, when needed, belong in human active effort; the AI side represents one ordinary forward synthesis of each excerpt at the observed lengths.

## Quality comparison

Original paper Table 1 reports LJ Speech naturalness MOS **4.43 ± 0.06** for VITS and **4.46 ± 0.06** for ground-truth recordings. These are broadly comparable. The human-time estimate explicitly targets similarly natural, intelligible delivery, so the row is match. This is neither a claim of identical voices nor a voice-identity evaluation.

The MOS test used evaluated LJ Speech utterances, not a separately reported test on these five published demonstrations. The point flags that concrete assessment transfer. No five-clip MOS or human recording sample count is invented. `compute_subset` and attempts are not applicable because this is an operation recipe at source-established lengths; `compute_statistic=total` represents the five-clip bundle.
