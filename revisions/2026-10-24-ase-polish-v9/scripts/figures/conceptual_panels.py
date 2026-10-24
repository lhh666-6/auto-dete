"""Conceptual constructions, not measured observations.

Original artwork using the process/artifact/decision grammar of published ASE
workflow figures. No published artwork is copied or embedded.
"""
from figure_style import *
from paper_objects import candidate, grant, CONTEXT, INSTANCE, CONTEXT_TINT, INSTANCE_TINT


def build_gap():
    from build_gap import build_gap as render_gap
    render_gap()


def build_design_space():
    fig, ax = canvas(90)
    text(ax, 5, 86, "(a)  Which requests can be admitted?", size=8.5, ha="left")
    # Set geometry is schematic. It encodes weak inclusion, not set cardinality.
    sets = [
        (5, 50, 140, 30, "Value", "authorized value", "#F8F8F7", INK),
        (37, 53, 103, 23, "Context", "fields K", CONTEXT_TINT, CONTEXT),
        (70, 56, 65, 16, "Content", "fields R", "#FFFFFF", INK),
        (105, 59, 26, 8, "Instance", "", INSTANCE_TINT, INSTANCE),
    ]
    for x,y,w,h,label,desc,fill,color in sets:
        ax.add_patch(Rectangle((x,y),w,h,facecolor=fill,edgecolor=color,lw=.7))
        if desc:
            text(ax,x+3,y+h-4,label,size=7.5,ha="left",color=color)
            text(ax,x+3,y+h-9,desc,size=7.5,ha="left",color=MUTED)
        else:
            text(ax,x+w/2,y+h/2,label,size=7.5,color=color)
    text(ax,75,46,"Shared checks · immutable records · R includes K · equality is allowed",size=7.5)

    text(ax,5,41,"(b)  After an instance mismatch",size=8.5,ha="left")
    node(ax,5,14,29,14,"Mismatch\nno new commit",size=7.5)
    for y, ident, auth, title in [(27,'c1','a1','Reuse · existing grant'),(5,'c2','a2','Fresh matching authorization')]:
        text(ax,77,y+13.5,title,size=7.5)
        candidate(ax,48,y,ident,width=27,lines=('context K',),changed=ident=='c2')
        grant(ax,77,y+2,auth,width=26)
        ax.plot([75,79],[y+5,y+5],color=INK,lw=.6)
        flow(ax,[(34,21),(40,21),(40,y+5),(48,y+5)])
        flow(ax,[(103,y+5),(111,y+5),(111,21),(118,21)])
    node(ax,118,13,25,16,"New\ncheck",kind="decision",size=7.5)
    # Both routes return to a check; neither arrow promises successful admission.
    save_fixed(fig,"fig3-design-space")


if __name__ == "__main__":
    build_gap()
    build_design_space()
