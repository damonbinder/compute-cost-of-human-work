# Searchless Chess: one complete tactical puzzle

## game-searchless270m-lichess-puzzle

Estimate **2.59 × 10¹² FLOPs and 35 human seconds** to attempt one puzzle from the original 10,000-puzzle test set. The AI must enter the complete solution, stopping after a wrong move. The human baseline is an experienced tournament player solving a previously unseen board and entering the continuation.

The [original paper, Table 1](https://arxiv.org/html/2402.04494v2#S3.T1), reports 95.4% full-puzzle success for its 270M action-value transformer. The retained [puzzle collection](https://storage.googleapis.com/searchless_chess/data/puzzles.csv) spans ratings 399–2867, with mean 1460.76 and mean 2.3251 solver moves. These are puzzle ratings, not player ratings. Every supplied PGN's final board matches its FEN; the first listed move belongs to the opponent and is applied before the solver acts.

## Compute

The released evaluator scores every legal action separately. Each forward pass processes 79 positions: a beginning marker, 77 encoded FEN positions, and a discrete action. The target return bin is shifted out of the input. Attention is bidirectional, so there is no reusable causal prefix. The actual engine builder sets batch size to one; the wrapper's default of 32 does not apply.

The network has 16 layers, width 1024, eight heads, and a SwiGLU hidden width of 4096. At two operations per multiply-add, its attention projections, attention matrices, three feedforward matrices and output head cost **42,842,521,600 FLOPs per legal action**. The 128-bin output head runs at all 79 positions before the final result is selected. Scalar normalization, activation, softmax and legal-move enumeration are not individually counted; matrix work dominates this estimate.

All complete reference solutions require 614,233 legal-action evaluations, or 61.4233 per puzzle. This would cost 2.63153 × 10¹² FLOPs per puzzle. Actual unsuccessful attempts stop earlier. Their identities and failure locations are not supplied. The central estimate assumes a common independent probability of a correct decision, calibrated so the mean predicted puzzle success across actual solution lengths is 95.4%. The fitted probability is 0.979859; it gives 60.5098 evaluated actions and **2.59239 × 10¹² FLOPs** per puzzle. This is a workload assumption, not reconstructed model predictions.

The full-path estimate is 1.5% higher. Assigning all 460 nominal failures to the first decision of puzzles with the largest remaining workload gives 2.41805 × 10¹² FLOPs, about 6.7% below central. The published percentage is rounded, so 460 is a calibration count rather than a recovered exact list of failed trials. No reference state allows an earlier alternative mate that would shorten a successful solution.

The CSV records an analytic `point_estimate`, with attempt count and subset `not_applicable`. The 10,000 puzzles define the reference collection; they are not 10,000 measured compute observations. `tokens` counts 78 text/special positions per expected action evaluation, including the beginning marker and FEN positions. The discrete action position remains in the operation calculation. `encoder_processed` describes this bidirectional discriminative transformer despite the implementation's `transformer_decoder` function name.

## Human time

[Sheridan and Reingold (2014)](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2014.00941/full) timed 17 experts solving eight unfamiliar board problems each. Mean decision time was 28.946 seconds, with 93% best-move selections. The experts' mean Canadian rating was 2223. They pressed a button when decided, then reported their move verbally; no expert reached the three-minute limit.

Use about 29 seconds to recognize the motif and verify the line, plus six seconds to enter and check its short continuation: **35 seconds**, with 15- and 90-second alternatives. Planning the continuation is largely part of the initial decision, so the donor time is not multiplied by every move. The 136 donor attempts include all outcomes. The target remains an estimated transfer, not a measured mean on these Lichess puzzles.

A broad expert-quality `match` is supported by the two task outcomes, with `different_assessment` identifying the transfer. The 93% and 95.4% figures come from different problems and endpoints; their small difference does not establish which side is better. Further source details and the separate online-game timing reconstruction are in `human-helper/human-and-helper.md`.

## Model

Exact architecture parameters total **270,730,368**, including token and position embeddings, normalization and the output head. The registry's 2P coefficient is a reference approximation; this row uses the full operation recipe above.

The first public repository commit, [April 10, 2024](https://github.com/google-deepmind/searchless_chess/blob/d5aab18b59c84f2defc71673b3e76d517b0cff2c/checkpoints/download.sh), links the complete 270M checkpoint. Public object metadata records its creation the previous day. Use April 10 as the best supported public availability date, not the paper date. First-release and current neural implementation bodies agree apart from copyright text; weights were not downloaded or executed.

The separate 2895 rating against human players involved occasional Stockfish assistance when the network's best moves were all predicted overwhelming wins. It is not used for this pure-network puzzle point. Neither that helper's call frequency nor its runtime can be recovered from game moves alone.

## Reproduction

`puzzle_workload_review.py` takes explicit `--sources` and `--output` paths and requires the `chess` package. Its retained result is `puzzle-workload-review.json`. `count_workload.py` independently counts the separate 62,829 held-out board positions; those positions are a source audit, not the puzzle workload. The human aggregate script and result are in `human-helper/`. Source URLs and hashes are in `neural-source-manifest.json` and the human source locators. No model execution or API calls are required.
