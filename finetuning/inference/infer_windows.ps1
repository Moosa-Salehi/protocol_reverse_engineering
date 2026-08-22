param([string]$Model = "D:\Models\Qwen2.5-14B-ProtocolRE-Q4_K_M.gguf", [string]$PromptFile, [int]$Seed=42, [int]$MaxTokens=512)
$ErrorActionPreference="Stop"
if (-not (Test-Path $Model)) { throw "GGUF not found: $Model" }
if ($PromptFile) {
  $Prompt=Get-Content -Raw $PromptFile
  if ($Prompt -notmatch '### TASK:' -or $Prompt -notmatch 'Evidence Bundle') { throw "Prompt must contain the training TASK and Evidence Bundle sections" }
  & llama-cli.exe -m $Model -c 4096 -n $MaxTokens --temp 0 --top-k 1 --top-p 1 --seed $Seed --no-display-prompt -p $Prompt
}
else { & llama-cli.exe -m $Model -c 4096 -n $MaxTokens --temp 0 --top-k 1 --top-p 1 --seed $Seed --no-display-prompt -p "Return JSON only." }
