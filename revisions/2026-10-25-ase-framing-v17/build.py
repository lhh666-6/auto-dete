"""Compile manuscript sources with pdfLaTeX and BibTeX. Requires Python 3 and TeX."""
from pathlib import Path
import argparse
import shutil
import subprocess
import sys
import re

ROOT = Path(__file__).resolve().parent


def run(args, work, log):
    p = subprocess.run(args, cwd=work, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log.write_bytes(p.stdout)
    if p.returncode:
        print(p.stdout.decode("utf8", errors="replace")[-5000:])
        raise SystemExit(f"Build failed; see {log}")


def compile_document(work, dest, bibliography=False):
    out = work / "out"
    out.mkdir(exist_ok=True)
    args = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-output-directory=out", "main.tex"]
    run(args, work, out / "pass1.txt")
    if bibliography:
        run(["bibtex", "out/main"], work, out / "bibtex-pass.txt")
    for n in range(2, 7):
        run(args, work, out / f"pass{n}.txt")
        text = (out / 'main.log').read_text(encoding='utf8', errors='replace')
        if not re.search(r'Label\(s\) may have changed|There were undefined references|(?:Reference|Citation).*undefined|Rerun to get', text):
            break
    else:
        raise SystemExit(f"References did not settle; inspect {out / 'main.log'}")
    shutil.copy2(out / "main.pdf", dest)
    print("Built", dest.relative_to(ROOT))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf8")
    p = argparse.ArgumentParser()
    p.add_argument("--main-only", action="store_true")
    p.add_argument("--supplements-only", action="store_true")
    args = p.parse_args()
    if not args.supplements_only:
        compile_document(ROOT, ROOT/"main.pdf", True)
    if not args.main_only:
        for n in (1, 2):
            compile_document(ROOT/"supplements"/f"online-resource-{n}", ROOT/f"Online-Resource-{n}.pdf")
