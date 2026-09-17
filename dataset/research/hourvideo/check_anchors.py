#!/usr/bin/env python3
"""Check that every research/ and agent-work/sources/ citation in a candidate's CSVs resolves.

The anchor test is copied verbatim from lines 25-32 of
../AI Compute vs Human Time/collection-work/tools/validate.py, so it fails on exactly
what that validator fails on. The rule worth knowing: the validator slugifies the
*heading text* — `re.sub(r'[^\\w\\- ]','',h.lower()).replace(' ','-')` — so a Markdown
explicit-anchor attribute like `## Human time {#human-time}` does NOT create the anchor
`#human-time`; it creates `#human-time-human-time`. Write the heading plainly, or put a
literal `id="..."` in the file, which the validator also accepts.

Dependencies: Python 3.8+ standard library only.

Usage:
    python3 check_anchors.py --base ../.. --csv ../../candidates/hourvideo/points.csv \\
                                          --csv ../../candidates/hourvideo/models.csv

Exits non-zero if any citation is missing or any anchor fails to resolve.
"""

import argparse
import csv
import pathlib
import re
import sys

FIELDS = ["human_time_source", "compute_source", "source_record", "parameter_source"]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", required=True,
                    help="directory the research/ and agent-work/sources/ paths are relative to")
    ap.add_argument("--csv", required=True, action="append",
                    help="a candidate CSV to check; repeat for points.csv and models.csv")
    args = ap.parse_args()
    base = pathlib.Path(args.base)

    fails = []
    for path in args.csv:
        for row in csv.DictReader(open(path)):
            ident = row.get("point_id") or row.get("model_id") or path
            for field in FIELDS:
                for ref in re.findall(
                        r"(?<![\w/.-])(?:research|sources)/[^\s;,()]+", row.get(field, "") or ""):
                    p, _, anchor = ref.partition("#")
                    target = base / p
                    if not target.is_file():
                        fails.append(f"{ident}: missing {ref}")
                        continue
                    if anchor and target.suffix == ".md":
                        text = target.read_text()
                        headings = re.findall(r"^#+\s+(.+)$", text, re.M)
                        slugs = [re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-")
                                 for h in headings]
                        if anchor not in slugs and 'id="' + anchor + '"' not in text:
                            fails.append(f"{ident}: missing anchor {ref}")
                            continue
                    print(f"OK   {ident}: {ref}")

    if fails:
        for f in fails:
            print("FAIL " + f, file=sys.stderr)
        sys.exit(1)
    print("all citations resolve")


if __name__ == "__main__":
    main()
