# CheXNet pneumonia classification

## perc-cxr-chexnet

Use the [original November 2017 version](https://arxiv.org/html/1711.05225v1), Sections 2–3 and Figure 2. It specifies one 224×224 input and DenseNet-121 with a binary pneumonia head. Four practicing radiologists assessed 420 frontal radiographs without patient information; they entered labels for all 14 conditions. The AI pneumonia ROC curve exceeds their average sensitivity/specificity point. Classify above for this study comparison. No F1 figure from a later revision is substituted, and this does not assert the same outcome for the other 13 labels.

The point's human work is to inspect the displayed frontal radiograph and record a pneumonia judgment. The timing is an estimate for that binary task, not the duration of the original 14-label annotation exercise.

## Human duration

[Ahn et al. 2022](https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2795798), Methods and Interpretation Times Results, recorded unaided interpretation of 497 frontal chest radiographs. Six readers comprised two attending thoracic radiologists, two fellows and two residents. Readers entered four findings, laterality or lung zones, confidence scores and other-finding comments; timing ran from image loading to form submission. The full-data unaided median is **42.0 seconds** (IQR 28.2–60.2). The headline 40.8-second median excludes 81 reads longer than three minutes. Use the full-data figure as the timing anchor.

Use **40 active seconds** as a transferred estimate for an experienced reader's pneumonia judgment. The target omits the multi-finding form but retains careful anatomical inspection and review; dividing by four would underestimate the shared inspection. A component check is five seconds for image orientation/quality, twenty for lung inspection, ten for ambiguous findings and final review, and five to enter the judgment. These components are assumptions. A 20–60-second sensitivity covers rapid confident reads and borderline cases. The method is `estimated`, evidence `transferred_timings` and statistic `point_estimate`; it is not a measured pneumonia median. The donor is 2,982 unaided reads (six readers × 497 images), including the long readings in the full-data median. Use human_attempts=2982 and subset all; the ten familiarization images per reader are outside the analyzed sample.

## FLOPs

The [original DenseNet architecture table and implementation description](https://arxiv.org/html/1608.06993v5) specify growth 32, bottleneck width 128, blocks of 6/12/24/16 layers, and half-width transitions. The stem maps RGB 224×224 to 64 channels at 112×112, followed by pooling. Dense-block widths are 56/28/14/7. Convolution operations are 2×input channels×output channels×kernel area×output area; concatenation copies data and is not arithmetic.

The reproducible calculation in `agent-work/sources/chexnet/operations.py` and `agent-work/sources/chexnet/operations.json` gives **5,698,465,281 FLOPs**. It includes all convolutions, inference batch-normalization affine operations, average pooling, the binary head and a small class-activation-map projection. ReLU and max-pool comparisons are not floating arithmetic. The scalar sigmoid and image resampling are negligible at this precision. No GPU-capacity multiplier, training work, crop ensemble or later implementation is used.

The architecture inputs are supported, although this remains a calculation rather than a profiler measurement. The apparent precision comes from arithmetic, not an assertion that every scalar instruction was counted. The exact public availability of this trained checkpoint is not established; leave the release date blank.

The donor-count audit additionally retained original ACT/Ahn/Bindemann evidence in agent-work/sources/timing-donor-audit/.
