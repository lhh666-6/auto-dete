"""Independent check of r22-concise compression: citations, section deltas."""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
REVIEW = ROOT / "revisions/2026-09-08-r22-review-response/paper"
CONCISE = ROOT / "revisions/2026-09-08-r22-concise/paper"

CITE_RE = re.compile(r"\\cite[a-zA-Z]*\s*\{([^}]*)\}")
BIB_RE = re.compile(r"@\w+\s*\{\s*([^,]+),")


def cited(root):
    keys = set()
    for f in pathlib.Path(root).rglob("*.tex"):
        s = f.read_text(encoding="utf-8", errors="replace")
        for m in CITE_RE.findall(s):
            keys |= {c.strip() for c in m.split(",") if c.strip()}
    return keys


def bib_keys(p):
    return set(BIB_RE.findall(pathlib.Path(p).read_text(encoding="utf-8", errors="replace")))


for name, root in (("r22-64p", REVIEW), ("r22-concise", CONCISE)):
    bib = bib_keys(root / "filtered.bib")
    cit = cited(root)
    print(f"{name}: bib={len(bib)} cited={len(cit)} uncited={len(bib - cit)} missing={sorted(cit - bib)}")

print("\n=== section char counts (base=64p -> concise) ===")
for f in sorted((REVIEW / "sections").glob("*.tex")):
    c = CONCISE / "sections" / f.name
    cb = c.stat().st_size if c.exists() else 0
    print(f"{f.name:45s} base={f.stat().st_size:6d} concise={cb:6d} delta={cb - f.stat().st_size:+6d}")
for f in ("main.tex", "artifact_appendix.tex"):
    b = (REVIEW / f).stat().st_size
    c = (CONCISE / f).stat().st_size
    print(f"{f:45s} base={b:6d} concise={c:6d} delta={c - b:+6d}")
print("supplement.tex concise:", (CONCISE / "supplement.tex").stat().st_size)

print("\n=== citation keys: r22-64p vs concise ===")
a, b = cited(REVIEW), cited(CONCISE)
print("only in 64p:", sorted(a - b))
print("only in concise:", sorted(b - a))
