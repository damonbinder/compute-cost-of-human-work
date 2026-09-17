#!/usr/bin/env python3
"""Fallingwater compute reconstruction, Python 3 standard library.
Usage: python3 fallingwater-compute.py --input fallingwater-inputs.json --output new-results.json
Reads explicit native counters and declared assumptions; never modifies its inputs.
"""
import argparse,json,math,pathlib
p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);a=p.parse_args()
if pathlib.Path(a.input).resolve() == pathlib.Path(a.output).resolve():
 p.error('input and output must differ')
x=json.loads(pathlib.Path(a.input).read_text())
def calc(n,percall,count=None,width=None,height=None):
 count=x['assumed_image_sends'] if count is None else count
 width=x['assumed_image_width'] if width is None else width
 height=x['assumed_image_height'] if height is None else height
 patches=math.ceil(width/32)*math.ceil(height/32)
 billed=math.ceil(patches*x['image_billing_multiplier'])*count
 visual=patches*count
 text=x['input_uncached']+x['output']-billed
 processed=text+visual
 assert text>0
 dense=max(8,round((n/196608)**(1/3)));layers=max(1,round(dense*.65));querywidth=128*dense
 q=min(200000,processed/2,x['cache_read']/processed*percall)
 f=processed*(2*n+4*layers*querywidth*q)
 return dict(text_tokens=text,image_billing_units=billed,visual_positions=visual,backbone_positions=processed,attention_context=q,attention_ratio=2*layers*querywidth*q/n,compute_flops=f)
n=x['active_parameters'];out=calc(n,2800)
out['compute_flops_low']=calc(x['active_parameters_low'],1976)['compute_flops'];out['compute_flops_high']=calc(x['active_parameters_high'],19088)['compute_flops']
out['scenarios']={'double_image_sends':calc(n,2800,count=2*x['assumed_image_sends']),'1920x1080':calc(n,2800,width=1920,height=1080),'3840x2160':calc(n,2800,width=3840,height=2160),'no_image_adjustment':calc(n,2800,count=0)}
pathlib.Path(a.output).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
