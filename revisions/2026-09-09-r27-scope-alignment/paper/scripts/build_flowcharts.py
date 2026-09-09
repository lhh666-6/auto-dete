# Academic Figure Skill Asset Confirmation (verified against assets/figures/)
# Figure 1: admission schematic -> no semantically matching statistical asset -> param inherit from prior verified vector builder
# Figure 2: evidence map -> no semantically matching statistical asset -> param inherit from prior verified vector builder
# Existing source PDF previews inspected; no raster content is embedded.
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
    "pdf.fonttype": 42,         # TrueType font embedding
    "svg.fonttype": "none",     # editable text in SVG
    "savefig.bbox": "tight",    # trim whitespace
    "savefig.dpi": 300,
})

def save_cns_figure(fig, filename):
    """Standard Academic Figure Skill export: vector PDF + 300dpi PNG preview."""
    fig.savefig(f"{filename}.pdf", bbox_inches="tight", dpi=300)
    fig.savefig(f"{filename}.png", bbox_inches="tight", dpi=300)

from pathlib import Path
import json
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures/refined'
OUT.mkdir(exist_ok=True)
BLUE, PURPLE, GREEN = '#2166AC', '#762A83', '#1B7837'
INK, MUTED = '#222222', '#555555'
BLUE_BG, PURPLE_BG, GREEN_BG = '#EDF4FA', '#F4EFF8', '#EEF6F0'
ORANGE_BG, GREY_BG, RED_BG = '#FCF3E8', '#F3F5F6', '#FAEDF0'


def canvas(height):
    fig = plt.figure(figsize=(6, height / 30))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, 180), ylim=(0, height))
    ax.axis('off')
    return fig, ax


def box(ax, x, y, w, h, fill, edge='none'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=1.2',
        facecolor=fill,edgecolor=edge,linewidth=.65))
    if not hasattr(ax,'qa_boxes'):ax.qa_boxes=[]
    ax.qa_boxes.append((x,y,w,h))


def label(ax,x,y,s,size=8.5,bold=False,color=INK,ha='center',va='center'):
    return ax.text(x,y,s,fontsize=size,fontweight='bold' if bold else 'normal',
        color=color,ha=ha,va=va,linespacing=1.25)


def arrow(ax,a,b,color=MUTED,dashed=False):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=9,
        linewidth=1.0,color=color,linestyle=(0,(3,2)) if dashed else '-',
        shrinkA=0,shrinkB=0))


def export(fig,stem):
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    errors=[]
    texts=[t for ax in fig.axes for t in ax.texts]
    for t in texts:
        b=t.get_window_extent(renderer)
        if not (b.x0>=-1 and b.y0>=-1 and b.x1<=fig.bbox.x1+1 and b.y1<=fig.bbox.y1+1):
            errors.append('Outside figure: '+t.get_text())
        x,y=t.get_position()
        containing=[q for q in getattr(t.axes,'qa_boxes',[]) if q[0]<x<q[0]+q[2] and q[1]<y<q[1]+q[3]]
        if containing:
            q=min(containing,key=lambda q:q[2]*q[3])
            low=t.axes.transData.transform((q[0],q[1]));high=t.axes.transData.transform((q[0]+q[2],q[1]+q[3]))
            if b.x0<low[0]-1 or b.x1>high[0]+1 or b.y0<low[1]-1 or b.y1>high[1]+1:
                errors.append('Outside card: '+t.get_text())
    for i,t in enumerate(texts):
        b=t.get_window_extent(renderer)
        for other in texts[i+1:]:
            o=other.get_window_extent(renderer)
            if b.overlaps(o):errors.append('Text overlap: '+t.get_text()+' / '+other.get_text())
    if errors:raise ValueError('\n'.join(errors))
    # Fixed canvas preserves the final typography scale; no post-render shrink-to-fit.
    with mpl.rc_context({'savefig.bbox':None}):
        fig.savefig(OUT/f'{stem}.pdf',metadata={'Title':stem,'Creator':'Auto-Decte figure revision'})
        fig.savefig(OUT/f'{stem}.svg')
        fig.savefig(OUT/f'{stem}.png',dpi=300)
    plt.close(fig)
    return {'width_pt':432,'height_pt':fig.get_figheight()*72,
            'minimum_font_pt':min(t.get_fontsize() for t in texts),
            'text_count':len(texts),'text_overlap_count':0}


def workflow():
    fig,ax=canvas(116)
    for x,w,title,color in [(2,36,'1  Candidate',BLUE),(45,40,'2  Human review',PURPLE),
                            (94,43,'3  Admission',INK),(146,32,'4  Successor',GREEN)]:
        label(ax,x+w/2,110,title,10,True,color)
        ax.plot([x,x+w],[104,104],color=color,lw=1)
    box(ax,2,38,36,62,BLUE_BG)
    label(ax,20,93,'Keep candidate',9.5,True,BLUE)
    label(ax,20,79,'Exact $c_i$\nRecord + field',9.5)
    label(ax,20,63,'Evidence\n+ producer',9.5)
    label(ax,20,46,'Proposal $x_c$\nVersion $v$',9.5)
    label(ax,20,27,'No direct\nfact-write port',9.5,color=MUTED)
    box(ax,45,34,40,66,PURPLE_BG)
    label(ax,65,94,'Bind $c_i$ to $x_a$',9.5,color=PURPLE)
    box(ax,48,70,34,17,'white')
    label(ax,65,82,'Accept',9.8,True)
    label(ax,65,75,'$x_a=x_c$',9.5)
    box(ax,48,47,34,20,'#E7DCEE')
    label(ax,65,62,'Correction',9.8,True)
    label(ax,65,53,'$x_a\\ne x_c$'.replace('\\\\','\\'),9.5)
    box(ax,53,34,24,10,'white')
    label(ax,65,39,'Reject',9.8,True,color=ACCENT_RED)
    arrow(ax,(38,91),(45,91),BLUE)
    ax.plot([82,88,88,82],[78,78,56,56],color=PURPLE,lw=1)
    arrow(ax,(88,67),(94,67),PURPLE)
    box(ax,94,34,43,66,ORANGE_BG)
    label(ax,115.5,94,'One transaction',9.5,True)
    for y,st in [(84,'$D_C$  Candidate'),(76,'$D_V$  Value roles'),(68,'$D_F$  Freshness'),
                 (60,'$D_B$  Whole batch'),(52,'$D_S$  Field sources')]:
        label(ax,97,y,st,9.5,ha='left')
    label(ax,115.5,44,'Recheck policy',9.5)
    box(ax,95,34,41,7,'white')
    label(ax,115.5,37.5,'CAS + commit',9.5,True)
    box(ax,146,34,32,66,GREEN_BG)
    label(ax,162,93,'Record $v+1$',9.5,True,GREEN)
    label(ax,162,79,'All values\n+ sources',9.5)
    label(ax,162,62,'Changed:\nnew source',9.5)
    label(ax,162,44,'Unchanged:\nprior source',9.5)
    arrow(ax,(137,70),(146,70),GREEN)
    box(ax,45,10,133,12,RED_BG)
    label(ax,111.5,16,'No authoritative change',10,True,ACCENT_RED)
    arrow(ax,(65,34),(65,22),ACCENT_RED,True)
    arrow(ax,(115.5,34),(115.5,22),ACCENT_RED,True)
    label(ax,120,28,'Fail / CAS loss',9.5,color=ACCENT_RED,ha='left')
    label(ax,90,3,'Solid: admission flow. Dashed: rejection or rollback.',9.5,color=MUTED)
    return export(fig,'figure-1-admission-workflow')


def evidence():
    fig,ax=canvas(112)
    label(ax,90,107,'What each contribution establishes',10.5,True)
    cards=[
      (2,59,BLUE_BG,BLUE,'C1  Admission contract',
       'Preserves proposal and human\nvalue authority in one successor.',
       'Exact candidate + authorized value\n+ complete field-source lineage'),
      (95,59,PURPLE_BG,PURPLE,'C2  Conditional characterization',
       'Shows which omissions hide\neach declared failure family.',
       'Paired histories / Proposition 1\nWithin the declared observation model'),
      (2,17,GREEN_BG,GREEN,'C3  Realization checks',
       'Checks the contract in a model\nand the persisted implementation.',
       'Alloy, projections and fault tests\nBounded; implementation-specific'),
      (95,17,ORANGE_BG,'#995A14','C4  Cost and agent observations',
       'Characterizes cost and separates\ntask behavior from host authority.',
       'Persistence / trace / agent workloads\nFixed environment and restricted tools')]
    for x,y,bg,col,title,claim,support in cards:
        box(ax,x,y,83,38,bg)
        label(ax,x+4,y+32,title,9.7,True,col,ha='left')
        label(ax,x+4,y+22,claim,9.5,ha='left')
        label(ax,x+4,y+9,support,9.5,color=MUTED,ha='left')
    label(ax,90,8,'Reproducibility: raw records → normalized inputs → reported outputs',9.5)
    return export(fig,'figure-2-evidence-map')


if __name__=='__main__':
    # Values are inherited from the unchanged frozen paper tables and results.
    results=(ROOT/'sections/08-results.tex').read_text(encoding='utf-8')
    for token in ['66','354','33','2,000','7,200','1,260','320','335','720','179','93']:
        assert token in results, token
    audit={'figure_1':workflow(),'figure_2':evidence(),
           'statistics':'Frozen counts, not new experiments; separate denominators; no inferential test performed.',
           'source_map':{'Alloy':'tables/generated/formal_evidence.tex',
             'projection_concrete_regression':'tables/generated/validation_evidence.tex',
             'runtime':'tables/generated/runtime_endpoint_table.tex',
             'behavior':'tables/generated/agent_behavior_table.tex',
             'authority':'sections/07-evaluation-protocol.tex and sections/08-results.tex',
             'performance':'sections/08-results.tex, RQ6'}}
    (OUT/'figure-audit.json').write_text(json.dumps(audit,indent=2))
    print(json.dumps(audit,indent=2))
