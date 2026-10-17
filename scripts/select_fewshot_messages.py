#!/usr/bin/env python3
"""List the messages to label for few-shot boundaries (main.py --fewshot-labels).

Strata = (family, log2 payload length), visited round-robin in order of their total bytes, so long messages
(which carry most fields) are covered. Run after stage 04 (e.g. main.py --stop-after 04_discover_families).
Writes JSONL lines {"msg_id", "payload_hex", "family_id"}; add "boundaries" ([0, ..., len], every field edge) to
each line and pass the file as --fewshot-labels.

Usage: select_fewshot_messages.py <01_messages.jsonl> <02_family_assignments.json> <output.jsonl> [--k 50]
       [--only-ids ids.json]   (restrict the candidates, e.g. to messages that can be labelled)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from protocol_re.inference import fewshot_boundaries as fsb  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("messages_jsonl", type=Path)
    parser.add_argument("assignments_json", type=Path)
    parser.add_argument("output_jsonl", type=Path)
    parser.add_argument("--k", type=int, default=50)
    parser.add_argument("--seed", type=int, default=20261017)
    parser.add_argument("--only-ids", type=Path, help="JSON list of candidate msg_ids")
    args = parser.parse_args()
    payload, order = {}, []
    for line in args.messages_jsonl.open(encoding="utf-8"):
        if line.strip():
            m = json.loads(line)
            payload[int(m["msg_id"])] = bytes.fromhex(m["payload_hex"])
            order.append(int(m["msg_id"]))
    family_of = {int(a["msg_id"]): a["family_id"] for a in json.loads(args.assignments_json.read_text(encoding="utf-8"))["assignments"]}
    if args.only_ids:
        allowed = set(json.loads(args.only_ids.read_text()))
        order = [m for m in order if m in allowed]
    chosen = fsb.select_messages(order, family_of, payload, args.k, seed=args.seed)
    with args.output_jsonl.open("w", encoding="utf-8") as fh:
        for m in chosen:
            fh.write(json.dumps({"msg_id": m, "payload_hex": payload[m].hex(), "family_id": family_of.get(m)}) + "\n")
    print(f"[+] {len(chosen)} messages to label -> {args.output_jsonl}")


if __name__ == "__main__":
    main()
