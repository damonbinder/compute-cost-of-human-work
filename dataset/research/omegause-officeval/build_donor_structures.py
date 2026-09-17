#!/usr/bin/env python3
"""Aggregate the donor cache structures used by the OmegaUse-OfficeVal cost inversion.

Two donor families, both agentic tool-use runs of the same model endpoints:

  1. Epoch AI's SWE-bench Verified per-instance logs (measured cache reads and
     measured agent working time).
  2. Artificial Analysis's long-horizon agent benchmarks (gross prompt tokens and
     AA's own `cacheableInput` eligibility figure; no runtime).

Writes one CSV row per donor configuration with the two transferred parameters:

  h   = served cache reads / gross prompt positions
  rho = output tokens / freshly processed input positions (input + cache writes)

Usage:
  python3 build_donor_structures.py \
      --epoch  <path>/epoch-swebench-perinstance.csv \
      --aa     <path>/artificialanalysis-per-task-tokens.csv \
      --out    <path>/donor-structures.csv

Dependencies: Python 3.8+ standard library only.
"""
import argparse, csv, collections

# Epoch run id -> (model_id, label)
EPOCH_RUNS = {
    "agen-epoch-swebench-glm52max":    ("glm-5.2", "epoch-swebench-verified"),
    "agen-epoch-swebench-kimik26":     ("kimi-k2.6", "epoch-swebench-verified"),
    "agen-epoch-swebench-dsv4promax":  ("deepseek-v4-pro-preview", "epoch-swebench-verified"),
    "agen-epoch-swebench-qwen37max":   ("qwen3.7-max", "epoch-swebench-verified"),
    "agen-epoch-swebench-qwen36plus":  ("qwen3.6-plus", "epoch-swebench-verified"),
}
# Artificial Analysis model slug -> model_id
AA_SLUGS = {
    "glm-5-2": "glm-5.2",
    "deepseek-v4-pro": "deepseek-v4-pro-0813",
    "minimax-m3": "minimax-m3",
}
# Achieved share of the AA-eligible prefix that is actually served from cache.
# 1.0 = complete reuse; 0.60 is the floor established in
# agent-work/sources/apex-agents/harness-and-provider-caching.md from Lumer et al. 2026.
AA_SERVED_SHARES = (1.0, 0.6)


def epoch_rows(path):
    agg = collections.defaultdict(collections.Counter)
    n = collections.Counter()
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            run = r["run"]
            if run not in EPOCH_RUNS:
                continue
            n[run] += 1
            for k in ("input_tokens", "output_tokens", "cache_read_tokens",
                      "cache_write_tokens", "working_time_s"):
                agg[run][k] += float(r[k] or 0)
    out = []
    for run, v in agg.items():
        model_id, label = EPOCH_RUNS[run]
        fresh = v["input_tokens"] + v["cache_write_tokens"]   # positions processed anew
        served = v["cache_read_tokens"]
        outp = v["output_tokens"]
        gross = fresh + served
        billed = fresh + outp                                  # dataset's counted positions
        out.append(dict(
            model_id=model_id, donor=label, donor_detail=run,
            served_share_of_eligible="measured", n_units=n[run],
            fresh_input=round(fresh), output=round(outp), served_cache=round(served),
            gross_prompt=round(gross), billed_tokens=round(billed),
            h=served / gross if gross else 0.0,
            rho=outp / fresh if fresh else 0.0,
            billed_per_unit=billed / n[run],
            working_time_s_per_unit=v["working_time_s"] / n[run],
            billed_per_working_second=billed / v["working_time_s"] if v["working_time_s"] else "",
        ))
    return out


def aa_rows(path):
    out = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            slug = r["model_slug"]
            if slug not in AA_SLUGS or not r["cacheable_input_total"]:
                continue
            tasks = float(r["tasks"])
            gross = float(r["input_tokens_total"])
            eligible = float(r["cacheable_input_total"])
            outp = float(r["answer_tokens_total"]) + float(r["reasoning_tokens_total"])
            for s in AA_SERVED_SHARES:
                served = s * eligible
                fresh = gross - served
                billed = fresh + outp
                out.append(dict(
                    model_id=AA_SLUGS[slug], donor="artificial-analysis",
                    donor_detail=r["benchmark"], served_share_of_eligible=s,
                    n_units=int(tasks),
                    fresh_input=round(fresh), output=round(outp),
                    served_cache=round(served), gross_prompt=round(gross),
                    billed_tokens=round(billed),
                    h=served / gross, rho=outp / fresh,
                    billed_per_unit=billed / tasks,
                    working_time_s_per_unit="", billed_per_working_second="",
                ))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epoch", required=True)
    ap.add_argument("--aa", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = epoch_rows(a.epoch) + aa_rows(a.aa)
    rows.sort(key=lambda r: (r["model_id"], r["donor"], str(r["donor_detail"]),
                             str(r["served_share_of_eligible"])))
    cols = ["model_id", "donor", "donor_detail", "served_share_of_eligible", "n_units",
            "fresh_input", "output", "served_cache", "gross_prompt", "billed_tokens",
            "h", "rho", "billed_per_unit", "working_time_s_per_unit",
            "billed_per_working_second"]
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            for k in ("h", "rho"):
                r[k] = round(r[k], 6)
            for k in ("billed_per_unit", "working_time_s_per_unit", "billed_per_working_second"):
                if r[k] != "":
                    r[k] = round(float(r[k]), 3)
            w.writerow(r)
    print("wrote", a.out, len(rows), "donor configurations")


if __name__ == "__main__":
    main()
