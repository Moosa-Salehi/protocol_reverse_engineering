#!/usr/bin/env python3
"""Select a small, tokenizer-safe, high-quality fine-tuning subset."""
from __future__ import annotations
import argparse, json, random
from collections import Counter, defaultdict
from pathlib import Path

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("data_root", type=Path); p.add_argument("output", type=Path)
    p.add_argument("--tokenizer", required=True); p.add_argument("--count", type=int, default=1000)
    p.add_argument("--max-tokens", type=int, default=4096); p.add_argument("--max-boundaries", type=int, default=32)
    p.add_argument("--preferred-payload-length", type=int, default=50); p.add_argument("--seed", type=int, default=42)
    a = p.parse_args()
    if a.count < 1 or a.max_tokens < 1 or a.max_boundaries < 2: p.error("invalid limits")
    try:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(a.tokenizer)
    except Exception as exc:
        raise SystemExit(f"Tokenizer unavailable: {exc}")
    excluded = {"raw.jsonl", "curated_1000.jsonl"}
    rows = []
    rejected = Counter()
    for path in sorted(a.data_root.glob("*.jsonl")):
        if path.name in excluded: continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip(): continue
            try:
                row = json.loads(line); meta = row["metadata"]; msgs = row["messages"]; target = json.loads(msgs[-1]["content"])
                rendered = tok.apply_chat_template(msgs[:-1], tokenize=False, add_generation_prompt=True)
                prompt_tokens = len(tok(rendered, add_special_tokens=False)["input_ids"])
                if prompt_tokens > a.max_tokens: rejected["prompt_tokens"] += 1; continue
                boundaries = target.get("boundaries", [])
                payload_len = int(row.get("metadata", {}).get("payload_len", 0) or 0)
                evidence = json.loads(msgs[1]["content"].split("```json\n", 1)[1].rsplit("\n```", 1)[0])
                payload_len = int(evidence["messages"][0]["payload_len"])
                if len(boundaries) > a.max_boundaries: rejected["dense_boundaries"] += 1; continue
                if boundaries and (boundaries[0] != 0 or boundaries[-1] != payload_len): rejected["boundary_endpoints"] += 1; continue
                if meta.get("task") == "semantic_labeling":
                    labels = target.get("semantic_labels", [])
                    if not labels: rejected["empty_semantics"] += 1; continue
                    if min(int(x["offset"]) for x in labels) != 0 or max(int(x["offset"]) + int(x["width"]) for x in labels) != payload_len:
                        rejected["incomplete_semantics"] += 1; continue
                semantic_score = len(target.get("semantic_labels", []))
                short_score = 1 if payload_len < a.preferred_payload_length else 0
                rows.append((short_score, semantic_score, prompt_tokens, row))
            except (KeyError, ValueError, IndexError, json.JSONDecodeError):
                rejected["malformed"] += 1
    rng = random.Random(a.seed)
    rng.shuffle(rows)
    rows.sort(key=lambda x: (-x[0], -x[1], x[2]))
    # Keep both tasks represented whenever possible, then fill by quality score.
    chosen = []
    for task in ("boundary_refinement", "semantic_labeling"):
        pool = [x for x in rows if x[3]["metadata"].get("task") == task]
        chosen.extend(pool[: a.count // 2])
    chosen_ids = {id(x[3]) for x in chosen}
    chosen.extend(x for x in rows if id(x[3]) not in chosen_ids)
    chosen = chosen[:a.count]
    if len(chosen) < a.count: rejected["insufficient_candidates"] = a.count - len(chosen)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text("\n".join(json.dumps(x[3], ensure_ascii=False) for x in chosen) + ("\n" if chosen else ""), encoding="utf-8")
    report = {"selected": len(chosen), "requested": a.count, "candidates": len(rows), "rejected": rejected, "tasks": Counter(x[3]["metadata"].get("task") for x in chosen), "protocols": Counter(x[3]["metadata"].get("protocol") for x in chosen), "max_prompt_tokens": max((x[2] for x in chosen), default=0), "max_boundaries": max((len(json.loads(x[3]["messages"][-1]["content"]).get("boundaries", [])) for x in chosen), default=0)}
    a.output.with_name(a.output.stem + "_summary.json").write_text(json.dumps(report, indent=2, default=dict), encoding="utf-8")
    print(json.dumps(report, indent=2, default=dict))

if __name__ == "__main__": main()
