from __future__ import annotations

import json
import os
import subprocess
import hashlib
from datetime import datetime
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Tuple

from protocol_re.model.schema import MessageRecord

try:
    from scapy.all import IP, TCP, PcapReader, rdpcap
except Exception:  # pragma: no cover - optional dependency at import time
    IP = None
    TCP = None
    PcapReader = None
    rdpcap = None


FlowKey = Tuple[str, int, str, int]
L2_ETHERTYPES = {
    "goose": "88b8",
    "sv": "88ba",
    "pn_rt": "8892",
    "pn_dcp": "8892",
    "pn_io": "8892",
    "ecatf": "88a4",
}


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
    if rdpcap is None or PcapReader is None or TCP is None or IP is None:
        raise RuntimeError("Scapy is required for PCAP extraction. Install scapy before running this stage.")


def _first(value: Any) -> Any:
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _get_nested_field(layers: Dict[str, Any], section: str, field: str) -> Any:
    section_obj = layers.get(section)
    if isinstance(section_obj, dict) and field in section_obj:
        return _first(section_obj[field])
    if field in layers:
        return _first(layers[field])
    return None


def _has_nested_field(layers: Dict[str, Any], section: str, field: str) -> bool:
    section_obj = layers.get(section)
    return (isinstance(section_obj, dict) and field in section_obj) or field in layers


def _clean_hex(hex_str: Any) -> str:
    if not hex_str:
        return ""
    return str(hex_str).replace(":", "").replace(" ", "").lower()

def iso_z_to_unix_float(s: str) -> float:
    # Expect e.g. 2023-03-25T12:23:36.835880000Z
    s = s.strip()
    try:
        return float(s)
    except ValueError:
        pass

    if s.endswith("Z"):
        s = s[:-1] + "+00:00"  # Z -> UTC offset for fromisoformat

    # Trim fractional seconds to 6 digits (microseconds) if present
    if "." in s:
        main, rest = s.split(".", 1)              # main: ...T12:23:36
        frac, offset = rest[:rest.find("+")], rest[rest.find("+"):]  # frac, +00:00
        frac = (frac[:6]).ljust(6, "0")           # keep 6 digits
        s = f"{main}.{frac}{offset}"

    dt = datetime.fromisoformat(s)
    return dt.timestamp()

def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


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


def _iter_pcap_packets(file_path: str):
    reader = PcapReader(file_path)
    try:
        for packet in reader:
            yield packet
    finally:
        reader.close()


def _iter_packet_payload_messages(file_path: str, service_port: int | None = None) -> Iterator[MessageRecord]:
    session_counts: Dict[str, int] = defaultdict(int)
    source_name = Path(file_path).name

    for packet in _iter_pcap_packets(file_path):
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

        yield MessageRecord(
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
        )
        session_counts[session_key] += 1


def _packet_payload_messages(file_path: str, service_port: int | None = None) -> List[MessageRecord]:
    return list(_iter_packet_payload_messages(file_path, service_port=service_port))


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


def _slice_l2_payload(frame_raw: Any, protocol_name: str) -> str | None:
    ethertype = L2_ETHERTYPES.get(protocol_name.lower())
    if not ethertype:
        return None

    hex_str = _clean_hex(frame_raw)
    for index in range(24, len(hex_str) - 4, 2):
        if hex_str[index : index + 4] == ethertype:
            return hex_str[index + 4 :]
    return None


def _slice_l7_payload_fallback(frame_raw: Any) -> str | None:
    hex_str = _clean_hex(frame_raw)
    if len(hex_str) < 28:
        return None

    ethertype = hex_str[24:28]
    ip_start_byte = 14
    if ethertype == "8100":
        ethertype = hex_str[32:36]
        ip_start_byte = 18

    if ethertype != "0800":
        return None

    ip_start_hex = ip_start_byte * 2
    try:
        ihl = int(hex_str[ip_start_hex + 1], 16)
        ip_proto = int(hex_str[ip_start_hex + 18 : ip_start_hex + 20], 16)
    except (ValueError, IndexError):
        return None

    ip_header_len = ihl * 4
    l4_start_byte = ip_start_byte + ip_header_len
    l4_start_hex = l4_start_byte * 2

    if ip_proto == 6:
        try:
            data_offset = int(hex_str[l4_start_hex + 24], 16)
        except (ValueError, IndexError):
            return None
        tcp_header_len = data_offset * 4
        payload_start = l4_start_byte + tcp_header_len
        return hex_str[payload_start * 2 :]

    if ip_proto == 17:
        payload_start = l4_start_byte + 8
        return hex_str[payload_start * 2 :]

    return None


def _extract_actual_tshark_payload(packet: Dict[str, Any]) -> str | None:
    protocol = str(packet.get("protocol", "unknown")).lower()
    metadata = packet.get("metadata", {})
    frame_raw = metadata.get("frame", {}).get("raw", "") if isinstance(metadata, dict) else ""

    if protocol in L2_ETHERTYPES:
        return _slice_l2_payload(frame_raw, protocol)

    tcp_meta = metadata.get("tcp") if isinstance(metadata, dict) else None
    if isinstance(tcp_meta, dict):
        payload = tcp_meta.get("payload")
        if payload and payload != "None":
            return _clean_hex(payload)

    udp_meta = metadata.get("udp") if isinstance(metadata, dict) else None
    if isinstance(udp_meta, dict):
        payload = udp_meta.get("payload")
        if payload and payload != "None":
            return _clean_hex(payload)

    return _slice_l7_payload_fallback(frame_raw)


def _tshark_protocol_name(tshark_filter: str) -> str:
    token = tshark_filter.strip().lower().split()[0] if tshark_filter.strip() else "unknown"
    return token.strip("()")


def _infer_tshark_protocol(layers: Dict[str, Any], tshark_filter: str) -> str:
    filter_text = tshark_filter.lower()
    for protocol_name in L2_ETHERTYPES:
        if protocol_name in layers or protocol_name in filter_text:
            return protocol_name
    if "tcp" in layers:
        return "tcp"
    if "udp" in layers:
        return "udp"
    protocol_name = _tshark_protocol_name(tshark_filter)
    return protocol_name if protocol_name in layers else "unknown"


def _tshark_cache_stem(pcap_path: Path, tshark_filter: str) -> str:
    filter_hash = hashlib.sha1(tshark_filter.encode("utf-8")).hexdigest()[:12]
    return f"{pcap_path.name}.{filter_hash}"


def _extract_tshark_packets(
    pcap_path: str,
    tshark_filter: str,
    max_packets: int | None = None,
) -> List[Dict[str, Any]]:
    cmd = [
        "tshark",
        "-r",
        pcap_path,
        "-o",
        "tcp.desegment_tcp_streams:true",
        "-o",
        "tcp.reassemble_out_of_order:true",
        "-o",
        "ip.defragment:true",
        "-x",
        "-Y",
        f"({tshark_filter})",
        "-T",
        "ek",
    ]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError("tshark is required for --extraction-method tshark but was not found on PATH.") from exc

    packets: List[Dict[str, Any]] = []
    assert proc.stdout is not None
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "layers" not in obj or not isinstance(obj["layers"], dict):
            continue

        layers = obj["layers"]
        found_protocol = _infer_tshark_protocol(layers, tshark_filter)
        frame_raw = _first(layers.get("frame_raw")) or _get_nested_field(layers, "frame", "frame_raw")
        metadata = {
            "frame": {
                "number": _get_nested_field(layers, "frame", "frame_frame_number"),
                "time_epoch": _get_nested_field(layers, "frame", "frame_frame_time_epoch"),
                "raw": frame_raw,
            },
            "eth": {
                "src": _get_nested_field(layers, "eth", "eth_eth_src"),
                "dst": _get_nested_field(layers, "eth", "eth_eth_dst"),
                "type": _get_nested_field(layers, "eth", "eth_eth_type"),
            },
            "ip": {
                "src": _get_nested_field(layers, "ip", "ip_ip_src"),
                "dst": _get_nested_field(layers, "ip", "ip_ip_dst"),
                "id": _get_nested_field(layers, "ip", "ip_ip_id"),
                "proto": _get_nested_field(layers, "ip", "ip_ip_proto"),
                "flags": _get_nested_field(layers, "ip", "ip_ip_flags"),
                "frag_offset": _get_nested_field(layers, "ip", "ip_ip_frag_offset"),
            },
            "tcp": {
                "stream": _get_nested_field(layers, "tcp", "tcp_tcp_stream"),
                "srcport": _get_nested_field(layers, "tcp", "tcp_tcp_srcport"),
                "dstport": _get_nested_field(layers, "tcp", "tcp_tcp_dstport"),
                "seq": _get_nested_field(layers, "tcp", "tcp_tcp_seq"),
                "ack": _get_nested_field(layers, "tcp", "tcp_tcp_ack"),
                "len": _get_nested_field(layers, "tcp", "tcp_tcp_len"),
                "flags": _get_nested_field(layers, "tcp", "tcp_tcp_flags"),
                "window_size": _get_nested_field(layers, "tcp", "tcp_tcp_window_size"),
                "analysis": {
                    "retransmission": _has_nested_field(layers, "tcp", "tcp_analysis_retransmission")
                    or _has_nested_field(layers, "tcp", "tcp_tcp_analysis_retransmission"),
                    "out_of_order": _has_nested_field(layers, "tcp", "tcp_analysis_out_of_order")
                    or _has_nested_field(layers, "tcp", "tcp_tcp_analysis_out_of_order"),
                    "lost_segment": _has_nested_field(layers, "tcp", "tcp_analysis_lost_segment")
                    or _has_nested_field(layers, "tcp", "tcp_tcp_analysis_lost_segment"),
                },
                "payload": _clean_hex(_get_nested_field(layers, "tcp", "tcp_tcp_payload")),
            },
            "udp": {
                "srcport": _get_nested_field(layers, "udp", "udp_udp_srcport"),
                "dstport": _get_nested_field(layers, "udp", "udp_udp_dstport"),
                "length": _get_nested_field(layers, "udp", "udp_udp_length"),
                "checksum": _get_nested_field(layers, "udp", "udp_udp_checksum"),
                "payload": _clean_hex(_get_nested_field(layers, "udp", "udp_udp_payload")),
            },
        }
        if found_protocol != "unknown" and frame_raw:
            packets.append({"protocol": found_protocol, "metadata": metadata})
            if max_packets is not None and len(packets) >= max_packets:
                proc.terminate()
                break

    proc.wait()
    return packets


def _payloads_from_tshark_packets(packets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    payloads: List[Dict[str, Any]] = []
    for packet in packets:
        tcp_meta = packet.get("metadata", {}).get("tcp")
        if isinstance(tcp_meta, dict) and tcp_meta.get("analysis", {}).get("retransmission") is True:
            continue

        payload_hex = _extract_actual_tshark_payload(packet)
        if payload_hex:
            payloads.append(
                {
                    "timestamp": packet.get("metadata", {}).get("frame", {}).get("time_epoch", ""),
                    "protocol": packet.get("protocol"),
                    "payload_hex": payload_hex,
                    "metadata": packet.get("metadata", {}),
                }
            )
    return payloads


def _tshark_payload_record_to_message(
    payload_record: Dict[str, Any],
    pcap_name: str,
    index_in_session: int,
) -> MessageRecord:
    metadata = payload_record.get("metadata", {})
    ip_meta = metadata.get("ip", {}) if isinstance(metadata, dict) else {}
    tcp_meta = metadata.get("tcp", {}) if isinstance(metadata, dict) else {}
    udp_meta = metadata.get("udp", {}) if isinstance(metadata, dict) else {}
    eth_meta = metadata.get("eth", {}) if isinstance(metadata, dict) else {}

    src_ip = str(ip_meta.get("src") or eth_meta.get("src") or "unknown")
    dst_ip = str(ip_meta.get("dst") or eth_meta.get("dst") or "unknown")
    if tcp_meta.get("stream") is not None or tcp_meta.get("payload"):
        src_port = _safe_int(tcp_meta.get("srcport"))
        dst_port = _safe_int(tcp_meta.get("dstport"))
        l4 = "tcp"
    elif udp_meta.get("srcport") is not None or udp_meta.get("payload"):
        src_port = _safe_int(udp_meta.get("srcport"))
        dst_port = _safe_int(udp_meta.get("dstport"))
        l4 = "udp"
    else:
        src_port = 0
        dst_port = 0
        l4 = "l2"

    stream = tcp_meta.get("stream") if isinstance(tcp_meta, dict) else None
    if stream is not None:
        session_key = f"tcp.stream:{stream}"
    else:
        session_key = _canonical_session_key(src_ip, src_port, dst_ip, dst_port)
    session_id = f"{pcap_name}:{session_key}"
    payload_hex = str(payload_record.get("payload_hex") or "")

    return MessageRecord(
        msg_id=-1,
        source_file=pcap_name,
        session_id=session_id,
        session_key=session_key,
        src_ip=src_ip,
        src_port=src_port,
        dst_ip=dst_ip,
        dst_port=dst_port,
        direction="unknown",
        payload_hex=payload_hex,
        payload_len=len(payload_hex) // 2,
        timestamp=iso_z_to_unix_float(str(payload_record.get("timestamp"))),        
        index_in_session=index_in_session,
    )


def _process_tshark_pcap_worker(args: Tuple[str, str, str, str]) -> Tuple[str, int, List[MessageRecord]]:
    pcap_path_str, tshark_filter, packets_dir, payloads_dir = args
    pcap_path = Path(pcap_path_str)
    cache_stem = _tshark_cache_stem(pcap_path, tshark_filter)
    packet_json = Path(packets_dir) / f"{cache_stem}.json"
    payload_json = Path(payloads_dir) / f"{cache_stem}.json"

    packet_records = []
    if not os.path.exists(packet_json):
        packet_records = _extract_tshark_packets(str(pcap_path), tshark_filter)
        with open(packet_json, "w", encoding="utf-8") as handle:
            json.dump(packet_records, handle, indent=4)
    else:
        with open(packet_json, "r", encoding="utf-8") as handle:
            packet_records = json.load(handle)

    payload_records = []
    if not os.path.exists(payload_json):
        payload_records = _payloads_from_tshark_packets(packet_records)
        with open(payload_json, "w", encoding="utf-8") as handle:
            json.dump(
                [
                    {
                        "timestamp": item.get("timestamp", ""),
                        "protocol": item.get("protocol"),
                        "payload_hex": item.get("payload_hex"),
                        # "metadata": item.get("metadata", {}),
                    }
                    for item in payload_records
                ],
                handle,
                indent=4,
            )
    else:
        with open(payload_json, "r", encoding="utf-8") as handle:
            payload_records = json.load(handle)

    session_counts: Dict[str, int] = defaultdict(int)
    messages: List[MessageRecord] = []
    for payload_record in payload_records:
        temp_message = _tshark_payload_record_to_message(
            payload_record,
            pcap_path.name,
            index_in_session=0,
        )
        temp_message.index_in_session = session_counts[temp_message.session_id]
        session_counts[temp_message.session_id] += 1
        messages.append(temp_message)
    return pcap_path.name, len(packet_records), messages


def _stream_reassembled_messages(file_path: str, service_port: int | None = None) -> List[MessageRecord]:
    source_name = Path(file_path).name
    segments_by_flow: Dict[FlowKey, List[TcpSegment]] = defaultdict(list)

    for packet in _iter_pcap_packets(file_path):
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
                            "tcp_start_seq": chunk.start_seq + stream_offset,
                            "tcp_end_seq": chunk.start_seq + stream_offset + len(payload),
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


def iter_messages_from_pcaps(
    pcap_dir: str,
    service_port: int | None = None,
    reassembly_mode: str = "packet",
    max_messages: int | None = None,
) -> Iterator[MessageRecord]:
    _require_scapy()
    pcap_paths = [str(path) for path in sorted(Path(pcap_dir).iterdir()) if path.suffix.lower() in {".pcap", ".pcapng"}]
    next_msg_id = 0

    for path in pcap_paths:
        if reassembly_mode == "packet":
            messages = _iter_packet_payload_messages(path, service_port=service_port)
        elif reassembly_mode == "stream":
            messages = iter(_stream_reassembled_messages(path, service_port=service_port))
        else:
            raise ValueError(f"Unsupported reassembly mode: {reassembly_mode}")

        for message in messages:
            message.msg_id = next_msg_id
            yield message
            next_msg_id += 1
            if max_messages is not None and next_msg_id >= max_messages:
                return


def iter_messages_from_pcaps_tshark(
    pcap_dir: str,
    tshark_filter: str,
    packets_dir: str,
    payloads_dir: str,
    max_messages: int | None = None,
    max_workers: int = 4,
) -> Iterator[MessageRecord]:
    packets_path = Path(packets_dir)
    payloads_path = Path(payloads_dir)
    packets_path.mkdir(parents=True, exist_ok=True)
    payloads_path.mkdir(parents=True, exist_ok=True)

    pcap_paths = [path for path in sorted(Path(pcap_dir).iterdir()) if path.suffix.lower() in {".pcap", ".pcapng"}]
    next_msg_id = 0

    if max_workers <= 1 or len(pcap_paths) <= 1:
        for pcap_path in pcap_paths:
            _, _, messages = _process_tshark_pcap_worker((str(pcap_path), tshark_filter, str(packets_path), str(payloads_path)))
            for message in messages:
                message.msg_id = next_msg_id
                yield message
                next_msg_id += 1
                if max_messages is not None and next_msg_id >= max_messages:
                    return
        return

    worker_count = min(max_workers, os.cpu_count() or 1, len(pcap_paths))
    next_submit_index = 0
    next_emit_index = 0
    pending: Dict[Any, int] = {}
    completed: Dict[int, List[MessageRecord]] = {}

    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        while next_submit_index < len(pcap_paths) and len(pending) < worker_count:
            pcap_path = pcap_paths[next_submit_index]
            future = executor.submit(
                _process_tshark_pcap_worker,
                (str(pcap_path), tshark_filter, str(packets_path), str(payloads_path)),
            )
            pending[future] = next_submit_index
            next_submit_index += 1

        while pending:
            for future in as_completed(tuple(pending.keys())):
                completed[pending.pop(future)] = future.result()[2]
                break

            while next_emit_index in completed:
                messages = completed.pop(next_emit_index)
                for message in messages:
                    message.msg_id = next_msg_id
                    yield message
                    next_msg_id += 1
                    if max_messages is not None and next_msg_id >= max_messages:
                        for future in pending:
                            future.cancel()
                        return
                next_emit_index += 1

                while next_submit_index < len(pcap_paths) and len(pending) < worker_count:
                    if max_messages is not None and next_msg_id >= max_messages:
                        break
                    pcap_path = pcap_paths[next_submit_index]
                    future = executor.submit(
                        _process_tshark_pcap_worker,
                        (str(pcap_path), tshark_filter, str(packets_path), str(payloads_path)),
                    )
                    pending[future] = next_submit_index
                    next_submit_index += 1


def write_messages_from_pcaps_jsonl(
    pcap_dir: str,
    output_path: str,
    service_port: int | None = None,
    reassembly_mode: str = "packet",
    max_messages: int | None = None,
) -> int:
    count = 0
    with open(output_path, "w", encoding="utf-8") as handle:
        for message in iter_messages_from_pcaps(
            pcap_dir,
            service_port=service_port,
            reassembly_mode=reassembly_mode,
            max_messages=max_messages,
        ):
            handle.write(json.dumps(message.to_dict(), sort_keys=True) + "\n")
            count += 1
    return count


def write_messages_from_pcaps_tshark_jsonl(
    pcap_dir: str,
    output_path: str,
    tshark_filter: str,
    packets_dir: str,
    payloads_dir: str,
    max_messages: int | None = None,
    max_workers: int = 4,
) -> int:
    count = 0
    with open(output_path, "w", encoding="utf-8") as handle:
        for message in iter_messages_from_pcaps_tshark(
            pcap_dir,
            tshark_filter=tshark_filter,
            packets_dir=packets_dir,
            payloads_dir=payloads_dir,
            max_messages=max_messages,
            max_workers=max_workers,
        ):
            handle.write(json.dumps(message.to_dict(), sort_keys=True) + "\n")
            count += 1
    return count


def write_messages_jsonl(messages: Iterable[MessageRecord], output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as handle:
        for message in messages:
            handle.write(json.dumps(message.to_dict(), sort_keys=True) + "\n")
