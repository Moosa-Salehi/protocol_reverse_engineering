#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from protocol_re.export.markdown import render_protocol_model_markdown


def _load_optional_json(path: str | None):
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a human-readable Markdown protocol specification from protocol_model.json.")
    parser.add_argument("protocol_model_json")
    parser.add_argument("output_md")
    parser.add_argument("--evaluation-json", help="Optional evaluation report JSON from 13_evaluate_pipeline.py")
    parser.add_argument("--llm-analysis-json", help="Optional LLM analysis JSON from 15_analyze_with_llm.py")
    parser.add_argument("--final-evaluation-json", help="Optional final evaluation report JSON from 17_evaluate_protocol_spec.py")
    args = parser.parse_args()

    with open(args.protocol_model_json, "r", encoding="utf-8") as handle:
        model = json.load(handle)

    markdown = render_protocol_model_markdown(
        model,
        evaluation=_load_optional_json(args.evaluation_json),
        llm_analysis=_load_optional_json(args.llm_analysis_json),
        final_evaluation=_load_optional_json(args.final_evaluation_json),
    )
    with open(args.output_md, "w", encoding="utf-8") as handle:
        handle.write(markdown)

    print(f"[+] Wrote Markdown protocol specification to {args.output_md}")


if __name__ == "__main__":
    main()
