param(
    [switch]$RequireRawResults
)

$ErrorActionPreference = 'Stop'

$batchRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$formalRoot = Split-Path -Parent $batchRoot
$expectedHistoricalHashes = @{
    'auto_decte.als' = '3E42226A642E458170B85671A56FF8438FDC7C8DBA72B970C53822867E7F9D19'
    'auto_decte_s2.als' = '44E54BA1BA81358308B1CBD1FE7D4B38AF79B05EA97E1487A48ED9E77781C4E9'
}

$requiredFiles = @(
    (Join-Path $batchRoot 'auto_decte_batch.als'),
    (Join-Path $batchRoot 'auto_decte_batch_s2.als'),
    (Join-Path $batchRoot 'command_manifest.tsv')
)

$errors = [System.Collections.Generic.List[string]]::new()
foreach ($path in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $path)) {
        $errors.Add("missing required batch artifact: $path")
    }
}

foreach ($entry in $expectedHistoricalHashes.GetEnumerator()) {
    $path = Join-Path $formalRoot $entry.Key
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash
    if ($actual -ne $entry.Value) {
        $errors.Add("historical singleton model changed: $($entry.Key) expected=$($entry.Value) actual=$actual")
    }
}

if (Test-Path -LiteralPath $requiredFiles[0]) {
    $model = Get-Content -LiteralPath $requiredFiles[0] -Raw
    $requiredTokens = @(
        'sig AdmissionItem',
        'sig BatchAdmissionEvent',
        'pred baseAdmissionEffect',
        'pred batchContract',
        'pred fullItemOk',
        'assert StateInvariantPreserved',
        'assert FullNoPartialItemEffects',
        'assert SingletonContractEquivalence',
        'run SAT_BATCH_accept_multi',
        'run SAT_BATCH_correction_multi',
        'run SAT_BATCH_mixed_accept_correction',
        'run SAT_BATCH_same_value_multi',
        'run SAT_P6_legal_anchor_loss',
        'run SAT_P6_legal_anchor_replacement',
        'run SAT_P6_legal_source_version_duplicate'
    )
    foreach ($token in $requiredTokens) {
        if (-not $model.Contains($token)) {
            $errors.Add("batch model missing token: $token")
        }
    }

    foreach ($name in @('ABL_1','ABL_2a','ABL_2b','ABL_3','ABL_4a','ABL_4b','ABL_5','ABL_6','ABL_8','ABL_9','ABL_10')) {
        if (-not $model.Contains("run SAT_${name}_effective_pair")) {
            $errors.Add("batch model missing effective paired witness: $name")
        }
    }
}

if (Test-Path -LiteralPath $requiredFiles[2]) {
    $manifest = Import-Csv -Delimiter "`t" -LiteralPath $requiredFiles[2]
    if ($manifest.Count -eq 0) {
        $errors.Add('command manifest is empty')
    }
    $duplicate = $manifest | Group-Object profile, command | Where-Object Count -gt 1
    if ($duplicate) {
        $errors.Add('command manifest contains duplicate profile/command rows')
    }
    foreach ($row in $manifest) {
        if ($row.expected -notin @('SAT','UNSAT')) {
            $errors.Add("invalid expected result for $($row.command): $($row.expected)")
        }
        if ($row.class -notin @('well-formedness','preservation','legal-witness','ablation-witness','attack-witness','regression')) {
            $errors.Add("invalid command class for $($row.command): $($row.class)")
        }
    }
}

if ($RequireRawResults) {
    $freezePath = Join-Path $batchRoot 'ACTIVE_FREEZE.txt'
    if (-not (Test-Path -LiteralPath $freezePath)) {
        $errors.Add("missing active freeze pointer: $freezePath")
    }
    else {
        $freezeId = (Get-Content -LiteralPath $freezePath -Raw).Trim()
        $freezeRoot = Join-Path $batchRoot "raw-results/$freezeId"
        foreach ($profile in @('S1','S2')) {
            $profilePath = Join-Path $freezeRoot $profile
            if (-not (Test-Path -LiteralPath $profilePath)) {
                $errors.Add("missing raw-result profile: $profilePath")
            }
        }

        $summaryPath = Join-Path $freezeRoot 'command_results.tsv'
        $metadataPath = Join-Path $freezeRoot 'run_metadata.json'
        $hashPath = Join-Path $freezeRoot 'artifact_hashes.sha256'
        foreach ($path in @($summaryPath, $metadataPath, $hashPath)) {
            if (-not (Test-Path -LiteralPath $path)) {
                $errors.Add("missing freeze control artifact: $path")
            }
        }

        if (Test-Path -LiteralPath $summaryPath) {
            $summary = Import-Csv -Delimiter "`t" -LiteralPath $summaryPath
            if ($summary.Count -ne $manifest.Count) {
                $errors.Add("freeze command count mismatch: expected=$($manifest.Count) actual=$($summary.Count)")
            }
            if (@($summary | Where-Object status -ne 'PASS').Count -gt 0) {
                $errors.Add('freeze contains failed command expectations')
            }
        }

        if (Test-Path -LiteralPath $metadataPath) {
            $metadata = Get-Content -LiteralPath $metadataPath -Raw | ConvertFrom-Json
            $currentS1 = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $batchRoot 'auto_decte_batch.als')).Hash
            $currentS2 = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $batchRoot 'auto_decte_batch_s2.als')).Hash
            $currentManifest = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $batchRoot 'command_manifest.tsv')).Hash
            if ($metadata.s1_model_sha256 -ne $currentS1) { $errors.Add('active freeze S1 model hash is stale') }
            if ($metadata.s2_model_sha256 -ne $currentS2) { $errors.Add('active freeze S2 model hash is stale') }
            if ($metadata.manifest_sha256 -ne $currentManifest) { $errors.Add('active freeze command manifest hash is stale') }
            if ([int]$metadata.fail_count -ne 0) { $errors.Add('active freeze metadata records failures') }
        }

        if (Test-Path -LiteralPath $hashPath) {
            $repoRoot = (Resolve-Path -LiteralPath (Join-Path $batchRoot '../../..')).Path
            foreach ($line in Get-Content -LiteralPath $hashPath) {
                if ($line -notmatch '^([0-9a-f]{64})  (.+)$') {
                    $errors.Add("malformed hash line: $line")
                    continue
                }
                $expectedHash = $Matches[1].ToUpperInvariant()
                $relativePath = $Matches[2].Replace('/', [System.IO.Path]::DirectorySeparatorChar)
                $artifactPath = Join-Path $repoRoot $relativePath
                if (-not (Test-Path -LiteralPath $artifactPath)) {
                    $errors.Add("hashed artifact missing: $relativePath")
                    continue
                }
                $actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $artifactPath).Hash
                if ($actualHash -ne $expectedHash) {
                    $errors.Add("artifact hash mismatch: $relativePath")
                }
            }
        }
    }
}

if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Output 'BATCH_PACKAGE_STRUCTURE_PASS'
