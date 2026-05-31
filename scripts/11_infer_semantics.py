#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from protocol_re.inference.semantic_labeling import summarize_semantics


def main() -> None:
    parser = argparse.ArgumentParser(description="Infer semantic labels for families and fields from boundaries plus request-response relations.")
    parser.add_argument("family_json", help="Output from 07_infer_boundaries.py")
    parser.add_argument("relations_json", help="Output from 10_infer_relations.py")
    parser.add_argument("output_json", help="Output JSON file for semantic summaries")
    parser.add_argument("--framing-json", help="Optional framing hypotheses from 05_infer_framing.py")
    parser.add_argument("--features-json", help="Optional family features from 06_extract_features.py")
    parser.add_argument("--keywords-json", help="Optional keyword/discriminator data from 09_infer_keywords.py")
    args = parser.parse_args()

    with open(args.family_json, "r", encoding="utf-8") as handle:
        family_data = json.load(handle)
    with open(args.relations_json, "r", encoding="utf-8") as handle:
        relations_data = json.load(handle)

    # Load optional evidence sources
    framing_data = None
    if args.framing_json:
        with open(args.framing_json, "r", encoding="utf-8") as handle:
            framing_data = json.load(handle)

    features_data = None
    if args.features_json:
        with open(args.features_json, "r", encoding="utf-8") as handle:
            features_data = json.load(handle)

    keywords_data = None
    if args.keywords_json:
        with open(args.keywords_json, "r", encoding="utf-8") as handle:
            keywords_data = json.load(handle)

    semantics = summarize_semantics(
        family_data,
        relations_data,
        framing_data=framing_data,
        features_data=features_data,
        keywords_data=keywords_data,
    )
    with open(args.output_json, "w", encoding="utf-8") as handle:
        json.dump(semantics, handle, indent=2)

    print(f"[+] Wrote semantic summaries for {len(semantics)} families to {args.output_json}")

    # Report semantic inference statistics
    total_labels = sum(len(sem.get("field_labels", [])) for sem in semantics.values())
    unique_roles = set()
    for sem in semantics.values():
        for label in sem.get("field_labels", []):
            unique_roles.add(label.get("label", "unknown"))

    print(f"[+] Generated {total_labels} semantic labels across {len(unique_roles)} unique roles")
    if unique_roles:
        print(f"[+] Detected roles: {', '.join(sorted(unique_roles))}")


if __name__ == "__main__":
    main()
