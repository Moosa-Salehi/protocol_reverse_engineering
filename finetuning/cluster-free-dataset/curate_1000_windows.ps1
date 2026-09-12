param(
  [string]$Python = "python",
  [string]$DataRoot = "$PSScriptRoot\data",
  [string]$Output = "$PSScriptRoot\data\curated_1000.jsonl",
  [string]$Tokenizer = "Qwen/Qwen2.5-Coder-7B-Instruct",
  [int]$Count = 1000,
  [int]$MaxTokens = 4096,
  [int]$MaxBoundaries = 32,
  [int]$PreferredPayloadLength = 50,
  [switch]$IncludeHoldout,
  [int]$ProtocolCap = 100,
  [int]$MinProtocolRecords = 10
)
$ErrorActionPreference = "Stop"
$script = Join-Path $PSScriptRoot "curate_dataset.py"
$holdoutArg = @(); if ($IncludeHoldout) { $holdoutArg = @("--include-holdout") }
& $Python $script $DataRoot $Output --tokenizer $Tokenizer --count $Count --max-tokens $MaxTokens --max-boundaries $MaxBoundaries --preferred-payload-length $PreferredPayloadLength --protocol-cap $ProtocolCap --min-protocol-records $MinProtocolRecords @holdoutArg
if ($LASTEXITCODE -ne 0) { throw "Dataset curation failed" }
