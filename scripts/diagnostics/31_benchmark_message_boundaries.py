"""Multi-protocol benchmark: per-message field-boundary F1 against tshark annotations.

For every protocol with a pipeline run and an annotation file, each message's
predicted boundaries (the field edges of its assigned family) are compared with
the dissector-derived boundaries for that same message. Scores are per message,
so they need no hand-written truth file and are comparable across protocols and
with published per-message boundary metrics.

Only interior edges are scored: offset 0 and the payload end are trivially
correct for every message.

Run from the project root:
    python scripts/diagnostics/31_benchmark_message_boundaries.py \
        [--runs-root finetuning/windows_data/runs] \
        [--annotations-root finetuning/cluster-free-dataset/annotations] \
        [--families-file 05_families.json] [--output-json report.json]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Set

ROOT = Path(__file__).resolve().parents[2]


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


def score_protocol(data_dir: Path, annotations_path: Path, families_file: str) -> Dict[str, Any]:
    with (data_dir / families_file).open("r", encoding="utf-8") as handle:
        family_edges = _family_edges(json.load(handle))
    with (data_dir / "02_family_assignments.json").open("r", encoding="utf-8") as handle:
        assignments = {int(item["msg_id"]): str(item["family_id"]) for item in json.load(handle)["assignments"]}
    payload_len = {int(m["msg_id"]): int(m["payload_len"]) for m in _iter_jsonl(data_dir / "01_messages.jsonl")}

    tp = fp = fn = 0
    scored = unassigned = exact = truth_edges = 0
    for annotation in _iter_jsonl(annotations_path):
        msg_id = int(annotation["msg_id"])
        length = payload_len.get(msg_id)
        if length is None or not annotation.get("boundaries"):
            continue
        truth = {int(edge) for edge in annotation["boundaries"] if 0 < int(edge) < length}
        family_id = assignments.get(msg_id)
        if family_id is None:
            unassigned += 1
        predicted = {edge for edge in family_edges.get(family_id or "", []) if 0 < edge < length}
        scored += 1
        truth_edges += len(truth)
        tp += len(predicted & truth)
        fp += len(predicted - truth)
        fn += len(truth - predicted)
        exact += predicted == truth
    return {
        "messages": scored,
        "families": len(family_edges),
        "unassigned_messages": unassigned,
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
        report[run_dir.name] = score_protocol(data_dir, annotations_path, args.families_file)

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
