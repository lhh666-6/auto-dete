$ErrorActionPreference = "Stop"

$RevisionRoot = "D:\Claude_Design\auto-decte-paper\revisions\2026-08-27-jss-r21-live-agent-performance"
$Base = Join-Path $RevisionRoot "evidence\agent-authority-benchmark-v2"
$Output = Join-Path $Base "final\2026-09-01-three-config-10x"
$OldScriptName = "continue-final-from-0072.ps1"
$NewScript = Join-Path $PSScriptRoot "continue-final-policy-a.ps1"
$HandoverRoot = Join-Path $Base "final-control\2026-09-01-three-config-10x-r3-policy-a-handover"

if (Test-Path -LiteralPath $HandoverRoot) {
    throw "Handover root already exists: $HandoverRoot"
}
New-Item -ItemType Directory -Path $HandoverRoot | Out-Null

[ordered]@{
    schema_version = "agent-authority-policy-handover.v1"
    status = "WAITING_FOR_SAFE_BOUNDARY"
    updated_at = (Get-Date -Format o)
    output_root = $Output
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $HandoverRoot "status.json") -Encoding utf8

while ($true) {
    $processes = Get-CimInstance Win32_Process
    $oldControllers = @($processes | Where-Object {
        $_.Name -eq "powershell.exe" -and $_.CommandLine -like "*$OldScriptName*"
    })
    if ($oldControllers.Count -eq 0) {
        break
    }
    Start-Sleep -Seconds 5
}

while ($true) {
    $processes = Get-CimInstance Win32_Process
    $activeWorkers = @($processes | Where-Object {
        ($_.Name -in @("python.exe", "codex.exe")) -and $_.CommandLine -like "*2026-09-01-three-config-10x*"
    })
    if ($activeWorkers.Count -eq 0) {
        break
    }
    Start-Sleep -Seconds 2
}

$count = @(Get-ChildItem -LiteralPath (Join-Path $Output "runs") -Directory).Count
if ($count -ge 1260) {
    [ordered]@{
        schema_version = "agent-authority-policy-handover.v1"
        status = "NOT_NEEDED_FINAL_COMPLETE"
        updated_at = (Get-Date -Format o)
        terminal_executions = $count
        output_root = $Output
    } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $HandoverRoot "status.json") -Encoding utf8
    exit 0
}

$checkpoint = Join-Path $Output ("checkpoints\{0:D4}.json" -f $count)
if (-not (Test-Path -LiteralPath $checkpoint -PathType Leaf)) {
    throw "Safe handover checkpoint is missing: $checkpoint"
}

$existingNewController = @(Get-CimInstance Win32_Process | Where-Object {
    $_.Name -eq "powershell.exe" -and $_.CommandLine -like "*continue-final-policy-a.ps1*"
})
if ($existingNewController.Count -gt 0) {
    throw "Policy A controller is already running"
}

$controller = Start-Process -FilePath "powershell.exe" `
    -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $NewScript) `
    -WindowStyle Hidden `
    -PassThru

[ordered]@{
    schema_version = "agent-authority-policy-handover.v1"
    status = "POLICY_A_LAUNCHED"
    updated_at = (Get-Date -Format o)
    terminal_executions = $count
    controller_pid = $controller.Id
    output_root = $Output
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $HandoverRoot "status.json") -Encoding utf8
