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
    parser.add_argument("--test-fraction", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if not 0 < args.validation_fraction < 1:
        raise ValueError("--validation-fraction must be between 0 and 1")
    if not 0 < args.test_fraction < 1:
        raise ValueError("--test-fraction must be between 0 and 1")
    if args.validation_fraction + args.test_fraction >= 1:
        raise ValueError("validation and test fractions must sum to less than 1")
    unique = {}
    protocols = Counter()
    for line_number, line in enumerate(args.input.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        record = json.loads(line)
        metadata = record.get("metadata", {})
        if metadata.get("reviewed") is not True or metadata.get("approved") is not True:
            raise ValueError(f"Unapproved record at line {line_number}; run promote_reviewed.py first")
        messages = record.get("messages")
        if not isinstance(messages, list) or [m.get("role") for m in messages] != ["system", "user", "assistant"]:
            raise ValueError(f"Invalid messages at line {line_number}")
        json.loads(messages[-1]["content"])
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
    # Stratify by protocol. Every protocol must occur in all three partitions.
    buckets = {}
    for record in records:
        meta = record.get("metadata", {})
        buckets.setdefault(meta.get("protocol", "unknown"), []).append(record)
    train, validation, test = [], [], []
    for protocol, bucket in buckets.items():
        if len(bucket) < 3:
            raise ValueError(f"Protocol {protocol!r} has {len(bucket)} records; at least 3 are required for train/validation/test")
        bucket.sort(key=lambda r: hashlib.sha256(json.dumps(r, sort_keys=True).encode()).hexdigest())
        validation_take = max(1, round(len(bucket) * args.validation_fraction))
        test_take = max(1, round(len(bucket) * args.test_fraction))
        while validation_take + test_take >= len(bucket):
            if validation_take >= test_take and validation_take > 1:
                validation_take -= 1
            elif test_take > 1:
                test_take -= 1
            else:
                raise ValueError(f"Protocol {protocol!r} cannot be split into non-empty train/validation/test partitions")
        validation.extend(bucket[:validation_take])
        test.extend(bucket[validation_take:validation_take + test_take])
        train.extend(bucket[validation_take + test_take:])
    if not train:
        raise ValueError("Split produced no training records; reduce validation/test fractions")
    tasks = {record.get("metadata", {}).get("task") for record in records}
    all_protocols = {record.get("metadata", {}).get("protocol", "unknown") for record in records}
    for subset_name, subset in (("train", train), ("validation", validation), ("test", test)):
        missing_protocols = all_protocols - {record.get("metadata", {}).get("protocol", "unknown") for record in subset}
        if missing_protocols:
            raise ValueError(f"{subset_name} split is missing protocol(s): {sorted(missing_protocols)}")
        missing = tasks - {record.get("metadata", {}).get("task") for record in subset}
        if missing:
            raise ValueError(f"{subset_name} split is missing task(s): {sorted(missing)}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, subset in (("train", train), ("validation", validation), ("test", test)):
        with (args.output_dir / f"{name}.jsonl").open("w", encoding="utf-8") as handle:
            for record in subset:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    summary = {"input": sum(protocols.values()), "deduplicated": len(records), "train": len(train), "validation": len(validation), "test": len(test), "protocols": protocols, "validation_protocols": Counter(r.get("metadata", {}).get("protocol", "unknown") for r in validation), "test_protocols": Counter(r.get("metadata", {}).get("protocol", "unknown") for r in test), "validation_tasks": Counter(r.get("metadata", {}).get("task", "unknown") for r in validation), "test_tasks": Counter(r.get("metadata", {}).get("task", "unknown") for r in test)}
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
