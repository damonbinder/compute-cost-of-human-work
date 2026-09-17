# GPT-3.5 Instruct: compute per post-opening chess move

The operating point is **4.7445 × 10¹² FLOPs per accepted move**, compared with **4.3 seconds of human own-turn time** in fast blitz. Compute includes estimated unsuccessful calls allocated within the same source games. The model's active size, 7B, is a weak transfer from a later chat model; it dominates the uncertainty.

## Original workload and source scope

The pinned [original games CSV](https://github.com/adamkarvonen/chess_gpt_eval/blob/9c704987b2b45c363a22a2fedb6bbee8fd31c441/logs/games.csv) contains 182 GPT-3.5 Instruct games. We select 180 whose move-number formatting agrees throughout with the legal board state. Two records are excluded because their formatting makes the historical caller attribution uncertain:

| Game ID | Source inconsistency | Reported model illegal counter |
|---|---|---:|
| `1695410287-2414` | `28. Qh5` is followed by `28. b6`, while Black is to move before `b6`. | 10 |
| `1695413213-5860` | `62. Rd1` starts a new numbered line while Black is to move. | 10 |

These exclusions concern transcript structure, not outcomes. They do not establish that the remaining 180 games are exactly the README's 180-game experiment. The calculator retains an all-182 sensitivity under the less reliable assumption that every legal move belongs to the player assigned that color.

The work unit includes model decisions with **pre-move `board.ply()` from 15 through 75**, or the 16th through 76th game ply. There are **4,823 accepted model moves** in this window. Each retained input uses its exact historical PGN header and preceding moves; the fictional championship metadata is prompt text. The current shorter prompt file is not substituted. For every clean game, a separate reconstruction of the original runner's newline, move-number and SAN concatenation agrees with the source prefix.

The September 22 [early runner](https://github.com/adamkarvonen/chess_gpt_eval/blob/9eee4665e8eb8b712dcd47b84e6c821a704b5de2/main.py) and [completion wrapper](https://github.com/adamkarvonen/chess_gpt_eval/blob/9eee4665e8eb8b712dcd47b84e6c821a704b5de2/gpt_query.py), retained alongside the later historical refactor, establish the relevant call protocol: a plain Completion prompt, `max_tokens=10`, no stop sequence, and only the response's first whitespace-delimited token retained as SAN. The ChatCompletion instruction to output one move is not sent to this endpoint. Failed legality checks repeat the same prompt with a higher temperature; they do not append error feedback.

## Tokens and failed work

Retokenizing the exact inputs with the endpoint's `cl100k_base` encoding gives **1,585,753 input tokens**. Native usage and full completions are not retained. We assume 10 generated tokens per accepted call because the prompt invites continued PGN and has no stop sequence after the first move. This is a cap-filling estimate, not an observed output length. A lower scenario counts only the shortest tokenization of the accepted SAN, allowing the source runner to add its own leading space.

The 180 clean games have 20 reported illegal-counter increments. Fifteen belong to three terminal five-attempt sequences, at pre-move plies 115, 91 and 89. Their exact prompts are recovered, but all lie outside this operating window. The remaining five increments occur in two games. Their location and error type are unavailable. Centrally, treat these five as fully processed calls and distribute each game's count uniformly across that game's accepted model decisions. This assigns **1.5256215 calls**, **482.674277 input tokens**, and **15.256215 output tokens** to the selected window. This is an allowance for missing work, not proof that every counted request completed generation. Zero-work, half-work and high-prefix placement scenarios show its effect.

The wrapper catches ordinary API exceptions and returns `None`; its outer six-attempt retry decorator therefore does not justify multiplying every source call by six. Unlogged SDK retries cannot be reconstructed. Cache counters are absent, so the calculation assumes full prefix processing. No separate reasoning stream is indicated for this 2023 completion endpoint. Opposing engines and players are the game environment, outside the model's work; the local legality check adds no neural helper calls.

Central arithmetic:

`(1,585,753 + 4,823 × 10 + 482.674277 + 15.256215) / 4,823`

`= 338.892998236 tokens per accepted move`

`2 × 7,000,000,000 × 338.892998236 = 4.7445019753 × 10¹² FLOPs`

| Workload assumption | Tokens per accepted move | FLOPs at 7B |
|---|---:|---:|
| Minimal accepted SAN, no failed-call work | 331.452623 | 4.640337 × 10¹² |
| Ten-token output, no failed-call work | 338.789757 | 4.743057 × 10¹² |
| Ten-token output, half the central failed-call allowance | 338.841378 | 4.743779 × 10¹² |
| Central estimate | 338.892998 | 4.744502 × 10¹² |
| Counter work placed at the largest in-window prompts within each game | 339.252125 | 4.749530 × 10¹² |
| Central plus one unrecorded generated position per call | 339.893315 | 4.758506 × 10¹² |

Under the all-182 color-attribution sensitivity, 4,874 moves give 339.587660 tokens per move, **0.205% above** the selected central estimate. This sensitivity does not repair the two ambiguous transcripts. A 20B active-size alternative gives 1.35557 × 10¹³ FLOPs; 175B gives 1.18613 × 10¹⁴. These size scenarios have a much larger effect than the missing continuation and retry details.

## Human baseline

Estimate **4.3 seconds** for a strong club player’s post-opening move in fast blitz. The original [Russek timing aggregates](https://github.com/evanrussek/Thinking_Time_VOC_Chess/tree/0f21b31c05bec0494bc3c5da2e14c0be55fa345e) give a count-weighted mean of 4.3100023748 seconds over **28,621,413 moves** in the (1800,3000] Lichess rating bin at 180+0. This broad bin includes the approximately 1900-rated performance comparator. The bin label 2400 is its midpoint, not the mean player rating. Five-minute games in the same bin average 6.9087588 seconds, a slower-control scenario. **Range: 4.3100 to 8.6200 seconds** (2026-09-17). The low sits at the central because 4.3100 s is a floor. Barry states a three-minute clock, so 180+0 is settled, and 4.3100 s is the lowest of the four controls the donor covers for this bin: 6.9991 at 180+2, 6.9088 at 300+0 and 11.0617 at 300+3 all sit above it, as does interpolating the bin to Barry's own approximately 1900 rating, which the 180+0 trend by bin puts near 4.34. The high comes from the clock convention in `../games-memory/chess.md#the-clock-convention`: own clock plus the opponent's is the whole elapsed move cycle and therefore the ceiling on active effort, and both players in the donor games are drawn from the same rating bin at the same control, so the opponent's mean own clock is the same 4.3100 s and the cycle is 2 x 4.3100 = 8.6200 s. That ceiling is generous for Barry's own match in particular, where the model replied in seconds and left almost no opponent clock to think on, which is a further reason the central sits on the own clock.

This is a timing transfer, not a measured average for the target player or source positions. Own-clock intervals include entry and possible distraction but omit thinking during the opponent’s turn. The donor’s move_ply 15–75 filter supports a post-opening-window transfer; the retained files do not establish its upstream ply-index convention, so exact one-ply alignment is not claimed. All outcomes contribute. The donor count is not the number of independently timed target-task attempts. The original aggregates and replay are in [the shared human timing record](../searchless-chess/human-helper/human-and-helper.md).

[David Barry’s original account](https://pappubahry.substack.com/p/ai-at-the-end-of-2023) describes an 8–2 fast-blitz loss to GPT-3.5 Instruct. Its retained [ten-game study](https://lichess.org/study/LTNLQjQV) contains seven AI wins, two draws and one loss, dated September 30, 2023. Barry reports approximately 1900 Lichess blitz, FIDE 1664 classical and 1583 blitz. He describes a three-minute human clock; the PGN itself lacks clock fields. The small match supports the best estimate `above` for a strong-club fast-blitz baseline, without converting Stockfish skill levels to human Elo. A longer game he won prevents generalizing this judgment to arbitrary thinking time.

Performance transfers from that separate match to the engine-game move sample. The human uses a board while the model receives PGN and automatic illegal-move rejection. These are the recorded assessment and input/tool differences. The estimated human duration targets the stronger club population; it is not silently assigned professional-master skill.

## Model assumptions

Use **7B active parameters**, a weak family transfer from Finlayson et al., [2403.09539v2](https://arxiv.org/html/2403.09539v2), section 4. That study tested GPT-3.5 Turbo 0125 in February 2024, estimated output rank 4600–4650, favored hidden width 4096 and inferred about 7B under conventional dense architecture. It explicitly allows architectural changes and MoE alternatives. Neither the width nor 7B is a measurement of September 2023 Instruct. The 20B and 175B alternatives are size scenarios, not confidence bounds.

The direct Instruct study, Carlini et al., [Stealing Part of a Production Language Model](https://proceedings.mlr.press/v235/carlini24a.html), included Instruct among January 2024 endpoints but withheld GPT-3.5 widths. It supplies no public numeric validation of 7B. Original papers are retained in agent-work/sources/gpt35-chess/human-model/ and agent-work/sources/gpt35-chess/review-carlini2024.pdf.

The release date is **2023-09-18**: [Carlini’s September 22 first-person account](https://nicholas.carlini.com/writing/2023/chess-llm.html) says the endpoint became available that Monday and describes using it. This dates the endpoint, not undisclosed weight revisions.

## Reproduction

Requires Python with chess and tiktoken; the retained replay used chess 1.11.2 and tiktoken 0.14.0. Supply the published paths and a new output file:

```sh
python3 /path/to/research/gpt35-chess/workload_review.py --sources /path/to/sources/gpt35-chess --output /path/to/new-workload-review.json
```

The calculator reads retained sources and does not make model calls or execute the historical runner. It hashes inputs and rejects existing output or output under the source directory. workload-review.json retains per-move inputs, excluded-game reasons, retry allocations and sensitivity calculations. Compute is total estimated workload per accepted move; 4,823 moves are not counted as independent AI games.
