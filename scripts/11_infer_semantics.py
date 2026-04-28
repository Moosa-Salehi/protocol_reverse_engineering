#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from protocol_re.inference.semantic_labeling import summarize_semantics


def main() -> None:
    parser = argparse.ArgumentParser(description="Infer semantic labels for families and fields from boundaries plus request-response relations.")
    parser.add_argument("family_json", help="Output from 06_infer_boundaries.py")
    parser.add_argument("relations_json", help="Output from 11_infer_relations.py")
    parser.add_argument("output_json", help="Output JSON file for semantic summaries")
    args = parser.parse_args()

    with open(args.family_json, "r", encoding="utf-8") as handle:
        family_data = json.load(handle)
    with open(args.relations_json, "r", encoding="utf-8") as handle:
        relations_data = json.load(handle)

    semantics = summarize_semantics(family_data, relations_data)
    with open(args.output_json, "w", encoding="utf-8") as handle:
        json.dump(semantics, handle, indent=2)

    print(f"[+] Wrote semantic summaries for {len(semantics)} families to {args.output_json}")


if __name__ == "__main__":
    main()
