from __future__ import annotations

from collections import defaultdict
import warnings
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Sequence

from protocol_re.clustering.diagnostics import build_family_diagnostics
from protocol_re.clustering.hybrid_features import build_feature_matrix
from protocol_re.clustering.latent_standardize import LatentStandardizer
from protocol_re.clustering.structural_features import downweight_raw_byte_matrix
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
    feature_mode: str = "raw_bytes"
    requested_feature_mode: str = "raw_bytes"
    neural_model: str | None = None
    latent_dim: int = 0
    latent_cache: str | None = None
    symbolic_feature_count: int = 0
    fallback_reason: str | None = None
    diagnostics: Dict[str, Any] | None = None



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
        feature_mode="heuristic",
        requested_feature_mode="heuristic",
    )


def _propagate_assignments(
    records: Sequence[MessageRecord],
    sampled_assignments: Sequence[FamilyAssignment],
    sampled_records: Sequence[MessageRecord],
    reduced_sample_matrix: object | None = None,
    reducer: Any | None = None,
    vector_width: int | None = None,
    unsampled_matrix_builder: Callable[[Sequence[MessageRecord]], object] | None = None,
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
        if unsampled_matrix_builder is not None:
            unsampled_matrix = unsampled_matrix_builder(batch)
        else:
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
    feature_mode: str = "raw_bytes",
    neural_model_path: str | None = None,
    latent_cache_path: str | None = None,
    neural_batch_size: int = 256,
    fusion_method: str = "adaptive",  # New parameter for learned fusion
    fusion_neural_weight: float | None = None,  # Manual weight for fixed fusion
    fusion_structural_weight: float | None = None,  # Manual weight for fixed fusion
    layer_aware: bool = False,  # A6: Enable layer-aware clustering
    framing_data: Dict[str, Any] | None = None,  # A6: Framing data for layer detection
    layer_min_confidence: float = 0.6,  # A6: Minimum confidence for layer detection
    standardize_latent: bool = True,  # Deterministic per-corpus z-score of latent features
) -> ClusteringResult:
    if feature_mode not in {"raw_bytes", "structural", "neural", "hybrid"}:
        raise ValueError(f"Unsupported feature mode: {feature_mode}")

    working_records = unique_messages(records)
    if sample_size is not None and len(working_records) > sample_size:
        working_records = working_records[:sample_size]

    unavailable_dependencies = []
    if np is None:
        unavailable_dependencies.append("numpy")
    if method == "dbscan" and DBSCAN is None:
        unavailable_dependencies.append("scikit_learn_dbscan")
    if method == "hdbscan" and hdbscan is None:
        unavailable_dependencies.append("hdbscan")

    if unavailable_dependencies:
        result = heuristic_family_assignments(records)
        return ClusteringResult(
            assignments=result.assignments,
            labels=result.labels,
            sample_size=len(working_records),
            feature_shape=result.feature_shape,
            feature_mode="heuristic",
            requested_feature_mode=feature_mode,
            neural_model=neural_model_path,
            latent_cache=latent_cache_path,
            fallback_reason="dependency_unavailable:" + ",".join(unavailable_dependencies),
            diagnostics=build_family_diagnostics(records, result.assignments),
        )

    feature_info = None
    latent_matrix = None
    unsampled_matrix_builder = None
    vector_width = None
    if feature_mode == "raw_bytes":
        matrix = vectorize_messages(working_records)
        matrix = downweight_raw_byte_matrix(matrix, working_records, corpus_records=records)
        vector_width = int(matrix.shape[1])

        def build_raw_unsampled(batch: Sequence[MessageRecord]) -> object:
            raw_matrix = vectorize_messages(batch, width=vector_width)
            return downweight_raw_byte_matrix(raw_matrix, batch, corpus_records=records)

        unsampled_matrix_builder = build_raw_unsampled
        actual_feature_mode = "raw_bytes"
        requested_feature_mode = feature_mode
        neural_model = None
        latent_dim = 0
        latent_cache = None
        symbolic_feature_count = 0
        fallback_reason = None
    else:
        # One standardizer is fit on the sampled matrix below and reused for every
        # unsampled batch, keeping sampled centroids and batched assignments in a single
        # latent coordinate system (a fresh per-batch fit would not).
        latent_standardizer = LatentStandardizer() if standardize_latent else None

        feature_info = build_feature_matrix(
            working_records,
            records,
            feature_mode=feature_mode,
            model_path=neural_model_path,
            latent_cache_path=latent_cache_path,
            neural_batch_size=neural_batch_size,
            fusion_method=fusion_method,  # Pass fusion method
            neural_weight=fusion_neural_weight,
            structural_weight=fusion_structural_weight,
            latent_standardizer=latent_standardizer,
        )
        matrix = feature_info.matrix
        if feature_info.latent_dim > 0:
            latent_matrix = np.asarray(matrix)[:, : feature_info.latent_dim]

        def build_feature_unsampled(batch: Sequence[MessageRecord]) -> object:
            return build_feature_matrix(
                batch,
                records,
                feature_mode=feature_mode,
                model_path=neural_model_path,
                latent_cache_path=latent_cache_path,
                neural_batch_size=neural_batch_size,
                fusion_method=fusion_method,  # Pass fusion method
                neural_weight=fusion_neural_weight,
                structural_weight=fusion_structural_weight,
                latent_standardizer=latent_standardizer,
            ).matrix

        unsampled_matrix_builder = build_feature_unsampled
        actual_feature_mode = feature_info.feature_mode
        requested_feature_mode = feature_info.requested_feature_mode
        neural_model = feature_info.neural_model
        latent_dim = feature_info.latent_dim
        latent_cache = feature_info.latent_cache
        symbolic_feature_count = feature_info.symbolic_feature_count
        fallback_reason = feature_info.fallback_reason
    reduced, reducer = maybe_reduce_dimensions(matrix, pca_components)

    if method == "dbscan":
        if DBSCAN is None:
            raise RuntimeError("scikit-learn is required for DBSCAN clustering")
        labels = DBSCAN(eps=dbscan_eps, min_samples=dbscan_min_samples, metric="euclidean").fit_predict(reduced)
    elif method == "hdbscan":
        if hdbscan is None:
            raise RuntimeError("hdbscan is required for HDBSCAN clustering")
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=".*force_all_finite.*ensure_all_finite.*",
                category=FutureWarning,
            )
            labels = hdbscan.HDBSCAN(min_cluster_size=hdbscan_min_cluster_size, allow_single_cluster=True).fit_predict(reduced)
    else:
        raise ValueError(f"Unsupported clustering method: {method}")

    sampled_assignments = []
    for record, label in zip(working_records, labels):
        family_id = "noise" if label == -1 else f"family_{label}"
        sampled_assignments.append(FamilyAssignment(msg_id=record.msg_id, family_id=family_id, confidence=1.0))

    assignments = _propagate_assignments(
        records,
        sampled_assignments,
        working_records,
        reduced_sample_matrix=reduced,
        reducer=reducer,
        vector_width=vector_width,
        unsampled_matrix_builder=unsampled_matrix_builder,
    )
    diagnostics = build_family_diagnostics(
        records,
        assignments,
        latent_matrix=latent_matrix,
        latent_records=working_records if latent_matrix is not None else None,
    )

    return ClusteringResult(
        assignments=assignments,
        labels=labels.tolist() if hasattr(labels, "tolist") else list(labels),
        sample_size=len(working_records),
        feature_shape=tuple(reduced.shape),
        feature_mode=actual_feature_mode,
        requested_feature_mode=requested_feature_mode,
        neural_model=neural_model,
        latent_dim=latent_dim,
        latent_cache=latent_cache,
        symbolic_feature_count=symbolic_feature_count,
        fallback_reason=fallback_reason,
        diagnostics=diagnostics,
    )
