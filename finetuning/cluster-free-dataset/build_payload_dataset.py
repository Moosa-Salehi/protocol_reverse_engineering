#!/usr/bin/env python3
"""Build SFT records without protocol-family clustering.

Annotations are supplied per message (or small local batch) and must already
be reviewed. Messages are grouped only by observable length/direction/session;
no learned family ID is required.
"""
from __future__ import annotations
import argparse, json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROLE_SET = {"address","bitfield","byte_count","checksum","constant","correlation_id","counter","crc","data","device_id","discriminator","error_code","flags","function_code","length","opcode","padding","payload","quantity","reserved","sequence_number","status","timestamp","transaction_id","unit_id","value"}

def load_messages(path: Path) -> dict[int, dict[str, Any]]:
    out = {}
    with path.open(encoding="utf-8") as h:
        for line in h:
            if line.strip():
                row = json.loads(line); out[int(row["msg_id"])] = row
    return out

def load_annotations(path: Path) -> dict[int, dict[str, Any]]:
    raw = None
    if path.suffix == ".json":
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            raw = None  # tolerate JSONL content with a .json suffix
    if raw is not None:
        raw = raw.get("annotations", raw) if isinstance(raw, dict) else raw
        if isinstance(raw, dict): return {int(k): v for k, v in raw.items()}
        if isinstance(raw, list): return {int(x["msg_id"]): x for x in raw}
    out = {}
    with path.open(encoding="utf-8") as h:
        for line in h:
            if line.strip():
                row = json.loads(line); out[int(row["msg_id"])] = row
    return out

def validate(a: dict[str, Any], length: int) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    boundary = a.get("boundary_refinement") or a.get("boundaries")
    semantic = a.get("semantic_labeling") or a.get("semantic_labels")
    bt = None
    if boundary is not None:
        vals = boundary.get("boundaries", boundary) if isinstance(boundary, dict) else boundary
        vals = sorted({int(x) for x in vals})
        if any(x < 0 or x > length for x in vals): raise ValueError("boundary outside payload")
        bt = {"boundaries": vals}
    st = None
    if semantic is not None:
        vals = semantic.get("semantic_labels", semantic) if isinstance(semantic, dict) else semantic
        labels = []
        for x in vals:
            role = x.get("semantic_role")
            if role not in ROLE_SET: raise ValueError(f"invalid semantic_role: {role!r}")
            off, width = int(x["offset"]), int(x["width"])
            if off < 0 or width < 1 or off + width > length: raise ValueError("semantic field outside payload")
            labels.append({"offset": off, "width": width, "semantic_role": role, "field_type": x.get("field_type", "bytes")})
        st = {"semantic_labels": labels}
    return bt, st

def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("messages", type=Path); p.add_argument("annotations", type=Path); p.add_argument("output", type=Path)
    p.add_argument("--protocol", required=True); p.add_argument("--batch-size", type=int, default=8); p.add_argument("--tasks", nargs="+", choices=["boundary_refinement","semantic_labeling"], default=["boundary_refinement","semantic_labeling"])
    p.add_argument("--include-empty-semantic", action="store_true", help="Keep semantic targets with no labels (disabled by default).")
    p.add_argument("--max-prompt-chars", type=int, default=12000, help="Reject prompts longer than this limit.")
    args = p.parse_args()
    if args.batch_size < 1: p.error("--batch-size must be >= 1")
    if args.max_prompt_chars < 1: p.error("--max-prompt-chars must be >= 1")
    messages, annotations = load_messages(args.messages), load_annotations(args.annotations)
    groups = defaultdict(list)
    for mid, ann in annotations.items():
        msg = messages.get(mid)
        if msg: groups[(msg.get("direction", "unknown"), int(msg.get("payload_len", len(msg.get("payload_hex", "")) // 2)))].append((mid, msg, ann))
    system = "You are an expert Protocol Reverse Engineering Analyst. Return one JSON object and no Markdown fences."
    rows = []; skipped = 0
    for group, items in groups.items():
        for start in range(0, len(items), args.batch_size):
            batch = items[start:start + args.batch_size]
            for task in args.tasks:
                targets = []
                for mid, msg, ann in batch:
                    bt, st = validate(ann, int(msg.get("payload_len", 0)))
                    target = bt if task == "boundary_refinement" else st
                    if target is not None: targets.append((mid, target))
                if task == "semantic_labeling" and not args.include_empty_semantic:
                    targets = [(mid, target) for mid, target in targets if target.get("semantic_labels")]
                if not targets: skipped += 1; continue
                # One target per message keeps supervision unambiguous.
                for mid, target in targets:
                    target_msg = messages[mid]
                    target_evidence = [{"msg_id": mid, "direction": target_msg.get("direction"), "payload_len": target_msg.get("payload_len"), "payload_hex": target_msg.get("payload_hex")}]
                    prompt = ("### TASK: " + task + "\n\nAnalyze the payload evidence and return the requested JSON.\n\n## Evidence Bundle\n\n```json\n" + json.dumps({"messages": target_evidence}, separators=(",", ":")) + "\n```\n")
                    if len(prompt) > args.max_prompt_chars:
                        raise ValueError(f"prompt for message {mid} is {len(prompt)} characters; reduce payload evidence")
                    rows.append({"messages":[{"role":"system","content":system},{"role":"user","content":prompt},{"role":"assistant","content":json.dumps(target,separators=(",", ":"))}],"metadata":{"task":task,"protocol":args.protocol,"message_id":mid,"evidence_level":"single_message","reviewed":bool(annotations[mid].get("reviewed", False)),"approved":bool(annotations[mid].get("approved", False)),"reviewer":annotations[mid].get("reviewer")}})
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text("\n".join(json.dumps(x) for x in rows) + ("\n" if rows else ""), encoding="utf-8")
    print(json.dumps({"written":len(rows),"skipped_task_batches":skipped,"groups":len(groups),"output":str(args.output)}, indent=2))

if __name__ == "__main__": main()
