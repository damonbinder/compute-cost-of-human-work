#!/usr/bin/env python3
"""Scan the published GPT-6 Astra Portal session log and emit the counts used by
research/portal-astra.md.

Input is `evidence/session.sanitized.jsonl` from a clone of
https://github.com/cozyblaze/portal-agent (commit 31311b8fde8f242cc403bd51d45cb615ed645e4b).
The 2.9 MB log is not redistributed here; this script regenerates the retained
scan from it.

Two subtleties the independent review identified, both handled below:

  * Deferred results. A `portal_exec` cell that outruns its turn returns
    "Script running with cell ID N"; the agent then issues a `wait` tool call
    carrying `{"cell_id": "N"}`, and the screenshot arrives in the wait's result.
    Classifying by the wait's own input would call every such image a default
    360p capture. Images are instead attributed to the originating cell.
  * Text echoes of an image block. A cell that prints an MCP result before
    emitting its images (`text({result: r.value})` then `image(c)`) puts the
    literal string `image_omitted` into a text payload as well as a structured
    image block. Only structured blocks are counted as images; the echoes are
    reported separately because the exporter's own `removed_images` includes
    them.

Dependencies: Python 3.9+ standard library. `tiktoken` is optional; when it is
importable the scan also records o200k_base token counts for the log's text
payloads, which are used only as a corroborating decomposition, never as the
headline workload.

Usage:
  python3 scan_session.py --session /path/to/session.sanitized.jsonl \
                          --out /path/to/sources/portal-astra/session-scan.json
"""
import argparse
import collections
import json
import re

FULL_RES = re.compile(r"fullRes\s*:\s*true")
AIM_DEF = re.compile(r"portalAimPixel\s*=\s*async function\([^)]*\)\{(.{0,200})", re.S)
AIM_CALL = re.compile(r"portalAimPixel\((\d+)\s*,\s*(\d+)\)")
# The agent's own screen-to-world helper divides by the image centre; the
# principal point it uses is the only published statement of the screenshot size.
PRINCIPAL = re.compile(r"\(px-(\d+)\)/(\d+)[^;]*?\((\d+)-py\)/(\d+)")
TICKS = re.compile(r'"ticks"\s*:\s*(\d+)')
CELL_ID_ANNOUNCED = re.compile(r"Script running with cell ID (\d+)")
CELL_ID_REQUESTED = re.compile(r'"cell_id"\s*:\s*"?(\d+)"?')


def text_blocks(record):
    """Text payloads of one tool result.

    Output chunks are usually {"type": "input_text", "text": ...} dicts, but a
    deferred result streams its text as bare single-character strings; those are
    joined so the "cell ID N" announcement is readable.
    """
    loose = []
    for chunk in record.get("output") or []:
        if isinstance(chunk, dict) and isinstance(chunk.get("text"), str):
            yield chunk["text"]
        elif isinstance(chunk, str):
            loose.append(chunk)
    if loose:
        yield "".join(loose)


def count_images(record):
    """Structured image blocks, and separately the text echoes of one."""
    structured = 0
    echoed = 0
    for chunk in record.get("output") or []:
        if isinstance(chunk, dict):
            if chunk.get("type") == "image_omitted":
                structured += 1
            if isinstance(chunk.get("text"), str):
                echoed += chunk["text"].count("image_omitted")
    return structured, echoed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    with open(args.session, encoding="utf-8") as handle:
        records = [json.loads(line) for line in handle if line.strip()]

    calls = {r["call"]: r for r in records if r["kind"] == "tool_call" and "call" in r}
    results = {r["call"]: r for r in records if r["kind"] == "tool_result" and "call" in r}

    # cell id -> the exec call that announced it, for resolving deferred results
    cell_owner = {}
    for call_id, result in results.items():
        for block in text_blocks(result):
            for cell in CELL_ID_ANNOUNCED.findall(block):
                cell_owner.setdefault(cell, call_id)

    kinds = collections.Counter(r["kind"] for r in records)
    tool_names = collections.Counter(r.get("name") for r in records if r["kind"] == "tool_call")
    roles = collections.Counter(r.get("role") for r in records if r["kind"] == "message")

    images = collections.Counter()
    images_per_result = collections.Counter()
    echoes = 0
    deferred = []
    unresolved_deferred = []
    for record in records:
        if record["kind"] != "tool_result":
            continue
        n, echoed = count_images(record)
        echoes += echoed
        images_per_result[n] += 1
        if n == 0:
            continue
        call = calls.get(record.get("call"), {})
        source = call.get("input") or ""
        attributed_to = record.get("call")
        if call.get("name") == "wait":
            cell = CELL_ID_REQUESTED.search(source)
            owner = cell_owner.get(cell.group(1)) if cell else None
            if owner:
                attributed_to = owner
                source = calls.get(owner, {}).get("input") or ""
                deferred.append({"wait_call": record.get("call"), "cell_id": cell.group(1),
                                 "originating_call": owner, "images": n})
            else:
                unresolved_deferred.append({"wait_call": record.get("call"), "images": n})
        # portal_screenshot is documented as capturing at full resolution.
        if FULL_RES.search(source) or "portal_screenshot" in source:
            images["full_res"] += n
        else:
            images["default_360p"] += n

    principal_points = sorted({tuple(int(g) for g in m) for m in PRINCIPAL.findall(
        "\n".join([c.get("input") or "" for c in calls.values()]))})
    aim_defs = len(AIM_DEF.findall("\n".join([c.get("input") or "" for c in calls.values()])))
    aim_calls = [(int(x), int(y)) for c in calls.values()
                 for x, y in AIM_CALL.findall(c.get("input") or "")]

    ticks = [int(t) for r in records if r["kind"] == "tool_result"
             for block in text_blocks(r) for t in TICKS.findall(block)]
    results_with_ticks = sum(1 for r in records if r["kind"] == "tool_result"
                             and any(TICKS.search(b) for b in text_blocks(r)))

    chars = collections.Counter()
    for record in records:
        if record["kind"] == "tool_call":
            chars["tool_call_input"] += len(record.get("input") or "")
        elif record["kind"] == "message":
            chars["message_" + str(record.get("role"))] += len(record.get("text") or "")
        elif record["kind"] == "tool_result":
            for block in text_blocks(record):
                chars["tool_result_text"] += len(block)

    tokens = None
    try:
        import tiktoken
        enc = tiktoken.get_encoding("o200k_base")

        def count(s):
            return len(enc.encode(s, disallowed_special=()))

        tokens = collections.Counter()
        for record in records:
            if record["kind"] == "tool_call":
                tokens["tool_call_input"] += count(record.get("input") or "")
            elif record["kind"] == "message":
                tokens["message_" + str(record.get("role"))] += count(record.get("text") or "")
            elif record["kind"] == "tool_result":
                for block in text_blocks(record):
                    tokens["tool_result_text"] += count(block)
        tokens = dict(tokens)
    except ImportError:
        pass

    scan = {
        "source": {
            "repository": "https://github.com/cozyblaze/portal-agent",
            "commit": "31311b8fde8f242cc403bd51d45cb615ed645e4b",
            "file": "evidence/session.sanitized.jsonl",
        },
        "records": len(records),
        "records_by_kind": dict(kinds),
        "tool_calls_by_name": dict(tool_names),
        "messages_by_role": dict(roles),
        "images_total": sum(images.values()),
        "images_by_resolution_request": dict(images),
        "images_per_tool_result": {str(k): v for k, v in sorted(images_per_result.items())},
        "image_text_echoes": echoes,
        "images_plus_echoes": sum(images.values()) + echoes,
        "deferred_results_resolved": deferred,
        "deferred_results_unresolved": unresolved_deferred,
        "aim_pixel_helper_definitions": aim_defs,
        "aim_pixel_principal_points": [
            {"centre_x": p[0], "u_divisor": p[1], "centre_y": p[2], "v_divisor": p[3]}
            for p in principal_points
        ],
        "aim_pixel_calls": len(aim_calls),
        "aim_pixel_x_range": [min(x for x, _ in aim_calls), max(x for x, _ in aim_calls)] if aim_calls else None,
        "aim_pixel_y_range": [min(y for _, y in aim_calls), max(y for _, y in aim_calls)] if aim_calls else None,
        "tick_readings": len(ticks),
        "tool_results_with_a_tick_reading": results_with_ticks,
        "tick_sum": sum(ticks),
        "characters": dict(chars),
        "o200k_base_tokens": tokens,
        "first_record": records[0],
        "last_record": records[-1],
    }

    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(scan, handle, indent=1, ensure_ascii=False)
        handle.write("\n")
    print("wrote", args.out)


if __name__ == "__main__":
    main()
