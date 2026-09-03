param(
  [Parameter(Mandatory=$true)][string]$MessagesRoot,
  [Parameter(Mandatory=$true)][string]$AnnotationsRoot,
  [Parameter(Mandatory=$true)][string]$OutputRoot,
  [string]$PcapRoot = "",
  [string]$Python = "python",
  [int]$BatchSize = 8,
  [string]$Tshark = "tshark",
  [string[]]$Protocols = @(),
  [ValidateSet("boundary_refinement", "semantic_labeling")][string[]]$Tasks = @("boundary_refinement", "semantic_labeling")
)
$ErrorActionPreference = "Stop"
$Builder = Join-Path $PSScriptRoot "build_payload_dataset.py"
if ([string]::IsNullOrWhiteSpace($PcapRoot)) { $PcapRoot = Join-Path (Split-Path -Parent $MessagesRoot) "sampled_pcaps" }
$ConfigPath = Join-Path (Split-Path -Parent $PSScriptRoot) "dataset-generation\protocols.json"
$Config = Get-Content -Raw $ConfigPath | ConvertFrom-Json
New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null
if ($Protocols.Count -eq 0) {
  $files = Get-ChildItem -Path $MessagesRoot -Recurse -Filter "01_messages.jsonl" -File
  $Protocols = @($files | ForEach-Object { $_.Directory.Parent.Name } | Sort-Object -Unique)
}
foreach ($protocol in $Protocols) {
  $messages = Join-Path $MessagesRoot "$protocol\01_messages.jsonl"
  if (!(Test-Path $messages)) { $messages = Join-Path $MessagesRoot "$protocol\data\01_messages.jsonl" }
  $annotations = Join-Path $AnnotationsRoot "$protocol.jsonl"
  # Always use JSONL for generated annotations. A legacy/empty .json file must
  # not shadow the TShark output.
  if (!(Test-Path $messages)) { Write-Warning "Skipping $protocol : messages not found"; continue }
  if (!(Test-Path $annotations) -or ((Get-Item $annotations).Length -eq 0)) {
    New-Item -ItemType Directory -Force -Path $AnnotationsRoot | Out-Null
    $entry = $Config.train.PSObject.Properties[$protocol]
    if ($null -eq $entry) { $entry = $Config.holdout.PSObject.Properties[$protocol] }
    if ($null -eq $entry) { throw "No TShark filter configured for $protocol" }
    & $Python (Join-Path $PSScriptRoot "generate_tshark_annotations.py") $messages $PcapRoot $annotations --filter $entry.Value.filter --tshark $Tshark
    if ($LASTEXITCODE -ne 0) { throw "TShark annotation generation failed for $protocol" }
    if (!(Test-Path $annotations) -or (Get-Item $annotations).Length -eq 0) { throw "TShark generated no annotations for $protocol; check PcapRoot and frame metadata" }
  }
  $out = Join-Path $OutputRoot "$protocol.jsonl"
  & $Python $Builder $messages $annotations $out --protocol $protocol --batch-size $BatchSize --tasks $Tasks
  if ($LASTEXITCODE -ne 0) { throw "Builder failed for $protocol" }
}
Write-Host "Cluster-free dataset written to $OutputRoot"
