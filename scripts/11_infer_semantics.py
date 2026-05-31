#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.inference.semantic_labeling import summarize_semantics
from protocol_re.utils.logging import setup_stage_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Infer semantic labels for families and fields from boundaries plus request-response relations.")
    parser.add_argument("family_json", help="Output from 07_infer_boundaries.py")
    parser.add_argument("relations_json", help="Output from 10_infer_relations.py")
    parser.add_argument("output_json", help="Output JSON file for semantic summaries")
    parser.add_argument("--framing-json", help="Optional framing hypotheses from 05_infer_framing.py")
    parser.add_argument("--features-json", help="Optional family features from 06_extract_features.py")
    parser.add_argument("--keywords-json", help="Optional keyword/discriminator data from 09_infer_keywords.py")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("11_infer_semantics", Path(args.log_dir))

    logger.info("Inferring semantic labels from boundaries and relations")

    with logger.stage("load_required_data"):
        logger.info(f"Loading family data from {args.family_json}")
        with open(args.family_json, "r", encoding="utf-8") as handle:
            family_data = json.load(handle)
        logger.metric("families_loaded", len(family_data), "families")

        logger.info(f"Loading relations from {args.relations_json}")
        with open(args.relations_json, "r", encoding="utf-8") as handle:
            relations_data = json.load(handle)
        logger.metric("relations_loaded", len(relations_data.get("family_edges", [])), "relations")

    with logger.stage("load_optional_evidence"):
        # Load optional evidence sources
        framing_data = None
        if args.framing_json:
            logger.info(f"Loading framing from {args.framing_json}")
            with open(args.framing_json, "r", encoding="utf-8") as handle:
                framing_data = json.load(handle)

        features_data = None
        if args.features_json:
            logger.info(f"Loading features from {args.features_json}")
            with open(args.features_json, "r", encoding="utf-8") as handle:
                features_data = json.load(handle)

        keywords_data = None
        if args.keywords_json:
            logger.info(f"Loading keywords from {args.keywords_json}")
            with open(args.keywords_json, "r", encoding="utf-8") as handle:
                keywords_data = json.load(handle)

    with logger.stage("infer_semantics"):
        semantics = summarize_semantics(
            family_data,
            relations_data,
            framing_data=framing_data,
            features_data=features_data,
            keywords_data=keywords_data,
        )
        logger.metric("families_with_semantics", len(semantics), "families")

    # Report semantic inference statistics
    total_labels = sum(len(sem.get("field_labels", [])) for sem in semantics.values())
    unique_roles = set()
    for sem in semantics.values():
        for label in sem.get("field_labels", []):
            unique_roles.add(label.get("label", "unknown"))

    logger.metric("total_semantic_labels", total_labels, "labels")
    logger.metric("unique_semantic_roles", len(unique_roles), "roles")

    if unique_roles:
        logger.info(f"Detected semantic roles: {', '.join(sorted(unique_roles))}")

    with logger.stage("write_output"):
        with open(args.output_json, "w", encoding="utf-8") as handle:
            json.dump(semantics, handle, indent=2)
        logger.info(f"Wrote semantic summaries to {args.output_json}")

    print(f"[+] Wrote semantic summaries for {len(semantics)} families to {args.output_json}")
    print(f"[+] Generated {total_labels} semantic labels across {len(unique_roles)} unique roles")
    if unique_roles:
        print(f"[+] Detected roles: {', '.join(sorted(unique_roles))}")

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
