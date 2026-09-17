# AlphaGo Zero: two observed inference settings

The candidates use the final 40-block, 40-day network from [Silver et al. (2017)](https://www.nature.com/articles/nature24270). They represent one move, excluding training. The existing 20-block, three-day, 1,600-simulation entry already covers the smaller search player; it is not duplicated here.

The complete paper is retained as `agent-work/sources/alphago-zero/silver-2017.pdf`, from the [coauthor's publicly linked copy](https://drive.google.com/file/d/1XN0QXdYKjbuMuVnQ7ASb6oxVo7DHy1Hx/view). The linking [author page](https://www.julian.ac/about/) is retained. Methods, rather than the abbreviated block names in the body, defines the architectures. The original publisher's supplementary SGFs are also retained. They contain board moves and two-hour match controls but no per-move clocks or search counts; they cannot establish the workload of the separate fast evaluation.

## alphago-zero-40block-40day

Methods, Neural network architecture (PDF pp.8–9): 19×19×17 input; a 256-channel 3×3 stem followed by **39 residual blocks**, each containing two 256-channel 3×3 convolutions. Thus “40-block” means one stem and 39 residual blocks, not 40 residual blocks after the stem. The 20-block network instead has 19 residual blocks.

The policy head has a two-channel 1×1 convolution and a 722→362 linear layer. The value head has a one-channel 1×1 convolution and 361→256→1 linear layers. Batch normalization and rectification follow the indicated convolutions; each residual block adds its input. Both heads are counted. Removing the unused value head for greedy policy play saves only 371,773 operations, about 0.0011%.

Count two operations per multiply-add, affine batch normalization as two operations per output, residual additions, linear biases, and one operation per rectifier, exponential, or tanh. Convolution biases are folded into batch normalization. This is a logical neural operation convention, independent of precision or hardware speed; it excludes integer board rules, tree bookkeeping, memory movement and argmax comparisons. Fused normalization or a different special-function convention changes little compared with the convolutions. No language-token coefficient applies.

The calculation yields **33,271,582,274 FLOPs per complete forward pass**. It uses 79 tower convolutions. Full trained weights were not publicly released in the inspected sources; the release date is blank. The October 2017 paper and announcement dates are not model-availability dates.

## Human active time

The baseline is a world-class professional choosing a representative move during serious long-clock play. It is not a claim that a human could reproduce the search player's superhuman strength by spending more time.

[Fan Hui's original DeepMind game-1 commentary](https://deepmind-media.storage.googleapis.com/alphago/pdf-files/english/ls-vs-ag1/LS%20vs%20AG%20-%20G1%20-%20English.pdf) reports clocks at several points in Lee Sedol's game. Through move 73, Lee had made 37 moves. His remaining clock was 83 minutes; AlphaGo's was 78 minutes, from 120 each (PDF p.22). Thus Lee used 37 minutes on his own clock while the opponent used 42 minutes. The first smoking break is described after move 77 (p.24), outside this prefix.

Dividing Lee's own clock by his moves gives 60 seconds per move. AlphaGo's 42 minutes over the same 37 moves is 68.1 seconds. Adding half the opponent's clock gives 94.1 seconds; sustained engagement on both turns gives 128.1 seconds, which is the whole elapsed move cycle. The retained inputs give every clock and page locator.

Use **60 seconds**, Lee's own clock, as the active-effort point estimate, with **60 to 128.1 seconds** as the range. This replaces the earlier 120-second central on 2026-09-17, under the convention that the own-clock reading is the central and the engagement-inclusive reading is the ceiling; `../games-memory/chess.md#the-clock-convention` states the convention and the rows it governs.

The reasoning is the same one the clock arithmetic already sets out, read the other way round. Own clock plus the opponent's clock is the whole elapsed interval of a move cycle, 60 + 68.1 = 128.1 seconds here, and elapsed time is an upper bound on active time. A central at 120 seconds is 94% of that ceiling, and the argument for it—that Lee analyzed throughout AlphaGo's turn—is an assumption about an engagement fraction nobody measured. The own clock is measured. Its two errors run in opposite directions: it counts move entry and any lapse inside Lee's own turn, and it counts none of the thinking he did on AlphaGo's. Taking it as the central asserts that those two roughly offset, which needs no unmeasured multiplier, and it leaves the engagement fraction where it belongs, in the upper bound.

The low sits at the central because the own clock is a floor here. This is game one of a title match: the player is at the board, the first smoking break falls after move 77 and outside the prefix, so idle time inside his own turn is small, and thinking on the opponent's turn is nonnegative. Active time is therefore at or above 60 seconds and at or below 128.1. The 94.1-second half-engagement reading sits inside the interval and is not a separate bound. Earlier overlapping prefixes at moves 30, 33, 39, 57, 61 and 67 imply 126-141 seconds with full engagement, 59.0 to 66.0 on the own clock at the same 2.135 ratio; they are consistency checks within one game, not independent samples. This transfer from one opening/middlegame prefix does not establish a full-game mean, an average over all professionals, or identical effort in quick endgame moves. Classification: `transferred_timings`, `estimated`, `point_estimate`; the donor comprises 37 human move attempts, subset all, timed cumulatively in one game prefix. These are not 37 independently timed intervals; overlapping checkpoints do not add attempts.

## game-go-alphagozero-40block-policy

One greedy move from the final 40-block network, selecting maximum policy probability without MCTS. Figure 6b and Final performance (PDF p.5) report **Elo 3055** for this actual player, versus AlphaGo Lee 3739 and AlphaGo Fan 3144 in the same anchored scale. The scale includes AlphaGo's matches with Lee Sedol and Fan Hui (Methods, Evaluation, p.9). The raw policy is below the elite baseline: the gap is large, and it is near the older Fan-level program rather than the Lee/Master level. This is a qualitative inference from the human-anchored tournament, not an observed raw-policy match against Lee Sedol.

Compute is one forward pass: **33,271,582,274 FLOPs**. The source specifies one greedy policy, not an eight-symmetry ensemble. It does not report pruning the value head, so the complete network is counted. The architecture and workload support `derived_supported_inputs`.

## game-go-alphagozero-40block-1600

One move using the final 40-day network with 1,600 MCTS simulations, selecting the most-visited move. Figure 6a's caption explicitly describes the **40-block** learning-curve evaluations as approximately **0.4 seconds per search**. Methods, Evaluator (p.8), specifies 1,600 simulations and deterministic maximum-visit selection. The final learning-curve point is around Elo 5000 and lies above both human-anchored Lee and Master baselines. Classify above world-class human play. Do not substitute the separate 5-second tournament's exact 5185 rating or the two-hour match's 89–11 result for this configuration.

The nominal recipe is `1600 × 33,271,582,274` = **53,234,531,638,400 FLOPs**. Each new leaf receives one joint policy/value evaluation. The paper's batch size of eight means eight positions per batch, not eight evaluations of every position, and its random symmetry selects one transform per leaf. There are no rollout networks.

The search retains the chosen child and subtree between moves, so do not add a fresh root or charge for re-evaluating inherited nodes. The 40-block player additionally uses a transposition table. The paper does not publish its hit rate or whether a hit bypasses a network call; terminal leaves also need not call the network. Therefore 1,600 full evaluations is a **nominal estimate**, not a measured count. Use `derived_assumed_inputs` for this mapping from simulations to calls. Scenarios in the calculation reduce new evaluations by 25% or 50%, giving 39.93 or 26.62 TFLOPs; those fractions are sensitivity choices, not source observations. Without native search traces there is no evidence-based correction factor to prefer over the nominal recipe.

Both rows flag `different_assessment`: AI quality comes from a tournament/learning-curve rating while human timing comes from an elite long-clock game prefix. The human-anchored scale supports the directional judgment, but neither configuration has direct human move-quality observations paired with these timings. No different-human-baseline flag is needed: timing and the quality anchor concern elite professional play.

## Excluded interpretations and overlap

- Eight simulations as a top-human parity threshold is not a reported result. The actual raw-policy and 1,600-search results bracket very different strengths; interpolating between them would not establish a tested parity point.
- The 20-block, 1,600-search configuration is already `game-go-alphagozero-1600`. Fresh reconstruction gives 16,224,526,914 FLOPs per pass versus the existing 16,224,527,019, a 105-operation difference in small elementwise allowances (0.00000065%). Its architecture and nominal search treatment agree. No production correction is warranted for that convention difference.
- The 5-second final tournament reports quality but not call counts. The 40-block caption supplies its own approximate 0.4-second calibration; correcting that stated duration by the 20/40 architecture ratio would contradict the source. Linear extrapolation gives 20,000 nominal calls, but batch occupancy, retained trees, transpositions and timed-search overhead could change throughput. This extrapolation is calculated only for audit and is **not** a candidate point.
- There is no learning row: a human-time endpoint at the final superhuman capability is not established by generic years spent studying Go.

## Reproduction

`python3 research/calculate.py sources /tmp/alphago-zero-recomputed.json`

Python standard library only. `agent-work/sources/alphago-zero/inputs.json` separates reported architecture, search, rating and clock inputs from analyst conventions. `research/calculations.json` retains component counts, engagement scenarios and the SGF audit. All paths are explicit; output can be written outside this batch.
