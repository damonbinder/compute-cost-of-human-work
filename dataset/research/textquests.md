# TextQuests — four 25-game Infocom suite runs against community completion times

*Created 2026-09-13 18:06.*
*Revision 1, 2026-09-13 18:58, on the independent review at
`reviews/textquests-independent.md`; change log in `candidates/textquests/REVISION.md`.*

## Summary

TextQuests (arXiv:2507.23701) ran twelve whole-suite evaluations — six models in each of two
clue modes — over the 25 Infocom interactive fiction games, and published per-mode input,
cache and output token totals for all twelve in Appendix E. Four of those twelve cells clear
the exclusion rule and become rows: the **With Clues** runs of o3, Gemini 2.5 Pro, Claude Opus
4 and Claude Sonnet 4, at **1.06e18 to 8.44e18 FLOPs** against **646,708 human seconds** (179.6
hours) for the same 25 games, all `below`. The other eight token-bearing cells, the 58 cells of
the 29 leaderboard models with no published tokens, and the 12 individual games the four
models finished are recorded in `candidates/textquests/dispositions.csv`.

The rows are **suite-level, not per-game**, and the reason is on both sides of the ledger: the
token table is a 25-game total with no per-game split and no per-game step counts, and two of
the four games these models finished — The Witness, which all four completed, and Seastalker —
have no human completion time anywhere reachable. Argued in
[Why the suite is the unit](#why-the-suite-is-the-unit).

Three things determine the numbers, in descending order.

1. **The human baseline is 26 self-reported completion times from 13 IFDB members, covering 18
   of the 25 games**, with the other seven imputed at the mean of those 18. The imputation is not
   the uncertainty that matters — placing those seven anywhere from the 10th to the 90th
   percentile of the timed eighteen moves the suite only 0.89x to 1.12x. The population is
   what matters: the paper's own anchor says these games "can take human players over 30
   hours", 4.17x the IFDB figure. Ten of the 26 votes record hint use, which matches the With
   Clues mode these rows are built on, so the IFDB figure is the matched comparator and the
   1983 one is an unaided upper scenario. [Human baseline](#human-baseline).
2. **HowLongToBeat, the source the two accepted game rows in this folder used, is unreachable
   from this environment.** Four independent routes refuse it, including HowLongToBeat's own
   edge returning 403 to a plain request, so no per-game cross-check against it exists here.
   [HowLongToBeat is unreachable](#howlongtobeat-is-unreachable).
3. **Cached-context attention runs one way and is large**, because these runs re-read a
   40,000 to 51,000-token prefix on every one of roughly 12,500 calls. At the bracketing
   shapes it adds 0.27x to 1.94x on top of the parameter-only value, and
   `research/attention-correction.md` folds it into `compute_flops`. Its size is
   uncertain in both directions, since the call count is nominal rather than a bound.
   [Compute scenarios](#compute-scenarios).

Everything else is read off the paper's own table, the released harness at a pinned commit,
the live leaderboard's data array, and the game files in the repository.

## Shared evidence

### The benchmark and the runs

Paper: `https://arxiv.org/abs/2507.23701`, v1 31 Jul 2025, v2 11 Aug 2025, v3 13 Aug 2025.
Tables and the verbatim evaluation-setting text are retained in
`agent-work/sources/textquests/textquests-paper-tables-2026-09-13.md`; the token table is also
machine-readable in `agent-work/sources/textquests/textquests-token-table-2026-09-13.json`.
Harness: `https://github.com/centerforaisafety/textquests`, cloned 2026-09-13 at commit
`18dc472618cc522dfaad04fec19fae775a87860f`, excerpted in
`agent-work/sources/textquests/textquests-harness-extracts.md`. Leaderboard: the `{model, noClues,
withClues, completedGames, noCluesCompletedGames}` array embedded in
`https://www.textquests.ai/_next/static/chunks/app/page-405dffcbe9e7190f.js`, parsed whole
into `agent-work/sources/textquests/textquests-leaderboard-2026-09-13.json` (35 models).

A run is 25 concurrent game sessions under one model and one clue mode. Each session is up to
500 parser commands and stops early if the game is finished. The agent's context is the
system prompt — the game name, its maximum score, the printed feelies, and in With Clues the
complete InvisiClues hint booklet — followed by the untruncated alternation of game
observations and its own `{"reasoning", "action"}` JSON objects. A reasoning model's thinking
is discarded rather than re-entered, so the per-turn increment does not grow with model
verbosity. `restore {step_id}` returns the game to any earlier step; the environment
autosaves every step.

The two clue modes differ only in whether the InvisiClues text is in the system prompt.
Measured from the repository's own game files with the `o200k_base` tokenizer
(`agent-work/sources/textquests/game-context-sizes-2026-09-13.json`): the feelies total 168,013
tokens over the 25 games and the InvisiClues 191,988, so With Clues adds a mean 7,680 tokens
to each game's opening context. The same file carries each game's optimal walkthrough length,
82 commands for The Witness up to 604 for Trinity, 6,739 in total.

**Model identity.** `model_configs.yaml` at the pinned commit resolves `o3-high` to
`openai/o3` at `reasoning_effort: high`, `gemini-2.5-pro` to `gemini/gemini-2.5-pro` through
Google's OpenAI-compatibility endpoint at `reasoning_effort: high`, and the Claude 4 entries
to `anthropic/claude-*-4-0` with `max_tokens: 20000` and a 16,000-token thinking budget. Table
5's caption says "a 20k token thinking budget for Claude 4 models"; 20,000 is the released
config's `max_tokens` and 16,000 its `budget_tokens`, so the caption is loose and the figure
used here is the config's. The paper's Table 5 column is labelled "Claude Opus 4.0", and there
is no `claude-opus-4-0` entry
in the released config, only `claude-opus-4-1` with the same generation block. Registry IDs
used, unchanged from the Codex registry with their inherited priors and copied into
`agent-work/sources/textquests/model-coefficients-2026-09-13.json`:

| Table 5 column | model_id | FLOPs per token | Active parameters | Basis |
|---|---|---:|---:|---|
| o3 | o3-2025-04-16 | 1.0e11 | 5.0e10 | estimated |
| Gemini 2.5 Pro | gemini-2.5-pro | 2.0e11 | 1.0e11 | estimated |
| Claude Opus 4.0 | claude-opus-4 | 3.6e11 | 1.8e11 | estimated |
| Claude Sonnet 4.0 | claude-sonnet-4 | 2.0e11 | 1.0e11 | estimated |
| GPT-4.1 | gpt-4.1-2025-04-14 | 1.0e11 | 5.0e10 | estimated |
| GPT-4.1-mini | gpt-4.1-mini-2025-04-14 | 4.8e10 | 2.4e10 | estimated |

No new model IDs are minted, so `candidates/textquests/models.csv` carries only its header.

### What the published token counters contain

This is the one reading the whole compute side turns on, so it is argued rather than asserted.

Table 5 prints, for each model and mode, `Max Input Tokens`, `Max Output Tokens`, `Total Input
Tokens`, an indented `Cache Tokens`, and `Total Output Tokens`. `src/llm_agents.py` shows what
the harness accumulates into those fields:

- **OpenAI-compatible path** (o3, GPT-4.1, GPT-4.1-mini, and Gemini through Google's
  compatibility endpoint): `input_tokens = usage.prompt_tokens`, `cached_tokens =
  prompt_tokens_details.cached_tokens`. `prompt_tokens` already contains the cached prefix, so
  `cached_tokens` is a subset of it.
- **Anthropic path**: `input_tokens = usage.input_tokens + usage.cache_creation_input_tokens`,
  `cached_tokens = usage.cache_read_input_tokens`. Here the two are disjoint.

If Table 5's `Total Input Tokens` were the raw `input_tokens` field on both paths, then for the
Claude columns `Cache / Total Input` would be 522/524 and 567/569 — and the hit rate, properly
`reads / (reads + processed)`, would be 49.9 per cent, contradicting the caption's "exceeding
95-99 per cent". Read instead as `processed + reads` for the Anthropic columns, the ratio
`Cache / Total Input` is the hit rate directly, and across all twelve cells it runs 94.1 to
99.7 per cent, which is what the caption says. The second reading is therefore the right one,
and under it the same subtraction works on every path:

```
counted tokens = Total Input Tokens - Cache Tokens + Total Output Tokens
```

which is exactly COLUMNS' `params_tokens` rule — fresh input plus cache creation plus output,
cache reads excluded. Under DECISIONS' cache-counter ruling this row set states the form: the
OpenAI and Gemini columns are the partitioned form (cached inside input), the Anthropic
columns the additive form with reads added back by the paper.

Two independent checks support it. The README's sample run for GPT-5-mini prints
`input_tokens 610,771,490`, `output_tokens 27,193,585`, `total_tokens 637,965,075`,
`cached_tokens 582,565,248`; input plus output equals total exactly, so `cached_tokens` is
indeed inside `input_tokens` on the OpenAI path. And the residual is the right size: 2M of
processed prompt tokens for Claude Opus 4 over 25 games and up to 12,500 calls is 160 tokens a
call, which is one game observation plus one short JSON object — the actual per-turn
increment — plus the 25 one-off system prompts, which the repository measurement puts at
174K (No Clues) to 366K (With Clues).

Retries are inside the totals: `play_game` passes `max_retries=10`, a retry re-sends the
identical history, and `_parse_response` accumulates on every call including failed ones.

**A defect in Table 5.** Claude Sonnet 4.0's With Clues column repeats its No Clues column
exactly in Max Input (132K), Total Input (569M), Cache (567M) and Total Output (3.3M), and
differs only in Max Output (1.6K to 1.9K). Every other model's Total Input rises 10.7 to 26.0
per cent between the modes. The defect is original rather than a transcription artifact: the
same duplicated column is Appendix D of the 31 July 2025 v1 and has survived three versions.
The input side of the quantity the rows use survives it: for Claude Opus 4 the difference
`Total Input - Cache` is 2M in **both** modes, because the per-turn increment that drives it
does not depend on the clue booklet, and the booklet's own 192K one-off contribution is inside
the rounding. The output side is less certain, and in one direction: output falls between modes
for all three reasoning models with distinct columns (o3 10 to 9.6M, Gemini 2.7 to 2.2M, Opus
3.1 to 2.8M, 4 to 19 per cent), so a true Sonnet With Clues output below 3.3M would put counted
tokens near 0.94x the recorded 5.3M — inside the 0.81x to 1.19x rounding band the row already
carries. The Sonnet row carries the defect in its `notes`.

### Rounding

Table 5 prints three significant figures in millions. The difference of two such numbers
inherits up to 1e6 of error in the worst case, which matters where the difference is small:

| Cell | Processed input | Output | Counted | Worst-case band on counted |
|---|---:|---:|---:|---|
| o3, With Clues | 17M | 9.6M | 26.6M | 25.6M to 27.6M |
| Gemini 2.5 Pro, With Clues | 40M | 2.2M | 42.2M | 41.2M to 43.2M |
| Claude Opus 4, With Clues | 2M | 2.8M | 4.8M | 3.8M to 5.8M |
| Claude Sonnet 4, With Clues | 2M | 3.3M | 5.3M | 4.3M to 6.3M |

So the two Claude rows carry a 0.79x to 1.21x rounding band and the other two about 0.96x to
1.04x. The Claude band is stated in those rows' `notes`; it is smaller than their
active-parameter uncertainty.

## Human baseline

### HowLongToBeat is unreachable

The obvious source, and the one the accepted `game-portal-gpt6astra` and
`game-factorio-gpt6astra` rows used, is HowLongToBeat's per-game community completion times.
Damon has ruled the source usable, so those two rows stand on their own terms, but no route
available in this environment reaches it. Four were tried, by this note and by the independent
review:

| Route | Result |
|---|---|
| `WebSearch` restricted to the domain | refused, "not accessible to our user agent", citing Anthropic's crawler policy |
| `WebFetch` on a game page | refused, "unable to fetch from howlongtobeat.com" |
| Browser pane navigation | refused by organization policy |
| Plain `curl` on `/robots.txt` | HTTP 403 from HowLongToBeat's own edge (Varnish, `IFW-U01`) |

The fourth is the decisive one: the block is not only a policy applied on this side. The
`robots.txt` body that a single earlier request did return lists `ClaudeBot`, `Claude-User`,
`Claude-SearchBot`, `Claude-Web` and `anthropic-ai` among about a hundred named agents under a
single `Disallow: /`, and its header comment prohibits automated retrieval and dataset
creation. Presenting a browser user agent to get past that is not something this note does.

The consequence for these rows is only that there is no second community timing source to
cross-check IFDB against. A person opening the pages in their own browser is the only route to
one.

### What the benchmark itself claims

The paper's abstract and introduction say these games "can take human players over 30 hours
and require hundreds of precise actions to solve", citing Susan Smetale, "Through the zorking
glass", The Washington Post, December 1983. That is a newspaper feature, not a timing study;
no population, method or sample is described. The article returns HTTP 403 to this
environment, so the sentence behind the figure could not be read at all. Carried as a named
scenario, not as the row's value.

### IFDB member completion times

IFDB (`https://ifdb.org`), the Interactive Fiction Database, runs a play-time vote: members
submit **the time it took them to finish a game**, the game page shows the median and lists
every vote with an optional free-text note. Its `robots.txt` carries a content-signals
preamble and no `User-agent` or `Disallow` directive at all, so the pages were fetched
directly, one per game at about one request a second. All 25 entries, with each individual
vote, its note and the member name, are retained in
`agent-work/sources/textquests/ifdb-playtimes-2026-09-13.json`. Game identities were confirmed
against the author field; two first search hits were the wrong game (a non-Infocom
Hitchhiker's and a different Sorcerer) and were replaced.

| Game | Votes | Mean (h) | IFDB median (h) | Notes members left |
|---|---:|---:|---:|---|
| ballyhoo | 2 | 5.750 | 5.750 | "with hints" |
| borderzone | 1 | 6.000 | 6.000 | "two hints" |
| cutthroats | 1 | 5.167 | 5.167 | — |
| deadline | 1 | 10.000 | 10.000 | — |
| enchanter | 1 | 7.500 | 7.500 | "with hints" |
| hitchhiker | 1 | 15.000 | 15.000 | "With extensive hints" |
| hollywoodhijinx | 3 | 8.417 | 8.250 | "with just one hint :/" |
| infidel | 1 | 6.383 | 6.417 | — |
| lurkinghorror | 2 | 5.042 | 5.083 | "Using the Invisiclues in places" |
| moonmist | 1 | 2.000 | 2.000 | "without hints" |
| planetfall | 1 | 7.000 | 7.000 | — |
| plunderedhearts | 3 | 2.833 | 3.000 | "One hint"; "With a couple of hints" |
| sorcerer | 1 | 10.500 | 10.500 | "with hints" |
| spellbreaker | 1 | 10.250 | 10.250 | "with hints" |
| stationfall | 1 | 6.000 | 6.000 | — |
| trinity | 2 | 7.500 | 7.500 | — |
| wishbringer | 1 | 5.000 | 5.000 | — |
| zork1 | 2 | 9.000 | 9.000 | — |
| seastalker, sherlock, starcross, suspect, witness, zork2, zork3 | 0 | — | — | no vote |

```
sum of the 18 per-game means            = 129.342 h
mean of the 18                          =   7.186 h
suite = 129.342 + 7 * 7.186             = 179.641 h = 646,708 s
```

**Value used: 646,708 seconds.** Eleven of the 26 votes carry a note: **ten record hint use**
and one (Moonmist, 2 hours) records the opposite, "without hints". One of the ten names the
InvisiClues explicitly — Adam Biltcliffe's Lurking Horror vote, "Using the Invisiclues in
places" — which is the same material the With Clues agent has in context; that is the reason
these rows are built on the With Clues mode and not the other one. The arithmetic mean is used
per game where COLUMNS prefers it; IFDB's own displayed figure is the median, and substituting
medians throughout moves the suite to 647,083 seconds, a 0.06 per cent change.

Field choices, and what is weak about them:

- `human_skill` is `typical`, following the Factorio row's treatment of self-selected players
  who log their games. IFDB members are interactive-fiction hobbyists rather than a general
  population, which biases the duration low; they are not professionals, which is what
  `expert` means in COLUMNS.
- `human_time_subset` is `successful` with `human_attempts` 26. IFDB's field is the time to
  finish, so only finishers contribute. This is a selection rule, not a claim about how often
  players finish.
- `human_time_evidence` is `task_timings` and `human_time_method` is `other_calculation`.
  Each vote is a recorded timing of that very game by the member who played it: IFDB's own
  guidance is to report how long it took you to reach an ending once, and the votes read that
  way, at minute-level precision (6h23m, 5h10m, 3h55m) and with first-person conditions. The
  seven unvoted games are neither another task nor another population — they are other members
  of the same source-defined 25-game suite, timed by the same community — so the imputation does
  not make the number an `llm_estimate_from_data`, any more than a collection average makes a
  compute figure a transfer under the parallel rule in COLUMNS. 72.0 per cent of the recorded
  value, 465,630 of 646,708 seconds, is measured directly on games inside the row's own work
  unit. This also matches the two accepted rows built on the structurally identical
  HowLongToBeat community means. The imputation is disclosed in every row's `notes`.
  (Revision 1 changed these two fields from `llm_estimate_from_data` and `estimated`.)
- Thin samples and wide dispersion. Twelve of the eighteen games rest on a single vote, and
  where two exist they disagree widely: 1.5 against 10 hours on Ballyhoo, 3 against 12 on
  Trinity. Thirteen distinct members produced the 26 votes, the largest contributor seven of
  them.
- **The imputation is not the binding uncertainty.** Placing the seven unvoted games anywhere
  from the 10th to the 90th percentile of the timed eighteen moves the suite 0.89x to 1.12x
  (`imputation_sensitivity_seconds` in `agent-work/derived/textquests/calculations.json`), which is well
  inside the roughly 3x grade-C band on the active-parameter priors already pricing
  `compute_flops`, and inside the 0.79x to 1.21x rounding band the two Claude rows carry.
- The 4.17x disagreement with the paper's 30-hour anchor is the largest single uncertainty on
  the human side, and it is a difference in population rather than in sample size, so no number
  of extra votes would close it. Damon's ruling is that the IFDB hinted-player figure is the
  value and the 1983 figure is the unaided upper scenario, which is the reading the hint notes
  support: the With Clues agent holds the complete booklet from its first turn, and ten of the
  26 votes record hint use.

### A floor from the walkthroughs

The repository's optimal walkthroughs total 6,739 commands across the 25 games. A player who
already knows every solution and simply retypes them, at 10 to 20 seconds a command, replays
the whole suite in **18.7 to 37.4 hours**. That is a floor, and the ratio of a candidate human
figure to it says what kind of play the figure describes:

| Figure | Suite hours | Ratio to the 10-20 s floor |
|---|---:|---|
| Walkthrough replay, 10 to 20 s a command | 18.7 to 37.4 | 1x |
| IFDB member completion votes, as built | 179.6 | 4.8x to 9.6x |
| The paper's 30 hours a game | 750.0 | 20x to 40x |

Both candidate figures are far above the floor, so neither is walkthrough-following — which is
the failure mode that would have killed these rows. IFDB sits at the low end of plausible
first-time exploratory play and the newspaper figure at the high end, which is the
hinted-enthusiast versus unaided-discoverer reading with a number attached rather than only an
interpretation. The floor is computed in `research/textquests/compute_textquests.py` and
retained as `walkthrough_floor`.

## Why the suite is the unit

The alternative is a per-game row for each game a model finished: twelve cells, four models,
four distinct games (moonmist 4, witness 4, plunderedhearts 3, seastalker 1). Both sides fail.

**Compute.** Table 5 is a 25-game total and nothing published splits it. A game's counted
tokens are its one-off system prompt plus a per-step increment, so they scale with steps taken
— and a finished game stops before the 500-step cap by an unpublished amount. The only
per-game step count the project publishes anywhere is the README's sample, where GPT-5-mini
finished Moonmist in 182 of 500 steps. Splitting the suite total evenly would therefore
overstate a finished game by something between 1x and about 2.7x, with no evidence to pin it.

**Human time.** The Witness, which all four models finished, and Seastalker, which Claude Opus
4 finished, have no IFDB vote at all, and no other reachable source carries an Infocom
completion time. Moonmist has one vote and Plundered Hearts three. Five of the twelve cells
would have no human duration whatever, and four more would rest on one person's self-report.

The suite avoids the first problem entirely — the token total is measured for exactly the
source-defined collection the row describes, so it is not a transfer — and softens the second,
since 18 of the 25 games carry a timing. All twelve per-game cells are in
`candidates/textquests/dispositions.csv` with this reasoning attached, and Plundered Hearts is
the one that would come closest if per-game steps were ever published.

## Performance and the exclusion rule

The benchmark's own metric is mean game progress: per game, the highest labelled checkpoint
percentage the trajectory ever reached, averaged over the 25 games. `game_progress.json`
assigns 10 to 20 checkpoints a game along the critical path with the last always 100, and
`textquests_env.py` sets a game finished at progress 100, so **a player who finishes the game
scores 100 per cent by construction** and the human side of the ratio is 100.

The per-game progress values behind each model's mean are not published, so the standard error
of the 25-game mean cannot be computed. It can be bounded: for a variable on [0, 100] with
mean p the largest possible standard deviation is sqrt(p(100-p)), so the largest possible
standard error of the mean is that over sqrt(25). Every cell is therefore judged at the most
generous dispersion it could have.

| Mode | Model | Progress (%) | Ratio to human | Max SE of ratio | SE below the 0.5 guide | Outcome |
|---|---|---:|---:|---:|---:|---|
| With Clues | Gemini 2.5 Pro | 60.6 | 0.606 | 0.098 | -1.08 | row |
| With Clues | Claude Opus 4 | 60.5 | 0.605 | 0.098 | -1.07 | row |
| With Clues | o3 | 60.4 | 0.604 | 0.098 | -1.06 | row |
| With Clues | Claude Sonnet 4 | 57.2 | 0.572 | 0.099 | -0.73 | row |
| With Clues | GPT-4.1 | 37.5 | 0.375 | 0.097 | 1.29 | not a row |
| No Clues | o3 | 30.9 | 0.309 | 0.092 | 2.07 | not a row |
| No Clues | Claude Opus 4 | 26.4 | 0.264 | 0.088 | 2.68 | not a row |
| No Clues | Claude Sonnet 4 | 24.7 | 0.247 | 0.086 | 2.93 | not a row |
| No Clues | GPT-4.1 | 22.8 | 0.228 | 0.084 | 3.24 | not a row |
| No Clues | Gemini 2.5 Pro | 23.2 | 0.232 | 0.084 | 3.17 | not a row |
| With Clues | GPT-4.1-mini | 15.9 | 0.159 | 0.073 | 4.66 | not a row |
| No Clues | GPT-4.1-mini | 10.6 | 0.106 | 0.062 | 6.40 | not a row |

The four retained cells sit a full standard error above the guide and the nearest excluded one
is 1.29 below it even at maximum dispersion, so the close-call rule does not bite anywhere and
the cut is not fragile.

**The label is `below`, and two things qualify it, both stated in every row.** First, progress
is a position on the critical path, not a share of the effort: the checkpoints are milestones,
and the last 40 per cent of them is the harder part, so 60 per cent of the checkpoints is less
than 60 per cent of the work. Second, on completion rather than progress these runs finished 2
to 4 of 25 games against a timing sample composed of people who finished, a ratio of 0.08 to
0.16. Progress is the benchmark's headline metric and the one with a defined human value, so
it governs; the completion counts are in `performance_evidence` and `notes` so the harsher
reading is reconstructible. There is no chance floor to subtract, and that is provable from
`game_progress.json` rather than inferred: 8 of the 25 games place their first checkpoint at
percentage 0 and the other 17 place theirs at 2 to 10 per cent, so an agent that does nothing
scores exactly 0 on every game. Even at a generous 5 per cent floor the ratios would be 0.583
for the retained cells and 0.342 for GPT-4.1, so no decision turns on it. The weakest board
entry, Llama 4 Scout With Clues, scores 7.7 per cent.

`comparison_issues` is `different_task; different_inputs_or_tools; different_attempt_selection`.
The agent did a bounded 500 steps a game and reached part of the path while the human time is
for finishing. It held the complete InvisiClues booklet in context from the first turn, where a
human's hint use was partial, on demand, and recorded for only ten of 26 votes. And the two
sides select different outcome subsets: `compute_subset` is `all`, covering 25 sessions of
which 21 to 23 never reached an ending, against `human_time_subset` `successful`, covering only
members who did — which is the flag's definition, and which all 42 rows in this folder with
that subset pair carry. (Revision 1 added the third flag.) Save and restore is **not** flagged:
Infocom players saved and restored constantly, which is why the benchmark implements it.

## Compute

`research/textquests/compute_textquests.py` takes the retained extracts and the shared price
table and writes `agent-work/derived/textquests/calculations.json`;
`research/textquests/build_rows.py` turns that into the candidate CSVs. Both take explicit
input and output paths and read nothing from a candidate folder or a scratch directory.

```
python3 research/textquests/compute_textquests.py \
  --sources agent-work/sources/textquests \
  --prices research/cost/list-prices.csv \
  --out agent-work/derived/textquests/calculations.json
python3 research/textquests/build_rows.py \
  --calculations agent-work/derived/textquests/calculations.json \
  --leaderboard agent-work/sources/textquests/textquests-leaderboard-2026-09-13.json \
  --ifdb agent-work/sources/textquests/ifdb-playtimes-2026-09-13.json \
  --outdir candidates/textquests
```

### Compute scenarios

One at a time, judgmental rather than confidence intervals. Ratios are to each row's own
central value.

| Scenario | o3 | Gemini 2.5 Pro | Claude Opus 4 | Claude Sonnet 4 |
|---|---:|---:|---:|---:|
| Central | 2.66e18 | 8.44e18 | 1.728e18 | 1.06e18 |
| Table 5 rounding, low | 0.96x | 0.98x | 0.79x | 0.81x |
| Table 5 rounding, high | 1.04x | 1.02x | 1.21x | 1.19x |
| Plus cached-context attention, L=64 d=8192 | 1.86x | 1.53x | 1.27x | 1.48x |
| Plus cached-context attention, L=80 d=10240 | 2.35x | 1.83x | 1.42x | 1.74x |
| Plus cached-context attention, L=96 d=12288 | 2.94x | 2.20x | 1.61x | 2.07x |
| Hidden reasoning, 1,000 tokens a call | — | 1.30x | — | — |
| Hidden reasoning, 2,000 tokens a call | — | 1.59x | — | — |
| No cache-read exclusion, full prefix charged | 20.3x | 16.0x | 122x | 108x |

**Cached-context attention.** The dataset's `2 * active_parameters` coefficient prices
projection and feedforward matrices and nothing else. These runs are the case where that hurts
most: the prefix is re-read on every call and averages `Cache / 12,500` = 41,120 tokens for o3,
50,800 for Gemini 2.5 Pro, 46,640 for Claude Opus 4 and 45,360 for Claude Sonnet 4 in With
Clues. Attention per processed or generated position is `4 * layers * d_model * context`, the
recipe the dataset's RULER row uses and the accepted Portal row reproduces; applied here over
the counted tokens it adds 0.86x to 1.94x (o3), 0.53x to 1.20x (Gemini), 0.27x to 0.61x (Opus)
and 0.48x to 1.07x (Sonnet). The shapes bracket a 2025 frontier decoder and are not re-derived
per model, because attention cost follows depth and width rather than how many experts a token
activates. The omission is one-directional: it can only raise the true figure. Per DECISIONS
this stays out of `compute_flops` so the rows remain comparable with the other 1,410 points.

**12,500 is a nominal call count, not a bound, and the attention scenario is two-sided.**
Finishing 2 to 4 games before the 500-step cap removes steps, while a parse failure retries the
identical history and adds a call whose tokens are already inside the published totals. Since
the scenario scales as 1/calls, it moves either way, and it does not touch the central value.

**Hidden reasoning, Gemini only.** Gemini 2.5 Pro cannot disable thinking and the harness
requests `reasoning_effort: high`, yet Table 5's mean Gemini output is 176 tokens a call. That
figure on its own is not evidence of anything: the two Claude models bill thinking inside
`output_tokens` and run 224 and 264 tokens a call, so a low mean is what this task produces.
The argument rests on the endpoint instead. On Google's OpenAI-compatibility endpoint in the
run window, thinking tokens sat outside `completion_tokens` and were recovered as
`total_tokens - prompt_tokens - completion_tokens`; a May 2025 thread on Google's own developer
forum does exactly that arithmetic for a 2.5 model and gets a positive residual, which is only
possible if the thoughts are not in `completion_tokens`. Google's compatibility documentation
does not address usage reporting either way, and an older thread about a 2.0 thinking model
reads the other way, so this is a live scenario rather than a settled correction. If it holds,
the hidden amount is a quantity the harness did capture — `OpenAIAgent._parse_response` records
`total_tokens` — and the paper simply did not print, which would make it a real undercount
rather than a speculative one. The scenarios price 500, 1,000 and 2,000 hidden tokens a call.
The Anthropic path bills thinking inside `output_tokens` and the OpenAI path bills reasoning
inside `completion_tokens`, so no other row is affected.

**No cache-read exclusion.** Charging every input token a full forward pass is not a live
scenario — caching is what made these runs affordable and the counters record it — but it
bounds the top of the range and shows how much of the workload the convention removes.

### Cost

`ai_cost_basis` is `list_price` on all four rows, at the `research/cost/list-prices.csv`
windows in force on `ai_cost_date` 2025-07-31. That date is the arXiv v1 submission: the runs
are complete by then, and no run date is published anywhere, which is the case
COLUMNS covers with "the price-sheet date where the run date is unknown".

| Row | Processed input | Cache reads | Output | Cost |
|---|---:|---:|---:|---:|
| o3 | 17M at $2.00 | 514M at $0.50 | 9.6M at $8.00 | $367.80 |
| Gemini 2.5 Pro | 40M at $1.25 | 635M at $0.125 | 2.2M at $10.00 | $151.38 |
| Claude Opus 4 | 2M at $18.75 | 583M at $1.50 | 2.8M at $75.00 | $1,122.00 |
| Claude Sonnet 4 | 2M at $3.75 | 567M at $0.30 | 3.3M at $15.00 | $227.10 |

Two qualifications. The Anthropic figure prices the whole processed-input residual at the
cache-write rate, because the harness sets a cache breakpoint on the last message of every
call and so almost all of that residual is a cache write; pricing it all as ordinary input
instead gives $1,114 and $226, so the choice is worth under 1 per cent. And o3's price fell
from $10/$40 to $2/$8 per million on 2025-06-10, inside the window when these runs could have
happened; at the older sheet the o3 row would cost $1,839. Claude Opus 4 was released
2025-05-22 and is in the run set, so no run predates that.

`human_cost_basis` is `not_available` on all four: IFDB members were not paid and no price is
attached to their play.

## Dispositions

`candidates/textquests/dispositions.csv`, 82 rows, reconciling every leaderboard cell and
every finished game to a row or a reason.

| Family | Cells | Outcome |
|---|---:|---|
| Six token-bearing models, With Clues, above the guide | 4 | rows |
| Six token-bearing models, other cells | 8 | not a row, below the guide |
| 29 leaderboard models with no published tokens, both modes | 58 | not a row, no compute |
| Games the four row models finished | 12 | not a row, see [Why the suite is the unit](#why-the-suite-is-the-unit) |

The 58 no-token cells are the larger loss and the more interesting one: 16 of them would clear
the half-of-human guide, 14 With Clues and two No Clues, topped by GPT-5.6-sol at 86.84 per cent
with 13 of the 25 games finished and Claude Fable 5 at 82.04 per cent with 12. Those two are also
the only models to finish a game at all without clues, one and two games respectively. The token
table covers six models only, the run directories are not released, and
`simple-evals` — the maintained successor eval the repository now points at — carries a
different XML-tag harness and publishes no results either. Nothing in public material recovers
those counts.

Two reconciliation notes. The live leaderboard shows GPT-5, Claude Opus 4.1 and GPT-5-mini
completing 5, 4 and 1 games in **No Clues**, each equal to that model's own With Clues count,
where the paper's Table 4 shows 0 for every model in that mode. `noClues.completed` is a
literal published field in the leaderboard array rather than something the page derives, so
these are three published values that disagree with the paper, and the mechanism is unknown:
27 of the 35 entries carry no `noCluesCompletedGames` list, and 24 of those 27 publish a No
Clues count of 0, so a missing list does not by itself explain the anomaly. Table 4 is taken as
authoritative and the dispositions follow it; none of the three models is in these rows. And
Table 3's 800-step reruns of five models publish no token counts, so they are not cells here at
all.

## Row sections

### game-textquests-clues-o3

o3 at high reasoning effort, With Clues. Counted tokens 531M - 514M + 9.6M = 26.6M at 1.0e11
FLOPs per token = **2.66e18**. Mean game progress 60.4 per cent, finishing Moonmist, Plundered
Hearts and The Witness. Human time 646,708 s. Cost $367.80 at the 2025-07-31 sheet. Attention
scenario 0.86x to 1.94x on top. The largest single response in the suite is 6.8K tokens and
the mean is 768, both consistent with reasoning billed inside `completion_tokens`.

### game-textquests-clues-gemini25pro

Gemini 2.5 Pro through Google's OpenAI-compatibility endpoint at high reasoning effort, With
Clues. Counted tokens 675M - 635M + 2.2M = 42.2M at 2.0e11 = **8.44e18**, the largest of the
four. Mean game progress 60.6 per cent, finishing The Witness, Moonmist and Plundered Hearts.
Its 94.1 per cent cache hit rate is the lowest of the six models, which is why its processed
input is 40M against the Claude models' 2M — implicit caching reuses less of the prefix than an
explicit breakpoint does. The hidden-reasoning scenarios above are the material uncertainty on
this row.

### game-textquests-clues-claudeopus4

Claude Opus 4 with a 16,000-token thinking budget, With Clues. Counted tokens 585M - 583M +
2.8M = 4.8M at 3.6e11 = **1.728e18**. Mean game progress 60.5 per cent, finishing Moonmist,
Plundered Hearts, Seastalker and The Witness — four games, the most of the four row models, and
the only completion of Seastalker anywhere in these rows. The 0.79x to 1.21x rounding band on
the 2M residual is this row's largest stated uncertainty after the 1.8e11 prior, and
the row is the cheapest in FLOPs and the most expensive in dollars, $1,122, because Opus 4
charges $1.50 per million cache reads and it made 583M of them.

### game-textquests-clues-claudesonnet4

Claude Sonnet 4 with a 16,000-token thinking budget, With Clues. Counted tokens 569M - 567M +
3.3M = 5.3M at 2.0e11 = **1.06e18**. Mean game progress 57.2 per cent, finishing The Witness
and Moonmist. This is the cell whose Table 5 column duplicates its No Clues column; the row
uses it because the derived residual is 2M for Claude Opus 4 in both modes as well, so the
duplication does not move the quantity the row needs, and the rounding band already spans
0.81x to 1.19x.

## Open questions, and what is now closed

Closed by Damon and the coordinator on the independent review at
`reviews/textquests-independent.md`:

1. **The human value stands at 646,708 s**, the IFDB hinted-player figure, with the 1983
   "over 30 hours" carried as the unaided upper scenario. The review's sensitivity work, which
   this note reproduces, is why: the imputation moves the suite only 0.89x to 1.12x and a
   resample of the votes 0.93x to 1.07x, both smaller than uncertainties the same rows already
   carry on the compute side. One consequence worth stating plainly: **the human time enters no
   inclusion decision.** The exclusion rule runs on progress against the human completer's 100
   per cent, so even the full 4.17x move to the paper's anchor would leave all four rows in and
   all eight excluded cells out.
2. **HowLongToBeat is usable as a source**, so `game-portal-gpt6astra` and
   `game-factorio-gpt6astra` stand on their own terms. It is simply not reachable from this
   environment by any of four routes, one of which is a 403 from the site's own edge, so no
   cross-check against it exists for these rows. [HowLongToBeat is
   unreachable](#howlongtobeat-is-unreachable).
3. **`ai_attempts = 25` stands and needs no convention change.** The dataset's seventeen other
   `total` rows carry 1 because each is a single continuous run; this work unit is 25 separate
   sessions with separate contexts and one agent instance each (`max_concurrent=25`), so 25 is
   the applicable recorded task-run count rather than a per-question normaliser. The precedent
   differs because the work unit differs.

Still open:

4. **Gemini's hidden reasoning.** If the coordinator prefers a central value that includes
   thoughts rather than a scenario, the Gemini row moves to 1.09e19 at 1,000 tokens a call.
   Left on the published counter here, since that is what the source measured, and since the
   endpoint evidence is a developer-forum demonstration rather than documentation.
5. **`human_time_method`.** Revision 1 moved it from `estimated` to `other_calculation`
   alongside the ruled `human_time_evidence` change, matching the Portal and Factorio rows and
   the source-published-means ruling in `DECISIONS.md`. That change was not enumerated in the
   revision brief, only implied by it, so it is flagged here as the one field a reverting
   coordinator might want back.
