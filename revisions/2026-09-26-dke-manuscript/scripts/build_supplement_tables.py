from pathlib import Path
import csv, json, hashlib
p=Path(__file__).resolve().parents[1]
src=p/'tables'/'supplement-current'
out=p/'tables'/'supplement-current'; out.mkdir(exist_ok=True)
manifest={}
for name in ['e3-mechanism-summary.csv','e3-ablation-summary.csv','e3-trace-summary.csv','storage.csv']:
    data=(src/name).read_bytes(); (out/name).write_bytes(data)
    manifest[name]=hashlib.sha256(data).hexdigest()

def rows(name):
    with (src/name).open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
def fmt(r): return f"{float(r['p50_ms']):.2f} / {float(r['p95_ms']):.2f}"
trace=rows('e3-trace-summary.csv'); groups={}
for r in trace: groups.setdefault(tuple(int(r[k]) for k in ['fields','versions','records']),{})[r['arm']]=r
s=r'''\begingroup
\small
\setlength{\tabcolsep}{3pt}
\begin{longtable}{@{}rrrllrr@{}}
\caption{Complete current trace grid. Latency is p50 / p95 in milliseconds; each arm has 200 timed observations after five warmups. SQL counts are constant within each arm/cell.}\label{tab:s-trace-grid}\\
\toprule
Fields & Versions & Records & Bulk access & Point access & Bulk SQL & Point SQL \\
\midrule
\endfirsthead
\toprule
Fields & Versions & Records & Bulk access & Point access & Bulk SQL & Point SQL \\
\midrule
\endhead
\bottomrule
\endfoot
'''
for key,g in sorted(groups.items()):
    s+=' & '.join([*(str(x) for x in key),fmt(g['batch']),fmt(g['point_lookup']),g['batch']['sql_min'],g['point_lookup']['sql_min']])+r' \\'+'\n'
s+=r'\end{longtable}'+'\n'+r'\endgroup'+'\n'
(out/'trace-grid.tex').write_text(s,encoding='utf-8')
for name,arms,title in [('mechanism',['reference','journal_exact'],'Complete confirmation paths with pre-registered recognition candidates'),('ablation',['full','materialization'],'Full confirmation and prevalidated materialization')]:
    rs=rows('e3-'+name+'-summary.csv'); gs={}
    observed=sorted(set(r['arm'] for r in rs))
    if not all(a in observed for a in arms):
        print(name, observed); continue
    for r in rs: gs.setdefault((int(r['fields']),int(r['changed'])),{})[r['arm']]=r
    s=r'\begin{table}[htbp]'+'\n'+r'\centering\small'+'\n'+f'\\caption{{{title}. Entries are p50 / p95 in milliseconds; 200 observations per arm/cell.}}\n'+f'\\label{{tab:s-{name}-grid}}\n'+r'\begin{tabular}{@{}rrll@{}}'+'\n'+r'\toprule'+'\n'+('Fields & Changed & Reference & Exact journal' if name=='mechanism' else 'Fields & Changed & Full confirmation & Materialization')+r' \\'+'\n'+r'\midrule'+'\n'
    for key,g in sorted(gs.items()): s+=' & '.join([*(str(x) for x in key),*(fmt(g[a]) for a in arms)])+r' \\'+'\n'
    s+=r'\bottomrule\end{tabular}\end{table}'+'\n'
    (out/(name+'-grid.tex')).write_text(s,encoding='utf-8')
(p/'editorial'/'table-input-hashes.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')


