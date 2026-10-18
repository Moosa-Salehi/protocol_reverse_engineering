#!/usr/bin/env python3
"""Stage 07c: write the few-shot per-message edges (stage 04b) into the families.

Each family's fields become the edges present in at least half of its messages; stage-07 field records are kept
where a field is unchanged or split, and families with TLV-tagged element fields keep that chain (only the prefix
before it is rebuilt). The stage-07 original is kept as 05_families.pre-fewshot.json.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from protocol_re.inference import fewshot_boundaries as fsb  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("messages_jsonl", type=Path)
    parser.add_argument("assignments_json", type=Path)
    parser.add_argument("fewshot_json", type=Path)
    parser.add_argument("families_json", type=Path)
    parser.add_argument("--gate", action="store_true",
                        help="Keep stage-07 fields; predicted edges only split fields of >= 3 bytes and extend past the last field")
    args = parser.parse_args()
    edges = {int(m): set(e) for m, e in json.loads(args.fewshot_json.read_text(encoding="utf-8"))["edges"].items()}
    family_of = {int(a["msg_id"]): a["family_id"] for a in json.loads(args.assignments_json.read_text(encoding="utf-8"))["assignments"]}
    payload_len = {}
    for line in args.messages_jsonl.open(encoding="utf-8"):
        if line.strip():
            m = json.loads(line)
            payload_len[int(m["msg_id"])] = int(m["payload_len"])
    families = json.loads(args.families_json.read_text(encoding="utf-8"))
    shutil.copy(args.families_json, args.families_json.with_name("05_families.pre-fewshot.json"))
    if args.gate:
        summary = fsb.apply_gated(families, family_of, edges, payload_len)
    else:
        summary = fsb.apply_to_families(families, family_of, edges, payload_len)
    args.families_json.write_text(json.dumps(families, indent=2), encoding="utf-8")
    print(f"[+] few-shot edges applied: {summary}")


if __name__ == "__main__":
    main()
