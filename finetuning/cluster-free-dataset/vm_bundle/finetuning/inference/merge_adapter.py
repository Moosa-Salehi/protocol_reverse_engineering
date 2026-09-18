#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen2.5-Coder-7B-Instruct")
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # Merge is CPU-bound (~14 GB fp16 weights + overhead). On 48GB RAM box keep CPU path
    # explicitly to avoid accidentally placing 7B on the GPU and competing with training.
    # float16 is correct for Turing Quadro 8000; bf16 would be wrong.
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16, device_map="cpu", low_cpu_mem_usage=True, trust_remote_code=True)
    merged = PeftModel.from_pretrained(model, args.adapter).merge_and_unload()
    merged.save_pretrained(args.output, safe_serialization=True, max_shard_size="2GB")
    # prefer adapter tokenizer (has chat template) but fall back to base model
    try:
        AutoTokenizer.from_pretrained(args.adapter, trust_remote_code=True).save_pretrained(args.output)
    except Exception:
        AutoTokenizer.from_pretrained(args.model, trust_remote_code=True).save_pretrained(args.output)
    print(f"Merged model written to {args.output}")


if __name__ == "__main__":
    main()
