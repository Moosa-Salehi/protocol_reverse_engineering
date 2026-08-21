param([string]$Model = "D:\Models\Qwen2.5-Coder-7B-ProtocolRE-Q4_K_M.gguf", [string]$PromptFile)
$ErrorActionPreference="Stop"
if (-not (Test-Path $Model)) { throw "GGUF not found: $Model" }
if ($PromptFile) { Get-Content -Raw $PromptFile | & llama-cli.exe -m $Model -c 4096 --temp 0.1 }
else { & llama-cli.exe -m $Model -c 4096 --temp 0.1 -p "Return JSON only." }
