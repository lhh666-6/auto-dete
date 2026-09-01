$ErrorActionPreference = "Stop"

$RevisionRoot = "D:\Claude_Design\auto-decte-paper\revisions\2026-08-27-jss-r21-live-agent-performance"
$Base = Join-Path $RevisionRoot "evidence\agent-authority-benchmark-v2"
$Freeze = Join-Path $Base "final-freezes\2026-09-01-three-config-10x-r3"
$FrozenBenchmark = Join-Path $Freeze "source\agent-authority-benchmark"
$Config = Join-Path $FrozenBenchmark "config"
$Output = Join-Path $Base "final\2026-09-01-three-config-10x"
$Python = Join-Path $RevisionRoot "source\agent-authority-benchmark\.venv\Scripts\python.exe"
$ImplementationPython = Join-Path $RevisionRoot "source\implementation\.venv\Scripts\python.exe"
$Policy = Join-Path $PSScriptRoot "continuation-policy.ps1"

. $Policy
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:AUTO_DECTE_IMPLEMENTATION_PYTHON = $ImplementationPython

$existingRuns = @(Get-ChildItem -LiteralPath (Join-Path $Output "runs") -Directory)
$startingCount = $existingRuns.Count
if ($startingCount -lt 72 -or $startingCount -ge 1260) {
    throw "Unexpected starting terminal count: $startingCount"
}
$checkpoint = Join-Path $Output ("checkpoints\{0:D4}.json" -f $startingCount)
if (-not (Test-Path -LiteralPath $checkpoint -PathType Leaf)) {
    throw "Latest checkpoint is missing: $checkpoint"
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Control = Join-Path $Base ("final-control\2026-09-01-three-config-10x-r3-policy-a-after-{0:D4}-{1}" -f $startingCount, $stamp)
if (Test-Path -LiteralPath $Control) {
    throw "Control root already exists: $Control"
}
New-Item -ItemType Directory -Path $Control | Out-Null

$saveStatus = {
    param([string]$Status, [string]$Reason, [int]$Count, [object]$Run)
    [ordered]@{
        schema_version = "agent-authority-continuous-control.v2"
        policy = "policy-a-continue-valid-terminals"
        status = $Status
        reason = $Reason
        updated_at = (Get-Date -Format o)
        terminal_executions = $Count
        remaining_executions = 1260 - $Count
        latest_run_id = if ($null -eq $Run) { "" } else { $Run.run_id }
        latest_terminal_class = if ($null -eq $Run) { "" } else { $Run.terminal_class }
        frozen_root = $Freeze
        output_root = $Output
        control_root = $Control
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $Control "status.json") -Encoding utf8
}

Set-Location -LiteralPath $FrozenBenchmark
$freezeOutput = @(& $Python -B -m auto_decte_agent_benchmark.post_pilot verify-freeze --root $Freeze 2>&1)
$freezeExit = $LASTEXITCODE
$freezeFailures = @()
if ($freezeExit -ne 0) {
    $freezeFailures = @($freezeOutput)
}
if ($freezeFailures.Count -gt 0) {
    & $saveStatus "STOPPED" "FREEZE_VERIFICATION_FAILED" $startingCount $null
    exit 6
}

& $saveStatus "RUNNING" "POLICY_A_ACTIVE" $startingCount $null
while ($true) {
    $before = @(Get-ChildItem -LiteralPath (Join-Path $Output "runs") -Directory | Select-Object -ExpandProperty FullName)
    $log = Join-Path $Control ("invocation-{0:D4}.log" -f ($before.Count + 1))
    & $Python -B -m auto_decte_agent_benchmark.runner --final --config $Config --output $Output --frozen-root $Freeze --resume --max-new-invocations 1 *>&1 | Tee-Object -FilePath $log
    $runnerExit = $LASTEXITCODE
    $after = @(Get-ChildItem -LiteralPath (Join-Path $Output "runs") -Directory | Select-Object -ExpandProperty FullName)
    $new = @($after | Where-Object { $_ -notin $before })
    $run = if ($new.Count -eq 1 -and (Test-Path -LiteralPath (Join-Path $new[0] "run.json"))) {
        Get-Content -LiteralPath (Join-Path $new[0] "run.json") -Raw | ConvertFrom-Json
    } else {
        $null
    }

    $evidenceParts = @()
    if ($null -ne $run -and $null -ne $run.error_class) {
        $evidenceParts += [string]$run.error_class
    }
    if ($new.Count -eq 1) {
        $stderrFiles = @(Get-ChildItem -LiteralPath $new[0] -Filter "stderr.txt" -Recurse -File -ErrorAction SilentlyContinue)
        foreach ($stderrFile in $stderrFiles) {
            $evidenceParts += Get-Content -LiteralPath $stderrFile.FullName -Raw -ErrorAction SilentlyContinue
        }
        $jsonlFiles = @(Get-ChildItem -LiteralPath $new[0] -Filter "*.jsonl" -Recurse -File -ErrorAction SilentlyContinue)
        foreach ($jsonlFile in $jsonlFiles) {
            foreach ($line in Get-Content -LiteralPath $jsonlFile.FullName -ErrorAction SilentlyContinue) {
                try {
                    $event = $line | ConvertFrom-Json
                    if ($event.type -eq "error" -or $event.item.type -eq "error") {
                        $evidenceParts += ($event | ConvertTo-Json -Compress -Depth 8)
                    }
                } catch {
                }
            }
        }
    }

    $decision = Get-AutoDecteContinuationDecision `
        -RunnerExit $runnerExit `
        -NewTerminalCount $new.Count `
        -FreezeFailures @() `
        -Run $run `
        -EvidenceText ($evidenceParts -join "`n")

    if ($decision.action -eq "STOP") {
        & $saveStatus "STOPPED" $decision.reason $after.Count $run
        exit 7
    }
    if ($after.Count -ge 1260) {
        & $saveStatus "COMPLETE" "ALL_TERMINALS_PRESENT" $after.Count $run
        exit 0
    }
    if ($decision.action -eq "PAUSE") {
        & $saveStatus "PAUSED" $decision.reason $after.Count $run
        exit 5
    }
    & $saveStatus "RUNNING" "LAST_TERMINAL_RECORDED_CONTINUING" $after.Count $run
}
