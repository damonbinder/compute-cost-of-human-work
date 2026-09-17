#!/usr/bin/env python3
"""Fold the training attention term into the ten 6ND operation_count rows.

Each row is rebuilt component by component from its own research note. A
component is a block of positions processed by one model at one sequence
length. Weight-matrix FLOPs are 6 * N_active * positions for a weight-update
component and 2 * N_active * positions for a forward-only one; the attention
term is the same multiple of 4 * L * d_attn * N_ctx, so a component's
attention is its weight term times r = 2 * L * d_attn * N_ctx / N_active.

N_ctx is the mean attended context of a causal pass over a length-S sequence,
(S + 1) / 2 -- the same length-weighted mean prefix the inference rows use.

`attention_context` is the weight-FLOP-weighted mean over the positions the
row's own model processes, so that
attention_ratio = 2 * L * d_attn * attention_context / N_active holds exactly.

Usage: python3 training_attention.py OUTPUT_DIR
"""
import csv
import json
import sys
from pathlib import Path

# (L, d_attn, N_active) per model.
SHAPE = {
    # OpenAI family share 0.65 of the dense layer bracket, per architectures.py
    'codex-300m-research': (8, 1536, 3.0e8),
    'codex-2-5b-research': (15, 2944, 2.5e9),
    'codex-12b-research': (25, 4992, 1.2e10),
    'code-llama-7b-base': (32, 4096, 7.0e9),
    'code-llama-34b-base': (48, 8192, 3.4e10),
    'code-llama-7b-kexer': (32, 4096, 7.0e9),
    'multipl-t-starcoder-1b-ocaml': (24, 2048, 1137207296.0),
    'multipl-t-starcoder-15b-ocaml': (40, 6144, 15517456384.0),
    'multipl-t-starcoder-15b-racket': (40, 6144, 15517456384.0),
    'llama-2-13b': (40, 5120, 1.3e10),
    # Unidentified GPT-3.5 helper, 7e9 active by family transfer; shape from the
    # estimated-architecture rule L = (N/196608)^(1/3), d_attn = 128 L.
    'gpt35-helper-assumed': (21, 4224, 7.0e9),
    # StarCoderBase-15B as the MultiPL-T curriculum helper.
    'starcoderbase-15b-helper': (40, 6144, 15517456384.0),
}


def ctx(seq_len):
    return (seq_len + 1) / 2


def comp(model, positions, per_position, seq_len, label):
    """per_position is 6 (weight update) or 2 (forward only), times N_active."""
    L, d, N = SHAPE[model]
    weights = per_position * N * positions
    n_ctx = ctx(seq_len)
    r = 2 * L * d * n_ctx / N
    return dict(label=label, model=model, positions=positions, seq_len=seq_len,
                n_ctx=n_ctx, weights=weights, attention=weights * r, ratio=r)


ROWS = {}

# ---- Codex: 6PT plus a 1-forward-token-per-100 monitoring allowance.
# GPT-3 family context window n_ctx = 2048 (Brown et al. 2020, Table 2.1);
# the Codex paper fine-tunes from that family and does not change it.
for pid, model, P in [('agen-codexfer-codex300m', 'codex-300m-research', 3.0e8),
                      ('agen-codexfer-codex2p5b', 'codex-2-5b-research', 2.5e9),
                      ('agen-codexfer-codex12b', 'codex-12b-research', 1.2e10)]:
    T = 100e9
    ROWS[pid] = (model, [comp(model, T, 6, 2048, 'training'),
                         comp(model, T * 0.01, 2, 2048, 'monitoring')])

# ---- Code Llama: 500B code tokens at sequence length 4,096, then LCFT at
# 16,384 (Rozière et al. §2.4 / Appendix: 7B 3,000 x 2M = 6B, 34B 11,000 x 1M
# = 11B). Monitoring is charged at the token-weighted mean of the two.
for pid, model, P, lcft in [('agen-codexfer-codellama7b', 'code-llama-7b-base', 7.0e9, 6e9),
                            ('agen-codexfer-codellama34b', 'code-llama-34b-base', 3.4e10, 11e9)]:
    base = 500e9
    total = base + lcft
    mean_ctx = (base * ctx(4096) + lcft * ctx(16384)) / total
    mon = comp(model, total * 0.01, 2, 2 * mean_ctx - 1, 'monitoring')
    ROWS[pid] = (model, [comp(model, base, 6, 4096, 'training base'),
                         comp(model, lcft, 6, 16384, 'training LCFT'), mon])

# ---- Kotlin Kexer: 15,000 examples x 4 epochs. The card's 256-example batch
# at "~130K tokens per step" is 256 x 512, so the fine-tune pads to 512.
k_train = comp('code-llama-7b-kexer', 14e6, 6, 512, 'training')
k_mon = comp('code-llama-7b-kexer', 4 * (630 + 161) * 512, 2, 512, 'monitoring')
k_create = comp('gpt35-helper-assumed', 15000 * (100 + 230) * 1.25, 2, 330, 'helper: create Python')
k_trans = comp('gpt35-helper-assumed', (15000 * (25 + 230) + 3.5e6) * 1.25, 2, 255 + 3.5e6 / 15000,
               'helper: translate to Kotlin')
ROWS['agen-codexfer-kotlin7b'] = ('code-llama-7b-kexer', [k_train, k_mon, k_create, k_trans])

# ---- MultiPL-T: demo.py sets max_seq_length 2048 and packs to it. Helper
# curriculum generation runs on StarCoderBase-15B at its own short lengths.
MPLT = dict(test_functions=432361, test_suites=5, test_prompt=160, test_output=160,
            translation_functions=133168)
tests = comp('starcoderbase-15b-helper',
             MPLT['test_functions'] * MPLT['test_suites'] * (MPLT['test_prompt'] + MPLT['test_output']),
             2, MPLT['test_prompt'] + MPLT['test_output'], 'helper: test generation')
for pid, model, tok, epochs, probs, per_fn, prompt_tok, out_tok in [
        ('agen-codexfer-mplt-ocaml1b', 'multipl-t-starcoder-1b-ocaml', 43737088, 7, 156, 100, 138.647, 140),
        ('agen-codexfer-mplt-ocaml15b', 'multipl-t-starcoder-15b-ocaml', 61603840, 10, 156, 100, 138.647, 140),
        ('agen-codexfer-mplt-racket15b', 'multipl-t-starcoder-15b-racket', 47841280, 10, 161, 50, 146.375, 110)]:
    trans = comp('starcoderbase-15b-helper',
                 MPLT['translation_functions'] * per_fn * (prompt_tok + out_tok),
                 2, prompt_tok + out_tok, 'helper: translation')
    ROWS[pid] = (model, [comp(model, tok, 6, 2048, 'training'),
                         comp(model, epochs * probs * 20 * 512, 2, 512, 'monitoring'),
                         tests, trans])

# ---- Memorization: 100 copies of a 1,025-token string padded to 1,032;
# metric callbacks trim to 1,024 positions, the Trainer validation keeps 1,032.
ROWS['memo-binary-1024-llama2-13b'] = ('llama-2-13b', [
    comp('llama-2-13b', 103200, 6, 1032, 'training'),
    comp('llama-2-13b', 2275328, 2, 1024, 'monitoring: metric callbacks'),
    comp('llama-2-13b', 1032000, 2, 1032, 'monitoring: Trainer validation')])


def main(out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows, detail = [], {}
    for pid, (primary, comps) in ROWS.items():
        before = sum(c['weights'] for c in comps)
        after = before + sum(c['attention'] for c in comps)
        own = [c for c in comps if c['model'] == primary]
        own_w = sum(c['weights'] for c in own)
        a_ctx = sum(c['weights'] * c['n_ctx'] for c in own) / own_w
        L, d, N = SHAPE[primary]
        a_ratio = 2 * L * d * a_ctx / N
        rows.append(dict(point_id=pid, model_id=primary, attention_layers=L,
                         attention_width=d, active_parameters=N,
                         attention_context=a_ctx, attention_ratio=a_ratio,
                         compute_flops_before=before, compute_flops_after=after,
                         factor=after / before))
        detail[pid] = comps
    with (out_dir / 'training-corrections.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (out_dir / 'training-components.json').write_text(json.dumps(detail, indent=2) + '\n')
    for r in rows:
        print(f"{r['point_id']:32s} N={r['attention_context']:9.1f} r={r['attention_ratio']:.4f} "
              f"{r['compute_flops_before']:.6e} -> {r['compute_flops_after']:.6e}  x{r['factor']:.4f}")


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
