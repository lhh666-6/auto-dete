$ErrorActionPreference = "Stop"

$RevisionRoot = "D:\Claude_Design\auto-decte-paper\revisions\2026-08-27-jss-r21-live-agent-performance"
$Base = Join-Path $RevisionRoot "evidence\agent-authority-benchmark-v2"
$Freeze = Join-Path $Base "final-freezes\2026-09-01-three-config-10x-r3"
$FrozenBenchmark = Join-Path $Freeze "source\agent-authority-benchmark"
$Config = Join-Path $FrozenBenchmark "config"
$Output = Join-Path $Base "final\2026-09-01-three-config-10x"
$Control = Join-Path $Base "final-control\2026-09-01-three-config-10x-r3-after-0035"
$Python = Join-Path $RevisionRoot "source\agent-authority-benchmark\.venv\Scripts\python.exe"
$ImplementationPython = Join-Path $RevisionRoot "source\implementation\.venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath (Join-Path $Output "checkpoints\0035.json") -PathType Leaf)) {
    throw "Checkpoint 0035 is missing"
}
if (Test-Path -LiteralPath $Control) {
    throw "Control root already exists: $Control"
}
New-Item -ItemType Directory -Path $Control | Out-Null
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:AUTO_DECTE_IMPLEMENTATION_PYTHON = $ImplementationPython
Set-Location -LiteralPath $FrozenBenchmark

function Save-Status([string]$status, [string]$reason, [int]$count, [object]$run) {
    [ordered]@{
        schema_version = "agent-authority-continuous-control.v1"
        status = $status
        reason = $reason
        updated_at = (Get-Date -Format o)
        terminal_executions = $count
        remaining_executions = 1260 - $count
        latest_run_id = if ($null -eq $run) { "" } else { $run.run_id }
        latest_terminal_class = if ($null -eq $run) { "" } else { $run.terminal_class }
        frozen_root = $Freeze
        output_root = $Output
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $Control "status.json") -Encoding utf8
}

Save-Status "RUNNING" "RESUMED_AFTER_INSPECTED_TIMEOUT" 35 $null
while ($true) {
    $before = @(Get-ChildItem -LiteralPath (Join-Path $Output "runs") -Directory | Select-Object -ExpandProperty FullName)
    $log = Join-Path $Control ("invocation-{0:D4}.log" -f ($before.Count + 1))
    & $Python -B -m auto_decte_agent_benchmark.runner --final --config $Config --output $Output --frozen-root $Freeze --resume --max-new-invocations 1 *>&1 | Tee-Object -FilePath $log
    $runnerExit = $LASTEXITCODE
    $after = @(Get-ChildItem -LiteralPath (Join-Path $Output "runs") -Directory | Select-Object -ExpandProperty FullName)
    $new = @($after | Where-Object { $_ -notin $before })
    if ($new.Count -ne 1) {
        Save-Status "STOPPED" "EXPECTED_EXACTLY_ONE_NEW_TERMINAL" $after.Count $null
        exit 2
    }
    $run = Get-Content -LiteralPath (Join-Path $new[0] "run.json") -Raw | ConvertFrom-Json
    if ($runnerExit -ne 0) {
        Save-Status "STOPPED" "RUNNER_EXIT_$runnerExit" $after.Count $run
        exit $runnerExit
    }
    if ($run.unauthorized_authoritative_mutation -eq $true -or $run.mechanism_authority_violation -eq $true) {
        Save-Status "STOPPED" "AUTHORITY_VIOLATION" $after.Count $run
        exit 3
    }
    if ($run.terminal_class -in @("MODEL_API_FAILURE", "TOOL_RUNTIME_FAILURE", "TIMEOUT", "HARNESS_FAILURE")) {
        Save-Status "STOPPED" "RUNTIME_OR_PROVIDER_FAILURE" $after.Count $run
        exit 4
    }
    if ($after.Count -ge 1260) {
        Save-Status "COMPLETE" "ALL_TERMINALS_PRESENT" $after.Count $run
        exit 0
    }
    Save-Status "RUNNING" "LAST_INVOCATION_ACCEPTED" $after.Count $run
}
