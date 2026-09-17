#!/usr/bin/env python3
"""Range-read `header.json` and `summaries.json` out of a remote Inspect `.eval` log.

An Inspect `.eval` file is a ZIP.  The two members needed to bin a run are a few megabytes
inside archives that run to 15 GB, so this reads the ZIP end-of-central-directory record from
the tail, locates those two members, and fetches only their compressed bytes.  Members written
by Inspect after early 2026 use compression method 93 (Zstandard), which `zipfile` refuses;
those are inflated with `zstandard`.

Dependencies: Python 3.9+ standard library, `zstandard`, and `curl` on PATH.  Network access
to the log URL is required.

  python3 fetch_log_members.py --url https://.../inspect_ai_logs/<id>.eval --out-dir <dir>

Writes <dir>/header.json and <dir>/summaries.json plus <dir>/fetch.json, which records the
URL, the total object size, the byte ranges read, and the SHA256 of each written file.
"""

import argparse
import hashlib
import json
import os
import struct
import subprocess
import sys
import zlib

WANTED = ("header.json", "summaries.json")


def curl_range(url, start, end):
    """Bytes [start, end] inclusive."""
    cmd = ["curl", "-sS", "--fail", "--max-time", "300", "-H",
           "Range: bytes=%d-%d" % (start, end), url, "--output", "-"]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0:
        raise SystemExit("range read failed: %s" % res.stderr.decode()[:300])
    return res.stdout


def content_length(url):
    res = subprocess.run(["curl", "-sSI", "--fail", "--max-time", "120", url],
                         capture_output=True, text=True)
    if res.returncode != 0:
        raise SystemExit("HEAD failed: %s" % res.stderr[:300])
    for line in res.stdout.splitlines():
        if line.lower().startswith("content-length:"):
            return int(line.split(":", 1)[1].strip())
    raise SystemExit("no content-length for %s" % url)


def central_directory(url, size):
    """Return (entries, ranges_read) where entries maps filename -> dict."""
    ranges = []
    tail_len = min(size, 1 << 16)
    tail = curl_range(url, size - tail_len, size - 1)
    ranges.append([size - tail_len, size - 1])
    idx = tail.rfind(b"PK\x05\x06")
    if idx < 0:
        raise SystemExit("no end-of-central-directory record in the last 64 KiB")
    cd_size, cd_off = struct.unpack("<II", tail[idx + 12:idx + 20])
    if cd_off == 0xFFFFFFFF or cd_size == 0xFFFFFFFF:
        loc = tail.rfind(b"PK\x06\x07")
        if loc < 0:
            raise SystemExit("zip64 locator missing")
        z64_off = struct.unpack("<Q", tail[loc + 8:loc + 16])[0]
        head = curl_range(url, z64_off, z64_off + 55)
        ranges.append([z64_off, z64_off + 55])
        if head[:4] != b"PK\x06\x06":
            raise SystemExit("zip64 end-of-central-directory record missing")
        cd_size, cd_off = struct.unpack("<QQ", head[40:56])
    blob = curl_range(url, cd_off, cd_off + cd_size - 1)
    ranges.append([cd_off, cd_off + cd_size - 1])

    entries, pos = {}, 0
    while pos + 46 <= len(blob):
        if blob[pos:pos + 4] != b"PK\x01\x02":
            break
        method, = struct.unpack("<H", blob[pos + 10:pos + 12])
        csize, usize = struct.unpack("<II", blob[pos + 20:pos + 28])
        n, m, k = struct.unpack("<HHH", blob[pos + 28:pos + 34])
        offset, = struct.unpack("<I", blob[pos + 42:pos + 46])
        name = blob[pos + 46:pos + 46 + n].decode("utf-8", "replace")
        extra = blob[pos + 46 + n:pos + 46 + n + m]
        if 0xFFFFFFFF in (csize, usize, offset):  # zip64 extended information
            e = 0
            while e + 4 <= len(extra):
                tag, ln = struct.unpack("<HH", extra[e:e + 4])
                if tag == 0x0001:
                    vals, v = [], e + 4
                    while v + 8 <= e + 4 + ln:
                        vals.append(struct.unpack("<Q", extra[v:v + 8])[0])
                        v += 8
                    it = iter(vals)
                    if usize == 0xFFFFFFFF:
                        usize = next(it)
                    if csize == 0xFFFFFFFF:
                        csize = next(it)
                    if offset == 0xFFFFFFFF:
                        offset = next(it)
                    break
                e += 4 + ln
        entries[name] = {"method": method, "csize": csize, "usize": usize, "offset": offset}
        pos += 46 + n + m + k
    return entries, ranges


def member_bytes(url, entry, ranges):
    head = curl_range(url, entry["offset"], entry["offset"] + 29)
    ranges.append([entry["offset"], entry["offset"] + 29])
    if head[:4] != b"PK\x03\x04":
        raise SystemExit("bad local file header")
    n, m = struct.unpack("<HH", head[26:30])
    start = entry["offset"] + 30 + n + m
    raw = curl_range(url, start, start + entry["csize"] - 1)
    ranges.append([start, start + entry["csize"] - 1])
    if entry["method"] == 0:
        data = raw
    elif entry["method"] == 8:
        data = zlib.decompress(raw, -zlib.MAX_WBITS)
    elif entry["method"] == 93:
        import zstandard
        data = zstandard.ZstdDecompressor().decompress(
            raw, max_output_size=max(entry["usize"], 1))
    else:
        raise SystemExit("unsupported compression method %d" % entry["method"])
    if entry["usize"] and len(data) != entry["usize"]:
        raise SystemExit("inflated size %d != recorded %d" % (len(data), entry["usize"]))
    return data


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)

    size = content_length(args.url)
    entries, ranges = central_directory(args.url, size)
    record = {"url": args.url, "object_bytes": size, "members": {}, "files": {}}
    for name in WANTED:
        if name not in entries:
            raise SystemExit("%s absent; archive holds %d members" % (name, len(entries)))
        data = member_bytes(args.url, entries[name], ranges)
        path = os.path.join(args.out_dir, name)
        with open(path, "wb") as fh:
            fh.write(data)
        record["members"][name] = entries[name]
        record["files"][name] = {"bytes": len(data),
                                 "sha256": hashlib.sha256(data).hexdigest()}
    record["ranges_read"] = ranges
    record["bytes_read"] = sum(b - a + 1 for a, b in ranges)
    with open(os.path.join(args.out_dir, "fetch.json"), "w") as fh:
        json.dump(record, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("%s -> %s (%.1f MB read of %.2f GB)"
          % (args.url.rsplit("/", 1)[-1], args.out_dir,
             record["bytes_read"] / 1e6, size / 1e9))
    return 0


if __name__ == "__main__":
    sys.exit(main())
