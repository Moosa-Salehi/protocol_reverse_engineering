param(
  [string]$PcapDir="D:\tez\practical\traffic",
  [string]$Python="py -3.12",
  [int]$BudgetPerProtocol=20000,
  [int]$MaxMessages=20000,
  [int]$MinimumTargetSupport=2,
  [int]$MinimumFamilyPackets=2,
  [double]$MinimumFamilyPurity=0.95,
  [switch]$SkipTargetGeneration,
  [switch]$IncludeHoldout,
  [switch]$ReuseSampledPcaps
)
$ErrorActionPreference="Stop"
$FinetuningRoot=Split-Path -Parent $PSScriptRoot
$Root=Split-Path -Parent $FinetuningRoot
$Work=Join-Path $FinetuningRoot "windows_data"
$Samples=Join-Path $Work "sampled_pcaps"
$SupervisedCheckpoint=Join-Path $Root "VAE_supervised_train\checkpoints\best_v3.pth"
New-Item -ItemType Directory -Force -Path $Samples | Out-Null
function Invoke-Python([string[]]$Arguments) {
  if($Python -eq "py -3.12") { & py -3.12 @Arguments }
  else { & $Python @Arguments }
  if($LASTEXITCODE -ne 0){throw "Python command failed: $Python $($Arguments -join ' ')"}
}
$samplingReport=Join-Path $Samples "sampling_report.json"
if($ReuseSampledPcaps -and (Test-Path $samplingReport)) {
  Write-Host "Reusing existing sampled PCAPs in $Samples"
} else {
  $sampleArgs=@("$PSScriptRoot\sample_pcaps_windows.py","--pcap-dir",$PcapDir,"--output-dir",$Samples,"--budget-per-protocol",$BudgetPerProtocol)
  if($IncludeHoldout){$sampleArgs+="--include-holdout"}
  Invoke-Python $sampleArgs
}
$Config=Get-Content -Raw "$PSScriptRoot\protocols.json" | ConvertFrom-Json
$Protocols=@($Config.train.PSObject.Properties)
if($IncludeHoldout){$Protocols+=@($Config.holdout.PSObject.Properties)}
$JsonlDir=Join-Path $Work "candidate_jsonl";New-Item -ItemType Directory -Force -Path $JsonlDir|Out-Null
foreach($Entry in $Protocols){
  $Name=$Entry.Name;$Filter=$Entry.Value.filter;$SampleInput=Join-Path $Samples $Name
  $SetName = if($Config.holdout.PSObject.Properties.Name -contains $Name){"holdout"}else{"train"}
  $PcapFiles=@(Get-ChildItem $SampleInput -File -ErrorAction SilentlyContinue | Where-Object {$_.Extension -in ".pcap", ".pcapng", ".cap"})
  if($PcapFiles.Count -eq 0){Write-Warning "No sampled PCAPs for $Name; skipping protocol";continue}
  $Run=Join-Path $Work "runs\$Name";$Data=Join-Path $Run "data";$Output=Join-Path $Run "output";$Logs=Join-Path $Run "logs"
  if(-not (Test-Path $SupervisedCheckpoint)){ throw "Supervised VAE checkpoint not found: $SupervisedCheckpoint" }
  Invoke-Python @("$Root\main.py", $SampleInput, "--extraction-method", "tshark", "--tshark-filter", $Filter, "--save-field-spans", "--max-messages", $MaxMessages, "--data-dir", $Data, "--output-dir", $Output, "--log-dir", $Logs, "--family-feature-mode", "neural", "--family-neural-model-path", $SupervisedCheckpoint, "--family-supervised-hdbscan-checkpoint", $SupervisedCheckpoint, "--llm-render-only", "--stop-after", "13_evaluate_pipeline")
  Invoke-Python @("$Root\scripts\14_export_llm_evidence.py", "$Data\10_protocol_model.json", "$Data\12_llm_evidence.json", "--evaluation-json", "$Data\11_evaluation.json", "--pretty", "--log-dir", $Logs)
  $Targets=Join-Path $Work "wireshark_targets\$Name.json"
  if(-not $SkipTargetGeneration){
    $Report=Join-Path $Work "wireshark_target_reports\$Name.review.json"
    $PcapFiles=@(Get-ChildItem $SampleInput -File | Where-Object {$_.Extension -in ".pcap", ".pcapng", ".cap"} | Sort-Object FullName)
    if($PcapFiles.Count -eq 0){Write-Warning "No sampled PCAP files available for automatic targets: $Name"}
    else{
      $targetArgs=@("$PSScriptRoot\generate_wireshark_targets.py", "$Data\10_protocol_model.json", "$Data\01_messages.jsonl", "$Data\02_family_assignments.json")
      $targetArgs+=@($PcapFiles.FullName)
      $targetArgs+=@("--filter",$Filter,"--output",$Targets,"--report",$Report,"--minimum-support",$MinimumTargetSupport,"--minimum-family-packets",$MinimumFamilyPackets,"--minimum-family-purity",$MinimumFamilyPurity)
      Invoke-Python $targetArgs
      Write-Warning "Generated target candidates for $Name. Review $Report, then rerun with -SkipTargetGeneration to create approved candidate JSONL."
      continue
    }
  }
  if(-not(Test-Path $Targets)){Write-Warning "Skipping {$Name}: create $Targets from trusted Wireshark annotations first"; continue}
  $SetDir=Join-Path $JsonlDir $SetName;New-Item -ItemType Directory -Force -Path $SetDir|Out-Null
  Invoke-Python @("$PSScriptRoot\build_evidence_dataset.py", "$Data\10_protocol_model.json", "$SetDir\$Name.jsonl", "--evidence-bundle", "$Data\12_llm_evidence.json", "--wireshark-targets", $Targets)
}
Write-Host "Candidate artifacts created under $Work"
Write-Host "Review ambiguity reports under $Work\wireshark_target_reports, then run prepare_dataset_windows.ps1."
