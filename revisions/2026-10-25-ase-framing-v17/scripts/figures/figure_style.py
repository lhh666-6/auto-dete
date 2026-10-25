"""Shared typography and print-oriented drawing primitives.
ASE references are documented in STYLE-REFERENCES.md.
User override: white interiors, structural shapes, restrained outline accents.
"""
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
GREY        = "#999999"
BLACK       = "#222222"
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
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle, Ellipse
from matplotlib.path import Path as MplPath

PACKAGE = Path(__file__).resolve().parents[2]
FIGURES = PACKAGE / "figures"
INK = "#303332"
MUTED = "#706F69"
# User-approved revision: neutral ink/warm grey, with small ivory accents.
# Historical role variable names are retained for API compatibility only.
BLUE, RED, GREEN = "#59605F", "#6E625B", "#373E3C"
ORANGE, PURPLE, GRAY = "#C9BFA5", "#817867", "#898780"
IVORY = "#F4F0E6"
mpl.rcParams.update({"text.color": INK, "hatch.linewidth": .45})

def canvas(height_mm):
    fig, ax = plt.subplots(figsize=(150 / 25.4, height_mm / 25.4))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set(xlim=(0, 150), ylim=(0, height_mm))
    ax.axis("off")
    return fig, ax

def text(ax, x, y, value, size=8, ha="center", color=INK, weight="normal", **kwargs):
    return ax.text(x, y, value, fontsize=size, ha=ha, va="center", color=color,
                   weight=weight, linespacing=1.35, **kwargs)

def node(ax, x, y, w, h, value, kind="activity", color=INK, style="-", size=8):
    if kind == "decision":
        p = Polygon([(x,y+h/2),(x+w/2,y+h),(x+w,y+h/2),(x+w/2,y)],
                    closed=True, facecolor="white", edgecolor=color, lw=.85, ls=style)
    elif kind == "document":
        fold=3
        p=Polygon([(x,y),(x+w,y),(x+w,y+h-fold),(x+w-fold,y+h),(x,y+h)],
                  closed=True, facecolor="white", edgecolor=color, lw=.85, ls=style)
        ax.plot([x+w-fold,x+w-fold,x+w],[y+h,y+h-fold,y+h-fold],color=color,lw=.65)
    elif kind == "record":
        p=Rectangle((x,y),w,h,facecolor="white",edgecolor=color,lw=.85,ls=style)
        ax.plot([x,x+w],[y+h-5,y+h-5],color=color,lw=.55)
    else:
        p=FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0,rounding_size=2.2",
                         facecolor="white",edgecolor=color,lw=.85,ls=style)
    ax.add_patch(p)
    text(ax,x+w/2,y+h/2,value,size=size)
    return p

def record(ax,x,y,w,h,title,body,color=INK,style="-"):
    node(ax,x,y,w,h,"",kind="record",color=color,style=style)
    ax.add_patch(Rectangle((x+.2,y+h-5+.1),w-.4,4.7,facecolor=IVORY,edgecolor="none"))
    text(ax,x+w/2,y+h-2.6,title,weight="bold",color=color)
    text(ax,x+w/2,y+(h-5)/2,body)

def flow(ax, points, color=INK, style="-", width=.8):
    """Polyline with a single arrowhead; orthogonal routes are explicit."""
    p=MplPath(points,[MplPath.MOVETO]+[MplPath.LINETO]*(len(points)-1))
    ax.add_patch(FancyArrowPatch(path=p,arrowstyle="-|>",mutation_scale=8,
                                lw=width,color=color,ls=style,zorder=0))

def step(ax,x,y,label):
    ax.add_patch(Ellipse((x,y),4.5,4.5,facecolor="white",edgecolor=INK,lw=.65))
    text(ax,x,y,str(label),size=7,weight="bold")

def panel(ax,x,y,label):
    text(ax,x,y,label,size=9,weight="bold",ha="left")

FIG_TEXT_SCALE = 1.30  # artboard is 150 mm; the manuscript includes it near 122 mm

def _scale_text(fig, scale):
    for ax in fig.axes:
        for t in list(ax.texts):
            if t.get_text():
                t.set_fontsize(t.get_fontsize() * scale)
        for t in list(ax.get_xticklabels()) + list(ax.get_yticklabels()):
            if t.get_text():
                t.set_fontsize(t.get_fontsize() * scale)
        leg = ax.get_legend()
        if leg is not None:
            for t in leg.get_texts():
                t.set_fontsize(t.get_fontsize() * scale)
    for t in fig.texts:
        t.set_fontsize(t.get_fontsize() * scale)

def save_fixed(fig,name):
    """Exact 150-mm vector artboard; size/labels audited before export."""
    FIGURES.mkdir(parents=True,exist_ok=True)
    _scale_text(fig, FIG_TEXT_SCALE)
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    for ax in fig.axes:
        for t in ax.texts:
            if not t.get_text(): continue
            b=t.get_window_extent(renderer)
            if b.x0 < -1 or b.y0 < -1 or b.x1 > fig.bbox.width+1 or b.y1 > fig.bbox.height+1:
                raise ValueError(f"Text outside artboard in {name}: {t.get_text()}")
    with mpl.rc_context({"savefig.bbox":None}):
        for ext in ("pdf","svg","png"):
            fig.savefig(FIGURES/f"{name}.{ext}",bbox_inches=None,dpi=300)
    plt.close(fig)

