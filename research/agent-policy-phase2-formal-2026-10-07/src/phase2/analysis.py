"""Paired effects with task-cluster, scenario-stratified percentile bootstrap."""
import math, random


def paired_estimates(rows, iterations=10000, seed=20261007):
    lookup={(r['task_instance_id'],r['config_id'],r['policy']):r for r in rows}
    tasks=sorted({r['task_instance_id'] for r in rows}); configs=['A','B']
    strata={s:[t for t in tasks if next(r['scenario'] for r in rows if r['task_instance_id']==t)==s] for s in sorted({r['scenario'] for r in rows})}
    def deltas(field,unknown_value=None):
        out={}
        for t in tasks:
            out[t]=[]
            for c in configs:
                pair=[lookup.get((t,c,p)) for p in ['context','bound']]
                if any(x is None for x in pair): raise ValueError('planned arm missing from analysis input')
                a,b=[p[field] for p in pair]
                if a is None or b is None:
                    if unknown_value=='lower': a=1 if a is None else a; b=0 if b is None else b
                    elif unknown_value=='upper': a=0 if a is None else a; b=1 if b is None else b
                    else: out[t].append(None); continue
                out[t].append(int(b)-int(a))
        return out
    def summary(values):
        if any(x is None for v in values.values() for x in v): return {'estimate':None,'interval':None}
        mean=lambda ts:sum(sum(values[t])/2 for t in ts)/len(ts)
        rng=random.Random(seed); draws=[]
        for _ in range(iterations):
            sample=[rng.choice(block) for block in strata.values() for _ in block]
            draws.append(mean(sample))
        draws.sort()
        return {'estimate':mean(tasks),'interval':[draws[int(.025*(iterations-1))],draws[int(.975*(iterations-1))]]}
    incidence=deltas('continuity_failure_incidence')
    mcnemar={}
    for c in configs:
        cb=bc=0
        for t in tasks:
            a=bool(lookup[t,c,'context']['task_completion']); b=bool(lookup[t,c,'bound']['task_completion'])
            cb+=int(a and not b); bc+=int(b and not a)
        n=cb+bc
        p=1 if n==0 else min(1,2*sum(math.comb(n,k) for k in range(min(cb,bc)+1))/(2**n))
        mcnemar[c]={'context_only':cb,'bound_only':bc,'exact_two_sided_p':p,'secondary':True}
    return {'planned_arms':len(rows),'task_clusters':len(tasks),'paired_units':len(tasks)*2,
        'completion':summary(deltas('task_completion')),
        'completion_by_config':{c:summary({t:[v[i],v[i]] for t,v in deltas('task_completion').items()}) for i,c in enumerate(configs)},
        'continuity_by_config':{c:summary({t:[v[i],v[i]] for t,v in incidence.items()}) for i,c in enumerate(configs)},
        'continuity':{**summary(incidence),'unknown_arms':sum(r['continuity_failure_incidence'] is None for r in rows),
            'identification_lower':summary(deltas('continuity_failure_incidence','lower')),
            'identification_upper':summary(deltas('continuity_failure_incidence','upper'))},
        'mcnemar_by_config':mcnemar,'bootstrap_seed':seed,'bootstrap_iterations':iterations}
