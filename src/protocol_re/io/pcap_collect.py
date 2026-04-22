from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass
class CollectedPcap:
    source_path: str
    target_path: str


def collect_pcaps(source_root: str, output_dir: str, suffixes: tuple[str, ...] = (".pcap", ".pcapng")) -> List[CollectedPcap]:
    source_root_path = Path(source_root)
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    collected: List[CollectedPcap] = []
    used_names = set()

    for path in sorted(source_root_path.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue

        candidate_name = path.name
        while candidate_name in used_names:
            stem = Path(candidate_name).stem
            suffix = Path(candidate_name).suffix
            candidate_name = f"{stem}-copy{suffix}"
        used_names.add(candidate_name)

        target_path = output_dir_path / candidate_name
        shutil.copy2(path, target_path)
        collected.append(CollectedPcap(source_path=str(path), target_path=str(target_path)))

    return collected
