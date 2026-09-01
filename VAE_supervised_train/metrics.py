from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

import hdbscan
import numpy as np
from sklearn.metrics import (adjusted_mutual_info_score, adjusted_rand_score,
                             completeness_score, homogeneity_score, v_measure_score)
from sklearn.preprocessing import StandardScaler


def clustering_metrics(truth: np.ndarray, predicted: np.ndarray) -> dict[str, Any]:
    trusted_count = len(set(truth.tolist()))
    clusters = sorted(set(predicted.tolist()) - {-1})
    predicted_count = len(clusters)
    non_noise = predicted >= 0
    cluster_members = {cluster: np.flatnonzero(predicted == cluster) for cluster in clusters}
    pure = sum(max(Counter(truth[idx]).values()) for idx in cluster_members.values())
    assigned = int(non_noise.sum())
    purity = pure / assigned if assigned else 0.0
    family_clusters = defaultdict(set)
    for actual, cluster in zip(truth, predicted):
        if cluster >= 0:
            family_clusters[int(actual)].add(int(cluster))
    fragmented = sum(len(values) > 1 for values in family_clusters.values())
    merged_family_ids = set()
    for idx in cluster_members.values():
        members = set(truth[idx].tolist())
        if len(members) > 1:
            merged_family_ids.update(members)
    merged = len(merged_family_ids)
    noise_count = int((~non_noise).sum())
    return {
        "trusted_family_count": trusted_count,
        "predicted_cluster_count": predicted_count,
        "family_count_error": abs(predicted_count - trusted_count),
        "relative_family_count_error": abs(predicted_count - trusted_count) / max(1, trusted_count),
        "weighted_cluster_purity": purity, "weighted_cluster_impurity": 1.0 - purity,
        "merged_family_count": merged, "merged_family_rate": merged / max(1, trusted_count),
        "fragmented_family_count": fragmented, "fragmented_family_rate": fragmented / max(1, trusted_count),
        "noise_count": noise_count, "noise_fraction": noise_count / max(1, len(truth)),
        "adjusted_rand_index": adjusted_rand_score(truth, predicted),
        "adjusted_mutual_information": adjusted_mutual_info_score(truth, predicted),
        "homogeneity": homogeneity_score(truth, predicted), "completeness": completeness_score(truth, predicted),
        "v_measure": v_measure_score(truth, predicted), "message_count": len(truth),
    }


def run_hdbscan(embeddings: np.ndarray, min_cluster_size: int = 5, min_samples: int | None = None,
                cluster_selection_epsilon: float = 0.0, standardized: bool = False) -> np.ndarray:
    if len(embeddings) < 2:
        return np.full(len(embeddings), -1, dtype=int)
    scaled = embeddings if standardized else StandardScaler().fit_transform(embeddings)
    return hdbscan.HDBSCAN(min_cluster_size=min(min_cluster_size, len(embeddings)), min_samples=min_samples,
                           cluster_selection_epsilon=cluster_selection_epsilon,
                           cluster_selection_method="eom", allow_single_cluster=True).fit_predict(scaled)


def checkpoint_key(metrics: dict[str, Any]) -> tuple[float, ...]:
    return (metrics["family_count_error"], metrics["weighted_cluster_impurity"],
            metrics["merged_family_rate"] + metrics["fragmented_family_rate"], metrics["noise_fraction"])
