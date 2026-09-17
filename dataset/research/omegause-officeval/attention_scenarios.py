#!/usr/bin/env python3
"""Quantify the cached-context attention term that compute_flops omits.

The dataset prices every processed position at 2 * active_parameters, which
leaves out the cost of attending over the cached prefix.  DECISIONS.md requires
every long-context row to state that omission with the 4 * L * d_model *
N_context recipe used by the RULER row, on bracketing architectures.

Context length is not published for the OmegaUse runs, so it is reconstructed
from the inverted structure.  With a prefix that grows linearly to its final
length, gross prompt positions G = n * N_final / 2 and freshly processed input
F = N_final, so n = 2 * G / F = 2 / (1 - h) calls and the call-averaged context
is N_bar = N_final / 2 = F / 2.

Three of the five models select a bounded number of key positions per query
(GLM-5.2's indexer at top-2048, MiniMax M3's MSA at 16 blocks of 128 on 57 of
60 layers); for those the recipe runs at min(N_bar, selected) on the sparse
layers.  Both limbs are reported.

Usage:
  python3 attention_scenarios.py \
      --calculations <path>/calculations.json \
      --architectures <path>/architectures.csv \
      --out <path>/attention-scenarios.json

Dependencies: Python 3.8+ standard library only.
"""
import argparse, csv, json


def main():
    ap = argparse.ArgumentParser()
    for f in ("calculations", "architectures", "out"):
        ap.add_argument("--" + f, required=True)
    a = ap.parse_args()
    calc = json.load(open(a.calculations))
    arch = {r["model_id"]: r for r in
            csv.DictReader(open(a.architectures, newline="", encoding="utf-8-sig"))}

    out = {}
    for agent, v in calc["agents"].items():
        m = arch[v["model_id"]]
        L, d = int(m["layers"]), int(m["hidden_size"])
        ics = v["implied_central_structure"]
        F = ics["fresh_input_tokens"]
        h = ics["h"]
        n_calls = 2.0 / (1.0 - h)
        N_bar = F / 2.0
        B = v["billed_tokens_central"]
        per_pos_full = 4.0 * L * d * N_bar
        full = per_pos_full * B
        res = {"layers": L, "hidden_size": d, "attention": m["attention"],
               "implied_calls_per_task": n_calls, "final_context_tokens": F,
               "call_averaged_context_tokens": N_bar,
               "attention_flops_full": full,
               "ratio_to_recorded_full": full / v["flops_central"]}
        if m["sparse_selected_positions"]:
            k = float(m["sparse_selected_positions"])
            share = float(m["sparse_layer_share"]) if m["sparse_layer_share"] else 1.0
            N_eff = share * min(N_bar, k) + (1 - share) * N_bar
            sparse = 4.0 * L * d * N_eff * B
            res.update(sparse_selected_positions=k, sparse_layer_share=share,
                       effective_context_tokens=N_eff,
                       attention_flops_sparse=sparse,
                       ratio_to_recorded_sparse=sparse / v["flops_central"])
        out[agent] = res
    json.dump(out, open(a.out, "w"), indent=1)
    print("wrote", a.out)
    print(f'{"agent":16s} {"L":>4s} {"d":>6s} {"calls":>7s} {"N_bar":>10s} '
          f'{"full x":>8s} {"sparse x":>9s}')
    for k, v in out.items():
        print(f'{k:16s} {v["layers"]:4d} {v["hidden_size"]:6d} '
              f'{v["implied_calls_per_task"]:7.1f} {v["call_averaged_context_tokens"]:10,.0f} '
              f'{v["ratio_to_recorded_full"]:8.2f} '
              f'{v.get("ratio_to_recorded_sparse", float("nan")):9.3f}')


if __name__ == "__main__":
    main()
