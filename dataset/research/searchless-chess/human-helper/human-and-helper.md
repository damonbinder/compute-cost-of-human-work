# Human puzzle timing and game helper scope

## Proposed puzzle baseline

Use **35 seconds** for a strong amateur/expert solving one previously unseen tactical puzzle and entering its short winning continuation. This is a transfer estimate, not a measured time on the model's 10,000 puzzles. Suggested fields: `transferred_timings`, `estimated`, `point_estimate`, human attempts `136`, subset `all`, skill `expert`.

Sheridan and Reingold (2014), Methods and Global Behavioral Results, tested 17 experts (mean CFC rating 2223, range 1876–2580) on eight chess problems each. Mean decision time was 28.946 seconds (SE 5.441); 93% of best-move selections were correct (SE 2%). Participants pressed a button when ready and then verbally reported the move. None of the experts reached the three-minute limit. The global timing result precedes the later correct-only eye-movement analysis; it is not identified as a successful-trials-only time. Thus the timing donor is 136 attempts, not 17 attempts or the model's 10,000 puzzles.

The study requires recognizing a tactical motif and selecting the best move from a novel board. Examples involve mate, material gain and defensive moves. That initial decision already requires considering continuations. I retain approximately 29 seconds for this work and allow approximately six seconds to enter/check the remaining short line, rounded to 35 seconds. I do not multiply 29 seconds by every move. The target puzzle sample has mean 2.3251 model turns and mean Lichess puzzle rating 1460.7603 according to the separate source reconstruction. CFC player ratings and Lichess puzzle ratings are not interchangeable.

Use 15 and 90 seconds as alternative fast-recognition and harder-puzzle scenarios, not confidence limits. The 93% first-move accuracy is evidence for a broad expert-quality match to 95.4% model full-puzzle success; it is not a directly matched 93% versus 95.4% comparison. The source problems and endpoint differ. A `different_assessment` flag is appropriate for the quality transfer. Do not claim that the timed experts achieved 95.4% on these Lichess puzzles.

Original source: https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2014.00941/full . The retained human-source folder contains `sheridan2014.pdf` and its text extraction. DOI 10.3389/fpsyg.2014.00941.

## Online-game clocks: useful cross-check, not the puzzle donor

Russek (2025), DOI 10.1111/cogs.70119, publishes small aggregate timing tables and their construction code at https://github.com/evanrussek/Thinking_Time_VOC_Chess . Retained revision: `0f21b31c05bec0494bc3c5da2e14c0be55fa345e`.

The original code takes the difference between consecutive clocks for the same player and adds the increment. It restricts analysis to plies 15–75. These are own-clock intervals, excluding thinking on the opponent's turn; they do not measure attention. No clock budget is substituted for observed mean time. These observations support ongoing-game timing, not 29-second isolated puzzle decisions.

`recompute-human.py` verifies each used CSV's Git blob hash against the retained tree and combines the source `rtmean` and `rtcount` cells with count weighting over the eleven disjoint original job shards. It uses `aggregate_voc_vs_rt`, not the similarly named older aggregate directory. This pooled mean is not the paper notebook's equally weighted mean of monthly cells. The original aggregate code separates January controls into jobs and later months into other jobs; the script does not count repeated empty January files as observations. Raw participant deduplication cannot be independently repeated from these aggregates.

For the source rating bin (1800,3000], the pooled means are 4.3100 seconds at 180+0, 6.9991 at 180+2, 6.9088 at 300+0 and 11.0617 at 300+3. The source label `2400.0` is a bin midpoint, not the observed average rating. These figures are contextual checks only and do not enlarge the 136 puzzle timing donors.

Replay with explicit paths:

```sh
python3 /path/to/research/human-helper/recompute-human.py --sources /path/to/sources/human-helper --output /absolute/new/output.json
```

Pass the retained human-source directory explicitly; no particular working directory is required. The output must not already exist or be inside the input directory. All 88 contributing aggregate file hashes and counts are in `research/calculations.json`.

## Why the human-game rating is not a pure-network result

The original searchless-chess paper's discussion of overwhelming victories explicitly says that when all top five predicted moves exceed 99% win probability, Stockfish checks the position and, if it agrees, selects its preferred move among those five. The 2895 rating over 174 human games therefore describes a system with this helper. Released `neural_engines.py` does not implement that fallback. A PGN cannot recover the network's five probabilities or whether the helper agreed. The frequency of oracle >99% positions in a separate test set is not the trigger frequency, and the data-generation oracle's 50-ms budget does not establish the live helper's budget.

Use the original pure-network puzzle evaluation for the proposed observation. Do not attach the 2895 human-game rating to its FLOPs. A whole-game estimate would need a disclosed helper workload reconstruction that the retained evidence presently does not supply.
