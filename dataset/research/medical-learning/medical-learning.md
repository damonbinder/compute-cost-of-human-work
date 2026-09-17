# Training single-purpose medical models against learning the same read

*Created 2026-09-14 14:12.*

*Last revised 2026-09-14 16:25.*

Five single-purpose medical models were trained to read one thing — a chest
radiograph, a fundus photograph, a skin lesion, a screening mammogram, an
ambulatory ECG — and each was scored against the people who read it. This
note builds one `skill_acquisition` row per model. The AI side is the training
run that produced the compared weights. The human side is the active time a
person spends doing that one read while learning it, to the accuracy of the
readers the paper compared the model against, derived by one method applied to
all five rows. The four inference rows for these models already exist and are
untouched; these rows sit beside them.

## Summary

| Point | Model | Scope | Training FLOPs | Comparator | Human hours | Label |
|---|---|---|---:|---|---:|---|
| `med-cxr-train-chexnet` | CheXNet, DenseNet-121 | full_training | 4.98e16 | US radiologist | 110 | above |
| `med-retina-train-gulshan` | Gulshan, 10 x Inception v3 | additional_training | 1.32e18 | US ophthalmologist | 130 | above |
| `med-skin-train-esteva` | Esteva, Inception v3 | additional_training | 1.31e17 | US dermatologist | 4.0 | match |
| `med-mammo-train-mckinney` | McKinney, three branches | additional_training | 1.38e20 | US radiologist | 68 | above |
| `med-ecg-train-hannun` | Hannun, 34-layer 1D ResNet | full_training | 2.50e16 | US cardiologist or electrophysiologist | 190 | above |

Four orders of magnitude separate the cheapest training run from the most
expensive, and the human side spans a factor of 48, so the ratio these rows
carry is still set mostly by the AI leg. The mammography system costs more to
train than the other four combined by three orders of magnitude, because its
dominant branch reads two 4096x3328 images per breast for 120,000 steps at batch
16.

Three of the five rows rest on an assumed epoch count, which is the largest
single uncertainty on the AI side. Mammography does not: its supplement
publishes step counts and batch sizes for every branch.

## What the row compares

The AI quantity is the training run that produced the weights the paper
evaluated, including the validation passes that selected the checkpoint. It
excludes the subsequent test-set inference, which the existing perception rows
carry.

The human quantity is the active time spent doing this one read while learning
it: looking at the images or tracings, calling them, and being corrected. The
test is what a person would spend who wanted only to read this one thing as
accurately as the paper's comparators and cared about nothing else. Medical
school, residency rotations, anatomy and physiology are not charged, because
they are not this read; a row charges the reading itself and the instruction
aimed directly at it.

`performance_vs_human` compares the model with those same readers on the paper's
own metric, and carries over the label the existing inference row established
from the same comparison. No row is `far_above`: in every case the readers do
the job, and the model's edge is modest on the paper's metric.

## Human learning time

### One method

Active hours to read this one thing as well as the paper's comparators are

    hours = cases read in training x measured time per read
            + documented directly-on-task instruction hours

with the case count, the per-case time and the instruction hours all taken from
published sources for that read, and nothing outside the read charged. Three
stipulations apply identically to all five rows.

**A case counts only if the learner calls it.** The quantity is reading, not
attendance. Where a source gives a case count under supervision, that count is
used whole, because a supervised read is a read plus its correction and both are
time on the task.

**The per-case time is the learner's, where one is measured.** Learners read
slower than the readers they are training to match: 205 seconds against 108 for
an ECG, and experts reach a dermoscopic diagnosis 70% quicker than novices. Two
rows use a time measured on the learning population itself, two use a measured
interpretation time for the read, and one uses a programme's own operational
figure.

**Instruction counts only when it is the read.** Sixty hours of category I
mammography education and eighty guided learning hours on grading retinal images
are instruction in the read. A physiology course is not, and is not charged.

### The five reads

| Read | Cases | Source of the count | Seconds per case | Source of the time | Instruction hours | Hours |
|---|---:|---|---:|---|---:|---:|
| Chest radiograph | 4523 | end-of-residency reported volume | 88 | same readers, free-text reporting | 0 | 110 |
| Referable diabetic retinopathy | 1000 | NHS DESP minimum annual grading volume | 192 | programme workload figure | 80 | 130 |
| Dermoscopic lesion | 600 | measured training-to-pass protocol | 14.1 | same participants, measured in-app | 1.7 | 4.0 |
| Screening mammogram | 240 | MQSA initial qualification | 118 | measured interpretation time | 60 | 68 |
| Ambulatory ECG rhythm | 3250 | COCATS 4 Level I volume | 205 | residents, measured | 0 | 190 |

**Chest radiograph.**
[Khoobi et al. (2025)](https://arxiv.org/abs/2510.16070) recorded, for four
residents who had completed radiography training and were awaiting board
certification, a mean of 4,523 chest radiographs reported (range 1,789 to 6,561)
over 43.5 months, against 75 for the novice group at 6.8 months. The same study
measured 88 +/- 38 seconds per radiograph in free-text reporting, the mode that
matches clinical reporting. One study therefore supplies both the count and the
rate for the same readers, which is why this row is the best anchored of the
five. CheXNet's comparators are four practising radiologists, one rung above
that resident group; the accuracy ladder in
[Kelly et al. (2016)](https://doi.org/10.1148/radiol.2016150409) is flat between
registrar and consultant, so the resident volume is where the comparators' level
is reached.

**Referable diabetic retinopathy.** The English programme documents both halves.
Units 7 and 8 of the
[City & Guilds Level 3 qualification in diabetic retinopathy screening](https://www.cityandguilds.com/qualifications-and-apprenticeships/health-and-social-care/health/7360-diabetic-retinopathy-screening),
which a grader must pass before grading unsupervised, recommend 60 and 20
guided learning hours for assessing fundus images for disease and for
classifying diabetic retinopathy, so 80 hours of instruction in the read. The
[interim quality assurance standards](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/805606/DES_interim_quality_assurance_standards.pdf)
set a minimum of 1,000 grades a year, and the full qualification must be
obtained within two years of appointment, so one qualifying year of the minimum
volume is the reading charged. Grading takes 3.2 minutes per image set, 2 for a
negative and 5 for a positive, on the operational figure in
[Bodrogi et al. (2025)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC13413944/).
Gulshan's comparators are US ophthalmologists whose mean agreement with the
reference panel was 77.7% sensitivity at 97.4% specificity, which is screening
grader territory, so a trained grader's pathway is the right ladder.

**Dermoscopic lesion.**
[Ternov et al. (2023)](https://doi.org/10.5826/dpc.1302a105) is the only measured
reads-to-competence curve on any of these five reads. Seventy-six medical
students with no prior experience diagnosed 500 dermoscopic cases over eight
days and 100 more in a retention phase, with immediate feedback on every case,
and 78% then passed a 25-item test in skin cancer diagnostics whose pass mark
was set by the contrasting-groups method against 136 doctors and 36 students in
[Ternov et al. (2021)](https://doi.org/10.1007/s00403-020-02097-8). The
application measured the time: 117.1 minutes diagnosing the 500 cases, 14.1
seconds each, and 100 minutes reading the learning modules. The 100 retention
cases at the same rate bring the total to 240 minutes. The learning curve is a
straight line on the log-odds scale with one knot at 100 cases, and 40% of the
training time falls in those first 100.

**Screening mammogram.** An interpreting physician qualifies under
[21 CFR 900.12](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-I/part-900/subpart-B/section-900.12)
by holding 60 hours of category I continuing medical education in mammography
and by interpreting or multi-reading at least 240 mammographic examinations
under direct supervision. Both requirements are the read itself. Screening
mammograms are interpreted in 118 +/- 4 seconds without computer-aided
detection, the mean in
[Tchou et al. (2010)](https://doi.org/10.1148/radiol.10092170).

**Ambulatory ECG rhythm.**
[COCATS 4 Task Force 3](https://www.jacc.org/doi/10.1016/j.jacc.2015.03.021)
states that no threshold number of studies serves as a training landmark but
that interpreting approximately 3,000 to 3,500 ECGs within 36 months should
provide ample experience, and that trainees should read side by side with
faculty for immediate review. Residents take 205.31 +/- 57.43 seconds per
tracing against 107.61 +/- 32.78 for expert cardiologists, measured by
[Bortolotti et al. (2025)](https://doi.org/10.1111/anec.70082).

### Where the comparators sit on the measured accuracy curve

The ECG row is the one read with a published accuracy ladder in training level.
[Cook et al. (2020)](https://pubmed.ncbi.nlm.nih.gov/32986084/) pool ECG
interpretation accuracy at 42.0% for medical students, 55.8% for residents,
68.5% for practising physicians and 74.9% for cardiologists. Hannun's annotators
are eight cardiac electrophysiologists and one cardiologist, so they sit on the
top rung, and the COCATS volume is exactly the volume a cardiology fellowship
puts behind that rung. The model's average F1 of 0.837 exceeds the
cardiologists' 0.780, so it is above the last rung the curve has.

The other reads have rungs but no hours or case counts attached to them:
Kelly's four experience levels on pneumothorax detection, the volume-versus-
outcome association in
[Miglioretti et al. (2009)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2375876/)
and [the RSNA volume study](https://pubs.rsna.org/doi/10.1148/radiol.2533090070)
for mammography, and the three experience groups timed in
[Dreiseitl et al. (2012)](https://doi.org/10.1016/j.artmed.2011.11.004) for
dermoscopy. They place the comparators on their ladders, which is how each row's
case count was chosen, but they cannot be read off for hours directly.

### Scenarios

| Scenario | Effect |
|---|---|
| Chest radiographs at the observed range of 1,789 to 6,561 rather than the mean | 44 to 160 hours on that row |
| Retinopathy grading charged two qualifying years rather than one | 190 hours |
| Dermoscopy carried to the experienced-dermatologist band rather than the pass mark | 5.8 hours, quantified 2026-09-17 |
| Mammography charged the MQSA continuing volume of 960 examinations per 24 months as well | 99 hours |
| ECG read at the expert's 108 seconds rather than the resident's 205 | 97 hours |

### Bounds, 2026-09-17

All four of the remaining rows take bounds; the chest-radiograph row already had them
from the observed 1,789-to-6,561 volume range.

**Ambulatory ECG, 190 hours, bounded 89.7 to 199.6.** Both factors have a published
range of their own. COCATS 4 names 3,000 to 3,500 tracings, and Bortolotti et al.
measure 107.61 s for the expert cardiologist against 205.31 s for the resident. The
low takes both at their fast end, 3,000 x 107.61 = 322,830 s = **89.7 h**, which is
the Scenarios table's expert-rate reading at the lower volume; the high takes both
at their slow end, 3,500 x 205.31 = 718,585 s = **199.6 h**. The central reads at
the resident's rate over the midpoint volume and sits just under the high, which is
right: a learner reads at the learner's rate for most of the way.

**Referable diabetic retinopathy, 130 hours, bounded 110 to 190.** The high is the
Scenarios table's two qualifying years, 190 h. The low moves the other named factor.
Bodrogi et al.'s 3.2 minutes an image set is an operational mean over a mix whose
composition is not this programme's; the same source prices a negative set at 2
minutes, and a screening grader's year is dominated by negatives. At 2 minutes the
reading is 1,000 x 120 = 120,000 s = 33.3 h, and with the 80 instruction hours that
is **110 h**.

**Screening mammogram, 68 hours, with the central as the floor, bounded to 99.**
Both terms of this one are statutory minima: 21 CFR 900.12 sets 60 hours of category
I education and 240 supervised interpretations as the least anyone may qualify on,
and Tchou et al.'s 118 +/- 4 s leaves the reading term, 7.9 h of the 68, with almost
no room. Every alternative the sources offer adds volume, so 68 h is a floor and the
Scenarios table's continuing-volume reading, **99 h**, is the ceiling.

**Dermoscopic lesion, 4.0 hours, bounded 3.4 to 5.8.** Both papers were reached on
2026-09-17 and the alternative the earlier pass could not quantify is now a number.
[Ternov et al. (2021)](https://doi.org/10.1007/s00403-020-02097-8), Table 1, gives
the 25-item test's group means: 7.5 of 25 for its 35 medical students, 18.4 for the
32 clinicians in departments of dermatology, and a pass-fail limit of 12 set by
contrasting groups. [Ternov et al. (2023)](https://doi.org/10.5826/dpc.1302a105)
gives the other end of the same scale: after 600 cases its 76 students scored a mean
13.85 (13.8 intervention, 13.9 control), and its fitted learning curve is a line on
the log-odds scale.

That is enough to run the line. On the log-odds of a correct item, the students move
from `ln(7.5/17.5) = -0.84730` to `ln(13.85/11.15) = 0.21683` over 600 cases, a slope
of **0.00177355 per case**. The 2023 paper fits one knot at 100 cases but publishes
neither segment's slope, describing the result as an almost straight line, so the
single fitted slope stands for both segments.

| Scenario | Target score | Log-odds | Cases | Reading at 14.1 s | Plus 100 min modules | Hours |
|---|---:|---:|---:|---:|---:|---:|
| Pass mark | 12 | -0.08004 | 433 | 6100 | 12100 | 3.4 |
| Protocol as run | 13.85 | 0.21683 | 600 | 8460 | 14460 | 4.0 |
| Dermatology group | 18.4 | 1.02524 | 1056 | 14887 | 20887 | 5.8 |

The central stays on the protocol as run, which is the training that was measured and
that put 78% of the students past the pass mark. The two bounds are the two targets
the note already named: the pass mark the row is read off at, reached by the mean
student 167 cases earlier, and the comparator band the method asks for, which Esteva's
21 board-certified dermatologists sit in. The module reading is held at its measured
100 minutes at every target, because the application has 38 modules and a longer case
run rereads them rather than adding new ones; holding it fixed keeps the low bound
higher and the high bound lower than a scaling term would.

Two things the range does not carry. The knot means the post-100-case slope is
shallower than the fitted average, so the 1,056-case figure understates the cases a
learner needs to reach 18.4, and 5.8 hours is a conservative ceiling. And Ternov's
dermatology group is everyone employed in a dermatology department rather than the
board-certified subset; the published experience bands nearby, 18.5 at 6-10 years and
17.7 above 10, say that experience alone does not move the target much.

### The rejected reading: whole specialist training

The first version of these rows charged the entire professional training of the
comparator specialist, at 27,000 hours for a radiologist, 23,000 for an
ophthalmologist or dermatologist and 38,000 for the ECG paper's annotator pool.
That figure was (clinical medical-school years + postgraduate years) x 80 hours
x 48 weeks, with program lengths from the ACGME requirements and the 80-hour
week from the common program requirements' duty-hour limit. It is rejected. The
dataset's convention for `skill_acquisition` is the task-specific learning time,
and a residency is not the read: it buys a whole specialty, of which this one
interpretation is a small part. Charging it put the human side one to two orders
of magnitude above the quantity the row is supposed to measure, and made all
five rows nearly identical on the human axis whatever the read. The figures are
recorded here so the change is legible, and `medical_learning_calc.py` still
computes them under `rejected_whole_training`.

## Compute

### Recipe

Training FLOPs are three forward passes per training example — one forward, two
backward — times the examples the run processed, plus one forward pass per
validation example where the run evaluated a held-out set each epoch. Arithmetic
is counted at two FLOPs per multiply-add, as in the inference rows. The
per-forward costs come from the audited inference notes where one exists
([chexnet.md](../chexnet/chexnet.md#flops),
[skin.md](../medical-vision/skin.md),
[retina.md](../medical-vision/retina.md),
[mammography.md](../medical-vision/mammography.md)), and `medical_learning_calc.py`
beside this note recomputes every shared component from the architecture and
asserts it against the retained ledger.

Three of the five papers publish no epoch count. All three take the same assumed
**30 epochs**, with 10 and 100 as the scenario ends; the assumption is uniform so
that the rows stay comparable with each other. The ECG model's public code
constrains it best, running `MAX_EPOCHS = 100` with early stopping at patience 8
and learning-rate reduction at patience 2.

Where the run fine-tunes an ImageNet-pretrained backbone the row is
`additional_training` and the backbone's own training is excluded, following the
dataset's convention for an already-trained starting model and the Code Llama
rows' precedent. Each row states below what the excluded pretraining would cost
at a standard 90-epoch ImageNet schedule over 1,281,167 images.

### med-cxr-train-chexnet

[CheXNet v1](https://arxiv.org/abs/1711.05225v1), the version the inference row
uses, states that the weights of the network are randomly initialized, so the row
is `full_training` and no backbone is excluded. Section 3.1 splits ChestX-ray14's
112,120 images 80/20, giving 89,696 training and 22,424 validation images, at
224x224 through DenseNet-121 with a binary head, 5,698,465,281 FLOPs per forward.
At 30 epochs the run costs 4.60e16 FLOPs of training plus 3.83e15 of validation,
**4.98e16 FLOPs**. The epoch scenario is 1.66e16 to 1.66e17.

Later revisions of the same paper describe a different setup: v3 initializes from
ImageNet weights and splits the data 98,637 / 6,351 / 420 by patient. Read that
way the row would be `additional_training` at 5.17e16 FLOPs with a 1.97e18
DenseNet-121 ImageNet run excluded, which is 38 times the fine-tune. The dataset
follows v1 throughout for this model.

Four practicing Stanford radiologists with 4, 7, 25 and 28 years of experience
labelled the 420-image test set, one of them fellowship-trained in thoracic
radiology.

### med-retina-train-gulshan

[Gulshan et al. (2016)](https://jamanetwork.com/journals/jama/fullarticle/2588763)
preinitializes from ImageNet weights and trains an ensemble of ten Inception v3
networks on the same 128,175-image development set, so the row is
`additional_training`. Each network costs 1.1422e10 FLOPs per forward on the
audited 299x299 count. Ten networks over 30 epochs give **1.32e18 FLOPs**, with
4.39e17 to 4.39e18 across the epoch scenario. The tuning split sits inside the
development set and is not separately charged.

The excluded ImageNet pretraining is 3.95e18 FLOPs for one Inception v3, three
times the recorded fine-tune if the ten networks shared one pretrained
checkpoint and thirty times if each had its own. The inference note flags that
the model's input may have been 587x587 rather than 299x299; at that size every
figure here rises by about 3.8 times.

The comparator is the eight US board-certified ophthalmologists who graded
EyePACS-1, whose mean agreement with the panel's positive and negative labels the
model exceeded.

### med-skin-train-esteva

[Esteva et al. (2017)](https://cs.stanford.edu/people/esteva/home/assets/nature_skincancer.pdf)
fine-tunes all layers of an ImageNet-pretrained Inception v3 on 127,463 training
images at 1.1425e10 FLOPs per forward, so the row is `additional_training`. At 30
epochs the run costs **1.31e17 FLOPs**, 4.37e16 to 4.37e17 across the scenario.
The excluded ImageNet pretraining is 3.95e18 FLOPs, thirty times the fine-tune,
which is the largest backbone-to-run ratio in this set.

The paper's own schedule mentions a decay factor of 16 every 30 epochs, so 30
epochs is the shortest run consistent with it and the central is a floor in that
respect. The paper also states that images are augmented by a factor of 720
during training. Read as a presentation count rather than as on-the-fly
transformation, that gives 9.18e7 presentations and 3.15e18 FLOPs, which is the
upper scenario worth naming.

The comparator is the 21 board-certified dermatologists of the 111-image
dermoscopy reader study, whom the model matched.

### med-mammo-train-mckinney

The
[revised supplement](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-020-2679-9/MediaObjects/41586_2020_2679_MOESM1_ESM.pdf)
publishes a step count and a batch size for each of the three branches, so this
row needs no epoch assumption. Every branch is the average of three stochastic
training runs, and parameters were initialized from ImageNet pretraining where
possible, so the row is `additional_training`.

| Branch | Published schedule | Per-case forward | Training FLOPs |
|---|---|---:|---:|
| Case | 50,000 steps, batch 2 | 2.33e12 | 2.09e18 |
| Breast | 120,000 steps, batch 16 | 7.78e12 | 1.34e20 |
| Lesion classifier | 750,000 iterations, batch 4, 5 sampled crops | 2.05e10 | 5.54e17 |
| Detector | assumed 50,000 steps, batch 4 | 1.57e12 | 9.39e17 |

The total is **1.38e20 FLOPs**. The breast branch is 97% of it, because it runs a
ResNet-v2-50 over four 4096x3328 images per case at batch 16 for 120,000 steps.

Two inputs are not published. The RetinaNet detector's own schedule is absent, so
it takes the case model's 50,000 steps at the lesion stage's batch of 4, trained
once rather than three times; at 0.7% of the total the choice barely matters. The
supplement also says the second stage was trained on inputs from a fixed detector
without saying whether those crops were precomputed; if the detector instead ran
online through the second stage's 750,000 iterations it would add 5.6e19 FLOPs,
which is the row's high scenario. The low scenario reads the breast branch's
batch of 16 as images rather than cases, dividing that branch by four for a
3.72e19 total. Head widths and detector details carry the same architecture
assumptions as the inference row.

The excluded ImageNet pretraining is 2.41e18 FLOPs for a ResNet-50, 1.7% of the
run — the one row here where the backbone is a rounding error against the
run it initializes.

The comparator is the six US board-certified radiologists of the enriched US
reader study, all of whom the model exceeded.

### med-ecg-train-hannun

[Hannun et al. (2019)](https://www.nature.com/articles/s41591-018-0268-3) trains
its 34-layer one-dimensional residual network de novo with random initialization,
so the row is `full_training` and this is the only model here with no ImageNet
inheritance. The architecture is exact: 16 residual blocks of two convolutions,
filter width 16, 32 x 2^k filters incrementing every fourth block, subsampling by
two on alternate blocks, over a 30-second single-lead record sampled at 200 Hz,
with a time-distributed 12-class head. `medical_learning_calc.py` builds it as
[the public code](https://github.com/awni/ecg) does and counts 1,627,914,240 MACs,
so 3.256e9 FLOPs per record.

The training set is 91,232 records from 53,549 patients, with a random 10% of
training patients held out as the development set, giving 82,109 training and
9,123 development records. At 30 epochs the run costs **2.50e16 FLOPs**, the
cheapest of the five, with 8.32e15 to 8.32e16 across the epoch scenario.

The comparator is the individual cardiologist annotators: nine
board-certified physicians, eight of them cardiac electrophysiologists, six of
whom annotated each test record individually. The model's average F1 of 0.837
exceeded the cardiologists' 0.780.

This is the dataset's first ECG point of any kind. No inference row exists for
this model.

## Limits

**No source times a cohort to the comparator's accuracy on the paper's own
read.** Each row multiplies a case count documented for one purpose by a rate
measured for another, and only the chest row takes both from the same study.
Rows carry `human_time_evidence = llm_estimate_from_data` because a documented
case count and a measured rate anchor the number, and no human attempt count
exists for the target task.

**The dermoscopy row is read off at a pass mark, not at the comparator's mean.**
Ternov's standard separates competent from not competent, and Esteva's readers
are 21 board-certified dermatologists sitting above it. The measured
experience bands put experienced dermatologists at 85.7% sensitivity and 81.3%
specificity on dermoscopic images against 78.0% and 69.5% for inexperienced
ones, so there is a gap past the pass mark with no case count attached to it.
Four hours is the floor of this set, and the comparator-band reading quantified below puts the gap at 1.8 hours.

**Three of the five case counts are volume standards rather than measurements.**
The MQSA 240, the COCATS 3,000 to 3,500 and the NHS 1,000 a year say what a
programme requires, not what a learner needed. COCATS says so itself: no
threshold number of studies serves as a training landmark.

**Three of five compute cells rest on an assumed epoch count**, which moves them
by a factor of ten in each direction.

## Reproduction

`medical_learning_calc.py` beside this note computes every figure above:

    python3 dataset/research/medical-learning/medical_learning_calc.py \
        agent-work/derived/medical-learning/

Python 3 standard library only. It writes `calculations.json` and asserts its
recomputed component MAC counts against the retained inference ledger.
