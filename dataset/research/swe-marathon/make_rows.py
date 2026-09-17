"""Build the SWE-Marathon candidate rows.

Compute. The leaderboard publishes, per rollout, a token total that is the whole
prefix re-read on every API call plus the output ("tokens" = n_input + n_output
with cached tokens included, arXiv 2606.07682 Section 4.2). Charging every one of
those positions a full weights pass would price a cache read as a forward pass.
Writing C for the counted total and k for the measured API turn count, an
append-only dialog whose prefix grows linearly gives C = P*k/2 for P processed
positions, so

    P = 2C/k            processed positions, one weights pass each
    Nbar = C/k          mean context those positions attended over
    flops = 2*N_active*P + 4*L*d_attn*Nbar*P

per research/attention-correction.md. k is measured here rather than inferred
from an assumed new-tokens-per-call, which is what the METR rows have to do.

The inversion is checked against a third measurement. Each trajectory's rows
carry the model's own text, so summing them measures the rollout's output tokens
O, which are processed positions by definition. O > P refutes the inversion for
that cell -- the harness is not append-only, it is holding a rolling or compacted
context -- and the cell is withheld. O/P below 1 but not far below says fresh
tool-result input was small relative to output, which for a tool-using agent
means the same thing more weakly, and those rows say so.

Inputs   agent-work/derived/swe-marathon/{cells,turns,trials}.csv
         dataset/models.csv
Outputs  agent-work/derived/swe-marathon/points-swe-marathon.csv
         agent-work/derived/swe-marathon/dispositions.csv
         agent-work/derived/swe-marathon/row-arithmetic.csv
"""
import csv, os, statistics as st

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DER = os.path.join(ROOT, "agent-work", "derived", "swe-marathon")
MODELS = os.path.join(ROOT, "dataset", "models.csv")

HEADER = ("point_id,task,task_category,task_description,model_id,compute_scope,compute_flops,"
          "human_skill,human_time_scope,human_time,performance_vs_human,comparison_issues,"
          "compute_evidence,human_time_evidence,performance_evidence,human_time_statistic,"
          "human_time_subset,human_attempts,human_time_source,compute_method,compute_statistic,"
          "compute_subset,ai_attempts,compute_source,tokens,tokens_accounting,source_dataset,"
          "source_record,notes,ai_cost_usd,ai_cost_basis,ai_cost_date,human_cost_usd,"
          "human_cost_basis,attention_context,attention_ratio").split(",")

# Cell selection. A cell is one task x one agent-model configuration over 8 trials.
PASS_RATE_FLOOR = 0.5          # the configuration resolves the task in most of its trials

# No per-task cap and no reasoning-effort deduplication: every agent-model configuration
# clearing the floor on a task gets a row, so the set shows the trend across models on one
# task. Coordinator ruling, 2026-09-14, replacing a 5-at-40h-and-above / 3-below cap that
# kept one configuration per distinct model.

# Tasks whose deliverable is itself a trained model. The agent chooses the
# training recipe and its GPU cost is the dominant term and is not published, so
# the token compute is not an estimate of the task's compute.
TRAINING_DELIVERABLE = {"parameter-golf", "post-train-ifeval-gpu"}

OUTPUT_SHARE_REFUTED = 1.0     # measured output tokens exceed the rebuilt processed positions
OUTPUT_SHARE_THIN = 0.5        # fresh tool-result input smaller than output; flag in notes
CHARS_PER_TOKEN = 4

MODEL_ID = {
    "Claude Opus 5": "claude-opus-5", "Claude Opus 4.8": "claude-opus-4-8",
    "Claude Sonnet 5": "claude-sonnet-5", "Claude Fable 5": "claude-fable-5",
    "Claude Fable 5.1": "claude-fable-5-1", "GPT-6 Astra": "gpt-6-astra",
    "GPT-5.6-sol": "gpt-5-6-sol", "GPT-5.6-terra": "gpt-5-6-terra",
    "GPT-5.6-luna": "gpt-5-6-luna", "Kimi K3": "kimi-k3", "GLM 5.3": "glm-5.3",
    "GLM 5.3 Flash": "glm-5.3-flash", "GLM 5.2": "glm-5.2", "Grok 4.5": "grok-4-5",
    "Grok 4.6": "grok-4-6", "Muse Spark 1.3": "muse-spark-1-3",
    "DeepSeek V4 Pro": "deepseek-v4-pro-0813", "Gemini 3.7 Flash": "gemini-3-7-flash",
    "Grok 4.6": "grok-4-6",
}
SHORT_MODEL = {
    "claude-opus-5": "opus5", "claude-opus-4-8": "opus48", "claude-fable-5": "fable5",
    "claude-fable-5-1": "fable51", "gpt-6-astra": "astra", "gpt-5-6-sol": "sol",
    "gpt-5-6-terra": "terra", "kimi-k3": "kimik3", "glm-5.3": "glm53",
    "glm-5.3-flash": "glm53flash", "grok-4-5": "grok45", "muse-spark-1-3": "muse13",
    "claude-sonnet-5": "sonnet5", "gpt-5-6-luna": "luna", "glm-5.2": "glm52",
    "grok-4-6": "grok46", "gemini-3-7-flash": "gem37flash",
    "deepseek-v4-pro-0813": "dsv4pro",
}
SHORT_TASK = {
    "kubernetes-rust-rewrite": "k8srust", "excel-clone": "excel", "ruby-rust-port": "rubyrust",
    "mastodon-clone": "mastodon", "trimul-cuda": "trimul", "find-network-alignments": "ppialign",
    "stripe-clone": "stripe", "wasm-simd": "wasmsimd", "zstd-decoder": "zstd",
    "jax-pytorch-rewrite": "jaxtorch", "vliw-kernel-optimization": "vliw",
    "embedding-eval": "embedeval", "parameter-golf": "paramgolf",
    "post-train-ifeval-gpu": "ifeval",
}
# Context window as published for the run window, used only as a consistency check.
WINDOW = {
    "claude-opus-5": 1_000_000, "claude-opus-4-8": 1_000_000, "claude-fable-5": 1_000_000,
    "claude-fable-5-1": 1_000_000, "gpt-6-astra": 400_000, "gpt-5-6-sol": 400_000,
    "gpt-5-6-terra": 400_000, "kimi-k3": 262_144, "glm-5.3": 203_000,
    "glm-5.3-flash": 203_000, "grok-4-5": 2_000_000, "muse-spark-1-3": 1_000_000,
    "claude-sonnet-5": 1_000_000, "gpt-5-6-luna": 400_000, "glm-5.2": 203_000,
    "grok-4-6": 2_000_000, "gemini-3-7-flash": 1_000_000,
    "deepseek-v4-pro-0813": 1_000_000,
}

# Model records this batch adds, written to candidates/swe-marathon-models.csv.
NEW_MODELS = [{
    "model_id": "gemini-3-7-flash", "model": "Gemini 3.7 Flash",
    "company": "Google DeepMind", "model_release_date": "2026-08-13",
    "model_release_source": "https://blog.google/innovation-and-ai/models-and-research/"
                            "gemini-models/introducing-gemini-3-7-flash/",
    "flops_per_token": "80000000000", "flops_per_token_method": "two_active_parameters",
    "active_parameters": "40000000000", "active_parameters_basis": "estimated",
    "active_parameters_low": "15000000000", "active_parameters_high": "90000000000",
    "encoder_parameters": "not_applicable", "encoder_parameters_basis": "not_applicable",
    "decoder_parameters": "not_applicable", "decoder_parameters_basis": "not_applicable",
    "parameter_source": "research/model-priors/google-xai-others.md; "
                        "research/attention-correction.md#model-architectures",
    "notes": "40B active is the Gemini-generation Flash prior the file already holds for "
             "gemini-3-flash-preview, gemini-3.5-flash and gemini-3-8-flash, range 15-90B. "
             "Google discloses no Gemini expert sizes or routing.",
    "attention_layers": "59", "attention_width": "7552", "attention_basis": "estimated",
}]

NAME = {
    "kubernetes-rust-rewrite": "Port Kubernetes from Go to Rust",
    "excel-clone": "Build a spreadsheet product from scratch",
    "ruby-rust-port": "Port a Ruby web application to Rust",
    "mastodon-clone": "Build a Mastodon-compatible social server",
    "trimul-cuda": "Write a Triton kernel for AlphaFold-3 TriMul",
    "find-network-alignments": "Align two protein-interaction networks",
    "stripe-clone": "Build a Stripe-compatible payments API",
    "wasm-simd": "Add SIMD-128 to a WebAssembly interpreter",
    "zstd-decoder": "Implement a Zstandard decompressor in C",
    "jax-pytorch-rewrite": "Port and optimize a JAX policy in PyTorch",
    "vliw-kernel-optimization": "Hand-schedule a kernel for a VLIW simulator",
    "embedding-eval": "Reimplement a text-embedding evaluation framework",
    "parameter-golf": "Train a GPT under a 32 MB checkpoint budget",
    "post-train-ifeval-gpu": "Post-train Llama-3.2-1B to an IFEval target",
}
DESC = {
 "kubernetes-rust-rewrite":
  "One complete attempt at the SWE-Marathon kubernetes-rust-rewrite task: port Kubernetes from Go "
  "to Rust inside the supplied container, reproducing the control-plane behaviour the suite "
  "exercises. The deliverable passes when roughly 3,600 integration tests pass; reward is binary. "
  "Wall-clock limit 10 hours, no GPU.",
 "excel-clone":
  "One complete attempt at the SWE-Marathon excel-clone task: build Tabula, an Excel-style "
  "spreadsheet product serving a single-page browser app and a JSON API from one container, with "
  "formula evaluation and dependency tracking, copy/fill, sort/filter, CSV and XLSX I/O, "
  "persistence across restarts, dynamic arrays, pivot tables, collaboration, locale support and "
  "validation. The deliverable passes when 18 correctness gates pass, including cell-by-cell XLSX "
  "parity to 1e-6 against a vendored LibreOffice oracle, and a browser-driven UX rubric passes in "
  "full. Wall-clock limit 6 hours, no GPU.",
 "ruby-rust-port":
  "One complete attempt at the SWE-Marathon ruby-rust-port task: port a 4,000-line Ruby web "
  "application to Rust inside the supplied container. The deliverable passes 22 checks driven from "
  "2,000 recorded input-output traces; reward is binary. Wall-clock limit 10 hours, no GPU.",
 "mastodon-clone":
  "One complete attempt at the SWE-Marathon mastodon-clone task: build Chirp, a single-container "
  "self-hosted social-media service whose REST API is Mastodon v1-compatible, covering cursor "
  "pagination, RFC 5988 Link headers, idempotency-key deduplication, timeline visibility across "
  "follows and blocks, media, polls, notifications, trending, an admin surface and OAuth2 with "
  "mandatory PKCE, plus a server-rendered HTMX and SSE web UI with no build step and a strict CSP. "
  "The deliverable passes when 19 correctness gates pass and a 10-criterion browser UX rubric "
  "passes in full. No GPU.",
 "trimul-cuda":
  "One complete attempt at the SWE-Marathon trimul-cuda task: write a Triton kernel for the "
  "AlphaFold-3 outgoing TriMul operator, fusing row-wise LayerNorm, five gated linear projections, "
  "a pairwise batched GEMM across the sequence dimension, a second LayerNorm, an output gate and a "
  "final projection over a [B,N,N,C] tensor. The deliverable passes 20 correctness cases and then "
  "must hold maximum per-shape median latency at or under 10,400 microseconds across 10 H100 "
  "benchmark shapes. Wall-clock limit 7 hours, one H100 attached.",
 "find-network-alignments":
  "One complete attempt at the SWE-Marathon find-network-alignments task: find high-quality "
  "alignments between two protein-protein interaction network pairs, fly to human and yeast to "
  "yeast2k, and output two injective alignments. The deliverable passes when both are complete and "
  "injective and clear the S3 structural-similarity thresholds, with node correctness also checked "
  "on the yeast pair. Wall-clock limit 8 hours, no GPU.",
 "stripe-clone":
  "One complete attempt at the SWE-Marathon stripe-clone task: build a single-container "
  "Stripe-compatible payments API covering idempotency-key correctness, webhook delivery with "
  "HMAC-SHA256 signatures and exponential backoff, and the PaymentIntent state machine including "
  "automatic and manual capture, 3DS challenge, declines and illegal transitions. The real Stripe "
  "Python SDK is pointed at the service and every assertion must pass. Wall-clock limit 4 hours, "
  "no GPU.",
 "wasm-simd":
  "One complete attempt at the SWE-Marathon wasm-simd task: add the SIMD-128 proposal to a "
  "WebAssembly interpreter inside the supplied container. The deliverable passes when 31,767 "
  "specification assertions pass; reward is binary. Wall-clock limit 5 hours, no GPU.",
 "zstd-decoder":
  "One complete attempt at the SWE-Marathon zstd-decoder task: implement a Zstandard decompressor "
  "in C, covering the Huffman and FSE table modes, the literal-length, match-length and offset "
  "sequence machinery with repeated-offset history and overlapping match copies, multi-frame "
  "inputs and trained-dictionary frames. The deliverable passes 43 binary comparisons against the "
  "reference decoder; reward is binary. Wall-clock limit 5 hours, no internet, no GPU.",
 "jax-pytorch-rewrite":
  "One complete attempt at the SWE-Marathon jax-pytorch-rewrite task: port a JAX "
  "vision-language-action robotics policy to PyTorch, mapping the nested parameter and state tree "
  "across framework conventions, then optimize the PyTorch inference path under profiler-based "
  "verification without breaking determinism or parity. The deliverable is checked for topology, "
  "layer-level tensor parity, loss and deterministic sampling against the JAX reference, and "
  "latency is measured against a PyTorch baseline on an A100. Wall-clock limit 5 hours.",
 "vliw-kernel-optimization":
  "One complete attempt at the SWE-Marathon vliw-kernel-optimization task: hand-schedule a kernel "
  "for a custom VLIW SIMD architecture simulator under strict per-cycle slot constraints. The "
  "deliverable must match the reference output on randomized correctness checks and then run the "
  "canonical benchmark input in under 1,250 cycles. Wall-clock limit 8 hours, no GPU.",
 "embedding-eval":
  "One complete attempt at the SWE-Marathon embedding-eval task: build a text-embedding evaluation "
  "framework from scratch for all-MiniLM-L6-v2 covering 37 datasets across retrieval, semantic "
  "textual similarity, classification, clustering, pair classification and summarization, "
  "reproducing each protocol's scoring behaviour. The evaluator is re-run from scratch and every "
  "one of the 37 tasks must match the MTEB-derived golden main score and its secondary metrics "
  "within tolerance. Wall-clock limit 4 hours, one H100 attached.",
}
GPU_NOTE = {
 "trimul-cuda": "The attached H100 runs the agent's own correctness cases and the 10 benchmark "
                "shapes; that GPU work is outside compute_flops.",
 "jax-pytorch-rewrite": "The attached A100 runs parity checks and latency profiling of the agent's "
                        "own PyTorch code; that GPU work is outside compute_flops.",
 "embedding-eval": "The attached H100 runs all-MiniLM-L6-v2 over the 37 datasets each time the "
                   "agent re-runs its evaluator; that GPU work is outside compute_flops.",
}


def load(name):
    return list(csv.DictReader(open(os.path.join(DER, name), newline="")))


def select(cells):
    """Per task, the highest-passing configuration of each distinct model, capped."""
    """Every cell clearing the pass-rate floor; the rest recorded with its reason."""
    out, held = [], []
    for c in sorted(cells, key=lambda c: (c["task"], -float(c["pass_rate"] or 0))):
        pr = float(c["pass_rate"]) if c["pass_rate"] != "" else 0.0
        if pr >= PASS_RATE_FLOOR:
            out.append(c)
            continue
        reason = ("no trial resolved the task" if pr == 0 else
                  f"resolved {c['n_pass']} of {c['n_success']} trials, below the "
                  f"{PASS_RATE_FLOOR:.0%} floor for having done the job")
        held.append(dict(task=c["task"], expert_hours=float(c["expert_hours"]),
                         config=c["display_label"] or c["model"], agent=c["agent"],
                         pass_rate=pr, n_pass=c["n_pass"], n_success=c["n_success"],
                         reason=reason))
    return out, held


def main():
    cells = load("cells.csv")
    trials = {t["trial"]: t for t in load("trials.csv")}
    turns = {t["trial"]: int(t["api_turns"]) for t in load("turns.csv") if t["api_turns"]}
    outtok = {t["trial"]: float(t["output_chars"]) / CHARS_PER_TOKEN
              for t in load("turns.csv") if t["api_turns"]}
    models = {m["model_id"]: m for m in csv.DictReader(open(MODELS, newline=""))}
    known = set(models)
    models.update({m["model_id"]: m for m in NEW_MODELS})

    keep, held = select(cells)
    rows, arith = [], []
    for c in keep:
        task, mid = c["task"], MODEL_ID[c["model"]]
        hours = float(c["expert_hours"])
        if task in TRAINING_DELIVERABLE:
            held.append(dict(task=task, expert_hours=hours,
                             config=c["display_label"] or c["model"], agent=c["agent"],
                             pass_rate=float(c["pass_rate"]), n_pass=c["n_pass"],
                             n_success=c["n_success"],
                             reason="deliverable is a trained model; the agent chooses the training "
                                    "recipe and its GPU compute is unpublished and dominates, so "
                                    "the token total is not an estimate of the task's compute"))
            continue
        m = models[mid]
        fpt = float(m["flops_per_token"])
        nact = float(m["active_parameters"])
        L, d = float(m["attention_layers"]), float(m["attention_width"])

        ids = c["pass_trials"].split(";")
        Cs = [float(trials[i]["tokens"]) for i in ids]
        ks = [turns[i] for i in ids]
        Ps = [2 * C / k for C, k in zip(Cs, ks)]
        Os = [outtok[i] for i in ids]
        share = st.mean(Os) / st.mean(Ps)
        if share > OUTPUT_SHARE_REFUTED:
            held.append(dict(task=task, expert_hours=hours,
                             config=c["display_label"] or c["model"], agent=c["agent"],
                             pass_rate=float(c["pass_rate"]), n_pass=c["n_pass"],
                             n_success=c["n_success"],
                             reason=f"measured output tokens are {share:.2f} times the processed "
                                    f"positions the linear-growth inversion rebuilds, so this "
                                    f"harness is not append-only and the inversion gives no "
                                    f"compute estimate for the cell"))
            continue
        Ns = [C / k for C, k in zip(Cs, ks)]
        flops = st.mean(fpt * P + 4 * L * d * N * P for P, N in zip(Ps, Ns))
        Pbar = st.mean(Ps)
        nbar = sum(N * P for N, P in zip(Ns, Ps)) / sum(Ps)      # P-weighted, so flops = fpt*Pbar*(1+r)
        r = 2 * L * d * nbar / nact
        assert abs(flops - fpt * Pbar * (1 + r)) / flops < 1e-9
        costs = [float(trials[i]["cost_usd"]) for i in ids if trials[i]["cost_usd"] != ""]
        dates = sorted(trials[i]["started_at"][:10] for i in ids)

        eff = c["reasoning_effort"]
        pid = f"agen-swemar-{SHORT_TASK[task]}-{SHORT_MODEL[mid]}" + (f"-{eff}" if eff else "")
        Tlen = 2 * st.mean(Cs) / st.mean(ks)
        win = WINDOW[mid]
        note = [
            "The published per-rollout token total is the whole prefix re-read on every call plus "
            f"the output. Processed positions are rebuilt as 2C/k from the counted total and the "
            f"measured API turn count, {st.mean(ks):.0f} turns on these trials, giving "
            f"{Pbar/1e3:.0f}k positions against {st.mean(Cs)/1e6:.1f}M counted tokens; the mean "
            "attended context is measured as C/k rather than assumed."]
        if Tlen > win:
            note.append(f"The implied trajectory length {Tlen/1e3:.0f}k exceeds the "
                        f"{win/1e3:.0f}k context window, so the run compacted and the processed-"
                        "position count is a lower bound by roughly the number of compactions.")
        else:
            note.append(f"The implied trajectory length {Tlen/1e3:.0f}k fits inside the "
                        f"{win/1e3:.0f}k context window, so no compaction is needed for the "
                        "linear-growth inversion to hold.")
        note.append(f"Output tokens measured off the published trajectories are "
                    f"{st.mean(Os)/st.mean(Cs):.2%} of the counted total, against the paper's "
                    f"0.53% for the whole corpus, and {share:.0%} of the rebuilt processed "
                    f"positions" +
                    ("; that leaves less fresh tool-result input than output, so the rebuilt "
                     "count is close to its floor and compute_flops is best read as a lower "
                     "bound." if share > OUTPUT_SHARE_THIN else ", leaving the rest as fresh "
                     "tool-result input."))
        if task in GPU_NOTE:
            note.append(GPU_NOTE[task])
        note.append("Median tokens per trial vary by up to 12x across scaffolds holding the model "
                    "fixed, which is why the row is one task x one agent-model configuration and "
                    "not one per model.")
        rows.append({
            "point_id": pid, "task": NAME[task], "task_category": "coding",
            "task_description": DESC[task], "model_id": mid, "compute_scope": "inference",
            "compute_flops": repr(flops), "human_skill": "expert",
            "human_time_scope": "task_performance", "human_time": repr(hours * 3600),
            "performance_vs_human": "match",
            "comparison_issues": ("different_assessment" if task in ("excel-clone", "mastodon-clone")
                                  else "none_identified"),
            "compute_evidence": "derived_assumed_inputs",
            "human_time_evidence": "source_estimate",
            "performance_evidence": (
                f"Binary verifier reward. AI: {c['n_pass']} of {c['n_success']} completed trials "
                f"resolved the task, pass@1 {float(c['pass_rate']):.0%}; mean partial score "
                f"{float(c['mean_partial']):.3f}. Human: no human attempted the task under "
                f"measurement. The task ships a human-written reference solution that the verifier "
                f"passes, and its author's expert time estimate is {hours:g} hours, so a resolved "
                f"trial is the same deliverable the estimate describes."),
            "human_time_statistic": "point_estimate", "human_time_subset": "not_applicable",
            "human_attempts": "not_applicable",
            "human_time_source": (f"https://swe-marathon.org task metadata, "
                                  f"expert_time_estimate_hours = {hours:g} for {task}; "
                                  f"research/swe-marathon/swe-marathon.md#human-time"),
            "compute_method": "params_tokens", "compute_statistic": "mean",
            "compute_subset": "successful", "ai_attempts": c["n_pass"],
            "compute_source": (f"research/swe-marathon/swe-marathon.md#{pid}; "
                               f"research/swe-marathon/make_rows.py; "
                               f"research/attention-correction.md"),
            "tokens": repr(st.mean(Cs)), "tokens_accounting": "source_total",
            "source_dataset": "SWE-Marathon v1.1",
            "source_record": (f"SWE-Marathon v1.1 leaderboard at https://swe-marathon.org, task "
                              f"{task}, {c['display_label'] or c['model']} under "
                              f"{c['agent']}; trials {c['pass_trials']}; benchmark paper arXiv "
                              f"2606.07682; performance: the same leaderboard's per-trial binary "
                              f"reward; research/swe-marathon/swe-marathon.md#source"),
            "notes": " ".join(note),
            "ai_cost_usd": (f"{st.mean(costs):.2f}" if costs else ""),
            "ai_cost_basis": ("reported" if costs else "not_available"),
            "ai_cost_date": (dates[0] if costs else ""),
            "human_cost_usd": "", "human_cost_basis": "not_available",
            "attention_context": repr(nbar), "attention_ratio": f"{r:.4g}",
        })
        arith.append(dict(point_id=pid, task=task, model_id=mid,
                          reasoning_effort=eff, n_pass=len(ids),
                          C_mean=st.mean(Cs), k_mean=st.mean(ks), P_mean=Pbar,
                          nbar=nbar, attention_ratio=r, flops=flops,
                          output_tokens=st.mean(Os), output_share_of_C=st.mean(Os) / st.mean(Cs),
                          output_share_of_P=share,
                          implied_T=Tlen, context_window=win, ratio_T_window=Tlen / win,
                          expert_hours=hours, flops_per_human_second=flops / (hours * 3600)))

    rows.sort(key=lambda r: r["point_id"])
    with open(os.path.join(DER, "points-swe-marathon.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(DER, "dispositions.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(held[0]))
        w.writeheader()
        w.writerows(sorted(held, key=lambda h: (-h["expert_hours"], h["task"], -h["pass_rate"])))
    with open(os.path.join(DER, "row-arithmetic.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(arith[0]))
        w.writeheader()
        w.writerows(arith)
    mh = list(csv.DictReader(open(MODELS, newline="")).fieldnames)
    used = {r["model_id"] for r in rows}
    add = [m for m in NEW_MODELS if m["model_id"] in used and m["model_id"] not in known]
    missing = used - known - {m["model_id"] for m in add}
    assert not missing, missing
    with open(os.path.join(DER, "models-swe-marathon.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=mh)
        w.writeheader()
        w.writerows(add)
    print(f"{len(rows)} rows, {len(held)} dispositions, {len(add)} new models")


if __name__ == "__main__":
    main()
