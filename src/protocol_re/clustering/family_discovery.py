from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from protocol_re.model.schema import FamilyAssignment, MessageRecord
from protocol_re.utils.bytes import hex_to_bytes, pad_messages

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None

try:
    import hdbscan
except Exception:  # pragma: no cover - optional dependency
    hdbscan = None

try:
    from sklearn.cluster import DBSCAN
    from sklearn.decomposition import PCA
except Exception:  # pragma: no cover - optional dependency
    DBSCAN = None
    PCA = None


@dataclass
class ClusteringResult:
    assignments: List[FamilyAssignment]
    labels: List[int]
    sample_size: int
    feature_shape: tuple[int, int]



def unique_messages(records: Sequence[MessageRecord]) -> List[MessageRecord]:
    seen = set()
    unique: List[MessageRecord] = []
    for record in records:
        if record.payload_hex in seen:
            continue
        seen.add(record.payload_hex)
        unique.append(record)
    return unique



def vectorize_messages(records: Sequence[MessageRecord]) -> np.ndarray: # type: ignore
    messages = [hex_to_bytes(record.payload_hex) for record in records]
    if np is None:
        raise RuntimeError("NumPy is required for vectorization-based clustering")
    max_len = max((len(msg) for msg in messages), default=0)
    matrix = np.zeros((len(messages), max_len), dtype=np.uint8)
    for idx, msg in enumerate(messages):
        matrix[idx, : len(msg)] = list(msg)
    return matrix



def maybe_reduce_dimensions(matrix: np.ndarray, n_components: int | None = None) -> np.ndarray: # pyright: ignore[reportInvalidTypeForm]
    if n_components is None or PCA is None or matrix.size == 0:
        return matrix
    if matrix.shape[1] <= 1:
        return matrix
    n_components = min(n_components, matrix.shape[0], matrix.shape[1])
    if n_components <= 1:
        return matrix
    return PCA(n_components=n_components).fit_transform(matrix)


def heuristic_family_assignments(records: Sequence[MessageRecord]) -> ClusteringResult:
    assignments: List[FamilyAssignment] = []
    labels: List[int] = []
    label_by_bucket = {}

    for record in records:
        bucket = (record.payload_len, record.payload_hex[:4])
        if bucket not in label_by_bucket:
            label_by_bucket[bucket] = len(label_by_bucket)
        label = label_by_bucket[bucket]
        labels.append(label)
        assignments.append(FamilyAssignment(msg_id=record.msg_id, family_id=f"family_{label}", confidence=0.5))

    return ClusteringResult(
        assignments=assignments,
        labels=labels,
        sample_size=len(records),
        feature_shape=(len(records), 2),
    )



def discover_families(
    records: Sequence[MessageRecord],
    method: str = "hdbscan",
    sample_size: int | None = None,
    pca_components: int | None = 32,
    dbscan_eps: float = 40.0,
    dbscan_min_samples: int = 5,
    hdbscan_min_cluster_size: int = 50,
) -> ClusteringResult:
    working_records = unique_messages(records)
    if sample_size is not None and len(working_records) > sample_size:
        working_records = working_records[:sample_size]

    if np is None or (method == "dbscan" and DBSCAN is None) or (method == "hdbscan" and hdbscan is None):
        return heuristic_family_assignments(working_records)

    matrix = vectorize_messages(working_records)
    reduced = maybe_reduce_dimensions(matrix, pca_components)

    if method == "dbscan":
        if DBSCAN is None:
            raise RuntimeError("scikit-learn is required for DBSCAN clustering")
        labels = DBSCAN(eps=dbscan_eps, min_samples=dbscan_min_samples, metric="euclidean").fit_predict(reduced)
    elif method == "hdbscan":
        if hdbscan is None:
            raise RuntimeError("hdbscan is required for HDBSCAN clustering")
        labels = hdbscan.HDBSCAN(min_cluster_size=hdbscan_min_cluster_size, allow_single_cluster=True).fit_predict(reduced)
    else:
        raise ValueError(f"Unsupported clustering method: {method}")

    assignments = []
    for record, label in zip(working_records, labels):
        family_id = "noise" if label == -1 else f"family_{label}"
        assignments.append(FamilyAssignment(msg_id=record.msg_id, family_id=family_id, confidence=1.0))

    return ClusteringResult(
        assignments=assignments,
        labels=labels.tolist() if hasattr(labels, "tolist") else list(labels),
        sample_size=len(working_records),
        feature_shape=tuple(reduced.shape),
    )
