# Helix: transfer and orient one conveyor parcel

## robo-package-helix

Primary sources: Figure's [June 2025 logistics evaluation](https://www.figure.ai/news/scaling-helix-logistics), [initial logistics architecture](https://www.figure.ai/news/helix-logistics), and [original Helix architecture](https://www.figure.ai/news/helix). Work: take one small mixed-format parcel from the incoming conveyor, orient its barcode downward for scanning, and transfer it to the outgoing belt. Select the 60-hour model with stereo vision, memory, state history and force feedback: **4.31 seconds per package and 94.4% scan orientation success**. The 4.05-second result uses a larger decoder and lower reported accuracy; it is not mixed into this row.

## Compute estimate

The logistics studies describe a specialized System-1 visuomotor policy. The original S1 transformer has 80M parameters, with a separate fully convolutional multiscale backbone. Stereo features are fused before tokenization. The later study adds visual memory and force/state inputs without publishing layer sizes, image resolution, token count or the network query interval. Its 200 Hz refers to action samples within output chunks; it cannot be assumed to mean 200 complete image-encoder calls per second.

Use the following explicit component approximation, constrained by this architecture rather than unspecified GPU utilization:

- Stereo vision: two ResNet-18-scale backbones operating at 640×480. The independently counted standard ResNet-18 backbone is 22,206,873,600 FLOPs per image. Assume ten fresh stereo observations per second.
- Transformer: partition the reported 80M parameters into 40M encoder and 40M decoder parameters. Assume 256 fused visual/memory positions per observation. Encoder work is 2×40M×256×10 per second.
- Decoder: treat 10M parameters as source K/V projections evaluated for 256 positions at ten observations per second, and the remaining 30M as action-position work at 200 output positions per second. This is 2×10M×256×10 + 2×30M×200 per second. Each action position is a full upper-body action vector, not one token per joint.
- Add 20% of the subtotal for stereo fusion, visual memory and the learned calibration/visual-proprioception component described in the initial logistics report. These auxiliary architectures are undisclosed; this is an explicit helper-work allowance.

Total = 1.2×[2×22,206,873,600×10 + 2×40M×256×10 + 2×10M×256×10 + 2×30M×200] = **854,564,966,400 FLOPs/s**. Multiply by the reported 4.31 seconds = **3,683,175,005,184 FLOPs per package**. The recipe assumes S1-only specialized logistics inference, as described by the logistics studies; they do not report an active S2 language pipeline for this fixed task. The original 7B S2 is not silently treated as part of the 80M transformer.

This is necessarily a coarse architectural transfer. A 5–20 Hz observation cadence, 128–512 visual positions, smaller/larger convolutional backbones or an active S2 would materially change compute. A factor-of-four uncertainty around the central S1 recipe is appropriate; it is not a measured confidence interval. No exact checkpoint or profile is claimed. Training demonstrations and motor-control arithmetic are excluded. Unlike completion-only robot recipes, the reported steady-stream per-package duration covers the source's evaluated handling stream; no separate success-rate multiplier is applied.

## Human active work and quality

Estimate **4 seconds** for a practiced parcel handler working at the same prepared conveyor station: acquire and grip the next parcel (1 second), inspect/rotate to put the label down (1.5 seconds), transfer and release (1 second), plus an average 0.5 seconds for smoothing a flexible mailer or correcting orientation. The visible task includes boxes, bags and envelopes, so merely counting a reach-and-drop would omit the barcode-facing requirement. The source describes the system as approaching human speed and dexterity, but gives no independent direct human timing. A 3–6-second range is reasonable for ordinary small parcels at this station.

Classify match for this practical manipulation target: the model is in the same few-second range and successfully presents the label on about 94% of packages. The human estimate targets comparable routine parcel handling with occasional corrections, not perfect industrial throughput. This is a substantive approximate comparison, not a measured human trial result. Human hands and humanoid grippers differ.

## Model release provenance

The original and logistics publications describe proprietary deployed systems rather than publicly released evaluated weights. Leave exact model release date blank; June 2025 is the study date, not an established weight-release date.

## Reproduction

`python3 build_tranche3.py` uses standard-library integer arithmetic to enumerate all convolutions of the assumed ResNet-18 backbone, excluding its classification head. It writes component totals to `research/tranche3-operations.json`. Decimal multiplication preserves the exact reported 4.31-second multiplier. The architecture is a proxy, not a disclosed Figure backbone.
