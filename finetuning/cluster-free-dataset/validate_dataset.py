#!/usr/bin/env python3
"""Validate cluster-free SFT JSONL before it is split or trained."""
from __future__ import annotations
import argparse, json, re
from collections import Counter, defaultdict
from pathlib import Path

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("--max-prompt-chars", type=int, default=12000)
    p.add_argument("--allow-empty-semantic", action="store_true")
    args = p.parse_args()
    rows = []
    for n, line in enumerate(args.input.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip(): continue
        row = json.loads(line); meta = row.get("metadata", {}); msgs = row.get("messages")
        if meta.get("reviewed") is not True or meta.get("approved") is not True:
            raise ValueError(f"line {n}: record is not reviewed and approved")
        if not isinstance(msgs, list) or [m.get("role") for m in msgs] != ["system", "user", "assistant"]:
            raise ValueError(f"line {n}: invalid chat message structure")
        if len(msgs[1]["content"]) > args.max_prompt_chars:
            raise ValueError(f"line {n}: prompt exceeds {args.max_prompt_chars} characters")
        target = json.loads(msgs[2]["content"])
        if meta.get("task") == "semantic_labeling" and not args.allow_empty_semantic and not target.get("semantic_labels"):
            raise ValueError(f"line {n}: empty semantic target")
        rows.append(row)
    prompts = defaultdict(set)
    for row in rows: prompts[row["messages"][1]["content"]].add(row["messages"][2]["content"])
    conflicts = sum(len(v) > 1 for v in prompts.values())
    if conflicts: raise ValueError(f"{conflicts} prompts have conflicting targets")
    leaked = sum(bool(re.search(r'"protocol"\s*:', r["messages"][1]["content"])) for r in rows)
    if leaked: raise ValueError(f"{leaked} prompts contain protocol identity")
    print(json.dumps({"records": len(rows), "unique_prompts": len(prompts), "tasks": Counter(r["metadata"].get("task") for r in rows), "status": "passed"}, indent=2))

if __name__ == "__main__": main()
