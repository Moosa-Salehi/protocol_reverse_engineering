"""Build the training rows shipped for few-shot boundaries (protocol_re.inference.fewshot_boundaries).

For each protocol run (<runs-root>/<protocol>/data with 01_messages.jsonl and 02_family_assignments.json) the
framing is recomputed with the current stage 05 (body starts), every (family, exact length) group is turned into
feature rows, and the rows are labelled from per-message annotations (<annotations-root>/<protocol>.jsonl,
`boundaries`; the truth-file convention ones are in dol/accuracy-push/annotations-truthconv). Rows keep their
protocol so a protocol can be left out (main.py --fewshot-exclude-protocol) when it is the one evaluated.

Usage: 32_build_fewshot_training_set.py --runs-root dol/benchmark-14-protocols \\
           --annotations-root dol/accuracy-push/annotations-truthconv \\
           --output assets/pre_trained/fewshot_boundary_training.npz [--protocols modbus,dnp3,...]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from protocol_re.inference import fewshot_boundaries as fsb  # noqa: E402
from protocol_re.inference.framing import infer_framing_hypotheses  # noqa: E402

DEFAULT_PROTOCOLS = "modbus,hart_ip,zigbee,bacnet,powerlink,s7comm,mms,goose,dnp3,enip,cip,ethercat,opcua,iec104"


def load_run(data_dir: Path):
    order, payload = [], {}
    for line in (data_dir / "01_messages.jsonl").open(encoding="utf-8"):
        if line.strip():
            m = json.loads(line)
            mid = int(m["msg_id"])
            order.append(mid)
            payload[mid] = bytes.fromhex(m["payload_hex"])
    family_of = {int(a["msg_id"]): a["family_id"] for a in json.loads((data_dir / "02_family_assignments.json").read_text())["assignments"]}
    return order, payload, family_of


def body_starts(order, payload, family_of):
    grouped = defaultdict(list)
    for m in order:
        f = family_of.get(m)
        if f not in (None, "noise"):
            grouped[str(f)].append(payload[m].hex())
    framing = infer_framing_hypotheses(grouped)["families"]
    out = {}
    for fam, result in framing.items():
        best = (result.get("layout_hypotheses") or [{}])[0]
        if best.get("body_start"):
            out[fam] = int(best["body_start"])
    return out


def load_labels(path: Path):
    labels = {}
    for line in path.open(encoding="utf-8"):
        if line.strip():
            a = json.loads(line)
            if a.get("boundaries") and a.get("reviewer") != "tshark-cache":
                labels[int(a["msg_id"])] = [int(x) for x in a["boundaries"]]
    return labels


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs-root", required=True, type=Path)
    parser.add_argument("--annotations-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--protocols", default=DEFAULT_PROTOCOLS)
    args = parser.parse_args()
    per_protocol = {}
    for p in args.protocols.split(","):
        order, payload, family_of = load_run(args.runs_root / p / "data")
        labels = load_labels(args.annotations_root / f"{p}.jsonl")
        rows = fsb.build_rows(order, family_of, payload, body_starts(order, payload, family_of), labels)
        per_protocol[p] = rows
        print(f"{p:10s} groups {len(rows):4d}  labelled rows {sum(len(g['offs']) for g in rows if g['y'] is not None)}", flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fsb.save_training_set(args.output, per_protocol)
    print(f"[+] wrote {args.output} ({args.output.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
