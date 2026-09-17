"""Pull the SWE-Marathon v1.1 leaderboard out of the swe-marathon.org bundle.

The site is a client-rendered single-page app: every number it displays is
embedded in its one JavaScript bundle, so a plain fetch of a URL returns an
empty shell and the data has to be read out of the bundle itself. This script
reads the retained copy of that bundle and writes three flat tables.

Input   agent-work/sources/swe-marathon/site-bundle.js   (retained, gitignored)
Output  agent-work/derived/swe-marathon/task-meta.csv    20 tasks
        agent-work/derived/swe-marathon/trials.csv       7,650 rollouts
        agent-work/derived/swe-marathon/cells.csv        958 task x configuration cells
"""
import csv, json, os, re, statistics as st

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
SRC = os.path.join(ROOT, "agent-work", "sources", "swe-marathon", "site-bundle.js")
OUT = os.path.join(ROOT, "agent-work", "derived", "swe-marathon")


def read_bundle():
    with open(SRC, encoding="utf-8", errors="replace") as f:
        return f.read()


def task_meta(s):
    """Per-task author metadata: the expert time estimate and the run limits."""
    ids = [(m.group(1), m.start()) for m in
           re.finditer(r"[,{]id:[`\"']([a-z][a-z0-9-]{3,60})[`\"']", s)]
    out = {}
    for m in re.finditer(r"expert_time_estimate_hours:([0-9.]+)", s):
        task = [i for i in ids if i[1] < m.start()][-1][0]
        seg = s[m.start():m.start() + 900]
        t = re.search(r"agent:\{[^}]*timeout_sec:([0-9e.]+)", seg)
        g = re.search(r"gpus:([0-9]+)", seg)
        gt = re.search(r"gpu_types:\[`([^`]+)`\]", seg)
        out[task] = dict(task=task,
                         expert_hours=float(m.group(1)),
                         agent_timeout_sec=float(t.group(1)) if t else "",
                         gpus=int(g.group(1)) if g else "",
                         gpu_type=gt.group(1) if gt else "")
    assert len(out) == 20, len(out)
    return out


def leaderboard(s):
    """The one JSON.parse blob holding 20 tasks x 48 agent-model configurations."""
    m = re.search(r"version:`(v[0-9.]+)`,tasks:JSON\.parse\(`", s)
    ver, start = m.group(1), m.end()
    i = start
    while True:
        i = s.index("`", i)
        if s[i - 1] != "\\":
            break
        i += 1
    raw = s[start:i].replace("\\`", "`").replace("\\$", "$")
    return ver, json.loads(raw)


def main():
    s = read_bundle()
    meta = task_meta(s)
    ver, lb = leaderboard(s)
    os.makedirs(OUT, exist_ok=True)

    with open(os.path.join(OUT, "task-meta.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(next(iter(meta.values()))))
        w.writeheader()
        w.writerows(meta[k] for k in sorted(meta))

    trials, cells = [], []
    for task, d in sorted(lb.items()):
        for c in d["configs"]:
            ok = [t for t in c["trials"] if t.get("status") == "success"]
            ps = [t for t in ok if t["reward"] == 1.0]
            for t in c["trials"]:
                trials.append(dict(
                    trial=t["id"], task=task, agent=c["agent"], model=c["model"],
                    reasoning_effort=c.get("reasoningEffort") or "",
                    model_variant=c.get("modelVariant") or "",
                    display_label=c.get("displayLabel") or "",
                    reward=t["reward"], partial=t["partial"], status=t.get("status", ""),
                    tokens=t["tokensRaw"], cost_usd=t["costUsd"] if t["costUsd"] is not None else "",
                    tool_calls=t["steps"], duration=t["duration"], started_at=t["startedAt"]))
            mean = lambda xs: st.mean(xs) if xs else ""
            cells.append(dict(
                task=task, expert_hours=meta[task]["expert_hours"],
                agent=c["agent"], model=c["model"],
                reasoning_effort=c.get("reasoningEffort") or "",
                model_variant=c.get("modelVariant") or "",
                display_label=c.get("displayLabel") or "",
                n_listed=c["n"], n_success=len(ok), n_error=len(c["trials"]) - len(ok),
                n_pass=len(ps), pass_rate=len(ps) / len(ok) if ok else "",
                mean_partial=c["partial"], best_partial=c["best"],
                tokens_mean_all=mean([t["tokensRaw"] for t in ok]),
                tokens_mean_pass=mean([t["tokensRaw"] for t in ps]),
                cost_mean_pass=mean([t["costUsd"] for t in ps if t["costUsd"] is not None]),
                pass_trials=";".join(t["id"] for t in ps)))

    for name, rows in (("trials.csv", trials), ("cells.csv", cells)):
        with open(os.path.join(OUT, name), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    print(f"{ver}: {len(meta)} tasks, {len(cells)} cells, {len(trials)} trials")


if __name__ == "__main__":
    main()
