#!/usr/bin/env python3
"""Build conservative semantic-label SFT records from Wireshark PDML fields."""
from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from protocol_re.llm.stage_semantics import render_semantic_prompt

PCAP_SUFFIXES = {".pcap", ".pcapng", ".cap"}
SKIP_PREFIXES = ("frame.", "eth.", "ip.", "ipv6.", "tcp.", "udp.", "data.")

ROLE_RULES = [
    ("transaction_id", ("transaction_id", "transactionid", "invoke_id", "invokeid", "xid")),
    ("function_code", ("function_code", "functioncode", "func_code", "service", "opcode", "command")),
    ("byte_count", ("byte_count", "bytecount")),
    ("length", ("length", "packet_len", "payload_len", "data_len", "size")),
    ("sequence_number", ("sequence", "seq_num", "sequence_number")),
    ("counter", ("counter",)),
    ("unit_id", ("unit_id", "unitid", "slave_id", "station")),
    ("device_id", ("device_id", "deviceid", "vendor_id", "vendorid")),
    ("address", ("address", "addr", "object_id", "instance_id")),
    ("quantity", ("quantity", "item_count", "element_count", "number_of")),
    ("error_code", ("error_code", "errorcode", "exception_code", "abort_reason")),
    ("status", ("status", "result", "response_code")),
    ("checksum", ("checksum", "fcs")),
    ("crc", ("crc",)),
    ("timestamp", ("timestamp", "time_stamp", "utc_time")),
    ("flags", ("flags", "flag")),
    ("payload", ("payload", "user_data", "userdata")),
]


def role_for(name: str, showname: str) -> str | None:
    text = (name + " " + showname).lower().replace("-", "_")
    for role, needles in ROLE_RULES:
        if any(re.search(r"(?:^|[._ ])" + re.escape(n) + r"(?:$|[._ :])", text) for n in needles):
            return role
    return None


def encoding_for(size: int) -> str:
    return {1: "uint8", 2: "uint16_be", 4: "uint32_be", 8: "uint64_be"}.get(size, "bytes")


def candidate_files(root: Path, aliases: list[str], scan_all: bool) -> list[Path]:
    files = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in PCAP_SUFFIXES]
    if scan_all:
        return files
    matched = [p for p in files if any(a.lower() in str(p.relative_to(root)).lower() for a in aliases)]
    return matched


def sampled_frame_numbers(tshark: str, pcap: Path, display_filter: str, limit: int, rng: random.Random) -> list[int]:
    cmd = [tshark, "-n", "-r", str(pcap), "-Y", display_filter, "-T", "fields", "-e", "frame.number"]
    reservoir: list[int] = []
    seen = 0
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    assert proc.stdout is not None
    for line in proc.stdout:
        try:
            number = int(line.strip())
        except ValueError:
            continue
        seen += 1
        if len(reservoir) < limit:
            reservoir.append(number)
        else:
            index = rng.randrange(seen)
            if index < limit:
                reservoir[index] = number
    stderr = proc.stderr.read() if proc.stderr else ""
    if proc.wait() != 0:
        raise RuntimeError(stderr.strip() or f"TShark failed for {pcap}")
    return sorted(reservoir)


def pdml_packets(tshark: str, pcap: Path, display_filter: str, frames: list[int]) -> Iterable[ET.Element]:
    if not frames:
        return
    frame_filter = "frame.number in {" + ",".join(map(str, frames)) + "}"
    cmd = [tshark, "-n", "-r", str(pcap), "-Y", f"({display_filter}) && ({frame_filter})", "-T", "pdml"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdout is not None
    try:
        for _, element in ET.iterparse(proc.stdout, events=("end",)):
            if element.tag == "packet":
                yield element
                element.clear()
    finally:
        stderr = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
        if proc.wait() != 0:
            raise RuntimeError(stderr.strip() or f"PDML extraction failed for {pcap}")


def packet_record(packet: ET.Element, protocol: str, source: str, prefixes: list[str], unmapped: Counter[str]) -> dict[str, Any] | None:
    fields: list[dict[str, Any]] = []
    labels: list[dict[str, Any]] = []
    occupied: set[tuple[int, int]] = set()
    protocol_nodes = [node for node in packet.iter("proto") if node.get("name", "") in prefixes]
    if not protocol_nodes:
        return None
    try:
        protocol_start = min(int(node.get("pos", "0")) for node in protocol_nodes)
    except ValueError:
        return None
    for node in packet.iter("field"):
        name = node.get("name", "")
        if not name or name.startswith(SKIP_PREFIXES) or not any(name == prefix or name.startswith(prefix + ".") for prefix in prefixes):
            continue
        try:
            start, size = int(node.get("pos", "-1")), int(node.get("size", "0"))
        except ValueError:
            continue
        start -= protocol_start
        if start < 0 or size <= 0 or (start, size) in occupied:
            continue
        role = role_for(name, node.get("showname", ""))
        if role is None:
            unmapped[name] += 1
            continue
        occupied.add((start, size))
        index = len(fields)
        encoding = encoding_for(size)
        value = (node.get("value") or "").lower()
        fields.append({"start": start, "end": start + size, "width": size, "field_type": encoding})
        labels.append({
            "field_index": index, "offset": start, "width": size,
            "field_type": encoding, "encoding_type": encoding,
            "semantic_role": role, "human_label": name,
            "confidence": 0.95,
            "evidence": [f"Wireshark dissector field: {name}", f"PDML offset={start}, size={size}"],
            "alternative_roles": [],
        })
    if not labels:
        return None
    fields_and_labels = sorted(zip(fields, labels), key=lambda pair: (pair[0]["start"], pair[0]["width"]))
    fields = [pair[0] for pair in fields_and_labels]
    labels = [dict(pair[1], field_index=i) for i, pair in enumerate(fields_and_labels)]
    evidence = {
        "family_id": f"{protocol}:{source}", "fields": fields,
        "field_statistics": {}, "relations": [], "family_role": "unknown",
        "sample_values": [],
    }
    answer = {
        "family_id": evidence["family_id"], "family_role": "unknown",
        "semantic_labels": labels, "unlabeled_fields": [],
        "confidence_summary": {"high_confidence": len(labels), "medium_confidence": 0, "low_confidence": 0, "unlabeled": 0},
        "notes": "Gold labels derived from Wireshark dissector offsets and field names.",
    }
    return {"messages": [
        {"role": "system", "content": "You are an expert Protocol Reverse Engineering Analyst."},
        {"role": "user", "content": render_semantic_prompt(evidence)},
        {"role": "assistant", "content": json.dumps(answer, separators=(",", ":"), ensure_ascii=False)},
    ], "metadata": {"protocol": protocol, "source": source, "task": "semantic_labeling"}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pcap-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--protocols", type=Path, default=Path(__file__).with_name("protocols.json"))
    parser.add_argument("--split", choices=("train", "holdout"), default="train")
    parser.add_argument("--tshark", default="tshark")
    parser.add_argument("--max-files-per-protocol", type=int, default=40)
    parser.add_argument("--max-packets-per-file", type=int, default=12)
    parser.add_argument("--scan-all-files", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    config = json.loads(args.protocols.read_text(encoding="utf-8"))[args.split]
    rng = random.Random(args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    unmapped: Counter[str] = Counter()
    written = 0
    with args.output.open("w", encoding="utf-8") as output:
        for protocol, spec in config.items():
            prefixes = spec.get("field_prefixes") or re.findall(r"[A-Za-z][A-Za-z0-9_]*", spec["filter"])
            prefixes = [prefix for prefix in prefixes if prefix.lower() not in {"and", "or", "not"}]
            files = candidate_files(args.pcap_dir, spec["aliases"], args.scan_all_files)
            rng.shuffle(files)
            files = files[: args.max_files_per_protocol]
            print(f"[{protocol}] {len(files)} candidate PCAP files", flush=True)
            for pcap in files:
                try:
                    frames = sampled_frame_numbers(args.tshark, pcap, spec["filter"], args.max_packets_per_file, rng)
                    for packet in pdml_packets(args.tshark, pcap, spec["filter"], frames):
                        record = packet_record(packet, protocol, f"{pcap.name}", prefixes, unmapped)
                        if record:
                            output.write(json.dumps(record, ensure_ascii=False) + "\n")
                            written += 1
                except Exception as exc:
                    print(f"WARNING: {pcap}: {exc}", file=sys.stderr)
    report = args.output.with_suffix(".unmapped.json")
    report.write_text(json.dumps(unmapped.most_common(500), indent=2), encoding="utf-8")
    print(f"Wrote {written} examples to {args.output}")
    print(f"Wrote unmapped field report to {report}")


if __name__ == "__main__":
    main()
