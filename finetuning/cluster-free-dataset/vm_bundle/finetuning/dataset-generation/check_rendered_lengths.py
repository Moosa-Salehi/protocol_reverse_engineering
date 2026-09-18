#!/usr/bin/env python3
"""Check complete chat-rendered JSONL conversations against a token limit."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


def stats(values: list[int]) -> dict[str, float | int]:
    if not values:
        return {"count": 0, "min": 0, "max": 0, "mean": 0, "p95": 0}
    ordered = sorted(values)
    return {
        "count": len(values),
        "min": ordered[0],
        "max": ordered[-1],
        "mean": round(sum(values) / len(values), 2),
        "p95": ordered[min(len(ordered) - 1, math.ceil(0.95 * len(ordered)) - 1)],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, nargs="+", help="JSONL files to check")
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--max-seq-length", type=int, default=4096)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.max_seq_length < 1:
        parser.error("--max-seq-length must be positive")

    try:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        print(f"Unable to load tokenizer {args.tokenizer!r}: {exc}", file=sys.stderr)
        return 2

    lengths: list[int] = []
    oversized: list[dict[str, object]] = []
    files: dict[str, dict[str, object]] = {}
    for path in args.input:
        file_lengths: list[int] = []
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                messages = row["messages"]
                rendered = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
                token_count = len(tokenizer(rendered, add_special_tokens=False)["input_ids"])
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                print(f"Invalid record {path}:{line_number}: {exc}", file=sys.stderr)
                return 2
            lengths.append(token_count)
            file_lengths.append(token_count)
            if token_count > args.max_seq_length:
                metadata = row.get("metadata", {})
                oversized.append({
                    "file": str(path),
                    "line": line_number,
                    "tokens": token_count,
                    "over_by": token_count - args.max_seq_length,
                    "protocol": metadata.get("protocol"),
                    "task": metadata.get("task"),
                    "family_id": metadata.get("family_id"),
                })
        files[str(path)] = stats(file_lengths)

    report = {
        "tokenizer": args.tokenizer,
        "max_seq_length": args.max_seq_length,
        "records": len(lengths),
        "lengths": stats(lengths),
        "oversized_count": len(oversized),
        "oversized": oversized,
        "files": files,
        "status": "passed" if not oversized else "failed",
    }
    print(json.dumps(report, indent=2))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0 if not oversized else 1


if __name__ == "__main__":
    raise SystemExit(main())
