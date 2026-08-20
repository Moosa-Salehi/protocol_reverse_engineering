#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig,
    DataCollatorForSeq2Seq, Trainer, TrainingArguments,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Low-memory QLoRA training for Qwen2.5-Coder-7B-Instruct.")
    parser.add_argument("--model", default="Qwen/Qwen2.5-Coder-7B-Instruct")
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-length", type=int, default=1024)
    parser.add_argument("--epochs", type=float, default=2.0)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--lora-rank", type=int, default=16)
    parser.add_argument("--gradient-accumulation", type=int, default=16)
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU not detected. Install the CUDA PyTorch build and current NVIDIA drivers.")
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    tokenizer = AutoTokenizer.from_pretrained(args.model, use_fast=True)
    tokenizer.pad_token = tokenizer.eos_token
    quantization = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float16)
    model = AutoModelForCausalLM.from_pretrained(args.model, quantization_config=quantization, device_map={"": 0}, torch_dtype=torch.float16, low_cpu_mem_usage=True)
    model.config.use_cache = False
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    model = get_peft_model(model, LoraConfig(
        r=args.lora_rank, lora_alpha=args.lora_rank * 2, lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    ))
    dataset = load_dataset("json", data_files={"train": str(args.train), "validation": str(args.validation)})

    def tokenize(record):
        messages = record["messages"]
        prompt_messages = messages[:-1]
        prompt_text = tokenizer.apply_chat_template(prompt_messages, tokenize=False, add_generation_prompt=True)
        full_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        prompt_ids = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
        full_ids = tokenizer(full_text, add_special_tokens=False)["input_ids"]
        crop_start = max(0, len(full_ids) - args.max_length)
        input_ids = full_ids[crop_start:]
        visible_prompt = max(0, len(prompt_ids) - crop_start)
        labels = [-100] * min(visible_prompt, len(input_ids)) + input_ids[visible_prompt:]
        return {"input_ids": input_ids, "attention_mask": [1] * len(input_ids), "labels": labels}

    tokenized = dataset.map(tokenize, remove_columns=dataset["train"].column_names, desc="Tokenizing and masking prompt tokens")
    if not any(any(label != -100 for label in row["labels"]) for row in tokenized["train"]):
        raise RuntimeError("All assistant responses were truncated. Increase --max-length or shorten evidence.")
    training_args = TrainingArguments(
        output_dir=str(args.output), num_train_epochs=args.epochs, learning_rate=args.learning_rate,
        per_device_train_batch_size=1, per_device_eval_batch_size=1,
        gradient_accumulation_steps=args.gradient_accumulation, gradient_checkpointing=True,
        fp16=True, bf16=False, optim="paged_adamw_8bit", lr_scheduler_type="cosine", warmup_ratio=0.03,
        logging_steps=5, eval_strategy="epoch", save_strategy="epoch", save_total_limit=2,
        report_to="none", remove_unused_columns=False, group_by_length=True,
    )
    trainer = Trainer(model=model, args=training_args, train_dataset=tokenized["train"], eval_dataset=tokenized["validation"], data_collator=DataCollatorForSeq2Seq(tokenizer, padding=True, label_pad_token_id=-100))
    trainer.train()
    trainer.save_model(str(args.output / "adapter"))
    tokenizer.save_pretrained(str(args.output / "adapter"))
    (args.output / "training_config.json").write_text(json.dumps(vars(args), default=str, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
