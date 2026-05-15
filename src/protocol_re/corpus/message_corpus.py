from __future__ import annotations

import json
from collections import defaultdict
from typing import Dict, Iterable, Iterator, List

from protocol_re.model.schema import MessageRecord


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
