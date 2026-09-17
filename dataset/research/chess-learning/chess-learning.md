# Learning chess to a stated rating

*Created 2026-09-14 12:12.*

Four rows compare the compute that trained a chess network to the hours a human
spends reaching the same rating. The proficiency target is an Elo rating, which
is the one quantity both sides are measured in, so nothing has to be translated
between an AI benchmark and a human test. Two things still have to be bridged:
Lichess blitz ratings and FIDE ratings are different pools, and the human hours
come from surveys of over-the-board tournament players.

| Row | Model | Training FLOPs | Lichess blitz | FIDE equivalent | Human hours |
|---|---|---|---|---|---|
| game-chess-train-searchless270m | Searchless Chess 270M | 5.26e21 | 2895 | 2406 | 15213 |
| game-chess-train-maia1100 | Maia 1100-bin | 1.19e17 | 1417 | 1218 | 1165 |
| game-chess-train-maia1500 | Maia 1500-bin | 1.19e17 | 1489 | 1276 | 1320 |
| game-chess-train-maia1900 | Maia 1900-bin | 1.19e17 | 1621 | 1382 | 1661 |

Every number in the table comes from `chess_learning_calc.py`, whose retained
output is `agent-work/derived/chess-learning/chess-learning-calc.json`.

## Compute

Both recipes count a forward pass from the published architecture, take the
backward pass as twice the forward, and multiply by the reported number of
training examples. Neither involves an assumed parameter count.

### Searchless Chess

[Ruoss et al. (2024)](https://arxiv.org/html/2402.04494v2) train a decoder-only
transformer without causal masking, with post-normalization and SwiGLU. Section
A.2 gives the largest configuration as 16 layers, 8 heads and an embedding
dimension of 1024 with a widening factor of 4, and the training budget as 10
million steps at batch size 4096, which is 2.67 epochs over the 15.3 billion
annotated action-values.

One input sequence is 79 positions: a beginning marker, 77 encoded FEN
characters, and the discrete action whose value is predicted. Per position and
per layer the weight matrices cost 32d² FLOPs — four d×d attention projections
and three d×4d SwiGLU matrices, at two operations per multiply-add — and the two
attention matrix products cost 4·d·79. The 128-bin output head runs at every
position, adding 2·d·128. For d = 1024 and 16 layers that is 542,310,400 FLOPs
per position and **42,842,521,600 FLOPs per forward pass**, which reproduces
exactly the figure derived independently from the released implementation in
[the puzzle note](../searchless-chess/searchless-chess.md#compute).

Training processes 10⁷ × 4096 = 4.096 × 10¹⁰ sequences. At three times the
forward cost the run is **5.2645 × 10²¹ FLOPs**, over 3.2358 × 10¹² processed
text positions.

The 9M and 136M models are not built as rows; see the dispositions below.

**What the figure leaves out.** Stockfish 16 annotated all 15.3 billion
action-values at 50 ms per state-action pair. That is the teacher the network
distills, and it is the larger part of the real cost of producing this
capability, but it is integer alpha-beta search rather than floating-point
arithmetic and the repo has already ruled that node counts do not convert to
FLOPs (see the Deep Blue disposition in
[the chess inference note](../games-memory/chess.md#game-chess-move-deepblue)).
The recorded compute is therefore the network's own training arithmetic, not the
end-to-end cost of the pipeline that produced the policy. Evaluation play on
Lichess is a few hundred games and is negligible against 10⁷ training steps.

### Maia

[McIlroy-Young et al. (2020)](https://arxiv.org/abs/2006.01855), Supplement 7.1
and Table 3, train nine networks, one per 100-point Lichess rating band from
1100 to 1900. Each sees a training set of 12 million games and runs 400,000
steps at batch size 1024, which is **4.096 × 10⁸ sampled positions**. The
architecture is 6 residual blocks of two 64-channel convolutions, identical
across the nine bands: all nine `config.yaml` files in the release commit are
the same 176 bytes.

One forward pass costs 77,829,166.08 FLOPs. That figure was established from the
released weights in
[the Maia inference note](../games-memory/chess.md#maia-compute) and is reused
unchanged. Training adds one term the inference row deliberately excludes: the
training graph maps the policy head's 8×8×80 logits onto 1858 move classes with
a dense one-hot matrix, costing 2 × 5120 × 1858 = 19,025,920 FLOPs per position.
Lc0 does that mapping as an index selection at inference time, so it belongs in
the training count and not the inference count. The training forward pass is
therefore 96,855,086.08 FLOPs, and at three times that over 4.096 × 10⁸
positions the run is **1.1902 × 10¹⁷ FLOPs**.

Converting the Lichess PGN archive into the model's input format took about
seven days on an 80-core server. That is data preparation, not neural
arithmetic, and it is excluded on the same reasoning as the Stockfish
annotation.

All nine models share this budget, so the three Maia rows carry the same
compute and differ only in the rating reached. That is the point of the ladder:
a single training recipe lands on three different human proficiencies.

## Ratings and the pool bridge

The AI side's rating is the one the model actually holds, never the one it was
aimed at. Maia's authors caution that the rating of the training players is not
the engine's playing strength, and the bots bear that out: the model trained on
1900-rated games plays at Lichess blitz 1621.

| Model | Rating source | Games | Lichess blitz |
|---|---|---|---|
| Searchless Chess 270M | Ruoss et al. Table 1, vs. humans only | 174 | 2895 |
| Maia 1100-bin | [maia1](https://lichess.org/@/maia1) | 436223 | 1417 |
| Maia 1500-bin | [maia5](https://lichess.org/@/maia5) | 198686 | 1489 |
| Maia 1900-bin | [maia9](https://lichess.org/@/maia9) | 207631 | 1621 |

Bot profiles were retrieved on 2026-09-14; all three carry a rating deviation of
45, so none is provisional. The maia5 figure was 1486 when the inference row was
built two days earlier.

**Lichess blitz is not FIDE.** The two scales are separate pools and the offset
between them varies with strength. The bridge used here is the blitz-only
least-absolute-deviation model from
[the Lichess rating converter](https://ethanlebowitz.github.io/RatingConverter/about.html),
fitted to about 28,000 Lichess accounts that list a FIDE rating in their
profile, after dropping accounts with fewer than 50 games and residuals beyond
two standard deviations:

    FIDE = 78.643 + 0.80397 × Lichess blitz

Its Pearson correlation is 0.538 to 0.626 across the four single-rating models,
and the FIDE side is self-reported, so this is the weakest link in the chain.
A sensitivity is carried on every row: a flat 100-point discount instead of the
fitted line, which is roughly what
[the ChessGoals comparison](https://chessgoals.com/rating-comparison/) implies
at intermediate strength, raises the human hours by 24% to 35% at the Maia
ratings and by 2.3× at 2895. The fitted model is the central because it rests on paired
within-player observations rather than on matching two populations' percentiles.

## Human learning time

Two surveys measure cumulative chess hours against rating. Neither reports a
mean at each of our four targets, so both are read as curves and the central is
the geometric mean of the two readings.

**[Charness et al. (2005)](https://onlinelibrary.wiley.com/doi/10.1002/acp.1106)**
surveyed two independent samples of tournament-rated players, N = 239 and N =
180, recruited in Canada, Germany, Russia and the United States, who reported
hours per typical week for every year since learning the game. Ratings were
converted to the Elo scale. Tables 1 and 2 give, for the list-wise samples of
200 and 164, a mean rating of 2032 (SD 278) and 2008 (SD 253), a mean log₁₀
cumulative serious study alone of 3.4 (SD 0.5) and 3.5 (SD 0.4), and a mean
log₁₀ cumulative tournament play of 3.5 (SD 0.4) and 3.5 (SD 0.5).

The statistic we want is the conditional mean of hours given rating — how much a
player at rating R accumulated — so the slope is that of log hours on rating,
r·SD(log hours)/SD(rating): 0.000971 and 0.000759 log₁₀ units per Elo point,
averaging to one decade of hours per 1156 Elo points. Anchoring at the pooled
sample mean, rating 2020 with 5999 geometric-mean hours of study plus tournament
play:

    H_Charness(R) = 5999 × 10^((R − 2020) / 1156)

**[Gobet and Campitelli (2007)](https://bura.brunel.ac.uk/bitstream/2438/611/1/Gobet_DevPsyc_Final.pdf)**
surveyed 104 Argentinian players from weak amateurs to grandmasters, ratings
1490 to 2473. For the 34 players whose rating archives show when they crossed
Elo 2200, the mean cumulative total practice at that moment was 11,053 hours
(SD 5538, range 3016 to 23,608). This is the better statistic in kind, because
it is hours *to reach* a stated rating rather than career hours at a current
rating, but it exists at one rating only. Their Table 1 supplies a slope from
group means of cumulative total practice — 8303 hours at rating 1780, 11,715 at
2030, 19,618 at 2165, 27,929 at 2300, N = 89 — giving one decade of hours per
987 Elo points:

    H_Gobet(R) = 11053 × 10^((R − 2200) / 987)

The two curves are built from different samples, different countries, different
decades and different activity definitions, and they agree within 30% across the
whole range: at Elo 2200 Charness gives 8512 hours against Gobet's measured
11,053. The row's human time is their geometric mean, following the dataset's
rule for two defensible transfers from one evidence base.

| Target | FIDE | Charness (h) | Gobet (h) | Central (h) | Flat-100 bridge (h) |
|---|---|---|---|---|---|
| Searchless 270M | 2406 | 12946 | 17878 | 15213 | 35270 |
| Maia 1100-bin | 1218 | 1214 | 1118 | 1165 | 1444 |
| Maia 1500-bin | 1276 | 1362 | 1280 | 1320 | 1687 |
| Maia 1900-bin | 1382 | 1683 | 1639 | 1661 | 2244 |

`human_attempts` is 409: the 375 players in Charness's combined regression
sample plus Gobet's 34.

The row's range takes the lower of the two curve readings as `human_time_low` and the
flat-100-point bridge as `human_time_high`: 12,946 and 35,270 hours for Searchless
270M, 1,118 and 1,444 for Maia 1100, 1,280 and 1,687 for Maia 1500, and 1,639 and
2,244 for Maia 1900.

**What the human number is and is not.** It is active hours of study and of
competitive play, counted from the year a player took up chess, by people who
did reach the rating. Players who put in the hours and never got there are
excluded, which pushes the figure down; Gobet reports sample members with more
than 25,000 hours who never made master. All hours are retrospective
self-reports, which Charness notes tend to overstate actual practice. Both
samples are over-the-board tournament players, so the three Maia rows, at FIDE
equivalents of 1218 to 1382, extrapolate the curves below the weakest player in
either sample; those rows carry `different_human_baseline` for that reason.
Charness's ratings are mid-1990s Elo and Gobet's are late-1990s Argentinian
national ratings calibrated to Elo at r = 0.89, so neither is on today's FIDE
list.

## What is not built

- **Searchless Chess 9M and 136M.** Their only Lichess ratings, 2054 and 2156,
  come from the pool in which fewer than 4.5% of games were against humans.
  On the one model measured in both pools the gap is 596 points, 2299 against
  bots and 2895 against humans, so a bot-pool rating pushed through a
  human-pool conversion would not be the same proficiency as the human side's.
  Their training compute is 1.6978 × 10²⁰ and 2.6335 × 10²¹ FLOPs, already
  computed in the script, if a later ruling accepts the bot-pool rating.
- **Maia 1200 to 1800.** Six of the nine released models have no published or
  deployed playing strength, only move-matching accuracy, so there is no rating
  they demonstrably reach.
- **[Maia-2](https://arxiv.org/html/2409.20553v2).** Reports move-matching
  accuracy against rating-grouped test sets and no playing rating of its own.
- **Leela Chess Zero networks.** Ruoss et al. Table 1 gives them Lichess
  ratings, but against bots, and no training budget is stated for the specific
  networks tested.
- **AlphaZero chess.** Its training budget is recoverable but it has no rating
  on a human scale, so it cannot carry a rating-matched human baseline.

## Reproduction

`chess_learning_calc.py --output <path>` writes every figure above and needs
only the standard library. Retained sources are under
`agent-work/sources/chess-learning/`: the two paper HTML captures and their text
extracts, the Charness and Gobet PDFs, the three Lichess bot profile JSON
responses, the release-commit tree listing, and the rating converter's model
file and methodology page.
