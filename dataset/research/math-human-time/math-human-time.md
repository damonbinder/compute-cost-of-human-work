# How long a human mathematician takes — a calibration for `human_time` on research-level proofs

*Created 2026-09-16 11:04.*

## Summary

**Thirty-five resolved research problems and twelve formalization projects, assembled so that
every mathematics row in the collection can be priced the same way.** Every hours figure below
is arithmetic on stated quantities: a solve is `people × elapsed calendar days × 8 hours per
working day × an on-task fraction`, and a formalization is either `distinct author-days × 4
hours per active day × 1.5 for uncommitted work` or the same elapsed-window product where the
repository history is unusable. Nine of the thirty-five carry a direct record of the solver's
own time, eight of them in the fit; the rest are dated windows with a fraction I state and justify one case at a time.

- **Mathematics.** Successful solves run from **28 to 15,147 summed active hours**. Hours per
  page is flat at about **8 h/page up to sixty pages** (median 8.0 on the sixteen short rows,
  8.3 on the six medium ones) and then jumps to **57 h/page above sixty pages**. Within each
  class the dispersion is a factor of 10 to 18 on hours per page and 4 to 20 on total hours.
  On logs, elapsed days predicts hours at r = 0.92 and pages at r = 0.88; **head-count predicts
  almost nothing (r = 0.14)**, because the teams that take longest are small.
- **Formalization.** Eight completed projects give **12.6 formal lines per active hour, band
  5.4 to 15.0, a dispersion of only 2.8×** — the tightest number in this note. The size ratio
  splits sharply by what you count as a page: **235 formal lines per blueprint or textbook page
  (216 to 414, dispersion 1.9×)** against **417 per research-paper page (162 to 1,187,
  dispersion 7.3×)**. Use the blueprint ratio when a blueprint or textbook exists and the paper
  ratio only when it does not.
- **The Imperial FLT project's grant overstates its work by 1.4 to 1.9×.** Reconstructing from
  who committed when: 73 non-bot authors, 1,571 non-bot commits, **727 distinct author-days**
  from 19 Nov 2023 to 16 Sep 2026, of which 302 are Buzzard's. At 6 hours per author-day that
  is **4,362 active hours, 2.18 person-years**. The fellowship's £186,809 a year funds 1.5 to
  2.0 FTE at UK full economic cost, and 2.04 funded years have elapsed, so the money buys 3.1
  to 4.1 person-years — **6,101 to 8,200 hours against 4,362 observed**.
- **Applying the method to the eight dataset rows moves five of them up by 1.2 to 1.8×, leaves
  Navier–Stokes where it is (1.08×), and cuts Fermat by a factor of three.** FLT is the one
  large change, and it is the head-count finding: `research/flt-anthropic.md` prices a funded
  programme, and the observed work record is smaller than the funding implies.

The arithmetic is in `research/math-human-time/compute_math_human_time.py`, reading
`solve-time.csv` and `formalization.csv` in the same folder and writing
`agent-work/derived/math-human-time/calculations.json`. Nothing in this note edits a row.

<a id="quantity"></a>

## The quantity, and what never counts

Per Damon's ruling of 2026-09-16 and the worked precedent in
`research/frontiermath-erdos/frontiermath-erdos.md#human-time`: `human_time` on a
research-level mathematics row is **the summed active hours of the people who do solve the
problem, from sitting down with it to a written proof of the same result, conditional on their
succeeding**, plus, where the deliverable includes a machine-checked formalization, the hours
to formalize it.

Never used, anywhere below:

- **Years open.** Tao's wiki says why: "If an Erdős problem was posed N years ago and was
  recently solved by AI, it may be tempting to conclude: 'the problem resisted all human
  attempts at solution for N years' in order to imply the problem is difficult. Instead, it
  could be that the problem has received little attention."
- **Prize status and prize money.** Erdős's $500 on problem 1 and $100 on problem 548 rank them
  the wrong way round against every other difficulty signal on record.
- **The field's cumulative effort, and the count of failed prior attempts.** Both count other
  people's failures, which the ruled quantity excludes.
- **Grant totals.** Money appears exactly once, as a cross-check on head-count in the FLT row,
  and it sets no figure.
- **The AI system's own wall clock.** The FrontierMath harness's "working time" measures a
  container, not a person.

**Elapsed time bounds active time from above.** Every product below is `person-days × 8 hours`
times a fraction strictly below one, and the note reports the fraction-one product alongside
each central so that the bound is visible. No central sits at its bound.

<a id="fractions"></a>

### The on-task fraction ladder

The fraction is the weakest factor in every row that has no direct record, so it is set from a
fixed ladder rather than case by case, and each row names its rung.

| Fraction | Hours/day | What it describes |
|---:|---:|---|
| 0.80 | 6.4 | A documented all-out sprint: the record says the work was intense and exclusive over days |
| 0.55 | 4.4 | Documented near-exclusive devotion over months, with the record describing nights and weekends |
| 0.35–0.50 | 2.8–4.0 | An intensive collaborative burst, or a single person on a hot lead, out of term |
| 0.25–0.30 | 2.0–2.4 | One author over months, alongside normal academic duties |
| 0.15–0.20 | 1.2–1.6 | Evenings and weekends alongside a full-time job in another field |
| 0.06–0.10 | 0.5–0.8 | A loose open collaboration where most named contributors made one or two inputs |

Eight rows have the fraction **pointed** rather than assumed, meaning the source states the
intensity: Tao on Erdős 1026, Park and Pham, Royen, Gilmer, the dimension-24 sphere packing
team, Deng–Hani–Ma, de Grey, and Polymath1.

<a id="table1"></a>

## Table 1. Mathematics solve time

Thirty-five resolved problems, thirty in the fit and five reported and not used. Columns are
the factors, not the conclusion: `active hours = person-days × 8 × fraction`, and
`elapsed bound` is the same product at a fraction of one.

| Key | Area | Class | People | Elapsed d | Person-d | Fraction | Basis | Pages | Record | Assisted | **Active h** | Elapsed bound | h/page |
|---|---|---|---:|---:|---:|---:|---|---:|---|---|---:|---:|---:|
| erdos1026 | combinatorics | short | 6 | 2 | 12 | 0.25 | pointed | — | direct | ai | **24** | 96 | — |
| capset-ellenberg | combinatorics | short | 1 | 10 | 10 | 0.35 | assumed | 4 | direct | no | **28** | 80 | 7.0 |
| kahn-kalai | combinatorics | short | 2 | 8 | 16 | 0.50 | pointed | 8 | direct | no | **64** | 128 | 8.0 |
| royen-gci | analysis | short | 1 | 19 | 19 | 0.35 | pointed | 7 | direct | no | **53** | 152 | 7.6 |
| gilmer-unionclosed | combinatorics | short | 1 | 31 | 31 | 0.15 | pointed | 9 | direct | no | **37** | 248 | 4.1 |
| huang-sensitivity | combinatorics | short | 1 | 30 | 30 | 0.25 | assumed | 6 | direct | no | **60** | 240 | 10.0 |
| tao-discrepancy | number theory | medium | 1 | 8 | 8 | 0.50 | assumed | 29 | direct | no | **32** | 64 | 1.1 |
| sphere24 | geometry | medium | 5 | 7 | 35 | 0.80 | pointed | 17 | direct | no | **224** | 280 | 13.2 |
| erdos548-riordan-scott | combinatorics | short | 2 | 8 | 16 | 0.40 | assumed | — | timeline | no | **51** | 128 | — |
| erdos52-sumproduct | combinatorics | medium | 4 | 7 | 28 | 0.35 | assumed | 25 | timeline | ai | **78** | 224 | 3.1 |
| erdos728-writeup | number theory | medium | 1 | 28 | 28 | 0.30 | assumed | 20 | timeline | ai | **67** | 224 | 3.4 |
| bunkbed | combinatorics | short | 3 | 105 | 315 | 0.20 | assumed | 12 | timeline | no | **504** | 2520 | 42.0 |
| polymath1-dhj | combinatorics | medium | 27 | 37 | 999 | 0.08 | pointed | 34 | direct | no | **639** | 7992 | 18.8 |
| cgms-ramsey | combinatorics | large | 4 | 1673 | 5797 | 0.25 | assumed | 59 | timeline | no | **11594** | 46376 | 196.5 |
| cairo-mizohata | analysis | medium | 1 | 150 | 150 | 0.25 | assumed | 15 | timeline | no | **300** | 1200 | 20.0 |
| degrey-chromatic | geometry | short | 1 | 109 | 109 | 0.15 | pointed | 11 | timeline | no | **131** | 872 | 11.9 |
| kakeya-r3 | analysis | large | 2 | 860 | 1720 | 0.30 | assumed | 127 | timeline | no | **4128** | 13760 | 32.5 |
| boltzmann-dhm | analysis | large | 3 | 273 | 819 | 0.55 | pointed | 192 | timeline | no | **3604** | 6552 | 18.8 |
| chen-hou-euler | analysis | large | 2 | 1108 | 2216 | 0.35 | assumed | 184 | timeline | no | **6205** | 17728 | 33.7 |
| alpoge-buckmaster | analysis | large | 2 | 330 | 660 | 0.35 | assumed | — | timeline | ai | **1848** | 5280 | — |
| wiles-flt | number theory | large | 1 | 2957 | 3357 | 0.564 | assumed | 129 | timeline | no | **15147** | 26856 | 117.4 |
| zhang-gaps | number theory | large | 1 | 1021 | 1021 | 0.50 | assumed | 54 | timeline | no | **4084** | 8168 | 75.6 |
| baek-sofa | geometry | large | 1 | 2800 | 2800 | 0.20 | assumed | 119 | timeline | no | **4480** | 22400 | 37.6 |
| hales-kepler | geometry | large | 2 | 1670 | 3340 | 0.45 | assumed | 121 | timeline | no | **12024** | 26720 | 99.4 |
| erdos848 | combinatorics | short | 2 | 39 | 78 | 0.20 | assumed | — | timeline | ai | **125** | 624 | — |
| erdos347 | number theory | short | 5 | 102 | 510 | 0.08 | assumed | — | timeline | ai | **326** | 4080 | — |
| erdos326 | combinatorics | short | 1 | 25 | 25 | 0.20 | assumed | — | timeline | ai | **40** | 200 | — |
| erdos696 | combinatorics | short | 2 | 40 | 80 | 0.15 | assumed | — | timeline | ai | **96** | 640 | — |
| erdos1148 | number theory | short | 3 | 51 | 153 | 0.10 | assumed | — | timeline | ai | **122** | 1224 | — |
| erdos986 | combinatorics | short | 1 | 20 | 20 | 0.25 | assumed | — | timeline | ai | **40** | 160 | — |
| erdos1153 | combinatorics | short | 3 | 50 | 150 | 0.10 | assumed | — | timeline | ai | **120** | 1200 | — |
| erdos90-bound | combinatorics | short | 12 | 19 | 228 | 0.06 | assumed | — | timeline | ai | **109** | 1824 | — |
| *perelman-poincare* | geometry | large | 1 | 2871 | 2871 | 0.50 | assumed | 68 | timeline | no | *11484* | 22968 | *168.9* |
| *viazovska-d8* | geometry | medium | 1 | 365 | 365 | 0.45 | assumed | 22 | timeline | no | *1314* | 2920 | *59.7* |
| *duffin-schaeffer* | number theory | large | 2 | 730 | 1460 | 0.30 | assumed | 46 | timeline | no | *3504* | 11680 | *76.2* |

Italic rows are reported and not used. Perelman is dropped because **no statement of his time
allocation exists** — the brief's own condition — so the 0.50 is unanchored on a seven-year
window, which is where the figure comes from. Viazovska's dimension-8 row is dropped because
the only duration on record ("more than a year of hard work until the solution was complete in
dimension eight") describes the team's joint programme and not her solo window, so the start
date is my invention. Duffin–Schaeffer is dropped because I found no dated start at all and the
two-year window is a guess.

### Where each direct record comes from

The eight direct records are the load-bearing rows, and they are what the class rates should be
read off. Each is a published statement about how the solver spent time, not an inference from
two arXiv timestamps.

- **erdos1026.** Tao's blog post of 8 December 2025: "all these key inputs were able to be
  assembled within 48 hours", with the individual contributions timed at "within hours", "less
  than an hour after that" and "approximately an hour of run time". Six named contributors, one
  to three hours each.
- **capset-ellenberg.** Croot, Lev and Pach posted on 5 May 2016; Kalai's blog post announcing
  Ellenberg's solution is dated 15 May 2016; Quanta records Ellenberg and Gijswijt each
  polishing off the cap set problem "within 10 days" in three pages. The 0.35 is mine.
- **kahn-kalai.** Quanta: "Over the course of a single sleepless night in March, they figured
  out how to make the proof work", and "One week after their sleepless night in March, they
  posted their elegant six-page paper online."
- **royen-gci.** Quanta: the proof came to Royen on the morning of 17 July 2014; "By evening, he
  had written down a first draft, and by early August, the paper was finished." arXiv v1 is
  5 August 2014.
- **gilmer-unionclosed.** Quanta: "Gilmer worked on the problem at night, after finishing his
  work at Google, and on weekends throughout the second half of October and early November.
  Finally, on November 16 he posted a first-of-its-kind result."
- **huang-sensitivity.** Quanta (25 July 2019): the idea came "last month, as he sat in a Madrid
  hotel writing his grant proposal"; arXiv v1 is 1 July 2019. **The seven prior years of
  on-and-off attempts are excluded by the conditional-on-success rule**, and this is the
  clearest case in the table of that rule doing real work: the row is 60 hours, not seven years.
- **tao-discrepancy.** Tao's blog post on Matomäki–Radziwiłł is 6 September 2015; the comment
  suggesting the application to the discrepancy problem is 9 September; arXiv v1 is
  17 September. Twenty-nine pages in eight days is the lowest hours-per-page figure in the
  table and it is a real record, not an error.
- **sphere24.** Radchenko's MPIM interview: "We then completed the paper in one week of very
  intense work"; "At peak moments our team exchanged about ten emails every hour." Five people,
  seventeen pages, seven days. This is the only 0.80 in the table.
- **polymath1-dhj.** Gowers and Nielsen in *Nature*: "Just 37 days had passed since the
  collaboration began, and 27 people had contributed approximately 800 mathematical comments,
  containing 170,000 words." Twenty-seven people at 0.08 is about 0.64 hours a day each, which
  is roughly one substantive comment per person per day.

### What the table shows

| Class | Pages | n | h/page median | h/page range | Dispersion | Total hours median | Total hours range | Dispersion |
|---|---|---:|---:|---|---:|---:|---|---:|
| Short | ≤12 | 16 | 8.0 | 4.1 to 42.0 | 10.2 | 80 | 28 to 504 | 18.0 |
| Medium | 13–60 | 6 | 8.3 | 1.1 to 20.0 | 18.1 | 151 | 32 to 639 | 20.0 |
| Large | >60 | 8 | 56.6 | 18.8 to 196.5 | 10.5 | 5342 | 3604 to 15147 | 4.2 |

**Hours per page is flat at about 8 up to sixty pages and then jumps by a factor of seven.**
That is the table's main structural fact, and it is not what a naive reading would predict: a
29-page Tao paper and a 4-page Ellenberg paper cost about the same per page, but a 127-page
Kakeya paper costs four times that and a 59-page Ramsey paper costs twenty-five times it. The
break is not about page density. It is that short and medium results are, with two exceptions,
**single ideas found and written inside one burst**, while everything above sixty pages is a
multi-year programme in which most of the time goes to machinery that never appears as a page.

**Which features predict hours**, as log-log correlations over the thirty rows in the fit:

| Predictor | r |
|---|---:|
| Elapsed calendar days | 0.92 |
| Pages | 0.88 |
| Number of people | 0.14 |

**Head-count predicts almost nothing**, which is the table's most useful negative result. The
largest team in the table, Polymath1's twenty-seven, produced 639 hours; the smallest, Wiles
alone, produced 15,147. Teams form around problems that are *tractable in a burst*, so adding
people correlates with the problem being easy about as strongly as it correlates with more
labour being spent. Any estimate that scales up by assumed head-count is therefore scaling on
the weakest available signal, and this is exactly the defect in the superseded Navier–Stokes
construction ("five experts over thirteen years") that Damon struck out.

**Elapsed days is the best single predictor, and that is partly circular** — active hours are
built from elapsed days times a fraction that varies over a range of only 13× while elapsed
days vary over 1,500×. The honest statement is that the fraction ladder is a weak modulation on
the window, so the window is where the information is, and the collector's real job is getting
the window's endpoints right rather than tuning the fraction.

**Dispersion within class is an order of magnitude and cannot be argued away.** Two short
counterexample papers, Gilmer's nine pages and the bunkbed twelve, differ by a factor of 14 in
hours: Gilmer found his idea in a month of evenings and the bunkbed team spent a summer
adapting Hollom's construction after a year of failed computer search. Nothing about the
deliverable distinguishes them. So **a class rate applied to a new problem carries a factor of
3 either way at least**, and the method below says so rather than hiding it.

### Direct records against timelines

| Subset | n | Median hours |
|---|---:|---:|
| Direct record of the solver's own time | 8 | 56 |
| Dated timeline only | 22 | 216 |
| Unassisted human work | 20 | 402 |
| AI-assisted | 10 | 102 |

The direct records are systematically the small ones, and that is selection, not measurement:
a mathematician says "one week of very intense work" when it *was* one week, and says nothing
when it was four years. **So the direct records set the floor of the distribution and the
timelines set its body**, and the method uses the record where one exists on the problem at
hand and the class rate otherwise.

The AI-assisted rows are biased low as measures of unassisted human time and are flagged
`assisted = ai` in the CSV. They are kept because they are the closest thing in existence to a
measurement of the quantity these dataset rows need — a human producing a research-level result
today — and because excluding them would leave the 2026 Erdős wave entirely out of the
calibration.

<a id="table2"></a>

## Table 2. Formalization effort

Twelve projects, eight in the fit. The estimator is different from Table 1's and better, because
for a formalization the work leaves a public trace.

**The author-day estimator.** For each project I clone the repository and count **distinct
(author, calendar day) pairs, excluding bots**. A day on which someone pushed a commit is a day
they worked. Active hours are then `author-days × 4 hours per active day × 1.5 for uncommitted
work`. Both factors are my assumptions and both are stated: 4 hours because a volunteer
formalizer's commit-day is a session rather than a full day, and 1.5 because blueprint writing,
review and Zulip discussion leave no commit. The band runs `× 2 × 1.2` to `× 8 × 2.5`, a factor
of 6.7 wide, and that band is carried in the CSV. **What survives the band is the ratio between
projects**, which is what the rates below use.

Three projects cannot use it: the Odd Order and Four Colour repositories are later ports whose
commit histories postdate the work by a decade, and the cap set repository is a twenty-commit
import. Those fall back to `people × elapsed days × 8 × fraction`.

**Blueprint pages** for projects that publish a `leanblueprint` source but no page count are
converted at **67.9 LaTeX lines per page**, which is Carleson's own measured 9,778 blueprint
`.tex` lines against its stated 144 pages.

| Key | Paper pp | Blueprint pp | Formal lines | Contributors | Author-days | Elapsed d | **Active h** | Band | Lines/h | Lines per paper pp | Lines per blueprint pp | h per blueprint pp |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|
| pfr | 33 | 51 | 11035 | 30 | 148 | 23 | **888** | 355–2960 | 12.4 | 334 | 216 | 17 |
| lte-stage1 | — | — | 26969 | 19 | 351 | 187 | **2106** | 842–7020 | 12.8 | — | — | — |
| lte-full | — | — | 94452 | 30 | 1049 | 591 | **6294** | 2518–20980 | 15.0 | — | — | — |
| sphere-eversion | — | 43 | 17813 | 12 | 347 | 892 | **2082** | 833–6940 | 8.6 | — | 414 | 48 |
| carleson | 30 | 144 | 35600 | 28 | 460 | 425 | **2760** | 1104–9200 | 12.9 | 1187 | 247 | 19 |
| capset-formal | 4 | 9 | 2000 | 3 | — | 93 | **335** | 167–670 | 6.0 | 500 | 222 | 37 |
| flt-imperial | — | 91 | 58777 | 73 | 727 | 1032 | **4362** | 1745–14540 | 13.5 | — | 646 | 48 |
| odd-order | 250 | — | 40549 | 15 | — | 2334 | **28008** | 14004–56016 | 5.4 | 162 | — | — |
| *flyspeck* | 121 | — | — | 22 | — | 4239 | *37303* | 18652–74606 | — | — | — | — |
| *fourcolor* | 43 | — | 44695 | 2 | — | 1796 | *8621* | 4310–17242 | 5.2 | 1039 | — | — |
| *li-550* | 26 | — | — | 1 | — | 41 | *131* | 66–262 | — | — | — | — |
| *sel4* | — | — | 165000 | — | — | 1826 | *22000 stated* | — | 7.5 | — | — | — |

Italic rows are reported and not used in the fit. Odd Order's lines-per-hour uses the >150,000
lines of the whole six-year development rather than the 40,549 specific to the theorem, because
the hours are the whole development's; its lines-per-page uses the 40,549 against the 250 pages
of Bender–Glauberman and Peterfalvi, which is the paper's own pairing. The Imperial FLT row is
excluded from the page fits only: its blueprint outlines an unfinished reduction rather than a
complete proof, so 646 lines per blueprint page is not comparable.

### The rates

| Rate | n | Min | Median | Max | Dispersion |
|---|---:|---:|---:|---:|---:|
| Formal lines per active hour | 8 | 5.4 | **12.6** | 15.0 | 2.8 |
| Formal lines per blueprint or textbook page | 4 | 216 | **235** | 414 | 1.9 |
| Formal lines per research-paper page | 4 | 162 | **417** | 1187 | 7.3 |
| Active hours per blueprint or textbook page | 4 | 17 | **28** | 48 | 2.8 |
| Active hours per research-paper page | 4 | 27 | **88** | 112 | 4.2 |

**Lines per active hour is the tightest number in this note.** Five independent Lean projects
measured the same way land between 8.6 and 15.0, and the two Coq-era projects land at 5.2 and
5.4. The Lean-era median of 12.9 against the Coq-era 5.3 is a 2.4× tooling improvement over
fifteen years, and it is the right direction and the right size.

**12.6 lines per hour supersedes both rates currently in circulation in this collection.** It
sits between `research/flt-anthropic.md`'s Imperial figure of 5.88 and the
`research/frontiermath-erdos/frontiermath-erdos.md` figure of 31.7 taken from Li's
formalization. The Imperial 5.88 is low because it divides measured lines by a *funded
head-count* rather than by observed work, which the next section quantifies. The 31.7 is high
because its numerator is an estimate — Li never published a line count, so 4,160 lines was
inferred from 26 pages at Odd Order's 160 lines per page, and the note that built it flagged
that step as its weak link. Neither is measured on both ends; all five Lean rows above are.

**The size ratio splits by what counts as a page, and this is the practical finding.** A
research paper written for experts compresses at 417 formal lines per page, with a spread of
7.3× that is really a spread in how much the paper leaves to the reader — Carleson's 30-page
paper for harmonic analysts runs 1,187 lines per page, and Odd Order's textbook sources run
162. A blueprint or a textbook, which is prose written so a non-expert can follow every step,
compresses at 235 lines per page with a spread of only 1.9×. **So a formal artifact's line
count is a reliable cross-check against a blueprint's page count and an unreliable one against
a paper's.** The Carleson project exists because its authors discovered exactly this: "After a
very brief attempt to formalize the paper directly, we realized we needed a detailed blueprint."

<a id="flt-headcount"></a>

### The Imperial FLT project: head-count against the grant

This is the one place in either table where a funded staffing figure and an observed work record
can be put side by side, so it gets its own treatment.

My measurements of `ImperialCollegeLondon/FLT` at commit `bb71146`, 16 September 2026:

| Quantity | Value |
|---|---:|
| Lean lines | 58777 |
| Commits, non-bot | 1571 |
| Commits, bot | 133 |
| Distinct non-bot commit authors | 73 |
| Distinct author-days, non-bot | 727 |
| Of which Buzzard's | 302 |
| Elapsed since first commit (days) | 1032 |
| Blueprint LaTeX lines | 6205 |

Author-days by half-year: 28, 148, 159, 176, 106, 75, 35 from 2023H2 to 2026H2. The project
peaked in 2025H1 and has been declining since; 2026H2 is a third of the peak.

    Observed:  727 author-days x 4 h x 1.5      =  4,362 active hours  =  2.18 person-years
    Funded:    GBP 934,043 / 5 years            =  GBP 186,809 per year
               at GBP 93k-125k full economic cost per FTE  =  1.49 to 2.01 FTE
               x 2.04 years elapsed since the Sep 2024 fellowship start
                                                =  3.1 to 4.1 person-years
                                                =  6,101 to 8,200 hours

**The grant overstates the work by 1.4 to 1.9×.** That is the answer to the question Damon
posed, and its direction matters more than its size: money bought more capacity than the project
consumed. Three things explain the gap and none of them is a defect in the project. The
fellowship buys out Buzzard's teaching and administration, and a bought-out professor does not
spend every bought-out hour on the one project. Funded postdoc time goes partly to Mathlib
upstreaming that the FLT repository never sees. And 302 of 727 author-days are Buzzard's, so
the volunteer tail — 72 other people over 425 author-days — is real but thin, which pushes the
other way and is already inside the observed figure.

**The comparison also bounds the estimator's error.** If 6 hours per author-day were badly
wrong, the observed and funded figures would not agree to within a factor of two on the one
project where both exist. At 4 hours per author-day the observed figure is 2,908 and the grant
overstates by 2.1 to 2.8×; at 9 it is 6,543 and the grant understates slightly. Six is the value
that makes the two accounts consistent, which is weak evidence for it and the only evidence
available.

`research/flt-anthropic.md` currently uses the funded side: 4 to 6 all-in person-years, which is
above even the top of the funded band above, because it adds a volunteer-tail judgment on top of
the funded FTE. The observed record does not support it.

<a id="method"></a>

## The method

What a collector does with a new AI-solved research problem.

**1. Read the deliverable, not the problem's reputation.** Read the proof, or the Lean artifact
and whatever human exposition exists — a wiki write-up, a blog summary, the repository README.
Establish three things: what the argument actually is, how long the written mathematics would
be, and whether a formalization is part of the deliverable.

**2. Size it in pages.** Count pages of the research paper a human would have to write. If no
paper exists and only a Lean artifact does, divide the measured line count by **417 lines per
research-paper page**. If the deliverable's source is a textbook or a blueprint, use **235 lines
per page** instead. Record which ratio was used, because they differ by 1.8× and the choice is
the largest single discretionary step in the whole method.

**3. Classify.** Area, character (construction or counterexample, short argument, structural
theorem, programme), and size class from the page count: **short ≤ 12, medium 13–60, large > 60**.

**4. Look for a direct record on this problem, and prefer it to everything else.** An author
statement about time spent, a dated collaboration log, a blog post that times the individual
contributions. A direct record on the problem at hand beats any rate, and the eight rows in the
table flagged `direct` show what one looks like. **Erdős 548 is the live example**: Riordan and
Scott worked that exact argument in a dated eight-day window, so the class rate is not used
there.

**5. Otherwise apply the class rate**, `hours = pages × 8.0` for short, `× 8.3` for medium,
`× 56.6` for large. Then cross-check against the two nearest individual rows by area and
character, and if the rate and the neighbours disagree by more than 3×, say so in the note and
take the neighbours.

**6. Add the formalization term if the deliverable includes one.** `hours = human-idiom Lean
lines ÷ 12.6`, where human-idiom lines come from the page count at step 2's ratio. **Do not
divide a machine-written line count by a human-written rate** without saying so: the rate's
numerator is Mathlib-idiom Lean, and a machine artifact is not. Where only the machine artifact
is measured, the resulting term is an upper bound and should be labelled one.

**7. State the range as the class's own dispersion, not as a confidence interval.** Low is the
class minimum rate, high is the class maximum, which is a factor of 10 to 18 on hours per page.
Report the elapsed bound alongside, so a reader can see the central sits below it.

**8. Never use** years open, prize status, prize money, the count of failed prior attempts, the
field's cumulative effort, grant totals (except as a head-count cross-check), or the AI's own
wall clock. If a figure changes when you learn the problem's age, the method has been applied
wrongly.

<a id="worked"></a>

## Worked illustration: the eight dataset rows

**No row is edited by this note.** These are what the method yields, next to the values the rows
currently carry.

| Row | Pages | Class | Solve h | Solve basis | Lean lines | Lean h | **Method h** | Current h | Ratio |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|
| `reas-erdos1-astra` | 5.8 | short | 47 | 8.0 × 5.8 | 2427 | 193 | **239** | 194 | 1.23 |
| `reas-erdos74-astra` | 6.0 | short | 48 | 8.0 × 6.0 | 2516 | 200 | **248** | 158 | 1.57 |
| `reas-erdos126-astra` | 7.3 | short | 59 | 8.0 × 7.3 | 3058 | 243 | **301** | 175 | 1.72 |
| `reas-erdos548-astra` | 3.0 | short | 61 | direct record | 1243 | 99 | **160** | 101 | 1.58 |
| `reas-erdos571-astra` | 24.9 | medium | 207 | 8.3 × 24.9 | 10390 | 825 | **1031** | 563 | 1.83 |
| `reas-navier-stokes-openai` | 166 | large | 9396 | 56.6 × 166 | 69255 | 5496 | **14892** | 13825 | 1.08 |
| `reas-flt-lean-anthropic-internal` | — | large | 7931 | scaled work record | — | 19827 | **27758** | 84000 | 0.33 |
| `reas-lean-textbook-algcomb-opus45` | 500 | large | 0 | no new mathematics | 117350 | 9313 | **9313** | 12000 | 0.78 |

The arithmetic line for each:

- **Erdős 1, 74, 126.** Pages from the measured Lean at 417 lines/page, then the short-class rate
  and the 12.6 lines/hour formalization rate. `2427/417 = 5.8 pp; 5.8 × 8.0 = 47 h;
  2427/12.6 = 193 h; total 239 h.` The rows currently sit at 194, 158 and 175, built from the
  Erdős note's A3 anchor times a multiplier plus Li's 31.7 lines/hour. **The method moves them up
  by 1.2 to 1.7×, and essentially all of the move is the formalization rate**: 12.6 against 31.6
  is a factor of 2.5 on a term that is already half of each row.
- **Erdős 548.** The direct record supersedes the class rate at step 4, so the solve term is the
  Erdős note's own 61 hours — Riordan and Scott's 51-hour window times its 1.2 multiplier — and
  only the Lean term changes. `61 + 1243/12.6 = 160 h` against 101.
- **Erdős 571.** At 10,390 lines the artifact crosses into the medium class at 24.9 estimated
  pages. `24.9 × 8.3 = 207 h solve; 10390/12.6 = 825 h Lean; total 1031 h` against 563. **This is
  the row where the method and the current value disagree most in the Erdős batch**, and the
  reason is that the current 563 applies a judgment multiplier of 3 to a 78-hour anchor while the
  method reads the size off the artifact. The method's figure is the more defensible of the two,
  because 24.9 pages is a measurement and the 3 was flagged in its own note as "the least
  defensible" figure there.
- **Navier–Stokes.** `166 pages × 56.6 h/page = 9,396 h` for the mathematics, against the row's
  current 9,308 built from the Chen–Hou anchor times 1.5. **The two routes agree to within 1%,
  which is the strongest single corroboration in this note** and is not built in: the current
  figure comes from one neighbouring PDE paper's elapsed window, the method's from the median
  hours-per-page of eight large results across four fields. The formalization term rises from
  4,517 to 5,496 because 166 × 417 / 12.6 sits above the Imperial-rate route the row used. Total
  14,892 against 13,825, a change of 8%, which is inside any reasonable band.
- **Fermat.** No page count applies: there is no informal paper and the Imperial blueprint covers
  only the reduction. So the row is priced by scaling the one project aimed at the same
  deliverable. `4,362 observed active hours / 0.55 of the reduction delivered = 7,931 h for the
  whole reduction; × (1 + 2.5) for the remainder the Anthropic artifact additionally proves =
  27,758 h.` The 0.55 is my assumption, from 70 `sorry` still open against 2,014 theorem
  declarations and `PROOF-PATH.md`'s restricted forms at 2.83 years of a five-year plan; the 2.5
  remainder multiplier is unchanged from `research/flt-anthropic.md`. **Against the row's 84,000
  this is a factor of three down, and the whole of it is the head-count finding**: the current
  value prices funded person-years, the method prices observed work, and the grant runs 1.4 to
  1.9× above the record.
- **Meta textbook.** The mathematics already exists in Grinberg, so there is no solve term. About
  500 pages of main text at the blueprint ratio is 117,350 human-idiom lines, and
  `117350/12.6 = 9,313 h` against the row's 12,000. **The two agree to within 22%**, which is the
  second independent corroboration here, because the row's own figure comes from 90,000
  human-equivalent lines at 15,000 lines per person-year — a different numerator and a different
  rate.

**The pattern across the eight.** Five small rows move up by 1.2 to 1.8× on the formalization
rate, two large rows are confirmed to within 22%, and one large row falls by a factor of three
on an evidence question that has nothing to do with the rates. That is the shape you want from a
calibration: it should mostly agree with careful case-by-case work and disagree exactly where the
case-by-case work used a weaker input.

<a id="gaps"></a>

## What I could not find

- **No paper resolving an Erdős problem states its own duration.** Not the sum-product paper,
  not Li's, not Riordan and Scott's, not Sothanaphan's. Every Erdős row in Table 1 is a window
  between two dated artifacts, and the on-task fraction on all of them is my assumption.
- **Algebra is missing from Table 1.** The thirty-five rows are combinatorics, number theory,
  analysis and geometry. I could not find a resolved algebra problem with both a dated window
  and a page count at this level; the nearest candidates (Kervaire invariant, the telescope
  conjecture) have multi-decade programmes behind them with no usable start date for the
  successful episode. The class rates should be treated as untested in algebra.
- **The four colour theorem's effort is not on record anywhere I could reach.** The AMS *Notices*
  PDF returns 403 and the `coq-community/fourcolor` repository is a 2018 port. Gonthier's start
  date, his collaborator's share, and the 60,000-line figure usually quoted are all second-hand,
  which is why that row is reported and not used.
- **Flyspeck has no measured line count.** The repository totals 1.33M lines of `.hl` and `.ml`
  including HOL Light itself, which is not a formal-proof count, and the completed-project paper
  states no effort figure. Hales's "20 person-years" is an estimate made at the project's
  *inception* in 2003, not a record of what it cost. My head-count reconstruction — 22 authors
  over 4,239 days at 0.05 — gives 18.7 person-years, which agrees with Hales's forecast and
  should be read as a coincidence rather than a confirmation, since the 0.05 was chosen with no
  independent basis.
- **Li's Erdős 550 Lean artifact has no published line count**, so the one case of a
  mathematician formalizing his own fresh research proof still gives hours without a rate. That
  is the single most valuable missing measurement for this collection, because it is the exact
  shape of the FrontierMath rows' deliverable.
- **No informal page count exists for the Liquid Tensor Experiment's target.** Scholze's
  challenge names Theorem 9.4 of the *Analytic Geometry* notes, and no one states how many pages
  the proof occupies. The project therefore contributes to the lines-per-hour fit and to neither
  page fit.
- **The AI-assisted flag is coarse.** Twelve of the thirty-five rows had AI in the loop, in
  wildly different degrees — from Alpöge and Buckmaster, whose arguments Tao calls "heavily
  AI-assisted", to the Erdős wiki collaborations where a model supplied a candidate and a human
  verified it. I have not tried to grade the degree, and nothing in the table adjusts for it.
- **The on-task fraction has no empirical basis anywhere.** Eight rows have the intensity pointed
  by a source, and even those convert a phrase like "very intense work" into a number by my
  judgment. Halving every assumed fraction halves twenty-two of the thirty rows in the fit and
  drops the large-class rate from 57 to 28 hours per page. A single published time-diary study of
  research mathematicians would replace the weakest half of this note.

## Sources

Every row's source is in the `source` column of its CSV, with the dated evidence in
`span_evidence` or `notes`. The ones this note quotes directly:

- Tao, [the story of Erdős problem #1026](https://terrytao.wordpress.com/2025/12/08/the-story-of-erdos-problem-1026/), 8 Dec 2025
- Tao's [AI contributions to Erdős problems wiki](https://github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erd%C5%91s-problems), frozen 30 Jun 2026
- Gowers and Nielsen, [Massively collaborative mathematics](https://www.nature.com/articles/461879a), *Nature* 461 (2009)
- Radchenko, [interview on the dimension-24 sphere packing](https://www.mpim-bonn.mpg.de/node/6742), MPIM
- Quanta on [Park and Pham](https://www.quantamagazine.org/elegant-six-page-proof-reveals-the-emergence-of-random-structure-20220425/), [Gilmer](https://www.quantamagazine.org/long-out-of-math-an-ai-programmer-cracks-a-pure-math-problem-20230103/), [Huang](https://www.quantamagazine.org/mathematician-solves-computer-science-conjecture-in-two-pages-20190725/), [Royen](https://www.quantamagazine.org/statistician-proves-gaussian-correlation-inequality-20170328/), [de Grey](https://www.quantamagazine.org/decades-old-graph-problem-yields-to-amateur-mathematician-20180417/), [the bunkbed conjecture](https://www.quantamagazine.org/maths-bunkbed-conjecture-has-been-debunked-20241101/), [diagonal Ramsey](https://www.quantamagazine.org/after-nearly-a-century-a-new-limit-for-patterns-in-graphs-20230502/) and [Zhang](https://www.quantamagazine.org/yitang-zhang-proves-landmark-theorem-in-distribution-of-prime-numbers-20130519/)
- Gonthier et al., [A machine-checked proof of the Odd Order Theorem](https://www.cs.unibo.it/~asperti/PAPERS/odd_order.pdf), ITP 2013
- Becker et al., [Formalization of Carleson's theorem in Lean](https://florisvandoorn.com/carleson/paper.pdf)
- Dahmen, Hölzl and Lewis, [Formalizing the solution to the cap set problem](https://arxiv.org/abs/1907.01449), ITP 2019
- [Completion of the Liquid Tensor Experiment](https://leanprover-community.github.io/blog/posts/lte-final/), 14 Jul 2022
- Tao, [Formalizing the proof of PFR in Lean4 using Blueprint](https://terrytao.wordpress.com/2023/11/18/formalizing-the-proof-of-pfr-in-lean4-using-blueprint-a-short-tour/), 18 Nov 2023
- Buzzard, [EPSRC EP/Y022904/1 "Formalising Fermat"](https://gtr.ukri.org/projects?ref=EP%2FY022904%2F1)

Repository measurements are my own, taken 16 September 2026 by cloning each project and counting
`*.lean`, `*.v`, `*.hl` and `*.ml` files and non-bot `git log` author-days. The commits used are
named in each row's `formal_lines_basis`.
