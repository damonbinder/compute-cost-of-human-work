# Replaying published Epoch accounting

Source paths below are relative to the dataset root. The original native header/summaries remain under agent-work/sources/epoch/<point_id>/. Historical acquisition and correction artifacts are now retained unchanged under agent-work/sources/epoch/legacy-accounting/, with SHA256 and original collector locations in manifest.json. Some artifacts describe pre-correction intermediate values; the later retry audit supersedes the initial GLM5 recovery. They are evidence, not scripts to overwrite the current CSV.

## Native arithmetic replay

`check_legacy_accounting.py` is a Python-standard-library, read-only check of27 current rows in the initial SimpleQA, logged expansion, initial SWE and GLM/Kimi collections. It sums original native summary counters, applies the retained reviewed recovery/imputation totals, divides by original completed counts and multiplies by current shared coefficients. It checks agreement with current points.csv. It does not claim to repeat human research, tokenizer reconstruction or error classification.

Run the script by its absolute path; provide explicit paths:

```sh
python3 /path/to/dataset/research/epoch/check_legacy_accounting.py --sources /path/to/dataset/sources/epoch --points /path/to/dataset/points.csv --models /path/to/dataset/models.csv --output /path/to/new-result.json
```

Output must be new and outside the source directory. Inputs are never written. The script and its four neighboring study notes identify the bounded row set. No historical generator, network access or temporary dependency directory is used.

## Other retained evidence

- SWE original difficulty join/bin arithmetic: agent-work/sources/epoch/legacy-accounting/expansion-03/calculations.json; original500-row Parquet: agent-work/sources/epoch/swe-verified.parquet.
- Initial GLM retained-response recovery: agent-work/sources/epoch/legacy-accounting/expansion-04/usage-recovery.json. Current GLM5 GPQA full-run correction: agent-work/sources/epoch/legacy-accounting/native-audit-corrections/glm5-retry-calculations.json.
- Earlier missing-response decisions: agent-work/sources/epoch/legacy-accounting/native-audit-corrections/calculations.json. Original failure samples remain in their point directories.
- Haiku3.5 complete event-audit result: agent-work/sources/epoch/lang-epoch-simpleqa-haiku35/full-event-audit.json, with original full.eval archive. This is a retained audit result, not a claim that the new arithmetic checker repeats that full event audit.
- Original Anthropic tokenizer reconstruction: agent-work/sources/epoch/claude-legacy-input-counts.json and claude-input-strings.json, alongside the pinned tokenizer and original library code. These record the earlier GPQA/MATH count calculation; current OTIS uses the subsequent correction.
- Current OTIS reconstruction: recompute_otis_inputs.py and agent-work/sources/epoch/otis-input-correction/. Follow the explicit arguments in that calculator; its deltas preserve earlier and corrected values.

The obsolete collectors were not published as runnable production generators. Their source extraction/classification results remain inspectable, while current arithmetic can be checked without reverting accepted corrections.
