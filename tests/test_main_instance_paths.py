from __future__ import annotations

import json
import types
from pathlib import Path

import pytest

import main as pipeline_main


def _instance_args(tmp_path: Path):
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "output"
    log_dir = tmp_path / "logs"
    data_dir.mkdir()
    (data_dir / "01_messages.jsonl").write_text("", encoding="utf-8")

    args = pipeline_main.parse_args(
        [
            "--use-existing-messages",
            "--data-dir",
            str(data_dir),
            "--output-dir",
            str(output_dir),
            "--log-dir",
            str(log_dir),
        ]
    )
    pipeline_main.validate_args(args)
    return args


def _option_value(command: list[str], option: str) -> str:
    index = command.index(option)
    return command[index + 1]


def test_instance_paths_derive_writable_defaults_from_data_dir(tmp_path: Path) -> None:
    args = _instance_args(tmp_path)

    assert args.pcap_dir == args.data_dir / "pcaps"
    assert args.family_latent_cache_path == args.data_dir / "02_latent_cache.json"
    assert args.discriminator_salience_cache_path == args.data_dir / "07_salience_cache.json"

    pipeline_main.prepare_output_dirs(args)

    assert args.data_dir.is_dir()
    assert args.output_dir.is_dir()
    assert args.log_dir.is_dir()


def test_pipeline_passes_instance_log_dir_to_every_stage(tmp_path: Path) -> None:
    args = _instance_args(tmp_path)

    pipeline = pipeline_main.build_pipeline(args)

    assert pipeline
    for _, command in pipeline:
        assert command.count("--log-dir") == 1
        assert _option_value(command, "--log-dir") == str(args.log_dir)


def test_pipeline_keeps_llm_placeholders_and_caches_in_instance_data_dir(tmp_path: Path) -> None:
    args = _instance_args(tmp_path)

    pipeline = dict(pipeline_main.build_pipeline(args))
    user_response_dir = args.data_dir / "user_provided_LLM_responses"

    for stage_name in (
        "07b_refine_boundaries_llm",
        "10b_validate_relations_llm",
        "11b_label_semantics_llm",
        "15_analyze_with_llm",
    ):
        assert _option_value(pipeline[stage_name], "--user-response-dir") == str(user_response_dir)

    assert _option_value(pipeline["04_discover_families"], "--latent-cache-path") == str(
        args.data_dir / "02_latent_cache.json"
    )
    assert _option_value(pipeline["09_infer_keywords"], "--salience-cache-path") == str(
        args.data_dir / "07_salience_cache.json"
    )


def test_pipeline_forwards_local_backend_to_all_llm_stages(tmp_path: Path) -> None:
    """Regression: the backend forwarding ran before 10b/11b were appended, so
    those stages fell back to --llm-config (remote API) in local-finetuned mode."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "01_messages.jsonl").write_text("", encoding="utf-8")
    args = pipeline_main.parse_args(
        [
            "--use-existing-messages",
            "--backend", "local-finetuned",
            "--local-base-url", "http://127.0.0.1:9999",
            "--data-dir", str(data_dir),
            "--output-dir", str(tmp_path / "output"),
            "--log-dir", str(tmp_path / "logs"),
        ]
    )
    pipeline_main.validate_args(args)

    pipeline = dict(pipeline_main.build_pipeline(args))
    for stage_name in ("07b_refine_boundaries_llm", "10b_validate_relations_llm", "11b_label_semantics_llm"):
        command = pipeline[stage_name]
        assert "--backend" in command and command[command.index("--backend") + 1] == "local-finetuned", stage_name
        assert _option_value(command, "--local-base-url") == "http://127.0.0.1:9999"
    # Synthesis needs a host-class LLM: must be forced to render-only locally.
    assert "--render-only" in pipeline["15_analyze_with_llm"]
    # API stages untouched when the default backend is selected.
    args_api = pipeline_main.parse_args(
        [
            "--use-existing-messages",
            "--data-dir", str(data_dir),
            "--output-dir", str(tmp_path / "output2"),
            "--log-dir", str(tmp_path / "logs2"),
        ]
    )
    pipeline_api = dict(pipeline_main.build_pipeline(args_api))
    assert "--backend" not in pipeline_api["10b_validate_relations_llm"]
    assert "--render-only" not in pipeline_api["15_analyze_with_llm"]


def test_compare_no_llm_keeps_llm_stages_in_pipeline(tmp_path: Path) -> None:
    """Single-flag compare mode: the LLM stages run in the main pipeline; only
    the post-run baseline is rebuilt from raw stage-07 families."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "01_messages.jsonl").write_text("", encoding="utf-8")
    args = pipeline_main.parse_args(
        [
            "--use-existing-messages",
            "--compare-no-llm",
            "--ground-truth-json", "truth_files/modbus.json",
            "--data-dir", str(data_dir),
            "--output-dir", str(tmp_path / "output"),
            "--log-dir", str(tmp_path / "logs"),
        ]
    )
    pipeline_main.validate_args(args)
    pipeline = dict(pipeline_main.build_pipeline(args))

    assert "07b_refine_boundaries_llm" in pipeline
    assert "10b_validate_relations_llm" in pipeline
    assert "11b_label_semantics_llm" in pipeline
    assert "--render-only" not in pipeline["15_analyze_with_llm"]


def test_compare_no_llm_requires_ground_truth(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "01_messages.jsonl").write_text("", encoding="utf-8")
    argv = [
        "--use-existing-messages",
        "--compare-no-llm",
        "--data-dir", str(data_dir),
        "--output-dir", str(tmp_path / "output"),
        "--log-dir", str(tmp_path / "logs"),
    ]
    with pytest.raises(SystemExit):
        pipeline_main.validate_args(pipeline_main.parse_args(argv))


def test_run_no_llm_comparison_writes_variants(tmp_path: Path) -> None:
    """Functional test of the compare path against the real modbus-small run
    artifacts; writes both evaluation variants plus the delta report."""
    source = Path("dol/finetuned-modbus-small/data")
    required = [
        source / "05_families.json",
        source / "03_family_features.json",
        source / "07_keywords.json",
        source / "08_relations_validated.json",
        source / "09_semantics.json",
        source / "04_framing.json",
        source / "11_evaluation.json",
        source / "13_llm_analysis.json",
        source / "15_evaluation_result.json",
    ]
    if not all(path.is_file() for path in required):
        pytest.skip("modbus-small run artifacts not present")

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    for name in (
        "05_families.json", "03_family_features.json", "07_keywords.json",
        "08_relations_validated.json", "09_semantics.json", "04_framing.json",
        "11_evaluation.json", "13_llm_analysis.json", "15_evaluation_result.json",
    ):
        (data_dir / name).write_text((source / name).read_text(encoding="utf-8"), encoding="utf-8")

    args = types.SimpleNamespace(
        data_dir=data_dir,
        log_dir=tmp_path / "logs",
        ground_truth_json=Path("truth_files/modbus.json"),
    )
    if not args.ground_truth_json.is_file():
        pytest.skip("truth_files/modbus.json not present")

    class _Logger:
        def info(self, *a, **k): pass
        def error(self, *a, **k): raise AssertionError(k.get("msg", a))

    pipeline_main.run_no_llm_comparison(args, _Logger())

    compare_dir = data_dir / "llm_comparison"
    full = json.loads((compare_dir / "15_evaluation_result.full.json").read_text(encoding="utf-8"))
    no_llm = json.loads((compare_dir / "15_evaluation_result.no-llm.json").read_text(encoding="utf-8"))
    delta = json.loads((compare_dir / "15_evaluation_comparison.json").read_text(encoding="utf-8"))

    # Summaries are rounded to 4 decimals, so the delta identity holds at that precision.
    assert full["summary"]["overall_score"] == pytest.approx(no_llm["summary"]["overall_score"] + delta["delta"]["overall_score"], abs=1e-3)
    assert delta["variants"]["full_run (07b+10b+11b LLM stages)"]["verdict"] == full["summary"]["verdict"]
    assert delta["variants"]["no_llm (raw stage-07 families)"]["verdict"] == no_llm["summary"]["verdict"]
    assert "llm_contribution" in delta
