param(
  [string]$Python = "py",
  [string]$Tokenizer = "Qwen/Qwen2.5-14B-Instruct",
  [double]$ValidationFraction = 0.1,
  [int]$Seed = 42
)

$ErrorActionPreference = "Stop"
$FinetuningRoot = Split-Path -Parent $PSScriptRoot
$WindowsData = Join-Path $FinetuningRoot "windows_data"
$CandidateRoot = Join-Path $WindowsData "candidate_jsonl"
$ApprovedRoot = Join-Path $WindowsData "approved"
$VmBundle = Join-Path $WindowsData "vm_bundle"
$VmFinetuning = Join-Path $VmBundle "finetuning"
$DataDir = Join-Path $VmFinetuning "data"

function Invoke-Python {
  param([string[]]$Arguments)
  & $Python @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "Python command failed: $Python $($Arguments -join ' ')"
  }
}

function Join-JsonlFiles {
  param([System.IO.FileInfo[]]$Files, [string]$Output)
  if (-not $Files -or $Files.Count -eq 0) {
    throw "No approved JSONL files were found for $Output"
  }
  $writer = [System.IO.StreamWriter]::new($Output, $false, [System.Text.UTF8Encoding]::new($false))
  try {
    foreach ($file in $Files) {
      foreach ($line in [System.IO.File]::ReadLines($file.FullName)) {
        if (-not [string]::IsNullOrWhiteSpace($line)) { $writer.WriteLine($line) }
      }
    }
  } finally {
    $writer.Dispose()
  }
}

Remove-Item -Recurse -Force $ApprovedRoot -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force $VmBundle -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path (Join-Path $ApprovedRoot "train"), (Join-Path $ApprovedRoot "holdout"), $DataDir | Out-Null

foreach ($setName in @("train", "holdout")) {
  $candidateDir = Join-Path $CandidateRoot $setName
    if (-not (Test-Path $candidateDir)) { continue }
    foreach ($candidate in Get-ChildItem $candidateDir -Filter *.jsonl -File | Sort-Object Name) {
      if ($candidate.Length -eq 0) {
        Write-Host "Skipping empty candidate file $($candidate.FullName)"
        continue
      }
      $approved = Join-Path (Join-Path $ApprovedRoot $setName) $candidate.Name
      Invoke-Python @((Join-Path $PSScriptRoot "promote_reviewed.py"), $candidate.FullName, $approved)
  }
}

$trainFiles = @(Get-ChildItem (Join-Path $ApprovedRoot "train") -Filter *.jsonl -File | Sort-Object Name)
$holdoutFiles = @(Get-ChildItem (Join-Path $ApprovedRoot "holdout") -Filter *.jsonl -File | Sort-Object Name)
$raw = Join-Path $DataDir "raw.jsonl"
$holdout = Join-Path $DataDir "holdout.jsonl"
Join-JsonlFiles $trainFiles $raw
Join-JsonlFiles $holdoutFiles $holdout

$auditArgs = @((Join-Path $PSScriptRoot "audit_leakage.py"), "--train", $raw, "--holdout", $holdout)
$samplingReport = Join-Path $WindowsData "sampled_pcaps\sampling_report.json"
if (Test-Path $samplingReport) {
  Copy-Item $samplingReport (Join-Path $DataDir "sampling_report.json")
}
Invoke-Python $auditArgs
Invoke-Python @((Join-Path $PSScriptRoot "summarize_dataset.py"), $raw, "--tokenizer", $Tokenizer, "--output", (Join-Path $DataDir "dataset_summary.json"))
Invoke-Python @((Join-Path $PSScriptRoot "prepare_dataset.py"), $raw, (Join-Path $DataDir "split"), "--validation-fraction", "$ValidationFraction", "--seed", "$Seed")

foreach ($directory in @("dataset-generation", "inference", "training")) {
  Copy-Item (Join-Path $FinetuningRoot $directory) $VmFinetuning -Recurse -Force
}

Write-Host "Complete VM bundle is ready at $VmFinetuning"
Write-Host "Copy that single finetuning directory to the Ubuntu VM."
