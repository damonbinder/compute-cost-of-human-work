# Pixels to Polygons: Blender cabin production

Ten observations from Ralf Boltshauser's 10 July 2026 experiment. This is one task with repeated model/effort configurations, not ten independent task designs.

## Sources and retained evidence

- [Original study](https://blender-bench.ralfboltshauser.com/).
- [Frozen repository](https://github.com/ralfboltshauser/gpt-5-6-blender-benchmark/tree/b56cfa88c469cce6f7e62191d16c2e4f89527edc).
- [Raw counters](https://github.com/ralfboltshauser/gpt-5-6-blender-benchmark/blob/b56cfa88c469cce6f7e62191d16c2e4f89527edc/site/assets/data/benchmark.csv), retained outside the product in agent-work/sources/blender-bench-20260915/benchmark.csv.
- [Per-run author audits](https://github.com/ralfboltshauser/gpt-5-6-blender-benchmark/blob/b56cfa88c469cce6f7e62191d16c2e4f89527edc/site/app.js), retained outside the product as audit.js, read as text and never executed.
- All fifteen original builder scripts retained as text under agent-work/sources/blender-bench-20260915/builders/. The same source folder retains audit.js and tree.json. No scripts were executed.

The input is a single 1672×941 reference image and a one-line instruction to build it in Blender. Each row covers the initial autonomous run including its debugging and intermediate renders. The source says all fifteen files reopen and renders are nonblank. It reports one primary user turn per configuration; it does not report human corrective turns. Its score assesses geometry, composition, finish and reference similarity; it is not a human performance score.

## Human target and estimates

The comparator is an experienced Blender artist who can write procedural scene scripts, using normal Blender and Python tools without generative AI, prebuilt scene assets or the AI's builder. They produce a comparably detailed editable scene, a functioning builder and a render. They need not reproduce an erroneous mesh intersection precisely. They are not asked to recover the exact original 3D scene or produce photorealistic architectural work. Source failure/omission descriptions determine the target quality. The script's existence is part of the requested deliverable, not incidental code to ignore.

I read source-specific geometry/finish audits for all fifteen scenes and inspected the builder structure, including the detailed Sol Ultra and GPT-5.5 helpers and the concise Sol low implementation. Hundreds of scene objects are mostly repeated roof pieces, logs, grass and trees; they are not hundreds of separately hand-crafted assets. The richer scenes add terrain variation, custom gables, props, multiple lighting layers and renderer adjustment. The estimates allow construction using duplication/procedural loops and reuse of normal modelling knowledge. They include debugging and artifact testing, but exclude unattended render time.

The estimates use the original author's output-specific audits and the builder code. The renders were not independently viewed.

### External timing checks

[Yeho Studios, 18 August 2025](https://blenderartists.org/t/create-a-cabin-in-forest-landscape-blender-tutorial/1606982) reports about 80 minutes for making a cabin forest scene before video compression. This establishes that an experienced creator can make a cabin scene in hours rather than days. It does not establish the timing of these outputs or their procedural builder deliverable; its asset assumptions were not established, so I do not scale its timing into the row estimates.

[Polygon Runway's forest-cabin modelling demonstration](https://www.youtube.com/watch?v=K5xVvC-uciE) and the corresponding [course listing](https://www.classcentral.com/course/youtube-forest-cabin-in-blender-2-83-3d-low-poly-modeling-process-175782) were found as additional context. The listed 45-minute video is not a verified unedited active-time measurement, and contributes no numerical rate.

The estimates therefore remain **llm_estimate_judgment**. Stage allocations below make the choices inspectable; they are not measured subtasks. The coarsest acceptable scene takes 1.5 hours; richer scenes take 3–4.5 hours; the most developed scene takes 6 hours including procedural implementation and revision. The bounds are built on each row's own stage allocation rather than as a factor on its total. Write S for a row's scene-content stages—cabin, surroundings and props, and materials, lighting and camera—and O for the rest, the layout and geometry helpers and the testing, corrections and export. The low charges S at the pace of Polygon Runway's 45-minute forest-cabin modelling demonstration against the simplest row's 60 scene minutes, 0.75S+O. The high charges a second reference-matching pass over the scene stages, 2S+O; neither external timing includes one, because both build a scene freehand rather than to a supplied reference image. O is carried unchanged at both ends, because nothing external times the procedural builder. These bounds are separate from compute uncertainty bars. Replacing these judgments with observed artist replications would materially improve this collection.

## Compute

For native input I, cached-input subset C, and output O, native fresh units are I−C+O. Visual billing units must be separated before counting text and image positions. Reasoning tokens are already inside O and are not added. The source reports marginal child-agent usage inside the two Ultra totals. Their helper identities and component counters are not published; the primary model's coefficient is assumed for them. All four main models resolve to existing registry entries; no new model priors were invented.

Use the current dataset recipe F=2NP+4LDQP, with the model registry's active parameters N and attention shape L,D. Since no per-call records were found in the frozen repository tree, Q=min(C/P×2800, P/2, 200000). Tool-call count is not an API-call count and is not substituted for one. The source mentions local chat histories/telemetry, but these are not in the public tree. Low/high recompute both model size/shape and cache-implied context using 1976/19088, following COLUMNS.md. The source gives no independent vision encoder operation count; this term remains unpriced, as in the existing Portal treatment. Non-neural Blender rendering is outside AI-model compute.

Compute ranges cover the two prescribed parameter/context uncertainties only. They do not quantify helper-model identity, vision processing, reliability across new attempts, or human time.

## Dollars

Non-Ultra rows price the native uncached/cache-read/output components at the registry's launch-date standard API rates, dated 10 July 2026: GPT-5.5 and Sol $5/$0.50/$30, Terra $2.50/$0.25/$15, Luna $1/$0.10/$6 per million. These are list-price equivalents, not a subscription invoice. Unreported cache writes and possible long-context premiums cannot be reconstructed; these standard-rate figures are lower bounds under the project's existing cost ruling. The July 10 date is the publication/price date because exact run dates are not exposed. Price sources are in research/cost/list-prices.csv. Ultra dollar entries are unavailable because unsegmented helper usage cannot be assigned exact provider/model rates. No human payment was reported.

## Inclusion decisions

Five configurations are withheld where the author's audit identifies failed main roof geometry or an obscured main subject. Match-by-construction does not turn a catastrophic modelling failure into a successful task by asking humans to reproduce the failure. Luna low is retained as a recognisable but simple cabin deliverable, and Terra Ultra as a complete scene with a flawed ground offset. These inclusions distinguish a flawed but usable scene from failure of its main subject. The retained rows use match because their human target explicitly reproduces the delivered quality, not because the author measured human performance.

## Reproduction

`research/blender-bench-calculate.py` uses Python 3 standard library. Download the raw counters from the frozen source linked above, then supply their path with `--source`, the model registry with `--models`, the point headers with `--points-schema`, and a new `--output-dir`. The script writes derived CSVs, calculations and image-frequency scenarios into that output directory; it does not edit the input dataset. The source inputs and per-point arithmetic are also recorded below.

# Pixels to Polygons calculations

| point_id | processed decoder positions | cache reads | context | FLOPs | human hours | list-price USD |
|---|---:|---:|---:|---:|---:|---:|
| media-blender-cabin-gpt-5-5-xhigh | 206331 | 1398400 | 18976.9 | 8.33228e+16 | 4.5 | 2.61967 |
| media-blender-cabin-gpt-5-6-luna-low | 80984 | 148480 | 5133.7 | 1.45496e+15 | 1.5 | 0.11926 |
| media-blender-cabin-gpt-5-6-luna-high | 118518 | 574464 | 13571.8 | 2.5123e+15 | 3 | 0.2447614 |
| media-blender-cabin-gpt-5-6-luna-xhigh | 195990 | 1824768 | 26069.4 | 5.0926e+15 | 3.5 | 0.5024978 |
| media-blender-cabin-gpt-5-6-terra-high | 138375 | 625408 | 12655.0 | 6.84132e+15 | 2.5 | 0.6691645 |
| media-blender-cabin-gpt-5-6-terra-xhigh | 111682 | 1974272 | 49497.3 | 8.59105e+15 | 4 | 1.054013 |
| media-blender-cabin-gpt-5-6-terra-ultra | 225767 | 1385984 | 17189.2 | 1.19257e+16 | 4 |  |
| media-blender-cabin-gpt-5-6-sol-low | 51739 | 612864 | 25869.5 | 1.9201e+16 | 3 | 0.766447 |
| media-blender-cabin-gpt-5-6-sol-xhigh | 171224 | 2557952 | 41829.8 | 7.10558e+16 | 4.5 | 2.977131 |
| media-blender-cabin-gpt-5-6-sol-ultra | 516380 | 8944896 | 48502.5 | 2.23763e+17 | 6 |  |

## media-blender-cabin-gpt-5-5-xhigh

Source run `gpt-5.5-xhigh`; reported input 1569908, cache reads 1398400, output 35431, reasoning subset 3958; native total 1605339. AI elapsed time 1293.57 seconds is not human time.

Work: Detailed log cabin, shingles, masonry chimney and porch; sparse surroundings and oversized cabin.

Human estimate: 270 minutes (4.5 hours): layout and geometry helpers 45; cabin 75; surroundings and props 60; materials, lighting and camera 45; testing, corrections and export 45. These are judgment allocations, not observed stage timings. 

Native uncached input plus output = 206939; assumed image billable units 3648, image patch positions 3040. Text tokens = 206939 - 3648 = 203291; processed workload P = 203291 + 3040 = 206331; context = min(1398400/206331 * 2800, 206331/2, 200000) = 18976.9. Registry N=1.73e+11, L=62, width=12288; F=8.33228e+16, range [3.3507e+16, 2.79946e+17].


## media-blender-cabin-gpt-5-6-luna-low

Source run `gpt-5.6-luna-light`; reported input 225304, cache reads 148480, output 4598, reasoning subset 293; native total 229902. AI elapsed time 126.626 seconds is not human time.

Work: Simple boxy cabin and sparse primitive trees; no visible chimney in the author’s render audit and an inaccurate roof silhouette.

Human estimate: 90 minutes (1.5 hours): layout and geometry helpers 15; cabin 25; surroundings and props 20; materials, lighting and camera 15; testing, corrections and export 15. These are judgment allocations, not observed stage timings. 

Native uncached input plus output = 81422; assumed image billable units 2628, image patch positions 2190. Text tokens = 81422 - 2628 = 78794; processed workload P = 78794 + 2190 = 80984; context = min(148480/80984 * 2800, 80984/2, 200000) = 5133.66. Registry N=8e+09, L=22, width=4352; F=1.45496e+15, range [5.45992e+14, 5.35362e+15].


## media-blender-cabin-gpt-5-6-luna-high

Source run `gpt-5.6-luna-high`; reported input 679741, cache reads 574464, output 13673, reasoning subset 2377; native total 693414. AI elapsed time 357.218 seconds is not human time.

Work: Compact coherent cabin, shingles, rocks, mountains and water; limited path and scene coverage.

Human estimate: 180 minutes (3 hours): layout and geometry helpers 30; cabin 45; surroundings and props 45; materials, lighting and camera 35; testing, corrections and export 25. These are judgment allocations, not observed stage timings. 

Native uncached input plus output = 118950; assumed image billable units 2592, image patch positions 2160. Text tokens = 118950 - 2592 = 116358; processed workload P = 116358 + 2160 = 118518; context = min(574464/118518 * 2800, 118518/2, 200000) = 13571.8. Registry N=8e+09, L=22, width=4352; F=2.5123e+15, range [9.43585e+14, 9.97996e+15].


## media-blender-cabin-gpt-5-6-luna-xhigh

Source run `gpt-5.6-luna-extra-high`; reported input 1996535, cache reads 1824768, output 24709, reasoning subset 6331; native total 2021244. AI elapsed time 666.506 seconds is not human time.

Work: Complete prop set and forest on simple terrain; oversized roof and underexposed narrow composition.

Human estimate: 210 minutes (3.5 hours): layout and geometry helpers 30; cabin 55; surroundings and props 65; materials, lighting and camera 35; testing, corrections and export 25. These are judgment allocations, not observed stage timings. 

Native uncached input plus output = 196476; assumed image billable units 2916, image patch positions 2430. Text tokens = 196476 - 2916 = 193560; processed workload P = 193560 + 2430 = 195990; context = min(1824768/195990 * 2800, 195990/2, 200000) = 26069.4. Registry N=8e+09, L=22, width=4352; F=5.0926e+15, range [1.9144e+15, 2.2167e+16].


## media-blender-cabin-gpt-5-6-terra-high

Source run `gpt-5.6-terra-high`; reported input 750997, cache reads 625408, output 13256, reasoning subset 1991; native total 764253. AI elapsed time 489.633 seconds is not human time.

Work: Compact cabin, custom faceted ground, path and props; sparse background and tree occlusion.

Human estimate: 150 minutes (2.5 hours): layout and geometry helpers 25; cabin 40; surroundings and props 35; materials, lighting and camera 25; testing, corrections and export 25. These are judgment allocations, not observed stage timings. 

Native uncached input plus output = 138845; assumed image billable units 2816, image patch positions 2346. Text tokens = 138845 - 2816 = 136029; processed workload P = 136029 + 2346 = 138375; context = min(625408/138375 * 2800, 138375/2, 200000) = 12655. Registry N=2e+10, L=31, width=6016; F=6.84132e+15, range [2.68728e+15, 3.10555e+16].


## media-blender-cabin-gpt-5-6-terra-xhigh

Source run `gpt-5.6-terra-extra-high`; reported input 2064218, cache reads 1974272, output 22372, reasoning subset 5938; native total 2086590. AI elapsed time 1345.5 seconds is not human time.

Work: Rich terrain, forest and props; crossed braces and a protruding beam remain.

Human estimate: 240 minutes (4 hours): layout and geometry helpers 35; cabin 60; surroundings and props 80; materials, lighting and camera 40; testing, corrections and export 25. These are judgment allocations, not observed stage timings. 

Native uncached input plus output = 112318; assumed image billable units 3816, image patch positions 3180. Text tokens = 112318 - 3816 = 108502; processed workload P = 108502 + 3180 = 111682; context = min(1974272/111682 * 2800, 111682/2, 200000) = 49497.3. Registry N=2e+10, L=31, width=6016; F=8.59105e+15, range [3.28096e+15, 2.2815e+16].


## media-blender-cabin-gpt-5-6-terra-ultra

Source run `gpt-5.6-terra-ultra`; reported input 1576987, cache reads 1385984, output 35642, reasoning subset 12903; native total 1612629. AI elapsed time 1401.26 seconds is not human time.

Work: Clean cabin shell and roof, height-field terrain and vegetation; cabin base visibly floats.

Human estimate: 240 minutes (4 hours): layout and geometry helpers 35; cabin 65; surroundings and props 65; materials, lighting and camera 45; testing, corrections and export 30. These are judgment allocations, not observed stage timings. 

Native uncached input plus output = 226645; assumed image billable units 5268, image patch positions 4390. Text tokens = 226645 - 5268 = 221377; processed workload P = 221377 + 4390 = 225767; context = min(1385984/225767 * 2800, 225767/2, 200000) = 17189.2. Registry N=2e+10, L=31, width=6016; F=1.19257e+16, range [4.66113e+15, 6.5559e+16].


## media-blender-cabin-gpt-5-6-sol-low

Source run `gpt-5.6-sol-light`; reported input 657071, cache reads 612864, output 7966, reasoning subset 1007; native total 665037. AI elapsed time 312.099 seconds is not human time.

Work: Coherent cabin, porch, chimney, path and props with simple lighting and coarse materials.

Human estimate: 180 minutes (3 hours): layout and geometry helpers 25; cabin 50; surroundings and props 50; materials, lighting and camera 30; testing, corrections and export 25. These are judgment allocations, not observed stage timings. 

Native uncached input plus output = 52173; assumed image billable units 2600, image patch positions 2166. Text tokens = 52173 - 2600 = 49573; processed workload P = 49573 + 2166 = 51739; context = min(612864/51739 * 2800, 51739/2, 200000) = 25869.5. Registry N=1.5e+11, L=59, width=11648; F=1.9201e+16, range [8.03656e+15, 4.86149e+16].


## media-blender-cabin-gpt-5-6-sol-xhigh

Source run `gpt-5.6-sol-extra-high`; reported input 2696097, cache reads 2557952, output 33581, reasoning subset 10244; native total 2729678. AI elapsed time 971.295 seconds is not human time.

Work: Coherent steep roof, custom terrain, mountains, path and nearly complete props; repeated trees and shallow atmosphere.

Human estimate: 270 minutes (4.5 hours): layout and geometry helpers 40; cabin 70; surroundings and props 75; materials, lighting and camera 50; testing, corrections and export 35. These are judgment allocations, not observed stage timings. 

Native uncached input plus output = 171726; assumed image billable units 3012, image patch positions 2510. Text tokens = 171726 - 3012 = 168714; processed workload P = 168714 + 2510 = 171224; context = min(2557952/171224 * 2800, 171224/2, 200000) = 41829.8. Registry N=1.5e+11, L=59, width=11648; F=7.10558e+16, range [2.8176e+16, 2.16093e+17].


## media-blender-cabin-gpt-5-6-sol-ultra

Source run `gpt-5.6-sol-ultra`; reported input 9381999, cache reads 8944896, output 83945, reasoning subset 31441; native total 9465944. AI elapsed time 3151.86 seconds is not human time.

Work: Coherent detailed cabin, shingles, chimney, terrain, water, layered mountains, varied vegetation and placed props; refined lighting and haze.

Human estimate: 360 minutes (6 hours): layout and geometry helpers 50; cabin 90; surroundings and props 100; materials, lighting and camera 75; testing, corrections and export 45. These are judgment allocations, not observed stage timings. 

Native uncached input plus output = 521048; assumed image billable units 28008, image patch positions 23340. Text tokens = 521048 - 28008 = 493040; processed workload P = 493040 + 23340 = 516380; context = min(8944896/516380 * 2800, 516380/2, 200000) = 48502.5. Registry N=1.5e+11, L=59, width=11648; F=2.23763e+17, range [8.8644e+16, 9.70484e+17].


Image sensitivity outputs are retained outside the product in agent-work/derived/blender-bench-20260915/image-scenarios.json. Central FLOPs decrease 0.2–1.0% relative to counting every native fresh billing unit as a decoder position. This small arithmetic effect does not make the assumed image counts observed.
