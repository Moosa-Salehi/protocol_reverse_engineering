param(
    [string]$PcapDir = "D:\tez\practical\traffic\pcaps",
    [int]$MaxFilesPerProtocol = 40,
    [int]$MaxPacketsPerFile = 12,
    [switch]$ScanAllFiles
)
$ErrorActionPreference = "Stop"
$Python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$DataDir = Join-Path $PSScriptRoot "data"
New-Item -ItemType Directory -Force -Path $DataDir | Out-Null
$Arguments = @(
    "$PSScriptRoot\build_tshark_dataset.py", "--pcap-dir", $PcapDir,
    "--output", "$DataDir\raw_train.jsonl", "--split", "train",
    "--max-files-per-protocol", $MaxFilesPerProtocol,
    "--max-packets-per-file", $MaxPacketsPerFile
)
if ($ScanAllFiles) { $Arguments += "--scan-all-files" }
& $Python @Arguments
& $Python "$PSScriptRoot\prepare_dataset.py" "$DataDir\raw_train.jsonl" $DataDir

