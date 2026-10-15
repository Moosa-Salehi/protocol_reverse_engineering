from __future__ import annotations

import importlib.util
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import main as pipeline_main
from protocol_re.inference.periodic_arrays import detect_array_regions, split_positions_at_arrays
from protocol_re.model.schema import Segment


def _load_script(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _register_responses(count: int = 300, seed: int = 1) -> list[bytes]:
    """Modbus-like read responses: 4-byte header, byte count, then N big-endian registers."""
    rng = random.Random(seed)
    messages = []
    for i in range(count):
        n = rng.randint(4, 24)
        registers = b"".join(rng.randint(0, 900).to_bytes(2, "big") for _ in range(n))
        messages.append(i.to_bytes(2, "big") + b"\x00\x03" + bytes([2 * n]) + registers)
    return messages


def test_register_array_is_detected_with_two_byte_period() -> None:
    regions = detect_array_regions(_register_responses(), "strict")
    assert len(regions) == 1
    region = regions[0]
    assert region.period == 2
    assert region.tail
    assert region.evidence in {"count+stats", "length+stats"}
    # element edges start at the array (offset 5) and step by the register width
    assert {5, 7, 9, 11} <= set(region.edges)
    assert all((edge - 5) % 2 == 0 for edge in region.edges)


def test_off_mode_and_unstructured_family_add_nothing() -> None:
    assert detect_array_regions(_register_responses(), "off") == []
    rng = random.Random(7)
    # fixed-length messages of unrelated fields: no repeating structure, no length variation
    unstructured = [
        bytes([0x10, rng.randint(0, 255)]) + rng.randbytes(4) + bytes([rng.choice(b"ABC"), 0]) + rng.randint(0, 3).to_bytes(2, "big")
        for _ in range(300)
    ]
    assert detect_array_regions(unstructured, "strict") == []


def test_split_positions_stay_inside_the_field_span() -> None:
    regions = detect_array_regions(_register_responses(), "strict")
    positions = split_positions_at_arrays({0, 4, 5, 13}, regions)
    assert {7, 9, 11} <= positions
    assert max(positions) == 13


def test_stage07_split_keeps_segment_kind() -> None:
    stage07 = _load_script("stage07_periodic", "scripts/07_infer_boundaries.py")
    pieces = stage07._split_segments_at([Segment(start=0, end=4, kind="constant"), Segment(start=4, end=10, kind="variable")], {6, 8})
    assert [(p.start, p.end, p.kind) for p in pieces] == [(0, 4, "constant"), (4, 6, "variable"), (6, 8, "variable"), (8, 10, "variable")]
    assert pieces[1].evidence["periodic_array_split"] is True


def test_pipeline_defaults_to_loose_periodic_arrays(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "01_messages.jsonl").write_text("", encoding="utf-8")
    base = ["--use-existing-messages", "--data-dir", str(data_dir), "--output-dir", str(tmp_path / "out"), "--log-dir", str(tmp_path / "log")]

    default = dict(pipeline_main.build_pipeline(pipeline_main.parse_args(base)))["07_infer_boundaries"]
    assert default[default.index("--periodic-arrays") + 1] == "loose"

    disabled = dict(pipeline_main.build_pipeline(pipeline_main.parse_args(base + ["--boundary-periodic-arrays", "off"])))["07_infer_boundaries"]
    assert disabled[disabled.index("--periodic-arrays") + 1] == "off"
