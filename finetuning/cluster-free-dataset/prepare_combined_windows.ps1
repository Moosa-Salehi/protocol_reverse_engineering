param(
  [string]$Python = "python",
  [string]$DataRoot = "$PSScriptRoot\data",
  [string]$OutputRoot = "$PSScriptRoot\data\split",
  [string]$Tokenizer = "Qwen/Qwen2.5-Coder-7B-Instruct",
  [string]$VmBundleRoot = "$PSScriptRoot\vm_bundle",
  [switch]$IncludeHoldout,
  [double]$ValidationFraction = 0.1,
  [double]$TestFraction = 0.1,
  [int]$Seed = 42
)
$ErrorActionPreference = "Stop"
$combinedDir = Join-Path $DataRoot "combined"
$raw = Join-Path $combinedDir "raw.jsonl"
New-Item -ItemType Directory -Force -Path $combinedDir | Out-Null
$excluded = @("combined.jsonl", "raw.jsonl", "dataset_summary.json")
$curatedFiles = @(Get-ChildItem -Path $DataRoot -Filter "curated_*.jsonl" -File | Sort-Object Name)
if ($curatedFiles.Count -gt 0) {
  $files = $curatedFiles
} else {
  $files = Get-ChildItem -Path $DataRoot -Filter "*.jsonl" -File | Sort-Object Name | Where-Object {
    $_.Name -notin $excluded
  }
}
if ($files.Count -eq 0) { throw "No protocol JSONL files found under $DataRoot" }
Set-Content -Path $raw -Value $null
foreach ($file in $files) { Get-Content -LiteralPath $file.FullName | Add-Content -LiteralPath $raw }
Write-Host "Combined $($files.Count) protocol files into $raw"

$validator = Join-Path $PSScriptRoot "validate_dataset.py"
& $Python $validator $raw
if ($LASTEXITCODE -ne 0) { throw "Dataset validation failed" }

$prepare = Join-Path (Split-Path -Parent $PSScriptRoot) "dataset-generation\prepare_dataset.py"
& $Python $prepare $raw $OutputRoot --validation-fraction $ValidationFraction --test-fraction $TestFraction --seed $Seed
if ($LASTEXITCODE -ne 0) { throw "Dataset split failed" }

$summary = Join-Path (Split-Path -Parent $PSScriptRoot) "dataset-generation\summarize_dataset.py"
$summaryOut = Join-Path $DataRoot "combined\dataset_summary.json"
& $Python $summary (Get-Item $raw).FullName --tokenizer $Tokenizer --output $summaryOut
if ($LASTEXITCODE -ne 0) { throw "Dataset summary failed" }
Write-Host "Prepared split at $OutputRoot and summary at $summaryOut"

$finetuningRoot = Split-Path -Parent $PSScriptRoot
$vmFinetuning = Join-Path $VmBundleRoot "finetuning"
$vmData = Join-Path $vmFinetuning "data"
$vmSplit = Join-Path $vmData "split"
Remove-Item -Recurse -Force $VmBundleRoot -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $vmData, $vmSplit | Out-Null

Copy-Item $raw (Join-Path $vmData "curated.jsonl") -Force
Copy-Item $summaryOut (Join-Path $vmData "dataset_summary.json") -Force
Copy-Item (Join-Path $OutputRoot "train.jsonl") $vmSplit -Force
Copy-Item (Join-Path $OutputRoot "validation.jsonl") $vmSplit -Force
Copy-Item (Join-Path $OutputRoot "test.jsonl") $vmSplit -Force
Copy-Item (Join-Path $OutputRoot "summary.json") $vmSplit -Force
Copy-Item (Join-Path $DataRoot "curated_1000_summary.json") $vmData -Force -ErrorAction SilentlyContinue
Copy-Item (Join-Path $DataRoot "curated_1000_semantic_summary.json") $vmData -Force -ErrorAction SilentlyContinue

foreach ($directory in @("dataset-generation", "inference", "training")) {
  Copy-Item (Join-Path $finetuningRoot $directory) $vmFinetuning -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $vmFinetuning "cluster-free-dataset") | Out-Null
Copy-Item $validator (Join-Path $vmFinetuning "cluster-free-dataset\validate_dataset.py") -Force

Write-Host "VM bundle ready at $vmFinetuning"
Write-Host "Copy this finetuning directory to the Ubuntu VM."
