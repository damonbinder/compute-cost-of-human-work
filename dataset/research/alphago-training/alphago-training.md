# Learning Go: one AlphaGo Zero 40-day run

*Last revised 2026-09-14 17:07.*

*Label note, 2026-09-15: `far_above` was merged into `above` across the dataset (Damon's ruling that day), so rows this note calls `far_above` carry `above` in `points.csv`. The reasoning below is unchanged.*

## game-go-alphagozero-40day-training

This is a **non-parity learning comparison**. The AI begins with random weights and finishes above world-class human strength. The human baseline is a selected eventual top professional learning from beginner to the strongest rung a person occupies. Different final performance is represented as `far_above`; the row does not imply that humans can learn to match AlphaGo Zero. Learning the same game at unequal final strengths is a useful imperfect observation under the current columns, provided analyses do not treat it as parity compute.

`human_skill=world_class` identifies the retrospectively selected learner population, not their ability at the beginning. The learner starts as a beginner. This is not an ordinary-child forecast or a success probability for intensive training.

## AI run and architecture

Original source: [Silver et al. (2017)](https://www.nature.com/articles/nature24270), final-performance section, Methods “Self-play training pipeline”, “Search algorithm” and “Neural network architecture”. The 40-day run reports29 million self-play games and3.1 million 2,048-position updates. Checkpoints occur every 1,000 updates and undergo400-game selection matches. Both sides use 1,600 MCTS simulations per move.

The Methods tower is a stem followed by 39 residual blocks, each containing two convolutions, all 256 channels. The combined policy/value heads are included. Conventional dense multiply/add reconstruction gives **33,246,070,248FLOPs per forward evaluation**. Three forward-equivalents approximate each forward/backward update position. Small normalization, nonlinearities, optimizer and search-control arithmetic are not tallied. The first-layer input-gradient saving is immaterial.

The four TPUs quoted for playing strength are inference hardware, not the entire training cluster. No peak-hardware-times-runtime conversion is used. The64GPU optimization workers are not substituted for all self-play computation either.

This scope is one 40-day random-weight training run. It excludes earlier independent20-block research used to choose architecture/search settings, separate supervised baselines and the final post-training exhibition/tournament evaluation. It includes the checkpoint-selection evaluator used to determine the self-play policy. Neural work from **both sides** of self-play and selection games is counted through all moves; no extra factor of two is needed.

## Game-length reconstruction

The original supplementary ZIP’s “Extended Data Figure 5” directory supplies 20 games, one from the best network in each successive two-day period. All 20 terminate by resignation. Counting SGF move nodes gives mean **243.95**, range138–499. These are 2-hour exhibition games. They are not sampled actual1600-simulation training trajectories, and uniform periods are not necessarily uniform numbers of generated games.

Use the resigned exhibition-game mean of 243.95 as a proxy for the resignation-enabled 90% of training games. Enabling resignation does not mean all those games actually resign. For the 10% with resignation disabled, assume 350 moves, giving 0.9×243.95+0.1×350=**254.555moves per self-play game**. The 350-move value is a judgment for playing out an essentially full board, not an observed no-resignation mean. The source’s maximum is 722 moves;300–722 no-resignation alternatives are retained. Because search budget and curriculum sampling may matter more than that small branch, the calculator also reports overall 200–350 move alternatives.

Use 243.95 moves for evaluator games, transferring the same across-training sample to checkpoint-versus-incumbent play. This is a separate assumption: the released games do not measure actual checkpoint-match lengths.

Assume one fresh neural evaluation per simulation. Ordinary tree reuse does not add another evaluation at every root. The source mentions a transposition table for the40-block run but does not report hit rates or avoided network calls. Therefore the central calculation is a full-expansion reference estimate, plausibly high if cached evaluations materially reduce work; fresh fractions 0.5 and0.75 are sensitivity scenarios, not measured cache fractions. No such fraction is inferred from hardware or cost.

## Compute totals

| Component | Reconstruction | FLOPs |
|---|---|---:|
| Self-play |29M games×254.555moves×1600evaluations×forward|3.9268103832e23|
| Checkpoint evaluator |3100checkpoints×400games×243.95moves×1600evaluations×forward|1.6090991613e22|
| Weight updates |3.1M×2048positions×3×forward|6.3321795237e20|
| Total |Sum|**4.0940524788e23**|

The evaluator assumes every1000-update checkpoint receives the reported400games; asynchronous skipping is not reported. Shared-policy updates are already included by the reported update count. Source records do not provide a measured training-game-length distribution or actual unique neural-call count. `derived_assumed_inputs` is therefore essential. The workload is reconstructed from this run’s quantities, with source-informed move-length assumptions; it is not another model’s generic training cost.

## Human active learning time

The quantity is the hours a person spends actually playing and studying Go while
learning it, to the level the run demonstrated. Travel, meals, general schooling
and everything else in a Go student's day are excluded; purposeful play,
reviewing games, life-and-death problems, lessons and competition all count.

### The level the run demonstrated

The 40-day network with search reaches **Elo 5,185** on the paper's own scale and
beats AlphaGo Master 89/100; Master had beaten leading professionals 60/60. No
human holds that rating — the strongest human on the same scale sits about 1,500
Elo below it — so the human side is charged to the highest rung a person
occupies, top-professional strength, the level of the players Master beat. The
row stays `far_above` and asserts no parity.

### Span times rate

*Span.* [Lee et al. (2025)](https://doi.org/10.1038/s41598-025-98605-9) scanned 23
Go professionals certified by the Korean Baduk Association, mean age 22.8
(SD 3.3), and report a measured mean **training duration of 15.9 years (SD 3.4)**.
Go therefore begins at about 6.9 and a working Korean professional has sixteen
years of it behind them. Lee Sedol's own path agrees: [Relentless](https://cdn.online-go.com/relentless.pdf),
printed xiv–xv / one-based PDF pages 22–23, has his father assigning
life-and-death problems, amateur 5 dan by 8, dojo entry at 9, professional
qualification at 12 and a 2002 Fujitsu international title, fourteen years from
first stone to first international title. The measured cohort mean is used
because it is a cohort rather than one biography.

*Rate.* A full-time Korean baduk academy day runs from 11 in the morning to about
10 at night, eleven scheduled hours, in the
[American Go E-Journal's account of BIBA](https://www.usgo.org/news/2013/01/the-traveling-go-board-blackies-international-baduk-academy/).
Two further accounts put the same institution in the same place: the original
[AFP school interviews](https://jordantimes.com/news/features/dreams-fame-school-go)
report 12-hour practice days, and the
[AlphaGo documentary](https://www.youtube.com/watch?v=WXuK6gekU1Y), Joseph's
narration before the Kwon interview, recalls 9 am to 9 pm seven days a week.
Eight of those eleven hours are charged as active Go, the residential day also
carrying meals, rest and the evening, over 300 days a year from dojang entry at
about 9. The years before the dojang take 2 hours a day, the rate at which a
child works through problems set at home. Documentary text was inspected through
a transcript carrier, not independently watched.

| Phase | Active work | Hours |
|---|---|---:|
| Ages 6.9–9.4: home and club | 2.5 years × 300 days × 2 hours | 1500 |
| Ages 9.4–22.8: full-time Go | 13.4 years × 300 days × 8 hours | 32160 |
| Total | Rounded from 33,660 | **34000** |

Human duration is **122,400,000 seconds**. The eight-hour active share inside the
documented eleven-hour academy day is the method's one stipulation; at 6 and 11
hours the total is 26,000 and 46,000 hours. The figure is conditional on
exceptional eventual attainment. Formal instruction and human opponents differ
from AI self-play, recorded as `different_inputs_or_tools`.

`human_time_evidence` is `llm_estimate_from_data`: the span is a measured
duration for a cohort of 23 professionals and the rate is read off a documented
programme day, with no timing of anyone to a Go rating. The donor sample is
those 23 professionals.

### Superseded: 22,000 hours

The first version of this row built the same pathway from Lee Sedol's biography
alone — 4 years × 300 days × 1 hour to age 9, 3 years × 330 days × 8 hours to
12, and 7 years × 300 days × 6 hours to 19, for 21,720 hours rounded to 22,000,
or 79,200,000 seconds — and carried `llm_estimate_judgment` with a
12,000–35,000-hour pathway sensitivity. It is superseded on two counts: the
daily rates were chosen to deduct from the documented school schedules by
judgment rather than read off them, and the span rested on one player rather
than on a measured cohort. The new figure is 55% higher and sits at the top of
the old sensitivity band.

## Performance

The final network with search beat AlphaGo Master 89/100. Master had previously won 60/60 against leading professionals. Master lost no game to the professionals it played, so this indirect comparison supports `far_above` relative to top-professional human strength; it does not measure a direct Zero-versus-Lee series. The endpoint contests and opponents differ, recorded as `different_assessment`. The network’s greedy policy alone is not the playing agent used for this comparison; the learned network is deployed with search.

## Reproduction

Standard-library Python 3. Run from the published dataset with a new output file:

```sh
python3 -B research/alphago-training/recompute.py \
  --sources agent-work/sources/alphago-training \
  --output /tmp/alphago-training-recomputed.json
```

The script reads original SGFs, checks retained-source hashes and emits architecture components and workload scenarios. It does not run Go software or training. Original PDF/ZIP are retained; human sources whose direct download returned 403 have precise locators and paraphrased web-read evidence in `agent-work/sources/alphago-training/web-evidence.json`. The source-game mapping and all alternative totals are in `calculations.json`.
