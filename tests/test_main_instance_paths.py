from __future__ import annotations

from pathlib import Path

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
            "--llm-render-only",
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
