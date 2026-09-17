# ArcFace face verification

## perc-faceverif-arcface

The work is one same-person decision from two already aligned face crops. Use the CVPR 2019 MS1MV2-trained ResNet100 configuration, not the expanded 2022 version of the paper. Table 4 reports 99.83% accuracy on the 6,000 LFW pairs. Section 3.1 specifies 112×112 inputs, 512-dimensional embeddings and one crop at test time. Face detection and alignment precede this work unit.

[Original paper](https://openaccess.thecvf.com/content_CVPR_2019/papers/Deng_ArcFace_Additive_Angular_Margin_Loss_for_Deep_Face_Recognition_CVPR_2019_paper.pdf), section 3.1 and Table 4. Retained in `agent-work/sources/medical-vision/arcface/arcface-original.pdf`.

The [authors' MXNet architecture](https://github.com/deepinsight/insightface/blob/8b79096e70a10a4899f1ce59882ea4d56e634d40/recognition/arcface_mxnet/symbol/fresnet.py) has a 64-channel 3×3 stem and [3,13,30,3] residual units with [64,128,256,512] channels. Each unit uses two 3×3 convolutions; the first unit in each stage downsamples in its second convolution and projects its shortcut. The final 7×7×512 features project to a 512-dimensional embedding. We count the improved non-SE residual configuration. Removing the training classification layer does not remove this embedding projection.

`count_models.py` obtains 12,089,606,144 convolution/dense MACs per image. Two images × two FLOPs per MAC = **48,358,424,576 FLOPs**. Normalization, nonlinearities and cosine-distance arithmetic are minor omissions. The paper's single-crop protocol supports two forwards; a flip-augmented implementation would cost twice as much. This is an architecture calculation, not the paper's GPU latency converted to FLOPs.

The human result comes from [Kumar et al. 2009](https://www.cs.columbia.edu/CAVE/publications/pdfs/Kumar_ICCV09.pdf), section 4.2 and Figure 6. Ten crowd workers supplied confidence judgments for each LFW pair. Their replies were averaged to produce the reported curve. Accuracy was 97.53% for tightly cropped faces, versus 99.20% when the original image context was visible. The comparison uses the cropped condition. Consequently the human workload includes **ten judgments**, not one. ArcFace is above this pooled baseline; the crops and alignment procedures still differ.

No completion timings were reported for those LFW judgments. [Bindemann et al. 2016](https://journals.sagepub.com/doi/10.1177/2041669516672219), Experiment 1, records actual face-matching response times under generous and restrictive time budgets. In the increasing-pressure condition, even the slowest participant averaged 4.0 seconds under the 10-second budget. Several population means were below two seconds. This is different from a two-second image exposure followed by an untimed response.

Estimate **3 seconds per worker**, allowing more time than the fast group means for LFW's varied photographs and the confidence response. Total human work is **10 × 3 = 30 person-seconds**. A 2–6 second individual judgment gives 20–60 person-seconds. These are sensitivity assumptions, not a confidence interval or a claim that 97.53% was measured at a three-second deadline. The transfer is between university participants doing binary matching and crowd workers supplying confidence judgments. The timing anchor uses the 20 increasing-pressure observers in Experiment 1, each completing 200 face-pair trials: 4,000 donor attempts, subset all. No correct-response-only timing filter is reported. The ten LFW judgments per output do not multiply this timing sample.

Model first-public-availability date is left blank: the paper date does not identify the release of the precise MS1MV2 checkpoint. Model organization is InsightFace.

The donor-count audit additionally retained original ACT/Ahn/Bindemann evidence in agent-work/sources/timing-donor-audit/.
