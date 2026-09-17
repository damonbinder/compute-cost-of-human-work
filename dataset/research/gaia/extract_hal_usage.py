#!/usr/bin/env python3
"""Reduce one decrypted HAL run JSON to a compact per-task usage summary.

Input: a decrypted HAL upload JSON (see decrypt_hal_zip.py) with keys
config, results, raw_eval_results, raw_logging_results, total_usage, total_cost.
Output: a small JSON with the run config, the per-task score, and, for every
GAIA task id, the per-model token counters summed over that task's LLM calls.

DE-DUPLICATION. HAL logs a call routed through weave's OpenAI-client patch
twice: once as a ``litellm.completion`` parent span and once as its
``openai.chat.completions.create`` child, both carrying the identical usage
block. HAL's own ``total_usage`` and ``total_cost`` sum both, so they are doubled
for every such call and cannot be used as a check. This reduction counts a span
only when no usage-bearing span names it as parent, which keeps the leaf record
of every call exactly once: Anthropic-native and OpenRouter records are leaves
and are untouched, and the OpenAI, Together and Gemini parents are dropped.
``span_breakdown`` in the output reports, per op name, how many spans were seen,
how many carried usage, and how many were dropped as usage-bearing parents.

Token counters retained, per provider convention:
  OpenAI   prompt_tokens (INCLUDES prompt_tokens_details.cached_tokens),
           completion_tokens (INCLUDES completion_tokens_details.reasoning_tokens),
           cached_tokens, reasoning_tokens
  Anthropic prompt_tokens, completion_tokens,
           cache_creation_input_tokens, cache_read_input_tokens (additive)
OpenRouter returns null for both details blocks, so its cached_tokens are absent
rather than measured; ``details_present`` records how many usage blocks carried
each details block, so a reader can tell a measured zero from a missing counter.
The dataset's counted quantity is derived downstream, not here.

Streams with ijson so multi-GB runs do not have to be held in memory; only the
per-span identity and usage are retained, which is a few MB at most.
Dependencies: ijson.

Usage:
    python3 extract_hal_usage.py <decrypted_run.json> <out_summary.json>
"""
import json
import sys
from collections import defaultdict
from decimal import Decimal

import ijson

USAGE_FIELDS = (
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "requests",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
    "input_tokens",
    "output_tokens",
)


def _first(path, key):
    with open(path, "rb") as fh:
        for item in ijson.items(fh, key):
            return item
    return None


def _json_default(o):
    if isinstance(o, Decimal):
        return float(o)
    raise TypeError(f"not serializable: {type(o)}")


def _num(x):
    if x is None:
        return 0
    try:
        return int(x)
    except (TypeError, ValueError):
        return 0


def _accumulate(acc, u):
    for f in USAGE_FIELDS:
        if f in u:
            acc[f] += _num(u.get(f))
    pd = u.get("prompt_tokens_details")
    cd = u.get("completion_tokens_details")
    acc["cached_tokens"] += _num((pd or {}).get("cached_tokens"))
    acc["reasoning_tokens"] += _num((cd or {}).get("reasoning_tokens"))
    acc["prompt_tokens_details_present"] += 1 if isinstance(pd, dict) else 0
    acc["completion_tokens_details_present"] += 1 if isinstance(cd, dict) else 0
    acc["calls"] += 1


def extract(path, out_path):
    summary = {
        "config": _first(path, "config"),
        "total_usage": _first(path, "total_usage"),
        "total_cost": _first(path, "total_cost"),
        "results": _first(path, "results"),
        "raw_eval_results": _first(path, "raw_eval_results"),
        "git_info": _first(path, "git_info"),
    }

    # Pass 1: keep only span identity and usage, so memory stays small.
    spans = []
    parents_with_usage_child = set()
    calls = calls_no_usage = calls_no_task = exceptions = 0
    with open(path, "rb") as fh:
        for call in ijson.items(fh, "raw_logging_results.item"):
            calls += 1
            if call.get("exception"):
                exceptions += 1
            usage = ((call.get("summary") or {}).get("usage")) or {}
            op = (call.get("op_name") or "").rsplit("/op/", 1)[-1].split(":", 1)[0]
            if not usage:
                calls_no_usage += 1
                spans.append((call.get("id"), op, None, None))
                continue
            task = call.get("weave_task_id") or (call.get("attributes") or {}).get(
                "weave_task_id"
            )
            if not task:
                calls_no_task += 1
                task = "__no_task_id__"
            parent = call.get("parent_id")
            if parent:
                parents_with_usage_child.add(parent)
            spans.append((call.get("id"), op, task, usage))

    # Pass 2: a span counts only when nothing usage-bearing names it as parent.
    per_task = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    gross = defaultdict(lambda: defaultdict(int))
    by_op = defaultdict(lambda: defaultdict(int))
    counted = dropped = 0
    for span_id, op, task, usage in spans:
        by_op[op]["spans"] += 1
        if usage is None:
            continue
        by_op[op]["with_usage"] += 1
        for model, u in usage.items():
            if isinstance(u, dict):
                gross[model]["prompt_tokens"] += _num(u.get("prompt_tokens"))
                gross[model]["completion_tokens"] += _num(u.get("completion_tokens"))
        if span_id in parents_with_usage_child:
            by_op[op]["dropped_as_parent"] += 1
            dropped += 1
            continue
        by_op[op]["counted"] += 1
        counted += 1
        for model, u in usage.items():
            if isinstance(u, dict):
                _accumulate(per_task[task][model], u)

    summary["per_task_usage"] = {
        t: {m: dict(v) for m, v in models.items()} for t, models in per_task.items()
    }
    summary["call_counts"] = {
        "calls": calls,
        "calls_without_usage": calls_no_usage,
        "calls_without_task_id": calls_no_task,
        "calls_with_exception": exceptions,
        "tasks_with_usage": len(per_task),
        "usage_spans_counted": counted,
        "usage_spans_dropped_as_parent": dropped,
    }
    summary["span_breakdown"] = {
        "by_op_name": {k: dict(v) for k, v in sorted(by_op.items())},
        "gross_undeduplicated_by_model": {k: dict(v) for k, v in gross.items()},
    }
    with open(out_path, "w") as fh:
        json.dump(summary, fh, default=_json_default)
    return summary["call_counts"]


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    print(json.dumps(extract(sys.argv[1], sys.argv[2])))
