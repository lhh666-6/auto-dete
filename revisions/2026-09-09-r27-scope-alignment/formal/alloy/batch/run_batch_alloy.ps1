param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9._-]+$')]
    [string]$FreezeId,
    [string]$OutputRoot = ''
)

$ErrorActionPreference = 'Stop'

function Get-Sha256([string]$LiteralPath) {
    $stream = [System.IO.File]::OpenRead($LiteralPath)
    try {
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        try {
            return (($sha256.ComputeHash($stream) | ForEach-Object { $_.ToString('x2') }) -join '')
        }
        finally {
            $sha256.Dispose()
        }
    }
    finally {
        $stream.Dispose()
    }
}

function Get-PortableRelativePath([string]$BasePath, [string]$TargetPath) {
    $separator = [System.IO.Path]::DirectorySeparatorChar
    $baseUri = [System.Uri]($BasePath.TrimEnd($separator) + $separator)
    $targetUri = [System.Uri]$TargetPath
    return [System.Uri]::UnescapeDataString($baseUri.MakeRelativeUri($targetUri).ToString())
}

$batchRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $batchRoot '../../..')).Path
$manifestPath = Join-Path $batchRoot 'command_manifest.tsv'
$jarPath = Join-Path $repoRoot 'tools/alloy-6.2.0.jar'
$portableJava = Join-Path $repoRoot 'tools/jre21'
$javaPath = if (Test-Path -LiteralPath $portableJava) {
    Get-ChildItem -LiteralPath $portableJava -Recurse -Filter java.exe |
        Select-Object -First 1 -ExpandProperty FullName
}
else {
    (Get-Command java -ErrorAction SilentlyContinue).Source
}
$freezeRoot = if ($OutputRoot) { $OutputRoot } else { Join-Path $batchRoot "raw-results/$FreezeId" }

if (-not $javaPath) {
    throw 'Java runtime not found (portable tools/jre21 or PATH).'
}
if (-not (Test-Path -LiteralPath $jarPath)) {
    throw "Alloy jar not found: $jarPath"
}
if (Test-Path -LiteralPath $freezeRoot) {
    throw "Refusing to overwrite existing freeze: $freezeRoot"
}

if (-not $OutputRoot) {
    $resolvedBatchRoot = (Resolve-Path -LiteralPath $batchRoot).Path
    $resolvedRawRoot = [System.IO.Path]::GetFullPath((Join-Path $resolvedBatchRoot 'raw-results'))
    $resolvedFreezeRoot = [System.IO.Path]::GetFullPath($freezeRoot)
    if (-not $resolvedFreezeRoot.StartsWith(($resolvedRawRoot + [System.IO.Path]::DirectorySeparatorChar), [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Freeze target escapes batch workspace: $freezeRoot"
    }
}

$rows = Import-Csv -Delimiter "`t" -LiteralPath $manifestPath
$results = [System.Collections.Generic.List[object]]::new()
New-Item -ItemType Directory -Path $freezeRoot | Out-Null

foreach ($profile in @('S1', 'S2')) {
    $modelName = if ($profile -eq 'S1') {
        'auto_decte_batch.als'
    }
    else {
        'auto_decte_batch_s2.als'
    }
    $modelPath = Join-Path $batchRoot $modelName
    $profileRoot = Join-Path $freezeRoot $profile
    New-Item -ItemType Directory -Path $profileRoot | Out-Null

    foreach ($row in $rows | Where-Object profile -eq $profile) {
        $commandRoot = Join-Path $profileRoot $row.command
        $stdoutPath = Join-Path $profileRoot "$($row.command).stdout.txt"
        $started = Get-Date
        $cliOutput = & $javaPath -jar $jarPath exec -q -c $row.command -t text -o $commandRoot $modelPath 2>&1
        $exitCode = $LASTEXITCODE
        $cliOutput | Set-Content -LiteralPath $stdoutPath -Encoding utf8
        if ($exitCode -ne 0) {
            throw "Alloy CLI failed for $profile/$($row.command); see $stdoutPath"
        }

        $receiptPath = Join-Path $commandRoot 'receipt.json'
        if (-not (Test-Path -LiteralPath $receiptPath)) {
            throw "Missing receipt for $profile/$($row.command)"
        }
        $receipt = Get-Content -LiteralPath $receiptPath -Raw | ConvertFrom-Json
        $commandResult = $receipt.commands.PSObject.Properties[$row.command].Value
        $actual = if ($null -ne $commandResult.solution -and $commandResult.solution.Count -gt 0) {
            'SAT'
        }
        else {
            'UNSAT'
        }
        $durationMs = [int]((Get-Date) - $started).TotalMilliseconds
        $status = if ($actual -eq $row.expected) { 'PASS' } else { 'FAIL' }
        $results.Add([pscustomobject]@{
            profile = $profile
            command = $row.command
            class = $row.class
            expected = $row.expected
            actual = $actual
            status = $status
            wall_ms = $durationMs
            model = $modelName
        })
        Write-Output ("{0}`t{1}`t{2}`tEXPECTED={3}`t{4}" -f $profile, $row.command, $actual, $row.expected, $status)
    }
}

$summaryTsv = Join-Path $freezeRoot 'command_results.tsv'
$results | Export-Csv -Delimiter "`t" -NoTypeInformation -LiteralPath $summaryTsv
$results | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $freezeRoot 'command_results.json') -Encoding utf8

$javaVersionProcess = [System.Diagnostics.Process]::new()
$javaVersionProcess.StartInfo.FileName = $javaPath
$javaVersionProcess.StartInfo.Arguments = '-version'
$javaVersionProcess.StartInfo.UseShellExecute = $false
$javaVersionProcess.StartInfo.RedirectStandardOutput = $true
$javaVersionProcess.StartInfo.RedirectStandardError = $true
$null = $javaVersionProcess.Start()
$javaVersionStdout = $javaVersionProcess.StandardOutput.ReadToEnd()
$javaVersionStderr = $javaVersionProcess.StandardError.ReadToEnd()
$javaVersionProcess.WaitForExit()
if ($javaVersionProcess.ExitCode -ne 0) {
    throw "Java version probe failed with exit code $($javaVersionProcess.ExitCode)"
}
$javaVersion = (($javaVersionStderr + $javaVersionStdout) | Out-String).Trim()

$metadata = [ordered]@{
    freeze_id = $FreezeId
    generated_at = (Get-Date).ToString('o')
    java = $javaVersion
    alloy_jar = 'tools/alloy-6.2.0.jar'
    alloy_jar_sha256 = Get-Sha256 $jarPath
    manifest_sha256 = Get-Sha256 $manifestPath
    s1_model_sha256 = Get-Sha256 (Join-Path $batchRoot 'auto_decte_batch.als')
    s2_model_sha256 = Get-Sha256 (Join-Path $batchRoot 'auto_decte_batch_s2.als')
    command_count = $results.Count
    pass_count = @($results | Where-Object status -eq 'PASS').Count
    fail_count = @($results | Where-Object status -eq 'FAIL').Count
}
$metadata | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $freezeRoot 'run_metadata.json') -Encoding utf8

$hashInputs = @(
    (Join-Path $batchRoot 'auto_decte_batch.als'),
    (Join-Path $batchRoot 'auto_decte_batch_s2.als'),
    $manifestPath
) + @(Get-ChildItem -LiteralPath $freezeRoot -Recurse -File | Select-Object -ExpandProperty FullName)
$hashLines = foreach ($path in $hashInputs | Sort-Object -Unique) {
    $resolved = (Resolve-Path -LiteralPath $path).Path
    $relative = Get-PortableRelativePath $repoRoot $resolved
    $hash = Get-Sha256 $resolved
    "$hash  $relative"
}
$hashLines | Set-Content -LiteralPath (Join-Path $freezeRoot 'artifact_hashes.sha256') -Encoding ascii

$failures = @($results | Where-Object status -eq 'FAIL')
if ($failures.Count -gt 0) {
    throw "Alloy expectation failures: $($failures.Count). Freeze remains inactive for diagnosis."
}

if ($OutputRoot) {
    $FreezeId | Set-Content -LiteralPath (Join-Path $freezeRoot 'ACTIVE_FREEZE.txt') -Encoding ascii
} else {
    $FreezeId | Set-Content -LiteralPath (Join-Path $batchRoot 'ACTIVE_FREEZE.txt') -Encoding ascii
}
Write-Output ("BATCH_ALLOY_FREEZE_PASS`t{0}`tCOMMANDS={1}" -f $FreezeId, $results.Count)
