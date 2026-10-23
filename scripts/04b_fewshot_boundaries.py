#!/usr/bin/env python3
"""Stage 04b: learned boundary predictions per message (few-shot from labelled messages, or zero-shot), and the
family split by layout.

--mode fewshot (needs --labels) adapts the model to the capture with a few labelled messages; --mode zeroshot uses
the generic model trained on the shipped protocols, the label-free structural post-processors (--posts) and,
with --reference, edges carried over from known protocols that share a lower layer.

Runs after family discovery (04) when --fewshot-labels is given:
  1. framing body starts of the current families (stage-05 defaults),
  2. per-message edges for every message (protocol_re.inference.fewshot_boundaries.predict_edges),
  3. families whose messages disagree on their layout are split by layout (unless --no-split); the assignments
     file is rewritten (original kept as 02_family_assignments.pre-fewshot-split.json), so stages 05-07 run on
     the split families. Stage 07c later writes the predicted edges into the families.

Labels file (JSONL): {"msg_id": <id>, "boundaries": [0, ..., len]} per labelled message; a line may carry
"payload_hex" instead of (or with) "msg_id" to match by payload. scripts/select_fewshot_messages.py lists which
messages to label.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from protocol_re.inference import fewshot_boundaries as fsb  # noqa: E402
from protocol_re.inference.framing import infer_framing_hypotheses  # noqa: E402
from protocol_re.utils.logging import setup_stage_logging  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("messages_jsonl", type=Path)
    parser.add_argument("assignments_json", type=Path)
    parser.add_argument("output_json", type=Path, help="Per-message predicted edges")
    parser.add_argument("--mode", choices=["fewshot", "zeroshot"], default="fewshot")
    parser.add_argument("--labels", type=Path, help="Labelled messages (JSONL), required for --mode fewshot")
    parser.add_argument("--posts", default="strings,ber,crc", help="Zero-shot post-processors (comma list, may be empty)")
    parser.add_argument("--reference", type=Path, help="Zero-shot shared-layer transfer: reference messages (jsonl.gz)")
    parser.add_argument("--training-set", type=Path, required=True)
    parser.add_argument("--exclude-protocol", action="append", default=[],
                        help="Leave this protocol's rows out of the training set (evaluation on a benchmark protocol)")
    parser.add_argument("--discriminator-split", dest="discriminator_split", action=argparse.BooleanOptionalAction, default=False,
                        help="split families by a second-level discriminator byte chosen by predicted-layout agreement "
                             "(FewShotBoundaries.DISC_SPLIT_*), before the layout split")
    parser.add_argument("--split", dest="split", action=argparse.BooleanOptionalAction, default=True,
                        help="Split families whose messages disagree on their layout (default on)")
    parser.add_argument("--split-verify", dest="split_verify", action=argparse.BooleanOptionalAction, default=True,
                        help="Split a family only into layouts its labelled messages show (default on)")
    parser.add_argument("--split-support", type=int, default=None,
                        help="Labelled messages a layout needs to count as verified (default FewShotBoundaries.SPLIT_LABELLED_SUPPORT)")
    parser.add_argument("--log-dir", default="logs")
    args = parser.parse_args()
    logger = setup_stage_logging("04b_fewshot_boundaries", Path(args.log_dir))

    with logger.stage("load"):
        order, payload = [], {}
        for line in args.messages_jsonl.open(encoding="utf-8"):
            if line.strip():
                m = json.loads(line)
                mid = int(m["msg_id"])
                order.append(mid)
                payload[mid] = bytes.fromhex(m["payload_hex"])
        doc = json.loads(args.assignments_json.read_text(encoding="utf-8"))
        family_of = {int(a["msg_id"]): a["family_id"] for a in doc["assignments"]}
        by_payload = {payload[m].hex(): m for m in order}
        labels = {}
        for line in (args.labels.open(encoding="utf-8") if args.labels else []):
            if not line.strip():
                continue
            a = json.loads(line)
            mid = int(a["msg_id"]) if a.get("msg_id") is not None and int(a["msg_id"]) in payload else by_payload.get(str(a.get("payload_hex", "")).lower())
            if mid is not None and a.get("boundaries"):
                labels[mid] = [int(x) for x in a["boundaries"]]
        logger.metric("labelled_messages", len(labels), "messages")
        if args.mode == "fewshot" and not labels:
            raise SystemExit("04b_fewshot_boundaries: no labelled message matches the corpus")

    with logger.stage("framing_body_starts"):
        grouped = defaultdict(list)
        for m in order:
            f = family_of.get(m)
            if f not in (None, "noise"):
                grouped[str(f)].append(payload[m].hex())
        body_start_of = {}
        for fam, result in infer_framing_hypotheses(grouped)["families"].items():
            best = (result.get("layout_hypotheses") or [{}])[0]
            if best.get("body_start"):
                body_start_of[fam] = int(best["body_start"])

    with logger.stage("predict"):
        if args.mode == "fewshot":
            pred, summary = fsb.predict_edges(order, family_of, payload, body_start_of, labels, args.training_set,
                                              exclude=args.exclude_protocol)
        else:
            reference = fsb.load_reference_messages(args.reference, exclude=args.exclude_protocol) if args.reference else None
            posts = [x for x in args.posts.split(",") if x]
            pred, summary = fsb.predict_edges_zeroshot(order, family_of, payload, body_start_of, args.training_set,
                                                       exclude=args.exclude_protocol, posts=posts, reference=reference)
        print(f"[+] few-shot boundaries: { {k: v for k, v in summary.items() if k != 'family_probability'} }")

    disc_split = {"applied": False}
    if args.discriminator_split:
        with logger.stage("discriminator_split"):
            ref = (doc.get("metadata") or {}).get("discriminator_refinement") or {}
            start = int(ref["offset"]) + int(ref["width"]) if ref.get("applied") else 0
            moved, disc_split = fsb.discriminator_split(family_of, pred, payload, start=start)
            disc_split["applied"] = True
            if moved:
                backup = args.assignments_json.with_name("02_family_assignments.pre-discriminator-split.json")
                if not backup.exists():
                    shutil.copy(args.assignments_json, backup)
                for a in doc["assignments"]:
                    mid = int(a["msg_id"])
                    if mid in moved:
                        a["family_id"] = moved[mid]
                doc.setdefault("metadata", {})["discriminator_split"] = {k: v for k, v in disc_split.items()}
                args.assignments_json.write_text(json.dumps(doc), encoding="utf-8")
                family_of.update(moved)
            print(f"[+] second-level discriminator split: {disc_split.get('split_families')}")

    split = {"moved_messages": 0, "sub_families": 0, "skipped": {}}
    if args.split:
        with logger.stage("split_families"):
            moved, split = fsb.split_families(family_of, pred, payload, labels=labels if (args.split_verify and labels) else None,
                                              support=args.split_support)
            if moved:
                shutil.copy(args.assignments_json, args.assignments_json.with_name("02_family_assignments.pre-fewshot-split.json"))
                for a in doc["assignments"]:
                    mid = int(a["msg_id"])
                    if mid in moved:
                        a["family_id"] = moved[mid]
                args.assignments_json.write_text(json.dumps(doc), encoding="utf-8")
            print(f"[+] few-shot layout split: {split}")

    args.output_json.write_text(json.dumps({"summary": summary, "split": split, "discriminator_split": disc_split,
                                            "edges": {str(m): sorted(int(x) for x in e) for m, e in pred.items()}}),
                                encoding="utf-8")
    print(f"[+] Wrote {args.mode} edges for {len(pred)} messages to {args.output_json}")


if __name__ == "__main__":
    main()
