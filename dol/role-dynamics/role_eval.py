"""Idea 5: field roles from value dynamics. Builds feature rows for
  real   predicted fields of saved zero-shot runs that the evaluator matched to a truth field with a role (labels =
         truth role class), per protocol, for leave-one-protocol-out training;
  syn    true fields of synthetic protocols (dol/synthetic-pretrain/gen.py, roles from the generator);
trains a gradient-boosted classifier (real-LOPO / syn / syn+real-LOPO), writes the predicted roles into a copy of
each run's 14_evaluation_model_data.json and re-scores it with stage 17.

usage: role_eval.py build            (features -> feats/*.npz)
       role_eval.py eval <variant> <mode> <tau> [runs-root] [protocols]
           variant: real | syn | both ; mode: replace (override when confident) | fill (only fields without a role)
"""
from __future__ import annotations

import copy
import json
import random
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "dol/synthetic-pretrain")); sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402

import role_features as rf  # noqa: E402

PROTOS = ["bacnet", "cip", "dnp3", "enip", "ethercat", "goose", "hart_ip", "iec104", "mms", "modbus", "opcua", "powerlink",
          "s7comm", "zigbee"]
HELDOUT = ["synphasor", "ams", "doip", "cnip"]
FEATS = HERE / "feats"
PY = str(Path.home() / ".venvs/protocol_re/bin/python")


def run_dir(runs_root: Path, p: str) -> Path:
    return runs_root / p / "data"


def truth_path(p: str) -> Path:
    return ROOT / ("truth_files/heldout" if p in HELDOUT else "truth_files") / f"{p}.json"


def predicted_fields(data: Path):
    md = json.loads((data / "14_evaluation_model_data.json").read_text())
    for fam in md["predicted_protocol"].get("families", []):
        for k, h in enumerate(fam.get("field_hypotheses", []) or []):
            yield str(fam["family_id"]), k, int(h["start"]), int(h["length"]), h


def build_real(runs_root: Path, p: str):
    data = run_dir(runs_root, p)
    c = rf.load_run(data)
    res = json.loads((data / "15_evaluation_result.json").read_text())
    lab = {}
    for it in res["matches"]["fields"]:
        pr, role = it["predicted"], it.get("ground_truth_role")
        if role:
            lab.setdefault((str(pr["owner_id"]), int(pr["start"]), int(pr["length"])), role)
    X, y, keys = [], [], []
    for fam, k, s, w, _h in predicted_fields(data):
        v = rf.field_features(c, fam, s, w)
        if v is None:
            continue
        X.append(v); keys.append((fam, k)); y.append(lab.get((fam, s, w), ""))
    return np.array(X), np.array(y), keys


def build_syn(n: int, first: int = 50000, n_messages: int = 600):
    from gen import generate_protocol
    X, y, proto = [], [], []
    for seed in range(first, first + n):
        r = random.Random(seed)
        msgs = generate_protocol(r, n_messages)
        types = sorted({m["type"] for m in msgs})
        merge = {t: t for t in types}
        for t in types:
            if r.random() < 0.25 and len(types) > 2:
                merge[t] = merge[r.choice(types)]
        c = rf.synth_corpus(msgs, merge)
        for fam, mids in c["fams"].items():
            layouts = Counter((tuple(msgs[m]["boundaries"]), tuple(msgs[m]["roles"]), len(msgs[m]["payload"])) for m in mids)
            (edges, roles, ln), _ = layouts.most_common(1)[0]
            ends = list(edges[1:]) + [ln]
            for s, e, role in zip(edges, ends, roles):
                if role is None:
                    continue
                v = rf.field_features(c, fam, s, e - s)
                if v is not None:
                    X.append(v); y.append(role); proto.append(seed)
        if (seed - first) % 50 == 0:
            print(f"syn seed {seed}: rows {len(y)}", flush=True)
    return np.array(X), np.array(y), np.array(proto)


def cmd_build(runs_root: Path, protos):
    FEATS.mkdir(exist_ok=True)
    for p in protos:
        X, y, keys = build_real(runs_root, p)
        np.savez_compressed(FEATS / f"{runs_root.name}_{p}.npz", X=X, y=y, keys=np.array([f"{a}|{b}" for a, b in keys]))
        print(f"{p:10s} fields {len(y):4d} labelled {int((y != '').sum()):4d}", flush=True)
    if not (FEATS / "syn.npz").exists():
        X, y, pr = build_syn(400)
        np.savez_compressed(FEATS / "syn.npz", X=X, y=y, proto=pr)
        print(f"syn rows {len(y)}  {Counter(y).most_common()}")


def classifier():
    from sklearn.ensemble import HistGradientBoostingClassifier
    return HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, max_depth=6, l2_regularization=1.0,
                                          class_weight="balanced", random_state=0)


def cmd_eval(variant: str, mode: str, tau: float, runs_root: Path, protos, tag: str):
    syn = np.load(FEATS / "syn.npz")
    real = {p: np.load(FEATS / f"{runs_root.name if runs_root.name != 'zs' else 'zs'}_{p}.npz") for p in protos}
    train_real = {p: np.load(FEATS / f"zs_{p}.npz") for p in PROTOS}          # benchmark rows for training
    out_root = HERE / "runs" / tag
    summary = {}
    for p in protos:
        Xs, ys = [], []
        if variant in ("real", "both"):
            for q, d in train_real.items():
                if q == p:
                    continue
                m = d["y"] != ""
                Xs.append(d["X"][m]); ys.append(d["y"][m])
        if variant in ("syn", "both"):
            Xs.append(syn["X"]); ys.append(syn["y"])
        X, y = np.vstack(Xs), np.concatenate(ys)
        model = classifier().fit(X, y)
        d = real[p]
        prob = model.predict_proba(d["X"]) if len(d["X"]) else np.zeros((0, len(model.classes_)))
        pred = {tuple(k.split("|")): (model.classes_[int(np.argmax(pr))], float(pr.max())) for k, pr in zip(d["keys"], prob)}
        src = run_dir(runs_root, p)
        dst = out_root / p
        dst.mkdir(parents=True, exist_ok=True)
        md = json.loads((src / "14_evaluation_model_data.json").read_text())
        changed = 0
        for fam in md["predicted_protocol"].get("families", []):
            for k, h in enumerate(fam.get("field_hypotheses", []) or []):
                role, conf = pred.get((str(fam["family_id"]), str(k)), (None, 0.0))
                attrs = h.setdefault("attributes", {})
                current = attrs.get("semantic_role") or h.get("semantic_role")
                has = sys_role_class(current)
                if role is None or conf < tau or (mode == "fill" and has):
                    continue
                attrs["semantic_role"] = role; attrs["semantic_source"] = f"role-dynamics-{variant}"
                h.pop("semantic_role", None)
                changed += 1
        (dst / "14_evaluation_model_data.json").write_text(json.dumps(md))
        subprocess.run([PY, str(ROOT / "scripts/17_evaluate_protocol_spec.py"), str(dst / "14_evaluation_model_data.json"),
                        str(truth_path(p)), str(dst / "15_evaluation_result.json"), "--messages-jsonl", str(src / "01_messages.jsonl")],
                       check=True, capture_output=True)
        r = json.loads((dst / "15_evaluation_result.json").read_text())
        b = json.loads((src / "15_evaluation_result.json").read_text())
        summary[p] = dict(base=b["metrics"]["field_roles"]["f1_score"], new=r["metrics"]["field_roles"]["f1_score"],
                          overall_base=b["summary"]["overall_score"], overall_new=r["summary"]["overall_score"], changed=changed)
        print(f"{p:10s} roles {summary[p]['base']:.3f} -> {summary[p]['new']:.3f}  overall {summary[p]['overall_base']:.3f} -> "
              f"{summary[p]['overall_new']:.3f}  changed {changed}", flush=True)
    mb = np.mean([v["base"] for v in summary.values()]); mn = np.mean([v["new"] for v in summary.values()])
    print(f"MEAN roles {mb:.3f} -> {mn:.3f}")
    (out_root / "summary.json").write_text(json.dumps(summary, indent=1))


_EV = None


def sys_role_class(v):
    global _EV
    if _EV is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("ev", ROOT / "scripts/17_evaluate_protocol_spec.py")
        _EV = importlib.util.module_from_spec(spec); spec.loader.exec_module(_EV)
    return _EV._role_class(v)


if __name__ == "__main__":
    if sys.argv[1] == "build":
        root = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "dol/final-v4/zs"
        protos = sys.argv[3].split(",") if len(sys.argv) > 3 else PROTOS
        cmd_build(root, protos)
    else:
        variant, mode, tau = sys.argv[2], sys.argv[3], float(sys.argv[4])
        root = Path(sys.argv[5]) if len(sys.argv) > 5 else ROOT / "dol/final-v4/zs"
        protos = sys.argv[6].split(",") if len(sys.argv) > 6 else PROTOS
        cmd_eval(variant, mode, tau, root, protos, f"{root.parent.name}-{root.name}-{variant}-{mode}-{tau}")
