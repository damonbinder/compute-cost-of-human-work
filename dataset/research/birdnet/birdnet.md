# BirdNET v2.4: one minute of field soundscape annotation

## perc-birdsong-birdnet

The point represents one average minute from the **4224 one-minute recordings** in Funosas et al., *A global assessment of BirdNET performance: Differences among continents, biomes, and species*, Ecological Indicators 182 (2026), 114550, https://doi.org/10.1016/j.ecolind.2025.114550. Original author-hosted PDF: https://cobra2.ic.ufmt.br/wp-content/uploads/2026/01/2026-1-perez_schuchmann_marques_global_assessment_birdnet_2026_compressed.pdf (`agent-work/sources/birdnet/global-birdnet.pdf`). Sections 2.1–2.4 and Table 1 establish the work and performance. The unit is detecting bird species and occurrence intervals, not identifying a pre-isolated song, and not a species list aggregated across a whole site.

## Configuration and performance

The software version is **BirdNET-Analyzer v2.2.0**, but the model is explicitly **BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite**. These version numbers identify different components. Settings are overlap 2 seconds, sensitivity 1, occurrence frequency cutoff 0.02 and confidence cutoff 0.1. Overlapping detections count as matching an expert annotation when their time intervals intersect. At the vocalization level, continent means span precision 0.57–0.71 and recall 0.24–0.52. These are ranges of site-aggregated continental results, not a constructed global micro-average or per-minute measurement. Classification is below the local-expert reference, without treating the annotators as infallible.

The original lead's 2021 BirdNET paper predates this model and is not used as v2.4 performance evidence. A separate European-city study (https://doi.org/10.1371/journal.pone.0330836) discusses v2.4 but its methods use model v2.2; it is also not used for v2.4 scores.

## Human work

Section 2.2 describes local expert ornithologists using Raven Pro spectrograms and unrestricted replay. **One observer annotated each site.** This is not a pooled-vote baseline. They labeled species and temporal/frequency bounding boxes, grouping calls from the same species if within one second. The point uses the species/time component; no extra labor is assigned to producing frequency measurements absent from BirdNET output.

Table 1 gives 6455 + 8410 + 27582 + 29781 + 8748 + 8085 = **89061 vocalization annotations**, or **21.084517** per minute. This supports an explicit estimate:

* 60 seconds for an initial listening pass with the spectrogram;
* 60 seconds for a checking/replay pass, allowing overlapping calls, missed events and distinguishing similar species;
* 3 seconds per average vocalization to select its interval, enter or reuse its species label, and advance.

Total = 120 + 3 × 89061/4224 = **183.253551 seconds per minute**. The recording duration and annotation count are reported; the two passes and 3-second annotation action are assumptions. Three seconds assumes an experienced local annotator with a familiar species list, keyboard shortcuts or reusable labels, rather than typing each scientific name from scratch. A checking pass is appropriate to the source's overlapping wildlife soundscape task; it is not a measured replay rate. This estimate seeks the expert reference quality, not deliberately reproducing BirdNET's missed detections. Consequently AI performance remains below, not match by construction. A fast one-pass workflow plus two seconds per label gives 102.17 seconds; three passes plus six seconds per label gives 306.51 seconds. Sparse clips can be faster and dense unfamiliar mixtures much slower. These scenarios are judgments about this inspected annotation protocol, not sourced timing samples. The human_time_method is estimated because playback and annotation components are combined with judgment.

Experts have local familiarity and spectrogram/replay tools; the AI has an eBird-derived location/week prior. This material input/tool difference is flagged. The annotator-count and vocalization-count evidence does not establish a human timing sample size.

## Model and operation reconstruction

The public model release archive is https://zenodo.org/records/15050749 (metadata retained as `agent-work/sources/birdnet/model-record.json`). Its ordinary FP32 archive contains `audio-model.tflite` and `meta-model.tflite`; their SHA256 hashes are retained in `agent-work/sources/birdnet/model-sha256.txt`. This archive names the model v2.4 and supplies the global classification and occurrence networks. The primary audio model was publicly released on **2023-06-01** in [the v2.4 model commit](https://github.com/birdnet-team/BirdNET-Analyzer/commit/b32cdc54c9f2344b028e6378e9eae66e39110d27). Its 51,726,412-byte FP32 file has Git blob `e550dba1dba4488af4c606ac639d9a5c4e3f74cf`, exactly matching the retained audio model. The date identifies that primary model. The compute recipe uses the location network in the later Zenodo bundle; it does not claim that this companion network was unchanged since June 2023. Original repository history includes a January 2024 species-range update. Tree and history responses are retained under `agent-work/sources/birdnet/release-history/`.

`research/birdnet-count.py` parses these public model graphs and resolves dynamic dimensions with a dummy 144000-sample FP32 input. No audio predictions from that dummy input are used as evidence. Retained `research/birdnet-calculations.json` lists all operations, resolved shapes and arithmetic. The exported flatbuffer's pre-invocation temporal dimensions are placeholders, often 1; using them directly would badly undercount the model.

The waveform has two spectrogram branches, each 511 frames, with FFT lengths 2048 and 1024 and dense projections to 96 bins. They feed a 96×511×2 image. These are both part of one model invocation, not an ensemble. The convolutional trunk yields a 1024-dimensional embedding and a 6522-way classifier. The separate occurrence model consumes latitude, longitude and week. It has four dense layers and is charged once per one-minute query; repeated calls with shared metadata could cache this 14.77-million-FLOP contribution without materially changing the total.

Count multiply-adds as two operations, including neural arithmetic irrespective of execution precision. Conv2D costs 2×output elements×kernel height×kernel width×input channels; depthwise omits the input-channel multiplier. Fully connected layers, including the mel projections, use 2×output elements×input width. Bias additions are represented by the 2n dot-product convention. Means, elementwise arithmetic and average pooling are counted explicitly. Sigmoid uses four scalar operations (negation, exponential, add, divide); pow and sin each use one scalar-operation convention. ReLU/max comparisons, shape/index calculations, memory copies and padding are not converted into FLOPs. No separate batch-normalization term is added where weights already fold it into convolutions.

Real FFTs use the common analytic leading term 2.5 N log2(N) per transform, an assumed operation recipe rather than a measured kernel count. The count includes the graph's casts as data conversion, with no extra invented magnitude operation. This convention and elementwise transcendental implementation uncertainty make compute_evidence derived_assumed_inputs. FFT cost is 41.86 million of the 873.00 million total; doubling the FFT allowance increases the minute total by about 4.8%. Dense mel projection counts actual graph multiplications, including zero weights; sparsity-specialized implementations could reduce them but are not the documented ordinary graph execution.

| Component group per audio call | FLOPs |
|---|---:|
| Conv2D | 619201152 |
| Depthwise Conv2D | 24053760 |
| Fully connected, including both mel projections | 164253312 |
| Both real FFT branches | 41861120 |
| Remaining scalar arithmetic/pooling | 23632972 |
| Audio model total | **873002316** |
| Metadata model total | **14768082** |

Original study-version windowing is retained as `agent-work/sources/birdnet/analyzer-audio.py`, from https://raw.githubusercontent.com/birdnet-team/BirdNET-Analyzer/v2.2.0/birdnet_analyzer/audio.py. `split_signal` computes the final chunk start as ceil((samples−chunk size)/stride)×stride; for a 60-second file and 3-second window with 2-second overlap this yields starts 0 through 57 inclusive: **58 calls**. There is no extra padded 58/59-second window in this exact-length case. Final minute compute is **58 × 873002316 + 14768082 = 50648902410 FLOPs**. Audio decoding, resampling and integer threshold/export operations are outside this neural-workload count; there is no uncounted neural helper. No text-token coefficient applies.

Recompute retained graph counts from the dataset directory with `python research/birdnet/birdnet-count.py agent-work/sources/birdnet --output /tmp/birdnet-counts.json` (requires TensorFlow, NumPy and tflite). The JSON is an audit artifact; running the script does not update CSVs.
