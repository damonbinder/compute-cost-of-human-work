#!/usr/bin/env python3
"""Join Epoch AI SWE-bench Verified per-sample token counters to OpenAI's per-instance
difficulty bins, one row per (model run, instance).

Dependencies: Python 3.9+ standard library, plus pandas and pyarrow to read the
SWE-bench Verified Parquet.  No network access.

Usage (all paths explicit, output is written fresh and never inside an input tree):

  python3 extract_perinstance.py \
      --epoch-sources  /path/to/dataset/sources/epoch /path/to/extra-run-members \
      --difficulty     /path/to/swebench-verified-test.parquet \
      --allowances     /path/to/dataset/sources/epoch/native-final-accounting/expansion-14/usage-reconstruction.json \
      --hub            /path/to/epoch/benchmark_data/swe_bench_verified.csv \
      --points         /path/to/dataset/points.csv \
      --out-perinstance /path/to/out/epoch-swebench-perinstance.csv \
      --out-run-links   /path/to/out/epoch-swebench-run-links.csv \
      --out-hashes      /path/to/out/source-hashes.json

--hub is Epoch's published SWE-bench Verified index (swe_bench_verified.csv inside
https://epoch.ai/data/benchmark_data.zip).  Each retained run is matched to its hub row on
(model version, mean_score, stderr), which supplies the public .eval log URL; the Inspect
`run_id` inside the log header is a different identifier and is not the log's file name.
--points supplies the model_id for runs that already have a dataset row; --model-map
supplies it for runs that do not (a CSV with `run` and `model_id` columns).  More than one
--epoch-sources directory may be given: the twenty-five runs whose log members the earlier
Epoch collection already retained, plus directories written by fetch_log_members.py for runs
it did not cover.

--allowances is optional.  It supplies the per-instance missing-work allowances that the
Epoch collection in the read-only Codex dataset added to five of the twenty-five runs
(response-header read failures and other ambiguous network sends, each allowed half a
comparable recorded call).  Runs absent from that file get a zero allowance, which is what
their own research notes record.

Counter conventions.  Inspect's `model_usage` block does not use one convention across
endpoints.  For every run and every sample the script asserts the run's declared identity
for `total_tokens`, so a wrong rule fails loudly rather than silently mis-counting:

  endpoint family            source total          counted workload
  google/*                   I + O + R             I - CR + O + R
  openai/*, zhipu/*,         I + O                 I - CR + O
    moonshot/*
  epoch/gemini-3.5-flash     I + CR + O + R        I + O + R
  anthropic/*, other epoch/* I + CR + CW + O       I + CW + O

I = input_tokens, O = output_tokens, R = reasoning_tokens, CR = input_tokens_cache_read,
CW = input_tokens_cache_write.  Cache reads are excluded from the counted workload in
every case; reasoning is added only where it is reported additionally to output.
"""

import argparse
import csv
import hashlib
import json
import os
import sys

# (cache reads are inside input_tokens, reasoning is reported additionally to output)
ENDPOINT_RULES = {
    "google/": (True, True),
    "openai/": (True, False),
    "zhipu/": (True, False),
    "moonshot/": (True, False),
    "anthropic/": (False, False),
    "epoch/gemini-3.5-flash": (False, True),
    "epoch/": (False, False),
}

BIN_ORDER = ["<15 min fix", "15 min - 1 hour", "1-4 hours", ">4 hours"]


def rule_for(endpoint):
    if endpoint in ENDPOINT_RULES:
        return ENDPOINT_RULES[endpoint]
    for prefix in ("google/", "openai/", "zhipu/", "moonshot/", "anthropic/", "epoch/"):
        if endpoint.startswith(prefix):
            return ENDPOINT_RULES[prefix]
    raise SystemExit("no counter rule for endpoint %r" % endpoint)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def counters(usage):
    return (
        usage.get("input_tokens", 0),
        usage.get("output_tokens", 0),
        usage.get("total_tokens", 0),
        usage.get("input_tokens_cache_read", 0),
        usage.get("input_tokens_cache_write", 0),
        usage.get("reasoning_tokens", 0),
    )


def counted(usage, cr_in_input, reasoning_extra):
    i, o, tot, cr, cw, r = counters(usage)
    expected = i + o + (0 if cr_in_input else cr + cw) + (r if reasoning_extra else 0)
    return (i - (cr if cr_in_input else 0) + cw + o + (r if reasoning_extra else 0),
            expected, tot)


def load_difficulty(path):
    import pandas as pd
    frame = pd.read_parquet(path, columns=["instance_id", "difficulty"])
    return dict(zip(frame["instance_id"], frame["difficulty"]))


def load_allowances(path):
    """Per-(run, instance) missing-work allowance in counted tokens."""
    if not path:
        return {}
    with open(path) as fh:
        blob = json.load(fh)
    out = {}
    for run_id, record in blob.items():
        for correction in record.get("corrections", []):
            key = (run_id, correction["id"])
            out[key] = out.get(key, 0.0) + float(correction.get("central_extra_tokens", 0.0))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--epoch-sources", required=True, nargs="+",
                    help="directories holding agen-epoch-swebench-*/ with header.json and summaries.json")
    ap.add_argument("--difficulty", required=True,
                    help="SWE-bench Verified test Parquet with the difficulty column")
    ap.add_argument("--allowances", default=None,
                    help="usage-reconstruction.json with per-instance missing-work allowances")
    ap.add_argument("--hub", required=True,
                    help="Epoch benchmark index swe_bench_verified.csv")
    ap.add_argument("--points", required=True,
                    help="dataset points.csv, for the model_id runs with an existing row use")
    ap.add_argument("--model-map", default=None,
                    help="CSV with run,model_id for runs that have no existing dataset row")
    ap.add_argument("--out-perinstance", required=True)
    ap.add_argument("--out-run-links", required=True)
    ap.add_argument("--out-hashes", required=True)
    args = ap.parse_args(argv)

    for out in (args.out_perinstance, args.out_run_links, args.out_hashes):
        for src in args.epoch_sources:
            if os.path.abspath(out).startswith(os.path.abspath(src) + os.sep):
                raise SystemExit("refusing to write inside a source tree: %s" % out)
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)

    difficulty = load_difficulty(args.difficulty)
    allowances = load_allowances(args.allowances)

    run_dirs = {}
    for src in args.epoch_sources:
        for d in sorted(os.listdir(src)):
            if not d.startswith("agen-epoch-swebench-"):
                continue
            if d in run_dirs:
                raise SystemExit("run %s appears in two source directories" % d)
            run_dirs[d] = os.path.join(src, d)
    runs = sorted(run_dirs)
    if not runs:
        raise SystemExit("no agen-epoch-swebench-* directories under %s" % args.epoch_sources)

    with open(args.hub) as fh:
        hub = list(csv.DictReader(fh))
    with open(args.points) as fh:
        model_ids = {r["point_id"]: r["model_id"] for r in csv.DictReader(fh)}
    existing_rows = set(model_ids)
    if args.model_map:
        with open(args.model_map) as fh:
            for r in csv.DictReader(fh):
                model_ids.setdefault(r["run"], r["model_id"])

    hashes = {"difficulty_parquet": {"path": args.difficulty, "sha256": sha256(args.difficulty)},
              "epoch_hub_index": {"path": args.hub, "sha256": sha256(args.hub)},
              "runs": {}}
    if args.allowances:
        hashes["allowances"] = {"path": args.allowances, "sha256": sha256(args.allowances)}

    rows = []
    run_links = []
    for run in runs:
        base = run_dirs[run]
        hdr_path = os.path.join(base, "header.json")
        sum_path = os.path.join(base, "summaries.json")
        with open(hdr_path) as fh:
            header = json.load(fh)
        with open(sum_path) as fh:
            summaries = json.load(fh)
        endpoint = header["eval"]["model"]
        cr_in_input, reasoning_extra = rule_for(endpoint)
        hashes["runs"][run] = {
            "endpoint": endpoint,
            "run_id": header["eval"].get("run_id"),
            "created": header["eval"].get("created"),
            "cache_reads_inside_input": cr_in_input,
            "reasoning_additional_to_output": reasoning_extra,
            "header_json_sha256": sha256(hdr_path),
            "summaries_json_sha256": sha256(sum_path),
            "summaries": len(summaries),
        }

        metrics = header["results"]["scores"][0]["metrics"]
        accuracy = float(metrics["accuracy"]["value"])
        stderr = float(metrics["stderr"]["value"])
        short = endpoint.split("/", 1)[1]
        hub_rows = [h for h in hub
                    if abs(float(h["stderr"]) - stderr) < 1e-12
                    and abs(float(h["mean_score"]) - accuracy) < 5e-4
                    and (h["Model version"] == short or h["Model version"].startswith(short + "_"))]
        if len(hub_rows) != 1:
            raise SystemExit("%s: %d hub rows match %s" % (run, len(hub_rows), short))
        hub_row = hub_rows[0]
        version = hub_row["Model version"]
        # The log's own plan config is authoritative for reasoning effort; the hub's model
        # version suffix is a cross-check and must agree where it carries one.
        effort = header.get("plan", {}).get("config", {}).get("reasoning_effort") or "provider default"
        suffix = version.rsplit("_", 1)[-1] if "_" in version else ""
        if suffix in ("minimal", "low", "medium", "high", "xhigh", "max") and suffix != effort:
            raise SystemExit("%s: hub suffix %r disagrees with log reasoning_effort %r"
                             % (run, suffix, effort))
        task_name = header["eval"].get("task")
        harness = {
            "swe_bench_verified": "a bash shell and editor agent",
            "swe_bench_claude_code": "the Claude Code CLI agent",
            "swe_bench_codex": "the Codex CLI agent",
        }.get(task_name)
        if harness is None:
            raise SystemExit("%s: unknown task harness %r" % (run, task_name))
        if run not in model_ids:
            raise SystemExit("%s: no model_id in --points or --model-map" % run)
        run_links.append({
            "run": run,
            "model_id": model_ids[run],
            "inspect_task": task_name,
            "harness": harness,
            "has_existing_dataset_row": int(run in existing_rows),
            "endpoint": endpoint,
            "hub_model_version": version,
            "reasoning_effort": effort,
            "log_id": hub_row["id"],
            "log_url": hub_row["Logs"],
            "header_task_id": header["eval"].get("task_id"),
            "agent": header["eval"].get("task_args", {}).get("agent"),
            "token_limit": header["eval"].get("task_args", {}).get("token_limit"),
            "inspect_ai": header["eval"].get("packages", {}).get("inspect_ai"),
            "hub_mean_score": hub_row["mean_score"],
            "hub_stderr": hub_row["stderr"],
            "hub_started_at": hub_row["Started at"],
            "header_created": header["eval"].get("created"),
            "inspect_run_id": header["eval"].get("run_id"),
            "cache_reads_inside_input": int(cr_in_input),
            "reasoning_additional_to_output": int(reasoning_extra),
            "cache_counters_reported": 0,
        })

        for sample in summaries:
            usage = sample.get("model_usage", {})
            extra = sorted(k for k in usage if k != endpoint)
            if extra:
                raise SystemExit("%s sample %s records non-primary usage %s"
                                 % (run, sample["id"], extra))
            tokens, expected, reported_total = counted(usage.get(endpoint, {}),
                                                       cr_in_input, reasoning_extra)
            if expected != reported_total:
                raise SystemExit("%s sample %s fails its counter identity: %d vs %d"
                                 % (run, sample["id"], expected, reported_total))
            score = sample.get("scores", {}).get("swe_bench_scorer", {}).get("value")
            i, o, tot, cr, cw, r = counters(usage.get(endpoint, {}))
            inst = sample["id"]
            if inst not in difficulty:
                raise SystemExit("%s: instance %s is not in the difficulty source" % (run, inst))
            rows.append({
                "run": run,
                "endpoint": endpoint,
                "instance_id": inst,
                "epoch": sample.get("epoch"),
                "difficulty": difficulty[inst],
                "input_tokens": i,
                "output_tokens": o,
                "cache_read_tokens": cr,
                "cache_write_tokens": cw,
                "reasoning_tokens": r,
                "total_tokens": tot,
                "counted_tokens": tokens,
                "allowance_tokens": allowances.get((run, inst), 0.0),
                "scored": 1 if score in ("C", "I") else 0,
                "resolved": 1 if score == "C" else 0,
                "working_time_s": sample.get("working_time"),
                "total_time_s": sample.get("total_time"),
                "message_count": sample.get("message_count"),
            })
            if cr or cw:
                run_links[-1]["cache_counters_reported"] = 1

    # Every allowance belonging to a run we processed must have landed on a real record.
    # The allowance file also covers other Epoch benchmarks; those keys are ignored here.
    seen = {(r["run"], r["instance_id"]) for r in rows}
    missing = [k for k in allowances if k[0] in set(runs) and k not in seen]
    if missing:
        raise SystemExit("allowances reference unknown records: %s" % missing[:5])

    fields = list(rows[0].keys())
    with open(args.out_perinstance, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with open(args.out_run_links, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(run_links[0].keys()))
        writer.writeheader()
        writer.writerows(run_links)
    with open(args.out_hashes, "w") as fh:
        json.dump(hashes, fh, indent=1, sort_keys=True)
        fh.write("\n")

    print("runs=%d rows=%d -> %s" % (len(runs), len(rows), args.out_perinstance))
    return 0


if __name__ == "__main__":
    sys.exit(main())
