from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from dataclasses import asdict
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

from protocol_re.model.schema import MessageRecord
from protocol_re.utils.bytes import hex_to_bytes

_SESSION_RE = re.compile(
    r"^(?P<src_ip>[^:]+):(?P<src_port>\d+) -> (?P<dst_ip>[^:]+):(?P<dst_port>\d+)$"
)


def parse_session_key(session_key: str) -> Tuple[str, int, str, int]:
    match = _SESSION_RE.match(session_key.strip())
    if not match:
        raise ValueError(f"Unrecognized session key format: {session_key!r}")
    return (
        match.group("src_ip"),
        int(match.group("src_port")),
        match.group("dst_ip"),
        int(match.group("dst_port")),
    )


def infer_direction(src_port: int, dst_port: int, service_port: Optional[int] = None) -> str:
    if service_port is None:
        return "unknown"
    if dst_port == service_port and src_port != service_port:
        return "client_to_server"
    if src_port == service_port and dst_port != service_port:
        return "server_to_client"
    return "unknown"


def iter_message_records(
    json_folder_path: str,
    service_port: Optional[int] = None,
    deduplicate_payloads: bool = False,
) -> Iterator[MessageRecord]:
    next_msg_id = 0
    seen_payloads = set()

    for filename in sorted(os.listdir(json_folder_path)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(json_folder_path, filename)
        with open(filepath, "r", encoding="utf-8") as handle:
            data = json.load(handle)

        for session_index, (session_key, payloads) in enumerate(sorted(data.items())):
            src_ip, src_port, dst_ip, dst_port = parse_session_key(session_key)
            session_id = f"{filename}:{session_index}"
            direction_hint = infer_direction(src_port, dst_port, service_port=service_port)

            for index_in_session, payload_hex in enumerate(payloads):
                payload_hex = payload_hex.strip().lower()
                if deduplicate_payloads and payload_hex in seen_payloads:
                    continue
                seen_payloads.add(payload_hex)
                payload_len = len(hex_to_bytes(payload_hex))
                yield MessageRecord(
                    msg_id=next_msg_id,
                    source_file=filename,
                    session_id=session_id,
                    session_key=session_key,
                    src_ip=src_ip,
                    src_port=src_port,
                    dst_ip=dst_ip,
                    dst_port=dst_port,
                    # The legacy extracted JSON format stores one order-independent
                    # session key plus a payload list, so per-message direction is
                    # no longer trustworthy at this stage.
                    direction="unknown",
                    payload_hex=payload_hex,
                    payload_len=payload_len,
                    index_in_session=index_in_session,
                    metadata={
                        "service_port": service_port,
                        "session_direction_hint": direction_hint,
                    },
                )
                next_msg_id += 1


def build_corpus(
    json_folder_path: str,
    service_port: Optional[int] = None,
    deduplicate_payloads: bool = False,
    max_messages: Optional[int] = None,
) -> List[MessageRecord]:
    records = []
    for record in iter_message_records(
        json_folder_path,
        service_port=service_port,
        deduplicate_payloads=deduplicate_payloads,
    ):
        records.append(record)
        if max_messages is not None and len(records) >= max_messages:
            break
    return records


def write_corpus_jsonl(records: Sequence[MessageRecord], output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")


def load_corpus_jsonl(input_path: str) -> List[MessageRecord]:
    return list(iter_corpus_jsonl(input_path))


def iter_corpus_jsonl(input_path: str) -> Iterator[MessageRecord]:
    with open(input_path, "r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            item = json.loads(line)
            yield MessageRecord(**item)


def group_messages_by_session(records: Iterable[MessageRecord]) -> Dict[str, List[MessageRecord]]:
    grouped: Dict[str, List[MessageRecord]] = defaultdict(list)
    for record in records:
        grouped[record.session_id].append(record)
    for session_records in grouped.values():
        session_records.sort(key=lambda record: record.index_in_session)
    return dict(grouped)
