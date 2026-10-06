"""Publication exports from completed formal tables only; never mock model data."""
import csv,json
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def draw(directory):
    summary=json.loads((directory/'analysis-summary.json').read_text(encoding='utf-8'))
    if not summary['formal_inference_allowed']: raise ValueError('FIGURES_REQUIRE_COMPLETED_FORMAL_COLLECTION')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,
        'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none'})
    def read(name):
        with (directory/name).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
    episodes=read('table3-recovery.csv'); pairs=read('paired-effects.csv')
    fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    for ax,family in zip(axes,['N','G']):
        rows=[r for r in episodes if r['scenario']==family]
        counts=Counter((r['trigger_code'],r['first_meaningful_action'],r['U'],r['I']) for r in rows)
        ax.set_title(f'{family}: delivered feedback → next action → terminal outcome')
        ax.set_axis_off()
        if not counts:ax.text(.5,.5,'No delivered rejection observed',ha='center',transform=ax.transAxes);continue
        triples=sorted(counts.items()); n=len(triples)
        for i,((trigger,action,u,integrity),count) in enumerate(triples):
            y=1-(i+.5)/n
            for x,text in [(0.01,trigger),(0.43,action),(.82,f'U={u}, I={integrity}')]:
                ax.text(x,y,text,fontsize=7,va='center',transform=ax.transAxes)
            ax.annotate('',xy=(.4,y),xytext=(.24,y),xycoords='axes fraction',arrowprops={'arrowstyle':'->','lw':1+count/len(rows),'color':'#666666'})
            ax.annotate('',xy=(.79,y),xytext=(.65,y),xycoords='axes fraction',arrowprops={'arrowstyle':'->','lw':1+count/len(rows),'color':'#666666'})
            ax.text(.73,y+.03,f'n={count}',fontsize=6,transform=ax.transAxes)
    for ext in ['pdf','svg','png']:fig.savefig(directory/('figure1-recovery-flow.'+ext),dpi=300,bbox_inches='tight')
    plt.close(fig)
    fig,axes=plt.subplots(2,2,figsize=(9,6),layout='constrained')
    metrics=[('delta_task_completion','Completion difference'),('delta_suffix_agent_tool_calls','Additional Agent tool calls'),
             ('delta_suffix_authorization_requests','Additional authorization requests'),('delta_suffix_elapsed_ms','Suffix latency difference (seconds)')]
    tasks=sorted({r['task_instance_id'] for r in pairs}); indices={t:i for i,t in enumerate(tasks)}
    for ax,(metric,label) in zip(axes.flat,metrics):
        for config,color,marker in [('A','#0072B2','o'),('B','#D55E00','x')]:
            rows=[r for r in pairs if r['config_id']==config and r[metric]!='']
            values=[float(r[metric])/(1000 if metric.endswith('_ms') else 1) for r in rows]
            ax.scatter([indices[r['task_instance_id']] for r in rows],values,s=13,alpha=.65,c=color,marker=marker,label=config)
        ax.axhline(0,c='#555555',lw=.7);ax.set_xlabel('Frozen task index');ax.set_ylabel(label+'\n(bound − context)')
    axes.flat[0].legend(title='Config',frameon=False)
    for ext in ['pdf','svg','png']:fig.savefig(directory/('figure2-paired-policy-effects.'+ext),dpi=300,bbox_inches='tight')
    plt.close(fig)
