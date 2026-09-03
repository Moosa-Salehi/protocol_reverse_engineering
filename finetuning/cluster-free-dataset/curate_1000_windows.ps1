param(
  [string]$Python = "python",
  [string]$DataRoot = "$PSScriptRoot\data",
  [string]$Output = "$PSScriptRoot\data\curated_1000.jsonl",
  [string]$Tokenizer = "Qwen/Qwen2.5-Coder-7B-Instruct",
  [int]$Count = 1000,
  [int]$MaxTokens = 4096,
  [int]$MaxBoundaries = 32,
  [int]$PreferredPayloadLength = 50
)
$ErrorActionPreference = "Stop"
$script = Join-Path $PSScriptRoot "curate_dataset.py"
& $Python $script $DataRoot $Output --tokenizer $Tokenizer --count $Count --max-tokens $MaxTokens --max-boundaries $MaxBoundaries --preferred-payload-length $PreferredPayloadLength
if ($LASTEXITCODE -ne 0) { throw "Dataset curation failed" }
