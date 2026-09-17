# Prior update plan — applying the ruled parameter priors

*Created 2026-09-13 13:24.*
*Last revised 2026-09-13 13:30.*

## Summary

The ruling moves 16 model IDs and flips the basis on two more. **The batch-only half is now
applied to the root files** (2026-09-13 13:30, on the coordinator's word); the shared-ID half
waits for the merge. The dry-run tables below are unchanged and remain the record of what each
row moves by.

- **18 rows in the claude-rows batch** carry a changed coefficient: 9 recompute mechanically,
  9 need their retained scripts. They currently sit 7 in `points.csv` and 11 in `excluded.csv`,
  and that split is still moving as the exclusions ruling is applied; the total of 18 is the
  stable number.
- **27 rows in the Codex dataset** carry a changed coefficient, all `params_tokens`, all
  mechanical.
- **Largest factors:** GPT-6 Astra and the OpenAI Navier–Stokes model at 3.0x (2.855x on the
  Factorio row, which mixes in an unchanged 8B helper), qwen-turbo at 0.4286x, Claude Haiku 4.5
  at 2.0x, Grok 3 and Grok 4 at 1.739x, and the three Flash records at 0.625x.
- **All five flags are ruled**, in the flags section below.

## Applied so far

On 2026-09-13 13:30, `tools/apply_priors.py --only-own-registry --apply` was run against the root
`models.csv` with `points.csv` and then `excluded.csv`.

**Four model records updated** in the root `models.csv`: `gpt-6-astra` and
`openai-ns-2026-09-internal` to 300000000000 active and 600000000000 FLOPs per token,
`anthropic-internal-research-flt-2026-08` to 150000000000 and 300000000000, and
`claude-haiku-4-5` to 40000000000 and 80000000000. All four keep
`flops_per_token_method = two_active_parameters` and `active_parameters_basis = estimated`, and
all four carry the new note stating basis and range.

**Three rows recomputed mechanically:**

| point_id | File | Old compute, FLOPs | New compute, FLOPs | Factor |
|---|---|---|---|---|
| reas-navier-stokes-openai | points.csv | 7.068518518518518e+22 | 2.1205555555555554e+23 | 3.000 |
| reas-flt-lean-anthropic-internal | points.csv | 6.252e+21 | 9.378e+21 | 1.500 |
| game-balrog-crafter-claudehaiku45 | excluded.csv | 17528584000000000 | 35057168000000000 | 2.000 |

Change logs: `research/model-priors/change-log-points.csv` and
`research/model-priors/change-log-excluded.csv`.

**Left untouched on instruction:** `game-portal-gpt6astra` at 1577559600000000000 and
`game-factorio-gpt6astra` at 1.9324229651584856e+19, both still on the old coefficient, awaiting
their constructors' script reruns and the coordinator's re-sync. **Deferred to the merge:** 13
rows on Codex-registry IDs, listed by name in each run's output. Nothing under `candidates/` and
nothing in `../AI Compute vs Human Time/` was written; the retained `calculations.json` files are
unchanged.

Both files validate. `collection-work/tools/validate.py` on a staged copy, with the registry
completed from the Codex records the rows reference and a merged `research/` and `agent-work/sources/` tree,
reports **0 errors on the 108 `points.csv` rows and 0 errors on the 122 `excluded.csv` rows**,
including the validator's own `flops_per_token == 2 x active_parameters` check on all four
changed records.

### A bug this apply exposed

The first `excluded.csv` invocation silently recomputed nothing. `apply_priors.py` had been
reading the old coefficient from the registry, which the `points.csv` invocation had already
moved, so every not-yet-moved row looked like a no-op basis flip. The tool now takes the old
coefficient from the priors table's own `current_active`, and cross-checks the registry against
both the old and the new value. The `excluded.csv` run was repeated after the fix and the
`points.csv` run re-verified as a no-op. Anyone running this tool over more than one points file
against one registry needs the fixed version.

## The accepted table

`research/model-priors/accepted-priors.csv`, 18 rows. Value changes first, then the two basis
flips. `registry` says where the model record lives; no ID appears in both registries.

| model_id | registry | Current active, parameters | New active, parameters | Factor | Low, parameters | High, parameters |
|---|---|---|---|---|---|---|
| gpt-6-astra | claude-rows | 1.0e11 | 3.0e11 | 3.000 | 1.0e11 | 6.0e11 |
| openai-ns-2026-09-internal | claude-rows | 1.0e11 | 3.0e11 | 3.000 | 1.0e11 | 8.0e11 |
| anthropic-internal-research-flt-2026-08 | claude-rows | 1.0e11 | 1.5e11 | 1.500 | 5.5e10 | 4.0e11 |
| claude-haiku-4-5 | claude-rows | 2.0e10 | 4.0e10 | 2.000 | 1.5e10 | 8.0e10 |
| gpt-5-6-sol | codex | 1.0e11 | 1.5e11 | 1.500 | 6.0e10 | 4.0e11 |
| claude-3-opus-20240229 | codex | 1.8e11 | 3.0e11 | 1.667 | 1.2e11 | 6.0e11 |
| claude-3-5-haiku-20241022 | codex | 2.0e10 | 3.0e10 | 1.500 | 1.2e10 | 6.0e10 |
| grok-3-beta | codex | 1.15e11 | 2.0e11 | 1.739 | 8.0e10 | 4.5e11 |
| grok-4 | codex | 1.15e11 | 2.0e11 | 1.739 | 8.0e10 | 4.5e11 |
| gemini-2.0-flash-001 | codex | 4.0e10 | 2.5e10 | 0.625 | 1.0e10 | 5.5e10 |
| gemini-2.5-flash | codex | 4.0e10 | 2.5e10 | 0.625 | 1.0e10 | 5.5e10 |
| gemini-2.5-flash-preview-05-20 | codex | 4.0e10 | 2.5e10 | 0.625 | 1.0e10 | 5.5e10 |
| gpt-3.5-turbo-1106 | codex | 7.0e9 | 1.2e10 | 1.714 | 6.0e9 | 2.5e10 |
| gpt-3.5-turbo-0125 | codex | 7.0e9 | 1.2e10 | 1.714 | 6.0e9 | 2.5e10 |
| gpt-3.5-turbo-instruct | codex | 7.0e9 | 1.2e10 | 1.714 | 6.0e9 | 2.5e10 |
| qwen-turbo-2024-11-01 | codex | 1.4e10 | 6.0e9 | 0.4286 | 2.0e9 | 1.8e10 |
| gemini-1.5-flash-8b-001 | codex | 8.0e9 | 8.0e9 | 1.000 | 7.0e9 | 9.0e9 |
| glm-5.2 | codex | 4.0e10 | 4.0e10 | 1.000 | 3.5e10 | 4.5e10 |

The last two are basis flips to `reported` with no change of value, so they move no row's
`compute_flops`. Held at current and therefore absent: GPT-4 Turbo, Grok 4.20, Gemini 3.5 Flash,
and the Gemini 3 Pro family. Unchanged at 100B and absent: Opus 5, GPT-5.

`new_flops_per_token` is twice `new_active` throughout, keeping the dataset's
`two_active_parameters` convention.

## Dry run: claude-rows batch

Snapshot 2026-09-13 13:22. The root files are being rewritten concurrently by the exclusions
pass, so a row can move between `points.csv` and `excluded.csv`; the model, method and factor do
not.

Every `params_tokens` row below passed the check that the recorded `compute_flops` equals
`tokens` times the old coefficient, to the last bit. No row failed.

| point_id | model_id | Method | Old compute, FLOPs | New compute, FLOPs | Factor |
|---|---|---|---|---|---|
| reas-navier-stokes-openai | openai-ns-2026-09-internal | mechanical | 7.0685e22 | 2.1206e23 | 3.000 |
| reas-flt-lean-anthropic-internal | anthropic-internal-research-flt-2026-08 | mechanical | 6.2520e21 | 9.3780e21 | 1.500 |
| game-chess-move-arena-grok4 | grok-4 | mechanical | 5.3537e15 | 9.3109e15 | 1.739 |
| game-balrog-crafter-grok4 | grok-4 | mechanical | 1.0658e17 | 1.8535e17 | 1.739 |
| work-rli-grok4 | grok-4 | mechanical | 6.6066e16 | 1.1490e17 | 1.739 |
| game-balrog-crafter-grok3 | grok-3-beta | mechanical | 6.7879e16 | 1.1805e17 | 1.739 |
| game-balrog-crafter-gemini25flash | gemini-2.5-flash | mechanical | 2.5319e16 | 1.5824e16 | 0.625 |
| game-balrog-crafter-claude35haiku | claude-3-5-haiku-20241022 | mechanical | 1.2924e16 | 1.9386e16 | 1.500 |
| game-balrog-crafter-claudehaiku45 | claude-haiku-4-5 | mechanical | 1.7529e16 | 3.5057e16 | 2.000 |
| game-portal-gpt6astra | gpt-6-astra | script | 1.5776e18 | 4.7327e18 | 3.000 |
| game-factorio-gpt6astra | gpt-6-astra | script | 1.9324e19 | 5.5170e19 | 2.855 |
| game-vgb-civ1-gemini20flash | gemini-2.0-flash-001 | script | 7.4344e18 | 4.6465e18 | 0.625 |
| game-vgb-nfs-gemini20flash | gemini-2.0-flash-001 | script | 5.8611e16 | 3.6632e16 | 0.625 |
| game-vgb-tim-gemini20flash | gemini-2.0-flash-001 | script | 1.3233e17 | 8.2704e16 | 0.625 |
| game-vgb-doom2-gemini20flash | gemini-2.0-flash-001 | script | 7.1653e15 | 4.4783e15 | 0.625 |
| game-vgb-crystal-gemini20flash | gemini-2.0-flash-001 | script | 2.5696e18 | 1.6060e18 | 0.625 |
| game-vgb-kirby-gemini20flash | gemini-2.0-flash-001 | script | 1.0589e17 | 6.6179e16 | 0.625 |
| game-vgb-zelda-gemini20flash | gemini-2.0-flash-001 | script | 1.1815e17 | 7.3842e16 | 0.625 |

The new values in the script column are not projections. Each script was run in the scratchpad at
the new prior and the numbers above are what it produced.

The same 18 rows appear in `candidates/`, one copy each, spread over balrog (5), videogamebench
(7), portal-astra (1), factorio-astra (1), flt-anthropic (1), navier-stokes-openai (1),
game-arena (1), and remote-labor-index (1). A `candidates/gaia/` batch appeared during this pass
carrying 3 more `claude-haiku-4-5` rows at 2.000x; it is not yet in the root and is not counted
in the 18.

### The three script recomputes

**VideoGameBench, 7 rows, exactly 0.625x.** `gemini-2.0-flash-001` carries
`encoder_parameters: null`, so `flops = 2 x active_parameters x positions` and the positions come
from cost inversion, which does not involve the prior. The token counts do not move. The
parameter lives in `research/videogamebench/inputs.json` under `models.gemini20flash.active_parameters`,
not in a `models.csv`, so the edit is to that file and then a rerun.

**Portal, 1 row, exactly 3.000x.** `compute_portal_astra.py` carries `FLOPS_PER_POSITION = 2e11`
and `ACTIVE_PARAMETERS = 100e9` as module constants; both need changing to `6e11` and `300e9`.
The script's own `active_parameters_300B` scenario already equals the new central, 4.7326788e18.

**Factorio, 1 row, 2.855x rather than 3.000x.** `ASTRA_ACTIVE_PARAMS = 100e9` becomes `300e9`;
`LUNA_ACTIVE_PARAMS` stays at `8e9`. The row's compute is a bundle of Astra positions and Luna
positions, and the Luna share is unchanged, so the total scales by less than 3. Luna's share of
the total drops from 7.27% to 2.55%. Two further consequences: the row's `tokens` field also
moves, from 120477333.00200199 to 120493162.62828633, because the geometric-mean solve
re-allocates the billed units, and the script reads Portal's `calculations.json`, so **Portal must
be rerun before Factorio**.

## Dry run: Codex dataset

27 rows, every one `params_tokens`, every one mechanical, no operation_count rows affected. All 27
passed the `tokens` times old-coefficient check exactly.

| point_id | model_id | Old compute, FLOPs | New compute, FLOPs | Factor |
|---|---|---|---|---|
| reas-epoch-gpqa-haiku35 | claude-3-5-haiku-20241022 | 2.2638e13 | 3.3958e13 | 1.500 |
| reas-epoch-mathl5-haiku35 | claude-3-5-haiku-20241022 | 2.2579e13 | 3.3869e13 | 1.500 |
| reas-epoch-otis-haiku35 | claude-3-5-haiku-20241022 | 3.0005e13 | 4.5008e13 | 1.500 |
| lang-epoch-simpleqa-haiku35 | claude-3-5-haiku-20241022 | 3.9584e12 | 5.9375e12 | 1.500 |
| reas-epoch-gpqa-opus3 | claude-3-opus-20240229 | 2.5275e14 | 4.2125e14 | 1.667 |
| reas-epoch-mathl5-opus3 | claude-3-opus-20240229 | 2.2694e14 | 3.7824e14 | 1.667 |
| reas-epoch-otis-opus3 | claude-3-opus-20240229 | 2.7740e14 | 4.6233e14 | 1.667 |
| cyber-lyptus-password-strings-opus3 | claude-3-opus-20240229 | 1.3932e14 | 2.3220e14 | 1.667 |
| cyber-lyptus-cal-latex-opus3 | claude-3-opus-20240229 | 7.7040e13 | 1.2840e14 | 1.667 |
| reas-epoch-gpqa-gpt35-0125 | gpt-3.5-turbo-0125 | 5.2984e12 | 9.0829e12 | 1.714 |
| reas-epoch-mathl5-gpt35-0125 | gpt-3.5-turbo-0125 | 6.1197e12 | 1.0491e13 | 1.714 |
| reas-epoch-gpqa-gpt35-1106 | gpt-3.5-turbo-1106 | 5.1490e12 | 8.8269e12 | 1.714 |
| reas-epoch-mathl5-gpt35-1106 | gpt-3.5-turbo-1106 | 6.4637e12 | 1.1081e13 | 1.714 |
| game-chess-move-gpt35 | gpt-3.5-turbo-instruct | 4.7445e12 | 8.1334e12 | 1.714 |
| reas-epoch-gpqa-gemini20flash | gemini-2.0-flash-001 | 6.9679e13 | 4.3550e13 | 0.625 |
| reas-epoch-mathl5-gemini20flash | gemini-2.0-flash-001 | 8.3822e13 | 5.2389e13 | 0.625 |
| reas-epoch-otis-gemini20flash | gemini-2.0-flash-001 | 1.4089e14 | 8.8053e13 | 0.625 |
| reas-strawberry-gemini25-flash | gemini-2.5-flash | 2.2232e12 | 1.3895e12 | 0.625 |
| admin-taxcalc2024-single-w2-flash | gemini-2.5-flash-preview-05-20 | 3.5903e14 | 2.2439e14 | 0.625 |
| admin-taxcalc2024-hoh-box12-flash | gemini-2.5-flash-preview-05-20 | 3.8928e14 | 2.4330e14 | 0.625 |
| reas-epoch-gpqa-grok3 | grok-3-beta | 6.4076e14 | 1.1144e15 | 1.739 |
| reas-epoch-mathl5-grok3 | grok-3-beta | 6.7811e14 | 1.1793e15 | 1.739 |
| reas-epoch-otis-grok3 | grok-3-beta | 1.3191e15 | 2.2941e15 | 1.739 |
| reas-epoch-gpqa-qwenturbo24 | qwen-turbo-2024-11-01 | 2.4932e13 | 1.0685e13 | 0.4286 |
| reas-epoch-mathl5-qwenturbo24 | qwen-turbo-2024-11-01 | 2.3893e13 | 1.0240e13 | 0.4286 |
| reas-epoch-otis-qwenturbo24 | qwen-turbo-2024-11-01 | 3.4709e13 | 1.4876e13 | 0.4286 |
| vending-bench-2-gpt56sol | gpt-5-6-sol | 1.3299e19 | 1.9948e19 | 1.500 |

Three Codex rows are touched by the basis flips without a compute change:
`reas-epoch-gpqa-gemini15flash8b`, `reas-epoch-otis-gemini15flash8b`, and
`agen-epoch-swebench-glm52max`.

## Counts per registry

| Registry | Model records changed | Rows with a changed coefficient | Mechanical | Script | Rows touched by basis flip only |
|---|---|---|---|---|---|
| claude-rows | 4 | 18 | 9 | 9 | 5 |
| codex | 14 | 27 | 27 | 0 | 3 |

The claude-rows basis-flip count is the five `glm-5.2` rows (one apex-agents, four
epoch-swebench-bins). The claude-rows model records are the four batch-only IDs: `gpt-6-astra`,
`openai-ns-2026-09-internal`, `anthropic-internal-research-flt-2026-08`, and `claude-haiku-4-5`.

The ruling splits the work by where the model record lives, not by which batch the row is in. Of
the claude-rows batch's 18 rows, **5 are on batch-only IDs and can move now** (Navier–Stokes, FLT,
Haiku 4.5, and the two Astra script rows); the other **13 are on Codex-registry IDs and move once
at merge**, alongside Codex's own 27. So the merge batch is 40 rows: 33 mechanical, 7 script.
`tools/apply_priors.py --only-own-registry` implements exactly this split and reports the deferred
rows by name.

## Commands

`tools/apply_priors.py` is a dry run by default and rewrites nothing without `--apply`. It is
idempotent: a second run over an applied pair finds the registry already at the ruled values, and
recognizes a row that already carries `tokens` times the new coefficient rather than reporting it
as a failed check. It refuses to write if any model record's current value matches neither the
table's `current_active` nor its `new_active`, or if any `params_tokens` row fails the
`tokens` times old-coefficient identity.

### Now, in this folder, batch-only IDs

Run each without `--apply` first and read the change log.

```
cd "AI Compute vs Human Time claude-rows"

python3 tools/apply_priors.py \
    --models models.csv \
    --points points.csv \
    --priors research/model-priors/accepted-priors.csv \
    --also-models "../AI Compute vs Human Time/dataset/models.csv" \
    --only-own-registry \
    --change-log research/model-priors/change-log-points.csv \
    --apply

python3 tools/apply_priors.py \
    --models models.csv \
    --points excluded.csv \
    --priors research/model-priors/accepted-priors.csv \
    --also-models "../AI Compute vs Human Time/dataset/models.csv" \
    --only-own-registry \
    --change-log research/model-priors/change-log-excluded.csv \
    --apply
```

The second invocation leaves the model records alone, because the first already moved them, and
recomputes only the points. Repeat the pair for each `candidates/<study>/` whose rows are on
batch-only IDs (portal-astra, factorio-astra, flt-anthropic, navier-stokes-openai, balrog for the
Haiku 4.5 row, and gaia), passing `--paths-base` at the folder root:

```
python3 tools/apply_priors.py \
    --models candidates/balrog/models.csv \
    --points candidates/balrog/points.csv \
    --priors research/model-priors/accepted-priors.csv \
    --also-models models.csv \
    --also-models "../AI Compute vs Human Time/dataset/models.csv" \
    --paths-base . \
    --only-own-registry \
    --change-log research/model-priors/change-log-cand-balrog.csv \
    --apply
```

Then the two Astra scripts, in this order, Portal first:

```
# edit FLOPS_PER_POSITION to 6e11 and ACTIVE_PARAMETERS to 300e9 first
python3 research/portal-astra/compute_portal_astra.py \
    --summary agent-work/sources/portal-astra/summary.json \
    --scan    agent-work/sources/portal-astra/session-scan.json \
    --out     agent-work/derived/portal-astra/calculations.json

# edit ASTRA_ACTIVE_PARAMS to 300e9 first; leave LUNA_ACTIVE_PARAMS at 8e9
python3 research/factorio-astra/compute_factorio_astra.py \
    --portal-summary      agent-work/sources/portal-astra/summary.json \
    --portal-calculations agent-work/derived/portal-astra/calculations.json \
    --prices              agent-work/sources/factorio-astra/openai-list-prices-2026-09-13.json \
    --hltb                agent-work/sources/factorio-astra/howlongtobeat-factorio-17455.json \
    --out                 agent-work/derived/factorio-astra/calculations.json

python3 research/factorio-astra/build_rows.py \
    --calculations    agent-work/derived/factorio-astra/calculations.json \
    --points-header   points.csv \
    --models-header   models.csv \
    --astra-model-row candidates/portal-astra/models.csv \
    --out-points      candidates/factorio-astra/points.csv \
    --out-models      candidates/factorio-astra/models.csv
```

`build_rows.py` regenerates the Factorio candidate row from `calculations.json`, so its
`compute_flops` and `tokens` both come out right without a hand edit. The Portal row has no
equivalent builder, so `game-portal-gpt6astra` takes a hand edit to 4.7326788e18 in `points.csv`
and in `candidates/portal-astra/points.csv`, then `tools/resync.py`.

### At merge, against the unified registry

After `incorporate.py` has built the unified `dataset/`, run the same tool once over the whole
thing with no `--only-own-registry`, so the shared IDs and the 13 deferred claude-rows rows move
together with Codex's 27:

```
cd "AI Compute vs Human Time"

python3 "../AI Compute vs Human Time claude-rows/tools/apply_priors.py" \
    --models dataset/models.csv \
    --points dataset/points.csv \
    --priors "../AI Compute vs Human Time claude-rows/research/model-priors/accepted-priors.csv" \
    --paths-base dataset \
    --change-log dataset/research/model-priors/change-log-merge-points.csv \
    --apply

# only once the merge has created dataset/excluded.csv; it does not exist yet
python3 "../AI Compute vs Human Time claude-rows/tools/apply_priors.py" \
    --models dataset/models.csv \
    --points dataset/excluded.csv \
    --priors "../AI Compute vs Human Time claude-rows/research/model-priors/accepted-priors.csv" \
    --paths-base dataset \
    --change-log dataset/research/model-priors/change-log-merge-excluded.csv \
    --apply
```

Then the VideoGameBench script, once, for the 7 gemini-2.0-flash rows:

```
# set models.gemini20flash.active_parameters to 25000000000 in inputs.json first
python3 research/videogamebench/compute_videogamebench.py \
    --inputs       research/videogamebench/inputs.json \
    --walkthroughs agent-work/sources/videogamebench/walkthrough-metadata.json \
    --out          agent-work/derived/videogamebench/calculations.json \
    --points-out   candidates/videogamebench/points.csv \
    --models-out   candidates/videogamebench/models.csv
```

Finally `validate.py` and `build_inspector.py` per the merge procedure in `README.md`.

## Research notes whose scenario ranges need re-centring

Each of these states its parameter sensitivity as a multiple of the old prior, so the multiplier
and often the band itself are wrong after the change. Line numbers are as of this snapshot.

| Note | Lines | Model | What it says now | What it becomes |
|---|---|---|---|---|
| research/portal-astra.md | 17, 30, 332, 333, 512, 517, 518 | gpt-6-astra | central at 100B, 30-300B sensitivity, table rows 0.30 and 3.00, 4.73e17-4.73e18 | central at 300B; the old 300B scenario is the new central; band 100-600B at 0.33 and 2.0 |
| research/factorio-astra.md | 45, 481, 482, 507, 674, 678 | gpt-6-astra | 30-300B sensitivity, table rows 0.35 and 2.85 | band 100-600B; the Luna share means the multipliers are not the Portal ones and must be re-derived from the rerun |
| research/navier-stokes-openai.md | 42, 43, 363, 367, 369, 417 | openai-ns-2026-09-internal | 100B prior, 30-300B, table rows 0.30 and 3.00 | central at 300B, band 100-800B |
| research/flt-anthropic.md | 139, 142, 279 | anthropic-internal-research-flt-2026-08 | 100B prior, 30B-300B, 30B gives 1.88e21 and 300B gives 1.88e22 | central at 150B, band 55-400B, endpoints recomputed off 9.378e21 |
| research/videogamebench.md | 24, 25, 436 | gemini-2.0-flash-001 | one joint "30-300B (four closed models), 0.30 / 3.00" row | only Gemini 2.0 Flash moves; the joint row has to split, since the other three closed models are held |
| research/balrog.md | 201, 411-413, 675, 745, 755, 765, 815 | five models | Haiku 4.5 at 20B with "40B would double the row to 3.5e16"; per-submission lines quote the old FLOPs-per-token | 3.5e16 is now the central; the quoted coefficients become 8e10, 6e10, 5e10, and 4e11 |
| research/remote-labor-index.md | 373, 374 | grok-4 | "115B for Grok 4, so a 30-300B sensitivity is 0.3x to 3x" | Grok 4 at 200B, band 80-450B at 0.4x to 2.25x |
| research/game-arena.md | 255, 276, 476 | grok-4 | "model record grok-4 reused unchanged (115B active, 2.3e11 FLOPs per token)" | 200B active, 4.0e11 FLOPs per token |
| research/apex-agents.md | 118, 225 | glm-5.2 | "six of nine active-parameter counts are substantial assumed inputs"; "a model estimated at 40B active" | five of nine; the GLM-5.2 count is reported, not estimated |
| research/epoch-swebench-bins.md | 30, 466, 544 | glm-5.2 | describes the GLM-5.2 rows' active count as estimated and feeding `compute_evidence` | the count is reported; see the flag below |

The `models.csv` note text for every changed record is in the `notes_text` column of
`accepted-priors.csv` and is written by `apply_priors.py`, so the model records do not need a
separate pass. Three pieces of existing note text were dropped for the 365-character limit: the
GPT-6 Astra release-date corroboration, which `model_release_date` already carries; the FLT
record's "Claude 4.7 tokenizer era"; and the GPT-3.5 Turbo Instruct 175B scenario, which the new
6-25B band excludes rather than supersedes. Restore any of them if they should survive.

## Flags, as ruled

The coordinator ruled four of these on 2026-09-13, answering the TL;DR's ordering rather than
this document's numbering. Flag 4, the scope of "Gemini 3 Pro", was not among them and is still
open; it changes nothing already applied.

**1. RULED: keep 100-600B for Astra in the table, with the pricing band in the note.** The
sensitivity ranges for Astra and the Navier–Stokes model were a judgment, not the ruling. The ruling gives "300B active (Damon's read; pricing band 250-333B)". Read literally
that band is what centres 300B, not a sensitivity range: a 250-333B band on a grade C prior
would be narrower than any other row in the table. The accepted table therefore carries
100-600B, the pricing cross-check's own stated range, and states the 250-333B band in the note
as the thing that centres the value. The Navier–Stokes model carries 100-800B, the report's high
end kept because it is described as more capable than Astra, and is unchanged.

**2. RULED: apply only the ruling's enumerated set plus the two basis flips.** The sub-1.5x
proposals are out, and kimi-k3 is out because the APEX batch already priced it. "Adopt the
recommended set" is wider than the ruling's enumeration. The proposals CSVs
contain proposed changes the ruling does not name and does not hold: claude-2.0 and claude-2.1 at
1.3x, gpt-4.5-preview at 1.33x, the three o1 records at 1.2x, qwen3.7-max at 0.9x, gpt-4.1-mini at
1.04x, exactness fixes for gpt-3-davinci-175b, gpt-oss-120b and gpt-oss-20b, and a first value for
the new kimi-k3 ID. Per the coordinator's brief this table carries only what the ruling lists, so
none of them are in it. If "adopt the recommended set" was meant to pull them in, they are a
second tranche and the table needs extending.

**3. RULED: leave `compute_evidence` unchanged on the eight basis-flip rows; the merge pass
decides.** The two basis flips may move `compute_evidence` on eight rows. `gemini-1.5-flash-8b-001`
and `glm-5.2` currently make their rows `derived_assumed_inputs`, and the column's definition
names model size as the example of a substantial assumed input. Once the count is `reported`, a
row with no other assumed input becomes `derived_supported_inputs`. That is three Codex rows and five
claude-rows rows, one apex-agents and four epoch-swebench-bins. `apply_priors.py` does not touch `compute_evidence` and did not. The eight rows for the merge
pass to decide, all currently `derived_assumed_inputs`:

| point_id | Where it is now | model_id |
|---|---|---|
| agen-epoch-swebench-glm52max-lt15m | claude-rows points.csv | glm-5.2 |
| agen-epoch-swebench-glm52max-15m1h | claude-rows points.csv | glm-5.2 |
| agen-epoch-swebench-glm52max-1h4h | claude-rows excluded.csv | glm-5.2 |
| agen-epoch-swebench-glm52max-gt4h | claude-rows excluded.csv | glm-5.2 |
| work-apex-agents-glm52 | candidates/apex-agents | glm-5.2 |
| agen-epoch-swebench-glm52max | codex points.csv | glm-5.2 |
| reas-epoch-gpqa-gemini15flash8b | codex points.csv | gemini-1.5-flash-8b-001 |
| reas-epoch-otis-gemini15flash8b | codex points.csv | gemini-1.5-flash-8b-001 |

The apex-agents row still carries an assumed cache split and probably stays at
`derived_assumed_inputs` whatever the others do.

**4. OPEN: is "Gemini 3 Pro at 100B" the base ID or the family?** Read here as the family. The proposals put
`gemini-3-pro`, `gemini-3.1-pro-preview`, `gemini-3.1-pro-preview-customtools`, and
`gemini-3-deep-think-preview` on one 130B peer transfer. The ruling holds "Gemini 3 Pro" at 100B,
which is taken here to hold all four, so none appears in the table. If only the base ID was
meant, the other three move by 1.3x and touch 17 rows across the two registries. Nothing applied
so far depends on the answer, since all four are held either way in this tranche.

**5. RULED: the Factorio `tokens` move is expected, and Portal runs before Factorio.** The
Factorio row's `tokens` field moves as well as its compute. Nothing else in either batch changes a
non-compute field, so it is easy to miss. `build_rows.py` handles it if the row is regenerated
rather than hand-edited.
