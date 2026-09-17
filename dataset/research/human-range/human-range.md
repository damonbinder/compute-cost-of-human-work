# The human_time range

*Created 2026-09-16 10:01.*
*Last revised 2026-09-17.*

`human_time_low` and `human_time_high` bracket `human_time` with the alternative
scenarios the row's own research note argues, and with nothing else. They are
transcribed, not computed: a note that states a sensitivity interval, two anchors,
or a named factor's plausible alternative values supplies the two bounds directly,
and where the note gives its scenario in minutes, hours or person-years the only
operation applied is the unit conversion. No bound anywhere in this pass comes from
multiplying the central by a default factor.

**Counts.** 364 rows are eligible and **354 carry a range**: 144 transcribed from a
scenario the note already stated, 20 written by hand in the first pass from the
note's own reasoning, 117 re-argued on 2026-09-16 under Damon's ruling that no bound
may rest on a default factor, **68 argued on 2026-09-17** for rows whose notes had
stated no scenario at all, and **5 set by the clock convention** ruled later the same
day. **10 are left blank** and are listed below. The median high-to-low ratio is 3.0.

**The 2026-09-16 rework.** 111 rows carried bounds at exactly half and twice their
central, and 13 had the low bound sitting on the central. Every note behind them was
read again and its bounds re-derived from evidence: the dispersion of a donor set
where one exists, the note's own component budget re-run at each line's ends where
it does not, and an external measured anchor where the note had cited one and
declined to use it. Seven rows lost their bounds, one central moved, and the rest
took bounds that are mostly narrower than half-to-double and in no case a factor on
the central. `agent-work/reviews/human-range-rework-2026-09-16.md` records the
per-note argument.

**The 2026-09-17 pass.** The 81 rows the earlier passes left blank were taken one
family at a time, and 68 of them now carry a range. Where a note argued no
alternative it was made to argue one, from evidence the note already named or from a
source it had cited and not used. The eight families and their anchors:

| Note | Rows | Anchor the bounds come from |
|---|---:|---|
| `research/gdpval/gdpval.md` | 17 | The published Table 5 distribution over the same 220 gold tasks. The estimates and the source describe the same 220 numbers with fitted log spreads of 0.727 and 1.064; the rank-preserving map onto the published distribution and the residual spread of that map give each row its two bounds. |
| `research/cost-of-pass/cost-of-pass.md` | 29 | Addition: the donor's two group means at this sample's carry mix. GSM8K: Zhang's throughput converted to a per-attempt time at the measured human accuracy, which makes the central the floor. BBQ: the authors' own allowance above, the reading-plus-decision budget re-run at the decision term's end below. |
| `research/physical-intelligence/physical-intelligence.md` | 10 | Each step budget re-run at its own ends, with the fold-from-basket rows taking the `pi0-shirt.md` sibling's argued 10-to-25-second block whole. |
| `research/imagenet-cnn/imagenet-cnn.md`, `research/imagenet.md` | 5 | Shankar et al. publish two readings of the same effort: a 26-second per-image median and a 36-hour median total for 2,000 images, 64.8 seconds an image. The median is the floor. |
| `research/medical-learning/medical-learning.md` | 3 | Each factor's own published range: COCATS's 3,000-3,500 tracings against Bortolotti's 107.61 and 205.31 seconds; Bodrogi's 2-minute negative set against the Scenarios table's two qualifying years; the MQSA minima as a floor against its continuing volume. |
| `research/games-memory/chess.md` | 1 | The Maia bin's own count-weighted mean at the other Lichess blitz controls, 4.5055 s at 180+0 and 10.6315 s at 300+3. |
| `research/srt-h.md` | 1 | The spread of the transfer ratio across the three donor records, 0.66851 to 0.74000, against the per-task-rate transfer the note already named. |
| `research/robotics-science/sparrow.md`, `research/robotics-science/retrodfmr.md` | 2 | The bin-pick budget re-run at its ends; the retrosynthesis note's own six-to-twenty-minute range, which the earlier pass had missed. |

Three rows take a low equal to the central, each on an argued floor: GSM8K, where
both published anchors for the quantity sit at or above the batch pace; ImageNet,
where the median is the lower of the source's two published readings of one
distribution; and the mammography row, whose two terms are both statutory minima.

**What the pass found and did not fix.** Three notes turned out to have a wrong
central rather than a missing bound, and none of the three was changed in that pass.
The second pass of 2026-09-17, below, settled them.

## The clock convention, 2026-09-17

The chess and Go rows disagreed on whether a per-move clock reading is the central or
the low scenario, and the disagreement is now ruled in
`research/games-memory/chess.md#the-clock-convention`: **the own-clock figure is the
central and the own-clock-plus-opponent-clock figure is the ceiling.** The own clock
is what the sources measure, the elapsed move cycle is the ceiling by construction
under the rule that elapsed time bounds active time, and the pondering fraction that
separates them is unmeasured and belongs in the bar.

| Row | Old central | New central | Low | High | Anchor |
|---|---:|---:|---:|---:|---|
| `game-go-alphagozero-1600` | 120 | 60 | 60 | 128.1 | Lee's own clock, 37 min over 37 moves; AlphaGo's 42 min is 68.1 s, so the cycle is 128.1 s |
| `game-go-alphagozero-40block-policy` | 120 | 60 | 60 | 128.1 | same |
| `game-go-alphagozero-40block-1600` | 120 | 60 | 60 | 128.1 | same |
| `game-chess-alphazero` | 60 | 60 | 60 | 120 | one minute a move for each side, so the cycle is 60 + 60 |
| `game-chess-move-gpt35` | 4.3 | 4.3 | 4.3 | 8.62 | the (1800,3000] bin's 4.3100 s own-clock mean at 180+0, doubled for the cycle |

Three lows sit at their central on an argued floor: at world-class level in a serious
match idle time inside the player's own turn is small and thinking on the opponent's
turn is nonnegative, and on the GPT-3.5 row the control is settled at 180+0, the
lowest of the four the donor covers for that bin. The Maia and nine Game Arena rows
keep the bounds they already carried, because those answer which blitz control a
representative decision comes from, not the engagement fraction.

## The remaining three families, 2026-09-17

`med-skin-train-esteva` is now bounded 12,100 to 20,900 seconds. Both Ternov papers
were reached: the 25-item test's group means are 7.5 of 25 for medical students and
18.4 for the 32 clinicians in dermatology departments, and the 2023 trial's students
scored 13.85 after 600 cases. The fitted log-odds line through the students' two
points has a slope of 0.00177355 per case and reaches the 12/25 pass mark at 433
cases and the dermatology group's 18.4 at 1,056, which at the measured 14.1 seconds a
case plus the measured 100 minutes of module reading gives 3.4 and 5.8 hours. The
central stays on the protocol as run.

The three exam rows and the seven Table L rows stay blank, and both claims were
re-verified rather than carried over. The exam centrals are no longer open: a central
sitting on an exam's time allowance is allowed where people use the whole allowance,
and the sources say they do. The Table L invariance is now arithmetic: reading the
whole Cambridge table at its band ends moves a row's hours by at most 2.5%.

## The rule

- Only `human_time_evidence = llm_estimate_judgment` or `llm_estimate_from_data`
  may carry a range. A `task_timings`, `defined_duration` or `source_estimate`
  duration is someone else's measurement or estimate, and this dataset does not
  invent uncertainty on it. Blank on those rows means no range is asserted, not
  that the number is exact.
- The bounds are what the note argues, never a factor on the central. A stated
  scenario supplies them directly; otherwise they come from the dispersion of the
  evidence the note names, from its component budget re-run at each line's ends, or
  from a measured anchor it cites.
- **A low bound equal to the central is not a range** (Damon, 2026-09-16). Where the
  first pass put one there, either the central was too low or the low was: LUMEN now
  takes its low from the regression at the deduplicated count, LAIT's central moved
  up to the self-revision scenario because a first draft is not a publishable
  translation, and the seven Table L rows lost their bounds because the homework
  doubling that produced them rested on misreading Cambridge's guided learning hours
  as class hours. Where the central is a ceiling, as with Minerva's near-full use of
  a fixed session budget, the high bound sits at `human_time`.
- The central need not sit at the midpoint. It sits where the note put it.
  `human_time_low` <= `human_time` <= `human_time_high` holds on every row, and
  the validator enforces it.
- Where a note argues no scenarios, or only a one-sided one, the row stays blank.
  Half a range is not a range.

## The per-row record

`human-range.csv` carries one row per filled point: the bounds, the note they come
from, whether the scenario was already in the note or was written by hand in this
pass, and the sentence in the note the bounds are read off. Every bound in
`points.csv` is reproducible from that file and the note it names.

`scenario_source` reads `note_scenario` where the note already stated the bounds,
`hand_written` where the first pass wrote them, `reargued_2026-09-16` where the
rework replaced them, `argued_2026-09-17` where the 2026-09-17 pass wrote the note's
first scenario, and `clock_convention_2026-09-17` for the five game rows the clock
ruling settled.

**Table P filled 2026-09-16.** The nine skill-acquisition programming rows were
blank because the old practice curve rested on a measured anchor and an unmeasured
judgment, with no alternative stated for either. The rebuilt Table P is fitted to
twenty first-course cohorts on the Rainfall Problem, and its bounds are the same
curve refitted at that distribution's upper and lower quartiles. See
`agent-work/reviews/table-p-rebuild-2026-09-16.md`.

The eight notes gaining a scenario sentence in the first pass are
`skill-acquisition-human-time.md` (Table L's doubling and Table C's 1-and-3-hours-a-day
scenarios, per row), `mirrorcode.md` (the extremes across the exponent and test-count
columns for cal and choose), `chess-learning/chess-learning.md` (the Charness/Gobet
readings and the flat-100 bridge), `lumen.md` (the per-row band), `lait.md` (the
central as the floor of its own scenario table), `minerva/minerva.md` (the budget as
the ceiling), `robotics-science/ariane.md` (the one-to-four-day range in hours), and
`physical-intelligence/physical-intelligence.md` (the espresso rows' active-time
reading and the flat-shirt row's inherited range).

## The 10 rows left blank

| Note | Rows | Why no range | Points |
|---|---:|---|---|
| `research/exams-knowledge/exams-knowledge.md` | 3 | The GRE, MBE and USMLE durations divide an exam's time allowance by its question count, so each central sits on the elapsed ceiling. That is allowed here, because the sources show the allowance is consumed and the time inside it is active: Step 2 CK examinees revisit a mean of 16.0 items per 40-to-45-item block at 44 to 58 seconds a revisit, extra time raises GRE verbal scores by about seven points over 15,948 examinees, and the NCBE's own sample booklet sets 108.6 s against the exam's 108. The high bound would therefore be the central, and no source argues a scenario below it. Half a range is not a range. | `lang-exam-gre-verbal-gpt4`, `lang-exam-mbe-gpt4`, `lang-exam-usmle-gpt4` |
| `research/skill-acquisition-human-time.md` (Table L) | 7 | Re-verified 2026-09-17 with the arithmetic written out. A row's hours are the Cambridge level's hours over the C1 band times the FSI figure, so the band ends move numerator and denominator together: the ratio spans 0.1250 to 0.1286 at A1, is exactly 0.5 at B1, and 1.4286 to 1.5000 at C2, at most 2.5% either way. The only other factor, the score-to-CEFR placement, is a stipulation with no published dispersion. A 2.5% bar would understate the uncertainty rather than carry it. | `lang-xfer-ar-acegpt7b-base`, `lang-xfer-ar-acegpt13b-base`, `lang-xfer-et-llammas-base`, `lang-xfer-eu-latxa13b`, `lang-xfer-eu-latxa70b`, `lang-xfer-ja-swallow7b`, `lang-xfer-ja-swallow70b` |
