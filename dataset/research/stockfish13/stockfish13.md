# Stockfish 13: neural work on chess puzzles

These are new local observations collected on 13 September 2026, using the released Stockfish 13 engine and its default network. They measure NNUE arithmetic during complete puzzle attempts. They do not reconstruct an earlier tournament or convert engine ratings into compute.

## Task and observations

The source is the 10,000-puzzle CSV released with [Searchless Chess](https://github.com/google-deepmind/searchless_chess/blob/90ae0e6b121673fc3079aaeffa047580bb600c0a/src/puzzles.py), downloaded from the authors' [data bucket](https://storage.googleapis.com/searchless_chess/data/puzzles.csv). Before execution, `random.Random(42).sample(range(10000), 1000)` selected 1,000 rows without replacement; `selection.json` retains their indices, IDs and source hash. The sample requires an average 2.276 solver moves per complete reference line. Its mean puzzle rating is 1435.483, with range 434–2824; ratings are descriptive and do not enter either axis.

Each attempt starts from the original PGN history and puzzle position. The first listed source move is the opponent's setup move; the solver then supplies moves at odd indices, with the source opponent replies supplied automatically. An attempt ends at the first wrong move or at completion. As in the original evaluator, an alternative move that immediately checkmates is accepted. Each budget produced nine such accepted alternatives.

Settings are one thread, 16 MB hash, NNUE enabled, full skill, MultiPV 1, no strength limit and no external tablebases. The node limit applies separately to each solver decision. `ucinewgame` clears the transposition table and search history before each puzzle; normal state is retained between decisions within a puzzle. An uninstrumented control engine receives the same commands. Across all 4,230 decisions, the two engines have identical best moves, final search information apart from timing/rate fields, and node counts. Controls validate the measurement; they do not assist the solving engine and are excluded from task compute.

| Per whole puzzle attempt | 2,500-node decisions | 32,000-node decisions |
|---|---:|---:|
| Attempts | 1,000 | 1,000 |
| Complete successes | 872 | 966 |
| Mean neural arithmetic | 28,817,138.716 | 368,649,537.164 |
| Mean actual search nodes | 5,061.966 | 58,874.448 |
| Mean NNUE evaluations | 740.487 | 9,564.451 |
| Mean solver decisions | 2.026 | 2.204 |
| Attempts with no NNUE evaluation | 41 | 42 |

Every attempted puzzle enters the mean, including failures and zero-NNUE attempts. Stockfish is a hybrid engine: some searches use only its classical evaluator. The arithmetic column covers neural computation; classical evaluation, move generation and search instructions are not assigned an arbitrary FLOP equivalent. The source node counts retain a separate measure of search workload.

## Model

[Stockfish's release announcement](https://stockfishchess.org/blog/2021/stockfish-13/) establishes public availability on **19 February 2021**. The original `sf_13` tag resolves to commit `3597f1942ec6f2cfbd50b905683739b0900ff5dd`. The default file is `nn-62ef826d1a6d.nnue`, 21,022,697 bytes, SHA-256 `62ef826d1a6d11b9e814188025aa02a60815c037292e0ef9bbb9bf4f724e5e63`.

The [architecture](https://github.com/official-stockfish/Stockfish/blob/3597f1942ec6f2cfbd50b905683739b0900ff5dd/src/nnue/architectures/halfkp_256x2-32-32.h), `features/half_kp.h` and `nnue_common.h` specify 41,024 sparse input features, a shared 256-wide feature transformer evaluated from both players' perspectives, and affine layers 512→32→32→1. Including biases, the network contains:

```text
41,024 × 256 + 256 + 512 × 32 + 32 + 32 × 32 + 32 + 32 + 1
= 10,519,905 parameters
```

No text-token coefficient applies: sparse accumulator reuse and variable search determine the work. The model CSV therefore uses `not_applicable` for shared per-token and separate encoder/decoder fields.

## Arithmetic

`instrumentation.patch` adds counters to the pinned source without changing its evaluation or search calculations. The build uses the original ARM NEON implementation. The only compatibility edit in both control and instrumented sources removes an obsolete Clang option from the Makefile. The complete original source archive, network and native output are retained.

For each NNUE evaluation, the three affine layers execute 17,440 products. The inspected NEON implementation performs the corresponding 17,440 additions and three extra reduction additions for each of its 65 outputs: **35,075 affine operations** per evaluation. Counters also record:

- 256 additions per active feature during an accumulator refresh;
- 256 additions or subtractions per inserted or removed feature in each accumulator actually updated, including both historical updates when that path executes;
- one output scaling division per evaluation.

Copying a cached accumulator incurs no invented matrix multiplication. The measured total is the sum of affine multiplies, affine additions, sparse additions/subtractions and output divisions. Integer precision does not remove neural arithmetic under the dataset convention. The 576 clipped values and 64 fixed-point activation shifts per evaluation are separately recorded and excluded from the arithmetic sum, as are indexing, copying and control instructions. This is an operation count, not a CPU instruction count or hardware-runtime estimate.

| Component, total over 1,000 attempts | 2,500-node decisions | 32,000-node decisions |
|---|---:|---:|
| Two operations per affine multiply-add | 25,828,186,560 | 333,608,050,880 |
| Additional NEON reductions | 144,394,965 | 1,865,067,945 |
| Sparse accumulator arithmetic | 2,843,816,704 | 33,166,853,888 |
| Output divisions | 740,487 | 9,564,451 |
| Total | 28,817,138,716 | 368,649,537,164 |

The CSV records each total divided by 1,000: `mean`, `all`, 1,000 AI attempts, `measured_operations`. The saved native output supports every counter and outcome. No assumption about omitted output tokens or failed-call generation is required.

## Human time and performance

[Sheridan and Reingold (2014)](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2014.00941/full), Methods and the opening Results paragraphs, report 17 expert players completing eight move-selection problems each. Their mean decision time was **28.946 seconds**. Participants pressed a button when they had decided, then verbally reported their move; response entry was outside the timer. All 136 expert trials contribute to the timing donor. None reached the three-minute limit. The later correct-only restriction concerns eye-movement analyses, not this reaction-time summary.

Experts received the maximum master rating on **93% of trials**. Rating 10 means one of the best moves, rather than exact agreement with one reference move. This is a different eight-problem collection and a first-move assessment, whereas our AI outcome requires the whole reference line, allowing immediate alternative mates.

The target human is an expert solving a complete sampled puzzle on an interactive board without an engine, with opponent replies supplied. The estimate is **35 seconds**: approximately 29 seconds to find the initial tactical plan plus an assumed six seconds for entering that move and checking/entering the continuation. The sample averages 1.276 further own moves. Planning already involves continuations, so multiplying the first-move decision time by the number of moves would repeat much of the reasoning. Inspection of sampled puzzles found short mating, material-winning and defensive lines, with some longer calculation problems. **15–90 seconds** is a sensitivity range for easier or harder mixtures and continuation effort; it is not a confidence interval.

This is `transferred_timings` and `estimated`, with a `point_estimate`, donor subset `all` and 136 contributing attempts. The 136 is a donor count, not a measurement of people doing these 1,000 puzzles. Both performance classifications are broad transfer judgments. The donor's 93% first-move score does not establish a 93% full-line baseline: 6.2% conditional continuation failures would reduce it to 87.2%. Both 87.2% and 96.6% complete success are treated as broadly comparable with this expert baseline. `different_assessment` records the different problem collections, first-move versus complete-line endpoints and grading criteria. The study does not supply a measured human full-puzzle success rate for this sample.

## game-stockfish13-puzzle-nodes2500

One complete puzzle attempt at 2,500 nodes per solver decision: **28,817,138.716 neural operations**, **35 estimated human seconds**, **872/1,000 complete successes**, classified **match** with the transferred expert baseline.

## game-stockfish13-puzzle-nodes32000

One complete puzzle attempt at 32,000 nodes per solver decision: **368,649,537.164 neural operations**, **35 estimated human seconds**, **966/1,000 complete successes**, classified **match** with the transferred expert baseline.

## Reproduction

The ordinary replay needs Python 3 and `python-chess` (the original observations used chess 1.11.2). It reads original puzzles and the compressed native log, independently regrades all attempts, checks the paired controls and recomputes the CSV means. It does not run a chess engine. Pass actual paths and choose a new output outside the source directory:

```bash
python3 -B /path/to/research/stockfish13/recompute.py \
  --sources /path/to/sources/stockfish13 \
  --selection /path/to/research/stockfish13/selection.json \
  --output /path/to/new-results/stockfish13.json
```

To collect new observations, an ARM NEON host, Clang, Make and `python-chess` are needed. Prepare a new working directory from the retained original archive and network:

```bash
python3 -B /path/to/research/stockfish13/prepare_instrumentation.py \
  --archive /path/to/sources/stockfish13/stockfish13-source.zip \
  --net /path/to/sources/stockfish13/nn-62ef826d1a6d.nnue \
  --workdir /path/to/new-stockfish-build
make -C /path/to/new-stockfish-build/baseline/src -j2 build COMP=clang ARCH=apple-silicon
make -C /path/to/new-stockfish-build/instrumented/src -j2 build COMP=clang ARCH=apple-silicon
python3 -B /path/to/research/stockfish13/run_observations.py \
  --puzzles /path/to/sources/stockfish13/puzzles.csv \
  --selection /path/to/research/stockfish13/selection.json \
  --baseline /path/to/new-stockfish-build/baseline/src/stockfish \
  --instrumented /path/to/new-stockfish-build/instrumented/src/stockfish \
  --net /path/to/sources/stockfish13/nn-62ef826d1a6d.nnue \
  --output /path/to/new-results/stockfish13-observations.jsonl \
  --max-runtime-seconds 1800
```

The runner preserves partial output if its runtime guard is reached. The retained complete log is losslessly gzip-compressed; its original and compressed hashes are in `build-metadata.json` and the source manifest. `calculations.json` contains the full regrade and summary. Sources are read only; reruns must write new files.
