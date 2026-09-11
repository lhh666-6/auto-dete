"""Read-only style probe for the Auto-Decte manuscript.

Extracts approximate plain text from the LaTeX sources and reports:
  - sentence / word statistics per file and overall
  - exact literal occurrence counts for hedging, negation and AI-tell lexemes
  - the longest sentences, with their location, for manual inspection

Nothing is written except stdout.  This tool never modifies the manuscript.
"""

import io
import os
import re
import sys

PAPER = os.environ.get(
    "AUTODECTE_PAPER",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "latest", "paper"),
)

SECTIONS = [
    "main.tex",
    "sections/01-introduction.tex",
    "sections/02-related-work.tex",
    "sections/03-problem-contract.tex",
    "sections/04-relational-analysis.tex",
    "sections/05-transactional-realization.tex",
    "sections/06-formal-concrete-conformance.tex",
    "sections/07-evaluation-protocol.tex",
    "sections/08-results.tex",
    "sections/09-discussion-threats.tex",
    "sections/10-conclusion.tex",
    "sections/declarations.tex",
]

# ---------------------------------------------------------------- extraction

VERBATIM = re.compile(r"\\begin\{(verbatim|lstlisting)\}.*?\\end\{\1\}", re.S)


def read(path):
    with io.open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def strip_comments(src):
    out = []
    for line in src.split("\n"):
        if line.lstrip().startswith("%"):
            out.append("")
            continue
        # remove trailing comments, honouring a single backslash escape
        i = 0
        cut = len(line)
        while i < len(line):
            if line[i] == "\\":
                i += 2
                continue
            if line[i] == "%":
                cut = i
                break
            i += 1
        out.append(line[:cut])
    return "\n".join(out)


def to_text(src):
    """Very small LaTeX -> rough prose converter (approximate by design)."""
    t = strip_comments(src)
    t = VERBATIM.sub(" ", t)
    t = re.sub(r"\\begin\{(equation|align|table|figure|tabularx|tabular|description|enumerate|itemize)\*?\}.*?"
               r"\\end\{\1\*?\}", " ", t, flags=re.S)
    t = re.sub(r"\\\[.*?\\\]", " ", t, flags=re.S)
    t = re.sub(r"\$[^$]*\$", " X ", t)
    # keep the argument of these, drop the command
    for cmd in ("emph", "textit", "textbf", "texttt", "textrm", "textsc",
                "code", "url", "caption", "paragraph", "section", "subsection",
                "subsubsection", "title"):
        t = re.sub(r"\\" + cmd + r"\*?(?=\s*\{)", "", t)
    t = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", t)
    t = t.replace("{", " ").replace("}", " ").replace("~", " ")
    t = re.sub(r"\\\\", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


# ------------------------------------------------------------ sentence split

ABBREV = ["e.g.", "i.e.", "cf.", "vs.", "Fig.", "Eq.", "No.", "et al.",
          "Supplement S", "S1.", "S2.", "S3.", "S4.", "S5.", "v8.", "v2.1",
          "Inc.", "Ltd.", "pp.", "vol.", "Sec.", "Ref.", "approx."]


def split_sentences(text):
    guarded = text
    for k, ab in enumerate(ABBREV):
        guarded = guarded.replace(ab, "\x00%d\x00" % k)
    guarded = re.sub(r"(\d)\.(\d)", lambda m: m.group(1) + "\x01" + m.group(2), guarded)
    parts = re.split(r"(?<=[.!?])\s+", guarded)
    out = []
    for k, ab in enumerate(ABBREV):
        parts = [p.replace("\x00%d\x00" % k, ab) for p in parts]
    return [p.replace("\x01", ".").strip() for p in parts if p.strip()]


# -------------------------------------------------------------- lexicon hits

# exact literal substrings; case-sensitive unless noted
LEXICON = {
    "NEGATION / SCOPE": [
        "rather than", "not a ", "not an ", "does not", "do not", "did not",
        "is not", "are not", "cannot", "no ", "neither", "without ",
        "outside the", "beyond", "does not by itself",
        "not a substitute", "is not a claim", "does not establish",
        "does not entail", "does not certify", "does not address",
        "remains separate", "remain external", "external assumption",
        "remains unvalidated", "not independent",
    ],
    "HEDGES": [
        "may ", "might ", "could ", "would ", "should ", "possibly",
        "likely", "arguably", "tends to", "may or may not",
        "it is possible", "potentially", "somewhat", "to some extent",
    ],
    "EPISTEMIC LABELS": [
        "declared", "frozen", "scope", "boundary", "conditional",
        "descriptive", "post-hoc", "exploratory", "selected", "restricted",
    ],
    "BOOSTERS": [
        "clearly", "obviously", "evidently", "undoubtedly", "crucial",
        "essential", "fundamental", "significantly", "very ", "quite ",
        "remarkably", "substantially",
    ],
    "AI TELLS": [
        "delve", "intricate", "nuanced", "pivotal", "leverage", "robust",
        "multifaceted", "commendable", "seamless", "cutting-edge",
        "groundbreaking", "revolutionary", "unprecedented", "transformative",
        "state-of-the-art", "holistic", "paradigm", "realm", "landscape",
        "underscore", "showcase", "myriad", "comprehensive", "meticulous",
        "Furthermore", "Moreover", "Additionally", "Notably",
        "It is worth noting", "In conclusion", "In summary", "To summarize",
        "Taken together", "Overall,", "In recent years",
        "With the rapid development", "To the best of our knowledge",
        "As mentioned earlier", "As discussed above", "As previously stated",
    ],
    "CONNECTIVES": ["Thus,", "Therefore,", "Hence,", "Consequently,",
                    "Accordingly,", "Because ", "Since ", "while ",
                    "whereas ", "although ", "however", "but "],
    "PUNCTUATION": ["---", ";", ":", ":"],
}


def count_literal(text, needle):
    return text.count(needle)


def main():
    overall = []
    rows = []
    all_sentences = []

    for rel in SECTIONS:
        path = os.path.join(PAPER, rel)
        if not os.path.exists(path):
            print("MISSING: " + path)
            continue
        src = read(path)
        raw_words = len(re.findall(r"[A-Za-z][A-Za-z'\-]*", strip_comments(src)))
        txt = to_text(src)
        sentences = split_sentences(txt)
        lens = [len(s.split()) for s in sentences]
        rows.append((rel, len(sentences), raw_words,
                     (sum(lens) / len(lens)) if lens else 0.0,
                     max(lens) if lens else 0))
        overall.append(txt)
        for s in sentences:
            all_sentences.append((rel, len(s.split()), s))

    full = " ".join(overall)

    print("=" * 78)
    print("SENTENCE / WORD STATISTICS   (approximate text extraction)")
    print("=" * 78)
    print("%-42s %6s %7s %7s %6s" % ("file", "sents", "words", "mean", "max"))
    tot_s = tot_w = 0
    for rel, ns, nw, mean, mx in rows:
        print("%-42s %6d %7d %7.1f %6d" % (rel, ns, nw, mean, mx))
        tot_s += ns
        tot_w += nw
    print("%-42s %6d %7d" % ("TOTAL", tot_s, tot_w))

    lens = sorted((l for _, l, _ in all_sentences))
    n = len(lens)
    print("\nsentence length distribution (n=%d)" % n)
    for pct in (50, 75, 90, 95, 99):
        idx = min(int(round(pct / 100.0 * n)), n - 1)
        print("  p%-3d = %2d words" % (pct, lens[idx]))
    for thresh in (40, 50, 60, 70):
        c = sum(1 for l in lens if l >= thresh)
        print("  sentences >= %2d words: %4d  (%.1f%%)" % (thresh, c, 100.0 * c / n))

    print("\n" + "=" * 78)
    print("LEXICON COUNTS   (exact literal occurrences, whole manuscript)")
    print("=" * 78)
    for group, items in LEXICON.items():
        print("\n--- %s" % group)
        hits = []
        for it in items:
            c = count_literal(full, it)
            if c:
                hits.append((c, it))
        hits.sort(reverse=True)
        total = sum(c for c, _ in hits)
        print("    group total: %d occurrences over %d distinct forms"
              % (total, len(hits)))
        for c, it in hits:
            print("    %5d  %r" % (c, it.strip()))

    print("\n" + "=" * 78)
    print("LONGEST SENTENCES")
    print("=" * 78)
    for rel, l, s in sorted(all_sentences, key=lambda x: -x[1])[:25]:
        print("\n[%3d words] %s" % (l, rel))
        print("   " + s[:1500])

    print("\n" + "=" * 78)
    print("SENTENCE-OPENING REPETITION (first two words)")
    print("=" * 78)
    opens = {}
    for _, _, s in all_sentences:
        w = s.split()[:2]
        if len(w) == 2:
            k = " ".join(w)
            opens[k] = opens.get(k, 0) + 1
    for k, v in sorted(opens.items(), key=lambda x: -x[1])[:25]:
        if v >= 3:
            print("  %4d  %s ..." % (v, k))

    return 0


if __name__ == "__main__":
    sys.exit(main())
