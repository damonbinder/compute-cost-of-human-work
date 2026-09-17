"""Count API turns in the published SWE-Marathon v1.1 trajectories.

The leaderboard publishes a token total per rollout but not a call count, and
the token total is the whole prefix re-read on every call plus the output. The
call count is what separates those two, so it is read off the public trajectory
JSON: each row carries `step`, the API turn it belongs to, and `call`, its index
within that turn. The turn count is max(step).

Only the passing trials behind the built rows are fetched; the file list comes
from cells.csv. Trajectories are large and are not retained.

Input   agent-work/derived/swe-marathon/cells.csv
Output  agent-work/derived/swe-marathon/turns.csv
"""
import csv, json, os, urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
OUT = os.path.join(ROOT, "agent-work", "derived", "swe-marathon")
URL = "https://swe-marathon.org/trajectories/v1.1/{}.json"


def turns(tid):
    req = urllib.request.Request(URL.format(tid), headers={"User-Agent": "Mozilla/5.0"})
    err = ""
    for _ in range(3):
        try:
            rows = json.load(urllib.request.urlopen(req, timeout=180))["rows"]
            chars = sum(len(r.get("detail") or "") + len(r.get("title") or "")
                        for r in rows)
            return dict(trial=tid, api_turns=max(r.get("step", 0) for r in rows),
                        rows=len(rows), output_chars=chars, error="")
        except Exception as e:
            err = str(e)
    return dict(trial=tid, api_turns="", rows="", output_chars="", error=err)


def main(only=None):
    cells = list(csv.DictReader(open(os.path.join(OUT, "cells.csv"), newline="")))
    ids = sorted({t for c in cells if c["pass_trials"]
                  for t in c["pass_trials"].split(";")
                  if only is None or (c["task"], c["model_variant"]) in only})
    with ThreadPoolExecutor(8) as ex:
        rows = list(ex.map(turns, ids))
    with open(os.path.join(OUT, "turns.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["trial", "api_turns", "rows", "output_chars", "error"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} trajectories, {sum(1 for r in rows if not r['api_turns'])} failed")


if __name__ == "__main__":
    main()
