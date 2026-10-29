"""Parser synthesis for the largest families of a protocol (ideas 2 and 3), four arms under one label-free selection
rule (lowest description length, mdl.py):
  pipe    the pipeline's per-message edges (saved zero-shot run)
  search  local search over fixed edges, no LLM (remove / add one edge at a time, greedy)
  llm     LLM writes parser specs (dsl.py) from a statistics + samples packet, R rounds x S samples, with feedback
  agent   LLM with tools (field statistics, length-field scan, message samples, trial parse) before submitting
Per family it reports boundary P/R/F1 (truth-convention per-message boundaries) of each arm's selected candidate and,
for the LLM arms, of the best proposal by F1 (oracle, an upper bound on what selection could reach).
Results: results/<protocol>/<family>.json (resumable).

usage: synth.py <protocols> [--arms pipe,search,llm,agent] [--families 6] [--rounds 3] [--samples 2]
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

import common
import dsl
import mdl

HERE = Path(__file__).resolve().parent
URL = "http://127.0.0.1:8080/v1/chat/completions"
PAUSE = float(__import__("os").environ.get("LLM_PAUSE", "0"))   # seconds of rest before each call (laptop heat)
N_SCORE = 200
N_EVAL = 1500

DSL_DOC = """Parser spec language (JSON). {"fields": [node, ...]} where node is one of
  {"name": "x", "type": "uint", "size": 1|2|4|8, "endian": "big"|"little"}
  {"name": "x", "type": "bytes", "size": K}                               fixed-width opaque bytes or text
  {"name": "x", "type": "bytes", "size_from": "len", "adjust": 0}       width = value of earlier uint "len" + adjust
  {"name": "x", "type": "array", "count_from": "n", "item": [node, ...]} n repetitions of the item
  {"name": "x", "type": "array", "until_end": true, "item": [node, ...]} item repeated to the end of the message
  {"name": "x", "type": "tlv", "tag_size": 1, "len_size": 1, "endian": "big"}  tag-length-value records to the end
  {"name": "x", "type": "rest"}                                            all remaining bytes as one field
A message may end right after any field (later fields are then absent). Every node is one protocol field."""

GOAL = """Goal: a spec that parses ALL messages of this family and splits them into the real protocol fields.
Good specs separate constant bytes, identifiers, counters, opcodes and length fields from data; describe variable-length
parts with size_from / count_from / tlv / array instead of fixed sizes; and do not split a multi-byte number into bytes.
The spec is scored by description length (lower = better); rejected messages and unparsed bytes are expensive."""


# ------------------------------------------------------------------ evidence

def hexs(b: bytes, cap: int = 80) -> str:
    s = " ".join(f"{x:02x}" for x in b[:cap])
    return s + (" …" if len(b) > cap else "")


def evidence(pl):
    lens = Counter(len(b) for b in pl)
    med = sorted(len(b) for b in pl)[len(pl) // 2]
    lines = [f"{len(pl)} messages; length min {min(lens)}, median {med}, max {max(lens)}; most common lengths "
             + ", ".join(f"{l}({c})" for l, c in lens.most_common(5))]
    lines.append("Per offset (first 48): offset: distinct values / most common value")
    row = []
    for o in range(min(48, med)):
        c = Counter(b[o] for b in pl if len(b) > o)
        v, k = c.most_common(1)[0]
        row.append(f"{o}:{len(c)}/{v:02x}")
    lines += [" ".join(row[i:i + 12]) for i in range(0, len(row), 12)]
    by_len = {}
    for b in pl:
        by_len.setdefault(len(b), []).append(b)
    samples = []
    for l, _ in lens.most_common(10):
        samples.append(by_len[l][0])
    while len(samples) < 10 and len(samples) < len(pl):
        samples.append(pl[len(samples) * 7 % len(pl)])
    lines.append("Sample messages (hex):")
    lines += [hexs(b) for b in samples[:10]]
    return "\n".join(lines)


def evaluate_spec(spec, pl):
    segs, derived, reasons = dsl.run(spec, pl)
    bits, codes = mdl.score(pl, segs, derived, detail=True)
    rej = sum(s is None for s in segs) / len(pl)
    unc = sum(len(b) - max((e for _, _, e in s), default=0) for b, s in zip(pl, segs) if s is not None) / len(pl)
    return bits / len(pl), rej, unc, reasons, codes, segs


def feedback(spec, pl):
    try:
        bpm, rej, unc, reasons, codes, segs = evaluate_spec(spec, pl)
    except dsl.ParseError as e:
        return f"spec error: {e}"
    ex = next((s for s in segs if s), None)
    b = pl[segs.index(ex)] if ex else b""
    parse = ", ".join(f"{k}={b[s:e].hex()[:16]}" for k, s, e in (ex or [])[:16])
    return (f"score {bpm:.1f} bits/message; rejected {rej:.0%}" + (f" (reasons: {dict(Counter(reasons).most_common(3))})" if reasons else "")
            + f"; unparsed bytes per message {unc:.1f}\nfield codes: {dict(list(codes.items())[:12])}\nexample parse: {parse}")


# ------------------------------------------------------------------ LLM

def _trim(messages, budget=10500):
    """Keep the system prompt and the first user message; drop the oldest later turns until under ~budget chars."""
    msgs = list(messages)
    while sum(len(m["content"]) for m in msgs) > budget and len(msgs) > 4:
        del msgs[2:4]
    return msgs


def chat(messages, temperature=0.7, max_tokens=1500):
    messages = _trim(messages)
    if PAUSE:
        time.sleep(PAUSE)
    body = json.dumps({"messages": messages, "temperature": temperature, "max_tokens": max_tokens, "top_p": 0.9}).encode()
    req = urllib.request.Request(URL, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        out = json.loads(r.read())
    msg = out["choices"][0]["message"]
    text = re.sub(r"<think>.*?</think>", "", msg.get("content") or "", flags=re.S).strip()
    return text, out.get("usage", {})


def extract_json(text):
    text = re.sub(r"```(?:json)?", "", text)
    start = text.find("{")
    while start >= 0:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        break
        start = text.find("{", start + 1)
    return None


def labelled_block(lab):
    if not lab:
        return ""
    lines = ["Analyst-labelled messages of this family (fields separated by |). Your spec must reproduce these splits:"]
    for b, e in lab[:5]:
        pts = [0] + list(e) + [len(b)]
        lines.append(" | ".join(" ".join(f"{x:02x}" for x in b[s:t]) for s, t in zip(pts, pts[1:]) if t > s)[:300])
    return "\n".join(lines) + "\n\n"


def short(spec, n=40):
    """The spec as shown in a prompt: at most n top-level fields (long fixed field lists end in a rest field)."""
    f = spec.get("fields", []) if isinstance(spec, dict) else []
    return {"fields": f[:n] + ([{"name": "tail", "type": "rest"}] if len(f) > n else [])}


def arm_llm(pl, pipe_spec, rounds, samples, log, lab=None, lab_fb=None):
    sysmsg = {"role": "system", "content": "You reverse-engineer unknown binary network protocols from raw messages. "
              "The protocol is unknown and proprietary; reason only from the bytes and statistics shown. Reply with one JSON spec only."}
    best_spec, best_bits = pipe_spec, None
    cands = []
    for r in range(rounds):
        fb = feedback(best_spec, pl) + (lab_fb(best_spec) if lab_fb else "")
        user = (f"{DSL_DOC}\n\n{GOAL}\n\n{labelled_block(lab)}Family evidence:\n{evidence(pl)}\n\nCurrent best spec:\n{json.dumps(short(best_spec))}\n"
                f"Its result: {fb}\n\nWrite an improved spec (JSON only).")
        for s in range(samples):
            t0 = time.time()
            try:
                text, usage = chat([sysmsg, {"role": "user", "content": user}])
            except Exception as e:      # server hiccup: skip this sample
                log.append({"round": r, "error": str(e)}); continue
            spec = extract_json(text)
            entry = {"round": r, "sample": s, "secs": round(time.time() - t0, 1), "usage": usage, "spec": spec}
            if spec:
                try:
                    bpm, rej, unc, _, _, _ = evaluate_spec(spec, pl)
                    entry.update(bits=bpm, rejected=rej, unparsed=unc)
                    cands.append((bpm, spec))
                    if best_bits is None or bpm < best_bits:
                        best_bits, best_spec = bpm, spec
                except dsl.ParseError as e:
                    entry["error"] = str(e)
            else:
                entry["raw"] = text[:500]
            log.append(entry)
    return cands


# ------------------------------------------------------------------ agent (idea 3)

def tool_stats(pl, o, w, endian):
    vals = [int.from_bytes(b[o:o + w], "little" if endian == "little" else "big") for b in pl if len(b) >= o + w]
    if not vals:
        return "no message is that long"
    c = Counter(vals)
    lens = [len(b) for b in pl if len(b) >= o + w]
    inc = sum(1 for a, b in zip(vals, vals[1:]) if b > a) / max(1, len(vals) - 1)
    rel = []
    for name, ref in (("total length", lens), ("bytes after field", [l - o - w for l in lens])):
        d = Counter(r - v for r, v in zip(ref, vals)).most_common(1)[0]
        if d[1] >= 0.98 * len(vals):
            rel.append(f"equals {name} - {d[0]}")
    return (f"offset {o} size {w} {endian}: {len(c)} distinct of {len(vals)}; top {[(hex(v), k) for v, k in c.most_common(5)]}; "
            f"min {min(vals)} max {max(vals)}; increasing step fraction {inc:.2f}" + (f"; {'; '.join(rel)}" if rel else ""))


def tool_length_fields(pl):
    out = []
    for o in range(0, 32):
        for w in (1, 2, 4):
            for en in ("big", "little"):
                if w == 1 and en == "little":
                    continue
                s = tool_stats(pl, o, w, en)
                if "equals" in s and "distinct of" in s and not s.split(":")[1].strip().startswith("1 distinct"):
                    out.append(s)
    return "\n".join(out[:12]) or "no field equals the message length or the remaining bytes"


TOOLS_DOC = """Tools (reply with exactly one JSON object per turn):
  {"tool": "stats", "offset": O, "size": 1|2|4|8, "endian": "big"|"little"}   value statistics of a field
  {"tool": "length_fields"}                                                    fields whose value matches a length
  {"tool": "messages", "length": L or null, "n": 8}                            show messages (optionally of one length)
  {"tool": "try", "spec": {...}}                                               score a spec and show an example parse
  {"submit": {...spec...}}                                                     final answer
Use the tools to test hypotheses before submitting; at most 10 turns."""


def arm_agent(pl, pipe_spec, log, max_turns=8, lab=None, lab_fb=None):
    sysmsg = {"role": "system", "content": "You reverse-engineer unknown binary network protocols from raw messages by "
              "testing hypotheses with tools. The protocol is unknown and proprietary; reason only from the data."}
    msgs = [sysmsg, {"role": "user", "content": f"{DSL_DOC}\n\n{GOAL}\n\n{TOOLS_DOC}\n\n{labelled_block(lab)}Family evidence:\n{evidence(pl)}\n\n"
                     f"Pipeline's spec: {json.dumps(short(pipe_spec))}\nIts result: {feedback(pipe_spec, pl)}\n\nStart."}]
    cands = []
    for turn in range(max_turns):
        try:
            text, usage = chat(msgs, temperature=0.4)
        except Exception as e:
            log.append({"turn": turn, "error": str(e)}); break
        act = extract_json(text) or {}
        msgs.append({"role": "assistant", "content": text[:2000]})
        entry = {"turn": turn, "action": act, "usage": usage}
        spec = act.get("submit") or (act.get("spec") if act.get("tool") == "try" else None)
        if spec:
            try:
                bpm, rej, unc, _, _, _ = evaluate_spec(spec, pl)
                cands.append((bpm, spec)); entry.update(bits=bpm, rejected=rej, unparsed=unc)
            except dsl.ParseError as e:
                entry["error"] = str(e)
        log.append(entry)
        if "submit" in act:
            entry["submitted"] = True
            break
        t = act.get("tool")
        try:
            if t == "stats":
                res = tool_stats(pl, int(act.get("offset", 0)), int(act.get("size", 1)), act.get("endian", "big"))
            elif t == "length_fields":
                res = tool_length_fields(pl)
            elif t == "messages":
                L = act.get("length")
                sel = [b for b in pl if L is None or len(b) == int(L)][: int(act.get("n", 8) or 8)]
                res = "\n".join(hexs(b) for b in sel) or "none"
            elif t == "try":
                res = feedback(spec, pl) + (lab_fb(spec) if lab_fb else "")
            else:
                res = "Unknown action. Reply with one JSON tool call or {\"submit\": spec}."
        except Exception as e:  # malformed arguments
            res = f"tool error: {e}"
        msgs.append({"role": "user", "content": res[:1500] + ("\nNext action?" if turn < max_turns - 2 else "\nSubmit now.")})
    return cands


# ------------------------------------------------------------------ local search (no LLM)

def arm_search(pl, pipe_edges, max_iter=40):
    cur = [set(e) for e in pipe_edges]
    def bits(es):
        return mdl.score(pl, mdl.edges_to_segs(pl, es)) / len(pl)
    best = bits(cur)
    maxlen = min(64, max(len(b) for b in pl))
    for _ in range(max_iter):
        moves = []
        present = Counter(x for e in cur for x in e)
        for x in present:
            moves.append(("del", x))
        for x in range(1, maxlen):
            if x not in present:
                moves.append(("add", x))
        improved = None
        for kind, x in moves:
            es = [e - {x} if kind == "del" else (e | {x} if x < len(b) else e) for e, b in zip(cur, pl)]
            v = bits(es)
            if v < best - 1e-9 and (improved is None or v < improved[0]):
                improved = (v, es)
        if not improved:
            break
        best, cur = improved
    return [sorted(e) for e in cur], best


# ------------------------------------------------------------------ driver

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("protocols")
    ap.add_argument("--arms", default="pipe,search,llm,agent")
    ap.add_argument("--families", type=int, default=6)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--samples", type=int, default=2)
    ap.add_argument("--out", default=None)
    ap.add_argument("--fewshot", action="store_true", help="fs50 runs + analyst labels; selection by label agreement")
    args = ap.parse_args()
    arms = args.arms.split(",")
    mode = "fs50" if args.fewshot else "zs"
    args.out = args.out or str(HERE / ("results-fs50" if args.fewshot else "results"))
    model = "?"
    try:
        model = json.loads(urllib.request.urlopen(URL.replace("chat/completions", "models"), timeout=5).read())["data"][0]["id"]
    except Exception:
        pass
    for p in args.protocols.split(","):
        d = common.load(p, mode)
        need_lab = 2 if args.fewshot else 0
        fams = sorted(((f, m) for f, m in d["fams"].items() if sum(i in d["truth"] for i in m) >= 5
                       and sum(i in d["labels"] for i in m) >= need_lab), key=lambda x: -len(x[1]))[: args.families]
        for f, mids in fams:
            out = Path(args.out) / p / f"{f}.json"
            res = json.loads(out.read_text()) if out.exists() else {"protocol": p, "family": f, "arms": {}}
            step = max(1, len(mids) // N_SCORE)
            score_ids = mids[::step][:N_SCORE]
            eval_ids = [i for i in mids if i in d["truth"] and i not in d["labels"]][:N_EVAL]
            lab_ids = [i for i in mids if i in d["labels"]]
            lab = [(d["payload"][i], d["labels"][i]) for i in lab_ids]
            lpl = [b for b, _ in lab]

            def lab_f1(spec):
                segs, _, _ = dsl.run(spec, lpl)
                pred = {i: dsl.edges(s_, len(b)) for i, s_, b in zip(lab_ids, segs, lpl) if s_ is not None}
                return common.prf(pred, d["labels"], lab_ids)["f1"], sum(s_ is None for s_ in segs)

            def lab_fb(spec):
                try:
                    f1, rej = lab_f1(spec)
                except dsl.ParseError:
                    return ""
                return f"\nagreement with the analyst labels: F1 {f1:.2f}" + (f", {rej} labelled messages rejected" if rej else "")
            pl = [d["payload"][i] for i in score_ids]
            epl = [d["payload"][i] for i in eval_ids]
            pipe_edges = [d["pipe"][i] for i in score_ids]
            med_len = sorted(len(b) for b in pl)[len(pl) // 2]
            pipe_spec = dsl.fixed_spec(Counter(x for e in pipe_edges for x in e).most_common() and
                                       sorted({x for x, c in Counter(x for e in pipe_edges for x in e).items() if c >= 0.5 * len(pipe_edges)}), med_len)
            pipe_bits = mdl.score(pl, mdl.edges_to_segs(pl, pipe_edges)) / len(pl)
            pipe_eval = common.prf({i: d["pipe"][i] for i in eval_ids}, d["truth"], eval_ids)

            def spec_eval(spec):
                segs, _, _ = dsl.run(spec, epl)
                pred = {i: (dsl.edges(s, len(b)) if s is not None else d["pipe"][i]) for i, s, b in zip(eval_ids, segs, epl)}
                return common.prf(pred, d["truth"], eval_ids), sum(s is None for s in segs) / len(epl)

            for arm in arms:
                if arm in res["arms"]:
                    continue
                t0 = time.time(); log = []
                if arm == "pipe":
                    r = dict(bits=pipe_bits, **pipe_eval)
                elif arm == "search":
                    es, b = arm_search(pl, pipe_edges)
                    # apply the searched edge set as a fixed-offset list (majority over the scoring sample)
                    cnt = Counter(x for e in es for x in e)
                    keep = {x for x, c in cnt.items() if c >= 0.5 * sum(1 for bb in pl if len(bb) > x)}
                    pred = {i: sorted(x for x in keep if x < len(d["payload"][i])) for i in eval_ids}
                    r = dict(bits=b, **common.prf(pred, d["truth"], eval_ids))
                else:
                    kw = dict(lab=lab, lab_fb=lab_fb) if args.fewshot else {}
                    cands = arm_llm(pl, pipe_spec, args.rounds, args.samples, log, **kw) if arm == "llm" else arm_agent(pl, pipe_spec, log, **kw)
                    scored = []
                    for bpm, spec in cands:
                        ev, rej = spec_eval(spec)
                        row = dict(bits=bpm, rejected_eval=rej, **ev)
                        if args.fewshot:
                            row["label_f1"], row["label_rejected"] = lab_f1(spec)
                            row["rejected_score"] = sum(s_ is None for s_ in dsl.run(spec, pl)[0]) / len(pl)
                        scored.append(row)
                    base = dict(bits=pipe_bits, pipeline=True, **pipe_eval)
                    if args.fewshot:   # replace the pipeline only by a spec that reproduces the labels and parses the family
                        ok = [x for x in scored if x["label_f1"] >= 0.95 and x["rejected_score"] <= 0.05]
                        sel = min(ok, key=lambda x: (-x["label_f1"], x["bits"])) if ok else base
                    else:
                        sel = min([base] + scored, key=lambda x: x["bits"])
                    oracle = max([dict(pipeline=True, **pipe_eval)] + scored, key=lambda x: x["f1"])
                    r = dict(selected=sel, oracle=oracle, n_candidates=len(cands), n_valid=len(scored), candidates=scored)
                if any(str(e.get("error", "")).startswith(("HTTP", "<urlopen", "timed out")) for e in log):
                    print(f"{p:9s} {f:12s} {arm:6s} server errors, not saved (will be retried)", flush=True)
                    continue
                r["secs"] = round(time.time() - t0, 1); r["model"] = model; r["log"] = log
                res["arms"][arm] = r
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(json.dumps(res, indent=1, default=str))
                f1 = r.get("f1", r.get("selected", {}).get("f1"))
                extra = f" oracle {r['oracle']['f1']:.3f} valid {r['n_valid']}/{r['n_candidates']}" if "oracle" in r else ""
                print(f"{p:9s} {f:12s} n={len(mids):5d} {arm:6s} f1 {f1:.3f}{extra}  ({r['secs']:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
