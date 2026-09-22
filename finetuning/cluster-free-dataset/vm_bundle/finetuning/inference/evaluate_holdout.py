#!/usr/bin/env python3
"""Evaluate a causal LM on an approved evaluation JSONL split."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


VALID_TASKS = {
    "boundary_refinement",
    "semantic_labeling",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate a base model or a PEFT adapter on a JSONL holdout."
    )

    parser.add_argument(
        "--data",
        type=Path,
        required=True,
        help="Approved evaluation JSONL file.",
    )
    parser.add_argument(
        "--model",
        default="Qwen/Qwen2.5-Coder-7B-Instruct",
        help="Base model name or local path.",
    )
    parser.add_argument(
        "--adapter",
        type=Path,
        default=None,
        help="Optional PEFT adapter directory.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output report JSON path.",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=512,
    )
    parser.add_argument(
        "--max-input-tokens",
        type=int,
        default=4096,
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )
    parser.add_argument(
        "--dtype",
        choices=("fp16", "fp32"),
        default="fp16",
        help="Evaluation precision. FP16 is recommended for RTX 8000.",
    )

    return parser.parse_args()


def load_jsonl(path: Path):
    if not path.is_file():
        raise FileNotFoundError(f"Evaluation data not found: {path}")

    data_bytes = path.read_bytes()

    rows = [
        json.loads(line)
        for line in data_bytes.decode("utf-8").splitlines()
        if line.strip()
    ]

    if not rows:
        raise ValueError("Evaluation dataset is empty.")

    return data_bytes, rows


def validate_rows(rows):
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(
                f"Record {index} must be a JSON object."
            )

        messages = row.get("messages")

        if not isinstance(messages, list):
            raise ValueError(
                f"Record {index}: messages must be a list."
            )

        roles = [
            message.get("role")
            for message in messages
            if isinstance(message, dict)
        ]

        if len(roles) != len(messages):
            raise ValueError(
                f"Record {index}: each message must be an object."
            )

        if roles != ["system", "user", "assistant"]:
            raise ValueError(
                f"Record {index}: invalid chat roles: {roles}"
            )

        metadata = row.get("metadata", {})

        if not isinstance(metadata, dict):
            raise ValueError(
                f"Record {index}: metadata must be an object."
            )

        task = metadata.get("task")

        if task not in VALID_TASKS:
            raise ValueError(
                f"Record {index}: unsupported task {task!r}."
            )

        try:
            target = json.loads(messages[-1]["content"])
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError(
                f"Record {index}: assistant target is not valid JSON."
            ) from exc

        if not isinstance(target, dict):
            raise ValueError(
                f"Record {index}: assistant target must be a JSON object."
            )


def normalize_dtype(dtype_name: str):
    if dtype_name == "fp16":
        return torch.float16

    return torch.float32


def load_model_and_tokenizer(args):
    dtype = normalize_dtype(args.dtype)

    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA is not available. This evaluation is configured for GPU."
        )

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"BF16 hardware support: {torch.cuda.is_bf16_supported()}")
    print(f"Evaluation dtype: {args.dtype}")

    if args.dtype == "fp16" and not torch.cuda.is_available():
        raise RuntimeError("FP16 GPU evaluation requires CUDA.")

    # Always load the tokenizer from the base model.
    # The adapter directory may not contain a complete tokenizer.
    tokenizer = AutoTokenizer.from_pretrained(
        args.model,
        use_fast=True,
    )

    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=dtype,
        device_map="auto",
        low_cpu_mem_usage=True,
    )

    if args.adapter is not None:
        if not args.adapter.is_dir():
            raise FileNotFoundError(
                f"Adapter directory not found: {args.adapter}"
            )

        from peft import PeftModel

        model = PeftModel.from_pretrained(
            model,
            str(args.adapter),
        )

    model.eval()

    return model, tokenizer


def canonical(value: Any) -> str:
    """Convert JSON-compatible values to stable hashable strings."""
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )


def extract_semantic_roles(value):
    if not isinstance(value, dict):
        return set()

    labels = value.get("semantic_labels", [])

    if not isinstance(labels, list):
        return set()

    result = set()

    for item in labels:
        if not isinstance(item, dict):
            continue

        result.add(
            canonical(
                (
                    item.get("field_index"),
                    item.get("semantic_role"),
                )
            )
        )

    return result


def extract_boundaries(value):
    if not isinstance(value, dict):
        return set()

    boundaries = value.get("boundaries", [])

    if not isinstance(boundaries, list):
        return set()

    return {
        canonical(boundary)
        for boundary in boundaries
    }


def extract_items(value, task):
    if task == "semantic_labeling":
        return extract_semantic_roles(value)

    if task == "boundary_refinement":
        return extract_boundaries(value)

    return set()


def new_stat():
    return {
        "count": 0,
        "valid_json": 0,
        "exact": 0,
        "tp": 0,
        "fp": 0,
        "fn": 0,
        "parse_errors": 0,
    }


def calculate_metrics(stat):
    count = stat["count"]

    precision_denominator = stat["tp"] + stat["fp"]
    recall_denominator = stat["tp"] + stat["fn"]
    f1_denominator = (
        2 * stat["tp"] + stat["fp"] + stat["fn"]
    )

    return {
        "count": count,
        "valid_json": stat["valid_json"],
        "parse_errors": stat["parse_errors"],
        "json_validity": (
            stat["valid_json"] / count
            if count
            else 0.0
        ),
        "exact_match": (
            stat["exact"] / count
            if count
            else 0.0
        ),
        "true_positive": stat["tp"],
        "false_positive": stat["fp"],
        "false_negative": stat["fn"],
        "precision": (
            stat["tp"] / precision_denominator
            if precision_denominator
            else 0.0
        ),
        "recall": (
            stat["tp"] / recall_denominator
            if recall_denominator
            else 0.0
        ),
        "f1": (
            2 * stat["tp"] / f1_denominator
            if f1_denominator
            else 0.0
        ),
    }


def get_input_device(model):
    """
    Find the input embedding device.
    This is safer than assuming model.device when device_map='auto'.
    """
    return model.get_input_embeddings().weight.device


def main():
    args = parse_args()

    if args.max_new_tokens <= 0:
        raise ValueError("--max-new-tokens must be positive.")

    if args.max_input_tokens <= 0:
        raise ValueError("--max-input-tokens must be positive.")

    torch.manual_seed(args.seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)

    data_bytes, rows = load_jsonl(args.data)
    validate_rows(rows)

    print(f"Evaluation records: {len(rows)}")
    print(f"Dataset: {args.data}")
    print(f"Dataset SHA256: {hashlib.sha256(data_bytes).hexdigest()}")

    model, tokenizer = load_model_and_tokenizer(args)

    totals = defaultdict(new_stat)
    predictions = []

    input_device = get_input_device(model)

    for index, row in enumerate(rows, start=1):
        metadata = row.get("metadata", {})
        protocol = metadata.get("protocol", "unknown")
        task = metadata.get("task", "unknown")
        family = str(metadata.get("family_id", "unknown"))

        messages = row["messages"]
        target = json.loads(messages[-1]["content"])

        prompt = tokenizer.apply_chat_template(
            messages[:-1],
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            add_special_tokens=False,
        )

        input_length = inputs["input_ids"].shape[1]

        if input_length > args.max_input_tokens:
            raise ValueError(
                f"Record {index}: prompt length {input_length} exceeds "
                f"--max-input-tokens={args.max_input_tokens} "
                f"for {protocol}/{family}/{task}."
            )

        inputs = {
            key: value.to(input_device)
            for key, value in inputs.items()
        }

        with torch.inference_mode():
            output = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

        generated_ids = output[0, input_length:]

        raw_text = tokenizer.decode(
            generated_ids,
            skip_special_tokens=True,
        ).strip()

        try:
            prediction = json.loads(raw_text)
            valid_json = True
        except (json.JSONDecodeError, TypeError):
            prediction = None
            valid_json = False

        exact = prediction == target

        predicted_items = extract_items(prediction, task)
        target_items = extract_items(target, task)

        true_positive = len(predicted_items & target_items)
        false_positive = len(predicted_items - target_items)
        false_negative = len(target_items - predicted_items)

        keys = (
            ("overall", task),
            ("protocol", protocol, task),
            ("family", protocol, family, task),
        )

        for key in keys:
            stat = totals[key]

            stat["count"] += 1
            stat["valid_json"] += int(valid_json)
            stat["parse_errors"] += int(not valid_json)
            stat["exact"] += int(exact)
            stat["tp"] += true_positive
            stat["fp"] += false_positive
            stat["fn"] += false_negative

        predictions.append(
            {
                "record_index": index,
                "metadata": metadata,
                "prediction": prediction,
                "raw": raw_text,
                "target": target,
                "valid_json": valid_json,
                "exact_match": exact,
            }
        )

        print(
            f"[{index}/{len(rows)}] "
            f"task={task} protocol={protocol} "
            f"valid_json={valid_json} exact_match={exact}"
        )

    report = {
        "/".join(key): calculate_metrics(stat)
        for key, stat in totals.items()
    }

    generation = {
        "seed": args.seed,
        "do_sample": False,
        "max_input_tokens": args.max_input_tokens,
        "max_new_tokens": args.max_new_tokens,
        "dtype": args.dtype,
    }

    result = {
        "model": args.model,
        "adapter": (
            str(args.adapter)
            if args.adapter is not None
            else None
        ),
        "dataset_sha256": hashlib.sha256(data_bytes).hexdigest(),
        "generation": generation,
        "records": len(rows),
        "metrics": report,
        "predictions": predictions,
    }

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    args.output.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\n== Evaluation metrics ==")
    print(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        )
    )

    print(f"\nReport saved: {args.output}")


if __name__ == "__main__":
    main()
