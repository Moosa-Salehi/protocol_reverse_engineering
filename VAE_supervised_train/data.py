from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterator, Sequence

import numpy as np
import torch
from torch.utils.data import Dataset, Sampler

from .common import read_jsonl


class MessageFamilyDataset(Dataset):
    def __init__(self, path, protocols: set[str] | None = None, max_len: int = 256,
                 min_confidence: float = 0.0, min_family_support: int = 1) -> None:
        rows = read_jsonl(path)
        rows = [row for row in rows if (protocols is None or row["protocol_id"] in protocols)
                and float(row["annotation_confidence"]) >= min_confidence]
        counts = Counter((row["protocol_id"], row["trusted_family_id"]) for row in rows)
        self.rows = [row for row in rows if counts[(row["protocol_id"], row["trusted_family_id"])] >= min_family_support]
        keys = sorted({(row["protocol_id"], row["trusted_family_id"]) for row in self.rows})
        self.key_to_label = {key: index for index, key in enumerate(keys)}
        self.labels = np.asarray([self.key_to_label[(row["protocol_id"], row["trusted_family_id"])] for row in self.rows])
        self.max_len = max_len

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int):
        payload = bytes.fromhex(self.rows[index]["payload_hex"])[:self.max_len]
        ids = torch.full((self.max_len,), 256, dtype=torch.long)
        mask = torch.zeros(self.max_len, dtype=torch.float32)
        if payload:
            ids[:len(payload)] = torch.tensor(list(payload), dtype=torch.long)
            mask[:len(payload)] = 1.0
        return ids, mask, int(self.labels[index]), index


class FamilyBalancedBatchSampler(Sampler[list[int]]):
    def __init__(self, labels: Sequence[int], families_per_batch: int, examples_per_family: int,
                 batches_per_epoch: int | None, seed: int) -> None:
        self.groups: dict[int, np.ndarray] = {}
        for label in sorted(set(int(x) for x in labels)):
            self.groups[label] = np.flatnonzero(np.asarray(labels) == label)
        self.families_per_batch = min(families_per_batch, len(self.groups))
        self.examples_per_family = examples_per_family
        natural = max(1, len(labels) // max(1, self.families_per_batch * examples_per_family))
        self.batches_per_epoch = batches_per_epoch or natural
        self.seed = seed
        self.epoch = 0

    def set_epoch(self, epoch: int) -> None:
        self.epoch = epoch

    def __len__(self) -> int:
        return self.batches_per_epoch

    def __iter__(self) -> Iterator[list[int]]:
        rng = np.random.default_rng(self.seed + self.epoch)
        family_ids = np.asarray(list(self.groups))
        for _ in range(self.batches_per_epoch):
            chosen = rng.choice(family_ids, self.families_per_batch, replace=False)
            batch = []
            for family in chosen:
                indexes = self.groups[int(family)]
                batch.extend(rng.choice(indexes, self.examples_per_family,
                                        replace=len(indexes) < self.examples_per_family).tolist())
            rng.shuffle(batch)
            yield batch
