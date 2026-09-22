#!/usr/bin/env python3
from __future__ import annotations

import os
os.environ["UNSLOTH_RETURN_LOGITS"] = "1"

import argparse
import inspect
import json
from pathlib import Path

from datasets import load_dataset

from unsloth import FastLanguageModel
from unsloth.chat_templates import train_on_responses_only
from trl import SFTTrainer, SFTConfig


class ConfidenceWeightedSFTTrainer(SFTTrainer):
    """
    SFTTrainer with per-example confidence weighting.

    Important:
    - Trainer removes unused raw columns such as `text`.
    - `sample_weight` is explicitly preserved.
    - `compute_loss()` consumes `sample_weight`.
    """

    def _set_signature_columns_if_needed(self):
        super()._set_signature_columns_if_needed()

        if self._signature_columns is not None:
            if "sample_weight" not in self._signature_columns:
                self._signature_columns.append("sample_weight")

    def compute_loss(
        self,
        model,
        inputs,
        return_outputs=False,
        num_items_in_batch=None,
    ):
        weights = inputs.pop("sample_weight", None)

        outputs = model(**inputs)

        if weights is None:
            return (
                (outputs.loss, outputs)
                if return_outputs
                else outputs.loss
            )

        labels = inputs["labels"]

        logits = outputs.logits[..., :-1, :].contiguous()
        shifted = labels[..., 1:].contiguous()

        import torch

        token_loss = torch.nn.functional.cross_entropy(
            logits.view(-1, logits.size(-1)),
            shifted.view(-1),
            reduction="none",
            ignore_index=-100,
        ).view(shifted.size())

        mask = shifted.ne(-100)

        per_example_loss = (
            (token_loss * mask).sum(dim=1)
            / mask.sum(dim=1).clamp_min(1)
        )

        weights = weights.to(
            device=per_example_loss.device,
            dtype=per_example_loss.dtype,
        )

        weighted_loss = (
            (per_example_loss * weights).sum()
            / weights.sum().clamp_min(1e-6)
        )

        return (
            (weighted_loss, outputs)
            if return_outputs
            else weighted_loss
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "QLoRA fine-tuning for "
            "Qwen2.5-Coder-7B-Instruct using "
            "Unsloth + TRL."
        )
    )

    parser.add_argument(
        "--model",
        default="Qwen/Qwen2.5-Coder-7B-Instruct",
    )

    parser.add_argument(
        "--train",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--validation",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--max-seq-length",
        type=int,
        default=4096,
    )

    parser.add_argument(
        "--epochs",
        type=float,
        default=2,
    )

    parser.add_argument(
        "--max-steps",
        type=int,
        default=-1,
        help=(
            "Positive value overrides epochs; "
            "useful for smoke tests."
        ),
    )

    parser.add_argument(
        "--learning-rate",
        type=float,
        default=1e-4,
    )

    parser.add_argument(
        "--rank",
        type=int,
        default=32,
    )

    parser.add_argument(
        "--gradient-accumulation",
        type=int,
        default=8,
    )

    parser.add_argument(
        "--per-device-batch-size",
        type=int,
        default=2,
    )

    parser.add_argument(
        "--per-device-eval-batch-size",
        type=int,
        default=2,
    )

    args = parser.parse_args()

    args.output.mkdir(
        parents=True,
        exist_ok=True,
    )

    # =========================================================
    # GPU CHECK
    # =========================================================

    try:
        import torch

        if not torch.cuda.is_available():
            raise RuntimeError(
                "CUDA is not available."
            )

        free, total = torch.cuda.mem_get_info(0)

        print(
            f"GPU: {torch.cuda.get_device_name(0)}"
        )

        print(
            f"VRAM: "
            f"{total / 1024**3:.1f} GB total, "
            f"{free / 1024**3:.1f} GB free"
        )

        print(
            f"BF16 supported: "
            f"{torch.cuda.is_bf16_supported()}"
        )

        effective_batch = (
            args.per_device_batch_size
            * args.gradient_accumulation
        )

        print(
            f"Config: "
            f"rank={args.rank}, "
            f"per_device_batch={args.per_device_batch_size}, "
            f"gradient_accumulation={args.gradient_accumulation}, "
            f"effective_batch={effective_batch}, "
            f"seq_len={args.max_seq_length}"
        )

        if total < 40 * 1024**3:
            print(
                "WARNING: GPU has less than 40GB VRAM."
            )
            print(
                "Consider --per-device-batch-size 1 "
                "and --rank 16."
            )

    except Exception as exc:
        print(
            f"GPU check failed: {exc}"
        )
        raise

    # =========================================================
    # MODEL
    # =========================================================

    print()
    print("Loading model...")

    model, tokenizer = (
        FastLanguageModel.from_pretrained(
            model_name=args.model,
            max_seq_length=args.max_seq_length,
            load_in_4bit=True,
            dtype=None,
        )
    )

    print("Model loaded.")

    # =========================================================
    # LoRA
    # =========================================================

    print()
    print("Applying LoRA...")

    model = FastLanguageModel.get_peft_model(
        model,
        r=args.rank,
        lora_alpha=args.rank * 2,
        lora_dropout=0.05,
        bias="none",
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )

    print("LoRA applied.")

    # =========================================================
    # DATASET
    # =========================================================

    print()
    print("Loading dataset...")

    dataset = load_dataset(
        "json",
        data_files={
            "train": str(args.train),
            "validation": str(args.validation),
        },
    )

    print(
        "Original train columns:",
        dataset["train"].column_names,
    )

    print(
        "Original validation columns:",
        dataset["validation"].column_names,
    )

    # =========================================================
    # CHAT TEMPLATE
    # =========================================================

    def format_example(example):
        return tokenizer.apply_chat_template(
            example["messages"],
            tokenize=False,
            add_generation_prompt=False,
        )

    # =========================================================
    # CONFIDENCE WEIGHT
    # =========================================================

    def enrich(example):
        weight = 1.0

        try:
            target = json.loads(
                example["messages"][-1]["content"]
            )

            if target.get("semantic_labels"):
                values = [
                    float(
                        item.get(
                            "confidence",
                            1.0,
                        )
                    )
                    for item in target["semantic_labels"]
                ]

                if values:
                    weight = (
                        sum(values)
                        / len(values)
                    )

            elif "confidence" in target:
                weight = float(
                    target["confidence"]
                )

        except (
            KeyError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ):
            weight = 1.0

        weight = max(
            0.0,
            min(1.0, weight),
        )

        return {
            "text": format_example(example),
            "sample_weight": weight,
        }

    # =========================================================
    # REMOVE ALL RAW JSON COLUMNS
    # =========================================================

    original_columns = (
        dataset["train"].column_names
    )

    dataset = dataset.map(
        enrich,
        remove_columns=original_columns,
        desc="Formatting dataset",
    )

    print()
    print(
        "Processed train columns:",
        dataset["train"].column_names,
    )

    print(
        "Processed validation columns:",
        dataset["validation"].column_names,
    )

    # =========================================================
    # DATASET VALIDATION
    # =========================================================

    expected_columns = {
        "text",
        "sample_weight",
    }

    for split in (
        "train",
        "validation",
    ):
        actual_columns = set(
            dataset[split].column_names
        )

        if actual_columns != expected_columns:
            raise RuntimeError(
                f"{split} has unexpected columns: "
                f"{dataset[split].column_names}. "
                f"Expected: "
                f"{sorted(expected_columns)}"
            )

    print()
    print(
        "Dataset structure check passed."
    )

    first_example = dataset["train"][0]

    print(
        "First example keys:",
        list(first_example.keys()),
    )

    print(
        "First sample weight:",
        first_example["sample_weight"],
    )

    # =========================================================
    # SEQUENCE LENGTH CHECK
    # =========================================================

    print()
    print("Checking sequence lengths...")

    oversized = []

    for split in (
        "train",
        "validation",
    ):
        for index, text in enumerate(
            dataset[split]["text"]
        ):
            token_ids = tokenizer(
                text,
                add_special_tokens=False,
            )["input_ids"]

            length = len(token_ids)

            if length > args.max_seq_length:
                oversized.append(
                    (
                        split,
                        index,
                        length,
                    )
                )

    if oversized:
        report_path = (
            args.output
            / "oversized_examples.json"
        )

        report_path.write_text(
            json.dumps(
                oversized,
                indent=2,
            ),
            encoding="utf-8",
        )

        raise RuntimeError(
            f"{len(oversized)} examples exceed "
            f"{args.max_seq_length} tokens. "
            f"No truncation was performed. "
            f"See: {report_path}"
        )

    print(
        "Sequence length check passed."
    )

    # =========================================================
    # PRECISION
    # =========================================================

    import torch

    bf16 = bool(
        torch.cuda.is_available()
        and torch.cuda.is_bf16_supported()
    )

    if bf16:
        print(
            "Training precision: BF16"
        )
    else:
        print(
            "Training precision: FP16"
        )

    # =========================================================
    # SFT CONFIG
    # =========================================================

    config_kwargs = dict(
        output_dir=str(args.output),

        dataset_text_field="text",

        # CRITICAL:
        # Trainer will remove raw `text` before the
        # data collator.
        #
        # sample_weight is preserved by
        # _set_signature_columns_if_needed().
        remove_unused_columns=True,

        num_train_epochs=args.epochs,

        max_steps=args.max_steps,

        per_device_train_batch_size=(
            args.per_device_batch_size
        ),

        per_device_eval_batch_size=(
            args.per_device_eval_batch_size
        ),

        gradient_accumulation_steps=(
            args.gradient_accumulation
        ),

        learning_rate=args.learning_rate,

        warmup_ratio=0.03,

        logging_steps=(
            1
            if args.max_steps > 0
            else 5
        ),

        eval_strategy=(
            "steps"
            if args.max_steps > 0
            else "epoch"
        ),

        eval_steps=(
            1
            if args.max_steps > 0
            else None
        ),

        save_strategy=(
            "steps"
            if args.max_steps > 0
            else "epoch"
        ),

        save_steps=(
            args.max_steps
            if args.max_steps > 0
            else 500
        ),

        save_total_limit=1,

        packing=False,

        gradient_checkpointing=True,

        fp16=not bf16,

        bf16=bf16,

        optim="adamw_8bit",

        report_to="none",
    )

    # TRL compatibility:
    # TRL 0.15.x normally exposes max_length.
    sft_parameters = inspect.signature(
        SFTConfig
    ).parameters

    if "max_length" in sft_parameters:
        config_kwargs["max_length"] = (
            args.max_seq_length
        )

    elif "max_seq_length" in sft_parameters:
        config_kwargs["max_seq_length"] = (
            args.max_seq_length
        )

    else:
        raise RuntimeError(
            "Could not find max_length/max_seq_length "
            "in SFTConfig."
        )

    training_args = SFTConfig(
        **config_kwargs
    )

    # =========================================================
    # TRAINER
    # =========================================================

    trainer_kwargs = dict(
        model=model,

        train_dataset=dataset["train"],

        eval_dataset=dataset["validation"],

        args=training_args,
    )

    trainer_parameters = inspect.signature(
        SFTTrainer
    ).parameters

    if "processing_class" in trainer_parameters:
        trainer_kwargs["processing_class"] = (
            tokenizer
        )
    elif "tokenizer" in trainer_parameters:
        trainer_kwargs["tokenizer"] = (
            tokenizer
        )

    print()
    print("Creating trainer...")

    trainer = ConfidenceWeightedSFTTrainer(
        **trainer_kwargs
    )

    # =========================================================
    # RESPONSE-ONLY TRAINING
    # =========================================================

    print()
    print(
        "Applying response-only loss masking..."
    )

    trainer = train_on_responses_only(
        trainer,
        instruction_part="<|im_start|>user\n",
        response_part="<|im_start|>assistant\n",
    )

    # =========================================================
    # COLLATOR / BATCH TEST
    # =========================================================

    print()
    print(
        "Testing first training batch..."
    )

    train_loader = (
        trainer.get_train_dataloader()
    )

    first_batch = next(
        iter(train_loader)
    )

    print(
        "Batch keys:",
        list(first_batch.keys()),
    )

    for key, value in first_batch.items():
        print(
            f"  {key}: "
            f"shape={getattr(value, 'shape', None)} "
            f"dtype={getattr(value, 'dtype', None)}"
        )

    forbidden = {
        "text",
        "messages",
        "metadata",
    }

    leaked = forbidden.intersection(
        first_batch.keys()
    )

    if leaked:
        raise RuntimeError(
            "Raw fields reached the model batch: "
            f"{sorted(leaked)}"
        )

    required = {
        "input_ids",
        "attention_mask",
        "labels",
        "sample_weight",
    }

    missing = required.difference(
        first_batch.keys()
    )

    if missing:
        raise RuntimeError(
            "Required batch fields are missing: "
            f"{sorted(missing)}"
        )

    print()
    print(
        "First batch validation passed."
    )

    # =========================================================
    # TRAIN
    # =========================================================

    print()
    print(
        "Starting training..."
    )

    trainer.train()

    # =========================================================
    # SAVE
    # =========================================================

    print()
    print(
        "Saving adapter..."
    )

    adapter_dir = (
        args.output / "adapter"
    )

    trainer.save_model(
        str(adapter_dir)
    )

    tokenizer.save_pretrained(
        str(adapter_dir)
    )

    config_path = (
        args.output / "config.json"
    )

    config_path.write_text(
        json.dumps(
            vars(args),
            default=str,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "Training complete."
    )

    print(
        f"Adapter: {adapter_dir}"
    )

    print(
        f"Config:  {config_path}"
    )


if __name__ == "__main__":
    main()
