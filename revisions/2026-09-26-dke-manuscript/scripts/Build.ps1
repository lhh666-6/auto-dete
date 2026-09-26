$ErrorActionPreference = 'Stop'
$paperRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $paperRoot
try {
    New-Item -ItemType Directory -Path (Join-Path $paperRoot 'out') -Force | Out-Null
    foreach ($document in @('main', 'supplement')) {
        & pdflatex -interaction=nonstopmode -halt-on-error -output-directory=out "$document.tex"
        if ($LASTEXITCODE -ne 0) { throw "$document initial compilation failed." }
        if ($document -eq 'main') {
            & bibtex 'out/main'
            if ($LASTEXITCODE -ne 0) { throw 'Bibliography compilation failed.' }
        }
        foreach ($pass in 1..2) {
            & pdflatex -interaction=nonstopmode -halt-on-error -output-directory=out "$document.tex"
            if ($LASTEXITCODE -ne 0) { throw "$document reference pass $pass failed." }
        }
        $buildLog = Get-Content -LiteralPath (Join-Path $paperRoot "out/$document.log") -Raw
        if ($buildLog -match 'undefined|Overfull|LaTeX Warning') {
            throw "$document still has unresolved references or layout warnings; inspect out/$document.log."
        }
        Copy-Item -LiteralPath (Join-Path $paperRoot "out/$document.pdf") -Destination (Join-Path $paperRoot "$document.pdf")
    }
} finally {
    Pop-Location
}
