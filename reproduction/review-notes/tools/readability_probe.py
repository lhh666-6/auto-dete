"""Read-only readability probe: negation runs, scope-limiting density, paragraphs.

Complements style_probe.py.  Writes nothing; prints a report on stdout.
"""

import io
import os
import re

PAPER = os.environ.get(
    "AUTODECTE_PAPER",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "latest", "paper"),
)

SECTIONS = [
    ("01", "sections/01-introduction.tex"),
    ("02", "sections/02-related-work.tex"),
    ("03", "sections/03-problem-contract.tex"),
    ("04", "sections/04-relational-analysis.tex"),
    ("05", "sections/05-transactional-realization.tex"),
    ("06", "sections/06-formal-concrete-conformance.tex"),
    ("07", "sections/07-evaluation-protocol.tex"),
    ("08", "sections/08-results.tex"),
    ("09", "sections/09-discussion-threats.tex"),
    ("10", "sections/10-conclusion.tex"),
    ("DC", "sections/declarations.tex"),
]

NEG = re.compile(
    r"\b(not|no|none|neither|nor|without|cannot|never|"
    r"rather than|instead of|fails? to|remains? (?:separate|external|unvalidated)|"
    r"outside (?:the|this|that|these)|is not|are not)\b", re.I)

SCOPE = re.compile(
    r"\b(declared|frozen|selected|restricted|conditional|bounded|"
    r"within (?:the|this|these)|under (?:the|this)|"
    r"scope|boundary|post-hoc|exploratory|descriptive|"
    r"does not|do not|did not|not a|not an|only|separate(?:ly)? from|"
    r"separate(?:ly)?|beyond|outside)\b", re.I)


def read(p):
    with io.open(p, encoding="utf-8", newline="") as fh:
        return fh.read()


def strip_comments(src):
    out = []
    for line in src.split("\n"):
        out.append("" if line.lstrip().startswith("%") else line)
    return "\n".join(out)


def prose_units(src):
    """Yield (paragraph_index, sentence) for prose paragraphs only."""
    src = strip_comments(src)
    # drop float environments and math wholesale
    src = re.sub(r"\\begin\{(table|figure|tabularx|tabular|equation|align)\*?\}.*?"
                 r"\\end\{\1\*?\}", "\n", src, flags=re.S)
    src = re.sub(r"\\\[.*?\\\]", " ", src, flags=re.S)
    src = re.sub(r"\$[^$]*\$", " X ", src)
    for cmd in ("emph", "textit", "textbf", "texttt", "textrm", "textsc",
                "code", "url", "cite", "citep", "citet", "cref", "Cref",
                "ref", "label", "paragraph", "section", "subsection",
                "subsubsection"):
        src = re.sub(r"\\" + cmd + r"\*?(?=\s*\{)", "", src)
    src = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", src)
    src = src.replace("{", " ").replace("}", " ").replace("~", " ")
    src = re.sub(r"\\\\", "\n", src)

    paras = [p for p in re.split(r"\n\s*\n", src)]
    out = []
    for pi, p in enumerate(paras):
        p = re.sub(r"\s+", " ", p).strip()
        if len(p.split()) < 12:          # headings, stray fragments
            continue
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", p):
            s = s.strip()
            if len(s.split()) >= 4:
                out.append((pi, s))
    return out


def main():
    grand = []
    print("=" * 78)
    print("NEGATION AND SCOPE-LIMITING DENSITY  (prose paragraphs only)")
    print("=" * 78)
    print("%-4s %7s %8s %8s %8s %8s" %
          ("sec", "sents", "words", "neg", "neg/1k", "scope/1k"))
    for tag, rel in SECTIONS:
        path = os.path.join(PAPER, rel)
        units = prose_units(read(path))
        sents = [s for _, s in units]
        words = sum(len(s.split()) for s in sents)
        neg = sum(len(NEG.findall(s)) for s in sents)
        scope = sum(len(SCOPE.findall(s)) for s in sents)
        grand.extend(units)
        print("%-4s %7d %8d %8d %8.1f %8.1f" %
              (tag, len(sents), words, neg,
               1000.0 * neg / max(words, 1), 1000.0 * scope / max(words, 1)))

    alls = [s for _, s in grand]
    words = sum(len(s.split()) for s in alls)
    neg = sum(len(NEG.findall(s)) for s in alls)
    scope = sum(len(SCOPE.findall(s)) for s in alls)
    print("%-4s %7d %8d %8d %8.1f %8.1f" %
          ("ALL", len(alls), words, neg, 1000.0 * neg / words,
           1000.0 * scope / words))

    # ---------------------------------------------------- consecutive runs
    print("\n" + "=" * 78)
    print("CONSECUTIVE NEGATED-SENTENCE RUNS (within one paragraph)")
    print("=" * 78)
    runs = []
    for tag, rel in SECTIONS:
        units = prose_units(read(os.path.join(PAPER, rel)))
        cur = []
        last_pi = None
        for pi, s in units:
            if pi != last_pi and cur:
                runs.append((tag, cur))
                cur = []
            last_pi = pi
            if NEG.search(s):
                cur.append(s)
            else:
                if cur:
                    runs.append((tag, cur))
                cur = []
        if cur:
            runs.append((tag, cur))
    runs = [r for r in runs if len(r[1]) >= 3]
    runs.sort(key=lambda r: -len(r[1]))
    print("paragraph runs of >=3 consecutive negated sentences: %d\n" % len(runs))
    for tag, rs in runs[:12]:
        print("  [sec %s, %d consecutive]" % (tag, len(rs)))
        for s in rs:
            print("      - " + s[:180])
        print()

    # ---------------------------------------------------------- punctuation
    print("=" * 78)
    print("PUNCTUATION DENSITY (whole prose corpus)")
    print("=" * 78)
    joined = " ".join(alls)
    for ch, name in ((";", "semicolon"), (":", "colon")):
        c = joined.count(ch)
        print("  %-10s %4d   one per %5.1f words" % (name, c, words / max(c, 1)))
    print("  sentences with a semicolon: %d / %d (%.1f%%)" %
          (sum(1 for s in alls if ";" in s), len(alls),
           100.0 * sum(1 for s in alls if ";" in s) / len(alls)))
    print("  sentences with a colon:     %d / %d (%.1f%%)" %
          (sum(1 for s in alls if ":" in s), len(alls),
           100.0 * sum(1 for s in alls if ":" in s) / len(alls)))
    print("  sentences with >=2 clauses joined by ; or : or ,+which/while:")
    mult = sum(1 for s in alls if s.count(";") + s.count(":") >= 2)
    print("      %d / %d (%.1f%%)" % (mult, len(alls), 100.0 * mult / len(alls)))

    # ------------------------------------------------------------ abstract
    print("\n" + "=" * 78)
    print("ABSTRACT")
    print("=" * 78)
    src = read(os.path.join(PAPER, "main.tex"))
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", src, re.S)
    if m:
        a = m.group(1)
        a = re.sub(r"\\emph\{([^}]*)\}", r"\1", a)
        a = re.sub(r"\\[a-zA-Z]+\*?", " ", a)
        a = re.sub(r"\s+", " ", a).strip()
        sents = re.split(r"(?<=[.!?])\s+(?=[A-Z])", a)
        print("  words (whitespace tokens): %d" % len(a.split()))
        print("  sentences: %d, mean %.1f words" %
              (len(sents), sum(len(s.split()) for s in sents) / len(sents)))
        print("  longest sentence: %d words" %
              max(len(s.split()) for s in sents))
        print("  negations: %d" % len(NEG.findall(a)))
        print("\n  first sentence:\n    " + sents[0])
        print("\n  last sentence:\n    " + sents[-1])

    # ---------------------------------------------------------- paragraphs
    print("\n" + "=" * 78)
    print("PARAGRAPH LENGTHS (prose paragraphs only)")
    print("=" * 78)
    for tag, rel in SECTIONS:
        units = prose_units(read(os.path.join(PAPER, rel)))
        byp = {}
        for pi, s in units:
            byp.setdefault(pi, []).append(s)
        if not byp:
            continue
        wc = [sum(len(x.split()) for x in v) for v in byp.values()]
        print("  %-4s paragraphs=%3d  median words=%4d  max=%4d" %
              (tag, len(wc), sorted(wc)[len(wc) // 2], max(wc)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
