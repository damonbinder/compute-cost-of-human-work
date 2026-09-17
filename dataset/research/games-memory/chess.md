# Chess

## The clock convention

Every chess and Go row in this dataset whose human time comes from a game clock reads
that clock the same way, ruled 2026-09-17: **the own-clock figure is the central, and
the own-clock-plus-opponent-clock figure is the upper bound.** Twelve chess rows are
governed—`game-chess-alphazero`, `game-chess-move-maia`, `game-chess-move-gpt35`,
the nine `game-chess-move-arena-*` rows—together with the three AlphaGo Zero move
rows in `../alphago-zero/alphago-zero.md`, which used to read the same arithmetic the
other way round and put their central at the engagement-inclusive end.

What the clock measures settles it. The own clock is the elapsed interval in which it
is the player's turn; own clock plus the opponent's is the whole elapsed move cycle,
and the standing rule is that elapsed time is an upper bound on active time, with a
central at the ceiling needing an argument that people use the whole allowance. The
engagement-inclusive reading is that ceiling by construction, so it is the high bound.
The own clock is the reading the sources actually measure—the Lichess aggregates
behind the Maia, Game Arena and GPT-3.5 rows are own-clock means over tens of millions
of moves—and its two errors run in opposite directions: it counts move entry and any
lapse inside the player's own turn, and it counts none of the thinking done on the
opponent's turn. Taking it as the central asserts that those two roughly offset, which
needs no unmeasured multiplier; taking the engagement-inclusive figure as the central
needs a pondering fraction nobody has measured.

The convention moved three centrals, the AlphaGo Zero move rows from 120 seconds to 60.
It moved none of the chess centrals, which already sat on their own-clock figure. The
Maia and Game Arena rows keep the bounds they already carry, because those bounds answer
a different open factor—which blitz control a representative decision comes from—and
the convention does not require reopening them.

## game-chess-alphazero

[Silver et al. 2017 v1](https://arxiv.org/html/1712.01815), Table 1 and Methods: AlphaZero scored 28 wins, 72 draws and zero losses in 100 games against Stockfish 8 at one minute per move, without pondering. Reported search speed is 80,000 positions/second. The selected work unit is **one representative 60-second chess decision from that match configuration**, not a whole game or its training.

**Human judgment:** allocate the same 60 seconds of active consideration to a world-class player on the same class of positions. This is an assumed budget, not a measured human average. AI above is a strength transfer from its result against the contemporary champion chess engine; the paper describes top computer engines as superhuman. This is not a direct AlphaZero-versus-human trial or proof that every individual move is better. Flag different_assessment for the engine-match evidence.

**Range: 60 to 120 seconds** (2026-09-17). The match ran one minute a move for each side, so the own clock is 60 s and the whole elapsed move cycle is 60 + 60 = 120 s. Under the convention above the own clock is the central and the elapsed cycle is the ceiling, so the bar runs from the central to 120 s. The low sits at the central because 60 s is a floor for this player on this control: a world-class player given a fixed minute on each move of a serious match spends it, so idle time inside the own turn is small, and analysis during the engine's minute is nonnegative. The same arithmetic now runs the same way on Lee Sedol's clock in `../alphago-zero/alphago-zero.md#human-active-time`, where the own clock is also 60 s and the cycle is 128.1 s because AlphaGo used more of its budget than Lee did.

### AlphaZero compute

Architecture: 8×8 board, 119 input planes; 20 residual blocks, two 3×3 convolutions of 256 channels each, plus stem. The original paper inherits AlphaGo Zero architecture; [MuZero Appendix F](https://arxiv.org/html/1911.08265#A6) explicitly contrasts its 16-block network with AlphaZero's 20 blocks. Count trunk convolutions as 2×64×[119×256×9 + 40×256×256×9] = **3,054,993,408 FLOPs per evaluation**. Allocate a further 2% for policy/value heads, normalization and activation, rather than assuming these vanish. These small heads are orders of magnitude smaller than the repeated 256-channel trunk convolutions.

Assume the reported position rate represents approximately one fresh neural evaluation per searched position, as in a cached MCTS expansion. Then 60×80,000 = 4,800,000 evaluations, times 3,116,093,276.16 FLOPs = **1.4957247725568e16 FLOPs per decision**. This is a dense-network arithmetic estimate, not measured executed hardware instructions or TPU peak utilization. Transpositions, terminal positions and rate variation make it approximate. Search-control scalar arithmetic is small compared with billions of neural operations per node. Reproduce via `research/calculations.py`.

No rollout training, backpropagation or historical self-play is included in this inference point. A separate future full-training point would need its own human learning interval and quality comparison; the lead's combined “move + training” description is split rather than summed.

## game-chess-move-deepblue

Disposition: unsuitable for a defensible FLOP conversion from the available metric. The [original Campbell, Hoane and Hsu paper](https://sjeng.org/ftp/deepblue.pdf), sections 2–3 and tables 4–5, describes 480 specialized search chips, custom evaluation tables/registers and 126 million positions per second averaged over searches longer than one minute in the 1997 match. The 3.5–2.5 victory over Kasparov is direct performance evidence, but node counts are not floating-point operation counts. Neither the system's CPU peak GFLOPS nor arbitrary FLOPs/node represent this custom lookup/logic workload. No zero-compute row is invented. Reconsider only with an appropriate metric specification or original executed floating-operation accounting.

## game-chess-move-gpt35

Reconstructed and incorporated from the original historical game logs. The [new chess record](../gpt35-chess/gpt35-chess.md) estimates 4.7445e12 FLOPs per post-opening move versus 4.3 seconds of strong-club fast-blitz own-clock time. It includes estimated continuations/retries, excludes two structurally ambiguous transcripts and replaces the unsupported engine-to-human Elo conversion with separate human-match evidence. The model’s 7B active-size prior is explicitly uncertain.

## game-chess-move-maia

The original [Maia repository](https://github.com/CSSLab/maia-chess), README, says to use one node without tree search and identifies maia5 as Maia-1500. It also cautions that the rating of training players is not necessarily the engine's playing strength. The [public bot profile](https://lichess.org/@/maia5), retrieved 2026-09-12, identifies the original 1500-trained model and reports blitz rating 1486 across 198355 games. That is actual playing evidence, not the paper's move-prediction accuracy. Use broad match to ordinary approximately 1500-rated online blitz players. Ratings are pool-specific; no FIDE conversion is made. Profile results cover a live bot with an opening book, while this work unit is one representative **post-opening decision** by its single-node network. This is a qualified transfer of whole-game playing strength, flagged different_assessment.

**Human duration estimate:** use **7.1 seconds**, transferred from the original [Russek human-game timing aggregates](https://github.com/evanrussek/Thinking_Time_VOC_Chess/tree/0f21b31c05bec0494bc3c5da2e14c0be55fa345e). In five-minute games without increment, the (1250,1525] rating bin has a count-weighted mean of 7.090367734 seconds across 27,844,861 recorded move observations. This bin contains the approximately 1500 target; the adjacent (1525,1800] bin gives 6.935 seconds. Source preprocessing restricts to plies 15–75 and retained value-of-computation cells. No successful-outcome selection applies.

**Range: 4.5055 to 10.6315 seconds.** Unchanged by the 2026-09-17 clock convention, which puts this row's central where it already sat. Maia-1500's public bot is a blitz bot and its 1486 rating pools every blitz control Lichess runs, so which control a representative decision comes from is the open factor and the source measures it. The same (1250,1525] bin's count-weighted own-clock mean is 4.5055 s at 180+0 over 16,037,631 moves and 10.6315 s at 300+3 over 18,301,318 moves, against the 7.0904 s at 300+0 the central uses. Those two are the bounds; both are measured, and the central sits between them. Added 2026-09-17.

This is an estimated transfer from a broader player bin and position cohort, not a measured target-task average. Own-clock intervals include move entry and possible distraction but omit thinking during the opponent's turn. Treating them as active decision effort is an explicit proxy. The previous clock-budget calculation has been replaced by this empirical timing evidence; no guessed multiplier for pondering is added. The independently replayed source counts and script are in [the shared human timing note](../searchless-chess/human-helper/human-and-helper.md), with source data under `agent-work/sources/searchless-chess/human-helper/`.


### Maia compute

Retained `agent-work/sources/maia-chess-master/` contains released `maia_weights/maia-1500.pb.gz`. Tensor dimensions were checked against the protobuf field definitions; `agent-work/sources/games-memory/maia-shapes.json` records counts: six residual blocks; input 64512 convolution weights (=112×64×3×3), policy convolutions 36864 and 46080 (=64×64×9 and64×80×9), value convolution 2048 (=64×32), dense value matrices262144 and384 (=2048×128 and128×3). This verifies the actual released model, not the paper's accidentally swapped prose for value and policy heads.

Original `move_prediction/maia_chess_backend/maia/tfprocess.py` and `maia_config.yaml` specify squeeze-excitation ratio8: per block64→8→128, used to scale/shift64 channels. Convolutions cost75759616 FLOPs; dense and squeeze-excitation matrices543488. Allocate2% for pooled statistics, channel scaling, activation and normalization: **77829166.08 FLOPs** for one forward. Lc0 inference's policy mapping is an index selection of legal move logits; do not charge the training TensorFlow implementation's dense one-hot mapping matrix as an extra learned layer. Both value and policy heads are included even though a single-node move principally uses policy. Count one network evaluation with the cached game history; no training or opening-book work is added.

**Model release:** 2020-06-03. The [preliminary public release commit](https://github.com/CSSLab/maia-chess/commit/61b571905aeffa9112bc5196e6d3bc6f26916dfe) contains `model_files/1500/final_1500-40.pb.gz`. Its Git blob, `651551e2603c3efba9c6ded3b87da302c40722fb`, matches the retained 1,258,199-byte model exactly. The January 2021 commit renamed those same weights to `maia_weights/maia-1500.pb.gz`; the later release tag does not mark their first availability. Commit and tree responses are retained under `agent-work/sources/games-memory/maia-release/`. An independent reviewer verified the file identity and date.

## Other node-limited chess leads

[Meloni's original 2021 experiment](https://www.melonimarco.it/en/2021/03/08/stockfish-and-lc0-test-at-different-number-of-nodes/) and its graph were inspected; retained `agent-work/sources/games-memory/meloni-2021-nodes.png`. Lc0 67743 crosses the2830 anchor between10nodes(~2550) and50nodes(~2880), roughly40nodes by logarithmic interpolation. This remains pending: recover exact network architecture and assess how the Fruit2.2.1/SSDF hardware-and-time calibration transfers to contemporary human strength. A rating interpolation is not itself observed human parity. Stockfish leads also require deciding how to represent integer NNUE/search rather than inventing FLOPs per node. No rows are added from those leads yet.
