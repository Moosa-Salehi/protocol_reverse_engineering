"""Stage 17 with content-based family -> truth type pairing (2026-10-29).

The shipped evaluator pairs families with truth types by name tokens, field-count ratio and role, with an opcode gate
only when the truth declares a constant discriminator at PDU offset 0. With oracle families (every family exactly one
truth type, dol/oracle-ceilings) it paired a family with its own type in 36/198 cases. Here the pairing uses the
messages: score(family, type) = Jaccard overlap of the family's messages (02_family_assignments.json) and the type's
messages (per-message truth-convention annotations), greedy one-to-one above THRESHOLD, as before. Everything else in
stage 17 (scope, header types, field matching, offset alignment, metrics) is unchanged.

usage: rescore.py <run-data-dir> <truth.json> <annotations.jsonl> <out.json>
"""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
THRESHOLD = 0.1

data, truth, ann, out = (Path(x) for x in sys.argv[1:5])
spec = importlib.util.spec_from_file_location("ev17", ROOT / "scripts/17_evaluate_protocol_spec.py")
ev = importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)

fam_msgs = defaultdict(set)
for a in json.loads((data / "02_family_assignments.json").read_text())["assignments"]:
    fam_msgs[str(a["family_id"])].add(int(a["msg_id"]))
type_msgs = defaultdict(set)
for line in ann.open(encoding="utf-8"):
    if line.strip():
        a = json.loads(line)
        if a.get("type"):
            type_msgs[str(a["type"])].add(int(a["msg_id"]))


def _content_matches(predicted, truth_types, *, structural_tag=False):
    candidates = []
    for family in predicted:
        fid = str(family.get("family_id")); fm = fam_msgs.get(fid, set())
        for mt in truth_types:
            tid = str(mt.get("message_type_id")); tm = type_msgs.get(tid, set())
            if fm and tm:
                j = len(fm & tm) / len(fm | tm)
                if j > 0:
                    candidates.append((fid, tid, round(j, 6)))
    return [{"predicted_family_id": f, "ground_truth_message_type_id": t, "score": s, "reason": "message_overlap"}
            for f, t, s in ev._greedy_matches(candidates, THRESHOLD)]


ev._message_type_matches = _content_matches
sys.argv = [sys.argv[0], str(data / "14_evaluation_model_data.json"), str(truth), str(out), "--messages-jsonl", str(data / "01_messages.jsonl")]
ev.main()
