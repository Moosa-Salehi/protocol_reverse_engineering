from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from statistics import mean
from typing import Any, Dict, List, Mapping, Sequence

from protocol_re.model.schema import FamilyAssignment, MessageRecord
from protocol_re.utils.bytes import hex_to_bytes

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None

try:
    from sklearn.metrics import silhouette_samples, silhouette_score
except Exception:  # pragma: no cover - optional dependency
    silhouette_samples = None
    silhouette_score = None


def _round(value: Any, digits: int = 6) -> float | None:
    try:
        return round(float(value), digits)
    except Exception:
        return None


def _ratio(counter: Counter[Any]) -> float:
    total = sum(counter.values())
    if not total:
        return 0.0
    return round(counter.most_common(1)[0][1] / total, 6)


def _length_consistency(records: Sequence[MessageRecord]) -> float:
    return _ratio(Counter(record.payload_len for record in records))


def _direction_consistency(records: Sequence[MessageRecord]) -> float:
    usable = [record.direction for record in records if record.direction]
    return _ratio(Counter(usable))


def _discriminator_consistency(records: Sequence[MessageRecord], max_offsets: int = 8) -> float:
    payloads = [hex_to_bytes(record.payload_hex) for record in records]
    if not payloads:
        return 0.0
    max_offset = min(max_offsets, max((len(payload) for payload in payloads), default=0))
    best = 0.0
    for offset in range(max_offset):
        values = [payload[offset] for payload in payloads if len(payload) > offset]
        if len(values) < max(2, len(payloads) // 2):
            continue
        best = max(best, _ratio(Counter(values)))
    return round(best, 6)


def _family_layout_signature(details: Mapping[str, Any]) -> tuple[tuple[Any, ...], ...]:
    fields = details.get("field_hypotheses", []) or []
    if fields:
        return tuple(
            sorted(
                (
                    int(field.get("start", 0) or 0),
                    int(field.get("length", 0) or 0),
                    str(field.get("field_type", "unknown")),
                )
                for field in fields[:16]
            )
        )
    segments = details.get("segments", []) or []
    return tuple(
        (int(segment.get("start", 0) or 0), int(segment.get("end", 0) or 0), str(segment.get("kind", "unknown")))
        for segment in segments[:16]
    )


def _layout_consistency(details: Mapping[str, Any]) -> float | None:
    confidences: List[float] = []
    for field in details.get("field_hypotheses", []) or []:
        confidences.append(float(field.get("confidence", 0.0) or 0.0))
    for segment in details.get("segments", []) or []:
        confidences.append(float(segment.get("confidence", 0.0) or 0.0))
    if not confidences:
        return None
    return round(mean(confidences), 6)


def _layouts_compatible(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    left_signature = _family_layout_signature(left)
    right_signature = _family_layout_signature(right)
    if not left_signature or not right_signature:
        return True
    left_set = set(left_signature)
    right_set = set(right_signature)
    overlap = len(left_set & right_set) / max(1, min(len(left_set), len(right_set)))
    return overlap >= 0.6


def _symbolically_compatible(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return (
        float(left.get("length_profile_consistency", 0.0) or 0.0) >= 0.6
        and float(right.get("length_profile_consistency", 0.0) or 0.0) >= 0.6
        and abs(float(left.get("mean_length", 0.0) or 0.0) - float(right.get("mean_length", 0.0) or 0.0))
        <= max(8.0, 0.25 * max(float(left.get("mean_length", 0.0) or 0.0), float(right.get("mean_length", 0.0) or 0.0)))
        and float(left.get("direction_consistency", 0.0) or 0.0) >= 0.7
        and float(right.get("direction_consistency", 0.0) or 0.0) >= 0.7
    )


def _latent_metrics(
    latent_matrix: object | None,
    latent_records: Sequence[MessageRecord],
    assignment_by_msg_id: Mapping[int, FamilyAssignment],
    max_silhouette_samples: int,
) -> tuple[Dict[str, Dict[str, Any]], Dict[str, Any], Dict[tuple[str, str], float]]:
    if np is None or latent_matrix is None or not latent_records:
        return {}, {"latent_available": False}, {}
    matrix = np.asarray(latent_matrix, dtype=np.float32)
    if matrix.ndim != 2 or matrix.shape[0] != len(latent_records) or matrix.shape[0] == 0:
        return {}, {"latent_available": False}, {}

    labels = []
    row_indexes_by_family: Dict[str, List[int]] = defaultdict(list)
    for index, record in enumerate(latent_records):
        assignment = assignment_by_msg_id.get(record.msg_id)
        family_id = assignment.family_id if assignment else "unassigned"
        labels.append(family_id)
        if family_id not in {"noise", "unassigned"}:
            row_indexes_by_family[family_id].append(index)

    centroids = {
        family_id: matrix[indexes].mean(axis=0)
        for family_id, indexes in row_indexes_by_family.items()
        if indexes
    }
    centroid_distances: Dict[tuple[str, str], float] = {}
    for left, right in combinations(sorted(centroids), 2):
        centroid_distances[(left, right)] = float(np.linalg.norm(centroids[left] - centroids[right]))

    silhouette_by_family: Dict[str, List[float]] = defaultdict(list)
    usable_labels = [label for label in labels if label not in {"noise", "unassigned"}]
    global_silhouette = None
    if len(set(usable_labels)) >= 2 and silhouette_score is not None and silhouette_samples is not None:
        usable_indexes = [index for index, label in enumerate(labels) if label not in {"noise", "unassigned"}]
        if len(usable_indexes) > max_silhouette_samples:
            step = max(1, len(usable_indexes) // max_silhouette_samples)
            usable_indexes = usable_indexes[::step][:max_silhouette_samples]
        sample_matrix = matrix[usable_indexes]
        sample_labels = [labels[index] for index in usable_indexes]
        try:
            global_silhouette = float(silhouette_score(sample_matrix, sample_labels, metric="euclidean"))
            for label, score in zip(sample_labels, silhouette_samples(sample_matrix, sample_labels, metric="euclidean")):
                silhouette_by_family[label].append(float(score))
        except Exception:
            global_silhouette = None

    family_metrics: Dict[str, Dict[str, Any]] = {}
    for family_id, indexes in row_indexes_by_family.items():
        rows = matrix[indexes]
        centroid = centroids[family_id]
        distances = np.linalg.norm(rows - centroid, axis=1)
        nearest = None
        for pair, distance in centroid_distances.items():
            if family_id in pair:
                nearest = distance if nearest is None else min(nearest, distance)
        if len(rows) > 1:
            density_rows = rows
            if len(density_rows) > 500:
                step = max(1, len(density_rows) // 500)
                density_rows = density_rows[::step][:500]
            centered_distances = np.linalg.norm(density_rows[:, None, :] - density_rows[None, :, :], axis=2)
            k = min(5, len(density_rows) - 1)
            knn = np.partition(centered_distances, kth=k, axis=1)[:, 1 : k + 1]
            density = 1.0 / (1.0 + float(knn.mean())) if knn.size else None
        else:
            density = None
        scores = silhouette_by_family.get(family_id, [])
        family_metrics[family_id] = {
            "latent_dispersion": _round(distances.mean() if len(distances) else 0.0),
            "latent_dispersion_max": _round(distances.max() if len(distances) else 0.0),
            "latent_silhouette": _round(mean(scores)) if scores else None,
            "nearest_family_distance": _round(nearest),
            "density_estimate": _round(density),
            "latent_sample_count": len(indexes),
        }

    global_metrics = {
        "latent_available": True,
        "latent_dim": int(matrix.shape[1]),
        "latent_sample_count": int(matrix.shape[0]),
        "latent_silhouette": _round(global_silhouette),
    }
    return family_metrics, global_metrics, centroid_distances


def build_family_diagnostics(
    records: Sequence[MessageRecord],
    assignments: Sequence[FamilyAssignment],
    latent_matrix: object | None = None,
    latent_records: Sequence[MessageRecord] | None = None,
    max_silhouette_samples: int = 5000,
) -> Dict[str, Any]:
    assignment_by_msg_id = {assignment.msg_id: assignment for assignment in assignments}
    records_by_family: Dict[str, List[MessageRecord]] = defaultdict(list)
    for record in records:
        assignment = assignment_by_msg_id.get(record.msg_id)
        if assignment is not None:
            records_by_family[assignment.family_id].append(record)

    latent_family_metrics, global_metrics, centroid_distances = _latent_metrics(
        latent_matrix,
        latent_records or [],
        assignment_by_msg_id,
        max_silhouette_samples,
    )

    family_diagnostics: Dict[str, Dict[str, Any]] = {}
    for family_id, family_records in records_by_family.items():
        lengths = [record.payload_len for record in family_records]
        metrics = dict(latent_family_metrics.get(family_id, {}))
        metrics.update(
            {
                "family_id": family_id,
                "message_count": len(family_records),
                "mean_length": _round(mean(lengths)) if lengths else 0.0,
                "length_profile_consistency": _length_consistency(family_records),
                "discriminator_consistency": _discriminator_consistency(family_records),
                "direction_consistency": _direction_consistency(family_records),
                "field_layout_consistency": None,
                "split_suspicion": 0.0,
                "under_split_score": 0.0,
                "over_split_score": 0.0,
                "merge_candidates": [],
                "diagnostic_warnings": [],
            }
        )
        family_diagnostics[family_id] = metrics

    _score_diagnostics(family_diagnostics, centroid_distances, families_payload=None)
    return {
        "schema_version": 1,
        "global": {
            **global_metrics,
            "family_count": len(family_diagnostics),
            "noise_ratio": round(len(records_by_family.get("noise", [])) / len(assignments), 6) if assignments else 0.0,
        },
        "families": family_diagnostics,
    }


def augment_diagnostics_with_layouts(diagnostics: Dict[str, Any], families_payload: Mapping[str, Any]) -> Dict[str, Any]:
    output = dict(diagnostics or {})
    families = {family_id: dict(details) for family_id, details in (output.get("families", {}) or {}).items()}
    for family_id, details in families.items():
        if family_id in families_payload:
            details["field_layout_consistency"] = _layout_consistency(families_payload.get(family_id, {}) or {})
    output["families"] = families
    _score_diagnostics(families, {}, families_payload=families_payload)
    output["summary"] = diagnostic_summary(output)
    return output


def _score_diagnostics(
    families: Dict[str, Dict[str, Any]],
    centroid_distances: Mapping[tuple[str, str], float],
    families_payload: Mapping[str, Any] | None,
) -> None:
    dispersions = [float(item.get("latent_dispersion", 0.0) or 0.0) for item in families.values() if item.get("latent_dispersion") is not None]
    high_dispersion = sorted(dispersions)[int(0.75 * (len(dispersions) - 1))] if dispersions else None
    distances = sorted(float(value) for value in centroid_distances.values())
    low_distance = distances[int(0.25 * (len(distances) - 1))] if distances else None

    for family_id, details in families.items():
        warnings: List[str] = []
        if details.get("merge_candidates"):
            warnings.append("possible over-split merge candidate")
        dispersion = float(details.get("latent_dispersion", 0.0) or 0.0)
        discriminator = float(details.get("discriminator_consistency", 0.0) or 0.0)
        length_consistency = float(details.get("length_profile_consistency", 0.0) or 0.0)
        direction = float(details.get("direction_consistency", 0.0) or 0.0)
        layout = details.get("field_layout_consistency")
        layout_value = float(layout) if layout is not None else 1.0
        silhouette = details.get("latent_silhouette")
        silhouette_value = float(silhouette) if silhouette is not None else 0.5

        split_score = 0.0
        if high_dispersion is not None and dispersion > high_dispersion:
            split_score += 0.3
            warnings.append("high latent dispersion")
        if discriminator < 0.75:
            split_score += 0.25
            warnings.append("mixed discriminator values")
        if length_consistency < 0.65:
            split_score += 0.2
            warnings.append("mixed length profile")
        if direction < 0.75:
            split_score += 0.1
            warnings.append("mixed directions")
        if layout is not None and layout_value < 0.6:
            split_score += 0.25
            warnings.append("low field-layout consistency")
        if silhouette is not None and silhouette_value < 0.1:
            split_score += 0.2
            warnings.append("low latent silhouette")

        details["split_suspicion"] = round(min(1.0, split_score), 6)
        details["under_split_score"] = details["split_suspicion"]
        if family_id == "noise":
            warnings.append("noise family")
        details["diagnostic_warnings"] = sorted(set(warnings))

    for (left, right), distance in centroid_distances.items():
        left_details = families.get(left)
        right_details = families.get(right)
        if not left_details or not right_details or low_distance is None or distance > low_distance:
            continue
        layout_ok = True
        if families_payload is not None:
            layout_ok = _layouts_compatible(families_payload.get(left, {}) or {}, families_payload.get(right, {}) or {})
        if not (_symbolically_compatible(left_details, right_details) and layout_ok):
            continue
        proximity = 1.0 - min(1.0, distance / max(low_distance, 1e-9)) if low_distance > 0 else 1.0
        score = round(max(0.1, proximity), 6)
        candidate_left = {"family_id": right, "distance": round(distance, 6), "score": score, "reason": "near latent centroid with compatible symbolic layout"}
        candidate_right = {"family_id": left, "distance": round(distance, 6), "score": score, "reason": "near latent centroid with compatible symbolic layout"}
        left_details.setdefault("merge_candidates", []).append(candidate_left)
        right_details.setdefault("merge_candidates", []).append(candidate_right)
        left_details["over_split_score"] = round(max(float(left_details.get("over_split_score", 0.0) or 0.0), score), 6)
        right_details["over_split_score"] = round(max(float(right_details.get("over_split_score", 0.0) or 0.0), score), 6)
        left_details.setdefault("diagnostic_warnings", []).append("possible over-split merge candidate")
        right_details.setdefault("diagnostic_warnings", []).append("possible over-split merge candidate")

    for details in families.values():
        details["merge_candidates"] = sorted(
            details.get("merge_candidates", []) or [],
            key=lambda item: (-float(item.get("score", 0.0) or 0.0), float(item.get("distance", 0.0) or 0.0)),
        )[:5]
        details["diagnostic_warnings"] = sorted(set(details.get("diagnostic_warnings", []) or []))


def diagnostic_summary(diagnostics: Mapping[str, Any]) -> Dict[str, Any]:
    families = diagnostics.get("families", {}) or {}
    family_items = [item for family_id, item in families.items() if family_id != "noise"]
    warnings = [(family_id, item) for family_id, item in families.items() if item.get("diagnostic_warnings")]
    merge_candidates = []
    for family_id, item in families.items():
        for candidate in item.get("merge_candidates", []) or []:
            merge_candidates.append(
                {
                    "family_id": family_id,
                    "candidate_family_id": candidate.get("family_id"),
                    **{key: value for key, value in candidate.items() if key != "family_id"},
                }
            )
    return {
        "family_count": len(families),
        "warning_family_count": len(warnings),
        "split_candidate_count": sum(1 for item in family_items if float(item.get("split_suspicion", 0.0) or 0.0) >= 0.5),
        "merge_candidate_count": len(merge_candidates),
        "top_warning_families": [
            {
                "family_id": family_id,
                "message_count": item.get("message_count", 0),
                "split_suspicion": item.get("split_suspicion", 0.0),
                "under_split_score": item.get("under_split_score", 0.0),
                "over_split_score": item.get("over_split_score", 0.0),
                "diagnostic_warnings": item.get("diagnostic_warnings", [])[:5],
            }
            for family_id, item in sorted(
                warnings,
                key=lambda pair: (
                    -float(pair[1].get("split_suspicion", 0.0) or 0.0),
                    -float(pair[1].get("over_split_score", 0.0) or 0.0),
                    -int(pair[1].get("message_count", 0) or 0),
                ),
            )[:20]
        ],
        "top_merge_candidates": sorted(
            merge_candidates,
            key=lambda item: (-float(item.get("score", 0.0) or 0.0), float(item.get("distance", 0.0) or 0.0)),
        )[:20],
    }
