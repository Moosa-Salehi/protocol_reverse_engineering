param(
  [string]$PcapDir="D:\tez\practical\traffic\pcaps",
  [string]$Python="py",
  [int]$BudgetPerProtocol=20000,
  [int]$MaxMessages=20000,
  [switch]$IncludeHoldout
)
$ErrorActionPreference="Stop"
$FinetuningRoot=Split-Path -Parent $PSScriptRoot
$Root=Split-Path -Parent $FinetuningRoot
$Work=Join-Path $FinetuningRoot "windows_data"
$Samples=Join-Path $Work "sampled_pcaps"
New-Item -ItemType Directory -Force -Path $Samples | Out-Null
$sampleArgs=@("$PSScriptRoot\sample_pcaps_windows.py","--pcap-dir",$PcapDir,"--output-dir",$Samples,"--budget-per-protocol",$BudgetPerProtocol)
if($IncludeHoldout){$sampleArgs+="--include-holdout"}
& $Python @sampleArgs
if($LASTEXITCODE -ne 0){throw "PCAP inventory/sampling failed"}
$Config=Get-Content -Raw "$PSScriptRoot\protocols.json" | ConvertFrom-Json
$Protocols=@($Config.train.PSObject.Properties)
if($IncludeHoldout){$Protocols+=@($Config.holdout.PSObject.Properties)}
$JsonlDir=Join-Path $Work "candidate_jsonl";New-Item -ItemType Directory -Force -Path $JsonlDir|Out-Null
foreach($Entry in $Protocols){
  $Name=$Entry.Name;$Filter=$Entry.Value.filter;$SampleInput=Join-Path $Samples $Name
  $SetName = if($Config.holdout.PSObject.Properties.Name -contains $Name){"holdout"}else{"train"}
  if(-not(Test-Path $SampleInput)){Write-Warning "No sampled PCAPs for $Name";continue}
  $Run=Join-Path $Work "runs\$Name";$Data=Join-Path $Run "data";$Output=Join-Path $Run "output";$Logs=Join-Path $Run "logs"
  & $Python "$Root\main.py" $SampleInput --extraction-method tshark --tshark-filter $Filter --max-messages $MaxMessages --data-dir $Data --output-dir $Output --log-dir $Logs --llm-render-only --stop-after 13_evaluate_pipeline
  if($LASTEXITCODE -ne 0){throw "Pipeline failed for $Name"}
  & $Python "$Root\scripts\14_export_llm_evidence.py" "$Data\10_protocol_model.json" "$Data\12_llm_evidence.json" --evaluation-json "$Data\11_evaluation.json" --pretty --log-dir $Logs
  if($LASTEXITCODE -ne 0){throw "Evidence export failed for $Name"}
  $Targets=Join-Path $Work "wireshark_targets\$Name.json"
  if(-not(Test-Path $Targets)){Write-Warning "Skipping $Name: create $Targets from trusted Wireshark annotations first"; continue}
  $SetDir=Join-Path $JsonlDir $SetName;New-Item -ItemType Directory -Force -Path $SetDir|Out-Null
  & $Python "$PSScriptRoot\build_evidence_dataset.py" "$Data\10_protocol_model.json" "$SetDir\$Name.jsonl" --evidence-bundle "$Data\12_llm_evidence.json" --wireshark-targets $Targets
  if($LASTEXITCODE -ne 0){throw "Candidate JSONL generation failed for $Name"}
}
Write-Host "Candidate artifacts created under $Work"
Write-Host "Review/teacher-validate targets, then concatenate approved JSONL files for Ubuntu training."
