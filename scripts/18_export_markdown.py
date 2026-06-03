#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.export.markdown import render_protocol_model_markdown
from protocol_re.utils.logging import setup_stage_logging


def _load_optional_json(path: str | None):
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _estimate_tokens(text: str) -> int:
    return max(1, (len(text.encode("utf-8")) + 3) // 4) if text else 0


def _load_prompt_stats(llm_analysis: dict | None, llm_analysis_path: str | None = None) -> dict | None:
    if not llm_analysis:
        return None
    prompt_path = llm_analysis.get("prompt_path")
    if not prompt_path:
        if not llm_analysis_path:
            return None
        prompt_path = Path(llm_analysis_path).with_name("13_llm_prompt.md")
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
    parser = argparse.ArgumentParser(description="Render a human-readable Markdown protocol specification from protocol_model.json.")
    parser.add_argument("protocol_model_json")
    parser.add_argument("output_md")
    parser.add_argument("--evaluation-json", help="Optional evaluation report JSON from 13_evaluate_pipeline.py")
    parser.add_argument("--llm-analysis-json", help="Optional LLM analysis JSON from 15_analyze_with_llm.py")
    parser.add_argument("--final-evaluation-json", help="Optional final evaluation report JSON from 17_evaluate_protocol_spec.py")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("18_export_markdown", Path(args.log_dir))

    logger.info("Exporting Markdown protocol specification")

    with logger.stage("load_protocol_model"):
        logger.info(f"Loading protocol model from {args.protocol_model_json}")
        with open(args.protocol_model_json, "r", encoding="utf-8") as handle:
            model = json.load(handle)
        logger.metric("families_in_model", len(model.get("families", [])), "families")

    with logger.stage("load_optional_data"):
        llm_analysis = _load_optional_json(args.llm_analysis_json)
        if llm_analysis is not None:
            logger.info(f"Loaded LLM analysis from {args.llm_analysis_json}")
            llm_analysis["prompt_stats"] = _load_prompt_stats(llm_analysis, args.llm_analysis_json)

        evaluation = _load_optional_json(args.evaluation_json)
        if evaluation:
            logger.info(f"Loaded evaluation from {args.evaluation_json}")

        final_evaluation = _load_optional_json(args.final_evaluation_json)
        if final_evaluation:
            logger.info(f"Loaded final evaluation from {args.final_evaluation_json}")

    with logger.stage("render_markdown"):
        markdown = render_protocol_model_markdown(
            model,
            evaluation=evaluation,
            llm_analysis=llm_analysis,
            final_evaluation=final_evaluation,
        )
        logger.metric("markdown_size", len(markdown), "characters")
        logger.metric("markdown_lines", markdown.count('\n'), "lines")

    with logger.stage("write_output"):
        with open(args.output_md, "w", encoding="utf-8") as handle:
            handle.write(markdown)
        logger.info(f"Wrote Markdown specification to {args.output_md}")

    print(f"[+] Wrote Markdown protocol specification to {args.output_md}")

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
