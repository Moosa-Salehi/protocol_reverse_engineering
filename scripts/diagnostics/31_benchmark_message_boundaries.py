"""Multi-protocol benchmark: per-message field-boundary F1 against tshark annotations.

For every protocol with a pipeline run and an annotation file, each message's
predicted boundaries (the field edges of its assigned family) are compared with
the dissector-derived boundaries for that same message. Scores are per message,
so they need no hand-written truth file and are comparable across protocols and
with published per-message boundary metrics.

Only interior edges are scored: offset 0 and the payload end are trivially
correct for every message. A family carrying a ``message_layout`` (stage 07's
per-message TLV chain) is scored per message: the fixed edges before the chain
start plus that message's own TLV edges (``--no-message-layouts`` scores the
fixed edges only). Annotations from the ``tshark-cache`` fallback are
skipped by default: they hold only a few coarse layer spans (about one edge per
100 bytes), so any real segmentation scores as false positives against them.

Run from the project root:
    python scripts/diagnostics/31_benchmark_message_boundaries.py \
        [--runs-root finetuning/windows_data/runs] \
        [--annotations-root finetuning/cluster-free-dataset/annotations] \
        [--families-file 05_families.json] [--output-json report.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterator, List, Set

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from protocol_re.inference.tlv import message_layout_edges  # noqa: E402


def _iter_jsonl(path: Path) -> Iterator[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def _family_edges(families: Dict[str, Any]) -> Dict[str, List[int]]:
    """Field edges (starts and ends) of every family's field hypotheses."""
    edges: Dict[str, List[int]] = {}
    for family_id, details in families.items():
        values: Set[int] = set()
        for field in details.get("field_hypotheses", []) or []:
            start = int(field.get("start", 0) or 0)
            values.update((start, start + int(field.get("length", 0) or 0)))
        edges[str(family_id)] = sorted(values)
    return edges


def _f1(tp: int, fp: int, fn: int) -> Dict[str, float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}


COARSE_REVIEWERS = frozenset({"tshark-cache"})


def score_protocol(
    data_dir: Path,
    annotations_path: Path,
    families_file: str,
    include_coarse: bool = False,
    use_message_layouts: bool = True,
) -> Dict[str, Any]:
    with (data_dir / families_file).open("r", encoding="utf-8") as handle:
        families = json.load(handle)
    family_edges = _family_edges(families)
    layouts = {
        str(family_id): details["message_layout"]
        for family_id, details in families.items()
        if use_message_layouts and isinstance(details, dict) and details.get("message_layout")
    }
    with (data_dir / "02_family_assignments.json").open("r", encoding="utf-8") as handle:
        assignments = {int(item["msg_id"]): str(item["family_id"]) for item in json.load(handle)["assignments"]}
    payload_len, payloads = {}, {}
    for m in _iter_jsonl(data_dir / "01_messages.jsonl"):
        payload_len[int(m["msg_id"])] = int(m["payload_len"])
        if layouts and str(assignments.get(int(m["msg_id"]))) in layouts:
            payloads[int(m["msg_id"])] = bytes.fromhex(m["payload_hex"])

    tp = fp = fn = 0
    scored = unassigned = exact = truth_edges = skipped_coarse = 0
    for annotation in _iter_jsonl(annotations_path):
        if not include_coarse and annotation.get("reviewer") in COARSE_REVIEWERS:
            skipped_coarse += 1
            continue
        msg_id = int(annotation["msg_id"])
        length = payload_len.get(msg_id)
        if length is None or not annotation.get("boundaries"):
            continue
        truth = {int(edge) for edge in annotation["boundaries"] if 0 < int(edge) < length}
        family_id = assignments.get(msg_id)
        if family_id is None:
            unassigned += 1
        edges = family_edges.get(family_id or "", [])
        if family_id in layouts and msg_id in payloads:
            edges = message_layout_edges(payloads[msg_id], edges, layouts[family_id])
        predicted = {edge for edge in edges if 0 < edge < length}
        scored += 1
        truth_edges += len(truth)
        tp += len(predicted & truth)
        fp += len(predicted - truth)
        fn += len(truth - predicted)
        exact += predicted == truth
    return {
        "messages": scored,
        "families": len(family_edges),
        "message_layout_families": len(layouts),
        "unassigned_messages": unassigned,
        "skipped_coarse_annotations": skipped_coarse,
        "mean_truth_edges": round(truth_edges / scored, 2) if scored else 0.0,
        "exact_match": round(exact / scored, 4) if scored else 0.0,
        **_f1(tp, fp, fn),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs-root", default=str(ROOT / "finetuning" / "windows_data" / "runs"),
                        help="Directory holding one <protocol>/data pipeline run per protocol")
    parser.add_argument("--annotations-root", default=str(ROOT / "finetuning" / "cluster-free-dataset" / "annotations"),
                        help="Directory holding <protocol>.jsonl per-message annotations")
    parser.add_argument("--families-file", default="05_families.json",
                        help="Families artifact to score, e.g. 05_families_refined.json for the LLM-refined boundaries")
    parser.add_argument("--include-coarse", action="store_true",
                        help="Also score against the coarse tshark-cache fallback annotations")
    parser.add_argument("--no-message-layouts", action="store_true",
                        help="Ignore families' per-message TLV layouts and score the fixed edges only")
    parser.add_argument("--output-json", default=None, help="Optional path for the full report")
    args = parser.parse_args()

    report: Dict[str, Any] = {}
    for run_dir in sorted(Path(args.runs_root).iterdir()):
        data_dir = run_dir / "data"
        annotations_path = Path(args.annotations_root) / f"{run_dir.name}.jsonl"
        required = [data_dir / args.families_file, data_dir / "02_family_assignments.json", data_dir / "01_messages.jsonl"]
        if not annotations_path.is_file() or not all(path.is_file() for path in required):
            print(f"[*] Skipping {run_dir.name}: missing run artifacts or annotations")
            continue
        report[run_dir.name] = score_protocol(data_dir, annotations_path, args.families_file, args.include_coarse,
                                              use_message_layouts=not args.no_message_layouts)

    header = f"{'protocol':12s} {'messages':>8s} {'families':>8s} {'truth/msg':>9s} {'precision':>9s} {'recall':>7s} {'f1':>6s} {'exact':>6s}"
    print(header)
    print("-" * len(header))
    for name, row in sorted(report.items(), key=lambda item: -item[1]["f1"]):
        print(f"{name:12s} {row['messages']:>8d} {row['families']:>8d} {row['mean_truth_edges']:>9.2f} "
              f"{row['precision']:>9.3f} {row['recall']:>7.3f} {row['f1']:>6.3f} {row['exact_match']:>6.3f}")
    if report:
        macro = sum(row["f1"] for row in report.values()) / len(report)
        print("-" * len(header))
        print(f"{'macro F1':12s} {'':>8s} {'':>8s} {'':>9s} {'':>9s} {'':>7s} {macro:>6.3f}")

    if args.output_json:
        Path(args.output_json).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"[+] Wrote {args.output_json}")


if __name__ == "__main__":
    main()
