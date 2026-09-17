#!/usr/bin/env python3
"""Establish which OmegaUse-OfficeVal artefact carries the Chinese original.

The Hugging Face repository ships the benchmark twice: the Chinese source in
`tasks/` and `rubrics/`, and an English translation in `task-en/`, `rubrics-en/`
and the merged `tasks_and_rubrics_en.json`.  The default Data Studio parquet --
the file retained here -- is the English merge, so a claim that the tasks are
Chinese has to be sourced from `tasks/`, not from the parquet.  This script
counts CJK characters in both and in the input-file names, which are identical
across the two directories.

Usage:
  python3 language_check.py \
      --parquet <path>/omegause-officeval-tasks.parquet \
      --zh      <path>/omegause-instructions-zh.json \
      --out     <path>/language-check.csv

Dependencies: Python 3.8+ standard library, plus pyarrow for the parquet.
"""
import argparse, csv, json, re

CJK = re.compile(r"[㐀-䶿一-鿿豈-﫿]")


def main():
    ap = argparse.ArgumentParser()
    for f in ("parquet", "zh", "out"):
        ap.add_argument("--" + f, required=True)
    a = ap.parse_args()
    import pyarrow.parquet as pq
    df = pq.read_table(a.parquet).to_pandas()
    zh = json.load(open(a.zh, encoding="utf-8"))
    rows, tot = [], dict(en=0, zh=0, files=0, files_cjk=0)
    for _, r in df.iterrows():
        i = r["id"]
        en = len(CJK.findall(r["instruction"]))
        z = len(CJK.findall(zh[i]["instruction"]))
        names = [f["dest"] for f in r["origin_files"]]
        ncjk = sum(1 for n in names if CJK.search(n))
        tot["en"] += en; tot["zh"] += z
        tot["files"] += len(names); tot["files_cjk"] += ncjk
        rows.append(dict(id=i, cjk_chars_parquet_instruction=en,
                         cjk_chars_repo_tasks_instruction=z,
                         origin_files=len(names), origin_files_with_cjk_names=ncjk))
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print("wrote", a.out)
    print(f'CJK characters across 100 instructions: parquet (English merge) {tot["en"]}, '
          f'repo tasks/ (Chinese source) {tot["zh"]}')
    print(f'input files: {tot["files"]}, of which {tot["files_cjk"]} carry Chinese names')


if __name__ == "__main__":
    main()
