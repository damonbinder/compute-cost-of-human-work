# First Claude 3.7 website

## agen-village-claude37-first-own-site

One first own-site episode on 13 October 2025: create a personal portfolio, deploy it on Netlify, and send the deployed URL for the requested redirect. The delivered work is two static HTML pages, shared responsive CSS, three simple illustrations, personality cards, project descriptions and a contact link. Human time estimates an experienced web developer producing comparable work from the same identity, personality results and prior-project descriptions, without AI assistance.

The estimate is **9,000 active human seconds** and **6.881378690855895 × 10^17 FLOPs**, including GPT-5-Codex coding helpers. The text-token estimate is **1,665,228.448**; image positions are kept separately below. Numerical precision preserves the calculation, not the accuracy of its assumptions.

### Episode and delivered artifact

The original [weekly goal](https://theaidigest.org/village/goal/each-agent-build-your-own-personal-website) asked agents to build their own sites and email their URLs. The [13 October sessions API](https://theaidigest.org/village/api/computer-use-sessions?villageId=00ebc425-074c-466f-ab2d-5aa2efa445aa&date=2025-10-13) supplies native model responses, tool actions, usage and helper stderr; the [events API](https://theaidigest.org/village/api/events?villageId=00ebc425-074c-466f-ab2d-5aa2efa445aa&date=2025-10-13&page=1) supplies controller actions and session summaries. `selection.json` lists the ten complete sessions and 45 relevant outer events by exact ID. The selected work starts at 17:01 UTC, reaches a deployed site before 18:21, and finishes the URL email at 19:42; the immediate completion report at 19:43 is included. All failed commands, tool actions and email attempts within those sessions remain counted.

Three intervening sessions reviewing a Git-workflow Google Doc are unrelated work and excluded. The two preceding wait/coordination responses remain included: the first explicitly considers a possible email workaround, and the second continues that wait. Later redirect verification, site improvements and the later rescue of Grok's website are outside this first own-site episode. This boundary does not claim completion of all work in the week-long goal.

The [deployed site](https://capable-sunflower-da6d3a.netlify.app) still serves the original homepage and CSS. Removing Netlify's identifiable later hosting-ad injection from the current homepage gives a 5,191-byte file whose Git blob hash exactly matches the final original Codex diff. The 6,889-byte CSS also matches its original diff hash. The original 3,122-byte `projects.html` is reconstructed from its complete new-file diff. Its current counterpart changes only the back-home URL spelling; the historical reconstruction is used here. `artifact-identity.json` retains those checks.

The three image files have the same byte sizes as the original terminal listing: 26,496, 40,680 and 11,414 bytes. The original canvas code creates a letter-avatar, a random-node network thumbnail and a five-bar illustration. These are illustrative graphics; the text at the edge of the chart graphic is clipped. The original responsive screenshot shows the chart image rendered, the deployed screenshot shows the site under its Netlify URL, and the final Gmail Sent screenshot shows the handoff message. The assets are not broken-image placeholders.

The portfolio copy describes D3, Chart.js, WebSockets and Node projects and claims outcome improvements. These are static descriptions of prior work, not implemented systems in this deliverable. No such application development is charged to the human estimate. Personality scores were explicitly supplied in the coding requests; no new psychological assessment occurred in this episode. The site's only JavaScript in its two public pages updates the footer year.

### Human effort

This is a task-inspected estimate, with no contributing timed human sample. Ordinary editing tools, a graphics editor or simple canvas/SVG code, browser developer tools and free static hosting are allowed. The human receives the supplied content and implements comparable scope and finish; exact copying of the final HTML is not the target.

| Work | Assumed active minutes | Basis in the artifact |
|---|---:|---|
| Organize supplied identity, scores and project material into page copy | 20 | Short about text, four result cards, descriptions of two prior projects and a skills list |
| Implement the two HTML pages | 35 | Repeated card markup, shared header/footer, project descriptions and contact link; no application logic |
| Style the shared responsive layout | 40 | Typography, blue palette, card shadows/hover states, image sizing and small-screen rules |
| Create and integrate the three simple graphics | 20 | Letter-avatar, small network diagram and five bars; ordinary drawing/code tools suffice |
| Check the pages and fix layout, asset or link problems | 20 | Two pages and one narrow-screen layout, rather than a multi-browser product QA program |
| Deploy the folder and hand over its URL | 15 | Static hosting upload, live check and short email; no backend, domain purchase or waiting for a reply |
| Total | 150 | 9,000 seconds |

The bounds re-run the table at each line's ends. Reusing a familiar stylesheet and card markup takes implementation to 20 minutes and styling to 15, with graphics, checks and deployment at 12, 12 and 10: 89 minutes. A full styling and copy iteration with asset preparation and a deployment problem takes them to 45 and 70, with 25, 30, 35 and 25 on the rest: 230 minutes. Styling moves the bound furthest. Neither is a measured percentile. The estimate is not derived from the agent's elapsed three-hour work window or an assumed typing rate. Use `assumed`, `estimated`, `point_estimate`, and `not_applicable` for human attempts/subset. Performance is `match` by construction: the target is this inspected static output at comparable quality, not a fully verified account of the portfolio's project claims.

### Native usage and scope

There are 292 selected computer-turn records. Ten initial mouse moves have the all-zero synthetic message ID and zero usage; they are excluded. The remaining **282 native responses have unique message IDs** and all identify `claude-3-7-sonnet-20250219`. Their ordinary input, cache creation and output total **2,379,773 combined positions**. The separate **6,569,467 cache-read positions** are excluded from the parameter-multiplication term. Native output includes thinking; it is counted once.

Of the 45 selected outer events, 12 chat events mirror START/WAIT controller responses with identical input/output counters within a second. A thirteenth mirrors the exact text and usage of a computer chat response. These are excluded, leaving **32 additional controller responses** and **371,007 input-plus-output tokens**, of which 360,232 are input. The parser records every match. The events' scalar counters do not disclose cache creation/read components. The central contribution uses the reported scalar total assuming no omitted cache creation; half/double controller-input cases expose that limitation. The native computer-chat mirror shows ordinary-input semantics for that mirrored field, so these scalar totals must not be described as measured full-prefix processing.

The [author's scaffold explanation](https://aivillageblog.substack.com/p/how-the-ai-village-works) describes screenshots after computer actions, session consolidation and memory updates. The visible summaries are much longer than the corresponding STOP response output counters: for example, the second STOP records three output tokens, while its summary contains 1,051 tokens under the stated proxy tokenizer. One additional consolidation call per selected session is therefore included as an estimate. Its input is the final native full context plus the final response, last tool result and a 32-token wrapper. For a GUI result the last screenshot is included; for a text result its retained text is tokenized. Actual summary text is tokenized with `cl100k_base`, an explicit proxy for this small missing component. This gives **517,168.88 combined positions**, including 7,610 summary output tokens.

Historical consolidation input, cache reuse and any separate memory-rewrite calls are not exported. Central accounting assumes a full retained-context summary using the primary model. Scenarios remove the additional input while retaining the visible summary output, or double the estimated input. They change total FLOPs to 5.8503 × 10^17 and 7.9125 × 10^17. No arbitrary allowance for undetected service retries is added.

### Coding helpers

Five complete original stderr traces identify Codex CLI 0.46.0 and `gpt-5-codex`; their final counters are 11,551, 24,500, 15,929, 17,330 and 20,792. Two original terminal screenshots supply the initial HTML and CSS-retry counters of 2,853 and 9,815. Thus **102,770 helper tokens are observed**. The original [output formatter](https://github.com/openai/codex/blob/rust-v0.46.0/codex-rs/exec/src/event_processor_with_human_output.rs) prints `blended_total`, and the original [protocol implementation](https://github.com/openai/codex/blob/rust-v0.46.0/codex-rs/protocol/src/protocol.rs) defines it as input minus cached input plus output. Internal tool calls, retries and reasoning are already included. Repeated diffs printed in the same stderr are not additional work.

Two dispatched helpers have missing counters:

| Invocation | Central fresh tokens | Scenarios | Basis |
|---|---:|---:|---|
| First CSS extraction/styling attempt | 7,000 | 3,000–20,000 | The running helper read the page and removed inline CSS; the terminal was closed before a counter appeared. Before retry, only the shortened HTML existed. The completed similar CSS retry used 9,815 tokens. |
| First request for all four personality cards | 25,000 | 0–60,000 | The bash call timed out after dispatch; no helper trace survived. The later two-card/CSS task used 24,500 and the remaining-card task 15,929. The central allowance represents substantial failed work, not three complete replacement calls. |

These estimates are based on the actual work and nearby completed helpers, not elapsed-time throughput. The next command was explicitly rejected because the bash tool needed restarting; it is not another dispatched helper. A duplicate initial HTML command was typed while the first process was running; the screenshots establish one completed invocation, not a second launch. Total helper work is **134,770 fresh text tokens**. The missing-helper low/high cases move total compute only to 6.8234 × 10^17 / 6.9774 × 10^17 FLOPs.

### Text, screenshots and neural operations

The historical search-indexed original [Anthropic vision documentation](https://docs.anthropic.com/zh-CN/docs/build-with-claude/vision) explicitly names Claude 3.7 and estimates image units as pixel area divided by 750 when no resizing is required. Its relevant excerpt is retained as `methods/anthropic-vision-historical-index-extract.md`; direct opening now redirects to later documentation. At the source's 1024×768 desktop size this is **1,048.576 approximate image units**. The 28px rule in current documentation is a sensitivity only, not evidence about the historical tokenizer.

One initial screenshot and one after each graphical tool action are assigned to the next input; bash and chat outputs are text. Across 247 native GUI transitions, full-context growth minus the previous response has median 1,108 positions (range 832–1,587). This corroborates the scale, while also showing that wrapper/chat/history treatment prevents an exact split.

For each request, the parser places the new image interval near the end of its newly added context, before an assumed 10-token reminder, capped so it cannot overlap earlier context. Context never shrinks in the selected sessions. It retains earlier intervals and intersects them with the **native cache-read prefix**, counting only image positions outside that prefix as fresh. This matters because recent screenshots are repeatedly processed before they enter a cached prefix. It also counts images retained for the estimated summaries. The result is **1,737,490.432 fresh image-unit passes**, leaving **1,530,458.448 primary text tokens**. Add the helper text to obtain the CSV's 1,665,228.448 tokens. Screenshot separation is estimated; the raw combined native counters remain intact.

Both model records use the shared **100B active-parameter prior**, or 2 × 10^11 FLOPs per newly processed backbone position. Neither provider publishes the architecture. Anthropic's [24 February 2025 launch](https://www.anthropic.com/news/claude-3-7-sonnet) establishes the release date; `20250219` in the native checkpoint name is not the release date. The Sonnet size is the existing explicit family-scale assumption, not a reported count. [OpenAI's GPT-5-Codex announcement](https://openai.com/index/introducing-upgrades-to-codex/) establishes first subscription availability on 15 September, before API-key availability on 23 September. Its moving October alias does not identify immutable weights. The helper's shared GPT-5 family prior is likewise assumed.

The central backbone applies the coefficient to all fresh combined positions, including the estimated image contribution. Mapping an image accounting unit to a physical backbone position is a proxy; one-half and twice that visual contribution are scenarios. A separate frontend proxy uses the original [CLIP ViT-L/14-336 configuration](https://huggingface.co/openai/clip-vit-large-patch14-336/blob/main/config.json): 24 blocks, width 1,024, MLP width 4,096 and 577 positions. Per crop:

`2 × 576 × 14² × 3 × 1024 + 24 × (8 × 577 × 1024² + 4 × 577 × 1024 × 4096 + 4 × 577² × 1024) + 2 × 1024 × 768 = 381,919,789,056 FLOPs`.

Twelve 336px crops cover 1024×768 with padding. Apply that frontend allowance per estimated fresh screenshot-equivalent pass; one and 24 crops are alternatives. This is an architectural proxy, not Claude's disclosed encoder. It contributes 7.5941 × 10^15 FLOPs, about 1.10% of the central total. Nonlinear operations are omitted. Context-dependent decoder attention, including attention over cached keys/values, is carried in `compute_flops` (`research/attention-correction.md`). Known cache reads are not charged again as fresh matrix multiplication. The full native-prefix alternative is retained for comparison, not used centrally.

The calculation uses `operation_count` and `derived_assumed_inputs`; `input_cache_creation_output` describes the text workload after known cache reads are excluded. The whole episode is one AI attempt with `total` compute and `all` selection, retaining its failed intermediate work. Model-size, image serialization, visual-backbone, frontend, missing-helper, controller and consolidation sensitivities are all in `calculations.json`. These are assumption tests, not statistical confidence intervals.

### Replay

Use Python 3.12 or later with `tiktoken` installed. The retained run used tiktoken 0.14.0 and `cl100k_base`; no model/API calls are needed. The tokenizer vocabulary may be downloaded on first use if absent from its cache.

After publication, the study files are under `dataset/research/village-websites-remaining/` and `dataset/sources/village-websites-remaining/`:

```sh
python3 /absolute/path/dataset/research/village-websites-remaining/recompute.py \
  --source-dir /absolute/path/dataset/sources/village-websites-remaining \
  --selection /absolute/path/dataset/research/village-websites-remaining/selection.json \
  --output-dir /absolute/path/new-replay-directory
```

The output directory must not exist. The script verifies native message uniqueness, usage mirrors, helper counters and original artifact hashes, and writes all central arithmetic and sensitivity results to a new `calculations.json`. `agent-work/sources/village-websites-remaining/manifest.json` records original URLs and retained-file hashes. Archives and authoring helpers are outside the publication package.
