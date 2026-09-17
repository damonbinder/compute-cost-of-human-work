#!/usr/bin/env python3
"""Rebuild the retained ALE-Bench / AHC058 extracts in agent-work/sources/ale-bench/.

Reads only public endpoints plus a local copy of the Hugging Face dataset
`SakanaAI/ALE-Bench` (download it with `hf download SakanaAI/ALE-Bench
--repo-type dataset --local-dir <dir>`), and writes fresh extract files into the
output directory given on the command line. It never modifies its inputs.

Usage:
    python3 fetch_sources.py --hf-dir <ale-bench-hf-dir> --out <output-dir>

Dependencies: Python 3.10+ standard library only (urllib, zipfile, csv, json).
Network access to sakanaai.github.io, sakana.ai and atcoder.jp is required.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import html
import io
import json
import re
import statistics
import tarfile
import urllib.request
import zipfile
from pathlib import Path

LEADERBOARD = "https://sakanaai.github.io/ALE-Bench-Leaderboard"
SUMMARY_URL = f"{LEADERBOARD}/data/results_summary.json"
SAKANA_AHC058 = "https://sakana.ai/ahc058/"
AHC058_RESULTS = "https://atcoder.jp/contests/ahc058/results/json"
AHC058_SUBMISSIONS = "https://sakanaai.github.io/fishylene-ahc058/data/submissions.json"
# Pinned to the commit that carries every configuration the 2026-09-08 leaderboard shows;
# tag v1.6.1 predates twenty of them, including gpt-6-astra-max and claude-opus-5-high.
REPO_COMMIT = "3da9b12fb5d112dabb3af693d1a42031c95142bc"
REPO_TARBALL = f"https://codeload.github.com/SakanaAI/ALE-Bench/tar.gz/{REPO_COMMIT}"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}


def get(url: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read()


def page_text(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="replace")
    text = re.sub(r"<script.*?</script>", "", text, flags=re.S)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.S)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = html.unescape(text)
    return "\n".join(line.strip() for line in text.split("\n") if line.strip())


def window_hours(row: dict) -> float:
    start = datetime.datetime.fromisoformat(row["start_at"])
    end = datetime.datetime.fromisoformat(row["end_at"])
    return (end - start).total_seconds() / 3600.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hf-dir", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)
    hf: Path = args.hf_dir

    # --- ALE-Bench problem schedule and per-problem human performance ---------
    schedule = {r["problem_id"]: r for r in csv.DictReader((hf / "schedule.csv").open(newline=""))}
    problem_ids = (hf / "problem_ids.txt").read_text().split()
    lite_ids = set((hf / "problem_ids_lite.txt").read_text().split())

    human_rows = []
    for pid in problem_ids:
        with zipfile.ZipFile(hf / f"{pid}.zip") as zf:
            name = next(n for n in zf.namelist() if n.endswith("performance.csv"))
            with zf.open(name) as fh:
                perf = [
                    float(r["performance"])
                    for r in csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8"))
                ]
        hours = window_hours(schedule[pid])
        human_rows.append(
            {
                "problem_id": pid,
                "format": "short" if hours < 24 else "long",
                "lite": int(pid in lite_ids),
                "start_at": schedule[pid]["start_at"],
                "end_at": schedule[pid]["end_at"],
                "window_hours": round(hours, 4),
                "n_participants": len(perf),
                "mean_performance": round(statistics.mean(perf), 4),
                "median_performance": round(statistics.median(perf), 4),
                "min_performance": min(perf),
                "max_performance": max(perf),
            }
        )
    write_csv(out / "alebench-human-performance-per-problem.csv", human_rows)

    # --- global AtCoder heuristic ranking pool --------------------------------
    pool = list(csv.DictReader((hf / "ranking.csv").open(newline="")))
    min5 = [r for r in pool if int(r["competitions"]) >= 5]
    ratings = [float(r["rating"]) for r in min5]
    avg_perfs = [float(r["avg_perf"]) for r in min5]

    def top_pct(values: list[float], v: float) -> float:
        return round(100 * sum(1 for x in values if x >= v) / len(values), 2)

    # Paper figures the pool has to reproduce, as (value, percentile the paper prints).
    paper_rating_ranks = {1456: 43.2, 936: 80.1, 1135: 67.4, 1031: 74.6, 1636: 30.5, 2104: 11.8}
    paper_perf_ranks = {1217: 51.5, 1520: 22.3, 1352: 36.8, 1220: 51.1, 1879: 6.8, 618: 96.9}
    summary = {
        "n_users_all": len(pool),
        "n_users_min5": len(min5),
        "mean_rating_min5": round(statistics.mean(ratings), 4),
        "mean_avg_perf_min5": round(statistics.mean(avg_perfs), 4),
        "paper_rating_rank_check": {
            str(v): {"paper": p, "recomputed": top_pct(ratings, v)} for v, p in paper_rating_ranks.items()
        },
        "paper_avg_perf_rank_check": {
            str(v): {"paper": p, "recomputed": top_pct(avg_perfs, v)} for v, p in paper_perf_ranks.items()
        },
    }
    (out / "alebench-ranking-pool-summary.json").write_text(json.dumps(summary, indent=1) + "\n")

    # --- leaderboard: per-problem records at self-refine 1 --------------------
    results = json.loads(get(SUMMARY_URL))
    fmt = {r["problem_id"]: r["format"] for r in human_rows}
    per_problem, aggregates = [], []
    for model in results:
        for block in model["overall_results"]:
            aggregates.append(
                {
                    "model_name": model["model_name"],
                    "num_self_refine": block["num_self_refine"],
                    **{
                        f"{metric}_{sub}": block[metric][sub][stat]
                        for metric in ("performance", "rank", "input_tokens", "output_tokens", "cost")
                        for sub in ("short",)
                        for stat in ("mean",)
                    },
                    "performance_short_stdev": block["performance"]["short"]["stdev"],
                    "performance_all_mean": block["performance"]["all"]["mean"],
                    "performance_long_mean": block["performance"]["long"]["mean"],
                    "total_tokens_short_mean": block["total_tokens"]["short"]["mean"],
                }
            )
            if block["num_self_refine"] != 1:
                continue
            for rec in block["results"]:
                if fmt[rec["problem_id"]] != "short":
                    continue
                per_problem.append(
                    {
                        "model_name": model["model_name"],
                        "problem_id": rec["problem_id"],
                        "code_language": rec["code_language"],
                        "judge_result": rec["overall_judge_result"],
                        "rank": rec["rank"],
                        "performance": rec["performance"],
                        "input_tokens": rec["input_tokens"],
                        "output_tokens": rec["output_tokens"],
                        "total_tokens": rec["total_tokens"],
                        "cost": rec["cost"],
                    }
                )
    write_csv(out / "alebench-leaderboard-selfrefine1-short.csv", per_problem)
    write_csv(out / "alebench-leaderboard-aggregates.csv", aggregates)

    # --- model configurations from the ALE-Bench repository -------------------
    configs = []
    with tarfile.open(fileobj=io.BytesIO(get(REPO_TARBALL)), mode="r:gz") as tf:
        for member in tf.getmembers():
            if not member.name.endswith(".json") or "/llm_configs/" not in member.name:
                continue
            body = json.loads(tf.extractfile(member).read().decode("utf-8"))
            configs.append(
                {
                    "config": Path(member.name).stem,
                    "model_name": body["model_name"],
                    "provider": body["provider"],
                    "settings": json.dumps(body.get("settings", {}), sort_keys=True),
                }
            )
    configs.sort(key=lambda c: c["config"])
    write_csv(out / "alebench-llm-configs.csv", configs)

    # --- AHC058 -------------------------------------------------------------
    (out / "ahc058-sakana-report.txt").write_text(page_text(get(SAKANA_AHC058)) + "\n")
    (out / "ahc058-ale-agent-submissions.json").write_text(
        get(AHC058_SUBMISSIONS).decode("utf-8") + "\n"
    )
    official = json.loads(get(AHC058_RESULTS))
    write_csv(
        out / "ahc058-atcoder-results.csv",
        [
            {
                "place": e["Place"],
                "user": e["UserScreenName"],
                "is_rated": int(e["IsRated"]),
                "performance": e["Performance"],
                "old_rating": e["OldRating"],
                "new_rating": e["NewRating"],
                "affiliation": e["Affiliation"] or "",
            }
            for e in official
        ],
    )


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
