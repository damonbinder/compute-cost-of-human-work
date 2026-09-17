# ARC-AGI-1: Opus 4.6 low and Opus 4.8 max

The work is one public evaluation task's first test grid, with two independent AI answers or up to two human submissions. These settings differ from previously collected configurations. All quantities below are freshly computed from original records; old row estimates are not inputs.

## Original observations and joins

Source: [ARC Prize's v1 release, pinned 3e9c9d1](https://huggingface.co/datasets/arcprize/arc_agi_v1_public_eval/tree/3e9c9d1a8402aff82356815c106cecaea65cb7d9). All 792 top-level original files for the two configurations are retained and matched to the source Git blob hashes: 399/391 task files plus one results file each. Hidden progress files are also retained. Their 400 completed status labels do not prove that 400 complete response pairs exist: both use zero `attempts_completed` even for records with native answers, and some completed tasks have no task file. Use the actual response records.

The [H-ARC original study](https://www.nature.com/articles/s41597-025-05687-1) and [OSF release](https://osf.io/bh8yq/) supply raw human actions, summaries and task grids. The calculator takes that original shared source directory explicitly and verifies all three hashes; it does not duplicate the 475 MB action CSV. It checks every AI prompt's demonstrations and actual test grid against these task definitions. Array and metadata indices agree in these configurations; no repair was necessary. All available AI correctness labels agree with rescoring the actual supplied output grid.

Human sessions are timed from the initial reset to the first or second submitted grid, whichever is the final available submission within that limit. Raw submit-event grids determine correctness, rather than later summary-grid state. This preserves the original summary-state/label discrepancies in the audit. Ten sessions have no timestamps and cannot enter the common timed distribution; all 4,091 timed sessions are eligible, including unsuccessful sessions and participants who did not finish the larger study. No arbitrary pause subtraction or upper-time trimming is applied.

The human interface requests a first explanation whose start is not separately timestamped; that inseparable interval remains. A final explanation after submission is excluded. Humans use a colored grid editor and receive correctness feedback, whereas the AI reads text grids and produces two independent guesses. Hence `different_task; different_inputs_or_tools; different_assessment`. The ARC-AGI-2 report's >5-second view rule belongs to its separate human dataset; it is not imposed on H-ARC, whose original notebook uses five-second gaps only for a different thinking-time proxy.

For each included task, let n be its count of eligible human sessions. Weight AI tokens and AI correctness by n and average over the same sessions used for human duration and correctness. This keeps the task distribution common to both axes. It does not manufacture additional AI runs. Only tasks with both recoverable first-test responses are included; other native responses and omitted tasks remain itemized in the audit.

| Setting | Complete tasks | Human sessions | Mean human seconds | Human correct within two submissions | AI correct within two responses | Mean tokens | Estimated FLOPs |
|---|---:|---:|---:|---:|---:|---:|---:|
| Opus 4.6 low | 398 | 4,071 | 350.5883 | 60.9433% | 89.3884% | 22,503.6148 | 4.50072e15 |
| Opus 4.8 max | 383 | 3,945 | 345.5143 | 61.6477% | 97.8707% | 61,039.5939 | 1.22079e16 |

Both comparisons support `above`, without treating the cohort-filtered accuracy as a published leaderboard score.

## Workload accounting

Each response's native total equals input plus completion. The separate reasoning field is zero, but the original Anthropic adapter explicitly sets that field to zero because a separate breakdown is not provided; it does not establish absence of reasoning. Native completion already supplies the counted output work. Do not retokenize visible text or add a speculative thinking budget. Opus 4.6 uses low effort with a 120K budget; Opus 4.8 uses adaptive thinking at max effort. Neither budget is a measured token total.

The complete metadata scan finds no cache fields, nonempty helper/turn fields or recorded error fields. The original Anthropic adapter maps provider input/output counts and omits cache components; the retained configuration has no explicit cache-control setting. The central approximation counts the released input/output fields once and does not assume an unreported cached fraction. It could miss unexported cache creation or overstate fresh work if a source total included reads. The audit retains output-only and fully cached second-identical-prompt sensitivities. It does not claim the native release proves a cache-free execution path.

The retained Opus 4.6 responses total 9,819,951 tokens across all test inputs; 37,545 belong to a first-test singleton and 202,171 to later test inputs outside this point. Missing first-test coverage is `477d2879` (one response) and `da515329` (no file). Opus 4.8 retains 25,644,557 tokens overall; 993,727 belong to eight first-test singletons and 587,064 to other test inputs. Nine more tasks have no file. These are not zero-cost failures folded into the selected mean. The point describes the complete retained-pair subset; omission may alter its difficulty mix.

Multiply each included pair's counted tokens by the shared assumed 200 billion FLOPs/token and then apply the common human-session weights. The 100B active parameter prior is not disclosed model size; `derived_assumed_inputs` records this limitation. `arc-modern-models.md` explains identity and sensitivity. The point is a benchmark aggregate, so `ai_attempts=not_applicable`; `human_attempts` remains the actual contributing human-session count.

## Reproduction

`recompute-v1.py` uses the reviewed ARC1 source-parser implementation but recomputes all values from the newly retained records. It is standard-library Python and never executes generated responses. Give explicit paths for `--sources`, `--human-sources`, `--selection`, `--models`, and a new `--output`. For this submission the selection is `selection-v1-first.json`. Use the retained `models-first-input.csv` for the exact coefficient input and byte-identical replay; the growing production models.csv has a different file hash. The source manifest and shared-human manifest are verified before calculation. Output is rejected if it exists or is under either evidence directory.

The shared human source directory is currently `collection-work/batches/arc-v1/sources`, or `dataset/sources/arc-v1` after publication; choose the actual location with the CLI. The retained result is `calculations-v1-first.json`. Further ARC settings are collected separately and do not change this submission's rows.
