from __future__ import annotations

import json
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from protocol_re.model.schema import MessageRecord

try:
    from scapy.all import IP, TCP, rdpcap
except Exception:  # pragma: no cover - optional dependency at import time
    IP = None
    TCP = None
    rdpcap = None


FlowKey = Tuple[str, int, str, int]


@dataclass
class TcpSegment:
    seq: int
    payload: bytes
    timestamp: float | None


@dataclass
class TcpChunk:
    payload: bytes
    start_seq: int
    end_seq: int
    start_timestamp: float | None
    end_timestamp: float | None
    had_gap_before: bool = False


def _require_scapy() -> None:
    if rdpcap is None or TCP is None or IP is None:
        raise RuntimeError("Scapy is required for PCAP extraction. Install scapy before running this stage.")


def _canonical_session_key(src_ip: str, src_port: int, dst_ip: str, dst_port: int) -> str:
    left = (src_ip, src_port)
    right = (dst_ip, dst_port)
    if left <= right:
        return f"{src_ip}:{src_port} <-> {dst_ip}:{dst_port}"
    return f"{dst_ip}:{dst_port} <-> {src_ip}:{src_port}"


def _matches_service_port(src_port: int, dst_port: int, service_port: int | None) -> bool:
    return service_port is None or src_port == service_port or dst_port == service_port


def _direction(src_port: int, dst_port: int, service_port: int | None) -> str:
    if service_port is None:
        return "unknown"
    if dst_port == service_port and src_port != service_port:
        return "client_to_server"
    if src_port == service_port and dst_port != service_port:
        return "server_to_client"
    return "unknown"


def _packet_timestamp(packet) -> float | None:
    return float(packet.time) if hasattr(packet, "time") else None


def _packet_payload_messages(file_path: str, service_port: int | None = None) -> List[MessageRecord]:
    packets = rdpcap(file_path)
    session_counts: Dict[str, int] = defaultdict(int)
    messages: List[MessageRecord] = []
    source_name = Path(file_path).name

    for packet in packets:
        if IP not in packet or TCP not in packet:
            continue
        if len(packet[TCP].payload) <= 0:
            continue

        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        src_port = int(packet[TCP].sport)
        dst_port = int(packet[TCP].dport)
        if not _matches_service_port(src_port, dst_port, service_port):
            continue
        payload = bytes(packet[TCP].payload)
        session_key = _canonical_session_key(src_ip, src_port, dst_ip, dst_port)
        session_index = session_counts[session_key]
        session_id = f"{source_name}:{session_key}"

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
                direction=_direction(src_port, dst_port, service_port),
                payload_hex=payload.hex(),
                payload_len=len(payload),
                timestamp=_packet_timestamp(packet),
                index_in_session=session_index,
                metadata={"service_port": service_port, "extraction_mode": "packet_payload"},
            )
        )
        session_counts[session_key] += 1

    return messages


def _reassemble_directional_chunks(segments: List[TcpSegment]) -> List[TcpChunk]:
    chunks: List[TcpChunk] = []
    if not segments:
        return chunks

    ordered = sorted(segments, key=lambda item: (item.seq, item.timestamp if item.timestamp is not None else -1.0))
    buffer = bytearray()
    chunk_start_seq = ordered[0].seq
    chunk_start_ts = ordered[0].timestamp
    chunk_end_ts = ordered[0].timestamp
    expected_seq = ordered[0].seq
    gap_before_current = False

    for segment in ordered:
        payload = segment.payload
        if not payload:
            continue

        if not buffer:
            chunk_start_seq = segment.seq
            chunk_start_ts = segment.timestamp
            chunk_end_ts = segment.timestamp
            expected_seq = segment.seq

        if segment.seq > expected_seq and buffer:
            chunks.append(
                TcpChunk(
                    payload=bytes(buffer),
                    start_seq=chunk_start_seq,
                    end_seq=expected_seq,
                    start_timestamp=chunk_start_ts,
                    end_timestamp=chunk_end_ts,
                    had_gap_before=gap_before_current,
                )
            )
            buffer = bytearray()
            chunk_start_seq = segment.seq
            chunk_start_ts = segment.timestamp
            gap_before_current = True
            expected_seq = segment.seq

        offset = segment.seq - chunk_start_seq
        if offset < 0:
            trim = -offset
            if trim >= len(payload):
                continue
            payload = payload[trim:]
            offset = 0

        if offset > len(buffer):
            chunks.append(
                TcpChunk(
                    payload=bytes(buffer),
                    start_seq=chunk_start_seq,
                    end_seq=expected_seq,
                    start_timestamp=chunk_start_ts,
                    end_timestamp=chunk_end_ts,
                    had_gap_before=gap_before_current,
                )
            )
            buffer = bytearray(payload)
            chunk_start_seq = segment.seq
            chunk_start_ts = segment.timestamp
            chunk_end_ts = segment.timestamp
            expected_seq = segment.seq + len(payload)
            gap_before_current = True
            continue

        overlap = len(buffer) - offset
        if overlap < len(payload):
            buffer.extend(payload[overlap:])
            expected_seq = chunk_start_seq + len(buffer)
        chunk_end_ts = segment.timestamp if segment.timestamp is not None else chunk_end_ts

    if buffer:
        chunks.append(
            TcpChunk(
                payload=bytes(buffer),
                start_seq=chunk_start_seq,
                end_seq=expected_seq,
                start_timestamp=chunk_start_ts,
                end_timestamp=chunk_end_ts,
                had_gap_before=gap_before_current,
            )
        )

    return chunks


def _application_frames_from_stream(stream: bytes) -> List[Tuple[bytes, int, str]]:
    return [(stream, 0, "raw_tcp_stream")]


def _stream_reassembled_messages(file_path: str, service_port: int | None = None) -> List[MessageRecord]:
    packets = rdpcap(file_path)
    source_name = Path(file_path).name
    segments_by_flow: Dict[FlowKey, List[TcpSegment]] = defaultdict(list)

    for packet in packets:
        if IP not in packet or TCP not in packet:
            continue
        payload = bytes(packet[TCP].payload)
        if not payload:
            continue

        src_port = int(packet[TCP].sport)
        dst_port = int(packet[TCP].dport)
        if not _matches_service_port(src_port, dst_port, service_port):
            continue

        flow_key = (packet[IP].src, src_port, packet[IP].dst, dst_port)
        segments_by_flow[flow_key].append(
            TcpSegment(
                seq=int(packet[TCP].seq),
                payload=payload,
                timestamp=_packet_timestamp(packet),
            )
        )

    messages: List[MessageRecord] = []
    for flow_key, segments in sorted(segments_by_flow.items()):
        src_ip, src_port, dst_ip, dst_port = flow_key
        session_key = _canonical_session_key(src_ip, src_port, dst_ip, dst_port)
        session_id = f"{source_name}:{session_key}"
        direction = _direction(src_port, dst_port, service_port)

        for chunk_index, chunk in enumerate(_reassemble_directional_chunks(segments)):
            for frame_index, (payload, stream_offset, framing) in enumerate(_application_frames_from_stream(chunk.payload)):
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
                        timestamp=chunk.start_timestamp,
                        index_in_session=0,
                        metadata={
                            "service_port": service_port,
                            "extraction_mode": "tcp_stream",
                            "framing": framing,
                            "stream_chunk_index": chunk_index,
                            "frame_index_in_chunk": frame_index,
                            "stream_offset": stream_offset,
                            "tcp_start_seq": chunk.start_seq + stream_offset,
                            "tcp_end_seq": chunk.start_seq + stream_offset + len(payload),
                            "stream_gap_before": chunk.had_gap_before,
                        },
                    )
                )

    session_counts: Dict[str, int] = defaultdict(int)
    messages.sort(
        key=lambda item: (
            item.session_id,
            item.timestamp if item.timestamp is not None else float("inf"),
            item.metadata.get("tcp_start_seq", 0),
            item.direction,
        )
    )
    for message in messages:
        message.index_in_session = session_counts[message.session_id]
        session_counts[message.session_id] += 1

    return messages


def extract_messages_from_pcap(
    file_path: str,
    service_port: int | None = None,
    reassembly_mode: str = "packet",
) -> List[MessageRecord]:
    _require_scapy()
    if reassembly_mode == "packet":
        return _packet_payload_messages(file_path, service_port=service_port)
    if reassembly_mode == "stream":
        return _stream_reassembled_messages(file_path, service_port=service_port)
    raise ValueError(f"Unsupported reassembly mode: {reassembly_mode}")


def extract_messages_from_pcaps(
    pcap_dir: str,
    service_port: int | None = None,
    max_workers: int = 4,
    reassembly_mode: str = "packet",
    max_messages: int | None = None,
) -> List[MessageRecord]:
    pcap_paths = [str(path) for path in sorted(Path(pcap_dir).iterdir()) if path.suffix.lower() in {".pcap", ".pcapng"}]
    all_messages: List[MessageRecord] = []
    next_msg_id = 0

    if max_workers <= 1 or len(pcap_paths) <= 1:
        for path in pcap_paths:
            messages = extract_messages_from_pcap(path, service_port, reassembly_mode)
            for message in messages:
                message.msg_id = next_msg_id
                all_messages.append(message)
                next_msg_id += 1
                if max_messages is not None and len(all_messages) >= max_messages:
                    break
            if max_messages is not None and len(all_messages) >= max_messages:
                break
    else:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(extract_messages_from_pcap, path, service_port, reassembly_mode): path
                for path in pcap_paths
            }
            for future in as_completed(futures):
                messages = future.result()
                for message in messages:
                    message.msg_id = next_msg_id
                    all_messages.append(message)
                    next_msg_id += 1
                    if max_messages is not None and len(all_messages) >= max_messages:
                        break
                if max_messages is not None and len(all_messages) >= max_messages:
                    break

    all_messages.sort(key=lambda item: (item.session_id, item.index_in_session, item.msg_id))
    for idx, message in enumerate(all_messages):
        message.msg_id = idx
    return all_messages


def write_messages_jsonl(messages: Iterable[MessageRecord], output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as handle:
        for message in messages:
            handle.write(json.dumps(message.to_dict(), sort_keys=True) + "\n")
