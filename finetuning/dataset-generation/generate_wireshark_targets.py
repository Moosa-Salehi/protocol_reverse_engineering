#!/usr/bin/env python3
"""Generate conservative family-specific targets from TShark jsonraw data."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

EXCLUDED_PROTOCOLS = {"frame", "eth", "ethertype", "ip", "ipv6", "tcp", "udp", "sll", "sll2", "vlan", "data"}
ROLE_PATTERNS = [
    (r"transaction(_identifier|_id)?|trans_id|xid", "transaction_id"),
    (r"correlation(_identifier|_id)?|request_id", "correlation_id"),
    (r"sequence(_number|_num)?|seq(_num|_number)?", "sequence_number"),
    (r"function(_code)?|func(_code)?", "function_code"),
    (r"operation(_code)?|opcode", "opcode"),
    (r"unit(_identifier|_id)?|slave(_identifier|_id)?", "unit_id"),
    (r"device(_identifier|_id)?", "device_id"),
    (r"byte_count|bytecount", "byte_count"),
    (r"checksum", "checksum"), (r"\bcrc\b", "crc"),
    (r"timestamp|time_stamp", "timestamp"),
    (r"error(_code)?|exception(_code)?", "error_code"),
    (r"status", "status"), (r"flags?", "flags"),
    (r"quantity|number_of|num_of|count", "quantity"),
    (r"length|\blen\b", "length"), (r"address|\baddr\b|reference", "address"),
    (r"counter", "counter"), (r"padding|pad", "padding"), (r"reserved", "reserved"),
    (r"payload|data_value|values?", "payload"),
]

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def clean_hex(value: Any) -> str:
    return re.sub(r"[^0-9a-f]", "", str(value).lower())

def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")

def semantic_role(abbrev: str, display_name: str) -> str | None:
    text = normalize(f"{abbrev.rsplit('.', 1)[-1]} {display_name}")
    for pattern, role in ROLE_PATTERNS:
        if re.search(pattern, text):
            return role
    return None

def tshark_field_catalog(tshark: str) -> dict[str, dict[str, str]]:
    proc = subprocess.run([tshark, "-G", "fields"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
    catalog = {}
    for line in proc.stdout.splitlines():
        columns = line.split("\t")
        if len(columns) >= 4 and columns[0] == "F":
            catalog[columns[2]] = {"name": columns[1], "type": columns[3]}
    return catalog

def iter_raw_fields(value: Any) -> Iterable[tuple[str, str, int, int]]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.endswith("_raw"):
                abbrev = key[:-4]
                entries = child if isinstance(child, list) and child and isinstance(child[0], list) else [child]
                for entry in entries:
                    if isinstance(entry, list) and len(entry) >= 3:
                        try:
                            yield abbrev, clean_hex(entry[0]), int(entry[1]), int(entry[2])
                        except (TypeError, ValueError):
                            pass
            yield from iter_raw_fields(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_raw_fields(child)

def run_jsonraw(tshark: str, pcap: Path, display_filter: str) -> list[dict[str, Any]]:
    command = [tshark, "-n", "-r", str(pcap), "-Y", display_filter, "-T", "jsonraw"]
    proc = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
    payload = json.loads(proc.stdout or "[]")
    return payload if isinstance(payload, list) else []

def locate_payload(frame_hex: str, payload_hex: str, raw_fields: list[tuple[str, str, int, int]]) -> int | None:
    starts = [match.start() // 2 for match in re.finditer(re.escape(payload_hex), frame_hex)]
    if not starts:
        return None
    if len(starts) == 1:
        return starts[0]
    scored = []
    for start in starts:
        end = start + len(payload_hex) // 2
        contained = sum(start <= offset and offset + width <= end for _, _, offset, width in raw_fields)
        scored.append((contained, start))
    scored.sort(reverse=True)
    return scored[0][1] if len(scored) == 1 or scored[0][0] > scored[1][0] else None

def corpus_index(messages_path: Path, assignments_path: Path) -> dict[str, dict[str, Counter[str]]]:
    assignments = {int(x["msg_id"]): str(x["family_id"]) for x in load_json(assignments_path).get("assignments", [])}
    index: dict[str, dict[str, Counter[str]]] = defaultdict(lambda: defaultdict(Counter))
    for line in messages_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line); family = assignments.get(int(row["msg_id"]))
        if family:
            index[Path(str(row.get("source_file", ""))).name][clean_hex(row["payload_hex"])][family] += 1
    return index

def encoding_type(field_type: str, width: int) -> str:
    lowered = str(field_type).lower()
    if lowered.startswith("ft_uint") and width in {1, 2, 4, 8}:
        return f"uint{width * 8}_be"
    if lowered.startswith("ft_int") and width in {1, 2, 4, 8}:
        return f"int{width * 8}_be"
    return "bytes"

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("protocol_model", type=Path)
    parser.add_argument("messages", type=Path)
    parser.add_argument("assignments", type=Path)
    parser.add_argument("pcap", type=Path, nargs="+")
    parser.add_argument("--filter", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--tshark", default="tshark")
    parser.add_argument("--minimum-support", type=int, default=2)
    parser.add_argument("--minimum-family-packets", type=int, default=2,
                        help="Minimum packets contributing to a family before targets are eligible")
    parser.add_argument("--minimum-family-purity", type=float, default=0.95,
                        help="Minimum dominant packet signature share required for a family")
    args = parser.parse_args()
    if args.minimum_family_packets < 1:
        parser.error("--minimum-family-packets must be at least 1")
    if not 0.0 < args.minimum_family_purity <= 1.0:
        parser.error("--minimum-family-purity must be in (0, 1]")
    model = load_json(args.protocol_model); catalog = tshark_field_catalog(args.tshark)
    corpus = corpus_index(args.messages, args.assignments)
    observations: dict[str, dict[tuple[int, int], Counter[str]]] = defaultdict(lambda: defaultdict(Counter))
    packet_signatures: dict[str, Counter[tuple[tuple[int, int, str], ...]]] = defaultdict(Counter)
    errors = []; unmatched_packets = 0; ambiguous_families = 0
    for pcap in args.pcap:
        try:
            for packet in run_jsonraw(args.tshark, pcap, args.filter):
                fields = list(iter_raw_fields(packet))
                frame = next((raw for abbrev, raw, offset, _ in fields if abbrev == "frame" and offset == 0), "")
                if not frame:
                    continue
                source_payloads = corpus.get(pcap.name, {})
                candidates = [(payload, families) for payload, families in source_payloads.items() if payload and payload in frame]
                if not candidates:
                    unmatched_packets += 1; continue
                payload, family_counts = max(candidates, key=lambda item: len(item[0]))
                if len(family_counts) != 1:
                    ambiguous_families += 1; continue
                family = next(iter(family_counts)); payload_start = locate_payload(frame, payload, fields)
                if payload_start is None:
                    unmatched_packets += 1; continue
                payload_end = payload_start + len(payload) // 2
                signature = []
                for abbrev, _raw, frame_offset, width in fields:
                    protocol = abbrev.split(".", 1)[0]
                    if protocol in EXCLUDED_PROTOCOLS or width <= 0 or not (payload_start <= frame_offset and frame_offset + width <= payload_end):
                        continue
                    signature.append((frame_offset - payload_start, width, abbrev))
                    observations[family][(frame_offset - payload_start, width)][abbrev] += 1
                if signature:
                    packet_signatures[family][tuple(sorted(set(signature)))] += 1
        except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
            errors.append(f"{pcap}: {exc}")

    targets: dict[str, list[dict[str, Any]]] = {}; review: dict[str, Any] = {"errors": errors, "ambiguous": [], "unmatched": [], "rejected_families": []}
    for family in model.get("families", []) or []:
        family_id = str(family.get("family_id")); accepted = []
        signature_counts = packet_signatures[family_id]
        packet_count = sum(signature_counts.values())
        dominant_signature, dominant_count = signature_counts.most_common(1)[0] if signature_counts else ((), 0)
        purity = dominant_count / packet_count if packet_count else 0.0
        eligible = packet_count >= args.minimum_family_packets and purity >= args.minimum_family_purity
        if not eligible:
            review["rejected_families"].append({"family_id": family_id, "packet_count": packet_count, "purity": round(purity, 4), "required_packets": args.minimum_family_packets, "required_purity": args.minimum_family_purity})
            continue
        for field in family.get("field_hypotheses", []) or []:
            offset = int(field.get("start", field.get("offset", 0)) or 0)
            width = int(field.get("width", field.get("length", 0)) or 0)
            dominant_names = {name for field_offset, field_width, name in dominant_signature if field_offset == offset and field_width == width}
            supported = [(name, dominant_count) for name in sorted(dominant_names)
                         if dominant_count >= args.minimum_support]
            candidates = []
            for abbrev, count in supported:
                info = catalog.get(abbrev, {}); role = semantic_role(abbrev, info.get("name", abbrev))
                if role:
                    candidates.append((abbrev, info, role, count))
            roles = {item[2] for item in candidates}
            if candidates and len(roles) == 1:
                abbrev, info, role, count = candidates[0]
                accepted.append({"offset": offset, "width": width, "wireshark_name": info.get("name", abbrev), "wireshark_field": abbrev, "semantic_role": role, "field_type": field.get("field_type", "bytes"), "encoding_type": encoding_type(info.get("type", ""), width), "support": count})
            elif supported:
                review["ambiguous"].append({"family_id": family_id, "offset": offset, "width": width, "observed": supported, "mapped_roles": sorted(roles)})
            else:
                review["unmatched"].append({"family_id": family_id, "offset": offset, "width": width})
        if accepted:
            targets[family_id] = accepted
    review["summary"] = {"target_families": len(targets), "target_fields": sum(map(len, targets.values())), "ambiguous_fields": len(review["ambiguous"]), "unmatched_fields": len(review["unmatched"]), "rejected_families": len(review["rejected_families"]), "unmatched_packets": unmatched_packets, "ambiguous_packet_families": ambiguous_families}
    args.output.parent.mkdir(parents=True, exist_ok=True); args.report.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(targets, indent=2), encoding="utf-8"); args.report.write_text(json.dumps(review, indent=2), encoding="utf-8")
    print(json.dumps(review["summary"] | {"output": str(args.output), "report": str(args.report)}, indent=2))

if __name__ == "__main__":
    main()
