#!/usr/bin/env python3
"""Download, decrypt and reduce every HAL GAIA trace zip to a per-task usage summary.

For each ``gaia_*_UPLOAD.zip`` in the Hugging Face dataset agent-evals/hal_traces,
downloads the zip, decrypts it with HAL's published password (decrypt_hal_zip.py),
reduces it with extract_hal_usage.py, writes the compact summary into <out_dir>,
and deletes the zip and the decrypted JSON. Runs already summarised are skipped.

Dependencies: huggingface_hub, cryptography, ijson.

Usage:
    python3 fetch_hal_gaia.py <work_dir> <out_dir> [max_zip_mb]

<work_dir> holds the transient zip and decrypted JSON; <out_dir> receives
one ``<run_id>.json`` per run. max_zip_mb (default 1000) skips zips larger than
the cap, whose decrypted plaintext does not fit in memory on a 16 GB machine.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from decrypt_hal_zip import decrypt_zip  # noqa: E402
from extract_hal_usage import extract  # noqa: E402

REPO = "agent-evals/hal_traces"


def main(work_dir, out_dir, max_mb=1000):
    from huggingface_hub import HfApi, hf_hub_download

    work = Path(work_dir)
    out = Path(out_dir)
    work.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)

    api = HfApi()
    files = [
        f
        for f in api.list_repo_tree(REPO, repo_type="dataset", recursive=True, expand=True)
        if f.path.lower().startswith("gaia_") and f.path.endswith(".zip")
    ]
    files.sort(key=lambda f: f.size)
    manifest = []
    for f in files:
        stem = f.path[: -len("_UPLOAD.zip")]
        target = out / f"{stem}.json"
        rec = {"path": f.path, "size_bytes": f.size, "summary": str(target)}
        if target.exists():
            rec["status"] = "already_present"
            manifest.append(rec)
            continue
        if f.size > max_mb * 1e6:
            rec["status"] = "skipped_too_large"
            manifest.append(rec)
            print(f"SKIP {f.path} ({f.size/1e6:.0f} MB)", flush=True)
            continue
        print(f"GET  {f.path} ({f.size/1e6:.0f} MB)", flush=True)
        zip_path = hf_hub_download(REPO, f.path, repo_type="dataset", local_dir=str(work))
        plain = work / f"{stem}.plain.json"
        try:
            decrypt_zip(zip_path, plain)
            counts = extract(plain, target)
            rec["status"] = "ok"
            rec["call_counts"] = counts
            print(f"OK   {stem} {counts}", flush=True)
        except Exception as exc:  # noqa: BLE001
            rec["status"] = f"failed: {exc}"
            print(f"FAIL {stem}: {exc}", flush=True)
        finally:
            for p in (Path(zip_path), plain):
                if p.exists():
                    os.remove(p)
        manifest.append(rec)
    with open(out / "_fetch_manifest.json", "w") as fh:
        json.dump(manifest, fh, indent=1)
    print("done", len(manifest))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 1000)
