"""Convert the reviewed Markdown draft to an Elsevier LaTeX working draft.

The Markdown manuscript remains the prose source. This script only changes
formatting; it does not generate or alter scientific content.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "manuscript.md"
TARGET = ROOT / "manuscript.tex"

TOKEN = re.compile(r"(\$[^$]+\$|\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|\*[^*]+\*)")
IMAGE = re.compile(r"^!\[[^\]]*\]\(([^)]+)\)$")
CAPTION = re.compile(r"^\*\*(Figure|Table) (\d+)\.\*\* (.+)$")
HEADING = re.compile(r"^(#{1,3}) (.+)$")
NUMBER = re.compile(r"^\d+(?:\.\d+)?\.\s+")
CITATIONS = {
    "https://www.research.ed.ac.uk/en/publications/why-and-where-a-characterization-of-data-provenance/": "buneman2001why",
    "https://www.research.ed.ac.uk/en/publications/provenance-management-in-curated-databases/": "buneman2006curated",
    "https://arxiv.org/abs/cs/0612127": "eltabakh2006bdbms",
    "https://www.cs.uic.edu/~bglavic/dbgroup/bibliography/AG17c.html": "arab2018reenactment",
    "https://www.w3.org/TR/prov-dm/": "w3c2013prov",
}


def escape_plain(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def inline(value: str) -> str:
    parts: list[str] = []
    last = 0
    for match in TOKEN.finditer(value):
        parts.append(escape_plain(value[last : match.start()]))
        token = match.group()
        if token.startswith("$"):
            parts.append(token)
        elif token.startswith("["):
            label, url = token[1:-1].split("](", 1)
            if url in CITATIONS:
                if label.startswith(("Buneman et al.", "Arab et al.")):
                    parts.append(r"\citet{" + CITATIONS[url] + "}")
                else:
                    parts.append(inline(label) + r"~\citep{" + CITATIONS[url] + "}")
            else:
                parts.append(r"\href{" + url + "}{" + inline(label) + "}")
        elif token.startswith("**"):
            parts.append(r"\textbf{" + inline(token[2:-2]) + "}")
        else:
            parts.append(r"\emph{" + inline(token[1:-1]) + "}")
        last = match.end()
    parts.append(escape_plain(value[last:]))
    result = "".join(parts)
    result = re.sub(r"\bFig\. ([1-4])\b", r"Fig.~\\ref{fig:\1}", result)
    result = re.sub(r"\bTable ([12])\b", r"Table~\\ref{tab:\1}", result)
    return result


def table_lines(rows: list[str], caption: str, number: int) -> list[str]:
    parsed = [[cell.strip() for cell in row.strip().strip("|").split("|")] for row in rows]
    headers = parsed[0]
    body = parsed[2:]
    assert number in (1, 2)
    assert len(headers) == (3 if number == 1 else 5)
    assert all(len(row) == len(headers) for row in body)
    layout = (
        r"@{}>{\raggedright\arraybackslash}p{0.23\linewidth}"
        r">{\raggedright\arraybackslash}X>{\raggedright\arraybackslash}X@{}"
        if number == 1
        else r"@{}>{\raggedright\arraybackslash}p{0.21\linewidth}"
        r"*{4}{>{\centering\arraybackslash}p{0.165\linewidth}}@{}"
    )
    begin_tabular = (r"\begin{tabularx}{\linewidth}{" if number == 1 else r"\begin{tabular}{")
    end_tabular = r"\end{tabularx}" if number == 1 else r"\end{tabular}"
    output = [
        r"\begin{table}[tbp]",
        r"\caption{" + inline(caption) + "}",
        r"\label{tab:" + str(number) + "}",
        r"\centering",
        r"\footnotesize",
        begin_tabular + layout + "}",
        r"\toprule",
        " & ".join(inline(cell) for cell in headers) + r" \\",
        r"\midrule",
    ]
    output.extend(" & ".join(inline(cell) for cell in row) + r" \\" for row in body)
    output.extend([r"\bottomrule", end_tabular, r"\end{table}", ""])
    return output


def figure_lines(path: str, caption: str, number: int) -> list[str]:
    pdf_path = path.removesuffix(".png") + ".pdf"
    assert (ROOT / pdf_path).is_file(), pdf_path
    return [
        r"\begin{figure}[!htbp]",
        r"\centering",
        r"\includegraphics[width=\linewidth]{" + pdf_path.replace("\\", "/") + "}",
        r"\caption{" + inline(caption) + "}",
        r"\label{fig:" + str(number) + "}",
        r"\end{figure}",
        "",
    ]


def convert() -> str:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    assert lines and lines[0].startswith("# ")
    title = lines[0][2:]
    output = [
        r"\documentclass[preprint,12pt,authoryear]{elsarticle}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{lmodern}",
        r"\usepackage{amsmath,amssymb}",
        r"\usepackage{booktabs,tabularx,array}",
        r"\usepackage{graphicx}",
        r"\usepackage{flafter}",
        r"\usepackage{placeins}",
        r"\usepackage{microtype}",
        r"\usepackage[hidelinks]{hyperref}",
        r"\renewcommand{\topfraction}{0.9}",
        r"\renewcommand{\bottomfraction}{0.8}",
        r"\renewcommand{\textfraction}{0.05}",
        r"\renewcommand{\floatpagefraction}{0.8}",
        r"\setlength{\emergencystretch}{2em}",
        r"\journal{Data \& Knowledge Engineering}",
        r"\begin{document}",
        r"\begin{frontmatter}",
        r"\title{" + inline(title) + "}",
        r"\begin{abstract}",
    ]
    paragraph: list[str] = []
    abstract = True
    math = False
    i = 2

    def flush() -> None:
        if paragraph:
            output.append(inline(" ".join(paragraph)))
            output.append("")
            paragraph.clear()

    while i < len(lines):
        line = lines[i]
        if line == "$$":
            flush()
            output.append(r"\[" if not math else r"\]")
            math = not math
            i += 1
            continue
        if math:
            output.append(line)
            i += 1
            continue
        if not line.strip():
            flush()
            i += 1
            continue
        heading = HEADING.match(line)
        if heading:
            flush()
            level, text = heading.groups()
            if text == "Abstract":
                i += 1
                continue
            if abstract:
                output.extend([r"\end{abstract}", r"\end{frontmatter}", ""])
                abstract = False
            if level == "##":
                if text == "8. Data and knowledge engineering implications":
                    output.append(r"\FloatBarrier")
                if text in (
                    "Artifact availability",
                    "Declaration of generative AI and AI-assisted technologies in manuscript preparation",
                ):
                    output.append(r"\section*{" + inline(text) + "}")
                else:
                    output.append(r"\section{" + inline(NUMBER.sub("", text)) + "}")
            elif level == "###":
                output.append(r"\subsection{" + inline(NUMBER.sub("", text)) + "}")
            else:
                raise ValueError(f"Unexpected heading: {line}")
            output.append("")
            i += 1
            continue
        image = IMAGE.match(line)
        if image:
            flush()
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            match = CAPTION.match(lines[j]) if j < len(lines) else None
            assert match and match.group(1) == "Figure", f"Missing figure caption after line {i+1}"
            output.extend(figure_lines(image.group(1), match.group(3), int(match.group(2))))
            i = j + 1
            continue
        if line.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            match = CAPTION.match(lines[i]) if i < len(lines) else None
            assert match and match.group(1) == "Table", f"Missing table caption after line {i+1}"
            output.extend(table_lines(rows, match.group(3), int(match.group(2))))
            i += 1
            continue
        if CAPTION.match(line):
            raise ValueError(f"Unpaired caption: {line}")
        paragraph.append(line.strip())
        i += 1

    flush()
    assert not math and not abstract
    output.extend([r"\bibliographystyle{elsarticle-harv}", r"\bibliography{references}", r"\end{document}", ""])
    rendered = "\n".join(output)
    assert rendered.count(r"\begin{figure}") == 4
    assert rendered.count(r"\begin{table}") == 2
    assert rendered.count(r"\begin{abstract}") == 1
    return rendered


if __name__ == "__main__":
    TARGET.write_text(convert(), encoding="utf-8", newline="\n")
    print(f"Wrote {TARGET}")
