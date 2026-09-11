"""Read-only page-budget map for the compiled manuscript.

Reports which pages each top-level section occupies, plus the pages consumed by
floats (tables/figures) and references.  Writes nothing.
"""

import io
import os
import re
import sys

import fitz  # pymupdf

PAPER = os.environ.get(
    "AUTODECTE_PAPER",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "latest", "paper"),
)

# top-level headings as they appear in the rendered PDF
HEADINGS = [
    ("1 Introduction", "Introduction"),
    ("2 Background and related work", "Background and related work"),
    ("3 Authoritative-state admission contract", "Authoritative-state admission contract"),
    ("4 Bounded relational characterization", "Bounded relational characterization"),
    ("5 Transactional realization", "Transactional realization"),
    ("6 Formal--concrete projection", "Formal\u2013concrete projection and executable conformance"),
    ("7 Evaluation protocol", "Evaluation protocol"),
    ("8 Results", "Results"),
    ("9 Discussion and threats to validity", "Discussion and threats to validity"),
    ("10 Conclusion", "Conclusion"),
    ("Declarations", "Declarations"),
    ("References", "References"),
]


def page_text(doc):
    return [p.get_text("text") for p in doc]


def find_heading(pages, needle, start=0):
    """Return 0-based page index of a heading rendered as its own line."""
    pat = re.compile(r"^\s*" + re.escape(needle) + r"\s*$", re.M)
    for i in range(start, len(pages)):
        if pat.search(pages[i]):
            return i
    # fall back: heading text anywhere on the page
    for i in range(start, len(pages)):
        if needle in pages[i]:
            return i
    return None


def main():
    path = os.path.join(PAPER, "main.pdf")
    doc = fitz.open(path)
    pages = page_text(doc)
    n = len(pages)
    print("main.pdf: %d pages" % n)

    # ---- section map
    found = []
    cur = 0
    for label, needle in HEADINGS:
        idx = find_heading(pages, needle, cur)
        if idx is None:
            print("  !! heading not located: %s" % label)
            continue
        found.append((label, idx))
        cur = idx

    print("\n%-46s %8s %8s" % ("section", "starts", "pages"))
    for k, (label, idx) in enumerate(found):
        end = found[k + 1][1] - 1 if k + 1 < len(found) else n - 1
        print("%-46s %8d %8d" % (label, idx + 1, end - idx + 1))

    # ---- float / prose split by simple heuristics
    print("\n" + "=" * 70)
    print("PAGE CONTENT MIX (heuristic: lines with >=3 large gaps = float)")
    print("=" * 70)
    floatish = 0
    textish = 0
    for i, p in enumerate(doc):
        blocks = p.get_text("dict")["blocks"]
        imgs = sum(1 for b in blocks if b.get("type") == 1)
        tables = 0
        txt = pages[i]
        # a page whose lines are mostly short and column-like is a float page
        lines = [l for l in txt.split("\n") if l.strip()]
        short = sum(1 for l in lines if len(l.strip()) < 45)
        frac = short / max(len(lines), 1)
        if imgs or frac > 0.72:
            floatish += 1
        else:
            textish += 1
    print("  pages that are float-dominant : %d" % floatish)
    print("  pages that are prose-dominant  : %d" % textish)

    # ---- how many pages carry a numbered table or figure caption
    tab = fig = 0
    for p in pages:
        if re.search(r"^Table\s+\d+\.", p, re.M) or re.search(r"^Table S\d+\.", p, re.M):
            tab += 1
        if re.search(r"^Figure\s+\d+\.", p, re.M):
            fig += 1
    print("  pages containing a table caption  : %d" % tab)
    print("  pages containing a figure caption : %d" % fig)

    # ---- references
    ref_idx = find_heading(pages, "References")
    if ref_idx is not None:
        ref_pages = [i for i in range(ref_idx, n)
                     if re.search(r"\(\d{4}\)", pages[i]) or re.match(r"^[A-Z][a-z]+,", pages[i])]
        print("  reference-list pages              : %d (%d-%d)"
              % (len(ref_pages), ref_idx + 1, n))

    # ---- equation count
    eqs = sum(len(re.findall(r"\(\d+\)\s*$", p, re.M)) for p in pages)
    print("  numbered equations rendered       : %d" % eqs)

    # ---- total rendered words
    words = sum(len(p.split()) for p in pages)
    print("  total rendered words              : %d" % words)

    return 0


if __name__ == "__main__":
    sys.exit(main())
