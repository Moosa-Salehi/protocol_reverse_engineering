# Qwen2.5-Coder Protocol-RE Fine-Tuning

This toolkit trains a semantic-labeling LoRA adapter for the repository's existing LLM stage. It uses Wireshark dissector field offsets as conservative supervision. Modbus and GOOSE are configured as holdouts and are not included in training.

## Hardware limits

An RTX 3050 6 GB can run the default QLoRA configuration, but 1024 tokens is near the practical limit. Close GPU applications first. If CUDA runs out of memory, retry with `-MaxLength 768`, then `512`. Merging the adapter needs roughly 16 GB system RAM and may require a Windows page file of at least 24 GB.

The repository's full semantic prompt is longer than this GPU can train in full. The trainer renders the exact inference prompt and then left-crops tokenized examples so the evidence tail and complete assistant answer remain in the loss window. This is a hardware compromise; a 12 GB or larger GPU would permit materially better context coverage.

## Prerequisites

- Windows 10/11, current NVIDIA driver
- Python 3.11 x64
- Wireshark with TShark installed and `tshark.exe` on `PATH`
- Git and Git LFS
- At least 35 GB free disk space for the Hugging Face cache, checkpoints, and merged model

## Run

From PowerShell in the repository root:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\finetuning\setup_windows.ps1
.\finetuning\build_dataset_windows.ps1
.\finetuning\train_windows.ps1 -MaxLength 1024 -Epochs 2
```

The first training run downloads `Qwen/Qwen2.5-Coder-7B-Instruct`. Set `HF_HOME` before training to move the cache to a drive with enough space.

The dataset builder initially selects PCAPs whose path contains a protocol alias from `protocols.json`. Use `-ScanAllFiles` only when the directory/file names do not identify protocols; it makes TShark test every configured dissector against every capture and can be very slow.

Inspect `finetuning/data/raw_train.unmapped.json` after generation. It lists dissector fields that were deliberately excluded because they did not map safely to the project's semantic-role taxonomy.

## Merge and convert to GGUF

The LoRA adapter can be served directly with a Transformers/PEFT backend. To merge it:

```powershell
.\finetuning\.venv\Scripts\python.exe .\finetuning\merge_adapter.py `
  --adapter .\finetuning\output\qwen25-coder-7b-protocol-re\adapter `
  --output D:\Models\Qwen2.5-Coder-7B-ProtocolRE-merged
```

GGUF conversion requires a separate `llama.cpp` checkout:

```powershell
python D:\path\to\llama.cpp\convert_hf_to_gguf.py `
  D:\Models\Qwen2.5-Coder-7B-ProtocolRE-merged `
  --outfile D:\Models\Qwen2.5-Coder-7B-ProtocolRE-f16.gguf `
  --outtype f16

D:\path\to\llama.cpp\build\bin\Release\llama-quantize.exe `
  D:\Models\Qwen2.5-Coder-7B-ProtocolRE-f16.gguf `
  D:\Models\Qwen2.5-Coder-7B-ProtocolRE-Q4_K_M.gguf Q4_K_M
```

Do not merge the adapter into the existing Josiefied GGUF. The adapter was trained against the official Qwen base, so its weights are only compatible with that base.
