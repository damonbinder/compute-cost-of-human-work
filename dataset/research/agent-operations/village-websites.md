# AI Village: two first website deployments

These points cover each agent's first website build, initial deployment and URL handoff on 13 October 2025. Opus 4.1 ends at 17:36:34.451 UTC; Sonnet 4.5 ends at 17:42:59.495 UTC. Later website changes, DNS work and unrelated Git-workflow discussions are outside these points. Both start with the agent's existing biography, personality results and project descriptions available as material for the page. Creating those earlier projects is outside the work unit.

The original [goal](https://theaidigest.org/village/goal/each-agent-build-your-own-personal-website) ran for a week. Its displayed15 scheduled agent hours is a schedule, not human effort or inference usage. The shorter observations here are related to the original leads; they do not represent the entire week.

## Original evidence

The public replay's own Javascript identifies these read-only endpoints:

- `/village/api/events?villageId=00ebc425-074c-466f-ab2d-5aa2efa445aa&page=1&date=2025-10-13`
- `/village/api/computer-use-sessions?villageId=00ebc425-074c-466f-ab2d-5aa2efa445aa&date=2025-10-13`

Retained JSON includes the original messages, commands, tool outputs, session IDs and native Anthropic usage. `selection.json` names every included session and cutoff. The unfiltered downloads are preserved outside the publication sources in `source-archive/`; publication copies select eight sessions and the two agents' events plus human messages, without changing retained record values. The API includes some old sessions despite the date filter, so selection is by actual timestamps and session IDs.

The [publisher's data card](https://huggingface.co/datasets/aidigestorg/ai-village) distinguishes original turns from generated recaps, warns that agents can misreport, and says exact LLM-call prompts are not exported. Its full download requires reviewed access; this collection uses the independently public replay. Its website-goal recap is a source lead, not the evidence for the delivered code.

`recompute.py` reconstructs the historical HTML by applying the original Codex diffs with strict hunk checks. Opus's 221-line, 6,742-byte page is identical to the currently accessible [original deployment](https://resilient-pudding-ae3a6a.netlify.app). Sonnet's 433-line, 13,123-byte initial page differs from its later public website; the later version is not substituted. The reconstructed files are `opus41-first-site.html` and `sonnet45-first-site.html`.

## Work delivered and human effort

The human is a professional frontend developer, familiar with HTML/CSS and ordinary editor, browser and hosting tools. Existing biography, personality numbers and project links are supplied. This is an estimate of producing comparable page content and the same initial handoff without AI, not of manually repeating the agent's clicks or waiting through its failures.

| Work | Opus 4.1 | Sonnet 4.5 |
|---|---:|---:|
| Decide page structure and adapt supplied content |30 min|45 min|
| Write and style the page |75 min|100 min|
| Check in a browser and make small fixes |20 min|20 min|
| Initial hosting setup/upload and URL handoff |15 min|15 min|
| Total |140 min = 8,400 s|180 min = 10,800 s|
| Plausible experienced-developer range |80–240 min|100–300 min|

Opus's page has a gradient header, short biography, four descriptive project cards, five skills and contact links. There is no Javascript, backend, charting engine or working version of the projects described. Sonnet's page has a gradient header, six CSS personality bars, six portfolio cards, two technical-project cards and a footer. It also has no Javascript or embedded implementations of the linked sketches. One portfolio link is explicitly disabled. The additional styling and content explain the modestly larger human estimate. The estimates permit normal snippets and editor completion without generative AI; they do not assume typing all code from scratch at a fixed rate.

The ranges reflect familiarity with responsive CSS, amount of visual revision and hosting friction. They are judgmental scenarios, not measured distributions. No human completion timings were recorded for these two sites. Both points use `match` because the estimated human target is the actual first artifact and handoff, including its limitations.

Sonnet's first deployment was `resonant-gecko-15152c.netlify.app`. A human administrator later reported that it requested a password and prevented him viewing the page: event `43c562fe-f82b-4510-b993-f266f3ebf5e4` at 19:58:53.193 UTC. Thus this point does not claim successful unrestricted public hosting. It covers the completed page and its initial password-protected upload. Later repairs are not credited or charged. Opus's first deployment and handoff are supported by its uploaded artifact, native action sequence and session-end records.

## Recorded model work

| Quantity | Opus 4.1 | Sonnet 4.5 |
|---|---:|---:|
| Native computer calls |100|71|
| Native ordinary input positions |493,978|467,118|
| Native cache-creation positions |217,712|303,687|
| Native cache-read positions, excluded |1,743,403|1,479,446|
| Native output tokens, including thinking |13,006|14,427|
| Additional controller input plus output |92,157|158,156|
| Estimated consolidation input plus output |114,125|187,170|
| GPT-5-Codex fresh text tokens |4,950|62,064|

Computer-call counts exclude synthetic initial mouse moves with zero usage. They retain failed actions and all paid native outputs. Native message IDs are unique in the selected calls. Some computer turns also create an `AGENT_TALK` event with the same content and counters; those are removed from the event sum. A controller call can produce both a start-session event and a chat event, which are also deduplicated using identical counters within one second. The calculator retains the pairwise match audit.

Native Anthropic input and output counters have their provider meanings: add ordinary input, cache creation and output; do not add known cache reads to the parameter-multiplication term. Output already includes thinking. The scalar controller events do not retain cache creation/read fields. Their reported input plus output is the central contribution, assuming no omitted cache creation. The sensitivity adding another complete observed controller-input total shows the effect of missing creation. A small reported scalar input is not evidence of zero cache activity.

At each selected session's end, a substantial summary appears that is not the short recorded controller output. The central estimate includes one extra consolidation call, using the primary model, the final native full context plus its final output, and the actual summary text tokenized with `cl100k_base`. This proxy tokenizer and the retained-full-context assumption are explicit estimates. The original [scaffold explanation](https://aivillageblog.substack.com/p/how-the-ai-village-works) describes session consolidation and memory updates, but does not reveal the historical call input or cache treatment. Scenarios remove this extra call entirely or double its input. Extra unknown unlogged service retries are not assigned an arbitrary multiplier.

## Coding helper

The actual stderr identifies OpenAI Codex CLI 0.46.0, `gpt-5-codex`, and the displayed reasoning setting. Its original [output formatter](https://github.com/openai/codex/blob/rust-v0.46.0/codex-rs/exec/src/event_processor_with_human_output.rs) prints `blended_total`. The original [TokenUsage implementation](https://github.com/openai/codex/blob/rust-v0.46.0/codex-rs/protocol/src/protocol.rs) defines that as input minus cached input plus output. Therefore each completed invocation's final counter already excludes cache reads and includes all its internal requests. The repeated diffs in stderr are not additional calls.

Opus has one completed invocation reporting 4,950 fresh tokens. Sonnet has six completed invocations totaling 52,064, plus one 180-second timeout. The later read of the file shows that this first timeout had produced a substantial page before the next command replaced it. Central timeout allowance: 10,000 fresh helper tokens; scenarios 4,000–40,000. This is inferred work, not a throughput calculation from 180 seconds. All helper work, including this discarded page, is included.

[OpenAI's release](https://openai.com/index/introducing-upgrades-to-codex/) establishes GPT-5-Codex as a GPT-5 derivative first available in Codex on 15 September 2025; API-key availability followed 23 September. The alias was updated over time, so the exact October snapshot is unresolved. Its 100B active-parameter prior transfers the shared assumed GPT-5 registry value; OpenAI does not disclose its size. The two primary model rows are unchanged registry copies: 180B for Opus 4.1 and 100B for Sonnet 4.5. The calculator varies all active-size priors by 0.5–2.

## Screenshot and text separation

Anthropic input usage combines text and image positions. It must not all be entered into the CSV's text-token field. The retained GUI action sequence and native input growth support a rough separation: across 103 transitions following graphical actions, input growth minus the previous output has median 1,039 positions (range 836–2,052). These increments also include wrapper text and shared-chat updates.

Central estimate: 1,000 positions per inserted screenshot, consistent with the apparent 1024×768 desktop and roughly area/750 image-token accounting. Count one initial screenshot and one after each graphical action that is followed by a model call. Bash and chat-only actions do not insert an image. Within these selected sessions, native full input does not shrink. Place each new screenshot at the end of that call's input, capped by the newly added positions so it cannot overlap previous input/output text or earlier screenshots. Retain earlier image intervals, and intersect those intervals with the native cache-read prefix to exclude cached image positions. Exact serialization and image placement are not exported. Re-run with 750/1,250 positions to inspect the text-count sensitivity; it does not change the main native combined-position arithmetic.

This gives estimated fresh image-position totals, including consolidation, of 366,183 and 396,835. Subtracting these from primary positions and adding helper text gives 569,745 and 795,787 text tokens. These are estimates, not native text-only counters.

The backbone term applies 2 × active parameters to all fresh combined positions, including images. A separate visual-encoder allowance uses the original [CLIP ViT-L/14-336 configuration](https://huggingface.co/openai/clip-vit-large-patch14-336/blob/main/config.json): 24 layers, hidden width 1,024, MLP width 4,096, 576 patches plus one class position. Its arithmetic is patch projection plus 24 × (8SH²+4SHM+4S²H), plus pooled projection, with two operations per MAC. Twelve 336px crops cover a 1024×768 image. Apply that allowance per estimated fresh image encoding; one and 24 crops are scenarios. CLIP is an architectural proxy, not a claim about Claude's encoder. The central frontend contributes 0.50% and 0.76% of total FLOPs. Softmax/norm are omitted. Context-dependent decoder attention, including attention over cache reads, is carried in `compute_flops` (`research/attention-correction.md`).

## Result and replay

Total central compute is 3.378203104093907e17 FLOPs for Opus and 2.4034310967388045e17 for Sonnet. Use `operation_count` and `derived_assumed_inputs`: model sizes, missing consolidation, screenshot split/frontend and the Sonnet timeout are estimated. Full native-prefix alternatives, retaining known cache reads, are in `calculations.json` for comparison only.

Run from any working directory:

```sh
python3 /absolute/path/research/recompute.py --source-dir /absolute/path/sources --selection /absolute/path/research/selection.json --output-dir /absolute/path/replay-output
```

The dependency is `tiktoken` with `cl100k_base`; it only tokenizes the retained summaries. The script checks usage mirrors, message IDs, source diffs and original artifact hashes. `calculations.json` retains each included native counter, helper value, controller record and sensitivity. The reported precision preserves arithmetic, not measurement accuracy.
