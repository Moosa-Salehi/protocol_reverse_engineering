"""Offline validation: project TLV-mode results onto the real goose corpus.

Loads the existing goose run artifacts (messages + length-bucket assignments),
applies the new TLV detection/merge/field-derivation, and scores the result
with the real stage-17 evaluator against truth_files/goose.json.

Run from the project root:
    python scripts/diagnostics/30_tlv_offline_goose.py [data_dir] [truth_json]
"""

from __future__ import annotations

import importlib.util
import json
import sys
from importlib import util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from protocol_re.inference.tlv import (
    TlvFramingDetection,
    detect_tlv_framing,
    derive_tlv_field_hypotheses,
    merge_families_by_tlv_signature,
)
from protocol_re.model.schema import FamilyAssignment
from protocol_re.utils.bytes import hex_to_bytes


def _load_evaluator():
    spec = util.spec_from_file_location("stage17", ROOT / "scripts/17_evaluate_protocol_spec.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_messages(data_dir: Path):
    spec = util.spec_from_file_location("loader", ROOT / "src/protocol_re/corpus/message_corpus.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load_corpus_jsonl(str(data_dir / "01_messages.jsonl"))


def main() -> None:
    data_dir = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "dol/finetuned-goose/data")
    truth_path = Path(sys.argv[2] if len(sys.argv) > 2 else ROOT / "truth_files/goose.json")

    records = _load_messages(data_dir)
    print(f"[+] Loaded {len(records)} messages")

    with open(ROOT / "dol/finetuned-goose/data/02_family_assignments.json", "r", encoding="utf-8") as handle:
        assignments_payload = json.load(handle)
    assignments = [
        FamilyAssignment(msg_id=item["msg_id"], family_id=item["family_id"], confidence=item.get("confidence", 1.0))
        for item in assignments_payload.get("assignments", [])
    ]
    family_count_before = len({assignment.family_id for assignment in assignments})
    print(f"[+] Bootstrap families: {family_count_before}")

    messages = [hex_to_bytes(record.payload_hex) for record in records]
    detection = detect_tlv_framing(messages)
    if detection is None:
        print("[!] TLV framing NOT detected on this corpus")
        sys.exit(1)
    print(
        f"[+] TLV detected: header={detection.header_length}B, ratio={detection.parse_success_ratio}, "
        f"tags={detection.distinct_tags}, sequences={detection.sequence_count}"
    )

    merged, merge_meta = merge_families_by_tlv_signature(records, assignments, detection)
    print(
        f"[+] Family merge: {merge_meta['family_count_before']} -> {merge_meta['family_count_after']} "
        f"(parse_failures={merge_meta.get('parse_failures', 0)})"
    )

    # Build the family the way stage 12 would: merged members, TLV-derived fields.
    members_by_family: dict[str, list[str]] = {}
    for record, assignment in zip(records, merged):
        members_by_family.setdefault(assignment.family_id, []).append(record.payload_hex)
    families = []
    for family_id, members in sorted(members_by_family.items()):
        hypotheses, segments, meta = derive_tlv_field_hypotheses(family_id, members[:2000], detection)
        families.append(
            {
                "family_id": family_id,
                "role": "notification",
                "message_count": len(members),
                "field_hypotheses": [hypothesis.to_dict() for hypothesis in hypotheses],
                "tlv_metadata": meta,
                # Stage 12 attaches the per-family framing result; the TLV layout
                # is what lets the evaluator find the constant 0x61 at body offset.
                "framing_summary": {
                    "layout_hypotheses": [
                        {
                            "header_start": 0,
                            "header_end": detection.header_length,
                            "body_start": detection.header_length,
                            "confidence": 0.95,
                            "evidence": {"mode": "tlv_ber"},
                        }
                    ]
                },
            }
        )
        print(f"    {family_id}: {len(members)} messages, {len(hypotheses)} fields")

    model = {"predicted_protocol": {"families": families, "relations": []}}

    evaluator = _load_evaluator()
    with open(truth_path, "r", encoding="utf-8") as handle:
        truth = json.load(handle)
    result = evaluator.evaluate_protocol_spec(model, truth)

    summary = result["summary"]
    print(
        f"\n[=] Overall: {summary['overall_score']} ({summary['verdict']}) | "
        f"message types matched {summary['matched_message_type_count']}/{summary['ground_truth_message_type_count']}"
    )
    for name, metrics in result["metrics"].items():
        print(
            f"    {name:24s} f1={metrics['f1_score']:.3f} "
            f"precision={metrics['precision']:.3f} recall={metrics['recall']:.3f}"
        )
    for match in result["matches"]["message_types"]:
        print(f"    match: {match['predicted_family_id']} -> {match['ground_truth_message_type_id']} (score {match['score']})")

    out_path = data_dir / "tlv_offline_validation.json"
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump({"detection": detection.summary(), "merge": merge_meta, "evaluation": result}, handle, indent=2)
    print(f"[+] Wrote {out_path}")


if __name__ == "__main__":
    main()
