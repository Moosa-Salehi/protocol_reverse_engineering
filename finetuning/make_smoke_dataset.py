#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def select(source: Path, destination: Path, limit: int) -> int:
    records = []
    seen_tasks = set()
    for line in source.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        task = record.get("metadata", {}).get("task", "unknown")
        if task not in seen_tasks or len(records) < limit:
            records.append(record)
            seen_tasks.add(task)
        if len(records) >= limit and {"boundary_refinement", "semantic_labeling"}.issubset(seen_tasks):
            break
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create deterministic, task-covering smoke-test subsets.")
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--train-limit", type=int, default=8)
    parser.add_argument("--validation-limit", type=int, default=4)
    args = parser.parse_args()
    train_count = select(args.train, args.output_dir / "train.jsonl", args.train_limit)
    validation_count = select(args.validation, args.output_dir / "validation.jsonl", args.validation_limit)
    if train_count < 2 or validation_count < 1:
        raise RuntimeError("Dataset is too small for a meaningful smoke test")
    print(json.dumps({"train": train_count, "validation": validation_count}, indent=2))


if __name__ == "__main__":
    main()

