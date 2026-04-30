#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from protocol_re.export.llm_evidence import build_llm_evidence_bundle


def _load_optional_json(path: str | None):
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a compact per-family evidence bundle for downstream LLM analysis.")
    parser.add_argument("protocol_model_json", help="Input protocol model JSON from 12_build_protocol_model.py")
    parser.add_argument("output_json", help="Output compact evidence bundle JSON")
    parser.add_argument("--evaluation-json", help="Optional evaluation report JSON from 13_evaluate_pipeline.py")
    parser.add_argument("--family-limit", type=int, default=30, help="Optional maximum number of largest families to include")
    parser.add_argument("--relation-limit", type=int, default=8, help="Max global relation summaries to retain")
    parser.add_argument("--field-limit", type=int, default=8, help="Max field/semantic hypotheses to retain per family and global candidate type")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON; omitted by default to keep LLM evidence compact")
    args = parser.parse_args()

    with open(args.protocol_model_json, "r", encoding="utf-8") as handle:
        model = json.load(handle)

    bundle = build_llm_evidence_bundle(
        model,
        evaluation=_load_optional_json(args.evaluation_json),
        family_limit=args.family_limit,
        relation_limit=args.relation_limit,
        field_limit=args.field_limit,
    )

    with open(args.output_json, "w", encoding="utf-8") as handle:
        if args.pretty:
            json.dump(bundle, handle, indent=2)
        else:
            json.dump(bundle, handle, separators=(",", ":"))

    print(f"[+] Wrote LLM evidence bundle with {len(bundle['families'])} families to {args.output_json}")


if __name__ == "__main__":
    main()
