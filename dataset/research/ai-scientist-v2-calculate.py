"""Recompute the proposed point. Python 3 standard library only.

Usage: python calculate.py --workload workload.json --models model-inputs.csv --output new-calculation.json
All inputs are explicit; the output is new arithmetic, not an edit to evidence.
"""
import argparse, csv, json
from collections import defaultdict
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--workload',required=True);p.add_argument('--models',required=True);p.add_argument('--output',required=True)
a=p.parse_args()
if Path(a.output).resolve() in {Path(a.workload).resolve(), Path(a.models).resolve()}:
    p.error('output must differ from the input files')
data=json.loads(Path(a.workload).read_text());models={r['model_id']:r for r in csv.DictReader(open(a.models, newline=''))}
def shape(r,band):
    n=float(r['active_parameters' + ('_'+band if band else '')])
    if not band:return n,int(r['attention_layers']),int(r['attention_width'])
    dense=round((n/196608)**(1/3))
    share=0.70 if r['company']=='Anthropic' else 0.65
    return n,round(dense*share),128*dense
totals=defaultdict(float);by_model=defaultdict(lambda:defaultdict(float));factor=data['extra_call_factor']
for g in data['groups']:
    count=g['calls']*factor
    cached=g.get('cache_read',0)
    text_positions=(g['input']-cached+g['output'])*count
    visual=g.get('visual_positions',0)*count
    positions=text_positions+visual
    # Cached prefix stays in attention context but takes no new weights pass.
    context=cached+(g['input']-cached+g['output']+g.get('visual_positions',0)+1)/2
    for band in ['', 'low','high']:
        n,l,h=shape(models[g['model']],band)
        flops=positions*(2*n+4*l*h*context)
        totals['compute_flops'+('_'+band if band else '')]+=flops
    m=by_model[g['model']];m['text_tokens']+=text_positions;m['visual_positions']+=visual
    m['context_position_sum']+=positions*context;m['positions']+=positions
f=data['experimental_training'];h=f['hidden'];d=f['embedding']
# LSTM's four gate matrix products; triple forward arithmetic for gradients.
forward=8*h*(d+h)+2*h*f['output']
training=f['fits']*f['examples']*f['epochs']*f['sequence_length']*forward*3
# Add one held-out forward pass per epoch on a 200-example test set.
training+=f['fits']*200*f['epochs']*f['sequence_length']*forward
visual_encoder=data['visual_encoder']['images']*data['visual_encoder']['flops_per_image']*factor
for k in list(totals):totals[k]+=training+visual_encoder
for mid,m in by_model.items():m['attention_context']=m['context_position_sum']/m['positions']
primary='claude-3-5-sonnet-20241022';q=by_model[primary]['attention_context'];n,l,h=shape(models[primary],'')
out=dict(totals);out.update(tokens=sum(v['text_tokens'] for v in by_model.values()), attention_context=q, attention_ratio=2*l*h*q/n, experimental_training_flops=training, visual_encoder_flops=visual_encoder, by_model=dict(by_model))
Path(a.output).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='by_model'},indent=2))
