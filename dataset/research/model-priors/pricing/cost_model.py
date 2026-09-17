"""Serving-cost model and implied-active-parameter arithmetic for pricing-crosscheck.md.

Inputs are in agent-work/sources/model-priors/pricing/. Nothing here touches either models.csv.
Run: python3 cost_model.py > calculations.txt
"""
import json, csv, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "..", "..", "sources", "model-priors", "pricing"))

# ---------------------------------------------------------------- hardware
# SemiAnalysis InferenceX chip pages, retrieved 2026-09-13.
CHIPS = {
    # name:        fp4 dense F/s, fp8 dense F/s, HBM GB, BW B/s,  $/hr hyper, $/hr retail
    "gb300":  dict(fp4=1.50e16, fp8=5.00e15, hbm=278, bw=8.0e12, hyper=2.31, retail=5.00),
    "gb200":  dict(fp4=1.00e16, fp8=5.00e15, hbm=186, bw=8.0e12, hyper=1.86, retail=4.00),
    "b300":   dict(fp4=1.35e16, fp8=4.50e15, hbm=268, bw=8.0e12, hyper=2.26, retail=4.25),
    "b200":   dict(fp4=9.00e15, fp8=4.50e15, hbm=180, bw=8.0e12, hyper=1.73, retail=3.70),
    "h200":   dict(fp4=None,    fp8=1.979e15, hbm=141, bw=4.8e12, hyper=1.22, retail=2.90),
    "mi355x": dict(fp4=1.0066e16, fp8=5.033e15, hbm=288, bw=8.0e12, hyper=1.50, retail=2.90),
    # TPU v7 Ironwood: no public list price; $1.60/chip-hr is the SemiAnalysis estimate of
    # Anthropic's negotiated rate. No FP4 path is published.
    "tpuv7":  dict(fp4=None,    fp8=4.614e15, hbm=192, bw=7.37e12, hyper=1.60, retail=1.60),
}

def dollars_per_flop(chip, precision="fp4", tier="hyper", util=1.0):
    c = CHIPS[chip]
    peak = c[precision]
    if peak is None:
        return None
    return (c[tier] / 3600.0) / (peak * util)

# ------------------------------------------------- empirical utilisation
# InferenceX tco-feed rows: output tokens/sec per chip on the throughput-vs-interactivity
# Pareto frontier, at a stated interactivity tier (output tok/s/user). Retrieved 2026-09-13.
ACTIVE_B = {  # active parameters, billions, disclosed or Epoch-estimated
    "DeepSeek-R1-0528": 37.0,
    "DeepSeek-V4-Pro": 49.0,
    "Kimi-K2.5": 32.0,
    "MiniMax-M3": 22.0,
    "gpt-oss-120b": 5.1,
}

def load_feed():
    rows = []
    with open(os.path.join(SRC, "inferencex-tco-feed-2026-09-13.csv")) as fh:
        for r in csv.DictReader(fh):
            r["tier"] = int(r["tier"]); r["tput"] = float(r["output_tput_per_gpu"])
            rows.append(r)
    return rows

def utilisation_table(rows, tier=50, chips=("gb300", "gb200", "b200")):
    """Aggregate MFU on each workload, and the prefill/decode split where both workloads exist.

    FLOPs per output token on an ISL:OSL = n:1 workload are 2*P*(n+1): n input tokens prefilled
    and one decode step, each 2*P FLOP/token ignoring attention.
    Writing a = chip-seconds per input token and b = chip-seconds per output token,
        1/tput(8:1) = 8a + b ;  1/tput(1:1) = a + b  ->  a = (1/t8 - 1/t1)/7,  b = 1/t1 - a.
    """
    out = []
    for m, P in ACTIVE_B.items():
        for hw in chips:
            peak = CHIPS[hw]["fp4"]
            g = {r["workload"]: r for r in rows
                 if r["model"] == m and r["hardware"] == hw and r["tier"] == tier}
            rec = dict(model=m, P=P, hw=hw, peak=peak)
            for wl, n in (("8192x1024", 8), ("1024x1024", 1)):
                if wl in g and g[wl]["tput"] > 0:
                    t = g[wl]["tput"]
                    rec[f"tput_{n}"] = t
                    rec[f"mfu_{n}"] = t * 2 * P * 1e9 * (n + 1) / peak
            if "tput_8" in rec and "tput_1" in rec:
                a = (1 / rec["tput_8"] - 1 / rec["tput_1"]) / 7.0
                b = 1 / rec["tput_1"] - a
                if a > 0 and b > 0:
                    rec["eta_prefill"] = 2 * P * 1e9 / (a * peak)
                    rec["eta_decode"] = 2 * P * 1e9 / (b * peak)
                    # effective concurrent batch implied by the decode residual, FP4 = 0.5 B/param
                    rec["batch_eff"] = P * 1e9 * 0.5 / (0.70 * CHIPS[hw]["bw"] * b)
            out.append(rec)
    return out

# ------------------------------------------------------------ cost model
def cost_per_mtok(P, chip="gb300", precision="fp4", tier="hyper",
                  eta_prefill=0.30, eta_decode=0.05):
    """$ per million input tokens (prefill) and per million output tokens (decode).

    Both are 2*P FLOP per token, divided by an effective utilisation that differs because prefill
    is compute-bound and decode is memory-bound. Attention and KV traffic are excluded; see
    `attention_multiplier` for the long-context correction.
    """
    c = CHIPS[chip]
    peak = c[precision]
    per_s = c[tier] / 3600.0
    flops = 2.0 * P
    cin = 1e6 * flops / (eta_prefill * peak) * per_s
    cout = 1e6 * flops / (eta_decode * peak) * per_s
    return cin, cout

def attention_multiplier(context, P, n_kv_heads=8, head_dim=128, n_layers=64):
    """Attention FLOPs per decode token relative to 2*P, for a frontier-shaped proxy.

    Per decode token attention reads the whole KV cache: 4 * n_layers * n_kv_heads * head_dim
    * context FLOP (two matmuls, multiply-accumulate counted as 2).
    """
    attn = 4.0 * n_layers * n_kv_heads * head_dim * context
    return 1.0 + attn / (2.0 * P)

def implied_P(price_out, margin, chip="gb300", precision="fp4", tier="hyper", eta_decode=0.05):
    """Active parameters implied if list output price equals serving cost / (1 - margin)."""
    _, cout_at_100B = cost_per_mtok(100e9, chip, precision, tier, eta_decode=eta_decode)
    target = price_out * (1.0 - margin)
    return 100e9 * target / cout_at_100B

# -------------------------------------------------------------- prices
PRICES = {  # model: (input, cached_input, output)
    "GPT-6 Astra": (10.0, 1.00, 50.0),
    "GPT-5.6 Sol": (4.0, 0.40, 20.0),
    "GPT-5.5": (5.0, 0.50, 30.0),
    "GPT-5.4": (2.5, 0.25, 15.0),
    "GPT-5": (1.25, 0.125, 10.0),
    "GPT-5.6 Luna": (0.20, 0.02, 1.20),
    "GPT-5 nano": (0.05, 0.005, 0.40),
    "Claude Fable 5.1": (10.0, 0.25, 50.0),
    "Claude Fable 5": (10.0, 1.00, 50.0),
    "Claude Opus 5": (5.0, 0.50, 25.0),
    "Claude Opus 4.1": (15.0, 1.50, 75.0),
    "Claude Sonnet 5": (2.0, 0.20, 10.0),
    "Claude Sonnet 4.6": (3.0, 0.30, 15.0),
    "Claude Haiku 4.5": (1.0, 0.10, 5.0),
    "Gemini 3.1 Pro": (2.0, 0.20, 12.0),
    "Gemini 2.5 Pro": (1.25, 0.125, 10.0),
    "Gemini 3.5 Flash": (1.50, 0.15, 9.0),
    "Gemini 3.1 Flash-Lite": (0.25, 0.025, 1.50),
    "Grok 4": (3.0, None, 15.0),
    "Grok 4.6": (2.0, 0.50, 6.0),
    "Grok 4.20": (1.25, 0.20, 2.50),
}

def blended(p, w=(0.7, 0.2, 0.1)):
    """Artificial Analysis 7:2:1 cache:input:output blend."""
    cin, cc, cout = p[0], p[1], p[2]
    if cc is None:
        cc = cin * 0.1
    return w[0] * cc + w[1] * cin + w[2] * cout

# ----------------------------------------------------------------- main
def main():
    print("=" * 78)
    print("1. DOLLARS PER FLOP AT 100% UTILISATION (hyperscaler TCO tier)")
    print("=" * 78)
    for chip in CHIPS:
        for prec in ("fp4", "fp8"):
            v = dollars_per_flop(chip, prec, "hyper")
            if v:
                print(f"  {chip:7s} {prec}  {v:.3e} $/FLOP   ({v*1e21:6.2f} $ per ZFLOP,"
                      f" {1/v/1e21:6.2f} ZFLOP per $)")
    print()

    rows = load_feed()
    print("=" * 78)
    print("2. UTILISATION CALIBRATED ON MEASURED THROUGHPUT, MODELS OF KNOWN ACTIVE SIZE")
    print("   InferenceX tco-feed, interactivity tier 50 output tok/s/user, FP4, retrieved 2026-09-13")
    print("=" * 78)
    print(f"  {'model':18s} {'P(B)':>5s} {'hw':6s} {'t/s/chip 8:1':>12s} {'MFU 8:1':>8s}"
          f" {'t/s/chip 1:1':>12s} {'MFU 1:1':>8s} {'eta_pre':>8s} {'eta_dec':>8s} {'batch':>6s}")
    etas_p, etas_d, batches = [], [], []
    for r in utilisation_table(rows):
        if "tput_8" not in r and "tput_1" not in r:
            continue
        ep = r.get("eta_prefill"); ed = r.get("eta_decode"); be = r.get("batch_eff")
        if ep is not None and ep <= 1.0:
            etas_p.append(ep); etas_d.append(ed); batches.append(be)
        print(f"  {r['model']:18s} {r['P']:5.1f} {r['hw']:6s}"
              f" {r.get('tput_8', float('nan')):12.0f} {r.get('mfu_8', float('nan')):8.1%}"
              f" {r.get('tput_1', float('nan')):12.0f} {r.get('mfu_1', float('nan')):8.1%}"
              f" {(ep if ep else float('nan')):8.1%} {(ed if ed else float('nan')):8.2%}"
              f" {(be if be else float('nan')):6.0f}")
    if etas_p:
        print(f"\n  physically admissible decompositions (eta_prefill <= 1): n={len(etas_p)}")
        print(f"  eta_prefill  median {sorted(etas_p)[len(etas_p)//2]:.1%}  range "
              f"{min(etas_p):.1%}-{max(etas_p):.1%}")
        print(f"  eta_decode   median {sorted(etas_d)[len(etas_d)//2]:.2%}  range "
              f"{min(etas_d):.2%}-{max(etas_d):.2%}")
        print(f"  batch_eff    median {sorted(batches)[len(batches)//2]:.0f}  range "
              f"{min(batches):.0f}-{max(batches):.0f}")
    print()

    print("=" * 78)
    print("3. COST TO SERVE A MILLION TOKENS, MODEL OF P ACTIVE PARAMETERS")
    print("   GB300 NVL72, FP4, eta_prefill 0.30, eta_decode 0.05 (calibrated centrals from part 2)")
    print("=" * 78)
    print(f"  {'P (B)':>7s} {'$/Mtok in (hyper)':>18s} {'$/Mtok out (hyper)':>19s}"
          f" {'$/Mtok in (retail)':>19s} {'$/Mtok out (retail)':>20s} {'8:1 blend hyper':>16s}")
    for Pb in (20, 40, 100, 150, 200, 300, 600):
        P = Pb * 1e9
        ih, oh = cost_per_mtok(P, tier="hyper")
        ir, orr = cost_per_mtok(P, tier="retail")
        blend = (8 * ih + oh) / 9
        print(f"  {Pb:7d} {ih:18.4f} {oh:19.4f} {ir:19.4f} {orr:20.4f} {blend:16.4f}")
    print()
    print("  Long-context correction, decode attention FLOPs relative to 2P")
    print("  (64 layers, 8 KV heads, head dim 128 - a frontier-shaped proxy):")
    for Pb in (40, 100, 200):
        line = f"    P={Pb:3d}B: "
        for ctx in (4096, 32768, 131072, 1000000):
            line += f" {ctx//1024:5d}k x{attention_multiplier(ctx, Pb*1e9):.2f}"
        print(line)
    print()

    print("=" * 78)
    print("4. IMPLIED ACTIVE PARAMETERS FROM LIST OUTPUT PRICE AT AN ASSUMED MARGIN")
    print("   (no overhead wedge: pure GB300 FP4 marginal cost)")
    print("=" * 78)
    for margin in (0.50, 0.70, 0.90, 0.99):
        s = f"  margin {margin:>4.0%}: "
        for name in ("GPT-6 Astra", "Claude Opus 5", "Gemini 3.1 Pro"):
            P = implied_P(PRICES[name][2], margin)
            s += f" {name} {P/1e9:9.0f}B "
        print(s)
    print()
    print("  Wedge required to reconcile. Anthropic inference margin 70% (SemiAnalysis) means")
    print("  realised compute cost = 30% of realised revenue. Opus 5 at the AA 7:2:1 blend:")
    b_opus = blended(PRICES["Claude Opus 5"])
    print(f"    blended realised price          ${b_opus:.3f} /Mtok")
    print(f"    implied realised compute cost   ${0.30*b_opus:.3f} /Mtok")
    for Pb in (100, 200):
        ih, oh = cost_per_mtok(Pb*1e9, tier="hyper")
        ir, orr = cost_per_mtok(Pb*1e9, tier="retail")
        bh = blended((ih, ih*0.1, oh)); br = blended((ir, ir*0.1, orr))
        print(f"    model cost at P={Pb}B, same blend: ${bh:.4f} (hyper) to ${br:.4f} (retail)")
        print(f"      -> non-model overhead wedge {0.30*b_opus/br:.0f}x to {0.30*b_opus/bh:.0f}x")
    print()

    print("=" * 78)
    print("5. WITHIN-LAB PRICE RATIOS AT ONE DATE (2026-09-13)")
    print("=" * 78)
    pairs = [
        ("GPT-6 Astra", "GPT-5.6 Sol"), ("GPT-6 Astra", "GPT-5.5"),
        ("GPT-6 Astra", "GPT-5"), ("GPT-5.6 Sol", "GPT-5"), ("GPT-5.5", "GPT-5"),
        ("Claude Fable 5.1", "Claude Opus 5"), ("Claude Opus 5", "Claude Sonnet 5"),
        ("Claude Sonnet 5", "Claude Haiku 4.5"), ("Claude Opus 4.1", "Claude Opus 5"),
        ("Gemini 3.1 Pro", "Gemini 3.5 Flash"), ("Gemini 3.1 Pro", "Gemini 3.1 Flash-Lite"),
        ("Gemini 3.1 Pro", "Gemini 2.5 Pro"), ("Grok 4", "Grok 4.6"),
        ("GPT-6 Astra", "Claude Fable 5.1"), ("GPT-5.6 Sol", "Claude Opus 5"),
        ("GPT-6 Astra", "Gemini 3.1 Pro"), ("Claude Fable 5.1", "Gemini 3.1 Pro"),
    ]
    print(f"  {'pair':44s} {'in':>6s} {'out':>6s} {'cache':>6s} {'blend':>6s}"
          f" {'sqrt':>6s} {'^1.5':>6s}")
    for a, b in pairs:
        pa, pb = PRICES[a], PRICES[b]
        ri = pa[0] / pb[0]
        ro = pa[2] / pb[2]
        rc = (pa[1] / pb[1]) if (pa[1] and pb[1]) else float('nan')
        rbl = blended(pa) / blended(pb)
        print(f"  {a+' / '+b:44s} {ri:6.2f} {ro:6.2f} {rc:6.2f} {rbl:6.2f}"
              f" {math.sqrt(rbl):6.2f} {rbl**1.5:6.2f}")
    print()

    print("=" * 78)
    print("6. IMPLIED SIZE RATIOS UNDER THE THREE READINGS, AND THE RESULTING ACTIVE COUNTS")
    print("=" * 78)
    anchors = {"GPT-5.6 Sol": (100, 150), "Claude Opus 5": (100, 100), "GPT-5": (100, 100)}
    tests = [("GPT-6 Astra", "GPT-5.6 Sol"), ("GPT-6 Astra", "GPT-5"),
             ("Claude Fable 5.1", "Claude Opus 5")]
    for a, b in tests:
        rbl = blended(PRICES[a]) / blended(PRICES[b])
        cur, prop = anchors[b]
        print(f"  {a} vs {b}: blended price ratio {rbl:.2f}")
        for label, mult in (("sqrt  (margin-premium reading)", math.sqrt(rbl)),
                            ("face  (central)", rbl),
                            ("^1.5  (fixed-cost-dilution reading)", rbl ** 1.5)):
            print(f"    {label:38s} size ratio {mult:5.2f}"
                  f"  -> {mult*cur:6.0f}B on a {cur}B anchor,"
                  f" {mult*prop:6.0f}B on a {prop}B anchor")
    print()

    print("=" * 78)
    print("7. SENSITIVITY OF IMPLIED P TO MARGIN AND UTILISATION (GPT-6 Astra, $50/Mtok out)")
    print("=" * 78)
    print(f"  {'eta_decode':>10s} " + " ".join(f"{m:>12.0%}" for m in (0.50, 0.70, 0.90, 0.99)))
    for ed in (0.02, 0.05, 0.10, 0.20):
        line = f"  {ed:10.0%} "
        for m in (0.50, 0.70, 0.90, 0.99):
            P = implied_P(50.0, m, eta_decode=ed)
            line += f" {P/1e12:11.2f}T"
        print(line)
    print("\n  Only the bottom-left corner - a 99% effective margin on marginal decode cost -")
    print("  lands inside the credible band. Read the other way: for Astra's $50 output price to")
    print("  be consistent with a 200B active model on GB300 at FP4, the effective margin over")
    print("  marginal decode cost has to be")
    for Pb, tier in ((200, "hyper"), (200, "retail")):
        _, co = cost_per_mtok(Pb * 1e9, tier=tier)
        print(f"    P={Pb}B, {tier} TCO: cost ${co:.4f}/Mtok, price/cost {50/co:5.0f}x,"
              f" implied margin {1 - co/50:.3%}")
    print("  The implied-P calculation is therefore a statement about the overhead wedge, not")
    print("  about the model, and its sensitivity to the margin assumption is total: implied P")
    print("  is exactly proportional to (1 - margin).")

    print()
    print("=" * 78)
    print("8. PRICE TO MARGINAL SERVING COST MULTIPLE, AT EACH MODEL'S PROPOSED PRIOR")
    print("   M_out = list output price / GB300-FP4 decode cost at P_proposed (hyperscaler TCO)")
    print("   M_in  = list input  price / GB300-FP4 prefill cost at P_proposed")
    print("=" * 78)
    PROPOSED = {  # model: proposed active parameters in billions, from the three prior reports
        "GPT-6 Astra": 200, "GPT-5.6 Sol": 150, "GPT-5.5": 100, "GPT-5.4": 100,
        "GPT-5": 100, "GPT-5.6 Luna": 8, "GPT-5 nano": 8,
        "Claude Fable 5.1": 150, "Claude Fable 5": 150, "Claude Opus 5": 100,
        "Claude Opus 4.1": 180, "Claude Sonnet 4.6": 100, "Claude Haiku 4.5": 40,
        "Gemini 3.1 Pro": 130, "Gemini 2.5 Pro": 100, "Gemini 3.5 Flash": 40,
        "Gemini 3.1 Flash-Lite": 20, "Grok 4": 200, "Grok 4.20": 70,
    }
    print(f"  {'model':24s} {'P_prop(B)':>9s} {'$in':>7s} {'$out':>7s}"
          f" {'cost_in':>8s} {'cost_out':>9s} {'M_in':>6s} {'M_out':>6s} {'out:in px':>9s}")
    ms = []
    for name, Pb in PROPOSED.items():
        if name not in PRICES:
            continue
        pin, pc, pout = PRICES[name]
        ci, co = cost_per_mtok(Pb * 1e9)
        mi, mo = pin / ci, pout / co
        ms.append((name, mo))
        print(f"  {name:24s} {Pb:9d} {pin:7.2f} {pout:7.2f} {ci:8.4f} {co:9.4f}"
              f" {mi:6.0f} {mo:6.0f} {pout/pin:9.1f}")
    vals = sorted(m for _, m in ms)
    print(f"\n  M_out across the set: min {vals[0]:.0f} ({min(ms, key=lambda x: x[1])[0]}),"
          f" median {vals[len(vals)//2]:.0f},"
          f" max {vals[-1]:.0f} ({max(ms, key=lambda x: x[1])[0]}); spread {vals[-1]/vals[0]:.1f}x")
    print("  Modeled cost ratio out:in is eta_prefill/eta_decode = "
          f"{0.30/0.05:.1f}x; listed out:in price ratios run 2x to 8x.")
    print()
    def lab_of(n):
        for k, v in (("GPT", "OpenAI"), ("Claude", "Anthropic"),
                     ("Gemini", "Google"), ("Grok", "xAI")):
            if n.startswith(k):
                return v
        raise KeyError(n)
    bylab = {}
    for name, mo in ms:
        lab = lab_of(name)
        bylab.setdefault(lab, []).append((name, mo))
    print("  Within-lab median M_out, at the proposed priors:")
    labmed = {}
    for lab, items in bylab.items():
        v = sorted(m for _, m in items)
        labmed[lab] = v[len(v) // 2]
        print(f"    {lab:10s} n={len(v)}  median {labmed[lab]:5.0f}"
              f"  range {v[0]:.0f}-{v[-1]:.0f}")
    base = labmed["OpenAI"]
    print("  Relative to OpenAI: " + ", ".join(
        f"{lab} {labmed[lab]/base:.2f}x" for lab in sorted(labmed)))
    print("  A lab whose median M is high is either serving larger models than the priors say,")
    print("  or charging a wider margin. The reported margins (Anthropic inference 70%, API")
    print("  >80%; OpenAI consolidated 33%) point at the second.")
    print()
    print("  What P would put each model at its OWN LAB'S median M_out:")
    for name, Pb in PROPOSED.items():
        if name not in PRICES:
            continue
        lab = lab_of(name)
        _, co = cost_per_mtok(Pb * 1e9)
        mo = PRICES[name][2] / co
        print(f"    {name:24s} proposed {Pb:4d}B -> lab-median-M equivalent"
              f" {Pb*mo/labmed[lab]:6.0f}B")
    print()
    print("  What P would put each model at the whole-set median M_out (cross-lab, invalid if")
    print("  margins differ by lab, shown only to display the size of the cross-lab problem):")
    med = vals[len(vals)//2]
    for name, Pb in PROPOSED.items():
        if name not in PRICES:
            continue
        _, co = cost_per_mtok(Pb * 1e9)
        mo = PRICES[name][2] / co
        print(f"    {name:24s} proposed {Pb:4d}B -> median-M equivalent {Pb*mo/med:6.0f}B")

if __name__ == "__main__":
    main()
