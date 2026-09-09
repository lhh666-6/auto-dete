"""Run deterministic source-level integrity checks for the R21 manuscript."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"

CITE_RE = re.compile(
    r"\\(?:cite|citet|citep|textcite|autocite|parencite|citeauthor|citeyear|nocite)"
    r"(?:\[[^\]]*\])?\{([^}]*)\}"
)
BIB_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,", re.IGNORECASE)
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
REF_RE = re.compile(r"\\(?:ref|cref|Cref|eqref|autoref)\{([^}]+)\}")
PLACEHOLDER_RE = re.compile(
    r"TODO|FIXME|XXX|TBD|\[INSERT|PLACEHOLDER|Lorem ipsum", re.IGNORECASE
)


def split_keys(values: list[str]) -> set[str]:
    return {
        key.strip()
        for value in values
        for key in value.split(",")
        if key.strip() and key.strip() != "*"
    }


def main() -> int:
    tex_files = sorted(PAPER.rglob("*.tex"))
    combined = "\n".join(path.read_text(encoding="utf-8") for path in tex_files)
    bib_text = (PAPER / "filtered.bib").read_text(encoding="utf-8")

    cited = split_keys(CITE_RE.findall(combined))
    bib_list = BIB_RE.findall(bib_text)
    bib_keys = set(bib_list)
    labels = set(LABEL_RE.findall(combined))
    referenced = split_keys(REF_RE.findall(combined))
    duplicate_bib_keys = sorted(
        key for key in bib_keys if bib_list.count(key) > 1
    )
    placeholders = []
    for path in tex_files:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if PLACEHOLDER_RE.search(line):
                placeholders.append(f"{path.relative_to(ROOT).as_posix()}:{line_number}")

    report = {
        "schema": "auto-decte.r21-paper-source-audit.v1",
        "tex_files": len(tex_files),
        "cited_keys": len(cited),
        "bib_entries": len(bib_keys),
        "missing_citation_keys": sorted(cited - bib_keys),
        "unused_bib_keys": sorted(bib_keys - cited),
        "duplicate_bib_keys": duplicate_bib_keys,
        "missing_reference_labels": sorted(referenced - labels),
        "unreferenced_labels": sorted(labels - referenced),
        "placeholders": placeholders,
    }
    failures = (
        report["missing_citation_keys"]
        + report["duplicate_bib_keys"]
        + report["missing_reference_labels"]
        + report["placeholders"]
    )
    report["verified"] = not failures
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
