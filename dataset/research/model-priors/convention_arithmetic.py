"""Arithmetic behind the convention section of google-xai-others.md.

Two calculations:
  1. Reproduce Grok-2's published active and total parameter counts from its
     released config.json, as a check that architecture-derived counting is
     reliable when the config is public.
  2. Attention, router and speculative-decoding cost as a share of the 2N
     convention, for disclosed configurations and for two proxy configurations
     at the active-parameter scales estimated for Gemini Pro and Gemini Flash.

Run: python3 convention_arithmetic.py
"""

# ---------------------------------------------------------------- Grok-2 check
# https://huggingface.co/xai-org/grok-2/raw/main/config.json (retained alongside
# this note in agent-work/sources/model-priors/google-xai-others/grok-2-config.json)
G = dict(d=8192, layers=64, vocab=131072, heads=64, head_dim=128, kv_heads=8,
         inter=32768, moe_inter=16384, n_experts=8, top_k=2)

def grok2():
    d, hd = G["d"], G["head_dim"]
    attn = d*G["heads"]*hd + 2*d*G["kv_heads"]*hd + G["heads"]*hd*d
    shared = 3*d*G["inter"]            # SwiGLU gate + up + down, always on
    expert = 3*d*G["moe_inter"]        # one routed expert
    act = (attn + shared + G["top_k"]*expert)*G["layers"] + 2*G["vocab"]*d
    tot = (attn + shared + G["n_experts"]*expert)*G["layers"] + 2*G["vocab"]*d
    return attn, shared, expert, act, tot

# ------------------------------------------------- attention share of 2N
# Decode step at context L costs 2*layers*(d_q + d_v)*L FLOPs: one multiply-add
# per (query element, key) for the scores, and one per (value element, key) for
# the weighted sum. Prefill over a prompt of length L averages half that per
# token, because the mean token attends to L/2 predecessors.
CFGS = [
    # label, layers, d_q, d_v, active_params, provenance
    ("Grok-2", 64, 64*128, 64*128, 115.0e9, "disclosed config.json"),
    ("Qwen3-235B-A22B", 94, 64*128, 64*128, 22.0e9, "disclosed config.json"),
    ("GLM-4.5", 92, 96*128, 96*128, 32.0e9, "disclosed config.json"),
    ("DeepSeek-V3 (MLA, naive)", 61, 128*192, 128*128, 37.0e9, "disclosed config.json"),
    ("DeepSeek-V3 (MLA, absorbed)", 61, 128*576, 128*512, 37.0e9, "disclosed config.json"),
    ("Gemini-Pro proxy, 100B active", 80, 8192, 8192, 100.0e9, "assumed"),
    ("Gemini-Flash proxy, 25B active", 48, 5120, 5120, 25.0e9, "assumed"),
]
LS = [4096, 32768, 131072]

def attn_share():
    rows = []
    for label, nl, dq, dv, N, prov in CFGS:
        two_n = 2*N
        cells = []
        for L in LS:
            dec = 2*nl*(dq+dv)*L
            cells += [dec/two_n, dec/2/two_n]
        rows.append((label, two_n, cells, prov))
    return rows

def local_attention(window=1024, local_per_global=5):
    """Gemma 3's interleaved pattern: 5 sliding-window layers per global layer."""
    return [(L, (local_per_global*min(window, L) + L)/(local_per_global+1)) for L in LS]

def router_share(layers, d, n_experts, N):
    return 2*layers*d*n_experts/(2*N)

def spec_decode(k, alpha):
    """FLOPs per *accepted* token when drafting k tokens ahead with per-token
    acceptance alpha, verifying with the full model. Draft cost ignored (the
    draft head is small); the multiplier is positions-forwarded / accepted."""
    expected_accepted = sum(alpha**i for i in range(1, k+1)) + 1  # +1 bonus token
    return (k+1)/expected_accepted

if __name__ == "__main__":
    attn, shared, expert, act, tot = grok2()
    print("== Grok-2 architecture-derived counts")
    print(f"  per layer: attention {attn/1e6:.1f}M, shared MLP {shared/1e6:.1f}M, "
          f"one expert {expert/1e6:.1f}M")
    print(f"  active {act:.5e}  (published 1.15019056768e11, ratio {act/115019056768:.4f})")
    print(f"  total  {tot:.5e}  (published 2.69515497472e11, ratio {tot/269515497472:.4f})")
    print(f"  total/active sparsity ratio {tot/act:.2f}x")

    print("\n== Attention FLOPs as a share of the 2N convention")
    hdr = f"{'model':32s} {'2N':>10s} " + " ".join(
        f"{'dec'+str(L//1024)+'k':>8s} {'pre'+str(L//1024)+'k':>8s}" for L in LS)
    print(hdr)
    for label, two_n, cells, prov in attn_share():
        print(f"{label:32s} {two_n:10.2e} " +
              " ".join(f"{c*100:7.1f}%" for c in cells))

    print("\n== Interleaved local attention (Gemma 3 pattern: 5 local w=1024 : 1 global)")
    for L, eff in local_attention():
        print(f"  L={L:7d}  mean effective context per layer {eff:9.0f}  "
              f"reduction {L/eff:.2f}x")

    print("\n== Router FLOPs as a share of 2N")
    for nl, d, ne, N in [(80, 8192, 256, 100e9), (94, 4096, 128, 22e9),
                         (61, 7168, 384, 32e9)]:
        print(f"  layers={nl:3d} d={d:5d} experts={ne:3d} N={N/1e9:5.0f}B "
              f"-> {router_share(nl, d, ne, N)*100:.3f}%")

    print("\n== Speculative decoding FLOPs per accepted token, multiple of 2N")
    for k in (1, 2, 3):
        for alpha in (0.6, 0.8, 0.9):
            print(f"  k={k} alpha={alpha:.1f} -> {spec_decode(k, alpha):.2f}x")
