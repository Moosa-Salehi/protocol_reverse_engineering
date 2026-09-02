param(
  [Parameter(Mandatory=$true)][string]$MessagesRoot,
  [Parameter(Mandatory=$true)][string]$AnnotationsRoot,
  [Parameter(Mandatory=$true)][string]$OutputRoot,
  [string]$Python = "python",
  [int]$BatchSize = 8,
  [string[]]$Protocols = @()
)
$ErrorActionPreference = "Stop"
$Builder = Join-Path $PSScriptRoot "build_payload_dataset.py"
New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null
if ($Protocols.Count -eq 0) {
  $files = Get-ChildItem -Path $MessagesRoot -Recurse -Filter "01_messages.jsonl" -File
  $Protocols = @($files | ForEach-Object { $_.Directory.Parent.Name } | Sort-Object -Unique)
}
foreach ($protocol in $Protocols) {
  $messages = Join-Path $MessagesRoot "$protocol\01_messages.jsonl"
  if (!(Test-Path $messages)) { $messages = Join-Path $MessagesRoot "$protocol\data\01_messages.jsonl" }
  $annotations = Join-Path $AnnotationsRoot "$protocol.jsonl"
  if (!(Test-Path $annotations)) { $annotations = Join-Path $AnnotationsRoot "$protocol.json" }
  if (!(Test-Path $messages)) { Write-Warning "Skipping $protocol: messages not found"; continue }
  if (!(Test-Path $annotations)) { Write-Warning "Skipping $protocol: annotations not found"; continue }
  $out = Join-Path $OutputRoot "$protocol.jsonl"
  & $Python $Builder $messages $annotations $out --protocol $protocol --batch-size $BatchSize --tasks boundary_refinement semantic_labeling
  if ($LASTEXITCODE -ne 0) { throw "Builder failed for $protocol" }
}
Write-Host "Cluster-free dataset written to $OutputRoot"
