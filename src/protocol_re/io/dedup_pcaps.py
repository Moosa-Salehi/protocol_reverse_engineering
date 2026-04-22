from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass
class DuplicatePcap:
    duplicate_path: str
    original_path: str
    sha256: str


def sha256_file(path: str, block_size: int = 65536) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(block_size), b""):
            digest.update(block)
    return digest.hexdigest()


def find_duplicate_pcaps(folder: str) -> List[DuplicatePcap]:
    seen_by_hash: Dict[str, str] = {}
    duplicates: List[DuplicatePcap] = []

    for path in sorted(Path(folder).rglob("*")):
        if not path.is_file():
            continue
        file_hash = sha256_file(str(path))
        if file_hash in seen_by_hash:
            duplicates.append(
                DuplicatePcap(
                    duplicate_path=str(path),
                    original_path=seen_by_hash[file_hash],
                    sha256=file_hash,
                )
            )
        else:
            seen_by_hash[file_hash] = str(path)

    return duplicates


def remove_duplicates(duplicates: Iterable[DuplicatePcap]) -> int:
    removed = 0
    for duplicate in duplicates:
        path = Path(duplicate.duplicate_path)
        if path.exists():
            path.unlink()
            removed += 1
    return removed
