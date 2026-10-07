$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    New-Item -ItemType Directory -Path out -Force | Out-Null
    foreach ($documentName in @('main', 'supplement')) {
        foreach ($buildPass in @(1, 2, 3)) {
            & pdflatex -disable-installer -interaction=nonstopmode -halt-on-error -output-directory=out "$documentName.tex" *> "out/$documentName-pass$buildPass.txt"
            if ($LASTEXITCODE -ne 0) {
                throw "Compilation failed: $documentName; inspect out/$documentName-pass$buildPass.txt"
            }
        }
        $buildWarnings = Select-String -Path "out/$documentName.log" -Pattern 'undefined references|Citation .* undefined|Reference .* undefined|Overfull|Missing character:'
        if ($buildWarnings) {
            throw "Review build warnings in out/$documentName.log before delivery."
        }
        Copy-Item -LiteralPath "out/$documentName.pdf" -Destination "$documentName.pdf"
    }
} finally {
    Pop-Location
}
