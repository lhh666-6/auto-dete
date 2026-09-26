$ErrorActionPreference = 'Stop'
$paperRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $paperRoot
try {
    & latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
    if ($LASTEXITCODE -ne 0) { throw 'Main manuscript compilation failed.' }
    & latexmk -pdf -interaction=nonstopmode -halt-on-error supplement.tex
    if ($LASTEXITCODE -ne 0) { throw 'Supplement compilation failed.' }
} finally {
    Pop-Location
}
