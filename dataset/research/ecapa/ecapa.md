# ECAPA-TDNN: unfamiliar-speaker verification

## perc-speakerid-ecapa

The work unit is one same/different decision for two previously unseen, complete speech recordings. It represents an ordinary-length pair in the **VoxCeleb1-H** condition (same gender and nationality), with **8.2 seconds per utterance** as a corpus-average duration proxy. Both recordings are processed afresh. The primary model is the original single **C=1024 ECAPA-TDNN**, not an ensemble or a later SpeechBrain checkpoint. The task excludes training the model, enrolling a known person's voice over multiple recordings and prior human familiarization with the speakers.

## Original evidence

* Desplanques, Thienpondt and Demuynck (2020), https://arxiv.org/abs/2005.07143 (`agent-work/sources/ecapa/ecapa.pdf`). Figures 1–2, visually inspected on PDF page 3, specify the network; Sections 3.1–3.3 and 4.1 specify attention and dimensions. Table 1 reports **14.7M parameters** and **2.12% EER on VoxCeleb1-H** for C=1024. Its original VoxCeleb1 result is 0.87% and extended result 1.12%; these are alternative assessments, not scores averaged or fused into this point. Sections 4.2–4.3 give cosine scoring and adaptive s-norm, cohort size 1000 for VoxCeleb, and speaker-averaged training embeddings as cohort references.
* Nagrani, Chung and Zisserman (2017), https://arxiv.org/abs/1706.08612 (`agent-work/sources/ecapa/voxceleb.pdf`), Table 1 gives mean utterance duration **8.2 seconds**, minimum 4 and maximum 145. This is a full-corpus statistic, not the exact trial-weighted mean of the later hard pair list. Consequently compute_evidence is **transferred_workload**. The representative two-utterance unit is explicit; it is not a claim to have extracted and averaged every verification trial's runtime.
* Chung, Nagrani and Zisserman (2018), https://arxiv.org/abs/1806.05622 (`agent-work/sources/ecapa/voxceleb2.pdf`), Section 5 defines VoxCeleb1-H: 552536 pairs from the same nationality and gender. Its Section 4.4 distinguishes one whole-utterance pass from test-time crop augmentation for its own networks. These augmentation experiments are not silently imported into ECAPA.
* Sunilkumar et al. (2023), *Sounds and speech: Individual differences in unfamiliar voice recognition*, https://doi.org/10.1002/acp.4053. Original author-deposited PDF at https://strathprints.strath.ac.uk/84190/7/Sunilkumar_etal_ACP_2023_Sounds_and_speech_individual_differences_in_unfamiliar_voice_recognition.pdf (`agent-work/sources/ecapa/human-voices.pdf`). Experiment 1, Sections 3.3.2 and 3.4 and Table 1 describe the human comparison below.
* Huh et al. (2024), VoxSRC retrospective, https://arxiv.org/abs/2408.14886 (`agent-work/sources/ecapa/voxsrc-retrospective.pdf`), Section VIII.A discusses recent speaker verification surpassing unfamiliar human voice recognition. That statement concerns the most recent systems and does not establish an advantage for this 2020 ECAPA configuration.

## Human duration and performance transfer

Estimate **18.4 seconds**: one complete playback of each 8.2-second clip, followed by **2 seconds** to compare the remembered voices and enter the binary decision. Both clips are heard sequentially; parallel audio playback is not a usable substitute. This is a judgment-based estimate, not a reported mean. Much of the comparison can occur while hearing the second clip; the two-second tail allows a final identity decision and response without assigning another full clip duration to thinking. It assumes headphones, normal hearing, comprehension of the speech and voices unfamiliar to the listener. A one-second decision tail gives 17.4 seconds; replaying one whole clip before the two-second decision gives 26.6 seconds. More replays are possible on hard trials. The active-duration estimate is assumed, method estimated, with no fabricated recorded-attempt count.

The related AVMaT experiment contains 80 sentence pairs (40 same, 40 different), with same-gender mismatches, standard Southern British English speakers, and clips lasting **2–4 seconds each**. Table 1 reports **73% hits and 41% false alarms** for N=119, implying approximately **66% accuracy** on the balanced trials: (73 + 100 − 41) / 2. The 73% value is not overall accuracy. An initial **N=4 clean-clip pilot was at or near ceiling**, so the main study introduced acoustic environments/device distortions and effects to make the test challenging. Accuracy was emphasized over speed and replay was allowed. Its one-hour whole-study duration also includes other voice and face tasks and cannot establish time per voice pair.

Use **match** as the best estimate for ordinary judgments from complete utterances. The clean pilot is more relevant than the heavily distorted main experiment to speech without deliberately added effects; the longer 8.2-second inputs also provide more voice information. VoxCeleb still contains natural background/channel variation, and VoxCeleb1-H restricts gender/nationality cues. The four-person pilot does not measure human performance on that harder collection. Broad comparability is therefore an estimated transfer, not a claim of equal error rates; particularly noisy or difficult pairs could favor ECAPA. The 2024 retrospective cannot settle this comparison for the original 2020 system. EER is a threshold-operating-point metric, not an observed 97.88% fraction correct. `different_assessment; different_inputs_or_tools` records the assessment and audio-condition differences. The 18.4-second estimate remains ordinary listening and response time, not a duration constructed to force parity with the model.

## Inference workload

The original paper's **two-second random MFCC crops are training inputs**. Its inference section describes extracting an embedding and cosine scoring, and the network permits arbitrary temporal length through global pooling. The central reconstruction uses **one complete-utterance pass per side**, consistent with that protocol and common utterance-level scoring. The paper does not expose original inference logs or explicitly enumerate test-time crop calls; one full pass is a scoped reconstruction, not a measured trace. No evidence in this paper establishes a ten-crop ensemble, and such a factor is not borrowed from other architectures' augmentation experiments. If a later source establishes additional original-model passes, compute must be revised accordingly.

At 10 ms frame shift, the 8.2-second proxy gives **820 frames** per utterance. Endpoint padding conventions can give 818 rather than 820 frames for 25 ms windows; this changes the dominant count by about 0.24%. There is no VAD, and the final 192-dimensional embedding replaces the training-only AAM-softmax classifier. Query embeddings are normalized, scored against each other and compared to a bank of **5994 speaker means** for adaptive s-norm, retaining the top 1000 scores for each side. The cohort is a fixed, precomputed reference bank just as the classifier weights are fixed; its original construction is outside a single new verification query. All query-to-bank products and resulting mean/variance arithmetic are included. There is no model ensemble, ASR transcript or text-token workload.

## Operation calculation

Run `python3 research/ecapa-calculate.py`; output is retained as `research/ecapa-calculations.json`. Conv1D and linear multiply-adds count as two scalar operations. Crucially, SE layers and final embeddings execute once per utterance rather than once per frame. The temporal attention projections execute at every frame.

For C=1024, attention/SE bottleneck R=128, scale s=8 and MFA width D=1536, per-frame weight counts are:

| Component | Per-frame weights |
|---|---:|
| Initial width-5 convolution, 80 inputs | 409600 |
| Three SE-Res2 blocks: 3×(2C² + 7×(C/8)²×3) | 7323648 |
| MFA: 3C→1536 | 4718592 |
| Context attention: 3D→128→D | 786432 |
| Total | 13238272 |

The Res2 branch has seven width-3 convolutions for eight channel splits, with one split bypassing convolution. Three separate SE gates each add 2×C×128 weights; the 3072→192 final layer adds 589824. Their sum is **14614528 weights** before biases and normalization, consistent with the paper's rounded 14.7M. This independent agreement checks the architecture without using 2×14.7M at every audio frame, which would incorrectly repeat utterance-only layers.

The calculation also includes SE averages/gates, residual sums, Res2 branch sums, inference batch-normalization affine operations, context and attentive mean/variance pooling, softmax and embedding normalization. A 20D-per-frame scalar allowance covers context moments, attention softmax and weighted statistics; small endpoint terms are retained separately. This is an analytic implementation allowance, not a measured kernel count. ReLU comparisons and integer top-k sorting are not called floating-point operations.

For MFCC preprocessing the source establishes 80 coefficients, a 25 ms window, a 10 ms hop and cepstral mean subtraction. We assume 16 kHz PCM, a 512-point real FFT (2.5N log2N leading term), 80 dense triangular-filter outputs and an 80×80 DCT, plus windowing, power, logs and normalization. This intentionally explicit conventional front end costs **110057120 FLOPs per pair**, only 0.25% of total; using mel features without the DCT or sparse filters would reduce that small component. Most arithmetic is directly constrained by the published neural graph.

| Pair computation | FLOPs |
|---|---:|
| Initial convolution | 1343488000 |
| Three Res2 blocks | 24021565440 |
| MFA | 15476981760 |
| Context attention projections | 2579496960 |
| SE/embedding linears and scalar neural work | 112214272 |
| MFCC front ends | 110057120 |
| Query cohort cosine/statistics | 4615796 |
| Total | **43648419348** |

The operation total scales nearly linearly with combined clip duration; replacing two 8.2-second clips with two four-second clips roughly halves it and with two 12-second clips increases it by about 46%. These are duration scenarios, not substitute scores for the original test. Runtime, hardware utilization and peak throughput are not used. A first-public original checkpoint date was not established; the paper's May 2020 publication alone does not establish public availability, so release date is blank.
