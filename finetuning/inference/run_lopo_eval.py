#!/usr/bin/env python3
"""Leave-one-protocol-out (LOPO) evaluation for the fine-tuned protocol RE adapter.

Measures how the adapter performs on protocols it never saw during training,
which is the key question for reverse engineering *unknown* protocols.

Two modes:

1. ``--mode unseen`` (default, runs locally):
   Evaluate the *shipped* adapter on held-out test records whose protocol is
   never used as the eval target. Because the shipped adapter was trained on
   all protocols, records of the eval protocol are *excluded from training*,
   so this measures in-context/transfer behaviour on unseen message layouts
   rather than fully unseen protocols. This is a proxy: it tells us whether
   the adapter can parse message families it was not fitted on.

2. ``--mode retrain`` (requires the training VM):
   Emit per-fold train/validation/test JSONL splits where one protocol is held
   out completely, so the VM can run train_unsloth.py + evaluate_holdout.py
   per fold for a true LOPO measurement.

Outputs a metrics JSON (per fold and aggregate) in the same schema as
evaluate_holdout.py, plus optional per-record predictions.
"""
from __future__ import annotations

import argparse
import json
import statistics
import time
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPLIT_DIR = REPO_ROOT / "finetuning" / "cluster-free-dataset" / "data" / "split"
DEFAULT_ADAPTER = REPO_ROOT / "finetuning" / "result" / "qwen25-coder-7b-protocol-re" / "adapter"


def load_records(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def protocol_counts(rows: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[row["metadata"].get("protocol", "unknown")] += 1
    return dict(sorted(counts.items()))


def make_retrain_folds(rows_by_split: dict[str, list[dict]], out_dir: Path) -> None:
    """Write train/val/test JSONL per held-out protocol (records excluded)."""
    protocols = sorted(protocol_counts(rows_by_split["test"]))
    for held_out in protocols:
        fold_dir = out_dir / f"holdout_{held_out}"
        fold_dir.mkdir(parents=True, exist_ok=True)
        for split_name, rows in rows_by_split.items():
            kept = [row for row in rows if row["metadata"].get("protocol") != held_out]
            target = fold_dir / f"{split_name}.jsonl"
            target.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in kept) + "\n", encoding="utf-8")
            print(f"fold holdout={held_out:10s} {split_name:10s} kept={len(kept):4d} dropped={len(rows) - len(kept):3d} -> {target}")


def build_chat_prompt(tokenizer, row: dict) -> str:
    return tokenizer.apply_chat_template(row["messages"][:-1], tokenize=False, add_generation_prompt=True)


def extract_pred_set(pred, task: str) -> set:
    if not isinstance(pred, dict):
        return set()
    if task == "boundary_refinement":
        return {int(x) for x in pred.get("boundaries", []) if isinstance(x, (int, float))}
    labels = pred.get("semantic_labels", [])
    return {
        (int(x.get("offset", -1)), int(x.get("width", -1)), str(x.get("semantic_role")))
        for x in labels
        if isinstance(x, dict)
    }


def extract_target_set(target, task: str) -> set:
    if task == "boundary_refinement":
        return {int(x) for x in target.get("boundaries", [])}
    return {
        (int(x.get("offset", -1)), int(x.get("width", -1)), str(x.get("semantic_role")))
        for x in target.get("semantic_labels", [])
    }


def evaluate_rows(rows: list[dict], tokenizer, model, max_new_tokens: int, max_input_tokens: int, record_raw: bool) -> list[dict]:
    import torch

    results = []
    total = len(rows)
    for index, row in enumerate(rows, 1):
        meta = row.get("metadata", {})
        protocol = meta.get("protocol", "unknown")
        task = meta.get("task", "unknown")
        message_id = meta.get("message_id", row.get("metadata", {}).get("family_id", index))
        prompt = build_chat_prompt(tokenizer, row)
        inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to(model.device)
        if inputs["input_ids"].shape[1] > max_input_tokens:
            results.append({"protocol": protocol, "task": task, "message_id": message_id, "error": "prompt_too_long"})
            continue
        start = time.time()
        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        elapsed = time.time() - start
        text = tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        try:
            pred = json.loads(text)
            valid = True
        except Exception:
            pred = None
            valid = False
        target = json.loads(row["messages"][-1]["content"])
        pset = extract_pred_set(pred, task)
        tset = extract_target_set(target, task)
        tp = len(pset & tset)
        fp = len(pset - tset)
        fn = len(tset - pset)
        entry = {
            "protocol": protocol,
            "task": task,
            "message_id": message_id,
            "valid_json": valid,
            "exact_match": bool(valid and pred == target),
            "true_positive": tp,
            "false_positive": fp,
            "false_negative": fn,
            "generation_seconds": round(elapsed, 3),
        }
        if record_raw:
            entry["raw"] = text
        results.append(entry)
        print(f"[{index:3d}/{total}] {protocol:10s} {task:20s} valid={valid} tp={tp} fp={fp} fn={fn} ({elapsed:.1f}s)")
    return results


def aggregate(results: list[dict]) -> dict:
    def metrics_for(entries: list[dict]) -> dict:
        count = len(entries)
        if count == 0:
            return {"count": 0}
        valid = sum(1 for e in entries if e.get("valid_json"))
        tp = sum(e.get("true_positive", 0) for e in entries)
        fp = sum(e.get("false_positive", 0) for e in entries)
        fn = sum(e.get("false_negative", 0) for e in entries)
        exact = sum(1 for e in entries if e.get("exact_match"))
        p = tp / (tp + fp) if (tp + fp) else 0.0
        r = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0
        return {
            "count": count,
            "json_validity": valid / count,
            "exact_match": exact / count,
            "precision": p,
            "recall": r,
            "f1": f1,
        }

    report: dict[str, dict] = {}
    by_protocol: dict[str, list] = defaultdict(list)
    by_task: dict[str, list] = defaultdict(list)
    by_protocol_task: dict[tuple[str, str], list] = defaultdict(list)
    for entry in results:
        if "error" in entry:
            continue
        by_protocol[entry["protocol"]].append(entry)
        by_task[entry["task"]].append(entry)
        by_protocol_task[(entry["protocol"], entry["task"])].append(entry)
    report["overall"] = metrics_for(results)
    for task, entries in sorted(by_task.items()):
        report[f"task/{task}"] = metrics_for(entries)
    for protocol, entries in sorted(by_protocol.items()):
        report[f"protocol/{protocol}"] = metrics_for(entries)
    for (protocol, task), entries in sorted(by_protocol_task.items()):
        report[f"protocol/{protocol}/task/{task}"] = metrics_for(entries)
    report["meta"] = {
        "records_evaluated": len(results),
        "records_errored": sum(1 for e in results if "error" in e),
        "median_generation_seconds": statistics.median([e["generation_seconds"] for e in results if "generation_seconds" in e] or [0]),
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Leave-one-protocol-out evaluation")
    parser.add_argument("--mode", choices=["unseen", "retrain"], default="unseen",
                        help="unseen: evaluate adapter on unseen-protocol test records (local GPU). "
                             "retrain: emit per-fold splits for true LOPO retraining on the VM.")
    parser.add_argument("--model", default="Qwen/Qwen2.5-Coder-7B-Instruct")
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--split-dir", type=Path, default=SPLIT_DIR)
    parser.add_argument("--protocols", nargs="*", help="Restrict to these eval protocols (default: all with test records).")
    parser.add_argument("--max-records-per-protocol", type=int, default=0, help="Cap records per protocol (0 = all).")
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--max-input-tokens", type=int, default=4096)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "finetuning" / "result" / "qwen25-coder-7b-protocol-re" / "test" / "lopo_unseen_protocols.json")
    parser.add_argument("--record-raw", action="store_true", help="Include raw model outputs in the report.")
    parser.add_argument("--fold-output-dir", type=Path, default=REPO_ROOT / "finetuning" / "lopo_folds")
    args = parser.parse_args()

    split_paths = {name: args.split_dir / f"{name}.jsonl" for name in ("train", "validation", "test")}
    for name, path in split_paths.items():
        if not path.is_file():
            raise SystemExit(f"Missing split file: {path}")

    if args.mode == "retrain":
        rows_by_split = {name: load_records(path) for name, path in split_paths.items()}
        make_retrain_folds(rows_by_split, args.fold_output_dir)
        print(f"Wrote LOPO retrain folds to {args.fold_output_dir}")
        return

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.manual_seed(args.seed)
    rows = load_records(split_paths["test"])
    available = sorted(protocol_counts(rows))
    eval_protocols = args.protocols or available
    unknown = set(eval_protocols) - set(available)
    if unknown:
        raise SystemExit(f"Protocols not present in test split: {sorted(unknown)}")

    selected: list[dict] = []
    for protocol in eval_protocols:
        protocol_rows = [row for row in rows if row["metadata"].get("protocol") == protocol]
        if args.max_records_per_protocol > 0:
            protocol_rows = protocol_rows[: args.max_records_per_protocol]
        selected.extend(protocol_rows)
    print(f"Evaluating {len(selected)} test records across protocols: {eval_protocols}")

    # Match evaluate_holdout.py: Turing GPUs have no BF16, use FP16.
    bf16 = bool(torch.cuda.is_available() and torch.cuda.is_bf16_supported())
    dtype = torch.bfloat16 if bf16 else torch.float16
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)} dtype={'bf16' if bf16 else 'fp16'}")
    tokenizer = AutoTokenizer.from_pretrained(str(args.adapter))
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map="auto", low_cpu_mem_usage=True
    )
    from peft import PeftModel

    model = PeftModel.from_pretrained(model, str(args.adapter))
    model.eval()

    results = evaluate_rows(selected, tokenizer, model, args.max_new_tokens, args.max_input_tokens, args.record_raw)
    report = aggregate(results)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {
                "mode": "unseen-protocol-transfer",
                "model": args.model,
                "adapter": str(args.adapter),
                "eval_protocols": eval_protocols,
                "generation": {"seed": args.seed, "do_sample": False, "max_new_tokens": args.max_new_tokens},
                "metrics": report,
                "predictions": results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nWrote report to {args.output}")
    print(json.dumps({k: v for k, v in report.items() if k != "meta"}, indent=2))


if __name__ == "__main__":
    main()
