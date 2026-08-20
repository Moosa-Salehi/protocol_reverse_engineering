param(
    [string]$Model = "Qwen/Qwen2.5-Coder-7B-Instruct",
    [int]$MaxLength = 1024,
    [double]$Epochs = 2.0
)
$ErrorActionPreference = "Stop"
$env:PYTORCH_CUDA_ALLOC_CONF = "expandable_segments:True"
$Python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
& $Python "$PSScriptRoot\train_qlora.py" `
    --model $Model `
    --train "$PSScriptRoot\data\train.jsonl" `
    --validation "$PSScriptRoot\data\validation.jsonl" `
    --output "$PSScriptRoot\output\qwen25-coder-7b-protocol-re" `
    --max-length $MaxLength `
    --epochs $Epochs

