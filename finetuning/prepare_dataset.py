#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
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
        metadata = record.get("metadata", {})
        # Keep distinct tasks/targets even when they share the same evidence prompt.
        dedup_key = json.dumps(
            {"prompt": messages[1]["content"], "task": metadata.get("task"), "target": messages[-1]["content"]},
            sort_keys=True,
            ensure_ascii=False,
        )
        digest = hashlib.sha256(dedup_key.encode("utf-8")).hexdigest()
        unique[digest] = record
        protocols[record.get("metadata", {}).get("protocol", "unknown")] += 1
    records = list(unique.values())
    if not records:
        raise ValueError("Input contains no valid records")
    # Stable group split prevents the same protocol/family appearing in both sets.
    train, validation = [], []
    for record in records:
        meta = record.get("metadata", {})
        group = f"{meta.get('protocol','unknown')}:{meta.get('family_id','unknown')}"
        fraction = int(hashlib.sha256(f"{args.seed}:{group}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
        (validation if fraction < args.validation_fraction else train).append(record)
    if not validation and len(train) > 1:
        validation.append(train.pop())
    if not train:
        raise ValueError("Split produced no training records; reduce --validation-fraction")
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
