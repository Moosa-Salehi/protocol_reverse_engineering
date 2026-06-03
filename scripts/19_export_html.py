#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.export.html import render_protocol_model_html
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


def _load_stage_result(result_path: Path) -> dict:
    result = _load_optional_json(str(result_path))
    return {
        "result_path": str(result_path),
        "result": result or {},
    }


def _family_id_from_stage_filename(path: Path, prefix: str) -> str:
    name = path.name
    suffix = ".json"
    if not name.startswith(prefix) or not name.endswith(suffix):
        return ""
    return name[len(prefix):-len(suffix)]


def _load_family_stage_results(results_dir: Path, prefix: str) -> dict:
    by_family = {}
    for result_path in sorted(results_dir.glob(f"{prefix}*.json")):
        family_id = _family_id_from_stage_filename(result_path, prefix)
        if not family_id:
            continue
        by_family[family_id] = _load_stage_result(result_path)
    return by_family


def _load_llm_stage_results(results_dir: str | None, protocol_model_path: str) -> dict | None:
    candidates = []
    if results_dir:
        candidates.append(Path(results_dir))
    candidates.append(Path(protocol_model_path).parent / "llm_stage_results")

    stage_dir = next((path for path in candidates if path.is_dir()), None)
    if stage_dir is None:
        return None

    relation_result = stage_dir / "relation_validation.json"
    relation_stage = _load_stage_result(relation_result) if relation_result.is_file() else None
    return {
        "results_dir": str(stage_dir),
        "boundary_refinement": _load_family_stage_results(stage_dir, "boundary_refinement_"),
        "semantic_labeling": _load_family_stage_results(stage_dir, "semantic_labeling_"),
        "relation_validation": relation_stage,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a self-contained HTML protocol report from protocol_model.json.")
    parser.add_argument("protocol_model_json")
    parser.add_argument("output_html")
    parser.add_argument("--evaluation-json", help="Optional evaluation report JSON from 13_evaluate_pipeline.py")
    parser.add_argument("--llm-analysis-json", help="Optional LLM analysis JSON from 15_analyze_with_llm.py")
    parser.add_argument("--llm-stage-results-dir", help="Optional directory with stage 07b/10b/11b LLM result artifacts")
    parser.add_argument("--final-evaluation-json", help="Optional final evaluation report JSON from 17_evaluate_protocol_spec.py")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("19_export_html", Path(args.log_dir))

    logger.info("Exporting HTML protocol report")

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

        llm_stage_results = _load_llm_stage_results(args.llm_stage_results_dir, args.protocol_model_json)
        if llm_stage_results:
            logger.info(f"Loaded LLM stage results from {llm_stage_results.get('results_dir')}")
            logger.metric("boundary_refinement_stage_results", len(llm_stage_results.get("boundary_refinement", {})), "families")
            logger.metric("semantic_labeling_stage_results", len(llm_stage_results.get("semantic_labeling", {})), "families")

    with logger.stage("render_html"):
        html = render_protocol_model_html(
            model,
            evaluation=evaluation,
            llm_analysis=llm_analysis,
            final_evaluation=final_evaluation,
            llm_stage_results=llm_stage_results,
        )
        logger.metric("html_size", len(html), "characters")
        logger.metric("html_size_kb", len(html.encode('utf-8')) / 1024, "KB")

    with logger.stage("write_output"):
        with open(args.output_html, "w", encoding="utf-8") as handle:
            handle.write(html)
        logger.info(f"Wrote HTML report to {args.output_html}")

    print(f"[+] Wrote HTML protocol report to {args.output_html}")

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
