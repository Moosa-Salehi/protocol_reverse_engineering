#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from protocol_re.clustering.family_discovery import discover_families
from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.utils.logging import setup_stage_logging, ProgressTracker


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover message families from the canonical corpus.")
    parser.add_argument("input_jsonl")
    parser.add_argument("output_json")
    parser.add_argument("--method", choices=["dbscan", "hdbscan"], default="hdbscan")
    parser.add_argument("--sample-size", type=int, default=100000)
    parser.add_argument("--pca-components", type=int, default=32)
    parser.add_argument("--dbscan-eps", type=float, default=40.0)
    parser.add_argument("--dbscan-min-samples", type=int, default=5)
    parser.add_argument("--hdbscan-min-cluster-size", type=int, default=50)
    parser.add_argument("--feature-mode", choices=["raw_bytes", "structural", "neural", "hybrid"], default="raw_bytes")
    parser.add_argument("--neural-model-path", default="industrial_VAE.pth")
    parser.add_argument("--latent-cache-path")
    parser.add_argument("--neural-batch-size", type=int, default=256)
    parser.add_argument("--fusion-method", choices=["concat", "adaptive", "learned", "fixed"], default="adaptive",
                        help="Hybrid feature fusion method (default: adaptive)")
    parser.add_argument("--fusion-neural-weight", type=float, default=None,
                        help="Neural feature weight for --fusion-method fixed (0.0-1.0)")
    parser.add_argument("--fusion-structural-weight", type=float, default=None,
                        help="Structural feature weight for --fusion-method fixed (0.0-1.0)")
    parser.add_argument("--no-standardize-latent", dest="standardize_latent", action="store_false",
                        help="Disable deterministic per-corpus z-score of neural latent features (default: enabled)")
    parser.set_defaults(standardize_latent=True)
    parser.add_argument("--layer-aware", action="store_true", help="Enable layer-aware clustering (A6, experimental)")
    parser.add_argument("--framing-json", help="Framing JSON for layer detection (required with --layer-aware)")
    parser.add_argument("--layer-min-confidence", type=float, default=0.6, help="Minimum confidence for layer detection")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("04_discover_families", Path(args.log_dir))

    logger.info(f"Loading messages from {args.input_jsonl}")

    if args.layer_aware and not args.framing_json:
        logger.error("--framing-json is required when --layer-aware is enabled")
        print("[!] Error: --framing-json is required when --layer-aware is enabled", file=sys.stderr)
        sys.exit(1)

    with logger.stage("load_corpus"):
        records = load_corpus_jsonl(args.input_jsonl)
        logger.metric("message_count", len(records), "messages")
        logger.info(f"Loaded {len(records)} messages")

    framing_data = None
    if args.layer_aware and args.framing_json:
        # Framing (stage 05) runs after this stage, so on a clean first run the file
        # does not exist yet. Degrade gracefully instead of aborting the pipeline:
        # layer-aware clustering simply uses framing produced by a previous run, if any.
        if Path(args.framing_json).is_file():
            logger.info(f"Loading framing data from {args.framing_json}")
            with open(args.framing_json, "r", encoding="utf-8") as handle:
                framing_data = json.load(handle)
        else:
            logger.warning(
                "Layer-aware clustering requested but framing file not found (%s); "
                "proceeding without layer awareness. Re-run after framing exists to enable it.",
                args.framing_json,
            )
            print(
                f"[!] Warning: framing file not found ({args.framing_json}); "
                "layer-aware clustering disabled for this run.",
                file=sys.stderr,
            )
            args.layer_aware = False

    logger.info(f"Starting family discovery with method={args.method}, feature_mode={args.feature_mode}")
    logger.decision(
        decision=f"Using {args.method} clustering with {args.feature_mode} features",
        reason=f"User configuration",
        sample_size=args.sample_size,
        pca_components=args.pca_components,
    )

    with logger.stage("discover_families"):
        result = discover_families(
            records,
            method=args.method,
            sample_size=args.sample_size,
            pca_components=args.pca_components,
            dbscan_eps=args.dbscan_eps,
            dbscan_min_samples=args.dbscan_min_samples,
            hdbscan_min_cluster_size=args.hdbscan_min_cluster_size,
            feature_mode=args.feature_mode,
            neural_model_path=args.neural_model_path,
            latent_cache_path=args.latent_cache_path,
            neural_batch_size=args.neural_batch_size,
            fusion_method=args.fusion_method,
            fusion_neural_weight=args.fusion_neural_weight,
            fusion_structural_weight=args.fusion_structural_weight,
            standardize_latent=args.standardize_latent,
            layer_aware=args.layer_aware,
            framing_data=framing_data,
            layer_min_confidence=args.layer_min_confidence,
        )
    family_count = len({assignment.family_id for assignment in result.assignments})

    logger.metric("families_discovered", family_count, "families")
    logger.metric("assignments_created", len(result.assignments), "assignments")
    logger.metric("sample_size", result.sample_size, "messages")
    logger.metric("feature_shape", result.feature_shape)

    if result.feature_mode != result.requested_feature_mode or result.fallback_reason:
        logger.warning(
            f"Feature mode fallback: {result.requested_feature_mode} -> {result.feature_mode}",
            fallback_reason=result.fallback_reason or "unspecified"
        )
        logger.decision(
            decision=f"Fallback to {result.feature_mode} mode",
            reason=result.fallback_reason or "unspecified",
            requested_mode=result.requested_feature_mode,
            effective_mode=result.feature_mode,
        )

    requested_sample = args.sample_size if args.sample_size is not None else len(records)
    assignment_strategy = (
        "full_corpus_clustering"
        if result.sample_size >= len(records)
        else "sample_unique_then_duplicate_and_centroid_propagation"
    )

    payload = {
        "assignments": [assignment.to_dict() for assignment in result.assignments],
        "labels": result.labels,
        "sample_size": result.sample_size,
        "assigned_message_count": len(result.assignments),
        "total_message_count": len(records),
        "requested_sample_size": requested_sample,
        "assignment_strategy": assignment_strategy,
        "feature_shape": list(result.feature_shape),
        "diagnostics": result.diagnostics or {},
        "metadata": {
            "feature_mode": result.feature_mode,
            "requested_feature_mode": result.requested_feature_mode,
            "neural_model": result.neural_model,
            "latent_dim": result.latent_dim,
            "latent_cache": result.latent_cache,
            "symbolic_feature_count": result.symbolic_feature_count,
            "fallback_reason": result.fallback_reason,
        },
    }

    with logger.stage("write_output"):
        with open(args.output_json, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        logger.info(f"Wrote family assignments to {args.output_json}")

    print(f"[+] Family discovery clustering method: {args.method}")
    print(f"[+] Family discovery requested feature mode: {result.requested_feature_mode}")
    print(f"[+] Family discovery effective feature mode: {result.feature_mode}")
    if result.feature_mode != result.requested_feature_mode or result.fallback_reason:
        print(
            "[!] Warning: family discovery fallback applied "
            f"({result.requested_feature_mode} -> {result.feature_mode}); "
            f"reason: {result.fallback_reason or 'unspecified'}",
            file=sys.stderr,
        )
    print(f"[+] Discovered {family_count} families")
    print(f"[+] Wrote {len(result.assignments)} family assignments to {args.output_json}")

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
