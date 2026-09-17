#!/usr/bin/env python3
"""Measure a local clone of facebookresearch/algebraic-combinatorics.

Reproduces every figure in agent-work/sources/meta-textbook/algcomb-repo-measurements.md that is my own
measurement rather than a quotation. Dependencies: Python 3.9+ standard library only.

Usage:
    python3 measure_repo.py <path-to-clone> <output.json>

Example:
    git clone --depth 1 https://github.com/facebookresearch/algebraic-combinatorics /tmp/algcomb
    python3 research/meta-textbook/measure_repo.py /tmp/algcomb /tmp/algcomb-measurements.json

Writes a new output file; never modifies the clone.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

DECL = re.compile(
    r"^\s*(@\[[^\]]*\]\s*)?(private |protected |noncomputable |nonrec )*"
    r"(theorem|lemma|def|abbrev|instance|example|structure|inductive|class)\b"
)
NATIVE_DECIDE = re.compile(
    r"(by native_decide|<;>\s*native_decide|^\s*native_decide|;\s*native_decide)"
)
SORRY_TACTIC = re.compile(r"^\s*sorry(\s|$|--)")


def main(repo: str, out_path: str) -> None:
    root = Path(repo)
    src = root / "AlgebraicCombinatorics"
    if not src.is_dir():
        raise SystemExit(f"{src} not found; pass the root of the clone")

    files = sorted(src.rglob("*.lean"))
    total_lines = 0
    by_decl = Counter()
    nd_by_file = Counter()
    sorry_lines = []

    for path in files:
        lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
        # match `cat ... | wc -l`: count newline-terminated lines
        total_lines += len(lines) - 1 if lines and lines[-1] == "" else len(lines)
        nd_by_file[str(path.relative_to(root))] = sum(
            1 for l in lines if "native_decide" in l
        )
        for i, line in enumerate(lines):
            if SORRY_TACTIC.match(line):
                sorry_lines.append(
                    {"file": str(path.relative_to(root)), "line": i + 1, "text": line.strip()}
                )
            if "native_decide" in line and NATIVE_DECIDE.search(line):
                for j in range(i, -1, -1):
                    m = DECL.match(lines[j])
                    if m:
                        by_decl[m.group(3)] += 1
                        break
                else:
                    by_decl["<no enclosing declaration found>"] += 1

    manifest = json.loads((root / "manifest.json").read_text())
    chapters = manifest["chapters"]

    result = {
        "lean_files": len(files),
        "lean_lines": total_lines,
        "manifest_chapters": len(chapters),
        "manifest_target_theorems": sum(len(c["target_theorems"]) for c in chapters),
        "sorry_tactic_uses": len(sorry_lines),
        "sorry_tactic_lines": sorry_lines,
        "native_decide_tactic_uses_by_enclosing_declaration": dict(by_decl),
        "native_decide_tactic_uses_total": sum(by_decl.values()),
        "native_decide_tactic_uses_outside_example": sum(
            v for k, v in by_decl.items() if k != "example"
        ),
        "native_decide_string_occurrences_by_file": {
            k: v for k, v in sorted(nd_by_file.items(), key=lambda kv: -kv[1]) if v
        },
        "lean_toolchain": (root / "lean-toolchain").read_text().strip(),
        "print_axioms_occurrences": sum(
            1
            for p in root.rglob("*")
            if p.is_file()
            and p.suffix in {".lean", ".md"}
            and "#print axioms" in p.read_text(encoding="utf-8", errors="replace")
        ),
    }

    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=2)
        fh.write("\n")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(2)
    main(sys.argv[1], sys.argv[2])
