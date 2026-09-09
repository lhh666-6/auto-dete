function Get-AutoDecteContinuationDecision {
    param(
        [Parameter(Mandatory = $true)][int]$RunnerExit,
        [Parameter(Mandatory = $true)][int]$NewTerminalCount,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][object[]]$FreezeFailures,
        [AllowNull()][object]$Run,
        [AllowEmptyString()][string]$EvidenceText = ""
    )

    if ($FreezeFailures.Count -gt 0) {
        return [pscustomobject]@{ action = "STOP"; reason = "FREEZE_VERIFICATION_FAILED" }
    }
    if ($RunnerExit -ne 0) {
        return [pscustomobject]@{ action = "STOP"; reason = "RUNNER_EXIT_$RunnerExit" }
    }
    if ($NewTerminalCount -ne 1 -or $null -eq $Run) {
        return [pscustomobject]@{ action = "STOP"; reason = "EXPECTED_EXACTLY_ONE_NEW_TERMINAL" }
    }
    if ($Run.unauthorized_authoritative_mutation -eq $true -or $Run.mechanism_authority_violation -eq $true) {
        return [pscustomobject]@{ action = "STOP"; reason = "AUTHORITY_VIOLATION" }
    }

    $quotaPattern = "usage\s+limit|quota\s+(?:is\s+)?exhausted|quota\s+exceeded|insufficient_quota|out\s+of\s+credits|credit\s+balance|billing\s+hard\s+limit"
    if ($Run.terminal_class -eq "MODEL_API_FAILURE" -and $EvidenceText -match $quotaPattern) {
        return [pscustomobject]@{ action = "PAUSE"; reason = "EXPLICIT_QUOTA_EXHAUSTION" }
    }

    return [pscustomobject]@{ action = "CONTINUE"; reason = "TERMINAL_RECORDED" }
}
