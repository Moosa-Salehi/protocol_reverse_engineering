#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from protocol_re.export.llm_evidence import build_llm_evidence_bundle


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a compact per-family evidence bundle for downstream LLM analysis.")
    parser.add_argument("protocol_model_json", help="Input protocol model JSON from 12_build_protocol_model.py")
    parser.add_argument("output_json", help="Output compact evidence bundle JSON")
    parser.add_argument("--family-limit", type=int, help="Optional maximum number of largest families to include")
    parser.add_argument("--vector-limit", type=int, default=16, help="Number of vector entries/top offsets to retain per vector")
    parser.add_argument("--relation-limit", type=int, default=10, help="Max relation summaries to retain per family")
    args = parser.parse_args()

    with open(args.protocol_model_json, "r", encoding="utf-8") as handle:
        model = json.load(handle)

    bundle = build_llm_evidence_bundle(
        model,
        family_limit=args.family_limit,
        vector_limit=args.vector_limit,
        relation_limit=args.relation_limit,
    )

    with open(args.output_json, "w", encoding="utf-8") as handle:
        json.dump(bundle, handle, indent=2)

    print(f"[+] Wrote LLM evidence bundle with {len(bundle['families'])} families to {args.output_json}")


if __name__ == "__main__":
    main()
