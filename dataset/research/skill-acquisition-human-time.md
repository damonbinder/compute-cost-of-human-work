# Human learning time for the skill-acquisition rows

*Created 2026-09-14 14:12.*

*Last revised 2026-09-17 11:41.*

Twenty-one `skill_acquisition` rows had a human time that answered the wrong
question. Each estimated the hours a person would need to move a benchmark score
from the base model's number to the adapted model's number, which is a
test-preparation quantity with no published measurement behind it. This note
replaces all twenty-one with the active hours a learner needs to reach the
capability the training run demonstrably bought, read off a published
hours-to-proficiency table and credited with the starting point the base model
already had. The compute side is untouched.

## Summary

**One method, three tables.** Map the demonstrated score to a point on a
proficiency scale; read the cumulative active hours to that point from a
published hours-to-proficiency table for that skill and population; do the same
for the base model's score; charge the difference. The scale and the table differ
by domain — FSI and HABE hours against CEFR bands for the adult second-language
rows, a practice curve through the Rainfall Problem cohorts for the programming
rows, and measured daily language-interaction hours against developmental age for
the child first-language rows —but the three steps are the same everywhere, and within each
group every row goes through the same arithmetic with no per-row judgment.

**The adult language rows move by factors of one to eight, the code rows by one to
three, and the child grammar rows by three to a hundred.** The child rows move most
because the earlier estimates charged a second-language learner's course budget to
a process that runs for years. They are still active learning time, on the same
accounting as every other row: a child's hours of actual language interaction, not
the waking hours those interactions are spread across.

| Point | Capability the run bought | Old hours | New hours | Table |
|---|---|---:|---:|---|
| `lang-xfer-ja-swallow7b` | Read everyday written Japanese, partial comprehension | 100 | 310 | FSI / HABE |
| `lang-xfer-ja-swallow70b` | Read everyday written Japanese, near-native | 60 | 510 | FSI / HABE |
| `lang-xfer-ar-acegpt7b-base` | Read Modern Standard Arabic, minimal | 60 | 99 | FSI / HABE |
| `lang-xfer-ar-acegpt13b-base` | Read academic Modern Standard Arabic, elementary | 100 | 170 | FSI / HABE |
| `lang-xfer-et-llammas-base` | Read short Estonian factual passages, elementary | 150 | 220 | FSI / HABE |
| `lang-xfer-eu-latxa13b` | Read written Basque, lower intermediate | 500 | 580 | FSI / HABE |
| `lang-xfer-eu-latxa70b` | Read written Basque, intermediate | 1,000 | 1,200 | FSI / HABE |
| `agen-codexfer-codex300m` | Write short correct Python functions, 13.2% first-submission | 35 | 95 | Rainfall |
| `agen-codexfer-codex2p5b` | Write short correct Python functions, 21.4% first-submission | 70 | 150 | Rainfall |
| `agen-codexfer-codex12b` | Write short correct Python functions, 28.8% first-submission | 110 | 190 | Rainfall |
| `agen-codexfer-codellama7b` | Write short correct Python functions, 33.5% first-submission | 90 | 130 | Rainfall |
| `agen-codexfer-codellama34b` | Write short correct Python functions, 48.8% first-submission | 140 | 150 | Rainfall |
| `agen-codexfer-kotlin7b` | Write short correct Kotlin functions, 42.2% first-submission | 8 | 19 | Rainfall |
| `agen-codexfer-mplt-ocaml1b` | Write short correct OCaml functions, 9.7% first-submission | 10 | 12 | Rainfall |
| `agen-codexfer-mplt-ocaml15b` | Write short correct OCaml functions, 19.9% first-submission | 20 | 17 | Rainfall |
| `agen-codexfer-mplt-racket15b` | Write short correct Racket functions, 21.0% first-submission | 12 | 12 | Rainfall |
| `lang-lacq-blimp-lstm` | English grammatical competence of a 3.6-year-old | 900 | 2,500 | interaction hours |
| `lang-lacq-zorro-babyberta` | English grammatical competence of a 7.1-year-old | 40 | 4,900 | interaction hours |
| `lang-lacq-blimp-gptbert10m` | English grammatical competence of a 7.5-year-old | 1,600 | 5,200 | interaction hours |
| `lang-lacq-blimp-elcbert100m` | English grammatical competence of a 9.7-year-old | 2,400 | 6,700 | interaction hours |
| `lang-lacq-blimp-gptbert100m` | English grammatical competence of a 10.2-year-old | 2,400 | 7,100 | interaction hours |

Hours are rounded to two significant figures; `points.csv` carries the rounded
hours in seconds. Every row keeps `performance_vs_human=match`: the human target
is still the model's demonstrated endpoint, now expressed as a capability rather
than as a score.

## What was wrong with the old quantity

A continued-pretraining run is a targeted run — Swallow's hundred billion tokens
buy Japanese, Code Llama's five hundred billion buy programming — so the compute
cell is defensible. The human cell was not. It asked how long a person would take
to raise a JCommonsenseQA score from 38.5% to 48.1%, or an Arabic MMLU score by
2.7 points, and no learning study measures that. The estimates were therefore
course-sized budgets chosen by judgment and attached to score deltas, with the
odd result that two rows measuring the same skill to different levels could carry
the same hours, and that a 2.7-point move on a translated multiple-choice test
carried sixty hours on no evidence at all.

The quantity that does have published measurements behind it is hours to a stated
proficiency. Language ministries and foreign-service schools publish it; computing
education measures program-writing performance at known amounts of instruction;
child development measures waking hours and language input directly. Reading the
model's demonstrated score as a proficiency, and charging the hours to that
proficiency net of the base model's starting point, puts the human side on
measured ground.

## Method

Three steps, applied identically within each group.

1. **Score to proficiency.** Convert the adapted model's reported score to a
   position on a proficiency scale by a stated rule that uses no per-row judgment.
2. **Proficiency to cumulative hours.** Read the cumulative active learning hours
   to that position from a published table.
3. **Credit the starting point.** Do the same for the base model's score on the
   same benchmark and subtract. A model with prior exposure is not a zero-start
   learner, and neither is the human it is compared against: the comparison charges
   only the hours between the two proficiencies, exactly as the compute cell charges
   only the adaptation run and not the base model's pretraining.

### Table L — adult second-language reading

**Score to proficiency.** For a multiple-choice benchmark with chance floor `q`,
the comprehension fraction is `c = (score − q)/(1 − q)`, clamped below at zero: the
share of the test the reader commands beyond guessing. CEFR levels are placed on
`c` at 0.10 (A1), 0.25 (A2), 0.45 (B1), 0.65 (B2), 0.85 (C1) and 1.00 (C2), and `c`
is treated as continuous between them. This correspondence is the method's main
stipulation. It rests on the CEFR reading descriptors being themselves statements
about how much of a text distribution a reader handles — A1 recognizes familiar
words, B1 handles mainly high-frequency language, C1 handles long complex factual
text — and on nothing more precise than that.

**Proficiency to hours.** Cumulative guided learning hours by level come from the
[Cambridge English guided learning hours](https://support.cambridgeenglish.org/hc/en-gb/articles/202838506-Guided-learning-hours)
table, taken at its midpoints: 95 (A1), 190 (A2), 375 (B1), 550 (B2), 750 (C1) and
1,100 (C2). Those hours describe a Category-I-difficulty language. Scale them for
the target language by the ratio of that language's hours to professional
proficiency to the Category-I figure, from the
[FSI foreign language training table](https://web.archive.org/web/2023/https://www.state.gov/foreign-language-training/),
whose figures are what FSI has observed as the average time its students take to
reach ILR Speaking-3/Reading-3:

| Language | FSI category | Class hours to ILR-3 | Scale factor |
|---|---|---:|---:|
| Japanese | IV | 2200 | 2.93 |
| Arabic | IV | 2200 | 2.93 |
| Estonian | III | 1100 | 1.47 |
| Basque | — | 2250 | 3.00 |

The scale factor is class hours divided by 750, the Cambridge C1 midpoint; ILR-3 is
treated as the C1 rung. FSI's own Category I figure of 600–750 class hours agrees
with that midpoint to within a tenth, which is the one place the two tables can be
checked against each other. Basque is not an FSI language; its 2,250 hours are the
cumulative A1-to-C1 planning load in
[HABE's curriculum](https://www.habe.euskadi.eus/curriculo-basico-de-ensenanza-de-euskera-a-personas-adultas-heoc/webhabe00-edukiak/es/),
already established in the Latxa note.

The unit is Cambridge's guided learning hours, and Cambridge defines those as
learning in a classroom or as part of a programme, including homework and other
directed language-learning activity; only unguided private study sits outside
them. An earlier version of this note read them as class hours only and doubled
them for homework on that basis, which was wrong, so that upper scenario goes.
What is left is the score-to-CEFR placement, a stipulation with no measured
dispersion to read a bound off, and the FSI scale factor, whose one checkable
point—FSI's 600 to 750 class hours for Category I against Cambridge's 700 to 800
guided hours at C1—constrains the bridge rather than the method. The seven Table L
rows therefore assert no bounds.

Reviewed again on 2026-09-17, and the invariance is now arithmetic rather than an
assertion. Cambridge publishes its guided learning hours as bands, 90-100 at A1,
180-200 at A2, 350-400 at B1, 500-600 at B2, 700-800 at C1 and 1,000-1,200 at C2,
so the midpoints could in principle be moved to the band ends. But a row's hours are
`H(level) x FSI / H(C1)`, and the C1 band is the divisor, so what matters is the
ratio `H(level) / H(C1)` at each end of the table:

| Level | Low ends | Midpoints | High ends | Spread |
|---|---:|---:|---:|---:|
| A1 | 0.1286 | 0.1267 | 0.1250 | 2.8% |
| A2 | 0.2571 | 0.2533 | 0.2500 | 2.8% |
| B1 | 0.5000 | 0.5000 | 0.5000 | 0% |
| B2 | 0.7143 | 0.7333 | 0.7500 | 5.0% |
| C2 | 1.4286 | 1.4667 | 1.5000 | 5.0% |

Reading the whole Cambridge table at its band ends moves a row's hours by at most
2.5% either way, and by nothing at all at B1. A bar of that width would be a fake
bar: it would understate the real uncertainty rather than carry it. The second check
is the units. FSI's figure is class hours while Cambridge's includes homework and
other directed activity, which would make the scale factor's numerator too small; the
note's one cross-check, FSI's 600-750 Category I class hours against Cambridge's
700-800 guided hours at C1, says the two units are empirically close, so there is
nothing to read a bound off there either. What is left is the score-to-CEFR
placement, and no source puts a dispersion on it. These seven stay blank pending
either a measured placement or Damon's ruling that a stipulation may carry a bar.

**The A1 and A2 midpoints were wrong and are now corrected.** Until 2026-09-17 the
hours row above took 70 at A1 and 180 at A2, against published bands of 90-100 and
180-200 whose midpoints are 95 and 190; the other four levels always matched. The
row now carries 95 and 190, and the five rows whose base or adapted score falls at
or below B1 are recomputed below. The two rows that sit entirely above B1 —
`lang-xfer-ja-swallow70b`, and `lang-xfer-eu-latxa70b`, which starts at zero
comprehension and so charges the whole ladder up to a B1-to-B2 endpoint — are
untouched, because the ladder is piecewise linear and neither row's endpoints
interpolate against the A1 or A2 anchors.

### Table P — learning to write short correct functions

*Rebuilt 2026-09-16. The construction this replaces is recorded at the end of this
section.*

**Score to proficiency.** HumanEval pass@1 is itself the proficiency coordinate.
There is no chance floor to subtract: no guessing strategy passes hidden tests.

**The anchors.** The Rainfall Problem is the one short-function task that has been
set to cohorts of programming students often enough to have a distribution behind
it. A student is given a short specification with worked examples and writes one
function or short program that reads a stream of daily measurements, stops at a
sentinel, discards negative values, and reports the average or says it cannot be
computed; the solution is graded correct only if all six subgoals work.
[Seppälä et al. (2015)](https://dl.acm.org/doi/10.1145/2828959.2828963) survey every
published study that reports a success rate on it and add three cohorts of their
own, and their Table 2 is the input here.

Twenty of their cohorts sat the problem at or near the end of a first programming
course. Their fully-correct rates are 0, 2, 2, 5, 11, 11, 12, 14, 15, 19, 20, 20,
24, 31, 39, 39, 45, 53, 54 and 72 per cent, over 1,525 students: **median 19.5%,
quartiles 11% and 39%**. Three cohorts sat it after a second course — 36% and 61% in
[Soloway et al. (1983)](https://dl.acm.org/doi/10.1145/182.358436)'s two Pascal
groups and 42% for their 1982 intermediates, over 155 students — for a **median of
42%**. Within the two studies that ran both levels the second course multiplied the
rate by 2.57, 2.54 and 1.08; the two pooled medians give 2.15, which is the figure
used.

| Anchor | Task and protocol | Cohorts | Students | Cumulative hours | Pass rate |
|---|---|---:|---:|---:|---:|
| End of one programming course | Rainfall, fully correct on all six subgoals | 20 | 1,525 | 135 | 19.5 |
| End of a second course | Same, same scoring | 3 | 155 | 270 | 42.0 |

**How the anchors map to HumanEval's protocol.** Rainfall in its recent form is a
function variant: the student is handed a specification and two worked example runs
and writes one function, which is the HumanEval shape. Two differences run in
opposite directions. Rainfall is graded on six subgoals at once, and the
empty-input corner case is the most-missed of them, so it is harder than
a median HumanEval item and the anchor places students lower on the HumanEval axis
than they belong. Against that, most of the cohorts could run their code before
submitting — Seppälä's Context 3 had automated tests in front of it and reached 72%,
Context 2 was a take-home with internet access and reached 53% — where HumanEval
pass@1 is one submission with no execution, so the anchor places them higher than
they belong. Seppälä's Context 1 is the cohort closest to HumanEval's conditions:
unaided, no textbook, no internet, no tests, about an hour, near the end of the
course, 45%. The dispersion these conditions generate is not noise around a true
value; it is the reason the rows carry a wide range rather than a bound read off a
standard error.

**Hours.** A first programming course is **135 student-hours**: three credits at the
[Carnegie credit hour](https://en.wikipedia.org/wiki/Carnegie_Unit_and_Student_Hour)'s
three student hours a week over a fifteen-week semester. The European cohorts agree
by a different route, since a five-credit ECTS course is 125 to 150 hours of student
work. A second course doubles it to 270. The unit is the whole course budget —
lectures, labs, reading and assignments — on the same accounting as Table L's guided
learning hours.

**The curve.** Practice curves are conventionally power laws, so take
`pass rate = C · hours^β` through the two anchors. The second course multiplying the
rate by 2.15 over a doubling of hours gives **β = 1.107** and **C = 8.549 × 10⁻⁴**,
so hours to a pass rate `p` are `(p/0.0008549)^0.9033`.

β above one means accelerating returns, and the curve therefore cannot be run far
past its anchors: extended, it reaches 100% at 591 hours, which is false. It is
asserted only over the range the anchors bracket and the rows use, pass rates below
50% and cumulative hours below 320. Every endpoint in Table P sits inside that
range, the highest being Code Llama 34B's 48.8% at 309 hours. No professional or
expert anchor enters the construction, because no row needs one.

**The range.** The nine rows' bounds come from the quartiles of the twenty
first-course cohorts. Refitting the same curve with the first-course anchor at 39%
instead of 19.5% — a fast cohort, the second course still multiplying by 2.15 —
gives `C = 1.710 × 10⁻³` and puts every endpoint and every increment at 0.53 of the
central. Refitting at 11% gives `C = 4.823 × 10⁻⁴` and 1.68 times the central. Those
two refits are `human_time_low` and `human_time_high`. What the range does not carry
is the exponent: β rests on three within-study CS1-to-CS2 comparisons whose ratios
span 1.08 to 2.57, and moving it instead of the level would reorder the rows rather
than scale them.

**Transfer credit.** Table P describes someone acquiring programming through the
assessed language. Four rows assess a language the learner is transferring into —
Kotlin, OCaml and Racket, from Python or Java — and for them the general
problem-solving component of the ladder is already held and only the
language-specific component is charged. That component is set at **one fifth** of
the ladder's hours, from the scale of the transfer teaching the
[code learning note](code-learning/human-learning.md) documents: UW CSE413 covers
Racket basics in five scheduled contact hours for students who already program, and
Cornell CS3110's warmup of three documented OCaml functions took a mean 6.4 hours
with a standard deviation of 3.4. It is an assumption, not a measurement, but the
rebuild makes it agree with those two anchors where the old construction did not:
the four transfer rows now charge 12 to 19 hours, against the 65 hours the old curve
charged the Kotlin row. The five Python rows take no credit, because their learner
is learning Python.

**Superseded: the ITiCSE 2001 construction.** Until 2026-09-16 Table P ran through
[McCracken et al. (2001)](https://kar.kent.ac.uk/13514/4/a_multinational_ulti-institutional_mccracken.pdf)
at 200 hours and 20.8%, and a judgment point at 2,000 hours and 90%, giving
β = 0.636 and hours of 97, 210, 330, 340, 540, 65, 11, 30 and 24. Damon withdrew it
on two defects. The measured anchor was the wrong task: McCracken's students wrote a
whole calculator program in 60 or 90 minutes, scored out of 110 on a rubric, and
placing that 20.8% on the HumanEval axis stretched every increment above it. And the
upper anchor was a judgment with no evidence, which set the slope through exactly the
range where Code Llama 34B and the Kotlin row sat. McCracken survives as a
cross-check rather than an anchor: a harder task at more hours returning the same
20.8% is what the new curve predicts, since 200 hours of the new curve reaches 30% on
Rainfall and the calculator rubric is the harsher scorer.

### Table C — child first-language grammar

**Score to developmental stage.** BLiMP's published individual native-speaker
agreement is 88.6% and chance is 50%, so `a = (score − 50)/38.6` is the fraction of
adult native grammatical competence the model demonstrates. Grammatical competence
grows fast early and slowly late, so take it linear in log age from the one-word
stage at 1;0 to adult level at 12;0: **age = 12^a**. Twelve is where the
acquisition literature puts adult-like judgment across this range of constructions —
[tense-marking judgments keep rising from 5 to 18](https://pubs.asha.org/doi/10.1044/2023_JSLHR-22-00507),
and
[negative polarity comprehension is still not target-like at 11 to 12](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8660713/),
while agreement, word order and anaphora are in place years earlier.

The rule is mechanical, and the ages it returns can be checked against the category
profiles the derivation notes already record. It puts the LSTM at 3.6 years, which
is a model at chance on islands and negative polarity with solid agreement and
anaphora; GPT-BERT small at 7.5 years, strong on local agreement and polarity with
binding, island and quantifier gaps; and the two 100M models near 10 years,
reliable across most categories with binding and quantifiers still weakest. Those
are the right milestones for those ages, which is a genuine check because nothing
in the mapping used them.

**What counts as active learning time for a child: 1.9 hours a day.** Human time in
this dataset is active, task-specific learning time, so the hours charged here are
the hours a child spends in language interaction, not the waking hours those
interactions are spread across. The daily figure comes from
[Gilkerson et al. (2017)](https://pubs.asha.org/doi/10.1044/2016_AJSLP-15-0169),
3,213 twelve-hour daylong recordings from 329 families with children aged 2 to 48
months. Their measured daily averages are **12,700 adult words** spoken in the
child's presence and **1,817 child vocalizations**. Adult words convert to speech
time at the
[National Center for Voice and Speech's 150 words a minute](https://virtualspeech.com/blog/average-speaking-rate-words-per-minute)
for conversational US English, giving 1.41 hours a day of adult speech; the child's
own vocalizations at a second each add 0.51. **1.9 hours a day** is the sum, about a
seventh of a toddler's waking day.

The rate is held constant across childhood. Gilkerson reports adult word counts to
be age independent after early infancy and child vocalizations to plateau around 26
months, which supports holding it through the preschool years; for school-age
children it is conservative, since school, reading and peers add language the
infant recordings never saw. Restricting the count to strictly child-directed
speech would lower it, and Hart and Risley's professional families, at about 2,150
words an hour addressed to the child, would raise it; 1 and 3 hours a day are the
scenarios. Those two rates give the five Table C rows their range: 1,300 and 3,900
hours for the LSTM, 2,600 and 7,700 for BabyBERTa, 2,700 and 8,200 for GPT-BERT
small, 3,500 and 11,000 for ELC-BERT, and 3,700 and 11,000 for GPT-BERT base, each
rounded to two significant figures as the centrals are.

**Stage to hours.** 1.9 hours a day from birth to the mapped age, or 694 hours a
year. No starting-point credit is subtracted: these models train from random
initialization and the child starts from birth, so both sides begin with nothing.

As a scale check, the accounting implies about 60 million words heard by age 13,
against the roughly 100 million the BabyLM organizers attribute to a 13-year-old.
The gap is the school-age input Gilkerson's infant recordings do not cover, and it
says the daily rate errs low rather than high.

## Limits

**The score-to-proficiency step is the weak leg everywhere.** No cohort has been
timed to any of these benchmark scores. Table L's CEFR placement and Table C's
log-age curve are stipulations chosen to be monotone, uniform and checkable against
known milestones, not fitted to data. Table P is the one of the three fitted to
measurements, and what it is fitted to is a different task under a different
protocol.

**Two rows sit where their benchmark carries almost no signal.** The Arabic MMLU
moves are 2.7 and 6.7 points on a test whose own audit found 9.5% of its scored
weight occupied by corrupted duplicate items, and both endpoints are close enough
to the 25% floor that the comprehension fraction is small and noisy. The estimates
are still the correct ones under this method; they are the least constrained.

**Zorro has no human ceiling.** BabyBERTa's 80.5% is scored against BLiMP's adult
agreement because the Zorro paper itself proposes that comparison and collected no
human judgments of its own. Zorro uses child vocabulary and is the easier suite, so
if its native ceiling is above BLiMP's, that row's age and hours are overstated.

**The child rows' daily rate is measured on infants and toddlers only.** Gilkerson's
recordings stop at 48 months, and four of the five rows map to ages beyond that.
Holding 1.9 hours a day constant to age 10 is an extrapolation; the direction of the
error is toward understatement, because school-age language interaction is greater
than a toddler's, not less.

**Table P's exponent rests on three comparisons.** The two anchors fix the level
well — 1,525 students at the first and 155 at the second —but the slope between
them comes from the two studies that ran both course levels, whose within-study
ratios are 2.57, 2.54 and 1.08. The range does not carry that spread, and a
measured cohort somewhere between one course and professional practice would
constrain the rows more than anything else here.

**Table P's unit is the whole course budget.** 135 hours counts lectures, labs,
reading and assignments, consistent with Table L's guided learning hours. The
narrower reading, hands-on programming only, would be roughly a third of it: the
dataset's own [Python Grids](https://link.springer.com/article/10.1186/s41039-018-0085-9)
figure is 46.6 hours of self-reported exercise effort for a comparable course. That
is a definition the note settles rather than an uncertainty it carries, so it is
here and not in the bounds.

**No row in Table P is anchored above 50%.** Nothing in this dataset measures how
long it takes a person to pass most of HumanEval first submission without running
anything, and the rebuilt table no longer asserts it. A skill-acquisition row whose
model passes more than about half would need an anchor this note does not have.

**Table L's unit already includes homework.** Cambridge counts homework and other
directed activity inside its guided learning hours, so the adult language rows are
not conservative in the way an earlier version of this note claimed.

## Rows

### lang-xfer-ja-swallow7b

**310 active hours = 1,116,000 seconds.** Table L, Japanese, scale factor 2.93. The benchmark's chance floor is 20%; the base model scores 38.50% and the adapted model 48.10%, giving comprehension fractions 0.231 and 0.351. Those place the starting point at 523 cumulative hours and the endpoint at 832; the difference is 310, rounded to 310.

### lang-xfer-ja-swallow70b

**510 active hours = 1,836,000 seconds.** Table L, Japanese, scale factor 2.93. The benchmark's chance floor is 20%; the base model scores 86.90% and the adapted model 93.50%, giving comprehension fractions 0.836 and 0.919. Those place the starting point at 2,160 cumulative hours and the endpoint at 2,671; the difference is 511, rounded to 510.

### lang-xfer-ar-acegpt7b-base

**99 active hours = 356,400 seconds.** Table L, Arabic, scale factor 2.93. The benchmark's chance floor is 25%; the base model scores 29.47% and the adapted model 32.14%, giving comprehension fractions 0.060 and 0.095. Those place the starting point at 166 cumulative hours and the endpoint at 265; the difference is 99, rounded to 99.

### lang-xfer-ar-acegpt13b-base

**170 active hours = 612,000 seconds.** Table L, Arabic, scale factor 2.93. The benchmark's chance floor is 25%; the base model scores 33.76% and the adapted model 40.45%, giving comprehension fractions 0.117 and 0.206. Those place the starting point at 310 cumulative hours and the endpoint at 476; the difference is 166, rounded to 170.

### lang-xfer-et-llammas-base

**220 active hours = 792,000 seconds.** Table L, Estonian, scale factor 1.47. The benchmark's chance floor is 25%; the base model scores 22.95% and the adapted model 39.34%, giving comprehension fractions 0.000 and 0.191. Those place the starting point at 0 cumulative hours and the endpoint at 224; the difference is 224, rounded to 220.

### lang-xfer-eu-latxa13b

**580 active hours = 2,088,000 seconds.** Table L, Basque, scale factor 3.00. The benchmark's chance floor is 25%; the base model scores 25.90% and the adapted model 45.02%, giving comprehension fractions 0.012 and 0.267. Those place the starting point at 34 cumulative hours and the endpoint at 617; the difference is 583, rounded to 580.

### lang-xfer-eu-latxa70b

**1,200 active hours = 4,320,000 seconds.** Table L, Basque, scale factor 3.00. The benchmark's chance floor is 25%; the base model scores 24.16% and the adapted model 60.61%, giving comprehension fractions 0.000 and 0.475. Those place the starting point at 0 cumulative hours and the endpoint at 1,190; the difference is 1,190, rounded to 1,200.

### agen-codexfer-codex300m

**95 active hours = 342,000 seconds.** Table P. The adapted model passes 13.2% first submission, which the curve puts at 94.7 cumulative hours. The base model writes essentially no correct solutions, so the whole ladder is charged. The increment is 94.7 hours. Rounded to 95, with 51 and 160 from the fast-cohort and slow-cohort refits.

### agen-codexfer-codex2p5b

**150 active hours = 540,000 seconds.** Table P. The adapted model passes 21.4% first submission, which the curve puts at 146.6 cumulative hours. The base model writes essentially no correct solutions, so the whole ladder is charged. The increment is 146.6 hours. Rounded to 150, with 78 and 250 from the fast-cohort and slow-cohort refits.

### agen-codexfer-codex12b

**190 active hours = 684,000 seconds.** Table P. The adapted model passes 28.8% first submission, which the curve puts at 192.1 cumulative hours. The base model writes essentially no correct solutions, so the whole ladder is charged. The increment is 192.1 hours. Rounded to 190, with 100 and 320 from the fast-cohort and slow-cohort refits.

### agen-codexfer-codellama7b

**130 active hours = 468,000 seconds.** Table P. The adapted model passes 33.5% first submission, which the curve puts at 220.1 cumulative hours. The base model passes 12.2%, worth 88.4 cumulative hours, which is credited. The increment is 131.7 hours. Rounded to 130, with 70 and 220 from the fast-cohort and slow-cohort refits.

### agen-codexfer-codellama34b

**150 active hours = 540,000 seconds.** Table P. The adapted model passes 48.8% first submission, which the curve puts at 309.2 cumulative hours and is the highest endpoint the table asserts. The base model passes 22.6%, worth 154.2 cumulative hours, which is credited. The increment is 155.0 hours. Rounded to 150, with 83 and 260 from the fast-cohort and slow-cohort refits.

### agen-codexfer-kotlin7b

**19 active hours = 68,400 seconds.** Table P. The adapted model passes 42.2% first submission, which the curve puts at 271.4 cumulative hours. The base model passes 26.1%, worth 175.6 cumulative hours, which is credited. The increment is 95.8 hours. The learner already programs in another language, so the one-fifth language-specific share applies: 19.2 hours. Rounded to 19, with 10 and 32 from the fast-cohort and slow-cohort refits.

### agen-codexfer-mplt-ocaml1b

**12 active hours = 43,200 seconds.** Table P. The adapted model passes 9.7% first submission, which the curve puts at 71.8 cumulative hours. The base model passes 1.5%, worth 13.3 cumulative hours, which is credited. The increment is 58.5 hours. The learner already programs in another language, so the one-fifth language-specific share applies: 11.7 hours. Rounded to 12, with 6.3 and 20 from the fast-cohort and slow-cohort refits.

### agen-codexfer-mplt-ocaml15b

**17 active hours = 61,200 seconds.** Table P. The adapted model passes 19.9% first submission, which the curve puts at 137.5 cumulative hours. The base model passes 6.9%, worth 52.8 cumulative hours, which is credited. The increment is 84.7 hours. The learner already programs in another language, so the one-fifth language-specific share applies: 16.9 hours. Rounded to 17, with 9.1 and 28 from the fast-cohort and slow-cohort refits.

### agen-codexfer-mplt-racket15b

**12 active hours = 43,200 seconds.** Table P. The adapted model passes 21.0% first submission, which the curve puts at 144.3 cumulative hours. The base model passes 11.8%, worth 85.8 cumulative hours, which is credited. The increment is 58.5 hours. The learner already programs in another language, so the one-fifth language-specific share applies: 11.7 hours. Rounded to 12, with 6.3 and 20 from the fast-cohort and slow-cohort refits.

### lang-lacq-blimp-lstm

**2,500 active hours = 9,000,000 seconds.** Table C. The model scores 69.8%, which is 0.513 of adult native agreement above chance and so a developmental age of 3.6 years. At 1.9 hours of language interaction a day that is 2,481 hours, rounded to 2,500.

### lang-lacq-zorro-babyberta

**4,900 active hours = 17,640,000 seconds.** Table C. The model scores 80.5%, which is 0.790 of adult native agreement above chance and so a developmental age of 7.1 years. At 1.9 hours of language interaction a day that is 4,940 hours, rounded to 4,900.

### lang-lacq-blimp-gptbert10m

**5,200 active hours = 18,720,000 seconds.** Table C. The model scores 81.2%, which is 0.808 of adult native agreement above chance and so a developmental age of 7.5 years. At 1.9 hours of language interaction a day that is 5,168 hours, rounded to 5,200.

### lang-lacq-blimp-elcbert100m

**6,700 active hours = 24,120,000 seconds.** Table C. The model scores 85.3%, which is 0.915 of adult native agreement above chance and so a developmental age of 9.7 years. At 1.9 hours of language interaction a day that is 6,729 hours, rounded to 6,700.

### lang-lacq-blimp-gptbert100m

**7,100 active hours = 25,560,000 seconds.** Table C. The model scores 86.1%, which is 0.935 of adult native agreement above chance and so a developmental age of 10.2 years. At 1.9 hours of language interaction a day that is 7,085 hours, rounded to 7,100.

## Reproduction

`skill-acquisition-human-time.py` beside this note computes all three tables and every figure above from
the anchors stated here. Python 3 standard library only, no inputs beyond the
published scores; it prints hours and seconds per point.
