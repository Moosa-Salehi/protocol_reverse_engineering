#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate, deduplicate, and split chat JSONL data.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--validation-fraction", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    unique = {}
    protocols = Counter()
    for line_number, line in enumerate(args.input.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        record = json.loads(line)
        messages = record.get("messages")
        if not isinstance(messages, list) or [m.get("role") for m in messages] != ["system", "user", "assistant"]:
            raise ValueError(f"Invalid messages at line {line_number}")
        json.loads(messages[-1]["content"])
        digest = hashlib.sha256(messages[1]["content"].encode("utf-8")).hexdigest()
        unique[digest] = record
        protocols[record.get("metadata", {}).get("protocol", "unknown")] += 1
    records = list(unique.values())
    random.Random(args.seed).shuffle(records)
    validation_count = max(1, round(len(records) * args.validation_fraction)) if len(records) > 1 else 0
    validation, train = records[:validation_count], records[validation_count:]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, subset in (("train", train), ("validation", validation)):
        with (args.output_dir / f"{name}.jsonl").open("w", encoding="utf-8") as handle:
            for record in subset:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    summary = {"input": sum(protocols.values()), "deduplicated": len(records), "train": len(train), "validation": len(validation), "protocols": protocols}
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

