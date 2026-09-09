$ErrorActionPreference = "Stop"

$Policy = Join-Path $PSScriptRoot "continuation-policy.ps1"
if (-not (Test-Path -LiteralPath $Policy -PathType Leaf)) {
    throw "Missing continuation policy: $Policy"
}
. $Policy

function Assert-Decision(
    [string]$ExpectedAction,
    [string]$ExpectedReason,
    [int]$RunnerExit,
    [int]$NewTerminalCount,
    [object[]]$FreezeFailures,
    [object]$Run,
    [string]$EvidenceText
) {
    $actual = Get-AutoDecteContinuationDecision `
        -RunnerExit $RunnerExit `
        -NewTerminalCount $NewTerminalCount `
        -FreezeFailures $FreezeFailures `
        -Run $Run `
        -EvidenceText $EvidenceText
    if ($actual.action -ne $ExpectedAction -or $actual.reason -ne $ExpectedReason) {
        throw "Expected $ExpectedAction/$ExpectedReason, got $($actual.action)/$($actual.reason)"
    }
}

$safe = [pscustomobject]@{
    terminal_class = "PASS_UTILITY_SAFE"
    unauthorized_authoritative_mutation = $false
    mechanism_authority_violation = $false
}
$harness = [pscustomobject]@{
    terminal_class = "HARNESS_FAILURE"
    unauthorized_authoritative_mutation = $false
    mechanism_authority_violation = $false
}
$timeout = [pscustomobject]@{
    terminal_class = "TIMEOUT"
    unauthorized_authoritative_mutation = $false
    mechanism_authority_violation = $false
}
$ordinaryApi = [pscustomobject]@{
    terminal_class = "MODEL_API_FAILURE"
    unauthorized_authoritative_mutation = $false
    mechanism_authority_violation = $false
}
$authority = [pscustomobject]@{
    terminal_class = "PASS_UTILITY_SAFE"
    unauthorized_authoritative_mutation = $true
    mechanism_authority_violation = $false
}
$mechanism = [pscustomobject]@{
    terminal_class = "PASS_UTILITY_SAFE"
    unauthorized_authoritative_mutation = $false
    mechanism_authority_violation = $true
}

Assert-Decision "CONTINUE" "TERMINAL_RECORDED" 0 1 @() $safe ""
Assert-Decision "CONTINUE" "TERMINAL_RECORDED" 0 1 @() $harness ""
Assert-Decision "CONTINUE" "TERMINAL_RECORDED" 0 1 @() $timeout "request timed out"
Assert-Decision "CONTINUE" "TERMINAL_RECORDED" 0 1 @() $ordinaryApi "temporary upstream error"
Assert-Decision "PAUSE" "EXPLICIT_QUOTA_EXHAUSTION" 0 1 @() $ordinaryApi "usage limit reached; quota exhausted"
Assert-Decision "STOP" "AUTHORITY_VIOLATION" 0 1 @() $authority ""
Assert-Decision "STOP" "AUTHORITY_VIOLATION" 0 1 @() $mechanism ""
Assert-Decision "STOP" "RUNNER_EXIT_7" 7 1 @() $safe ""
Assert-Decision "STOP" "EXPECTED_EXACTLY_ONE_NEW_TERMINAL" 0 0 @() $null ""
Assert-Decision "STOP" "EXPECTED_EXACTLY_ONE_NEW_TERMINAL" 0 2 @() $null ""
Assert-Decision "STOP" "FREEZE_VERIFICATION_FAILED" 0 1 @("HASH_OR_SIZE:file") $safe ""

Write-Output "continuation-policy tests: PASS"
