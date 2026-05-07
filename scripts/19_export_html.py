#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from protocol_re.export.html import render_protocol_model_html


def _load_optional_json(path: str | None):
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _estimate_tokens(text: str) -> int:
    return max(1, (len(text.encode("utf-8")) + 3) // 4) if text else 0


def _load_prompt_stats(llm_analysis: dict | None) -> dict | None:
    if not llm_analysis:
        return None
    prompt_path = llm_analysis.get("prompt_path")
    if not prompt_path:
        return None
    path = Path(str(prompt_path))
    if not path.is_file():
        return {"path": str(path), "exists": False}
    text = path.read_text(encoding="utf-8")
    return {
        "path": str(path),
        "exists": True,
        "bytes": len(text.encode("utf-8")),
        "characters": len(text),
        "estimated_tokens": _estimate_tokens(text),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a self-contained HTML protocol report from protocol_model.json.")
    parser.add_argument("protocol_model_json")
    parser.add_argument("output_html")
    parser.add_argument("--evaluation-json", help="Optional evaluation report JSON from 13_evaluate_pipeline.py")
    parser.add_argument("--llm-analysis-json", help="Optional LLM analysis JSON from 15_analyze_with_llm.py")
    parser.add_argument("--final-evaluation-json", help="Optional final evaluation report JSON from 17_evaluate_protocol_spec.py")
    args = parser.parse_args()

    with open(args.protocol_model_json, "r", encoding="utf-8") as handle:
        model = json.load(handle)
    llm_analysis = _load_optional_json(args.llm_analysis_json)
    if llm_analysis is not None:
        llm_analysis["prompt_stats"] = _load_prompt_stats(llm_analysis)

    html = render_protocol_model_html(
        model,
        evaluation=_load_optional_json(args.evaluation_json),
        llm_analysis=llm_analysis,
        final_evaluation=_load_optional_json(args.final_evaluation_json),
    )
    with open(args.output_html, "w", encoding="utf-8") as handle:
        handle.write(html)

    print(f"[+] Wrote HTML protocol report to {args.output_html}")


if __name__ == "__main__":
    main()
