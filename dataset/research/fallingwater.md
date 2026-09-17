# Fallingwater architectural reconstruction

## media-fallingwater-astra

### Sources and recorded work

[Operator's article](https://www.aiformortals.co/blog/gpt-6-astra-blender-fallingwater), sections “How I ran it,” “Fallingwater: what it did on its own,” “Where Fallingwater falls short,” and “What the three cost.”

| Reported input | Value |
|---|---:|
| Fresh input tokens | 10,314,143 |
| Cache reads, additional to fresh input | 465,753,216 |
| Output tokens | 2,108,208 |
| Run duration | 29 h 11 m 3 s |
| API-equivalent cost | $674.31 |

The operator describes 27 rooms, 5,755 objects, ten camera views and a 106-second tour. Assets were reused. Water, later interiors, motion and frame rate remained deficient; 41 of 45 recorded defects were unresolved. These are reported observations, not this collector's visual judgments. The human target is this deliverable, not the requested perfect reconstruction.

[Video transcript, September 9, 2026](https://moderncreator.app/2026-09-09-pat-simmons-i-gave-gpt-6-astra-blender-access-the-results-are-insane), 06:25–14:27, corroborates the build sequence. The original video is linked there. The transcript is a secondary rendering of the operator's recording; the companion article remains the numerical source.

### Scope and autonomy

The row starts from the supplied research brief and reference pack. Preparatory reference gathering is outside both workloads. The source describes continuous unattended execution; the author eventually requested closure. This stopping instruction sets the budget, rather than supplying modeling decisions. The row does not claim that the original acceptance gates passed.

I assume the reported per-build totals cover its execution helpers, and price their tokens at the primary model's coefficient. The source does not disclose a helper-level ledger. If the counters omit child agents, the estimate is low; do not add an arbitrary helper multiplier merely because the ledger is unavailable. This is a material accounting qualification, not a measured completeness claim.

### Human time: 120 active hours

Baseline: an experienced architectural visualization artist using Blender or equivalent conventional tools, scripting, ordinary asset libraries and the same prepared drawings and photographs. No AI assistance, architectural design from scratch, archive research phase, survey, construction documentation or time learning Blender is included. Reuse of generic foliage, materials and furniture is allowed. The person need not recreate thousands of repeated scene objects separately.

This is a judgment estimate. No human timing sample feeds the number. I reviewed the published specification, task inventory, outcome description and defect account. Direct visual inspection of the deliverable was unavailable: browser policy blocked the delivered site's domain. I have not downloaded or opened the native model and do not assert personally verified scene quality.

| Work | Assumed active hours | Why this work remains necessary |
|---|---:|---|
| Interpret supplied plans and establish levels, scale and reference organization | 8 | Multiple levels and two linked buildings require consistent registration; finding the archive is already done. |
| Model architectural shell, openings, slabs, terraces and connections | 20 | Repeated wall/window components reduce effort, but the building is not one box or one representative floor. This allowance does not include furniture or material development. |
| Fit interior furniture, built-ins and fixtures | 40 | This is the largest term because separate rooms require different arrangements. An illustrative workload is ten more developed spaces at about three hours and seventeen sparse/service spaces at about 35 minutes. That split is an estimating scenario, not a measured inventory of finished room quality. |
| Establish and apply reusable stone, concrete, wood, glass and fabric materials | 16 | Shared materials cover many objects; this includes mapping and practical correction rather than bespoke painting of every surface. |
| Terrain, rocks, vegetation and basic water | 12 | Use conventional asset libraries and scattering. The target allows the reported poor water treatment; no polished fluid simulation is required. |
| Light the scene, set cameras and assemble the tour | 16 | Includes active test-render inspection and adjustments across interior/exterior settings, not unattended render duration. No additional professional color grade or cinematic route is assumed. |
| Pack assets, save views and check delivery | 8 | Basic reopen/navigation and missing-resource checks, not repairing every documented defect. |
| **Total** | **120** | **432,000 seconds** |

These components make the assumptions reviewable; they are not timings disguised as observations. The 40-hour interior term and the degree of reference-specific shell reconstruction are the largest human-side judgments. The bounds move that interior term across its own illustrative inventory of twenty-seven spaces. Treating every space at the sparse 35-minute rate takes the term from 40 to 15.75 hours, and generic assets take the shell from 20 to 12: **88 hours**. Treating every space at the developed three-hour rate takes the term to 81 hours: **161 hours**. Neither is a confidence interval or included in the FLOP range.

Two researched comparisons help define what this estimate is *not*:

- [ArchAdemia's Fallingwater AutoCAD course](https://archademia.com/lessons/autocad-architecture-3d-course/) contains a 43:25 lesson modeling the ground floor from supplied plans, within a short course. Its description covers walls, slabs, stairs, openings and balustrades. Lesson duration is edited teaching time, not end-to-end measured production time, and its output does not include all interiors, terrain, materials and a tour. It supports treating shell construction as only part of the job; it is not multiplied into the estimate.
- [Dave Mennenoh's Escher's Waterfall](https://blenderartists.org/t/eschers-waterfall/1508110) reports about 300 hours for a different, carefully composed architectural artwork. Its bespoke illusion, layout and artistic target differ. It illustrates why “one building” is not a reliable universal time unit; those hours are not transferred here.

`human_time_evidence=llm_estimate_judgment`; attempts and subset are `not_applicable`. `performance_vs_human=match` follows from targeting the delivered quality by construction, not claiming parity with an observed professional trial. No concrete difference is identified between the stipulated AI and human input/tool allowances, so `comparison_issues=none_identified`.

### Compute

Use the existing `gpt-6-astra` record, not a separate model for effort level. Its shared assumptions are 300B active parameters, 75 full-attention layers and query width 14,720. The architecture is undisclosed; these are the dataset's current assumptions, not facts established by this source.

The native fresh workload is 10,314,143 input + 2,108,208 output = 12,422,351 billing units. Cache reads are additional, not a subset of the smaller fresh-input number. Reasoning is not added separately to native output.

#### Text and image accounting

Follow the existing Portal convention and [OpenAI's vision-token rules](https://developers.openai.com/api/docs/guides/images-vision): Astra uses 32×32 patches and a 1.2 billing multiplier. Image billing units are not text tokens or physical backbone positions.

The article does not publish image-send events. I estimate their scale from the job: one execution-stage reading of each of 15 supplied drawing sheets and 49 photographs, two review views for each of 27 rooms, ten final camera views, and 45 intermediate defect/check captures. That is **173 image sends assumed**, not an observed count. The reference file count is reported, but whether every file was sent individually, the number of room reviews, and one capture per defect entry are assumptions. The captured work is large enough to justify more than one input and one final screenshot; this avoids an arbitrary percentage of total tokens.

Assume representative 1280×720 model inputs, consistent with the documented Portal screenshot scale, not established Fallingwater image dimensions. This gives 40×23=920 patches and ceil(920×1.2)=1,104 billed units per image. High-resolution crops or repeated sends can change this; scenarios below quantify the effect. It does not assert that the full-resolution architectural TIFFs were submitted unchanged.

- Estimated visual billing: 173×1,104 = 190,992 units.
- CSV text tokens: 12,422,351−190,992 = **12,231,359**.
- Visual backbone positions: 173×920 = **159,160**.
- Total backbone positions P = **12,390,519**.

No distinct vision-encoder term is added, following Portal's current approximation. A 2B-parameter frontend applied to all assumed patches would add 6.3664e14 FLOPs, under 0.005% of the total; this is a sensitivity calculation, not an identified architecture. Conventional non-neural Blender rendering remains outside the model FLOPs.

#### Backbone and attention

Q = min(200,000, P / 2, 465,753,216 / P × 2,800) = **105,250.55526729753**.

F = P × (2 × 300e9 + 4 × 75 × 14,720 × Q) = **1.3193256765196802e19 FLOPs**.

The attention/weights ratio is **0.7746440867673099**. The method is `operation_count`, because the backbone workload includes the separately counted image positions, while the CSV tokens field contains text only. `compute_evidence=derived_assumed_inputs` covers the image workload and the shared architecture assumptions. Cache-read mixture itself has no published visual split and is retained as the native proxy in the context recipe.

| Image-load scenario | FLOPs | Interpretation |
|---|---:|---|
| 173 sends at 1280×720 | 1.3193256765196802e19 | Central assumed workload |
| 346 sends at 1280×720 | 1.3174157565196802e19 | Double views, rereads or retries |
| 173 sends at 1920×1080 | 1.3170005565196800e19 | Larger screenshots |
| 173 sends at 3840×2160 | 1.3042954365196800e19 | Full 4K frames with original/auto processing |
| No image correction | 1.3212355965196802e19 | Previous all-billing-units-as-positions approximation |

These are alternatives, not confidence bounds. The correction changes the central by about 0.15%; the displayed 4K alternative is about 1.1% below the corrected central. Different image-send assumptions affect the semantic text count more than the overall FLOP estimate, because the billing-to-patch adjustment is only the multiplier difference.

The source reports an API-equivalent price, not a subscription invoice. Use `ai_cost_basis=list_price`, $674.31, and 2026-09-09, the public demonstration's date, as the price-date proxy; the exact rate-sheet date is not stated. No human payment is reported.

### Range

Apply the current two-uncertainty recipe, not an arbitrary percentage. For the low endpoint use active parameters 100B and new tokens per call 1,976; for the high use 600B and 19,088. Recompute attention shape using the OpenAI family rule:

D = round((N / 196608)^(1/3)); L = round(0.65 * D); W = 128 * D.

This gives low L=52, W=10,240 and high L=94, W=18,560. Recompute Q with the endpoint's call constant and the same cap, then recompute F. Bounds: **4.4383295694896947e18 to 3.2162218854528e19 FLOPs**. This range does not cover helper completeness, undisclosed architecture changes, visual quality or human duration. Native inputs and assumptions are retained in `research/fallingwater-inputs.json`; derived outputs and scenarios are retained outside the product in `agent-work/derived/fallingwater-20260915/fallingwater-results.json`. Reproduce with Python 3 standard library: `python3 fallingwater-compute.py --input fallingwater-inputs.json --output NEW-results.json`. The script accepts explicit paths and writes only the requested new output; it is independent of the candidate-folder layout.
