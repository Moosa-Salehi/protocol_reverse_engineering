from __future__ import annotations

import json
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from protocol_re.model.schema import MessageRecord

try:
    from scapy.all import IP, TCP, rdpcap
except Exception:  # pragma: no cover - optional dependency at import time
    IP = None
    TCP = None
    rdpcap = None



def _require_scapy() -> None:
    if rdpcap is None or TCP is None or IP is None:
        raise RuntimeError("Scapy is required for PCAP extraction. Install scapy before running this stage.")



def _canonical_session_key(src_ip: str, src_port: int, dst_ip: str, dst_port: int) -> str:
    left = (src_ip, src_port)
    right = (dst_ip, dst_port)
    if left <= right:
        return f"{src_ip}:{src_port} <-> {dst_ip}:{dst_port}"
    return f"{dst_ip}:{dst_port} <-> {src_ip}:{src_port}"



def extract_messages_from_pcap(file_path: str, service_port: int = 502) -> List[MessageRecord]:
    _require_scapy()
    packets = rdpcap(file_path)
    session_counts: Dict[str, int] = defaultdict(int)
    messages: List[MessageRecord] = []
    source_name = Path(file_path).name

    for packet in packets:
        if IP not in packet or TCP not in packet:
            continue
        if packet[TCP].sport != service_port and packet[TCP].dport != service_port:
            continue
        if len(packet[TCP].payload) <= 0:
            continue

        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        src_port = int(packet[TCP].sport)
        dst_port = int(packet[TCP].dport)
        payload = bytes(packet[TCP].payload)
        session_key = _canonical_session_key(src_ip, src_port, dst_ip, dst_port)
        session_index = session_counts[session_key]
        session_id = f"{source_name}:{session_key}"
        direction = "client_to_server" if dst_port == service_port else "server_to_client"
        timestamp = float(packet.time) if hasattr(packet, "time") else None

        messages.append(
            MessageRecord(
                msg_id=-1,
                source_file=source_name,
                session_id=session_id,
                session_key=session_key,
                src_ip=src_ip,
                src_port=src_port,
                dst_ip=dst_ip,
                dst_port=dst_port,
                direction=direction,
                payload_hex=payload.hex(),
                payload_len=len(payload),
                timestamp=timestamp,
                index_in_session=session_index,
                metadata={"service_port": service_port},
            )
        )
        session_counts[session_key] += 1

    return messages



def extract_messages_from_pcaps(pcap_dir: str, service_port: int = 502, max_workers: int = 4) -> List[MessageRecord]:
    pcap_paths = [str(path) for path in sorted(Path(pcap_dir).iterdir()) if path.suffix.lower() in {".pcap", ".pcapng"}]
    all_messages: List[MessageRecord] = []
    next_msg_id = 0

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(extract_messages_from_pcap, path, service_port): path for path in pcap_paths}
        for future in as_completed(futures):
            messages = future.result()
            for message in messages:
                message.msg_id = next_msg_id
                all_messages.append(message)
                next_msg_id += 1

    all_messages.sort(key=lambda item: (item.session_id, item.index_in_session, item.msg_id))
    for idx, message in enumerate(all_messages):
        message.msg_id = idx
    return all_messages



def write_messages_jsonl(messages: Iterable[MessageRecord], output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as handle:
        for message in messages:
            handle.write(json.dumps(message.to_dict(), sort_keys=True) + "\n")
