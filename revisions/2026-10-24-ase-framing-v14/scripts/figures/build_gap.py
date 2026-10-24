"""Manuscript Figure 1 with embedded AI-generated object glyphs and live text.

Conceptual example; deterministic hybrid export from archived image assets.
"""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[2] / "figures"
ASSETS = Path(__file__).resolve().parent / 'assets' / 'fig1-gpt-symbols'
SHEET = plt.imread(ASSETS / 'symbol-sheet.png')
# Crops are lossless placement windows in the unmodified generated sheet.
GLYPHS = {'candidate': (89,78,1165,472), 'grant': (69,576,1187,838),
          'state': (76,928,1172,1185)}
INK = '#333333'
WHITE = '#FFFFFF'
CONTEXT = '#8C6847'
INSTANCE = '#4F6B7A'
REGULAR = 9.75
EMPHASIS = 11.05
plt.rcParams.update({'font.family': 'Arial', 'svg.fonttype': 'none',
                     'pdf.fonttype': 42, 'savefig.bbox': None,
                     'image.composite_image': False})


def label(ax, x, y, value, *, emphasis=False, ha='center', color=INK):
    return ax.text(x, y, value, fontsize=EMPHASIS if emphasis else REGULAR,
                   weight='bold' if emphasis else 'normal', color=color,
                   ha=ha, va='center', linespacing=1.2)


def line(ax, points, lw=.6):
    return ax.plot(*zip(*points), color=INK, lw=lw,
                   solid_capstyle='round', solid_joinstyle='round')[0]


def glyph(ax, name, x, y, width, height, *, grayscale=False):
    left,top,right,bottom = GLYPHS[name]
    pixels = SHEET[top:bottom,left:right].copy()
    if grayscale:
        luminance = np.dot(pixels[:,:,:3], [0.2126,0.7152,0.0722])
        pixels[:,:,:3] = luminance[:,:,None]
    ax.imshow(pixels,extent=(x,x+width,y,y+height),origin='upper',
              aspect='auto',interpolation='none',zorder=1)


def card(ax, x, y, identifier, descriptor, *, height=9.5, inverted=False, grayscale=False, emphasis_desc=False):
    width = 34
    glyph(ax,'candidate',x,y,width,12.45,grayscale=grayscale)
    if inverted:
        ax.add_patch(FancyBboxPatch((x+2.1,y+9.35),8.55,3.25,
                                   boxstyle='round,pad=0,rounding_size=.7',
                                   facecolor=INK,edgecolor=INK,lw=.4,zorder=2))
    label(ax, x+6.35, y+11.0, identifier, color=WHITE if inverted else INK)
    label(ax, x+11.5, y+height+1.9, descriptor, ha='left', emphasis=emphasis_desc)
    label(ax, x+3, y+height-3.4, 'proposal 100', ha='left')
    label(ax, x+3, y+2.5, 'context K', ha='left')


def execution_path(ax, gate_x, cy, token_x, *, color=INK, rejected=False, grayscale=False):
    """An independent policy check and its effect; never a chain across columns."""
    r = 2.4
    ax.add_patch(Polygon([(gate_x-r,cy),(gate_x,cy+r),(gate_x+r,cy),(gate_x,cy-r)],
                         closed=True,facecolor=WHITE,edgecolor=color,lw=.7,
                         joinstyle='round'))
    if rejected:
        stop_x = gate_x+6.7
        line(ax,[(gate_x+r,cy),(stop_x,cy)],.65)
        line(ax,[(stop_x,cy-2.1),(stop_x,cy+2.1)],.8)
        label(ax,stop_x+2.3,cy,'reject · no commit',emphasis=True,ha='left')
    else:
        glyph(ax,'state',token_x,cy-3.3,23.4,6.6,grayscale=grayscale)
        ax.add_patch(FancyArrowPatch((gate_x+r+.2,cy),(token_x-.2,cy),
                                    arrowstyle='-|>',mutation_scale=7,lw=.65,
                                    color=INK,shrinkA=0,shrinkB=0))
        label(ax,token_x+11.7,cy,'90 → 101',emphasis=True)


def state_token(ax, x, cy, width, value, *, grayscale=False):
    """The authoritative state, before any of the alternative executions."""
    glyph(ax,'state',x,cy-3.3,width,6.6,grayscale=grayscale)
    label(ax,x+width/2,cy,value)


def render(grayscale=False):
    fig = plt.figure(figsize=(150/25.4, 76/25.4), facecolor=WHITE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, 150), ylim=(0, 76))
    ax.axis('off')

    label(ax, 7, 72, 'One review', ha='left')
    card(ax, 7, 56, 'c1', 'immutable candidate',grayscale=grayscale)
    # The string is a reference, not a directed execution or generation edge.
    glyph(ax,'grant',41,55.36,46,10.78,grayscale=grayscale)
    label(ax, 52, 67.8, 'grant a1', ha='left')
    label(ax, 70, 62.6, 'authorizes 101')
    label(ax, 70, 58.9, 'corrects 100')
    state_token(ax,97,60.75,23.4,'90',grayscale=grayscale)
    label(ax,123,60.75,'current state',ha='left')

    line(ax, [(7, 52), (143, 52)], .5)
    label(ax, 7, 48, 'Alternative runs from the current state · same unconsumed grant a1', ha='left')
    label(ax, 7, 43.5, 'Shared checks satisfied in every run.', ha='left')

    # Pale bands group independent runs under a policy, not a sequential workflow.
    for x, tint in ((44, '#F6F3F0'), (97, '#F1F3F4')):
        ax.add_patch(FancyBboxPatch((x,1),50,40,
                                   boxstyle='round,pad=0,rounding_size=.8',
                                   facecolor='#F4F4F4' if grayscale else tint,
                                   edgecolor='none',zorder=0))

    label(ax, 7, 38.7, 'Candidate', ha='left')
    label(ax, 69, 38.7, 'Context binding',
          color=INK if grayscale else CONTEXT)
    label(ax, 122, 38.7, 'Instance binding',
          color=INK if grayscale else INSTANCE)
    label(ax, 69, 34.3, 'checks context')
    label(ax, 122, 34.3, 'checks context + ID')
    line(ax, [(7, 31.8), (143, 31.8)], .5)

    card(ax, 7, 18, 'c1', 'reviewed ID',grayscale=grayscale)
    card(ax, 7, 2.5, 'c2', 'different ID', inverted=True,grayscale=grayscale, emphasis_desc=True)
    for cy in (22.75,7.25):
        execution_path(ax,49.5,cy,62.5,color=INK if grayscale else CONTEXT,grayscale=grayscale)
    execution_path(ax,104.5,22.75,119,color=INK if grayscale else INSTANCE,grayscale=grayscale)
    execution_path(ax,104.5,7.25,119,color=INK if grayscale else INSTANCE,rejected=True,grayscale=grayscale)
    # These tokens belong to alternative runs; the bracket is comparison, not flow.
    line(ax,[(87.4,22.75),(89.4,22.75),(89.4,7.25),(87.4,7.25)],.55)
    label(ax,87.6,15,'same endpoint',ha='right', emphasis=True)

    stem = 'fig1-review-execution-gap-grayscale' if grayscale else 'fig1-review-execution-gap'
    fig.canvas.draw()
    for ext in ('pdf', 'svg', 'png'):
        fig.savefig(ROOT/f'{stem}.{ext}', dpi=300, facecolor=WHITE,
                    metadata={'Creator': 'AI-generated object glyphs; Matplotlib layout and live text'} if ext == 'pdf' else None)
    plt.close(fig)
    svg = ROOT/f'{stem}.svg'
    source = re.sub(r'<!DOCTYPE[^>]*>', '', svg.read_text(encoding='utf-8'))
    # Declare text size in SVG user units, matching the point-based viewBox.
    # This removes the px-versus-physical-pt ambiguity for downstream validators.
    def explicit_user_font(match):
        attributes = match.group(1)
        size = re.search(r'font-size: ([0-9.]+)px;?\s*', attributes)
        if size:
            attributes = attributes[:size.start()]+attributes[size.end():]
            attributes += f' font-size="{size.group(1)}"'
        return '<text '+attributes+'>'
    source = re.sub(r'<text ([^>]+)>', explicit_user_font, source)
    ET.fromstring(source)
    svg.write_text(source, encoding='utf-8')


def build_gap():
    ROOT.mkdir(parents=True, exist_ok=True)
    render()
    render(grayscale=True)


if __name__ == '__main__':
    build_gap()
    print('Built manuscript Figure 1 and grayscale companion, 150 x 76 mm.')
