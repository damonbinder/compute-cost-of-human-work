"""Training-run FLOPs for the five single-purpose medical models, and the
comparator specialists' active training hours.

Self-contained: convolution/dense MAC counts are recomputed here with the same
shape-counting recipe as research/medical-vision/count_models.py, and the two
Inception v3 and the DenseNet-121 per-forward figures are quoted from the
audited inference notes (research/medical-vision/{skin,retina}.md,
research/chexnet/chexnet.md) as constants, asserted against the recomputed
values where a recomputation is possible. Two FLOPs per MAC. A weight update
costs three forward passes (one forward, two backward).

The human side is the active time a person spends doing this one read while
learning it: cases read in training times the measured time per read, plus
documented directly-on-task instruction. Nothing outside the read is charged.

Usage: python3 medical_learning_calc.py OUTPUT_DIR
Writes calculations.json into OUTPUT_DIR (agent-work/derived/medical-learning/).
"""
import argparse
import json
import math
from pathlib import Path

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("output_dir", type=Path)
args = cli.parse_args()
args.output_dir.mkdir(parents=True, exist_ok=True)

TRAIN = 3.0            # forward + backward, as a multiple of one forward
EPOCHS = 30            # uniform assumption where the paper publishes none
EPOCHS_LOW, EPOCHS_HIGH = 10, 100


class Counter:
    def __init__(self):
        self.rows = []

    def conv(self, x, c, k=1, s=1, padding="SAME", groups=1, name="conv"):
        h, w, ci = x
        kh, kw = (k, k) if isinstance(k, int) else k
        oh, ow = ((math.ceil(h / s), math.ceil(w / s)) if padding == "SAME"
                  else ((h - kh) // s + 1, (w - kw) // s + 1))
        self.rows.append(dict(name=name, macs=oh * ow * ci * c * kh * kw // groups))
        return oh, ow, c

    def conv1d(self, x, c, k, s=1, name="conv1d"):
        n, ci = x
        on = math.ceil(n / s)          # keras padding='same'
        self.rows.append(dict(name=name, macs=on * ci * c * k))
        return on, c

    def dense(self, ni, no, name="dense", repeats=1):
        self.rows.append(dict(name=name, macs=ni * no * repeats))

    @property
    def macs(self):
        return sum(r["macs"] for r in self.rows)


def resnet50(h, w, channels=3):
    """TF-Slim end-of-block stride convention, as in the inference audit."""
    count = Counter()
    x = count.conv((h, w, channels), 64, 7, s=2, name="stem")
    x = (math.ceil(x[0] / 2), math.ceil(x[1] / 2), x[2])
    for i, (b, n) in enumerate(zip([64, 128, 256, 512], [3, 4, 6, 3])):
        for j in range(n):
            previous = x
            s = 2 if i < 3 and j == n - 1 else 1
            if previous[2] != 4 * b:
                count.conv(previous, 4 * b, 1, s=s, name=f"block{i}.{j}.shortcut")
            x = count.conv(x, b, 1, name=f"block{i}.{j}.conv1")
            x = count.conv(x, b, 3, s=s, name=f"block{i}.{j}.conv2")
            x = count.conv(x, 4 * b, 1, name=f"block{i}.{j}.conv3")
    return count


def mobilenet_v2(size=409, width=1):
    count = Counter()

    def channels(c):
        return max(8, int(c * width + 4) // 8 * 8)

    x = count.conv((size, size, 3), channels(32), 3, s=2, name="stem")
    for i, (t, c, n, s) in enumerate([(1, 16, 1, 1), (6, 24, 2, 2), (6, 32, 3, 2),
                                      (6, 64, 4, 2), (6, 96, 3, 1), (6, 160, 3, 2),
                                      (6, 320, 1, 1)]):
        for j in range(n):
            expanded = x[2] * t
            if t != 1:
                x = count.conv(x, expanded, 1, name=f"block{i}.{j}.expand")
            x = count.conv(x, expanded, 3, s=s if j == 0 else 1, groups=expanded,
                           name=f"block{i}.{j}.depthwise")
            x = count.conv(x, channels(c), 1, name=f"block{i}.{j}.project")
    count.conv(x, max(1280, channels(1280)), 1, name="features")
    return count


def retinanet(size=2048):
    """Standard ResNet-50/FPN RetinaNet, 256-wide pyramid, 9 anchors, 1 class."""
    count = resnet50(size, size)
    for level, c in [(3, 512), (4, 1024), (5, 2048)]:
        n = size // (2 ** level)
        count.conv((n, n, c), 256, 1, name=f"fpn{level}.lateral")
        count.conv((n, n, 256), 256, 3, name=f"fpn{level}.output")
    count.conv((64, 64, 2048), 256, 3, s=2, name="fpn6")
    count.conv((32, 32, 256), 256, 3, s=2, name="fpn7")
    for level in range(3, 8):
        n = size // (2 ** level)
        for head, out in [("class", 9), ("box", 36)]:
            x = (n, n, 256)
            for j in range(4):
                x = count.conv(x, 256, 3, name=f"p{level}.{head}{j}")
            count.conv(x, out, 3, name=f"p{level}.{head}.out")
    return count


def breast_head(width=2048):
    """Unreported head widths: constant output width, quarter-width bottlenecks."""
    count = Counter()
    x = (128, 104, 4096)
    for group, stride in enumerate([4, 2, 2]):
        for j in range(4):
            s = stride if j == 0 else 1
            old = x
            x = count.conv(x, width // 4, 1, name=f"head{group}.{j}.conv1")
            x = count.conv(x, width // 4, 3, s=s, name=f"head{group}.{j}.conv2")
            x = count.conv(x, width, 1, name=f"head{group}.{j}.conv3")
            if old[2] != width:
                count.conv(old, width, 1, s=s, name=f"head{group}.{j}.shortcut")
    count.conv(x, 1, 1, name="breast_logit")
    return count


def hannun_ecg(samples=6000, classes=12, start_filters=32, filter_length=16,
               blocks=16, increase_every=4):
    """34-layer 1D residual network, exactly as awni/ecg network.py builds it."""
    count = Counter()
    x = count.conv1d((samples, 1), start_filters, filter_length, name="stem")
    for index in range(blocks):
        filters = 2 ** (index // increase_every) * start_filters
        subsample = 2 if index % 2 == 1 else 1
        for i in range(2):
            x = count.conv1d(x, filters, filter_length,
                             s=subsample if i == 0 else 1,
                             name=f"block{index}.conv{i}")
    count.dense(x[1], classes, name="timedistributed_logits", repeats=x[0])
    return count


# Audited per-forward figures from the inference notes.
DENSENET121_FLOPS = 5_698_465_281        # research/chexnet/chexnet.md#flops
INCEPTION_SKIN_MACS = 5_712_718_432      # research/medical-vision/skin.md
INCEPTION_RETINA_MACS = 5_711_176_288    # research/medical-vision/retina.md

macs = {
    "resnet50_case_2048": resnet50(2048, 2048).macs,
    "resnet50_breast_4096x3328": resnet50(4096, 3328).macs,
    "mobilenet_patch_409": mobilenet_v2().macs,
    "retinanet_detector_2048": retinanet().macs,
    "breast_head_assumed": breast_head().macs,
    "hannun_ecg_30s": hannun_ecg().macs,
}
# Reproduces the retained inference ledger exactly for the shared components.
assert macs["resnet50_case_2048"] == 290_916_925_440
assert macs["resnet50_breast_4096x3328"] == 945_480_007_680
assert macs["mobilenet_patch_409"] == 1_025_914_608
assert macs["retinanet_detector_2048"] == 782_631_501_824
assert macs["breast_head_assumed"] == 54_375_071_744

points = {}

# --- CheXNet -----------------------------------------------------------------
# arXiv v1: 112,120 images split 80/20; weights randomly initialised.
chexnet_train_images = round(112_120 * 0.8)
chexnet_val_images = 112_120 - chexnet_train_images


def chexnet_total(epochs):
    train = TRAIN * DENSENET121_FLOPS * chexnet_train_images * epochs
    val = DENSENET121_FLOPS * chexnet_val_images * epochs
    return train + val


points["med-cxr-train-chexnet"] = dict(
    scope="full_training",
    forward_flops=DENSENET121_FLOPS,
    examples_per_epoch=chexnet_train_images,
    epochs=EPOCHS,
    flops=chexnet_total(EPOCHS),
    low=chexnet_total(EPOCHS_LOW),
    high=chexnet_total(EPOCHS_HIGH),
    excluded_pretraining=0,
)

# --- Gulshan diabetic retinopathy --------------------------------------------
retina_forward = 2 * INCEPTION_RETINA_MACS
retina_images = 128_175
retina_networks = 10


def retina_total(epochs):
    return TRAIN * retina_forward * retina_images * epochs * retina_networks


imagenet_inception_pretrain = TRAIN * (2 * INCEPTION_RETINA_MACS) * 1_281_167 * 90
points["med-retina-train-gulshan"] = dict(
    scope="additional_training",
    forward_flops=retina_forward,
    examples_per_epoch=retina_images * retina_networks,
    epochs=EPOCHS,
    flops=retina_total(EPOCHS),
    low=retina_total(EPOCHS_LOW),
    high=retina_total(EPOCHS_HIGH),
    excluded_pretraining=imagenet_inception_pretrain,
)

# --- Esteva skin lesions ------------------------------------------------------
skin_forward = 2 * INCEPTION_SKIN_MACS
skin_images = 127_463


def skin_total(epochs):
    return TRAIN * skin_forward * skin_images * epochs


points["med-skin-train-esteva"] = dict(
    scope="additional_training",
    forward_flops=skin_forward,
    examples_per_epoch=skin_images,
    epochs=EPOCHS,
    flops=skin_total(EPOCHS),
    low=skin_total(EPOCHS_LOW),
    high=skin_total(EPOCHS_HIGH),
    augmentation_720_scenario=skin_total(720),
    excluded_pretraining=TRAIN * (2 * INCEPTION_SKIN_MACS) * 1_281_167 * 90,
)

# --- McKinney mammography -----------------------------------------------------
case_forward = 2 * (4 * macs["resnet50_case_2048"] + 4 * 2048 * 512)
breast_forward = 2 * (4 * macs["resnet50_breast_4096x3328"]
                      + 2 * macs["breast_head_assumed"])
lesion_patch_forward = 2 * (10 * macs["mobilenet_patch_409"] + 10 * (2 * 1280 + 8))
detector_forward = 2 * macs["retinanet_detector_2048"]

runs = 3
case_flops = runs * TRAIN * case_forward * 50_000 * 2
breast_flops = runs * TRAIN * breast_forward * 120_000 * 16
lesion_flops = runs * TRAIN * lesion_patch_forward * 750_000 * 4
detector_flops = TRAIN * detector_forward * 50_000 * 4      # schedule assumed
mammo_total = case_flops + breast_flops + lesion_flops + detector_flops
points["med-mammo-train-mckinney"] = dict(
    scope="additional_training",
    branches=dict(case=case_flops, breast=breast_flops,
                  lesion_classifier=lesion_flops, detector=detector_flops),
    flops=mammo_total,
    low=case_flops + breast_flops / 4 + lesion_flops + detector_flops,
    high=mammo_total + TRAIN * detector_forward * 4 * 4 * 750_000,
    excluded_pretraining=TRAIN * 2 * resnet50(224, 224).macs * 1_281_167 * 90,
)

# --- Hannun ECG ---------------------------------------------------------------
ecg_forward = 2 * macs["hannun_ecg_30s"]
ecg_records = 91_232
ecg_train = round(ecg_records * 0.9)
ecg_dev = ecg_records - ecg_train


def ecg_total(epochs):
    return (TRAIN * ecg_forward * ecg_train * epochs
            + ecg_forward * ecg_dev * epochs)


points["med-ecg-train-hannun"] = dict(
    scope="full_training",
    forward_flops=ecg_forward,
    examples_per_epoch=ecg_train,
    epochs=EPOCHS,
    flops=ecg_total(EPOCHS),
    low=ecg_total(EPOCHS_LOW),
    high=ecg_total(EPOCHS_HIGH),
    excluded_pretraining=0,
)

# --- Human side: active hours spent doing this read while learning it ---------
# One method: hours = cases read in training x measured time per read
#                     + documented directly-on-task instruction hours.
# Nothing outside the read itself is charged: no medical school, no rotations,
# no background science.

reads = {
    "med-cxr-train-chexnet": dict(
        cases=4523,                  # Khoobi et al. (2025), residents at 43.5 months
        seconds_per_case=88.0,       # same study, free-text reporting per radiograph
        instruction_hours=0.0),
    "med-retina-train-gulshan": dict(
        cases=1000,                  # NHS DESP minimum grades per annum, one qualifying year
        seconds_per_case=3.2 * 60,   # 3.2 min per image set
        instruction_hours=80.0),     # City & Guilds units 7 and 8: 60 + 20 guided learning hours
    "med-skin-train-esteva": dict(
        cases=600,                   # Ternov et al. (2023): 500 training + 100 retention
        seconds_per_case=117.1 * 60 / 500,   # measured diagnosing time over the 500
        instruction_hours=100.0 / 60),       # measured learning-module reading time
    "med-mammo-train-mckinney": dict(
        cases=240,                   # MQSA initial qualification, 21 CFR 900.12
        seconds_per_case=118.0,      # measured screening-mammogram interpretation time
        instruction_hours=60.0),     # MQSA category I mammography education
    "med-ecg-train-hannun": dict(
        cases=3250,                  # COCATS 4 Task Force 3, 3,000-3,500 in 36 months
        seconds_per_case=205.31,     # Bortolotti et al. (2025), resident interpretation time
        instruction_hours=0.0),
}


def two_sf(x):
    return float(f"{x:.2g}")


for point, r in reads.items():
    reading = r["cases"] * r["seconds_per_case"] / 3600
    hours = reading + r["instruction_hours"]
    rounded = two_sf(hours)
    points[point]["human_cases"] = r["cases"]
    points[point]["human_seconds_per_case"] = r["seconds_per_case"]
    points[point]["human_reading_hours"] = reading
    points[point]["human_instruction_hours"] = r["instruction_hours"]
    points[point]["human_hours_exact"] = hours
    points[point]["human_hours"] = rounded
    points[point]["human_seconds"] = rounded * 3600

# The rejected reading: whole specialist training, kept for the record only.
WEEKS, HOURS_WEEK, CLINICAL_MED_SCHOOL_YEARS = 48, 80, 2
HOURS_YEAR = WEEKS * HOURS_WEEK
pathways = {
    "radiologist": dict(pgy1=1, residency=4, fellowship=0),
    "ophthalmologist": dict(pgy1=1, residency=3, fellowship=0),
    "dermatologist": dict(pgy1=1, residency=3, fellowship=0),
    "cardiac_electrophysiologist": dict(pgy1=0, residency=3, fellowship=5),
    "general_cardiologist": dict(pgy1=0, residency=3, fellowship=3),
}


def pathway_hours(p):
    years = CLINICAL_MED_SCHOOL_YEARS + p["pgy1"] + p["residency"] + p["fellowship"]
    return years * HOURS_YEAR, years


rejected = {k: dict(zip(["hours", "years"], pathway_hours(v)))
            for k, v in pathways.items()}
ep, card = rejected["cardiac_electrophysiologist"], rejected["general_cardiologist"]
rejected["hannun_weighted_pool"] = dict(
    years=(8 * ep["years"] + card["years"]) / 9,
    hours=(8 * ep["hours"] + card["hours"]) / 9)
rejected_rows = {
    "med-cxr-train-chexnet": "radiologist",
    "med-mammo-train-mckinney": "radiologist",
    "med-retina-train-gulshan": "ophthalmologist",
    "med-skin-train-esteva": "dermatologist",
    "med-ecg-train-hannun": "hannun_weighted_pool",
}
for point, pathway in rejected_rows.items():
    points[point]["rejected_whole_training_hours"] = two_sf(
        rejected[pathway]["hours"])

report = dict(
    convention=("2 FLOPs per MAC; a training example costs 3 forward passes. "
                "Pooling, normalisation and nonlinearities are omitted."),
    per_forward_macs=macs,
    epochs_assumed=dict(central=EPOCHS, low=EPOCHS_LOW, high=EPOCHS_HIGH),
    human_reads=reads,
    rejected_whole_training=rejected,
    points=points,
)
(args.output_dir / "calculations.json").write_text(
    json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
