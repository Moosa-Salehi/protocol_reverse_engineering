from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence

from protocol_re.model.schema import FamilyAssignment, MessageRecord
from protocol_re.utils.bytes import hex_to_bytes

CENTROID_ASSIGNMENT_BATCH_SIZE = 10000

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



def vectorize_messages(records: Sequence[MessageRecord], width: int | None = None) -> np.ndarray: # type: ignore
    messages = [hex_to_bytes(record.payload_hex) for record in records]
    if np is None:
        raise RuntimeError("NumPy is required for vectorization-based clustering")
    max_len = width if width is not None else max((len(msg) for msg in messages), default=0)
    matrix = np.zeros((len(messages), max_len), dtype=np.uint8)
    for idx, msg in enumerate(messages):
        clipped = msg[:max_len]
        matrix[idx, : len(clipped)] = list(clipped)
    return matrix



def maybe_reduce_dimensions(matrix: np.ndarray, n_components: int | None = None) -> tuple[np.ndarray, Any | None]: # pyright: ignore[reportInvalidTypeForm]
    if n_components is None or PCA is None or matrix.size == 0:
        return matrix, None
    if matrix.shape[1] <= 1:
        return matrix, None
    n_components = min(n_components, matrix.shape[0], matrix.shape[1])
    if n_components <= 1:
        return matrix, None
    reducer = PCA(n_components=n_components)
    return reducer.fit_transform(matrix), reducer


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


def _propagate_assignments(
    records: Sequence[MessageRecord],
    sampled_assignments: Sequence[FamilyAssignment],
    sampled_records: Sequence[MessageRecord],
    reduced_sample_matrix: object | None = None,
    reducer: Any | None = None,
    vector_width: int | None = None,
) -> List[FamilyAssignment]:
    assignment_by_msg_id = {assignment.msg_id: assignment for assignment in sampled_assignments}
    family_by_payload = {}
    for record in records:
        assignment = assignment_by_msg_id.get(record.msg_id)
        if assignment is not None:
            family_by_payload.setdefault(record.payload_hex, assignment.family_id)

    assignments = []
    for record in records:
        sampled_assignment = assignment_by_msg_id.get(record.msg_id)
        if sampled_assignment is not None:
            assignments.append(sampled_assignment)
            continue
        family_id = family_by_payload.get(record.payload_hex)
        if family_id is None:
            continue
        assignments.append(FamilyAssignment(msg_id=record.msg_id, family_id=family_id, confidence=0.95))

    if np is None or reduced_sample_matrix is None:
        return sorted(assignments, key=lambda assignment: assignment.msg_id)

    assigned_msg_ids = {assignment.msg_id for assignment in assignments}
    sampled_by_msg_id = {record.msg_id: index for index, record in enumerate(sampled_records)}
    labels_by_family: Dict[str, List[int]] = defaultdict(list)
    for assignment in sampled_assignments:
        if assignment.family_id == "noise":
            continue
        sample_index = sampled_by_msg_id.get(assignment.msg_id)
        if sample_index is not None:
            labels_by_family[assignment.family_id].append(sample_index)
    if not labels_by_family:
        return sorted(assignments, key=lambda assignment: assignment.msg_id)

    sample_matrix = np.asarray(reduced_sample_matrix)
    centroids = {
        family_id: sample_matrix[indexes].mean(axis=0)
        for family_id, indexes in labels_by_family.items()
        if indexes
    }
    if not centroids:
        return sorted(assignments, key=lambda assignment: assignment.msg_id)

    unique_unsampled = unique_messages([record for record in records if record.msg_id not in assigned_msg_ids])
    if not unique_unsampled:
        return sorted(assignments, key=lambda assignment: assignment.msg_id)

    family_ids = list(centroids)
    centroid_matrix = np.vstack([centroids[family_id] for family_id in family_ids])
    for start in range(0, len(unique_unsampled), CENTROID_ASSIGNMENT_BATCH_SIZE):
        batch = unique_unsampled[start : start + CENTROID_ASSIGNMENT_BATCH_SIZE]
        unsampled_matrix = vectorize_messages(batch, width=vector_width or int(sample_matrix.shape[1]))
        if reducer is not None:
            unsampled_matrix = reducer.transform(unsampled_matrix)
        for record, row in zip(batch, unsampled_matrix):
            distances = np.linalg.norm(centroid_matrix - row, axis=1)
            best_index = int(np.argmin(distances))
            family_by_payload[record.payload_hex] = family_ids[best_index]

    for record in records:
        if record.msg_id in assigned_msg_ids:
            continue
        family_id = family_by_payload.get(record.payload_hex)
        if family_id is None:
            continue
        assignments.append(FamilyAssignment(msg_id=record.msg_id, family_id=family_id, confidence=0.75))
    return sorted(assignments, key=lambda assignment: assignment.msg_id)



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
        result = heuristic_family_assignments(records)
        return ClusteringResult(
            assignments=result.assignments,
            labels=result.labels,
            sample_size=len(working_records),
            feature_shape=result.feature_shape,
        )

    matrix = vectorize_messages(working_records)
    reduced, reducer = maybe_reduce_dimensions(matrix, pca_components)

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

    sampled_assignments = []
    for record, label in zip(working_records, labels):
        family_id = "noise" if label == -1 else f"family_{label}"
        sampled_assignments.append(FamilyAssignment(msg_id=record.msg_id, family_id=family_id, confidence=1.0))

    return ClusteringResult(
        assignments=_propagate_assignments(
            records,
            sampled_assignments,
            working_records,
            reduced_sample_matrix=reduced,
            reducer=reducer,
            vector_width=int(matrix.shape[1]),
        ),
        labels=labels.tolist() if hasattr(labels, "tolist") else list(labels),
        sample_size=len(working_records),
        feature_shape=tuple(reduced.shape),
    )
