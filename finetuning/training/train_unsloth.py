#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
import inspect
from pathlib import Path
from datasets import load_dataset
from unsloth import FastLanguageModel
from unsloth.chat_templates import train_on_responses_only
from trl import SFTTrainer, SFTConfig

class ConfidenceWeightedSFTTrainer(SFTTrainer):
    """Apply per-example confidence to the response-token loss."""
    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        weights = inputs.pop("sample_weight", None)
        outputs = model(**inputs)
        if weights is None:
            return (outputs.loss, outputs) if return_outputs else outputs.loss
        labels = inputs["labels"]
        logits = outputs.logits[..., :-1, :].contiguous()
        shifted = labels[..., 1:].contiguous()
        import torch
        loss = torch.nn.functional.cross_entropy(
            logits.view(-1, logits.size(-1)), shifted.view(-1), reduction="none", ignore_index=-100
        ).view(shifted.size())
        mask = shifted.ne(-100)
        per_example = (loss * mask).sum(dim=1) / mask.sum(dim=1).clamp_min(1)
        weighted = (per_example * weights.to(per_example.dtype)).sum() / weights.sum().clamp_min(1e-6)
        return (weighted, outputs) if return_outputs else weighted

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--model",default="Qwen/Qwen2.5-14B-Instruct"); p.add_argument("--train",type=Path,required=True); p.add_argument("--validation",type=Path,required=True); p.add_argument("--output",type=Path,required=True); p.add_argument("--max-seq-length",type=int,default=4096); p.add_argument("--epochs",type=float,default=2); p.add_argument("--max-steps",type=int,default=-1,help="Positive value overrides epochs; intended for smoke tests"); p.add_argument("--learning-rate",type=float,default=1e-4); p.add_argument("--rank",type=int,default=16); p.add_argument("--gradient-accumulation",type=int,default=16)
    a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
    model,tok=FastLanguageModel.from_pretrained(model_name=a.model,max_seq_length=a.max_seq_length,load_in_4bit=True,dtype=None)
    model=FastLanguageModel.get_peft_model(model,r=a.rank,lora_alpha=a.rank*2,lora_dropout=0.05,bias="none",target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],use_gradient_checkpointing="unsloth",random_state=42)
    ds=load_dataset("json",data_files={"train":str(a.train),"validation":str(a.validation)})
    def fmt(x): return tok.apply_chat_template(x["messages"],tokenize=False,add_generation_prompt=False)
    def enrich(x):
        weight = 1.0
        try:
            target = json.loads(x["messages"][-1]["content"])
            if target.get("semantic_labels"):
                vals = [float(v.get("confidence", 1.0)) for v in target["semantic_labels"]]
                weight = sum(vals) / len(vals)
            elif "confidence" in target:
                weight = float(target["confidence"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            pass
        return {"text": fmt(x), "sample_weight": max(0.0, min(1.0, weight))}
    ds=ds.map(enrich)
    oversized=[]
    for split in ("train","validation"):
        for i,text in enumerate(ds[split]["text"]):
            size=len(tok(text,add_special_tokens=False)["input_ids"])
            if size>a.max_seq_length: oversized.append((split,i,size))
    if oversized:
        report=a.output/"oversized_examples.json"; report.write_text(json.dumps(oversized,indent=2),encoding="utf-8")
        raise RuntimeError(f"{len(oversized)} examples exceed {a.max_seq_length} tokens; no truncation was performed. See {report}")
    import torch
    bf16 = bool(torch.cuda.is_available() and torch.cuda.is_bf16_supported())
    config_kwargs=dict(output_dir=str(a.output),dataset_text_field="text",remove_unused_columns=False,num_train_epochs=a.epochs,max_steps=a.max_steps,per_device_train_batch_size=1,per_device_eval_batch_size=1,gradient_accumulation_steps=a.gradient_accumulation,learning_rate=a.learning_rate,warmup_ratio=0.03,logging_steps=1 if a.max_steps > 0 else 5,eval_strategy="steps" if a.max_steps > 0 else "epoch",eval_steps=1 if a.max_steps > 0 else None,save_strategy="steps" if a.max_steps > 0 else "epoch",save_steps=a.max_steps if a.max_steps > 0 else 500,save_total_limit=1,packing=False,gradient_checkpointing=True,fp16=not bf16,bf16=bf16,optim="adamw_8bit",report_to="none")
    config_kwargs["max_length" if "max_length" in inspect.signature(SFTConfig).parameters else "max_seq_length"] = a.max_seq_length
    args=SFTConfig(**config_kwargs)
    trainer_kwargs=dict(model=model,train_dataset=ds["train"],eval_dataset=ds["validation"],args=args)
    trainer_kwargs["processing_class" if "processing_class" in inspect.signature(SFTTrainer).parameters else "tokenizer"] = tok
    trainer=ConfidenceWeightedSFTTrainer(**trainer_kwargs)
    trainer=train_on_responses_only(trainer,instruction_part="<|im_start|>user\n",response_part="<|im_start|>assistant\n")
    trainer.train(); trainer.save_model(str(a.output/"adapter")); tok.save_pretrained(str(a.output/"adapter")); (a.output/"config.json").write_text(json.dumps(vars(a),default=str,indent=2),encoding="utf-8")
if __name__ == "__main__": main()
