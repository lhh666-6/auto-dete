$ErrorActionPreference = "Stop"

$RevisionRoot = "D:\Claude_Design\auto-decte-paper\revisions\2026-08-27-jss-r21-live-agent-performance"
$BenchmarkBase = Join-Path $RevisionRoot "evidence\agent-authority-benchmark-v2"
$FrozenRoot = Join-Path $BenchmarkBase "final-freezes\2026-09-01-three-config-10x-r3"
$FrozenBenchmark = Join-Path $FrozenRoot "source\agent-authority-benchmark"
$ConfigRoot = Join-Path $FrozenBenchmark "config"
$OutputRoot = Join-Path $BenchmarkBase "final\2026-09-01-three-config-10x"
$ControlRoot = Join-Path $BenchmarkBase "final-control\2026-09-01-three-config-10x-r3"
$BenchmarkPython = Join-Path $RevisionRoot "source\agent-authority-benchmark\.venv\Scripts\python.exe"
$ImplementationPython = Join-Path $RevisionRoot "source\implementation\.venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $BenchmarkPython -PathType Leaf)) {
    throw "Benchmark Python is unavailable: $BenchmarkPython"
}
if (-not (Test-Path -LiteralPath $ImplementationPython -PathType Leaf)) {
    throw "Implementation Python is unavailable: $ImplementationPython"
}
if (-not (Test-Path -LiteralPath (Join-Path $OutputRoot "checkpoints\0002.json") -PathType Leaf)) {
    throw "The immutable two-terminal resume boundary is missing"
}
if (Test-Path -LiteralPath $ControlRoot) {
    throw "Control root already exists: $ControlRoot"
}

New-Item -ItemType Directory -Path $ControlRoot | Out-Null
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:AUTO_DECTE_IMPLEMENTATION_PYTHON = $ImplementationPython
Set-Location -LiteralPath $FrozenBenchmark

function Write-ControlStatus {
    param(
        [string]$Status,
        [string]$Reason,
        [int]$TerminalExecutions,
        [int]$RemainingExecutions,
        [string]$RunId,
        [string]$TerminalClass
    )
    $value = [ordered]@{
        schema_version = "agent-authority-continuous-control.v1"
        status = $Status
        reason = $Reason
        updated_at = (Get-Date -Format o)
        terminal_executions = $TerminalExecutions
        remaining_executions = $RemainingExecutions
        latest_run_id = $RunId
        latest_terminal_class = $TerminalClass
        frozen_root = $FrozenRoot
        output_root = $OutputRoot
    }
    $value | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $ControlRoot "status.json") -Encoding utf8
}

Write-ControlStatus -Status "RUNNING" -Reason "STARTED" -TerminalExecutions 2 -RemainingExecutions 1258 -RunId "" -TerminalClass ""

while ($true) {
    $existingRuns = @(
        Get-ChildItem -LiteralPath (Join-Path $OutputRoot "runs") -Directory |
            Select-Object -ExpandProperty FullName
    )
    $nextNumber = $existingRuns.Count + 1
    $iterationLog = Join-Path $ControlRoot ("invocation-{0:D4}.log" -f $nextNumber)
    $runnerArguments = @(
        "-B",
        "-m", "auto_decte_agent_benchmark.runner",
        "--final",
        "--config", $ConfigRoot,
        "--output", $OutputRoot,
        "--frozen-root", $FrozenRoot,
        "--resume",
        "--max-new-invocations", "1"
    )

    & $BenchmarkPython @runnerArguments *>&1 | Tee-Object -FilePath $iterationLog
    $runnerExitCode = $LASTEXITCODE

    $currentRuns = @(
        Get-ChildItem -LiteralPath (Join-Path $OutputRoot "runs") -Directory |
            Select-Object -ExpandProperty FullName
    )
    $newRuns = @($currentRuns | Where-Object { $_ -notin $existingRuns })
    if ($newRuns.Count -ne 1) {
        Write-ControlStatus -Status "STOPPED" -Reason "EXPECTED_EXACTLY_ONE_NEW_TERMINAL" -TerminalExecutions $currentRuns.Count -RemainingExecutions (1260 - $currentRuns.Count) -RunId "" -TerminalClass ""
        exit 2
    }

    $runPath = Join-Path $newRuns[0] "run.json"
    $run = Get-Content -LiteralPath $runPath -Raw | ConvertFrom-Json
    $terminalCount = $currentRuns.Count
    $remaining = 1260 - $terminalCount

    if ($runnerExitCode -ne 0) {
        Write-ControlStatus -Status "STOPPED" -Reason "RUNNER_EXIT_$runnerExitCode" -TerminalExecutions $terminalCount -RemainingExecutions $remaining -RunId $run.run_id -TerminalClass $run.terminal_class
        exit $runnerExitCode
    }
    if ($run.unauthorized_authoritative_mutation -eq $true -or $run.mechanism_authority_violation -eq $true) {
        Write-ControlStatus -Status "STOPPED" -Reason "AUTHORITY_VIOLATION" -TerminalExecutions $terminalCount -RemainingExecutions $remaining -RunId $run.run_id -TerminalClass $run.terminal_class
        exit 3
    }
    if ($run.terminal_class -in @("MODEL_API_FAILURE", "TOOL_RUNTIME_FAILURE", "TIMEOUT", "HARNESS_FAILURE")) {
        Write-ControlStatus -Status "STOPPED" -Reason "RUNTIME_OR_PROVIDER_FAILURE" -TerminalExecutions $terminalCount -RemainingExecutions $remaining -RunId $run.run_id -TerminalClass $run.terminal_class
        exit 4
    }
    if ($terminalCount -ge 1260) {
        Write-ControlStatus -Status "COMPLETE" -Reason "ALL_TERMINALS_PRESENT" -TerminalExecutions $terminalCount -RemainingExecutions 0 -RunId $run.run_id -TerminalClass $run.terminal_class
        exit 0
    }

    Write-ControlStatus -Status "RUNNING" -Reason "LAST_INVOCATION_ACCEPTED" -TerminalExecutions $terminalCount -RemainingExecutions $remaining -RunId $run.run_id -TerminalClass $run.terminal_class
}
