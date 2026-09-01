#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "src"))

from VAE_supervised_train.common import file_fingerprint, stable_id, write_jsonl
from protocol_re.io.extract_payloads import _extract_tshark_packets, _payloads_from_tshark_packets


PROTOCOLS: dict[str, dict[str, Any]] = {
    "bacnet": {"filter": "bacapp", "raw": ["bacapp", "bacnet"], "fields": [["bacapp.confirmed_service", "bacapp.unconfirmed_service"]]},
    "cip": {"filter": "cip", "raw": ["cip"], "fields": [["cip.service", "cip.service_code", "cip.serviceid"]]},
    "dnp3": {"filter": "dnp3", "raw": ["dnp3"], "fields": [["dnp3.al.func"]]},
    "enip": {"filter": "enip", "raw": ["enip"], "fields": [["enip.command"]]},
    "ethercat": {"filter": "ecat", "raw": ["ecat"], "fields": [["ecat.cmd", "ecat.subtype"]]},
    "goose": {"filter": "goose", "raw": ["goose"], "fields": [], "constant_family": "goose_pdu"},
    "hart_ip": {"filter": "hart_ip", "raw": ["hart_ip"], "fields": [["hart_ip.pt.command"], ["hart_ip.pt.rsp.embedded_command"], ["hart_ip.message_type"]]},
    "iec104": {"filter": "iec60870_104", "raw": ["iec60870_104"], "fields": [["iec60870_104.type"], ["iec60870_104.utype"]]},
    "mms": {"filter": "mms", "raw": ["mms"], "fields": [[
        "mms.confirmed_RequestPDU_element", "mms.confirmed_ResponsePDU_element", "mms.confirmed_ErrorPDU_element",
        "mms.unconfirmed_PDU_element", "mms.rejectPDU_element", "mms.initiate_RequestPDU_element",
        "mms.initiate_ResponsePDU_element", "mms.conclude_RequestPDU_element", "mms.conclude_ResponsePDU_element"]]},
    "modbus": {"filter": "mbtcp || modbus", "raw": ["modbus", "mbtcp"], "fields": [["modbus.func_code"]]},
    "opcua": {"filter": "opcua", "raw": ["opcua"], "fields": [["opcua.servicenodeid.numeric"], ["opcua.transport.type"]]},
    "powerlink": {"filter": "epl", "raw": ["epl"], "fields": [["epl.mtyp", "epl.asnd.serviceid"]]},
    "profinet": {"filter": "pn_io", "raw": ["pn_io"], "fields": [["pn_io.block_type"], ["pn_io.pdu_type.type"]]},
    "s7comm": {"filter": "s7comm", "raw": ["s7comm"], "fields": [["s7comm.param.userdata.subfunc"], ["s7comm.param.func"], ["s7comm.header.rosctr"]]},
    "zigbee": {"filter": "zbee_nwk", "raw": ["zbee_nwk"], "fields": [["zbee_nwk.cmd.id"], ["zbee_nwk.frame_type"]]},
}


def scalar_values(node: Any, wanted: set[str], found: dict[str, list[str]]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key in wanted and not key.endswith("_raw"):
                values = value if isinstance(value, list) else [value]
                found[key].extend(str(item) for item in values if not isinstance(item, (dict, list)))
            scalar_values(value, wanted, found)
    elif isinstance(node, list):
        for value in node:
            scalar_values(value, wanted, found)


def select_family(layers: dict[str, Any], tiers: list[list[str]]) -> tuple[str, str, float] | None:
    for rank, alternatives in enumerate(tiers):
        found = {name: [] for name in alternatives}
        scalar_values(layers, set(alternatives), found)
        present = []
        for name, values in found.items():
            unique = sorted(set(values))
            if len(unique) > 1:
                return None
            if unique:
                present.append((name, unique[0]))
        if len(present) == 1:
            field, value = present[0]
            return f"{field}={value}", field, max(0.8, 1.0 - rank * 0.1)
        if len(present) > 1:
            return None
    return None


def select_payload(layers: dict[str, Any], raw_names: list[str]) -> tuple[str, int, int, str] | None:
    frame_raw = layers.get("frame_raw")
    if not isinstance(frame_raw, list) or len(frame_raw) < 3:
        return None
    frame_hex = str(frame_raw[0]).lower()
    candidates = []
    for dissector in raw_names:
        raw = layers.get(f"{dissector}_raw")
        descriptors = raw if isinstance(raw, list) and raw and isinstance(raw[0], list) else [raw]
        for descriptor in descriptors:
            if isinstance(descriptor, list) and len(descriptor) >= 3:
                payload_hex, offset, length = str(descriptor[0]).lower(), int(descriptor[1]), int(descriptor[2])
                if payload_hex and length > 0 and len(payload_hex) == length * 2:
                    candidates.append((payload_hex, offset, length, dissector))
        if candidates:
            break
    unique = list(dict.fromkeys(candidates))
    if len(unique) != 1:
        return None
    payload_hex, offset, length, dissector = unique[0]
    if frame_hex[offset * 2:(offset + length) * 2] != payload_hex:
        return None
    if frame_hex.count(payload_hex) != 1:
        return None
    return payload_hex, offset, length, dissector


def tshark_packets(path: Path, display_filter: str) -> list[dict[str, Any]]:
    command = ["tshark", "-r", str(path), "-Y", display_filter, "-T", "json", "-x"]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"TShark exited {result.returncode}")
    return json.loads(result.stdout or "[]")


def process_pcap(path: Path, protocol_id: str, config: dict[str, Any], threshold: float) -> tuple[list[dict], Counter]:
    accepted, stats = [], Counter()
    generic_payloads: dict[int, list[dict[str, Any]]] = {}
    for payload in _payloads_from_tshark_packets(_extract_tshark_packets(str(path), config["filter"])):
        frame_number = int(payload.get("metadata", {}).get("frame", {}).get("number") or 0)
        generic_payloads.setdefault(frame_number, []).append(payload)
    for packet in tshark_packets(path, config["filter"]):
        layers = packet.get("_source", {}).get("layers", {})
        frame = layers.get("frame", {})
        family = select_family(layers, config["fields"])
        if family is None and config.get("constant_family") and config["raw"][0] in layers:
            family = (str(config["constant_family"]), f"{config['raw'][0]}_dissector", 1.0)
        if family is None:
            stats["rejected_family"] += 1
            continue
        frame_number = int(frame.get("frame.number", 0))
        payload_matches = generic_payloads.get(frame_number, [])
        if len(payload_matches) != 1:
            stats["rejected_payload"] += 1
            continue
        family_id, field_name, confidence = family
        if confidence < threshold:
            stats["rejected_confidence"] += 1
            continue
        payload_hex = str(payload_matches[0]["payload_hex"])
        length = len(payload_hex) // 2
        accepted.append({
            "record_id": stable_id(protocol_id, path, frame_number, payload_hex),
            "payload_hex": payload_hex, "payload_len": length, "protocol_id": protocol_id,
            "source_pcap": str(path), "frame_number": frame_number, "frame_offset": 0,
            "trusted_family_id": family_id, "annotation_confidence": confidence,
            "annotation_evidence": {
                "field_name": field_name,
                "payload_source": "tshark_transport_or_l2_payload",
            },
        })
        stats["accepted"] += 1
    return accepted, stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Build trusted TShark message-family annotations from sampled PCAPs.")
    parser.add_argument("--pcap-root", type=Path, default=Path("finetuning/windows_data/sampled_pcaps"))
    parser.add_argument("--output", type=Path, default=Path("VAE_supervised_train/cache/messages.jsonl"))
    parser.add_argument("--protocols", default="all", help="Comma-separated protocol directory names.")
    parser.add_argument("--min-confidence", type=float, default=0.9)
    parser.add_argument("--force", action="store_true", help="Ignore per-PCAP extraction cache.")
    args = parser.parse_args()
    selected = set(PROTOCOLS) if args.protocols in {"all", "*"} else set(args.protocols.split(","))
    unknown = selected - set(PROTOCOLS)
    if unknown:
        raise SystemExit(f"Unknown protocols: {sorted(unknown)}")
    cache_dir = args.output.parent / "pcap_records"
    cache_dir.mkdir(parents=True, exist_ok=True)
    all_rows, totals = [], Counter()
    for protocol_id in sorted(selected):
        for pcap in sorted((args.pcap_root / protocol_id).glob("*.pcap*")):
            fingerprint = file_fingerprint(pcap)
            cache_key = stable_id(
                "tshark_transport_or_l2_payload_v1",
                fingerprint,
                PROTOCOLS[protocol_id],
                args.min_confidence,
            )
            cache_path = cache_dir / f"{protocol_id}_{cache_key}.json"
            if cache_path.exists() and not args.force:
                cached = json.loads(cache_path.read_text(encoding="utf-8"))
                rows, stats = cached["records"], Counter(cached["stats"])
            else:
                rows, stats = process_pcap(pcap, protocol_id, PROTOCOLS[protocol_id], args.min_confidence)
                cache_path.write_text(json.dumps({"fingerprint": fingerprint, "records": rows, "stats": stats}), encoding="utf-8")
            all_rows.extend(rows)
            totals.update(stats)
    write_jsonl(args.output, all_rows)
    manifest = {"format": "protocol-re-trusted-families-v2", "records": len(all_rows),
                "payload_source": "tshark_transport_or_l2_payload",
                "protocols": sorted(selected), "min_confidence": args.min_confidence, "stats": totals}
    args.output.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
