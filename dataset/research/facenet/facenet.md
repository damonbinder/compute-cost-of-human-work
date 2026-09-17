# Face-image verification

## perc-faceverif-facenet

Work unit: one identity decision for two supplied face thumbnails. Compare one neural-model decision with ten ordinary human confidence judgments combined into one decision. The human duration sums person-time, not parallel elapsed time.

## Compute

[FaceNet](https://arxiv.org/html/1503.03832v3), Table 1 and section 5.6, specifies NN1 and reports 98.87% accuracy using a fixed central crop. We use that condition, not its 99.63% result requiring another detector/alignment stage. The task starts with supplied thumbnails.

Reconstruct convolution and dense matrix operations from the published dimensions. Each convolution costs output-height × output-width × input-channels × output-channels × kernel-area multiply-adds. Maxout's two projections both execute. `calculation.json` records every layer; `count_operations.py` regenerates it.

The result is 1,605,944,064 multiply-adds per image. Two images and two operations per multiply-add give **6,423,776,256 FLOPs**. Add 1% for resizing, bias and elementwise normalization: **6,488,014,019 FLOPs**. This small allowance does not supply a substantial part of the workload; the evidence remains derived_supported_inputs. A 0–2% allowance gives 6.424–6.552 GFLOPs.

The paper's rounded 1.6B “FLPS” uses a multiply-add convention: its first convolution is approximately 114M multiply-adds, not 114M under our two-operation convention. Counting the published value once would also omit the second image. No prior embeddings are cached. Training and threshold fitting are excluded from this inference work unit.

## Human time

[Kumar et al.](https://www.cs.columbia.edu/CAVE/publications/pdfs/Kumar_ICCV09.pdf), section 4.2 and Figure 6, average confidence from ten people per LFW pair; tightly cropped faces yield 97.53%. The crop masks background and some hair. This is pooled performance, not an individual-rater score. Both systems use LFW, but their crops and assessment procedures differ. Classify the close accuracies as match, retaining those differences.

[Bindemann et al. (2016), Matching Faces Against the Clock](https://journals.sagepub.com/doi/10.1177/2041669516672219), Experiment 1, records time through a binary response. Mean responses under increasing pressure were below two seconds even with generous targets; the slowest participant averaged four seconds in the ten-second condition. The stimuli were controlled frontal faces, not LFW confidence judgments. The paper also explains why an earlier two-second exposure result does not capture complete response time.

Estimate **three seconds on average per independent LFW confidence judgment**, using those recorded response times as an anchor and allowing additional scrutiny of variable crops and confidence entry. This is not a three-second deadline: difficult pairs can take longer. Ten judgments therefore require **30 active person-seconds**. Neither this duration nor quality at this duration was measured on LFW. Pooling ten judgments is part of the performance protocol; each individual need not achieve the pooled score. No independence of their errors is assumed.

A useful sensitivity is 2–10 seconds per rater, or 20–100 person-seconds. This is not a confidence interval. The timing anchor uses the increasing-pressure arm of Bindemann Experiment 1: 20 observers × 200 face-pair trials = 4,000 recorded attempts, with no reported correct-response-only time filter. Use human_attempts=4000 and subset all. The ten LFW raters belong to the target performance workflow and do not multiply the donor sample. Direct LFW response times would improve this transfer.

## Source files

`agent-work/sources/facenet/kumar-2009.pdf` and `agent-work/sources/facenet/facenet-v3.html` retain the two original performance/architecture studies. Timing DOI: 10.1177/2041669516672219. No date is imputed for availability of the evaluated FaceNet weights.

The donor-count audit additionally retained original ACT/Ahn/Bindemann evidence in agent-work/sources/timing-donor-audit/.
