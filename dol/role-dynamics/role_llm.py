"""Idea 5, LLM part: the LLM names field roles from statistics only (no bytes, no protocol name), one call per family,
given each field's value-dynamics summary and the classifier's top-3 roles. Written in fill mode (fields without a
role) into a copy of the run's 14_evaluation_model_data.json and re-scored with stage 17, like role_eval.py.

usage: role_llm.py <runs-root> <protocols> <out-tag> [--no-classifier-hint]
"""
from __future__ import annotations

import json
import os
import re
import time
import subprocess
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import role_eval as re_  # noqa: E402

URL = "http://127.0.0.1:8080/v1/chat/completions"
PAUSE = float(os.environ.get("LLM_PAUSE", "0"))   # seconds of rest between calls (laptop load)
ROLES = re_.rf.ROLES


def describe(v: np.ndarray) -> str:
    w, s = int(v[0]), int(v[1])
    be, le = v[12:23], v[23:34]
    parts = [f"offset {s}{'+' if s >= 64 else ''}, {w} byte(s)"]
    parts.append("constant in this message type" if v[7] <= 0.01 else f"{v[6]:.0%} distinct values, entropy {v[8]:.2f} of max")
    if v[9] > 0.5 and v[7] > 0.01:
        parts.append(f"most common value in {v[9]:.0%} of messages")
    if v[10] > 0.5:
        parts.append(f"{v[10]:.0%} zero bytes")
    if v[11] > 0.6:
        parts.append(f"{v[11]:.0%} printable ASCII")
    for tag, e in (("big-endian", be), ("little-endian", le)):
        if e[5] >= 0.95:
            parts.append(f"as {tag} equals a message/remaining length ({e[5]:.0%})")
        if e[2] >= 0.6:
            parts.append(f"as {tag} increases by 1-2 per message within a session ({e[2]:.0%})")
        if abs(e[7]) >= 0.8 and v[7] > 3:
            parts.append(f"as {tag} correlates with capture time (rho {e[7]:.2f})")
        if abs(e[6]) >= 0.8 and v[7] > 1:
            parts.append(f"as {tag} correlates with message length (rho {e[6]:.2f})")
        if w == 4 and e[10] >= 0.95 and v[7] > 3:
            parts.append(f"plausible as {tag} float32")
    if v[34] <= 0.375 and v[7] > 0.01:
        parts.append(f"values use few bits (OR of values sets {v[34]:.0%} of bits)")
    parts.append(f"across all message types: {v[37]:.0%} of types have it constant, it identifies the type with mutual information {v[36]:.2f}")
    if v[41] > 0.1:
        parts.append(f"same value in the paired request/response for {max(0, v[40]):.0%} of pairs")
    if v[5] > 0.5:
        parts.append("last bytes of the message")
    return "; ".join(parts)


def chat(prompt: str) -> str:
    body = json.dumps({"messages": [{"role": "system", "content": "You label fields of an unknown binary protocol from value statistics. Reply with JSON only."},
                                    {"role": "user", "content": prompt}], "temperature": 0.0, "max_tokens": 1200}).encode()
    with urllib.request.urlopen(urllib.request.Request(URL, body, {"Content-Type": "application/json"}), timeout=600) as r:
        out = json.loads(r.read())
    return re.sub(r"<think>.*?</think>", "", out["choices"][0]["message"].get("content") or "", flags=re.S)


def main():
    runs_root, protos, tag = Path(sys.argv[1]), sys.argv[2].split(","), sys.argv[3]
    hint = "--no-classifier-hint" not in sys.argv
    syn = np.load(re_.FEATS / "syn.npz")
    train_real = {p: np.load(re_.FEATS / f"zs_{p}.npz") for p in re_.PROTOS}
    out_root = HERE / "runs" / tag
    summary = {}
    for p in protos:
        done = out_root / p / "15_evaluation_result.json"
        if done.exists():                      # resume: re-read the finished protocol
            src = re_.run_dir(runs_root, p)
            r = json.loads(done.read_text()); b = json.loads((src / "15_evaluation_result.json").read_text())
            summary[p] = dict(base=b["metrics"]["field_roles"]["f1_score"], new=r["metrics"]["field_roles"]["f1_score"],
                              overall_base=b["summary"]["overall_score"], overall_new=r["summary"]["overall_score"], changed=None)
            continue
        if PAUSE:
            time.sleep(PAUSE)
        Xs, ys = [syn["X"]], [syn["y"]]
        for q, d in train_real.items():
            if q != p:
                m = d["y"] != ""; Xs.append(d["X"][m]); ys.append(d["y"][m])
        model = re_.classifier().fit(np.vstack(Xs), np.concatenate(ys))
        d = np.load(re_.FEATS / f"zs_{p}.npz")
        prob = model.predict_proba(d["X"]) if len(d["X"]) else np.zeros((0, len(model.classes_)))
        by_fam = defaultdict(list)
        for k, v, pr in zip(d["keys"], d["X"], prob):
            fam, idx = k.split("|")
            top = [(model.classes_[j], float(pr[j])) for j in np.argsort(-pr)[:3]]
            by_fam[fam].append((idx, v, top))
        src = re_.run_dir(runs_root, p)
        md = json.loads((src / "14_evaluation_model_data.json").read_text())
        dst = out_root / p; dst.mkdir(parents=True, exist_ok=True)
        log, changed = {}, 0
        for fam in md["predicted_protocol"].get("families", []):
            fid = str(fam["family_id"]); hyps = fam.get("field_hypotheses", []) or []
            todo = [(idx, v, top) for idx, v, top in by_fam.get(fid, [])
                    if not re_.sys_role_class((hyps[int(idx)].get("attributes") or {}).get("semantic_role") or hyps[int(idx)].get("semantic_role"))]
            if not todo:
                continue
            lines = [f"field {idx}: {describe(v)}" + (f"  [statistical classifier guesses: {', '.join(f'{r} {q:.2f}' for r, q in top)}]" if hint else "")
                     for idx, v, top in todo[:40]]
            prompt = (f"Fields of one message type of an unknown binary protocol, described only by statistics over many messages.\n"
                      f"Allowed roles: {', '.join(ROLES)}, or none if unsure.\n" + "\n".join(lines) +
                      '\nReply as JSON {"<field number>": "<role or none>", ...}.')
            if PAUSE:
                time.sleep(PAUSE)
            try:
                ans = json.loads(re.search(r"\{.*\}", chat(prompt), re.S).group(0))
            except Exception as e:   # unparsable / server error: leave the family unchanged
                log[fid] = {"error": str(e)}; continue
            log[fid] = ans
            for idx, role in ans.items():
                role = str(role).strip().lower()
                if role in ROLES and str(idx).isdigit() and int(idx) < len(hyps):
                    h = hyps[int(idx)]; h.setdefault("attributes", {})["semantic_role"] = role
                    h["attributes"]["semantic_source"] = "role-dynamics-llm"; h.pop("semantic_role", None); changed += 1
        (dst / "14_evaluation_model_data.json").write_text(json.dumps(md))
        (dst / "llm_log.json").write_text(json.dumps(log, indent=1))
        subprocess.run([re_.PY, str(re_.ROOT / "scripts/17_evaluate_protocol_spec.py"), str(dst / "14_evaluation_model_data.json"),
                        str(re_.truth_path(p)), str(dst / "15_evaluation_result.json"), "--messages-jsonl", str(src / "01_messages.jsonl")],
                       check=True, capture_output=True)
        r = json.loads((dst / "15_evaluation_result.json").read_text()); b = json.loads((src / "15_evaluation_result.json").read_text())
        summary[p] = dict(base=b["metrics"]["field_roles"]["f1_score"], new=r["metrics"]["field_roles"]["f1_score"],
                          overall_base=b["summary"]["overall_score"], overall_new=r["summary"]["overall_score"], changed=changed)
        print(f"{p:10s} roles {summary[p]['base']:.3f} -> {summary[p]['new']:.3f}  overall {summary[p]['overall_base']:.3f} -> "
              f"{summary[p]['overall_new']:.3f}  changed {changed}", flush=True)
    print(f"MEAN roles {np.mean([v['base'] for v in summary.values()]):.3f} -> {np.mean([v['new'] for v in summary.values()]):.3f}")
    (out_root / "summary.json").write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
