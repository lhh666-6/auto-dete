"""Shared Figure 1 glyphs, live labels, and restrained policy colors.

Reuses the archived generated sheet without changing its pixels. All scientific
labels and connecting relationships remain vector objects. No new generation.
"""
from matplotlib.patches import FancyBboxPatch, Polygon
from figure_style import text, INK
from build_gap import glyph

CONTEXT = '#8C6847'
INSTANCE = '#4F6B7A'
CONTEXT_TINT = '#F6F3F0'
INSTANCE_TINT = '#F1F3F4'


def candidate(ax, x, y, identity, *, width=34, lines=('context K', r'proposal $x_c$'), changed=False, descriptor=''):
    scale = width / 34
    h = 12.45 * scale
    glyph(ax, 'candidate', x, y, width, h)
    if changed:
        ax.add_patch(FancyBboxPatch((x+2.1*scale,y+9.35*scale),8.55*scale,3.25*scale,
            boxstyle='round,pad=0,rounding_size=.5',facecolor=INK,edgecolor=INK,lw=.4,zorder=2))
    text(ax,x+6.35*scale,y+11*scale,identity,size=7.5,color='white' if changed else INK,zorder=3)
    if descriptor:
        text(ax,x+12*scale,y+11*scale,descriptor,size=7.5,ha='left',zorder=3)
    for line, yy in zip(lines, (6.1,2.5)):
        text(ax,x+3*scale,y+yy*scale,line,size=7.5,ha='left',zorder=3)
    return x+width,y+h/2


def grant(ax,x,y,identity,*,width=31,subtitle=None):
    h=width*262/1118
    glyph(ax,'grant',x,y,width,h)
    text(ax,x+width*.61,y+h*.5,identity,size=7.5,zorder=3)
    if subtitle:
        text(ax,x+width*.6,y-2.8,subtitle,size=7.5)
    return x+width,y+h/2


def gate(ax,x,y,*,color=INK,identity=False):
    ax.add_patch(Polygon([(x-10.5,y),(x,y+8),(x+10.5,y),(x,y-8)],
        closed=True,facecolor='white',edgecolor=color,lw=.85,zorder=2))
    if identity:
        text(ax,x,y+2.4,'K',size=7.5,zorder=3)
        text(ax,x,y-2.4,'+ ID',size=8.5,weight='bold',color=color,zorder=3)
    else:
        text(ax,x,y,'K',size=7.5,zorder=3)


def band(ax,x,y,w,h,color):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=1.1',
                              facecolor=color,edgecolor='none',zorder=-2))
