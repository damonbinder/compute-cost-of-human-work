# SketchAgent drawing

## writing-sketchagent-quickdraw-sonnet35

Draw one recognizable black-and-white sketch of a common concept. The AI is SketchAgent with Claude 3.5 Sonnet (June 2024); the human baseline is an ordinary QuickDraw player. This point represents the method's simple-concept drawing setting, not scientific diagrams, iterative editing or human–AI collaboration.

[Original paper](https://openaccess.thecvf.com/content/CVPR2025/papers/Vinker_SketchAgent_Language-Driven_Sequential_Sketch_Generation_CVPR_2025_paper.pdf), §5.1/Table1, compares 500 sketches from 50 randomly selected categories. CLIP top-1 recognition is 0.23±0.05 for SketchAgent and 0.27±0.07 for humans; top-5 is 0.44 versus 0.49. In a separate preference test, human sketches were selected as more human-drawn 54.68±4.61% of the time. The [supplement](https://openaccess.thecvf.com/content/CVPR2025/supplemental/Vinker_SketchAgent_Language-Driven_Sequential_CVPR_2025_supplemental.pdf), §1/2.1, gives the exact model and average API cost of $0.05 per sketch. Evaluation used stochastic generation. Its exact category list and individual response logs are not released. The preference judges are not drawing-time participants.

Recognition and preference results support `match` for this simple-sketch task. Human time is based on recorded drawing durations with a planning allowance.

### Compute from the reported cost

Original [generation code](https://github.com/yael-vinker/SketchAgent/blob/14c4043064e91a0b2823718e4831b727e3c506d7/gen_sketch.py) sends one system/user prompt and receives planning text plus stroke instructions. Free generation passes no image, despite constructing a canvas for later display. It disables prompt caching. We therefore count text inference only, without inventing a vision encoder. The returned planning text is included in paid output; there is no additional reasoning multiplier. The closing answer tag is appended locally after the stop sequence and is not separately charged.

The published [June Sonnet price](https://www.anthropic.com/news/claude-3-5-sonnet) is $3/million input and $15/million output tokens. The original [Anthropic legacy tokenizer](https://github.com/anthropics/anthropic-tokenizer-typescript) is explicitly only an approximation for Claude 3 and later. We apply its NFKC normalization to the retained original prompt, add 12 assumed wrapper positions, and average the concept-name variation over the 20 timing categories. This gives 3,999.9 input tokens. Names change the otherwise fixed prompt by only a few positions; this is not a recovered tokenizer or original evaluation-category list.

Assuming one complete call per sketch, output is inferred as:

`($0.05 − 3,999.9 × $3/1,000,000) / ($15/1,000,000) = 2,533.353 tokens`.

That is below the released 3,000-token cap. The total is 6,533.253 tokens. At the shared assumed 100B active parameters, `2 × 100B × 6,533.253 = 1.30665e15 FLOPs`. The active-size prior is unchanged from models.csv, not an Anthropic disclosure. This is `params_tokens` with `transferred_workload`: billing constrains a reconstructed workload, not directly measured FLOPs. Small deterministic curve fitting and rendering are outside model FLOPs.

The paper-wide price is transferred to the simple-concept setting. Its averaging sample, rounding and retry coverage are unspecified. Original code allows up to three attempts following errors; no observed retry rate exists. Central one-call accounting follows the normal generation path, not an assertion that every call succeeded. Holding total reported cost fixed, two or three input prefixes imply 1.9466e15 or 2.5866e15 FLOPs because input and output have different prices. If the quoted cost excludes failed work entirely, those fixed-cost cases would not recover it.

Rounding $0.05 to the nearest cent gives 1.2400e15–1.3733e15 FLOPs; this is a rounding scenario, not a known reporting interval. Input-token estimates at 80–120% give 1.1787e15–1.4346e15, with output inferred consistently from the same cost. A 50–200B active-size range gives 6.5333e14–2.6133e15. These scenarios do not warrant a measured-workload label. Current code defaults to deterministic generation; the paper's stochastic protocol takes precedence.

### Human duration

The original [QuickDraw documentation](https://github.com/googlecreativelab/quickdraw-dataset) defines raw per-point timestamps. Twenty of 345 categories were selected by a fixed hash before inspecting durations; the first 100 released raw records per category give 2,000 unique drawings. This is a broad category sample with convenience prefixes within categories, not a random participant sample or the paper's exact 500 drawings. All recognition outcomes are retained. Source byte-range responses and Git identities of website assets were independently verified.

The mean first-to-last-point span is 8.4950695 seconds. It includes between-stroke thinking and pen movement, but excludes deciding how to start before the first recorded point. Add a judged two-second initial planning/movement allowance: **10.4950695 seconds**, approximately 10.5 seconds. An initial allowance of zero to five seconds gives 8.495–13.495 seconds. Mean pen-down time alone is 5.771 seconds and omits necessary work; it is not the chosen duration. Nine drawings exceed 20 seconds and remain included. The game limit is not substituted for actual drawing time.

Use `transferred_timings`, `estimated` and `point_estimate`. The 2,000 recorded drawings contribute directly to the duration estimate, so human_attempts is 2000 and the subset is all, not a count of judges or claimed independent people. The timing category mixture and paper-wide cost both transfer to this simple-sketch setting. Their provenance alone does not imply that the estimated human and AI tasks differ. The source's own AI/human quality comparison is retained, not recalculated using the QuickDraw game's separate recognition labels.

The [human-source audit](human-timing.md) contains category selection, per-drawing timestamps and source provenance. The original website's animal and other SVGs are retained for inspection; those gallery assets are not mislabeled as the released 500-sketch evaluation set or native API transcripts.

### Reproduction

Python 3 with `tiktoken`: run `recompute.py --sources /absolute/source/path --output /absolute/new.json`. The script checks retained hashes, invokes the standard-library human-timing audit and writes all calculations to a new output. It never calls a model. `convert-tokenizer.cjs` optionally rebuilds the standard BPE file from the original compressed vocabulary using npm `tiktoken`; the main calculator uses the retained conversion. JavaScript and Python independently count the example cat prompt as 3,999 positions including the assumed wrapper.
