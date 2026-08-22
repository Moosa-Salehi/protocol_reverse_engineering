#!/usr/bin/env python3
"""Build multi-task SFT records from protocol-re evidence artifacts.

No Wireshark field names are treated as labels. Semantic targets must already be
present in reviewed/teacher annotations; boundary targets come from reviewed
field boundaries or an explicitly supplied protocol model.
"""
from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path
from typing import Any

ROLE_SET = {"address","bitfield","byte_count","checksum","constant","correlation_id","counter","crc","data","device_id","discriminator","error_code","flags","function_code","length","opcode","padding","payload","quantity","reserved","sequence_number","status","timestamp","transaction_id","unit_id","value"}

def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def compact(value: Any, limit: int = 16) -> Any:
    if isinstance(value, list): return value[:limit]
    if isinstance(value, dict): return {k: compact(v, limit) for k, v in value.items()}
    return value

def evidence_for_family(family: dict[str, Any], bundle: dict[str, Any] | None) -> dict[str, Any]:
    candidate = next((x for x in (bundle or {}).get("families", []) if str(x.get("family_id")) == str(family.get("family_id"))), {})
    return {
        "family_id": family.get("family_id"),
        "family_role": family.get("role", "unknown"),
        "message_count": family.get("message_count"),
        "fields": compact(family.get("field_hypotheses", [])),
        "field_statistics": compact(candidate.get("field_statistics", {})),
        "sample_values": compact(candidate.get("sample_values", [])),
        "relations": compact(candidate.get("relations", [])),
        "framing": compact(family.get("framing_summary", {})),
    }

def semantic_target(family: dict[str, Any], wireshark: dict[str, Any] | None) -> dict[str, Any] | None:
    labels = []
    ws_fields = (wireshark or {}).get(str(family.get("family_id")), [])
    ws_by_offset = {(int(x.get("offset")), int(x.get("width"))): x for x in ws_fields if x.get("offset") is not None and x.get("width") is not None}
    for index, field in enumerate(family.get("field_hypotheses", []) or []):
        attrs = field.get("attributes", {}) if isinstance(field.get("attributes"), dict) else {}
        offset = int(field.get("start", field.get("offset", 0)))
        width = int(field.get("width", field.get("length", field.get("end", 0) - offset)))
        if width <= 0:
            continue
        ws = ws_by_offset.get((offset, width))
        if not ws: continue
        role = ws.get("semantic_role")
        if role not in ROLE_SET: raise ValueError(f"Wireshark target for {family.get('family_id')} offset {offset} has invalid mapped role {role!r}")
        labels.append({"field_index": index, "offset": offset, "width": width, "field_type": ws.get("field_type", field.get("field_type", "bytes")), "encoding_type": ws.get("encoding_type", ws.get("field_type", field.get("field_type", "bytes"))), "semantic_role": role, "human_label": ws.get("wireshark_name", ws.get("name", role)), "confidence": 1.0, "evidence": ["trusted Wireshark dissector", f"Wireshark field: {ws.get('wireshark_name', ws.get('name', 'unknown'))}"], "alternative_roles": []})
    labeled_indices = {item["field_index"] for item in labels}
    return {"family_id": family.get("family_id"), "family_role": family.get("role", "unknown"), "semantic_labels": labels, "unlabeled_fields": [i for i, _ in enumerate(family.get("field_hypotheses", []) or []) if i not in labeled_indices], "notes": "Target taken from reviewed or teacher-validated pipeline annotations."} if labels else None

def boundary_target(family: dict[str, Any], wireshark: dict[str, Any] | None = None) -> dict[str, Any] | None:
    ws_fields = (wireshark or {}).get(str(family.get("family_id")), [])
    if ws_fields:
        boundaries = sorted({boundary for x in ws_fields if x.get("offset") is not None and x.get("width") is not None and int(x["width"]) > 0 for boundary in (int(x["offset"]), int(x["offset"]) + int(x["width"]))})
        if boundaries:
            return {"family_id": family.get("family_id"), "boundaries": boundaries, "confidence": 1.0, "evidence_refs": ["trusted_wireshark_dissector_offsets"]}
    return None

def record(task: str, evidence: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    system = "You are an expert Protocol Reverse Engineering Analyst. Return one JSON object and no Markdown fences."
    user = f"### TASK: {task}\n\nUse only the supplied statistical and relational evidence. Do not infer labels from dissector names.\n\n## Evidence Bundle\n```json\n{json.dumps(evidence, indent=2, ensure_ascii=False)}\n```"
    return {"messages": [{"role":"system","content":system},{"role":"user","content":user},{"role":"assistant","content":json.dumps(target, separators=(",",":"), ensure_ascii=False)}], "metadata":{"task":task,"protocol":evidence.get("protocol"),"family_id":evidence.get("family_id"),"reviewed":True,"approved":True,"reviewer":"wireshark","supervision_source":"trusted_wireshark_targets"}}

def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("protocol_model", type=Path); p.add_argument("output", type=Path); p.add_argument("--evidence-bundle", type=Path); p.add_argument("--wireshark-targets", type=Path, help="JSON mapping family_id to trusted Wireshark fields; required for semantic_labeling"); p.add_argument("--tasks", nargs="+", choices=["boundary_refinement","semantic_labeling"], default=["boundary_refinement","semantic_labeling"]); p.add_argument("--max-families", type=int, default=0)
    a = p.parse_args(); model = load(a.protocol_model); bundle = load(a.evidence_bundle) if a.evidence_bundle else None; wireshark = load(a.wireshark_targets) if a.wireshark_targets else None
    if wireshark is None: raise SystemExit("--wireshark-targets is required; trusted Wireshark targets are the only gold supervision")
    families = (model.get("families") or [])[:a.max_families or None]; a.output.parent.mkdir(parents=True, exist_ok=True); count=0; skipped=0
    with a.output.open("w", encoding="utf-8") as out:
        for family in families:
            ev=evidence_for_family(family,bundle); ev["protocol"]=model.get("protocol_name", model.get("metadata",{}).get("protocol_name","unknown"))
            for task in a.tasks:
                target = boundary_target(family, wireshark) if task == "boundary_refinement" else semantic_target(family, wireshark)
                if target is None: skipped += 1; continue
                out.write(json.dumps(record(task,ev,target),ensure_ascii=False)+"\n"); count += 1
    print(json.dumps({"written":count,"skipped_without_targets":skipped,"output":str(a.output)},indent=2))

if __name__ == "__main__": main()
