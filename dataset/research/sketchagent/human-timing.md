# SketchAgent human source and released-output audit

Recommended human duration: **10.4950695 seconds**, rounded conceptually to 10.5 seconds. This is a transferred estimate: raw QuickDraw first-to-last-point mean 8.4950695 seconds plus 2 seconds for initial planning/moving to the first point. It is not a measured completion time for SketchAgent's exact evaluation cohort. Use transferred_timings/estimated and preserve the cohort transfer.

## Original evaluation

Main paper§5.1 randomly selects 50QuickDraw classes and generates 10 sketches/class. The human CLIP baseline comes from QuickDraw. Top 1recognition is0.23±0.05 for default SketchAgent versus0.27±0.07 human; top 5is0.44±0.03versus0.49±0.06. These are reasonably close, not evidence of identical task success.

Supplement§2.1's2AFC experiment instead uses50 sketches from 50 classes **per method**, with 150 MTurk workers each completing 50 sessions. It asks which sketch appears human-drawn. Human sketches receive 54.68±4.61%preference over SketchAgent. This supports broadly matching human-like appearance; it is not 54.68%task accuracy, and the 150 judges are not 150 drawing-time participants. Neither the code repository nor the separate website repository supplies evaluation IDs or the complete50-class list.

## Native human timings

Original documentation: https://github.com/googlecreativelab/quickdraw-dataset . Raw data documentation says each stroke has x,y,t arrays, with t in milliseconds from the first point. Simplified files delete these timestamps; they cannot recover duration. Retained quickdraw-readme.md preserves the definition.

Selected 20 of the 345 original classes by ascending SHA256 of `sketchagent-human-duration-v1:` plus exact category name, before reading timings. Classes are bottlecap, car, sink, dog, goatee, mouse, potato, church, laptop, dragon, boomerang, cat, broom, horse, scissors, peanut, stove, spreadsheet, hand, mountain. This supplies a broad mix rather than selecting the easiest recognition classes. Within each class, the first100 raw records are a convenience prefix, not a random subsample of users. There are 2000 unique drawing IDs from 92 countries;1844 are marked recognized. All records, including 156 unrecognized drawings, are retained.

Raw URL pattern is `https://storage.googleapis.com/quickdraw_dataset/full/raw/<URL-encoded-category>.ndjson`. `raw-source-manifest.json` gives the exact 25 URLs, requested byte ranges, bytes,100-record counts, SHA256 and response headers. Twenty files are the broad sample; five additional gallery-animal files are kept separately and do not enter the chosen mean. Each prefix was independently re-requested as an exact HTTP byte range; all responses matched byte-for-byte. Every file ends after a complete newline-delimited JSON record. Source response headers preserve full-object range sizes/ETags; this is not a partial JSON download interpreted as100 records.

For each drawing, the envelope is `(max(t)-min(t))/1000`; pen-down time is the sum of each stroke's own duration. Broad-sample mean envelope8.4950695 seconds, median7.499 seconds, mean pen-down5.7713895 seconds, mean 5.741 strokes. The envelope includes pen-up movement/thinking between strokes, appropriate active drawing effort for a short sketch, but it may include small pauses. It excludes initial planning before the first point. Nine records exceed20 seconds; maximum 29.63 seconds. They are kept, not clamped to the game limit or discarded merely for disagreeing with it.

A 2-second initial allowance is a judgment for reading a simple concept and choosing a starting shape. It does not assume planning always begins at the first recorded point. Mean envelope plus 0–5 seconds gives8.495–13.495 seconds; pen-down alone5.771 seconds is an incomplete-component lower scenario, not the preferred total. Variation in category mixture and desired detail remains more important than reporting decimal precision. The original study's selected50categories and drawing IDs are unknown, so this is a category-population transfer. The QuickDraw time cap is not used as measured active time.

The five gallery-only timing sets (100 each) have envelope means: butterfly 7.696s, camel 8.789s, elephant 11.937s, frog 10.825s, raccoon 13.302s. Their greater animal-detail burden shows why substituting an all-animal sample for the unknown50-category aggregate would bias the timing estimate. They are available if a later point explicitly targets those drawings.

## Attributable original outputs

The project page https://yael-vinker.github.io/sketch-agent/ is backed by **yael-vinker/sketch-agent**, separate from code repo **yael-vinker/SketchAgent**. Website tree pinned at 54bf05309b0c2f23dcd1bfee2510cbf0640ece69 is retained. All 49 SVGassets were downloaded byte-identically to that tree and checked by Git blob SHA. They include 15 individual gallery examples (five animals plus landmarks/science), seven variabilitysheets, user/agent/collaboration triples, and explanatory figures. Do not count49 assets as49independent evaluated AI outputs.

The gallery's individual SVGs are rendered outputs, not the original <thinking>/stroke-command transcripts. No JSON, CSV, API traces or evaluation manifest appears in the full92-entry website tree. The main code tree likewise has no generated-output corpus. The SVGs can support visible-output inspection and geometric path counts, but cannot reveal hidden natural-language planning length or exact API token usage. Paper-wide generation-cost evidence is stronger for that purpose if its scope is disclosed.

Supplement§1 explicitly names Claude3.5-Sonnet 20240620. Default stochastic settings were used for the 50×10generation experiment; temperature0/top_k1 were used only for controlled conditions. Do not infer the evaluation protocol from today's deterministic code default.

## Replay

`python3 audit_human.py --sources <published-human-source-directory> --output <new-json-outside-sources>` uses the standard library only. It verifies raw manifest byte lengths/hashes and every SVG's original Git blob hash, recomputes category selection, checks 2000 unique IDs, and returns all per-drawing/per-category timings. `timing-audit.json` is the retained result. No model execution or paid API call occurred.
