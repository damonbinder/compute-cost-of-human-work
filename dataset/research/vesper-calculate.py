"""Python 3 standard library. Writes arithmetic, never edits input evidence.

python vesper-calculate.py --inputs vesper-inputs.json --models ../models.csv --output calculation.json
"""
import argparse, csv, json, math
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--inputs',required=True)
p.add_argument('--models',required=True)
p.add_argument('--output',required=True)
a=p.parse_args()
if Path(a.output).resolve() in {Path(a.inputs).resolve(),Path(a.models).resolve()}:
    p.error('output must differ from inputs')
d=json.loads(Path(a.inputs).read_text())
with open(a.models,newline='') as f:
    m=next(r for r in csv.DictReader(f) if r['model_id']==d['model_id'])
t=d['token_budget_per_run']*d['runs'];q=(t/(d['algorithms_mean_per_run']*d['runs'])+1)/2
out={'tokens':t,'attention_context':q,'human_time':d['human_seconds']}
for suffix in ['', '_low','_high']:
    n=float(m['active_parameters'+suffix])
    if suffix:
        dense=(n/196608)**(1/3);l=0.65*dense;h=128*dense
    else:l=float(m['attention_layers']);h=float(m['attention_width'])
    out['compute_flops'+suffix]=t*(2*n+4*l*h*q)
    if not suffix:out['attention_ratio']=2*l*h*q/n
# A simple human construction attaining the recorded score. This is an
# independent feasibility check, not the AI output or a timing observation.
r=d['best_valid_score']/(25+math.sqrt(2)-1)
circles=[(r+2*r*i,r+2*r*j,r) for i in range(5) for j in range(5)]
circles.append((2*r,2*r,(math.sqrt(2)-1)*r))
margin=min(min(x-r,y-r,1-x-r,1-y-r) for x,y,r in circles)
gap=min(math.hypot(x-X,y-Y)-r-R for i,(x,y,r) in enumerate(circles) for X,Y,R in circles[i+1:])
assert margin>=-1e-12 and gap>=-1e-12
out['comparison_construction']={'sum_radii':sum(c[2] for c in circles),'min_boundary_clearance':margin,'min_pair_clearance':gap,'circles':circles}
Path(a.output).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='comparison_construction'},indent=2))
