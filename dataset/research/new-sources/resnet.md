# ImageNet recognition and taxonomy learning

Original sources: [He et al., ResNet](https://arxiv.org/pdf/1512.03385), section3.4, Tables1/3; [Karpathy's first-person human study account](https://karpathy.github.io/2014/09/02/what-i-learned-from-competing-against-a-convnet-on-imagenet/). The human account includes concrete examples of difficult fine-grained dog labels; this is a1000-class taxonomy task, not merely spotting an everyday object.

Human evidence: after500 practice images, the expert labeled1500 test images at5.1% top-five error. Annotation proceeded at about one image/minute, decreasing over time, with some images requiring several minutes. This is a rough reported pace, not a logged mean. It was the source of the 60-second human time these rows carried until 2026-09-16, when Damon ruled that the whole `classify-an-imagenet-image` task takes one estimate and the better-supported one is Shankar et al.'s 26-second median over 10,000 timed judgments ([imagenet-cnn.md](../imagenet-cnn/imagenet-cnn.md#human-baseline)). The pace is retained here as the competing evidence, not as the recorded duration. The interface allows class reference lookup; human test images differ from model validation images. Those are recorded comparison issues. The reported pace is not tied to an exact timed-image count: 1,500 test labels and 500 practice labels are known, but the blog does not identify which timings establish the rough rate. Neither 1,500 nor 2,000 was ever asserted to be the timing sample, which is why the blank human_attempts count stood while this donor supplied the duration. The rows now count the Shankar donor's 10,000 judgments instead, and record the statistic as median.

## FLOP convention

Table1 reports3.8G and11.3G for ResNet50/152 at224×224. Those magnitudes count a multiply-accumulate once: for example, the first7×7 convolution has112×112×64×7×7×3 products, and summing the bottleneck convolutions reproduces the reported magnitudes. We use two FLOPs per multiply-add. Table3 performance is TEN crops. Therefore multiply table complexity by20, not2. Table4's better errors use multiscale fully convolutional evaluation and are not paired with these costs. Costs include the image classifier, not prior training.

## resnet50_imagenet_10crop

`3.8e9 × 2 × 10 = 7.6e10` FLOPs. Error6.71% versus human5.1%: below. Human time is Shankar et al.'s 26s median.

## resnet152_imagenet_10crop

`11.3e9 × 2 × 10 = 2.26e11` FLOPs. Error5.71% versus human5.1%: match as a broad comparison, not a statistical-equivalence claim. Human time is Shankar et al.'s 26s median.

## resnet152_imagenet_learning — deferred after independent review

Human starts as acomputer-vision expert with lifetime visual competence but without thebenchmark's fine-grained class familiarity. Target is the observed5.1% result after500 practice images. Transfer the1min/image annotation pace to deliberate labeled practice: `500×60=30,000s` (8.33h). This is a judgment-based transfer, not measured practice duration. Review plausibility over roughly0.5–2min/practice image (4.2–16.7h); practice may be slower because errors require review, but easier examples also need less time.

AI starts from random weights. Section3.4 gives batch256, up to600,000 updates. Use600,000 as the schedule estimate for thedeep152-layer model; not a separately measured model-specific update count. Training forward+backward assumed3× forward. Add1% for validation/checkpoint evaluation, because no complete evaluation log is supplied. This modest allowance corresponds to4.608million forward-image equivalents, about92 single-crop validation passes. Thus `600000 ×256 ×3 ×(2×11.3e9) ×1.01 = 1.05182208e19` FLOPs. Sensitivity is linear in updates;300,000 would halve compute. No language token count enters.

The AI's full visual training and human's taxonomy adaptation have different starting capabilities; thework unit deliberately states this asymmetry. This row must not be interpreted as thehuman's total cost to develop vision. It is submitted for review because thehuman transition and numerical schedule estimate are consequential, not because formal paired timings are required.

Disposition: removed from candidate points.csv. Human taxonomy adaptation is not the same transition as random-weight acquisition of visual classification. A repair needs a pretrained model undergoing comparable taxonomy adaptation, or a credible full human-acquisition scope. Disclosure of asymmetry alone is insufficient. No replacement numerical estimate is forced.
