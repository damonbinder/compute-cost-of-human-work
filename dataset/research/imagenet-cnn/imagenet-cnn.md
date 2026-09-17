# ImageNet CNN comparisons

## Human baseline

Use the documented trained-human baseline from [Shankar et al.](https://proceedings.mlr.press/v119/shankar20c/shankar20c.pdf), section4.3, and [supplement](https://proceedings.mlr.press/v119/shankar20c/shankar20c-supp.pdf), sectionD/Table4: reported median26 seconds, transferred to the model evaluation. Human original-ImageNet top-1 scores are76.9,79.1,80.7,83.5,90.3%; equal-weight mean82.1%. Human reference search and exemplar access differ from model crops; source scoring excludes flagged images. Both comparison flags are retained. Timing covers mixed original/ImageNetV2 images; the publication does not specify whether its overall median pools observers or per-image medians. The timing donor count is 10,000 image judgments (five labelers × 2,000 mixed ImageNet/ImageNetV2 images), subset all. This is the contributing donor count, not an observed model-evaluation timing sample. Source PDFs and scoring code are retained.

**Range: 26 to 64.8 seconds, with the central as the floor.** Shankar et al.
publish two readings of the same labeling effort in the same sentence: a per-image
median of 26 seconds and a **median labeling time of 36 hours for the entire
labeling task**. The task is 2,000 images, so the second is 36 x 3,600 / 2,000 =
**64.8 seconds an image** for the median labeler, the mean pace behind the same
work. The two differ because the distribution is heavily right-skewed: the
supplement's Figure 9 omits 24 images whose median time exceeded 400 seconds, and
the paper says labelers spent "anywhere from a couple of seconds to 40 minutes"
on one image. The median is therefore the floor of the two published readings and
the implied mean is the ceiling. Added 2026-09-17.

This 26-second median is the human time on all four rows of the task, the two ResNet ten-crop rows included. Those rows previously carried 60 seconds from [Karpathy's account](https://karpathy.github.io/2014/09/02/what-i-learned-from-competing-against-a-convnet-on-imagenet/) of labeling at roughly one image per minute. Damon ruled on 2026-09-16 that one task gets one estimate, and Shankar et al. is the better-supported of the two: a published median over 10,000 timed judgments by five trained labelers, against a first-person recollection of a pace that the blog ties to no count of timed images. The ResNet rows are scored top-5 and the timing donor labeled top-1, which the 60-second figure does not repair, because it is not a measurement of top-5 labeling either. Those two rows therefore also carry `different_human_baseline`: the top-5 error they compare against is Karpathy's single expert, a different person from the timing donors. The derivation those rows used to carry is in [resnet.md](../new-sources/resnet.md).

## perc-imagenet-parity-effnet

[Original EfficientNet paper](https://arxiv.org/abs/1905.11946), Table2, reports84.3% top-1 and37 billion in its FLOPS convention, single model/single crop. Use the600-pixel B7 recipe. Broad performance is match:84.3% is close to the trained cohort mean82.1%, with substantial individual spread. This is a judgment about comparable quality, not exact score identity.

The retained original TensorFlow builder specifies width2.0, depth3.1 and input600. The accompanying model implementation uses ceil-scaled block repeats and same-padding spatial reductions. Our independent `count_efficientnet.py` counts expansion, depthwise and projection convolutions, both squeeze-excitation projections, stem and1000-way head. It yields37,745,884,192 MACs, hence75,491,768,384 FLOPs. This also explains the paper’s rounded37B convention: a multiply-add there corresponds to two operations here. Scalar activation, normalization, pooling, SE gate multiplications and residual additions are omitted. This is a dominant-operation count, not a device measurement. The release is Google’s May29,2019 announcement explicitly stating all models were open-sourced, not the paper submission date. Sources: [builder](https://github.com/tensorflow/tpu/blob/master/models/official/efficientnet/efficientnet_builder.py), [model](https://github.com/tensorflow/tpu/blob/master/models/official/efficientnet/efficientnet_model.py), [release](https://research.google/blog/efficientnet-improving-accuracy-and-efficiency-through-automl-and-model-scaling/).

## perc-imagenet-parity-mnv3

The [original release README](https://github.com/tensorflow/models/blob/0ba83cf02114/research/slim/nets/mobilenet/README.md), checkpoint table, reports217 million MACs and75.2% top-1 for Large depth-multiplier1.0 float at224 pixels. Use217e6×2=434,000,000 FLOPs. The [paper](https://arxiv.org/abs/1905.02244) Table3 reports219M at the same accuracy; the released-checkpoint recipe is the chosen operation count. No quantized-checkpoint accuracy is substituted. Performance is below the trained cohort:75.2% is below all five reported human scores. The legacy lead’s casual-parity label is not supported and is not retained in the task description. Release commit0ba83cf02114 explicitly releases models/checkpoint links on October17,2019; the May paper date is not model availability. Retained release history and README verify this.
