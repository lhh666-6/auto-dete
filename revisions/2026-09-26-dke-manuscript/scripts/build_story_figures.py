# Academic Figure Skill Typography Baseline — COPY VERBATIM, place at TOP of script
import matplotlib as mpl
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans"],
    "font.size": 8,
    "axes.titlesize": 8,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 8,
    "figure.titlesize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.6,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "legend.frameon": False,
})

# Academic Figure Skill Nature/Cell/Science Color Palette -- COPY VERBATIM
CATEGORICAL = ["#2166AC", "#B2182B", "#1B7837", "#F1A340", "#762A83", "#666666"]
CATEGORICAL_EXTENDED = [
    "#2166AC", "#B2182B", "#1B7837", "#F1A340", "#762A83", "#666666",
    "#4393C3", "#D6604D", "#5AAE61", "#B35806", "#9970AB", "#999999",
]
DIVERGING   = ["#2166AC", "#F7F7F7", "#B2182B"]
SEQUENTIAL  = ["#F7FBFF", "#6BAED6", "#08306B"]
ACCENT_RED  = "#B2182B"
GREY       = "#999999"
BLACK      = "#222222"

# Academic Figure Skill Export Baseline — COPY VERBATIM
mpl.rcParams.update({
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
    "savefig.bbox": "tight",
    "savefig.dpi": 300,
})

def save_cns_figure(fig, filename):
    """Standard Academic Figure Skill export: vector PDF + 300dpi PNG preview."""
    fig.savefig(f"{filename}.pdf", bbox_inches="tight", dpi=300)
    fig.savefig(f"{filename}.png", bbox_inches="tight", dpi=300)

from pathlib import Path
import csv
import hashlib
import json
import re
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "figures" / "refined"
DEST.mkdir(parents=True, exist_ok=True)
NAVY = "#102E65"
BLUE = "#1687DF"
ORANGE = "#DF8A23"
PALE_BLUE = "#ECF6FF"
PALE_ORANGE = "#FFF3E1"
GREEN = "#18765A"
PALE_GREEN = "#EDF7F2"
LINE = "#C8DDEC"
TEXT = "#18334E"

def canvas(title, subtitle):
    # Match the actual single-column manuscript width; retain readable print fonts.
    fig, ax = plt.subplots(figsize=(140 / 25.4, 128 / 25.4))
    fig.subplots_adjust(left=0.012, right=0.988, top=0.988, bottom=0.018)
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis("off")
    ax.text(0.014, 0.99, title, color=NAVY, size=12, weight="bold", va="top")
    ax.text(0.016, 0.938, subtitle, color=TEXT, size=8, va="top")
    return fig, ax

def card(ax, x, y, w, h, label, body="", color=BLUE, face=PALE_BLUE, label_size=8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.009,rounding_size=0.014",
                               lw=0.85, edgecolor=color, facecolor=face))
    if body:
        ax.text(x+w/2, y+h*0.72, label, ha="center", va="center", color=color,
                size=label_size, weight="bold")
        ax.text(x+w/2, y+h*0.33, body, ha="center", va="center", color=TEXT,
                size=7.7, linespacing=1.45)
    else:
        ax.text(x+w/2, y+h/2, label, ha="center", va="center", color=TEXT,
                size=label_size, linespacing=1.4)

def arrow(ax, p, q, color=BLUE, style="-|>", connection="arc3,rad=0"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=9,
                                 lw=1.15, color=color, connectionstyle=connection))

def panel(ax, x, y, label, title):
    ax.add_patch(FancyBboxPatch((x,y), .465,.365, boxstyle="round,pad=0.006,rounding_size=0.018",
                               lw=.8, edgecolor=LINE, facecolor="#FAFCFF"))
    ax.text(x+.014,y+.345,label,fontsize=13,fontweight="bold",color=NAVY,va="top")
    ax.text(x+.050,y+.340,title,fontsize=9,fontweight="bold",color=NAVY,va="top")

def footer(ax, text):
    ax.plot([.016,.984],[.053,.053],lw=1.1,color=BLUE)
    ax.text(.5,.025,text,ha="center",va="center",fontsize=8,fontweight="bold",color=NAVY)

def contract_figure():
    fig,ax=canvas("Same values, different admission histories",
                  "Preserve the reviewed proposal, authorized correction,\nand every successor field source.")
    panel(ax,.015,.515,"a","Equal values, distinct candidates")
    panel(ax,.520,.515,"b","Bind review to the exact candidate")
    panel(ax,.015,.112,"c","Commit one complete successor")
    panel(ax,.520,.112,"d","Preserve every field source")
    card(ax,.039,.677,.175,.091,"Review $c_1$","proposal 100")
    card(ax,.280,.677,.175,.091,"Final value","101",color=ORANGE,face=PALE_ORANGE)
    arrow(ax,(.219,.724),(.270,.724))
    ax.text(.244,.785,"authorize 101",color=TEXT,fontsize=7,ha="center")
    card(ax,.039,.552,.175,.075,"Admit $c_1$",color=BLUE)
    card(ax,.280,.552,.175,.075,"Substitute $c_2$",color=ORANGE,face=PALE_ORANGE)
    ax.text(.13,.641,"exact target",size=7,color=BLUE,ha="center")
    ax.text(.365,.641,"same value / context",size=7,color=ORANGE,ha="center")
    ax.text(.244,.518,"Distinct candidates; only $c_1$ was reviewed.",ha="center",size=7.5,color=TEXT)
    card(ax,.547,.674,.175,.110,"Persisted $c_1$","proposal\n100")
    card(ax,.789,.674,.175,.110,"Authorization $a$","target: exact $c_1$\nvalue: 101",color=ORANGE,face=PALE_ORANGE)
    arrow(ax,(.728,.730),(.780,.730))
    card(ax,.569,.548,.371,.065,"Correction retains 100;\nauthorization supplies 101.",
         color=BLUE,face=PALE_BLUE,label_size=7.6)
    card(ax,.039,.299,.175,.096,"Transaction","binding + principal\nfresh predecessor",label_size=8)
    card(ax,.280,.299,.175,.096,"CAS + commit","complete effects\none version",color=GREEN,face=PALE_GREEN)
    arrow(ax,(.219,.345),(.269,.345))
    arrow(ax,(.126,.294),(.126,.236),ORANGE)
    card(ax,.039,.157,.175,.069,"Fail: authoritative\nstate unchanged",color=ORANGE,face=PALE_ORANGE,label_size=7.5)
    ax.text(.366,.225,"unchanged fields",size=7.7,color=TEXT,ha="center")
    ax.text(.366,.184,"copy exact prior sources",size=7.7,color=GREEN,ha="center")
    card(ax,.547,.292,.417,.101,"Complete successor","quantity 101 → new transition\nbatch B-008 → exact prior transition",color=GREEN,face=PALE_GREEN)
    arrow(ax,(.754,.279),(.754,.253),GREEN)
    card(ax,.547,.144,.417,.100,"Reverse query","candidate $c_1$ · proposal 100\nauthorized 101",color=BLUE,face=PALE_BLUE,label_size=8)
    footer(ax,"exact candidate → bound authorization\n→ authorized value → complete successor → total field sources")
    save_cns_figure(fig,DEST/"figure-1-admission-workflow")
    fig.savefig(DEST/"figure-1-admission-workflow.svg",bbox_inches="tight")
    plt.close(fig)

def numeric_row(path, name):
    text=path.read_text(encoding="utf-8")
    row=next(s for s in text.splitlines() if s.startswith(name+" &"))
    return [int(re.sub(r"\D","",part)) for part in row.split("&")[1:]]

def evidence_figure():
    e1=ROOT/"tables/dke/comparator.tex"
    ctx=numeric_row(e1,"Context journal")
    exact=numeric_row(e1,"Exact journal")
    ref=numeric_row(e1,"Reference")
    assert ctx==[60,15,0,1020,60] and exact==ref==[45,0,15,810,0]
    e2=ROOT/"tables/dke/review.tex"
    request=numeric_row(e2,"Candidate, value, principal request substitutions")
    display=numeric_row(e2,"DOM-only substitution")
    assert request==[9,9,0] and display==[3,3,3]
    total=0
    sources=[e1,e2]
    for name in ("e3-mechanism-summary.csv","e3-ablation-summary.csv","e3-trace-summary.csv"):
        p=ROOT/"tables/supplement-current"/name
        rows=list(csv.DictReader(p.open(encoding="utf-8-sig")))
        total+=sum(int(r["n"]) for r in rows)
        sources.append(p)
    assert total==22400
    fig,ax=canvas("From admission relation to executable evidence",
                  "Each evidence layer answers a different question.\nConstructed cases and timed calls keep separate denominators.")
    panel(ax,.015,.515,"a","Five distinguishing classes")
    panel(ax,.520,.515,"b","Check relational persistence")
    panel(ax,.015,.112,"c","Isolate the binding policy")
    panel(ax,.520,.112,"d","Locate review and cost boundaries")
    labels=[("$D_C$","candidate identity + context"),("$D_V$","proposal / authorized value roles"),
            ("$D_F$","fresh predecessor"),("$D_B$","one complete successor"),
            ("$D_S$","total field-source attribution")]
    for i,(symbol,text) in enumerate(labels):
        y=.778-i*.043
        ax.text(.052,y,symbol,color=BLUE,weight="bold",fontsize=8,va="center")
        ax.text(.110,y,text,color=TEXT,fontsize=7.7,va="center")
    card(ax,.039,.542,.414,.035,"Omit a class: equal projections, distinct outcomes.",
         color=ORANGE,face=PALE_ORANGE,label_size=7)
    card(ax,.547,.704,.417,.082,"Bounded relational analysis","72 declared command outcomes",color=BLUE)
    arrow(ax,(.754,.697),(.754,.663))
    card(ax,.547,.590,.417,.064,"Persisted-state projection","9 intended · 20 mapping mutants")
    ax.text(.755,.551,"35 cases: admission, rejection, diagnosis",
            ha="center",fontsize=7.2,color=GREEN)
    ax.text(.245,.389,"E1: 15 inputs × 11 families × 3 mechanisms",ha="center",size=7.5,color=TEXT)
    card(ax,.039,.254,.190,.103,"Context journal",
         f"{ctx[1]} instance violations\n{ctx[4]} ambiguous answers",color=ORANGE,face=PALE_ORANGE)
    card(ax,.265,.254,.190,.103,"Exact + reference",
         f"{exact[1]} instance violations\n{exact[4]} ambiguous answers",color=BLUE,label_size=7.9)
    ax.text(.245,.224,"Equal-valued candidate substitution\nis the separator.",ha="center",va="top",size=7.5,color=NAVY,weight="bold")
    ax.text(.245,.162,"Under value/context policy:\nexact binding adds 15 rejections.",ha="center",va="top",size=7.5,color=TEXT)
    card(ax,.547,.283,.417,.108,"E2: 60 browser cases",
         f"request substitutions admitted: {request[1]} → {request[2]}\ndisplay-only substitutions: {display[1]} each",
         color=ORANGE,face=PALE_ORANGE)
    card(ax,.547,.155,.417,.073,f"E3: {total:,} timed observations",
         "admission · same-verifier trace access",color=BLUE,label_size=8)
    ax.text(.754,.122,"Storage footprint measured separately.",ha="center",size=7,color=TEXT)
    footer(ax,"conditional characterization → persisted checks\n→ policy separator → review and cost boundaries")
    save_cns_figure(fig,DEST/"figure-2-evidence-route")
    fig.savefig(DEST/"figure-2-evidence-route.svg",bbox_inches="tight")
    plt.close(fig)
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    (ROOT/"editorial/story-figure-source-hashes.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    contract_figure()
    evidence_figure()
    print("Two vector PDF/SVG figures and 300-dpi PNG previews generated; source counts verified.")
