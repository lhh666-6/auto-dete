#!/usr/bin/env python3
"""Four publication diagrams for the continuity revision (2026-10-07).

Run: python3 make_revision_figures.py
Output: figures/revised-figure{1..4}-*.{pdf,svg,png}

All marks and text are vector in PDF/SVG; SVG text remains editable. Fonts are
embedded in PDF. Page widths are exactly 172 mm (no tight-bounding-box resize).
Figure heights are 80, 80, 80 and 80 mm. PNGs are exported at 400 dpi.

SOURCE / CLAIM PROVENANCE
  Figure 1: main.tex, sections "Review-to-Execution Continuity" and
    "Four roles in a corrected state change", equations defining K_eq/I_eq and
    P_context/P_bound. This is an illustrative construction, not an observed run.
  Figure 2: main.tex, sections "Formal and Transactional Realization",
    "Controlled and Historical Evidence", "Prospective Online Agent Experiment".
    Evidence counts refer to separate units; they are never pooled.
  Figure 3: main.tex, shared review history, unique policy difference, feedback
    delivery, independent U/I scoring, and planned-ledger retention.
  Figure 4: evidence/online/table3-recovery.csv (actual G-bound feedback/action
    episodes), table2-continuity.csv (G substitutions and N transitions), and
    table1-outcomes.csv (planned denominators, completion, unknown coverage).
  Cross-check: evidence/online/manuscript-aggregates.json, COMPLETE frozen export.

The source validation below fails rather than silently plotting changed counts.
No interpolation, simulated observations, partial-collection recovery rates, or
pooling of the N agent-managed and G standardized-probe cohorts is used.
The frozen reference tree is never opened for writing.
"""

from pathlib import Path
import csv
import hashlib
import json
import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/kais-revision-mpl")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/kais-revision-cache")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Ellipse, Polygon, PathPatch
from matplotlib.path import Path as MplPath
import math

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "figures"
DEST.mkdir(exist_ok=True)
EVIDENCE = ROOT / "evidence" / "online"
WIDTH = 172
MM = 1 / 25.4

# Consistent accessible hierarchy: ink = ordinary process, teal = intact
# continuity/bound path, amber = a different instance (also labelled explicitly).
INK = "#18324A"
MUTED = "#536574"
LINE = "#B8C6D0"
PALE = "#F3F6F8"
BLUE = "#245B85"
BLUE_PALE = "#EAF1F7"
TEAL = "#147569"
TEAL_PALE = "#E9F4F1"
AMBER = "#995915"
AMBER_PALE = "#FBF1E3"
WHITE = "#FFFFFF"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 7.5,
    "mathtext.fontset": "dejavusans", "pdf.fonttype": 42,
    "ps.fonttype": 42, "svg.fonttype": "none", "svg.hashsalt": "kais-continuity-2026",
    "axes.unicode_minus": False, "savefig.facecolor": "white",
})


def rows(name):
    with (EVIDENCE / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def validate_sources():
    aggregate = json.loads((EVIDENCE / "manuscript-aggregates.json").read_text())
    assert aggregate["collection_status"] == "COMPLETE"
    assert aggregate["planned_arms"] == 512
    formal_path = ROOT / "evidence/formal/command_results.json"
    formal = json.loads(formal_path.read_text(encoding="utf-8-sig"))
    assert len(formal) == 72 and all(r["expected"] == r["actual"] and r["status"] == "PASS" for r in formal)
    controlled_path = ROOT / "evidence/controlled/results/e1/summary.json"
    controlled = json.loads(controlled_path.read_text(encoding="utf-8-sig"))
    assert len(controlled["arms"]) == 3 and all(r["planned"] == r["scored"] == 165 for r in controlled["arms"])
    historical_audit_path = ROOT / "evidence/final-number-verification.json"
    historical_audit = json.loads(historical_audit_path.read_text(encoding="utf-8-sig"))
    assert historical_audit["checks"]["historical_84_chains"] is True
    recovery = rows("table3-recovery.csv")
    transitions = rows("table2-continuity.csv")
    outcomes = rows("table1-outcomes.csv")
    failure_rows = rows("failure-archaeology-all-arms.csv")
    unknown_n = [r for r in failure_rows if r["scenario"] == "N" and r["I"] == "unknown"]
    assert len(unknown_n) == 2 and all(r["task_completion"] == "False" for r in unknown_n)
    g = [r for r in recovery if r["scenario"] == "G" and r["policy"] == "bound"]
    assert len(g) == 17
    assert all(r["Delivered"] == r["RecoverableReject"] == r["U"] == r["recovered"] == "True"
               and r["I"] == "1" and r["trigger_code"] == "INSTANCE_MISMATCH" for r in g)
    gb = [r for r in g if r["config_id"] == "B"]
    ga = [r for r in g if r["config_id"] == "A"]
    assert len(gb) == 16 and len(ga) == 1
    assert all(r["first_meaningful_action"] == "commit" and r["recovery_strategy"] == "reuse-reviewed" for r in gb)
    assert ga[0]["first_meaningful_action"] == "request_authorization"
    assert ga[0]["recovery_strategy"] == "reauthorization"
    for config, n in (("A", 3), ("B", 30)):
        for policy in ("context", "bound"):
            subset = [r for r in transitions if r["scenario"] == "N" and r["config_id"] == config and r["policy"] == policy]
            assert len(subset) == n
            assert all(r["same_instance"] == "True" and r["executed_substitution"] == "False" for r in subset)
    substitutions = [r for r in transitions if r["scenario"] == "G" and r["policy"] == "context" and r["executed_substitution"] == "True"]
    assert len(substitutions) == 17 and all(r["policy_admissible"] == "True" for r in substitutions)
    for policy in ("context", "bound"):
        n = next(r for r in outcomes if r["scenario"] == "N" and r["config_id"] == "B" and r["policy"] == policy)
        assert [int(n[k]) for k in ("planned", "task_completion", "integrity_1", "unknown")] == [32, 28, 31, 1]
    for config, checkpoint in (("A", 1), ("B", 16)):
        for policy in ("context", "bound"):
            r = next(r for r in outcomes if r["scenario"] == "G" and r["config_id"] == config and r["policy"] == policy)
            assert int(r["planned"]) == 16 and int(r["checkpoint_reached"]) == checkpoint
    hashes = {name: hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest()
              for name in ("manuscript-aggregates.json", "table1-outcomes.csv", "table2-continuity.csv", "table3-recovery.csv", "failure-archaeology-all-arms.csv")}
    for p in (formal_path, controlled_path, historical_audit_path):
        hashes[str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return hashes


def canvas(height):
    fig = plt.figure(figsize=(WIDTH * MM, height * MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, WIDTH), ylim=(height, 0))
    ax.set_axis_off()
    return fig, ax


def text(ax, x, y, label, size=8.0, color=INK, weight="normal", ha="center", va="center", **kwargs):
    return ax.text(x, y, label, ha=ha, va=va, color=color, fontsize=size,
                   fontweight=weight, linespacing=1.26, **kwargs)


def box(ax, x, y, w, h, fill=PALE, edge=LINE, lw=.65, radius=1.4):
    patch = FancyBboxPatch((x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=fill, edgecolor=edge, linewidth=lw)
    ax.add_patch(patch)
    return patch


def arrow(ax, start, end, color=MUTED, lw=.8, style="-|>", connectionstyle="arc3,rad=0", **kw):
    patch = FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=7,
        color=color, linewidth=lw, shrinkA=0, shrinkB=0,
        connectionstyle=connectionstyle, **kw)
    ax.add_patch(patch)
    return patch


def line(ax, points, color=LINE, lw=.7, **kw):
    ax.plot([p[0] for p in points], [p[1] for p in points], color=color, lw=lw,
            solid_capstyle="round", **kw)


def save(fig, name):
    # Preserve the exact final page dimensions: do not use bbox_inches='tight'.
    fig.savefig(DEST / f"{name}.pdf", metadata={"Title": name, "Author": "KAIS continuity revision", "Subject": "Source-validated vector scientific figure"})
    fig.savefig(DEST / f"{name}.svg")
    fig.savefig(DEST / f"{name}.png", dpi=400)
    plt.close(fig)


# Original vector icon system, drawn from geometric primitives. The supplied
# style reference is used only as a visual direction; none of its pixels or
# icon artwork are copied into the figures.
PALETTES = {
    "blue": ("#EDF5FD", "#D8E9FA", "#356799"),
    "peach": ("#FFF4EC", "#FAE3CF", "#A55C38"),
    "green": ("#EDF8F2", "#D8EEE1", "#32765A"),
    "violet": ("#F3F0FC", "#E5DFF6", "#675395"),
    "pink": ("#FCF0F7", "#F4DDED", "#984A7B"),
    "red": ("#FFF0EF", "#F7D9D6", "#B34F48"),
}


def icon(ax, kind, x, y, s=12, color=BLUE, fill=BLUE_PALE):
    def xy(u, v): return (x + u*s, y + v*s)
    def ln(a, b, lw=1.0, c=color): line(ax, [xy(*a), xy(*b)], color=c, lw=lw)
    def circ(u, v, r, fc=WHITE, ec=color, lw=.9):
        ax.add_patch(Circle(xy(u,v), r*s, facecolor=fc, edgecolor=ec, lw=lw))
    def ell(u, v, w, h, fc=WHITE, ec=color, lw=.9):
        ax.add_patch(Ellipse(xy(u,v), w*s, h*s, facecolor=fc, edgecolor=ec, lw=lw))
    def poly(points, fc=fill, ec=color, lw=.9):
        ax.add_patch(Polygon([xy(*p) for p in points], closed=True, facecolor=fc, edgecolor=ec, lw=lw, joinstyle="round"))
    def rect(u,v,w,h,fc=WHITE,ec=color,lw=.9,r=.065):
        box(ax,x+u*s,y+v*s,w*s,h*s,fc,ec,lw,r*s)
    def check(u=0,v=0,k=1,c=color):
        line(ax,[xy(u-.12*k,v),xy(u-.035*k,v+.075*k),xy(u+.13*k,v-.10*k)],color=c,lw=1.3)
    if kind == "robot":
        # Layered body, face, antenna and side housings.
        rect(-.28,.16,.56,.28,fill)
        rect(-.47,-.20,.11,.30,fill); rect(.36,-.20,.11,.30,fill)
        rect(-.37,-.30,.74,.57,fill)
        rect(-.29,-.235,.58,.36,WHITE,ec="none")
        circ(-.14,-.075,.043,fc=color,ec=color); circ(.14,-.075,.043,fc=color,ec=color)
        ln((-.09,.08),(.09,.08),1.0)
        ln((0,-.30),(0,-.44),.9); circ(0,-.48,.065,fc=fill)
        circ(-.15,.31,.026,fc=WHITE,ec=WHITE,lw=.4)
        ln((.04,.31),(.16,.31),.8,c=WHITE)
    elif kind == "reviewer":
        # Head and hair above a curved shoulder silhouette.
        path=[xy(-.38,.43),xy(-.38,.12),xy(-.18,.06),xy(0,.08),xy(.18,.06),xy(.38,.12),xy(.38,.43),xy(-.38,.43)]
        codes=[MplPath.MOVETO,MplPath.CURVE4,MplPath.CURVE4,MplPath.CURVE4,MplPath.CURVE4,MplPath.CURVE4,MplPath.CURVE4,MplPath.CLOSEPOLY]
        ax.add_patch(PathPatch(MplPath(path,codes),fc=fill,ec=color,lw=1.0))
        ell(0,-.18,.40,.49,fc=WHITE)
        poly([(-.20,-.20),(-.18,-.36),(-.08,-.43),(.08,-.43),(.18,-.34),(.20,-.20),(.09,-.28),(-.04,-.25),(-.13,-.28)],fc=color)
        ln((-.13,.14),(0,.24),.6);ln((0,.24),(.13,.14),.6)
    elif kind in ("document", "contract", "reviewed", "rejection"):
        poly([(-.29,-.42),(.12,-.42),(.31,-.23),(.31,.42),(-.29,.42)],fc=WHITE)
        poly([(.12,-.42),(.12,-.23),(.31,-.23)],fc=fill)
        ln((-.17,-.19),(.04,-.19),1.1)
        ln((-.17,-.04),(.17,-.04),.85)
        ln((-.17,.11),(.12,.11),.85)
        ln((-.17,.25),(.08,.25),.85)
        if kind in ("contract", "reviewed"):
            poly([(.10,.03),(.39,.08),(.39,.27),(.25,.43),(.10,.27)],fc=fill)
            check(.245,.21,.70)
        elif kind == "rejection":
            circ(.23,.25,.16,fc=color)
            ln((.16,.18),(.30,.32),1.05,c=WHITE);ln((.16,.32),(.30,.18),1.05,c=WHITE)
        else:
            circ(.25,.25,.16,fc=fill)
            text(ax,x+.25*s,y+.255*s,"?",max(7.5,s*.8),color,"bold")
    elif kind == "gear":
        pts=[]
        for i in range(40):
            a=math.pi*2*i/40; r=.44 if i%4 in (0,1) else .35
            pts.append((r*math.cos(a),r*math.sin(a)))
        poly(pts,fc=fill);circ(0,0,.17,WHITE)
    elif kind == "database":
        rect(-.33,-.30,.66,.60,fill,r=.02)
        ell(0,.30,.66,.22,fill)
        for yy in (-.08,.11):
            # White highlights give a layered cylinder without raster effects.
            ax.add_patch(Ellipse(xy(0,yy),.66*s,.22*s,fc="none",ec=color,lw=.7))
        ell(0,-.30,.66,.22,fill)
    elif kind == "network":
        nodes=[(-.37,.20),(-.14,-.30),(.30,-.18),(.19,.33)]
        for i,j in ((0,1),(1,2),(2,3),(3,0),(1,3)):
            ln(nodes[i],nodes[j],.9)
        for u,v in nodes:circ(u,v,.077,fill)
    elif kind == "chart":
        ln((-.38,-.03),(-.38,.40),.9);ln((-.38,.40),(.42,.40),.9)
        for u,h in ((-.24,.23),(-.01,.42),(.22,.61)):
            rect(u,.36-h,.14,h,fill,r=.01)
        line(ax,[xy(-.31,-.06),xy(-.06,-.22),xy(.18,-.28),xy(.36,-.43)],color=color,lw=1.25)
        for u,v in ((-.31,-.06),(-.06,-.22),(.18,-.28),(.36,-.43)):circ(u,v,.035,WHITE,lw=.8)
    elif kind == "feedback":
        poly([(-.40,-.30),(.40,-.30),(.40,.19),(-.05,.19),(-.24,.38),(-.24,.19),(-.40,.19)],fc=WHITE)
        for u in (-.19,0,.19):circ(u,-.055,.033,fc=color,ec=color)
    elif kind == "reuse":
        for start in (35,215):
            aa=[math.radians(start+i*145/24) for i in range(25)]
            pp=[xy(.29*math.cos(a),.29*math.sin(a)) for a in aa]
            line(ax,pp[:-2],color=color,lw=1.05)
            arrow(ax,pp[-3],pp[-1],color,lw=1.05)
        check(0,0,.72)
    elif kind == "check":
        circ(0,0,.38,fc=color,ec=color)
        check(0,0,1.4,c=WHITE)
    elif kind == "copy":
        rect(-.34,-.39,.48,.62,fill,r=.025)
        rect(-.10,-.19,.48,.62,WHITE,r=.025)
        ln((.00,-.02),(.26,-.02),.8);ln((.00,.13),(.26,.13),.8);ln((.00,.27),(.16,.27),.8)


def stage_card(ax,x,y,w,h,palette):
    fill, band, accent=PALETTES[palette]
    # A restrained offset shadow distinguishes layers at publication size.
    box(ax,x+.4,y+.5,w,h,fill="#E5EAF0",edge="none",radius=2)
    box(ax,x,y,w,h,fill=fill,edge=band,lw=.75,radius=2)
    return fill,band,accent


def chevron(ax,x,y,w,h,fill,edge="none"):
    ax.add_patch(Polygon([(x,y),(x+w-2,y),(x+w,y+h/2),(x+w-2,y+h),(x,y+h),(x+1.1,y+h/2)],
        closed=True,fc=fill,ec=edge,lw=.65,joinstyle="round"))


def ribbon(ax,x0,y0,x1,y1,width,color,edge=None):
    c=(x1-x0)*.55
    verts=[(x0,y0-width/2),(x0+c,y0-width/2),(x1-c,y1-width/2),(x1,y1-width/2),
           (x1,y1+width/2),(x1-c,y1+width/2),(x0+c,y0+width/2),(x0,y0+width/2),(x0,y0-width/2)]
    codes=[MplPath.MOVETO,MplPath.CURVE4,MplPath.CURVE4,MplPath.CURVE4,MplPath.LINETO,
           MplPath.CURVE4,MplPath.CURVE4,MplPath.CURVE4,MplPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MplPath(verts,codes),fc=color,ec=edge or color,lw=.6,alpha=.90,zorder=1))


def figure1():
    fig,ax=canvas(80)
    specs=[(3,"blue","1  Machine\nproposal","robot"),
           (46,"peach","2  Authorized\ncorrection","reviewer"),
           (89,"violet","3  Reviewed\ninstance","reviewed"),
           (132,"green","4  Executed\ntransition","gear")]
    for x,pal,title,kind in specs:
        fill,band,accent=stage_card(ax,x,3,37,57,pal)
        box(ax,x+1.2,4.2,34.6,12.5,band,"none",radius=1.25)
        text(ax,x+18.5,10.4,title,8.3,accent,"bold")
        if kind=="gear":
            icon(ax,"gear",x+12.0,28,11,accent,band)
            icon(ax,"database",x+25.7,28,11,accent,band)
        else: icon(ax,kind,x+18.5,28,13,accent,band)
        box(ax,x+3,39,31,17.7,WHITE,band,lw=.7,radius=1.3)
    text(ax,21.5,44.9,r"$x_c=100$",10.2,BLUE,"bold")
    text(ax,21.5,52.1,"origin candidate c₁",7.5,MUTED)
    text(ax,64.5,44.9,r"$x_a=101$",10.2,PALETTES["peach"][2],"bold")
    text(ax,64.5,52.1,"explicit grant a",7.5,MUTED)
    text(ax,107.5,44.9,r"$c_r=c_1$",10.2,PALETTES["violet"][2],"bold")
    text(ax,107.5,52.1,"identity fixed by a",7.5,MUTED)
    text(ax,150.5,44.5,r"$c_s=c_1$ → 101",8.6,TEAL,"bold")
    text(ax,150.5,52.1,r"$c_s=c_2$ → 101",8.6,AMBER,"bold")
    for x in (40.7,83.7,126.7):
        chevron(ax,x,27,4.6,5.4,"#A6BDCC")
    box(ax,3,65,166,12.5,"#F9F3EE","#E8D4C5",radius=1.5)
    text(ax,86,69.1,"Same proposal value + retained context  ⇏  same instance",8.6,INK,"bold")
    text(ax,86,74.3,"Original grant: context admits c₁ or c₂; bound admits only c₁.",7.7,MUTED)
    save(fig,"revised-figure1-concept")


def figure2():
    fig,ax=canvas(80)
    data=[("blue","Problem","document","Execution may\nuse a different\ninstance","Same value;\ndifferent identity"),
          ("green","Contract","contract","Four roles +\nadmission checks","Value, identity,\nfreshness, sources"),
          ("peach","Formal +\ntransactional","network","Bounded model\n+ atomic\npersistence","72 commands;\nindependent audit"),
          ("violet","Controlled +\nhistorical","chart","Mechanism tests\n+ persisted chains","165 cases per\nmechanism;\n84 correction\nchains"),
          ("pink","Prospective\nonline","robot","Paired live\ncontinuations","512 planned\narms; feedback\nto action")]
    for i,(pal,title,kind,core,unit) in enumerate(data):
        x=3+i*34.2
        fill,band,accent=stage_card(ax,x,4,29.2,60.5,pal)
        chevron(ax,x+.4,4.4,30.1,12.6,band)
        text(ax,x+14.6,10.7,title,7.7,accent,"bold")
        icon(ax,kind,x+14.6,29,12.5,accent,band)
        text(ax,x+14.6,41.5,core,7.5,INK,"bold")
        box(ax,x+1.7,49,25.8,14.5,WHITE,band,lw=.6,radius=1)
        text(ax,x+14.6,56.8,unit,7.5,MUTED)
        if i<4: arrow(ax,(x+29.7,30),(x+33.4,30),"#7F9BAF",lw=.85)
    chevron(ax,3,69,166,8.5,"#E5EFF8")
    text(ax,86,73.25,"Specify the relation  →  make it executable  →  test it  →  observe continuation",8.0,BLUE,"bold")
    save(fig,"revised-figure2-evidence-chain")


def figure3():
    fig,ax=canvas(80)
    box(ax,3,2.5,67,8.5,PALETTES["blue"][1],"none",radius=1.4)
    text(ax,36.5,6.75,"Shared prospective history",8.2,BLUE,"bold")
    box(ax,81,2.5,88,8.5,PALETTES["green"][1],"none",radius=1.4)
    text(ax,125,6.75,"Isolated policy continuations",8.2,TEAL,"bold")
    for x,w,pal,kind,title,detail in [(3,28,"blue","robot","Agent proposal","task + tools"),
                                  (38,32,"peach","gear","Host review +\ncheckpoint","copy history + state")]:
        fill,band,accent=stage_card(ax,x,15,w,42,pal)
        icon(ax,kind,x+w/2,28,12.5,accent,band)
        if kind=="gear": icon(ax,"reviewed",x+w/2+5.5,31.5,6.3,accent,band)
        text(ax,x+w/2,41,title,7.7,accent,"bold")
        box(ax,x+1.5,47,w-3,7.5,WHITE,band,lw=.6,radius=1)
        text(ax,x+w/2,50.75,detail,7.5,MUTED)
    chevron(ax,31.7,31,5.3,5.4,"#A6BDCC")
    line(ax,[(75,15),(75,58)],LINE,.6,linestyle=(0,(2.5,3)))
    line(ax,[(70.6,35),(78,35),(78,24)])
    line(ax,[(78,35),(78,49)])
    arrow(ax,(78,24),(80,24),PALETTES["violet"][2]);arrow(ax,(78,49),(80,49),TEAL)
    for y,pal,title,formula in [(14,"violet","Context",r"$G\wedge K_{eq}$"),(39,"green","Bound",r"$G\wedge K_{eq}\wedge I_{eq}$")]:
        fill,band,accent=stage_card(ax,81,y,37,20,pal)
        icon(ax,"document" if title=="Context" else "contract",87.5,y+10,7.5,accent,band)
        text(ax,106,y+5.6,title,8.0,accent,"bold")
        text(ax,106,y+13.4,formula,8.5,accent)
    arrow(ax,(118.7,24),(129,26),PALETTES["violet"][2],lw=.9)
    arrow(ax,(118.7,49),(129,34),TEAL,lw=.9)
    fill,band,accent=stage_card(ax,130,17,39,22,"blue")
    text(ax,149.5,21.8,"Actual feedback",8.2,accent,"bold")
    icon(ax,"feedback",136.5,30.5,8,accent,band)
    text(ax,155,31,"tool result to\nmodel response",7.5,MUTED)
    fill,band,accent=stage_card(ax,130,48,39,22,"green")
    text(ax,149.5,52.8,"Next agent action",8.2,accent,"bold")
    icon(ax,"robot",137,61,8,accent,band)
    text(ax,155.5,61.4,"meaningful\ntool choice",7.5,MUTED)
    arrow(ax,(149.5,40),(149.5,47),TEAL,lw=1)
    line(ax,[(169,61),(171,61),(171,13),(149.5,13)],TEAL,.65)
    arrow(ax,(149.5,13),(149.5,16),TEAL,lw=.65)
    # The loop returns actual results of further tool actions. The path and
    # oracle boxes describe recorded trajectories, not prescribed repairs.
    box(ax,81,66,37,11,PALETTES["violet"][0],PALETTES["violet"][1],radius=1.4)
    text(ax,99.5,71.5,"Observed path",8.2,PALETTES["violet"][2],"bold")
    line(ax,[(129,61),(124,61),(124,71.5)],TEAL,.85)
    arrow(ax,(124,71.5),(119,71.5),TEAL,.85)
    box(ax,38,66,32,11,PALETTES["green"][0],PALETTES["green"][1],radius=1.4)
    text(ax,54,71.5,r"$(U,I)$ oracle",8.7,TEAL,"bold")
    arrow(ax,(80,71.5),(71,71.5),TEAL,.85)
    text(ax,17,70.8,"All planned arms\nstay in the ledger",7.5,MUTED)
    save(fig,"revised-figure3-online-loop")


def figure4():
    fig,ax=canvas(80)
    text(ax,3,5.5,"G  |  Standardized queued handoff",9.0,BLUE,"bold",ha="left")
    text(ax,3,11.3,"Observed responses to delivered bound feedback",7.8,MUTED,ha="left")
    # Ribbon widths are proportional to the observed counts: 16:1. Their
    # geometry changes only for routing; there are exactly two observed paths.
    ribbon(ax,28,31.5,47,28.5,10.4,"#C0DBF3","#9ABDE1")
    ribbon(ax,28,48,47,53.5,.65,"#C5B9E9","#8E7ABC")
    ribbon(ax,92,28.5,107,38,10.4,"#C0DBF3","#9ABDE1")
    ribbon(ax,92,53.5,107,48.6,.65,"#C5B9E9","#8E7ABC")
    fill,band,accent=stage_card(ax,3,21,25,36,"red")
    icon(ax,"rejection",15.5,32.5,12,accent,band)
    text(ax,15.5,45,"17",14.5,accent,"bold")
    text(ax,15.5,52,"rejections",7.8,accent,"bold")
    for y,pal,title,detail,kind in [(20,"blue","B: 16 reuse paths","commit reviewed c₁","reuse"),
                                  (45,"violet","A: 1 reauthorization","authorize c₂ → commit","reviewed")]:
        fill,band,accent=stage_card(ax,47,y,45,17,pal)
        icon(ax,kind,53.5,y+8.5,8.7,accent,band)
        text(ax,74,y+5.3,title,7.6,accent,"bold")
        text(ax,74,y+12,detail,7.5,MUTED)
    text(ax,117,20,"Outcome",7.8,TEAL,"bold")
    fill,band,accent=stage_card(ax,107,27,20,32,"green")
    icon(ax,"check",117,34.8,8.3,TEAL,band)
    text(ax,117,45.2,"17/17",10.4,TEAL,"bold")
    text(ax,117,53.2,r"$(U,I)=(1,1)$",7.5,TEAL)
    text(ax,3,68.6,"Paired context: 17 accepted substitutions (I = 0).",7.5,MUTED,ha="left")
    text(ax,3,75,"17/32 G pairs exposed; 15 A prefix failures retained.",7.5,MUTED,ha="left")
    fill,band,accent=stage_card(ax,133,3,36,74,"green")
    box(ax,134.2,4.2,33.6,12.5,band,"none",radius=1.25)
    text(ax,151,10.4,"N  |  Refreshed\npreview",8.0,accent,"bold")
    icon(ax,"robot",151,25,12,accent,band)
    text(ax,151,37.6,"0 observed\nsubstitutions",8.7,TEAL,"bold")
    line(ax,[(136,44.5),(166,44.5)],"#B2D8C1",.7)
    text(ax,151,50.7,"Exact transitions\nper policy: B 30; A 3",7.5,INK)
    text(ax,151,59.1,"B / policy (32 arms):",7.5,INK,"bold")
    text(ax,151,68.4,"28 U = 1, I = 1;\n3 U = 0, I = 1;\n1 U = 0, I unknown.",7.5,MUTED)
    save(fig,"revised-figure4-recovery-paths")


if __name__ == "__main__":
    hashes = validate_sources()
    for fn in (figure1, figure2, figure3, figure4):
        fn()
    audit = {"width_mm": WIDTH, "heights_mm": [80, 80, 80, 80],
             "minimum_base_font_pt": 7.5, "math_subscripts_use_conventional_smaller_size": True,
             "png_dpi": 400, "source_sha256": hashes,
             "data_validation": "passed", "figure_count": 4,
             "observed_G_bound_paths": {"B_reuse": 16, "A_reauthorization": 1, "joint_1_1": 17},
             "ribbon_width_ratio": "16:1, proportional to delivered G-bound episode counts",
             "N_exact_transitions_per_policy": {"A": 3, "B": 30},
             "N_unknown_runs": {"count": 2, "utility": 0, "integrity": "unknown"},
             "outputs": [str(p.relative_to(ROOT)) for p in sorted(DEST.glob("revised-figure[1-4]-*"))
                         if p.suffix in {".pdf", ".svg", ".png"}]}
    (DEST / "revised-figure-source-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))
