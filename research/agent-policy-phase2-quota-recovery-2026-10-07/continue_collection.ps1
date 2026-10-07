$ErrorActionPreference = 'Stop'
$recoveryDir = $PSScriptRoot
$pythonPath = 'C:\Users\lenovo\AppData\Local\Programs\Python\Python311\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    $pythonPath = (Get-Command python -ErrorAction Stop).Source
}
$runnerPath = Join-Path $recoveryDir 'run_recovery.py'
$activeCollectors = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
    Where-Object { $_.CommandLine -like '*run_recovery.py*' -and $_.CommandLine -like '*--run*' })
if ($activeCollectors.Count -gt 0) {
    Write-Host 'Collection is already running. No duplicate process was started.'
    Write-Host ('PID: ' + ($activeCollectors.ProcessId -join ', '))
    exit 0
}
& $pythonPath $runnerPath --verify-only
if ($LASTEXITCODE -ne 0) { throw 'Verification failed. Existing data was not changed.' }
$statePath = Join-Path $recoveryDir 'results\collection-status.json'
$state = Get-Content -LiteralPath $statePath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($state.status -eq 'COMPLETE') {
    Write-Host 'This recovery batch has already finished.'
    exit 0
}
$terminalCount = @($state.pairs.PSObject.Properties | Where-Object { $_.Value.status -eq 'terminal' }).Count
$resumeStamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')
$resumePrefix = Join-Path $recoveryDir ('resume-' + $resumeStamp)
$startInfo = @{
    FilePath = $pythonPath
    ArgumentList = @('-u', ('"' + $runnerPath + '"'), '--run')
    WorkingDirectory = $recoveryDir
    WindowStyle = 'Hidden'
    RedirectStandardOutput = ($resumePrefix + '.stdout.log')
    RedirectStandardError = ($resumePrefix + '.stderr.log')
    PassThru = $true
}
$collector = Start-Process @startInfo
$launchRecord = @{
    pid = $collector.Id
    started_utc = [DateTime]::UtcNow.ToString('o')
    original_data = 'preserved'
    resume_from_terminal_pairs = $terminalCount
    planned_pairs = 117
    stdout = ($resumePrefix + '.stdout.log')
    stderr = ($resumePrefix + '.stderr.log')
}
$launchRecord | ConvertTo-Json | Set-Content -LiteralPath ($resumePrefix + '.launch.json') -Encoding UTF8
Write-Host ('Resume process started. PID: ' + $collector.Id)
Write-Host ('Previously ended pairs will be skipped: ' + $terminalCount)
Write-Host 'Use the live monitor to confirm progress. You can close this window.'
