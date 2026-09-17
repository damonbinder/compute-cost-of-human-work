#!/usr/bin/env python3
"""Dominant policy-forward operations for the July 2021 Sophy Maggiore lap.
Standard Python only; no model inference. Read-only sources; new output required.
"""
import argparse,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
s=a.sources.resolve();o=a.output.resolve()
if o.exists() or o==s or s in o.parents:p.error('Output must be new and outside sources')
def forward(d):
 return 2*(d*2048+2048*2048+2048*4)+2*2048+2*2048+4+20
result={'input_dimension_estimate':568,'hidden_width':2048,'hidden_layers':2,'gaussian_outputs':4,'actions_per_second':10,'ai_lap_seconds_figure_estimate':114.2,'human_best_lap_seconds_figure_estimate':114.2,'ai_observed_laps':100,'human_selected_best_laps':1,'flops_per_action':forward(568),'policy_calls_per_mean_lap':1142,'compute_flops':forward(568)*1142,'feature_sensitivity_flops':{str(d):forward(d)*1142 for d in [560,568,580]},'source_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in s.iterdir() if f.is_file()}}
o.write_text(json.dumps(result,indent=2)+'\n');print(result['compute_flops'])
