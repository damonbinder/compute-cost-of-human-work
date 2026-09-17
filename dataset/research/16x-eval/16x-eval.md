# 16x Eval: Markdown cleaning

Original records: [public export](https://github.com/paradite/eval-data/blob/b1244027edc2d745bc88f14f81e5683a7b31a438/model-eval-results/latest/evals-Clean_markdown__Medium_-2025-07-24.json), pinned commit b1244027edc2d745bc88f14f81e5683a7b31a438. The retained JSON contains the complete prompt, three supplied files, responses, ratings and token counters. Both selected runs are dated July 17, 2025. They use the Anthropic provider and the dated May 14 model IDs; the official public release was May 22, not May 14.

## Task and performance

The developer must write one TypeScript function that unwraps fenced code and Markdown links, removes heading markers, tables, React components, import statements and frontmatter. The supplied fixture contains one short Markdown document, including nested React components and two code fences. The test compares the resulting string with a supplied 627-character answer after trimming its ends. It does not assess a general Markdown parser. In particular, the fixture has no import statement.

I inspected both functions and ran them against the original fixture. Opus matches exactly. Sonnet preserves the content but removes six blank lines; its trimmed output has 621 characters. This agrees with the author's pass/formatting assessments; the retained ratings are 9.25 and 8. The additional 0.25 rewards short correct code; that style bonus is not our human comparison criterion.

The assumed professional human target is passing this exact test after implementing the requested transformations. Opus therefore matches that target. Sonnet is below on this binary completion criterion, with a small, explicitly identified formatting error rather than an inability to implement the main transformations. Neither observation estimates a model's success probability on repeated trials.

## Human time

Central estimate: **600 active seconds**, with bounds of 420 and 1,080 seconds. This is an estimate from inspecting the actual task, not an observed developer timing or a transfer from an unrelated software benchmark.

The baseline is a professional TypeScript developer familiar with regular expressions, working without AI. The project, test and fixture are supplied. Reading the seven rules and the roughly one-page example takes about two minutes. Implementing the short sequence of transformations takes about five minutes. Running the test, locating whitespace or ordering errors, and checking the result takes about three minutes. These are rough allocations supporting the rounded ten-minute estimate, not independent measurements. The bounds run those same three stages at their ends. A fluent developer reads in 90 seconds, implements in three and a half minutes and checks in two: 420 seconds. The whitespace or ordering error the fixture invites costs one extra implement-and-check cycle on top of the central: 1,080 seconds. General Markdown compliance, deployment and project setup are outside this task.

The human may run the supplied test and edit the function. The AI gets its text but no execution feedback. This concrete tool difference is flagged. No human timing sample, successful-attempt sample or observed human success rate is claimed. Both model rows use the same human estimate, so they do not supply independent evidence about human duration.

## Model coefficients

[The original throughput analysis](https://unexcitedneurons.substack.com/p/estimating-the-size-of-claude-opus) estimates Opus 4 at roughly 174–196 billion active parameters under FP8 serving assumptions. The shared model record uses a rounded 180 billion, giving 360 billion FLOPs/token. This remains a serving-based estimate, not an Anthropic architecture disclosure. The source discusses precision and serving assumptions that could materially change it.

For Sonnet 4, the same analysis estimates the subsequent Sonnet 4.5 at roughly 98–110 billion active parameters. I transfer a rounded 100 billion to Sonnet 4, giving 200 billion FLOPs/token. There is no direct Sonnet 4 size measurement here. Use 50–200 billion as a sensitivity range; this transfer is a weaker input than the task's recorded token counts. The source and official release announcement are retained alongside the export.

## Compute accounting

Each row represents its one recorded direct response, not a selected best of multiple runs. The export contains 687 input tokens for each Claude call, 374 Sonnet output tokens and 398 Opus output tokens. Reported reasoning tokens are zero and the total agrees with input plus output. No helper call or test-feedback loop appears in these records.

The export has no cache-read or cache-creation fields. The estimate counts its input total as fresh processing; it does not invent a cache split or multiply by unobserved retries. The shared two-parameter coefficient omits context-dependent attention arithmetic, which `compute_flops` carries separately (`research/attention-correction.md`). The combined model-size and cache assumptions are why compute_evidence is derived_assumed_inputs despite the native usage counters.

## 16x-clean-markdown-sonnet4

Run c1906794-d280-469f-a262-bd154fab9791, claude-sonnet-4-20250514. Compute: (687 + 374) × 200,000,000,000 = **212,200,000,000,000 FLOPs**. Parameter sensitivity gives 106.1–424.4 trillion FLOPs. Exact fixture: fail, because six blank lines are removed. Human estimate: 600 seconds to implement a passing function.

## 16x-clean-markdown-opus4

Run e742d7c7-3861-42cd-9e5a-06ec48688041, claude-opus-4-20250514. Compute: (687 + 398) × 360,000,000,000 = **390,600,000,000,000 FLOPs**. Half/double coefficient sensitivity gives 195.3–781.2 trillion FLOPs. Exact fixture: pass. Human estimate: 600 seconds to implement a passing function.

## Reproduction

Run `node PATH_TO_RECOMPUTE_JS SOURCES_DIRECTORY NEW_OUTPUT_DIRECTORY` with Node.js. It verifies the selected source hash, extracts the supplied fixture and the two inspected pure functions, removes only their TypeScript declaration syntax, and runs them in isolated contexts with a timeout. It writes the fixture, transformed output and arithmetic to the new output directory. It makes no network requests or model calls.

Other exports in this source collection need separate review. In particular, some o3 records have internally inconsistent normalized completion/reasoning fields; they must not be added by blindly summing those fields. They are not used here.
