#!/usr/bin/env python3
"""Build the GAIA candidate rows, the calculations file and the disposition table.

Input: the per-run, per-level join written by build_gaia_table.py, the annotator
time statistics written by parse_annotator_times.py, and the model registries
that supply flops_per_token and active_parameters_basis.

One row is one GAIA validation question at one difficulty level, run by one
(agent, model, effort) configuration. Rows are kept where the agent's accuracy on
that level is at least half the level's human annotator score, per the
"uninformative failures are excluded" ruling in DECISIONS.md, or within one
standard error of that guide, per the "close calls at the exclusion line" ruling;
every other (run, level) cell and every unusable run is written to the
disposition table with its score and the reason.

Dependencies: none beyond the standard library.

Usage:
    python3 make_rows.py <calc_json> <annotator_stats_json> <models_csvs> \
        <list_prices_csv> <out_dir>

<models_csvs> is a comma-separated list, the canonical root registry first; the
first file wins on duplicate ids. Only models absent from that first registry are
written to the candidate models.csv, copied byte-identically from the registry
that does carry them, following the batch convention that shared records stay
canonical in the root file.
<out_dir> receives points.csv, models.csv and dispositions.csv; calculations.json
is written next to this script.
"""
import csv
import json
import os
import sys

# ---------------------------------------------------------------- constants --

# GAIA paper Table 4: share of correct answers by the validating annotators on
# valid questions, per level, and the aggregate reported as the human score.
HUMAN_SCORE = {"1": 0.939, "2": 0.918, "3": 0.873, "all": 0.92}

# Keep a (run, level) cell if its accuracy is at least KEEP_FRACTION of the
# level's human score, or within one standard error of that guide. GAIA answers
# are open-ended exact match, so the chance floor is zero and no floor
# subtraction applies. Set CLOSE_CALL_SE to 0 for the strict bar.
KEEP_FRACTION = 0.5
CLOSE_CALL_SE = 1.0

# Questions carrying an attached file, by level, from the validation metadata.
N_WITH_FILE = {"1": 11, "2": 20, "3": 7}

LEVEL_DEF = {
    "1": "Level 1 took its annotator at most 5 steps and one tool",
    "2": "Level 2 took its annotator 5 to 10 steps and several tools",
    "3": "Level 3 took long step sequences and arbitrary tools",
}

AGENT_LABEL = {"hal": "HAL Generalist Agent", "odr": "HF Open Deep Research"}

TOOLS = {
    "hal": (
        "a smolagents code agent with web search, a page-to-markdown browser, a "
        "Python interpreter, a shell, a reader for office, PDF and audio files "
        "and a GPT-4o image helper"
    ),
    "odr": (
        "a smolagents manager code agent over a text-browser sub-agent with "
        "search, navigation, find-in-page and archive lookup, plus a reader for "
        "office, PDF and audio files and a GPT-4o image tool"
    ),
}

# (agent code, model code) per HAL run id, for point ids and row text.
RUN_CODE = {
    "gaia_hal_generalist_agent_claude37sonnet20250219_1744772193": ("hal", "sonnet37"),
    "gaia_hal_generalist_agent_claude37sonnet20250219_high_1744730242": ("hal", "sonnet37high"),
    "gaia_hal_generalist_agent_claudehaiku45_1760657477": ("hal", "haiku45"),
    "gaia_hal_generalist_agent_claudeopus41_1758719749": ("hal", "opus41high"),
    "gaia_hal_generalist_agent_claudeopus41_1758798743": ("hal", "opus41"),
    "gaia_hal_generalist_agent_claudeopus420250514_1754344946": ("hal", "opus4"),
    "gaia_hal_generalist_agent_claudeopus420250514_1754374886": ("hal", "opus4high"),
    "gaia_hal_generalist_agent_claudesonnet45_1759265643": ("hal", "sonnet45high"),
    "gaia_hal_generalist_agent_claudesonnet45_1759276006": ("hal", "sonnet45"),
    "gaia_hal_generalist_agent_claudesonnet45_1760447287": ("hal", "sonnet45v2"),
    "gaia_hal_generalist_agent_deepseekaideepseekr1_1744683894": ("hal", "dsr1"),
    "gaia_hal_generalist_agent_deepseekaideepseekv3_1744673872": ("hal", "dsv3"),
    "gaia_hal_generalist_agent_deepseekchatv30324_1760455632": ("hal", "dsv30324v2"),
    "gaia_hal_generalist_agent_gemini20flash_1744828175": ("hal", "gemini20flash"),
    "gaia_hal_generalist_agent_gpt4120250414_1744652581": ("hal", "gpt41"),
    "gaia_hal_generalist_agent_gpt520250807_1758875386": ("hal", "gpt5"),
    "gaia_hal_generalist_agent_o3mini20250131_1744609696": ("hal", "o3minilow"),
    "gaia_hal_generalist_agent_o3mini20250131_high_1744670471": ("hal", "o3minihigh"),
    "gaia_hal_generalist_agent_o4mini20250416_high_1745167285": ("hal", "o4minihigh"),
    "gaia_hal_generalist_agent_o4mini20250416_low_1745167262": ("hal", "o4minilow"),
    "gaia_hf_open_deep_research_claude37sonnet20250219_1745000974": ("odr", "sonnet37"),
    "gaia_hf_open_deep_research_claude37sonnet20250219_high_1745539901": ("odr", "sonnet37high"),
    "gaia_hf_open_deep_research_claudeopus41_1755030930": ("odr", "opus41"),
    "gaia_hf_open_deep_research_claudeopus41_high_1755092997": ("odr", "opus41think"),
    "gaia_hf_open_deep_research_claudeopus4_1754425534": ("odr", "opus4"),
    "gaia_hf_open_deep_research_deepseekaideepseekr1_1744851690": ("odr", "dsr1"),
    "gaia_hf_open_deep_research_deepseekaideepseekv3_1744851680": ("odr", "dsv3"),
    "gaia_hf_open_deep_research_gemini20flash_1744843220": ("odr", "gemini20flash"),
    "gaia_hf_open_deep_research_gpt4120250414_1744843595": ("odr", "gpt41"),
    "gaia_hf_open_deep_research_gpt520250807_1754605128": ("odr", "gpt5"),
    "gaia_hf_open_deep_research_o320250416_1745876880": ("odr", "o3"),
    "gaia_hf_open_deep_research_o3mini20250131_high_1744843485": ("odr", "o3minihigh"),
    "gaia_hf_open_deep_research_o4mini20250416_high_1744923206": ("odr", "o4minihigh"),
    "gaia_hf_open_deep_research_o4mini20250416_low_1744921254": ("odr", "o4minilow"),
}

# Effort wording for task_description, keyed by run id where the run sets one.
EFFORT = {
    "gaia_hal_generalist_agent_claude37sonnet20250219_high_1744730242": "high reasoning effort",
    "gaia_hal_generalist_agent_claudeopus41_1758719749": "high reasoning effort",
    "gaia_hal_generalist_agent_claudeopus420250514_1754374886": "high reasoning effort",
    "gaia_hal_generalist_agent_claudesonnet45_1759265643": "high reasoning effort",
    "gaia_hal_generalist_agent_o3mini20250131_1744609696": "low reasoning effort",
    "gaia_hal_generalist_agent_o3mini20250131_high_1744670471": "high reasoning effort",
    "gaia_hal_generalist_agent_o4mini20250416_high_1745167285": "high reasoning effort",
    "gaia_hal_generalist_agent_o4mini20250416_low_1745167262": "low reasoning effort",
    "gaia_hf_open_deep_research_claude37sonnet20250219_high_1745539901": "high reasoning effort",
    "gaia_hf_open_deep_research_o3mini20250131_high_1744843485": "high reasoning effort",
    "gaia_hf_open_deep_research_o4mini20250416_high_1744923206": "high reasoning effort",
    "gaia_hf_open_deep_research_o4mini20250416_low_1744921254": "low reasoning effort",
}

# Runs excluded outright, with the reason recorded in the disposition table.
RUN_EXCLUSIONS = {
    "gaia_hal_generalist_agent_claudeopus420250514_1754344946": (
        "Aborted run: 64 of 165 questions carry no logged model call and 90 calls "
        "ended in an exception, so its 30.3% accuracy measures the harness rather "
        "than the agent"
    ),
    "gaia_hal_generalist_agent_o320250416_1753903002": (
        "Slim upload: the zip carries run-level usage only, with no per-call "
        "records, so no per-question or per-level compute can be formed; its "
        "28.5% accuracy would fail the retention bar in any case"
    ),
    "gaia_hal_generalist_agent_claudesonnet45_1760447287": (
        "Ran agents/hal_generalist_agent_v2, which is absent from the repository "
        "at the commit the run records and from the repository today, so the tool "
        "set and step cap behind the token counts cannot be verified"
    ),
    "gaia_hal_generalist_agent_deepseekchatv30324_1760455632": (
        "Ran the unpublished agents/hal_generalist_agent_v2 as above; its 22.4% "
        "accuracy would fail the retention bar in any case"
    ),
    "gaia_hf_open_deep_research_claudesonnet45_1759311826": (
        "Not retrieved: the 2.0 GB upload decrypts to a plaintext too large to "
        "hold in memory on the machine used; the three HAL Generalist Agent runs "
        "of Claude Sonnet 4.5 cover the model"
    ),
    "gaia_hf_open_deep_research_claudesonnet45_1759261812": (
        "Not retrieved: the 2.4 GB upload decrypts to a plaintext too large to "
        "hold in memory on the machine used; the three HAL Generalist Agent runs "
        "of Claude Sonnet 4.5 cover the model"
    ),
}

# Provider whose price sheet applies to each usage-model name. OpenRouter
# publishes no per-token sheet of its own and passes the underlying provider's
# list rates through, so its Anthropic models are priced at Anthropic's.
PRICE_PROVIDER = {
    "o3-mini-2025-01-31": "openai",
    "o4-mini-2025-04-16": "openai",
    "o3-2025-04-16": "openai",
    "gpt-4.1-2025-04-14": "openai",
    "gpt-5-2025-08-07": "openai",
    "gpt-4o-2024-11-20": "openai",
    "claude-3-7-sonnet-20250219": "anthropic",
    "claude-opus-4-20250514": "anthropic",
    "claude-haiku-4-5": "anthropic",
    "claude-haiku-4-5-20251001": "anthropic",
    "anthropic/claude-opus-4": "anthropic",
    "anthropic/claude-opus-4.1": "anthropic",
    "anthropic/claude-sonnet-4.5": "anthropic",
    "deepseek-ai/DeepSeek-R1": "together",
    "deepseek-ai/DeepSeek-V3": "together",
    "deepseek/deepseek-chat-v3-0324": "deepseek",
    "gemini-2.0-flash": "google",
}

# Bracketing decoder shapes for the omitted cached-context attention term, by
# model id: (layers_low, layers_high, d_model_low, d_model_high, basis). Tiers
# follow research/apex-agents.md#cached-context-attention; DeepSeek's shape is
# its published config (61 layers, d_model 7168).
ATTENTION_SHAPE = {
    "claude-opus-4": (80, 120, 10240, 16384, "bracket, 180B-active tier"),
    "claude-opus-4-1": (80, 120, 10240, 16384, "bracket, 180B-active tier"),
    "claude-3-7-sonnet": (64, 96, 8192, 12288, "bracket, 100B-active tier"),
    "claude-sonnet-4-5": (64, 96, 8192, 12288, "bracket, 100B-active tier"),
    "claude-haiku-4-5": (36, 56, 3584, 5120, "bracket, 40B-active tier"),
    "gpt-5": (64, 96, 8192, 12288, "bracket, 100B-active tier"),
    "gpt-4.1-2025-04-14": (48, 72, 5120, 7168, "bracket, 50B-active tier"),
    "gpt-4o-2024-11-20": (48, 72, 5120, 7168, "bracket, 50B-active tier"),
    "o3-2025-04-16": (48, 72, 5120, 7168, "bracket, 50B-active tier"),
    "o3-mini-2025-01-31": (28, 40, 2880, 4096, "bracket, 20B-active tier"),
    "o4-mini-2025-04-16": (28, 40, 2880, 4096, "bracket, 20B-active tier"),
    "gemini-2.0-flash-001": (28, 40, 2880, 4096, "bracket, 25B-active tier"),
    "deepseek-r1": (61, 61, 7168, 7168, "published DeepSeek-V3 config"),
    "deepseek-v3": (61, 61, 7168, 7168, "published DeepSeek-V3 config"),
    "deepseek-v3-0324": (61, 61, 7168, 7168, "published DeepSeek-V3 config"),
}

POINT_COLUMNS = [
    "point_id", "task", "task_category", "task_description", "model_id",
    "compute_scope", "compute_flops", "human_skill", "human_time_scope",
    "human_time", "performance_vs_human", "comparison_issues", "compute_evidence",
    "human_time_evidence", "performance_evidence", "human_time_statistic",
    "human_time_subset", "human_attempts", "human_time_source",
    "human_time_method", "compute_method", "compute_statistic", "compute_subset",
    "ai_attempts", "compute_source", "tokens", "tokens_accounting",
    "source_dataset", "source_record", "notes",
    # Cost columns, appended after notes per the 2026-09-13 ruling in
    # DECISIONS.md. Observed only, never estimated; the backfill waits on the
    # shared list-price table, so they are written blank as the root rows are.
    "ai_cost_usd", "ai_cost_basis", "ai_cost_date",
    "human_cost_usd", "human_cost_basis",
]

MODEL_COLUMNS = [
    "model_id", "model", "company", "model_release_date", "model_release_source",
    "flops_per_token", "flops_per_token_method", "active_parameters",
    "active_parameters_basis", "encoder_parameters", "encoder_parameters_basis",
    "decoder_parameters", "decoder_parameters_basis", "parameter_source", "notes",
]

# CSV text-field caps from DECISIONS.md.
CAPS = {
    "notes": 586, "task_description": 560, "performance_evidence": 337,
    "source_record": 455, "compute_source": 220, "human_time_source": 205,
}

HUMAN_TIME_SOURCE = (
    "https://huggingface.co/datasets/gaia-benchmark/GAIA, 2023/validation "
    "metadata, Annotator Metadata 'How long did this take?'; "
    "agent-work/sources/gaia/gaia-validation-annotator-times.csv; research/gaia.md#human-time"
)

# -------------------------------------------------------------------- logic --


def load_prices(path):
    rows = []
    with open(path) as fh:
        for r in csv.DictReader(fh):
            rows.append(r)
    return rows


def price_row(prices, model_id, provider, date):
    """The sheet in force for this model and provider on the run date."""
    best = None
    for r in prices:
        if r["model_id"] != model_id or r["provider"] != provider:
            continue
        start, end = r["price_sheet_start"], r["price_sheet_end"]
        if start and date < start:
            continue
        if end and date > end:
            continue
        best = r
    return best


def usd(prices, per_model, date, n):
    """Mean dollar cost per question at list prices on the run date.

    Priced on the de-duplicated counters, so this is what the work would have
    cost, not the doubled figure HAL publishes. Cache reads are priced at the
    cached-input rate rather than excluded, per COLUMNS and the shared price
    table's conventions; cache writes are priced where a provider charges for
    them. Standard tier, no batch discount. Returns None if any contributing
    model lacks a sheet.
    """
    total = 0.0
    for name, info in per_model.items():
        provider = PRICE_PROVIDER.get(name)
        row = price_row(prices, info["model_id"], provider, date) if provider else None
        if row is None or not row["input_usd_per_m"]:
            return None
        rate_in = float(row["input_usd_per_m"])
        rate_out = float(row["output_usd_per_m"])
        rate_cached = (float(row["cached_input_usd_per_m"])
                       if row["cached_input_usd_per_m"] else rate_in)
        rate_write = (float(row["cache_write_usd_per_m"])
                      if row["cache_write_usd_per_m"] else rate_in)
        fresh = info["prompt_tokens"] - info["cached_tokens"]
        total += (
            fresh * rate_in
            + info["cached_tokens"] * rate_cached
            + info["cache_read_input_tokens"] * rate_cached
            + info["cache_creation_input_tokens"] * rate_write
            + info["completion_tokens"] * rate_out
        ) / 1e6
    return total / n


def load_models(paths):
    models = {}
    for path in paths:
        with open(path) as fh:
            for row in csv.DictReader(fh):
                models.setdefault(row["model_id"], row)
    return models


def attention_ratio(per_model, flops_total, prefix_tokens):
    """Attention FLOPs the 2 x active-parameters convention omits, as a multiple.

    Per processed position with a context of N tokens the attention products cost
    4 * layers * d_model * N, counting a multiply and an add as two operations
    (the recipe the dataset's RULER row uses). N is the run's mean prefix per
    call. This is the append-to-a-cached-prefix form and is the upper of the two
    readings: where a call re-processes the whole prefix, the mean context over
    the prefill positions is N/2 and the term halves.
    """
    lo = hi = 0.0
    for info in per_model.values():
        shape = ATTENTION_SHAPE.get(info["model_id"])
        if shape is None or not info["counted_tokens"]:
            continue
        l_lo, l_hi, d_lo, d_hi, _ = shape
        lo += 4 * l_lo * d_lo * prefix_tokens * info["counted_tokens"]
        hi += 4 * l_hi * d_hi * prefix_tokens * info["counted_tokens"]
    if not flops_total:
        return None, None
    return lo / flops_total, hi / flops_total


def fit(field, text):
    text = " ".join(text.split())
    cap = CAPS.get(field)
    if cap and len(text) > cap:
        raise SystemExit(f"{field} is {len(text)} chars, over the {cap} cap:\n{text}")
    if text.rstrip().endswith((".", ",", ";")) and field in (
        "human_time_source", "compute_source", "source_record"
    ):
        raise SystemExit(f"{field} ends in punctuation: {text[-60:]}")
    return text


def main(calc_json, stats_json, models_csvs, list_prices_csv, out_dir):
    with open(calc_json) as fh:
        runs = {r["run_id"]: r for r in json.load(fh)["runs"]}
    with open(stats_json) as fh:
        stats = json.load(fh)
    registries = models_csvs.split(",")
    models = load_models(registries)
    canonical = load_models(registries[:1])
    prices = load_prices(list_prices_csv)
    os.makedirs(out_dir, exist_ok=True)

    points, dispositions, calcs = [], [], []
    used_model_ids = set()

    for rid in sorted(set(runs) | set(RUN_EXCLUSIONS)):
        if rid in RUN_EXCLUSIONS:
            run = runs.get(rid)
            acc = run["levels"]["all"]["accuracy"] if run else None
            dispositions.append({
                "run_id": rid,
                "level": "all",
                "n_questions": 165,
                "accuracy": round(acc, 4) if acc is not None else "",
                "human_score": HUMAN_SCORE["all"],
                "ratio_to_human": round(acc / HUMAN_SCORE["all"], 3) if acc else "",
                "outcome": "excluded",
                "reason": RUN_EXCLUSIONS[rid],
            })
            continue
        run = runs[rid]
        if rid not in RUN_CODE:
            raise SystemExit(f"no point-id code for run {rid}")
        agent_code, model_code = RUN_CODE[rid]

        for level in ("1", "2", "3"):
            d = run["levels"][level]
            acc, human = d["accuracy"], HUMAN_SCORE[level]
            ratio = acc / human
            se_ratio = d["accuracy_se"] / human
            close_call = ratio < KEEP_FRACTION
            base = {
                "run_id": rid, "level": level, "n_questions": d["n_questions"],
                "accuracy": round(acc, 4), "human_score": human,
                "ratio_to_human": round(ratio, 3),
                "se_of_ratio": round(se_ratio, 3),
                "standard_errors_below_guide": round(
                    (KEEP_FRACTION - ratio) / se_ratio, 2) if se_ratio else "",
            }
            if ratio < KEEP_FRACTION - CLOSE_CALL_SE * se_ratio:
                gap = (f"{(KEEP_FRACTION - ratio) / se_ratio:.2f} standard errors"
                       if se_ratio else "infinitely many standard errors")
                dispositions.append({**base, "outcome": "not a row", "reason": (
                    f"Accuracy {acc:.1%} is {ratio:.0%} of the {human:.1%} human "
                    f"score at this level, {gap} below the half-of-human guide")})
                continue
            if d["n_missing_usage"] > 0.1 * d["n_questions"]:
                dispositions.append({**base, "outcome": "not a row", "reason": (
                    f"{d['n_missing_usage']} of {d['n_questions']} questions carry "
                    f"no logged model call, too large a share of the level for a "
                    f"per-question compute mean")})
                continue
            if close_call:
                dispositions.append({**base, "outcome": "row, close call", "reason": (
                    f"Accuracy {acc:.1%} is {ratio:.0%} of the {human:.1%} human "
                    f"score, {(KEEP_FRACTION - ratio) / se_ratio:.2f} standard "
                    f"errors below the half-of-human guide, so it is kept under "
                    f"the close-calls ruling")})

            point_id = f"agen-gaia-{agent_code}-{model_code}-l{level}"
            primary_id, primary_name, primary_tokens = None, None, -1
            helper_counted = counted_total = prompt_total = cached_total = 0
            for name, info in d["per_model"].items():
                counted_total += info["counted_tokens"]
                prompt_total += info["prompt_tokens"]
                cached_total += info["cached_tokens"]
                used_model_ids.add(info["model_id"])
                if name == "gpt-4o-2024-11-20":
                    helper_counted += info["counted_tokens"]
                elif info["counted_tokens"] > primary_tokens:
                    primary_tokens = info["counted_tokens"]
                    primary_id, primary_name = info["model_id"], name
            any_estimated = any(
                models.get(i["model_id"], {}).get("active_parameters_basis") != "reported"
                for i in d["per_model"].values())
            cached_share = cached_total / prompt_total if prompt_total else 0.0
            att_lo, att_hi = attention_ratio(
                d["per_model"], d["flops_total"], d["mean_prefix_tokens_per_call"])
            helper_share = helper_counted / counted_total if counted_total else 0.0
            gross_mult = d["gross_tokens_per_question"] / d["counted_tokens_per_question"]
            cost = usd(prices, d["per_model"], run["date"], d["n_with_usage"])
            solved_t = d["counted_tokens_per_solved_question"]
            failed_t = d["counted_tokens_per_failed_question"]
            fail_ratio = (failed_t / solved_t) if solved_t and failed_t else None
            openrouter = any(n.startswith("anthropic/") for n in d["per_model"])
            # A primary model whose parent spans were dropped was double-logged by
            # HAL; the helper alone accounts for at most a couple of dozen drops.
            doubled_primary = primary_name is not None and not (
                openrouter or primary_name.startswith("claude-")
            )

            calcs.append({
                "point_id": point_id, "run_id": rid, "agent": AGENT_LABEL[agent_code],
                "agent_args": run["agent_args"], "run_date": run["date"],
                "level": level, "n_questions": d["n_questions"],
                "n_with_usage": d["n_with_usage"],
                "n_missing_usage": d["n_missing_usage"],
                "accuracy": acc, "accuracy_se": d["accuracy_se"],
                "human_score": human, "human_mean_s": d["human_mean_s"],
                "human_median_s": d["human_median_s"],
                "primary_model_usage_name": primary_name,
                "primary_model_id": primary_id,
                "tokens_per_question_counted": d["counted_tokens_per_question"],
                "tokens_per_question_gross": d["gross_tokens_per_question"],
                "tokens_per_question_output_only": d["output_tokens_per_question"],
                "llm_calls_per_question": d["llm_calls_per_question"],
                "mean_prefix_tokens_per_call": d["mean_prefix_tokens_per_call"],
                "cached_share_of_prompt_tokens": cached_share,
                "helper_share_of_counted_tokens": helper_share,
                "flops_per_question": d["flops_per_question"],
                "scenario_gross_multiple": gross_mult,
                "scenario_output_only_multiple":
                    d["output_tokens_per_question"] / d["counted_tokens_per_question"],
                "scenario_attention_multiple_low": att_lo,
                "scenario_attention_multiple_high": att_hi,
                "ratio_to_human": ratio,
                "se_of_ratio": se_ratio,
                "close_call": close_call,
                "n_solved_with_usage": d["n_solved_with_usage"],
                "n_failed_with_usage": d["n_failed_with_usage"],
                "counted_tokens_per_solved_question":
                    d["counted_tokens_per_solved_question"],
                "counted_tokens_per_failed_question":
                    d["counted_tokens_per_failed_question"],
                "failed_to_solved_token_ratio": fail_ratio,
                "duplicate_spans_dropped": run["call_counts"].get(
                    "usage_spans_dropped_as_parent"),
                "ai_cost_usd_per_question": cost,
                "openrouter_path": openrouter,
                "per_model": d["per_model"],
            })

            effort = EFFORT.get(rid)
            desc = (
                f"One of the {d['n_questions']} Level {level} questions in GAIA's "
                f"2023 validation split of 165: a factoid question whose answer is "
                f"not in plain text on the web, {N_WITH_FILE[level]} with an "
                f"attached file. {LEVEL_DEF[level]}. Run by "
                f"{AGENT_LABEL[agent_code]}, {TOOLS[agent_code]}"
                + (f", at {effort}" if effort else "")
                + ". Output is one short string, number or list, scored by "
                "GAIA's quasi-exact-match scorer."
            )
            perf = (
                f"Quasi-exact match on the reference answer: the agent solves "
                f"{round(acc * d['n_questions'])} of {d['n_questions']} Level "
                f"{level} questions ({acc:.1%}), against {human:.1%} for GAIA's "
                f"validating annotators at this level, {ratio:.0%} of the human "
                f"rate, with no chance floor. The human figure is the "
                f"share of correct answers by two fresh annotators over the valid "
                f"subset of GAIA's 623 validation questions."
            )
            src = (
                f"HAL run {rid}, model argument {run['agent_args'].get('model_name')}, "
                f"agents/{'open_deep_research' if agent_code == 'odr' else 'hal_generalist_agent'}, "
                f"run date {run['date']}; "
                f"https://huggingface.co/datasets/agent-evals/hal_traces file "
                f"{rid}_UPLOAD.zip; GAIA 2023 validation Level {level}, "
                f"{d['n_questions']} of 165 questions; performance: per-task scores "
                f"in the same trace, human score https://arxiv.org/abs/2311.12983 Table 4"
            )
            note_parts = []
            if cached_share > 0.01:
                note_parts.append(
                    f"Cache reads excluded at {cached_share:.0%} of prompt tokens; "
                    f"the endpoint caches by default, so no reuse is not live and "
                    f"the full prefix gives {gross_mult:.1f}x.")
            elif openrouter:
                note_parts.append(
                    "No cache_control in the harness, so no Anthropic caching "
                    "occurred; OpenRouter returns null details blocks, so zero "
                    "cached tokens is a missing counter, and its counts are its "
                    "own, not Anthropic's.")
            else:
                note_parts.append(
                    "No cache_control in the harness and zero cache reads "
                    "reported, so every call re-processed the whole prefix: "
                    "harness re-processing, not the task, sets the size.")
            if doubled_primary:
                note_parts.append(
                    "HAL double-logs each call here; the duplicate is dropped, "
                    "so these counts are half HAL's published totals.")
            if fail_ratio:
                note_parts.append(
                    f"Failed questions cost {fail_ratio:.1f}x a solved one; "
                    f"annotator timings are solves by construction.")
            if agent_code == "odr":
                note_parts.append(
                    "The scaffold's GPT-4o image tool bypasses the trace, so its "
                    "tokens are missing.")
            # The dropped questions are carried by compute_subset = positive_tokens
            # and by ai_attempts against human_attempts, so notes do not repeat them.
            if close_call:
                note_parts.append(
                    f"Close call: {ratio:.2f} of the human rate, "
                    f"{(KEEP_FRACTION - ratio) / se_ratio:.2f} standard errors "
                    f"under the guide.")
            note_parts.append(
                "The annotator timed their own solve while writing the question, "
                "so it understates a fresh solver.")

            points.append({
                "point_id": point_id,
                "task": f"GAIA Level {level} validation question",
                "task_category": "research_analysis",
                "task_description": fit("task_description", desc),
                "model_id": primary_id,
                "compute_scope": "inference",
                "compute_flops": d["flops_per_question"],
                "human_skill": "typical",
                "human_time_scope": "task_performance",
                "human_time": round(d["human_mean_s"], 2),
                "performance_vs_human": "below",
                "comparison_issues":
                    "different_inputs_or_tools; different_assessment; "
                    "different_human_baseline; different_attempt_selection",
                "compute_evidence": "derived_assumed_inputs" if any_estimated
                    else "derived_supported_inputs",
                "human_time_evidence": "task_timings",
                "performance_evidence": fit("performance_evidence", perf),
                "human_time_statistic": "mean",
                "human_time_subset": "all",
                "human_attempts": d["n_questions"],
                "human_time_source": fit("human_time_source", HUMAN_TIME_SOURCE),
                "human_time_method": "other_calculation",
                "compute_method": "params_tokens",
                "compute_statistic": "mean",
                "compute_subset": "positive_tokens"
                    if d["n_missing_usage"] else "all",
                "ai_attempts": d["n_with_usage"],
                "compute_source": fit("compute_source",
                    f"research/gaia.md#{point_id}; research/gaia/calculations.json; "
                    f"agent-work/sources/gaia/hal-run-summaries/{rid}.json"),
                "tokens": d["counted_tokens_per_question"],
                "tokens_accounting": "input_cache_creation_output"
                    if cached_total else "input_output",
                "source_dataset": "GAIA, HAL agent traces",
                "source_record": fit("source_record", src),
                "notes": fit("notes", " ".join(note_parts)),
                # Cost columns, per the 2026-09-13 ruling in DECISIONS.md.
                # Observed only: the token counts are measured and the rates come
                # from the shared list-price table at the run date.
                "ai_cost_usd": cost if cost else "",
                "ai_cost_basis": "list_price" if cost else "not_available",
                "ai_cost_date": run["date"] if cost else "",
                # GAIA reports no payment to its annotators and no price for
                # their work.
                "human_cost_usd": "",
                "human_cost_basis": "not_available",
            })

    with open(os.path.join(out_dir, "points.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=POINT_COLUMNS)
        w.writeheader()
        w.writerows(points)

    missing = sorted(m for m in used_model_ids if m and m not in models)
    if missing:
        raise SystemExit(f"model ids not in any registry: {missing}")
    # Only records the canonical root registry does not already carry.
    model_rows = [models[m] for m in sorted(used_model_ids)
                  if m in models and m not in canonical]
    with open(os.path.join(out_dir, "models.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MODEL_COLUMNS)
        w.writeheader()
        w.writerows([{k: r.get(k, "") for k in MODEL_COLUMNS} for r in model_rows])

    with open(os.path.join(out_dir, "dispositions.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "run_id", "level", "n_questions", "accuracy", "human_score",
            "ratio_to_human", "se_of_ratio", "standard_errors_below_guide",
            "outcome", "reason"])
        w.writeheader()
        w.writerows(dispositions)

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "calculations.json"), "w") as fh:
        json.dump({
            "human_time_statistics": stats,
            "human_score_by_level": HUMAN_SCORE,
            "keep_fraction": KEEP_FRACTION,
            "attention_shapes": {k: list(v) for k, v in ATTENTION_SHAPE.items()},
            "points": calcs,
        }, fh, indent=1)

    print(f"{len(points)} rows, {len(dispositions)} dispositions, "
          f"{len(model_rows)} models")


if __name__ == "__main__":
    if len(sys.argv) != 6:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
