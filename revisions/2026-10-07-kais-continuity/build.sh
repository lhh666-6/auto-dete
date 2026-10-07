#!/usr/bin/env bash
# Compile editable manuscript sources. No model/provider call is made.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p out
for document in main supplement; do
  for pass in 1 2 3; do
    pdflatex -interaction=nonstopmode -halt-on-error \
      -output-directory=out "${document}.tex" \
      >"out/${document}-pass${pass}.stdout" 2>&1 || {
        tail -60 "out/${document}-pass${pass}.stdout" >&2
        exit 1
      }
  done
  if grep -E 'undefined references|Citation .* undefined|Reference .* undefined|Overfull' \
      "out/${document}.log"; then
    echo "Review warnings in out/${document}.log before delivery." >&2
    exit 1
  fi
  cp "out/${document}.pdf" "${document}.pdf"
done
printf 'Compiled main.pdf and supplement.pdf.\n'
