#!/usr/bin/env python3
"""Append one per-point section to research/gaia.md for every candidate row.

Everything after the <!-- GENERATED POINTS --> marker in the note is replaced by
sections headed with the exact point_id, each restating the run identity, the
native per-model counters, the arithmetic from counted tokens to FLOPs, the human
side, and the scenarios the row's compute_flops omits.

Dependencies: none beyond the standard library.

Usage:
    python3 write_note_points.py <calculations.json> <points.csv> <models_csvs> <note.md>

<models_csvs> is a comma-separated list of registries supplying flops_per_token;
the first file wins on duplicate ids.
"""
import csv
import json
import sys

MARKER = "<!-- GENERATED POINTS -->"


def fmt(n):
    return f"{n:,.0f}"


def main(calc_path, points_path, models_path, note_path):
    with open(calc_path) as fh:
        calc = json.load(fh)
    points = {r["point_id"]: r for r in csv.DictReader(open(points_path))}
    coef = {}
    for path in models_path.split(","):
        for r in csv.DictReader(open(path)):
            try:
                coef.setdefault(r["model_id"], float(r["flops_per_token"]))
            except ValueError:
                pass  # not_applicable or blank; no model used here has one

    out = [MARKER, ""]
    for p in calc["points"]:
        row = points[p["point_id"]]
        n = p["n_with_usage"]
        out.append(f"## {p['point_id']}")
        out.append("")
        out.append(
            f"HAL run `{p['run_id']}` ({p['agent']}, arguments "
            f"`{json.dumps(p['agent_args'], sort_keys=True)}`, run date "
            f"{p['run_date']}), "
            f"[trace](https://huggingface.co/datasets/agent-evals/hal_traces/blob/main/{p['run_id']}_UPLOAD.zip), "
            f"reduced to `agent-work/sources/gaia/hal-run-summaries/{p['run_id']}.json`. "
            f"GAIA validation Level {p['level']}: {p['n_questions']} questions, "
            f"{n} with logged usage, "
            f"{round(p['accuracy'] * p['n_questions'])} solved "
            f"({p['accuracy']:.4f}, standard error {p['accuracy_se']:.4f}) against "
            f"{p['human_score']:.3f} for the human annotators at this level."
        )
        out.append("")
        out.append("| Model | Role | prompt | cached | cache write | cache read | output | reasoning | calls | counted | FLOPs/token |")
        out.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        total_counted = 0
        total_flops = 0.0
        for name, info in sorted(
            p["per_model"].items(), key=lambda kv: -kv[1]["counted_tokens"]
        ):
            role = "primary" if name == p["primary_model_usage_name"] else "helper"
            c = info["counted_tokens"]
            total_counted += c
            total_flops += c * coef[info["model_id"]]
            out.append(
                f"| `{name}` -> `{info['model_id']}` | {role} | "
                f"{fmt(info['prompt_tokens'])} | {fmt(info['cached_tokens'])} | "
                f"{fmt(info['cache_creation_input_tokens'])} | "
                f"{fmt(info['cache_read_input_tokens'])} | "
                f"{fmt(info['completion_tokens'])} | "
                f"{fmt(info['reasoning_tokens'])} | {fmt(info['calls'])} | "
                f"{fmt(c)} | {coef[info['model_id']]:.3g} |"
            )
        out.append("")
        out.append(
            f"Duplicate spans dropped run-wide: "
            f"{p['duplicate_spans_dropped']:,} usage-bearing parents whose child "
            f"carries the same block. Counted tokens are "
            f"`(prompt - cached) + cache write + output`, summing "
            f"to {fmt(total_counted)} over the level, that is "
            f"**{p['tokens_per_question_counted']:,.2f} tokens per question** over "
            f"{n} questions with usage. FLOPs are the per-model counted totals "
            f"times each model's coefficient, {total_flops:.6e} over the level, that "
            f"is **{p['flops_per_question']:.6e} FLOPs per question**. "
            f"Human time {p['human_mean_s']:.2f} s, the mean of the "
            f"{p['n_questions']} annotator self-reports at this level "
            f"(median {p['human_median_s']:.0f} s). At list prices on "
            f"{p['run_date']}, including cache reads and the helper, "
            f"**${p['ai_cost_usd_per_question']:,.4f} per question**."
        )
        out.append("")
        lo_a, hi_a = (p["scenario_attention_multiple_low"],
                      p["scenario_attention_multiple_high"])
        span = (f"{lo_a:.2f}x" if abs(hi_a - lo_a) < 5e-3
                else f"{lo_a:.2f}x to {hi_a:.2f}x")
        att = (
            f"cached-context attention {span} at the "
            f"{p['mean_prefix_tokens_per_call']:,.0f}-token mean prefix over "
            f"{p['llm_calls_per_question']:.1f} calls per question"
        )
        out.append(
            f"Scenarios, none of them entering `compute_flops`: charging the whole "
            f"prefix with no cache credit, "
            f"{p['scenario_gross_multiple']:.3f}x "
            f"({p['tokens_per_question_gross']:,.0f} tokens per question); generated "
            f"tokens only as a floor, {p['scenario_output_only_multiple']:.4f}x "
            f"({p['tokens_per_question_output_only']:,.0f} tokens per question); "
            f"omitted {att}, one-sided upward. Cached share of prompt tokens "
            f"{p['cached_share_of_prompt_tokens']:.3f}; helper share of counted "
            f"tokens {p['helper_share_of_counted_tokens']:.4f}."
        )
        out.append("")
        bar = ("above the half-of-human retention bar" if not p["close_call"]
               else f"kept under the close-calls ruling, "
                    f"{(0.5 - p['ratio_to_human']) / p['se_of_ratio']:.2f} standard "
                    f"errors under the 0.5 guide on a standard error of "
                    f"{p['se_of_ratio']:.3f}")
        solved_t = p["counted_tokens_per_solved_question"]
        failed_t = p["counted_tokens_per_failed_question"]
        fr = p["failed_to_solved_token_ratio"]
        outcome_split = (
            f" Compute averages all attempts: {solved_t:,.0f} counted tokens per "
            f"solved question against {failed_t:,.0f} per failed one over "
            f"{p['n_solved_with_usage']} and {p['n_failed_with_usage']} questions, "
            f"a ratio of {fr:.2f}." if fr else
            f" Compute averages all attempts, of which "
            f"{p['n_solved_with_usage']} were solved and "
            f"{p['n_failed_with_usage']} failed."
        )
        out.append(
            f"Label `{row['performance_vs_human']}`: "
            f"{p['ratio_to_human']:.2f} of the human rate, {bar} and short of "
            f"comparable." + outcome_split
        )
        out.append("")

    text = open(note_path).read()
    # Split on the LAST occurrence: prose above the marker may quote it, and
    # splitting on the first occurrence once silently truncated this note.
    head = text.rsplit(MARKER, 1)[0]
    if head.count(MARKER):
        raise SystemExit(
            "the marker appears more than twice; refusing to guess the split")
    with open(note_path, "w") as fh:
        fh.write(head + "\n".join(out).rstrip() + "\n")
    print(f"wrote {len(calc['points'])} point sections into {note_path}")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
