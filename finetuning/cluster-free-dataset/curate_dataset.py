#!/usr/bin/env python3
"""Select a small, tokenizer-safe, high-quality fine-tuning subset."""
from __future__ import annotations
import argparse, hashlib, json, random
from collections import Counter
from pathlib import Path

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("data_root", type=Path); p.add_argument("output", type=Path)
    p.add_argument("--tokenizer", required=True); p.add_argument("--count", type=int, default=1000)
    p.add_argument("--max-tokens", type=int, default=4096); p.add_argument("--max-boundaries", type=int, default=32)
    p.add_argument("--preferred-payload-length", type=int, default=50); p.add_argument("--seed", type=int, default=42)
    p.add_argument("--include-holdout", action="store_true", help="Deprecated; all protocol files are included by default.")
    p.add_argument("--protocol-cap", type=int, default=100)
    p.add_argument("--min-protocol-records", type=int, default=10)
    p.add_argument("--max-role-occurrences", type=int, default=3)
    p.add_argument("--max-role-record-fraction", type=float, default=.5)
    a = p.parse_args()
    if a.count < 1 or a.max_tokens < 1 or a.max_boundaries < 2: p.error("invalid limits")
    try:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(a.tokenizer)
    except Exception as exc:
        raise SystemExit(f"Tokenizer unavailable: {exc}")
    excluded = {"raw.jsonl", "curated_1000.jsonl"}
    rows = []; seen = set(); seen_prompts = set()
    rejected = Counter()
    for path in sorted(a.data_root.glob("*.jsonl")):
        if path.name in excluded or path.name.startswith("curated_"): continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip(): continue
            try:
                row = json.loads(line); meta = row["metadata"]; msgs = row["messages"]; target = json.loads(msgs[-1]["content"])
                rendered = tok.apply_chat_template(msgs[:-1], tokenize=False, add_generation_prompt=True)
                prompt_tokens = len(tok(rendered, add_special_tokens=False)["input_ids"])
                target_tokens = len(tok(msgs[-1]["content"], add_special_tokens=False)["input_ids"])
                full_rendered = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)
                total_tokens = len(tok(full_rendered, add_special_tokens=False)["input_ids"])
                if total_tokens > a.max_tokens: rejected["total_tokens"] += 1; continue
                boundaries = target.get("boundaries", [])
                payload_len = int(row.get("metadata", {}).get("payload_len", 0) or 0)
                evidence = json.loads(msgs[1]["content"].split("```json\n", 1)[1].rsplit("\n```", 1)[0])
                payload_len = int(evidence["messages"][0]["payload_len"])
                if payload_len > 200: rejected["payload_over_200"] += 1; continue
                if len(boundaries) > a.max_boundaries: rejected["dense_boundaries"] += 1; continue
                task = meta.get("task")
                if task == "boundary_refinement" and (not boundaries or boundaries[0] != 0 or boundaries[-1] != payload_len): rejected["boundary_endpoints"] += 1; continue
                if task == "semantic_labeling":
                    labels = target.get("semantic_labels", [])
                    if not labels: rejected["empty_semantics"] += 1; continue
                    keys = [(int(x["offset"]), int(x["width"]), x.get("semantic_role")) for x in labels]
                    if len(keys) != len(set(keys)): rejected["duplicate_semantic_labels"] += 1; continue
                    role_occurrences = Counter(role for _, _, role in keys)
                    if max(role_occurrences.values(), default=0) > a.max_role_occurrences: rejected["role_repetition"] += 1; continue
                    contained = False
                    for i, (off1, width1, role1) in enumerate(keys):
                        for off2, width2, role2 in keys[i + 1:]:
                            if role1 == role2 and ((off1 <= off2 and off1 + width1 >= off2 + width2) or (off2 <= off1 and off2 + width2 >= off1 + width1)):
                                contained = True; break
                        if contained: break
                    if contained: rejected["contained_same_role"] += 1; continue
                if task not in ("boundary_refinement", "semantic_labeling"): rejected["unknown_task"] += 1; continue
                semantic_score = len(target.get("semantic_labels", []))
                short_score = 1 if payload_len < a.preferred_payload_length else 0
                digest = hashlib.sha256((msgs[1]["content"] + "\0" + msgs[-1]["content"]).encode("utf-8")).hexdigest()
                if digest in seen: rejected["duplicate_prompt_target"] += 1; continue
                canonical_prompt = msgs[1]["content"]
                try:
                    prefix, encoded = canonical_prompt.split("```json\n", 1)
                    evidence_text, suffix = encoded.rsplit("\n```", 1)
                    evidence = json.loads(evidence_text)
                    for message in evidence.get("messages", []): message.pop("msg_id", None)
                    canonical_prompt = prefix + "```json\n" + json.dumps(evidence, separators=(",", ":")) + "\n```" + suffix
                except (ValueError, json.JSONDecodeError):
                    pass
                prompt_digest = hashlib.sha256((meta.get("task", "") + "\0" + canonical_prompt).encode("utf-8")).hexdigest()
                if prompt_digest in seen_prompts:
                    rejected["duplicate_prompt"] += 1; continue
                seen.add(digest)
                seen_prompts.add(prompt_digest)
                rows.append((short_score, semantic_score, prompt_tokens, target_tokens, total_tokens, row))
            except (KeyError, ValueError, IndexError, json.JSONDecodeError):
                rejected["malformed"] += 1
    rng = random.Random(a.seed); rng.shuffle(rows)
    def select_task(task):
        task_rows = [x for x in rows if x[5]["metadata"].get("task") == task]
        counts = Counter(x[5]["metadata"].get("protocol", "unknown") for x in task_rows)
        protocols = sorted(p for p, n in counts.items() if n >= a.min_protocol_records)
        pools = {p: [x for x in task_rows if x[5]["metadata"].get("protocol") == p] for p in protocols}
        for pool in pools.values(): pool.sort(key=lambda x: (-x[0], -x[1], x[4]))
        chosen = []; selected = Counter(); used = set()
        selected_roles = Counter()
        role_cache = {}
        def roles(item):
            key = id(item[5])
            if key not in role_cache:
                labels = json.loads(item[5]["messages"][-1]["content"]).get("semantic_labels", [])
                role_cache[key] = Counter(x.get("semantic_role") for x in labels if x.get("semantic_role"))
            return role_cache[key]
        def allowed(item, final_size):
            if task != "semantic_labeling": return True
            cap = max(1, round(final_size * a.max_role_record_fraction))
            return all(selected_roles[role] < cap for role in roles(item))
        def take_balanced(pool, limit):
            available = list(pool); result = []
            while available and len(result) < limit:
                if task == "semantic_labeling":
                    def score(item):
                        present = set(roles(item))
                        rare_reward = sum(1 / (1 + selected_roles[role]) for role in present) / max(1, len(present))
                        return (rare_reward, -item[4])
                    eligible = [item for item in available if allowed(item, a.count)]
                    if not eligible: break
                    best = max(eligible, key=score)
                else:
                    best = available[0]
                available.remove(best); result.append(best)
                if task == "semantic_labeling": selected_roles.update(set(roles(best)))
            return result
        quota = min(a.protocol_cap, max(1, a.count // max(1, len(protocols))))
        if task == "semantic_labeling":
            long_selected = Counter()
            while len(chosen) < a.count:
                progress = False
                for protocol in sorted(protocols, key=lambda p: (selected[p], p)):
                    if selected[protocol] >= a.protocol_cap: continue
                    available = [x for x in pools[protocol] if id(x[5]) not in used and allowed(x, a.count)]
                    if not available: continue
                    desired_long = round((selected[protocol] + 1) * .20)
                    preferred = [x for x in available if x[0] == 0] if long_selected[protocol] < desired_long else [x for x in available if x[0] == 1]
                    picked = take_balanced(preferred or available, 1)
                    if not picked: continue
                    x = picked[0]; chosen.append(x); used.add(id(x[5])); selected[protocol] += 1
                    if x[0] == 0: long_selected[protocol] += 1
                    progress = True
                    if len(chosen) >= a.count: break
                if not progress: break
            return chosen, counts
        for protocol in protocols:
            pool = pools[protocol]; long_pool = [x for x in pool if x[0] == 0]
            short_pool = [x for x in pool if x[0] == 1]
            long_take = min(len(long_pool), round(quota * .20))
            take = take_balanced(long_pool, long_take)
            take += take_balanced([x for x in short_pool if x not in take], quota-len(take))
            if len(take) < quota: take += take_balanced([x for x in pool if x not in take], quota-len(take))
            for x in take: chosen.append(x); used.add(id(x[5])); selected[protocol] += 1
        remaining = [x for x in task_rows if id(x[5]) not in used]
        remaining.sort(key=lambda x: (-x[0], -x[1], x[4]))
        while remaining and len(chosen) < a.count:
            eligible = [x for x in remaining if x[5]["metadata"].get("protocol", "unknown") in pools and selected[x[5]["metadata"].get("protocol", "unknown")] < a.protocol_cap]
            if not eligible: break
            picked = take_balanced(eligible, 1)
            if not picked: break
            x = picked[0]; remaining.remove(x)
            protocol = x[5]["metadata"].get("protocol", "unknown")
            chosen.append(x); selected[protocol] += 1
        return chosen[:a.count], counts
    boundary, boundary_counts = select_task("boundary_refinement")
    semantic, semantic_counts = select_task("semantic_labeling")
    a.output.parent.mkdir(parents=True, exist_ok=True)
    semantic_stem = a.output.stem.replace("boundary", "semantic") if "boundary" in a.output.stem else a.output.stem + "_semantic"
    semantic_path = a.output.with_name(semantic_stem + a.output.suffix)
    if semantic_path == a.output:
        raise ValueError("boundary and semantic output paths must be different")
    def training_record(item):
        row = json.loads(json.dumps(item[5]))
        prompt = row["messages"][1]["content"]
        prefix, encoded = prompt.split("```json\n", 1)
        evidence_text, suffix = encoded.rsplit("\n```", 1)
        evidence = json.loads(evidence_text)
        for message in evidence.get("messages", []): message.pop("msg_id", None)
        row["messages"][1]["content"] = prefix + "```json\n" + json.dumps(evidence, separators=(",", ":")) + "\n```" + suffix
        return row
    def write(path, values): path.write_text("\n".join(json.dumps(training_record(x), ensure_ascii=False) for x in values) + ("\n" if values else ""), encoding="utf-8")
    write(a.output, boundary); write(semantic_path, semantic)
    def report(values, counts):
        role_counts = Counter(label.get("semantic_role") for x in values for label in json.loads(x[5]["messages"][-1]["content"]).get("semantic_labels", []) if label.get("semantic_role"))
        role_records = Counter(role for x in values for role in {label.get("semantic_role") for label in json.loads(x[5]["messages"][-1]["content"]).get("semantic_labels", []) if label.get("semantic_role")})
        return {"selected": len(values), "requested": a.count, "eligible_protocols": sorted(p for p,n in counts.items() if n >= a.min_protocol_records), "excluded_protocols": sorted(p for p,n in counts.items() if n < a.min_protocol_records), "rejected": rejected, "tasks": Counter(x[5]["metadata"].get("task") for x in values), "protocols": Counter(x[5]["metadata"].get("protocol") for x in values), "semantic_roles": role_counts, "semantic_role_records": role_records, "max_prompt_tokens": max((x[2] for x in values), default=0), "max_target_tokens": max((x[3] for x in values), default=0), "max_total_tokens": max((x[4] for x in values), default=0), "max_boundaries": max((len(json.loads(x[5]["messages"][-1]["content"]).get("boundaries", [])) for x in values), default=0)}
    boundary_report, semantic_report = report(boundary, boundary_counts), report(semantic, semantic_counts)
    a.output.with_name(a.output.stem + "_summary.json").write_text(json.dumps(boundary_report, indent=2, default=dict), encoding="utf-8")
    semantic_path.with_name(semantic_path.stem + "_summary.json").write_text(json.dumps(semantic_report, indent=2, default=dict), encoding="utf-8")
    print(json.dumps({"boundary": boundary_report, "semantic": semantic_report}, indent=2, default=dict))

if __name__ == "__main__": main()
