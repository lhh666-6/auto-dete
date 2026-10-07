"""Publication figures derived from the completed frozen export; no simulated data."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/'evidence/online/manuscript-aggregates.json').read_text(encoding='utf-8'))
assert data['collection_status']=='COMPLETE'
DEST=ROOT/'figures';DEST.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':['Arial','DejaVu Sans'],'font.size':9,
    'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.8,
    'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','legend.frameon':False})
BLUE='#0F4D92';RED='#B64342';GREEN='#8BCF8B';GRAY='#CFCECE'
def save(fig,name):
    for ext in ('pdf','svg','png'):fig.savefig(DEST/(name+'.'+ext),dpi=400,bbox_inches='tight',pad_inches=.06)
    plt.close(fig)
def box(ax,x,y,w,h,text,color='#EDF3F8'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.012',fc=color,ec='#4D4D4D',lw=.8))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=9)
def arrow(ax,a,b,color='#4D4D4D'):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','lw':1.1,'color':color})
fig,ax=plt.subplots(figsize=(7.1,2.85));ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
box(ax,.015,.66,.20,.24,'Agent proposal\n'+r'$c_1: x_c=100$')
box(ax,.30,.66,.25,.24,'Review / correction\n'+r'$a: (c_1,x_a=101)$')
box(ax,.68,.66,.29,.24,'Authoritative transition\n'+r'$101$ + exact lineage')
arrow(ax,(.215,.78),(.285,.78));arrow(ax,(.565,.78),(.665,.78))
box(ax,.02,.16,.23,.24,'New instance '+r'$c_2$'+'\nSame value and context','#FAEFED')
box(ax,.345,.16,.23,.24,'Execute '+r'$c_2$'+' with '+r'$a$'+'\n'+r'$G=K_{eq}=1$'+'; '+r'$I_{eq}=0$','#FAEFED')
box(ax,.68,.16,.29,.24,'Bound: reject → feedback\nReuse '+r'$c_1$'+' or review '+r'$c_2$')
arrow(ax,(.25,.28),(.33,.28));arrow(ax,(.59,.28),(.665,.28),BLUE)
arrow(ax,(.825,.41),(.825,.645),BLUE)
ax.text(.46,.51,'Context admits the equivalent instance; bound requires the reviewed instance.',ha='center',fontsize=8)
save(fig,'figure1-contract')

fig,axes=plt.subplots(1,2,figsize=(7.1,2.9),layout='constrained')
cells=['1,1','1,0','0,1','0,0','0,unknown'];colors=[BLUE,RED,GRAY,'#E9A6A1','#FFD76A']
labels=[r'$U=1,I=1$',r'$U=1,I=0$',r'$U=0,I=1$',r'$U=0,I=0$',r'$I$ unknown']
for ax,config in zip(axes,'AB'):
    bottom=[0,0]
    for cell,color,label in zip(cells,colors,labels):
        vals=[data['groups'][config+'-'+p]['joint'].get(cell,0) for p in ('context','bound')]
        ax.bar([0,1],vals,bottom=bottom,color=color,edgecolor='white',linewidth=.6,label=label)
        for x,v,b in zip([0,1],vals,bottom):
            if v>=7:ax.text(x,b+v/2,str(v),ha='center',va='center',color='white' if color in (BLUE,RED) else '#272727',fontsize=9)
        bottom=[a+b for a,b in zip(bottom,vals)]
    ax.set(ylim=(0,140),xticks=[0,1],xticklabels=['Context','Bound'],title=f'{config}: 128 planned arms per policy')
    ax.set_ylabel('Planned arms')
    ax.text(.5,135,f"Review checkpoint: {data['checkpoint_pairs'][config]}/128 pairs",ha='center',fontsize=8)
handles,legend=axes[0].get_legend_handles_labels();fig.legend(handles,legend,ncol=5,loc='outside lower center',fontsize=8)
save(fig,'figure2-joint-outcomes')

fig,axes=plt.subplots(1,2,figsize=(7.1,3.15),layout='constrained')
for ax in axes:ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
axes[0].set_title('(a) N: agent-managed refreshed preview',fontsize=9)
box(axes[0],.05,.70,.90,.17,'32 planned arms / policy in B')
box(axes[0],.05,.37,.90,.22,'30 exact reviewed-instance transitions\n1 covered arm without a transition\n1 integrity-unknown arm')
box(axes[0],.05,.04,.90,.21,'Each policy: 28 '+r'$(U,I)=(1,1)$'+'\n3 '+r'$(0,1)$'+'; 1 '+r'$I$'+' unknown\nNo delivered mismatch feedback')
arrow(axes[0],(.5,.69),(.5,.60));arrow(axes[0],(.5,.36),(.5,.26))
axes[1].set_title('(b) G: standardized queued handoff',fontsize=9)
box(axes[1],.05,.70,.90,.17,'B bound: 16 instance-mismatch rejections')
box(axes[1],.05,.37,.90,.22,'16 delivered → next action: commit\nReuse the reviewed candidate\n16 complete with '+r'$(U,I)=(1,1)$')
box(axes[1],.05,.04,.90,.21,'A bound: 1 delivered → reauthorize\nthen commit; '+r'$(U,I)=(1,1)$'+'\n15 shared-prefix failures retained')
arrow(axes[1],(.5,.69),(.5,.60));arrow(axes[1],(.5,.36),(.5,.26))
save(fig,'figure3-feedback-paths')
print('Generated 3 figures in PDF, SVG and PNG from complete formal evidence.')
