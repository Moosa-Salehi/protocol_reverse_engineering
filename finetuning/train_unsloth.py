#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from datasets import load_dataset
from unsloth import FastLanguageModel
from unsloth.chat_templates import train_on_responses_only
from trl import SFTTrainer, SFTConfig

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--model",default="Qwen/Qwen2.5-Coder-7B-Instruct"); p.add_argument("--train",type=Path,required=True); p.add_argument("--validation",type=Path,required=True); p.add_argument("--output",type=Path,required=True); p.add_argument("--max-seq-length",type=int,default=4096); p.add_argument("--epochs",type=float,default=2); p.add_argument("--learning-rate",type=float,default=1e-4); p.add_argument("--rank",type=int,default=16); p.add_argument("--gradient-accumulation",type=int,default=8)
    a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
    model,tok=FastLanguageModel.from_pretrained(model_name=a.model,max_seq_length=a.max_seq_length,load_in_4bit=True,dtype=None)
    model=FastLanguageModel.get_peft_model(model,r=a.rank,lora_alpha=a.rank*2,lora_dropout=0.05,bias="none",target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],use_gradient_checkpointing="unsloth",random_state=42)
    ds=load_dataset("json",data_files={"train":str(a.train),"validation":str(a.validation)})
    def fmt(x): return tok.apply_chat_template(x["messages"],tokenize=False,add_generation_prompt=False)
    ds=ds.map(lambda x:{"text":fmt(x)})
    oversized=[]
    for split in ("train","validation"):
        for i,text in enumerate(ds[split]["text"]):
            size=len(tok(text,add_special_tokens=False)["input_ids"])
            if size>a.max_seq_length: oversized.append((split,i,size))
    if oversized:
        report=a.output/"oversized_examples.json"; report.write_text(json.dumps(oversized,indent=2),encoding="utf-8")
        raise RuntimeError(f"{len(oversized)} examples exceed {a.max_seq_length} tokens; no truncation was performed. See {report}")
    args=SFTConfig(output_dir=str(a.output),dataset_text_field="text",max_seq_length=a.max_seq_length,num_train_epochs=a.epochs,per_device_train_batch_size=1,per_device_eval_batch_size=1,gradient_accumulation_steps=a.gradient_accumulation,learning_rate=a.learning_rate,warmup_ratio=0.03,logging_steps=5,eval_strategy="epoch",save_strategy="epoch",save_total_limit=1,packing=False,gradient_checkpointing=True,fp16=False,bf16=True,optim="adamw_8bit",report_to="none")
    trainer=SFTTrainer(model=model,tokenizer=tok,train_dataset=ds["train"],eval_dataset=ds["validation"],args=args)
    trainer=train_on_responses_only(trainer,instruction_part="<|im_start|>user\n",response_part="<|im_start|>assistant\n")
    trainer.train(); trainer.save_model(str(a.output/"adapter")); tok.save_pretrained(str(a.output/"adapter")); (a.output/"config.json").write_text(json.dumps(vars(a),default=str,indent=2),encoding="utf-8")
if __name__ == "__main__": main()
