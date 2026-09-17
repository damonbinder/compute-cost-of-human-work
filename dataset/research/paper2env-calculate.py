#!/usr/bin/env python3
"""Python 3 stdlib. Rebuild one candidate from retained inputs; no API calls.
python paper2env-calculate.py --inputs paper2env-inputs.json --headers paper2env-headers.json --output /tmp/p2e.csv
"""
import argparse,json,csv
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--inputs',required=True);p.add_argument('--headers',required=True);p.add_argument('--output',required=True);a=p.parse_args()
if Path(a.output).resolve() in {Path(a.inputs).resolve(),Path(a.headers).resolve()}:p.error('output must differ from inputs and headers')
d=json.loads(Path(a.inputs).read_text());h=json.loads(Path(a.headers).read_text());v=d['trajectory'];m=d['model']
t=v['input_tokens']+v['output_tokens'];calls=v['num_turns'];q=(t/calls+1)/2
n=float(m['active_parameters']);l=float(m['attention_layers']);w=float(m['attention_width']);extra=d['test_neural_flops'];attention=4*l*w*q*t
f=2*n*t+attention+extra
bounds=[]
for key in ['active_parameters_low','active_parameters_high']:
 nn=float(m[key]);dense=(nn/196608)**(1/3);bounds.append(2*nn*t+4*d['full_attention_share']*dense*128*dense*q*t+extra)
r=dict.fromkeys(h,'');r.update(point_id='coding-paper2env-apt-sonnet37',task='Implement a masked low-rank adapter',task_category='coding',task_description='The task is to complete four PruningLinear methods in a supplied APT research repository: masked adapter forward computation, pruning-mask initialization, and train/evaluation weight unmerging and merging. The agent receives the paper, detailed TODO guidance and installed dependencies. Work includes implementing and smoke-testing these methods in one recorded run.',model_id=m['model_id'],compute_scope='inference',compute_flops=f,compute_flops_low=bounds[0],compute_flops_high=bounds[1],human_skill='expert',human_time_scope='task_performance',human_time=d['human_seconds'],performance_vs_human='match',comparison_issues='none_identified',compute_evidence='derived_assumed_inputs',human_time_evidence='llm_estimate_judgment',performance_evidence='The recorded submission scored 10/10 on forward-pass, mask-initialization, merge/unmerge and activation checks. The human baseline estimates implementing the same methods at this tested quality; no human timing was observed.',human_time_statistic='point_estimate',human_time_subset='not_applicable',human_attempts='not_applicable',human_time_source='research/paper2env.md#human-time',compute_method='operation_count',compute_statistic='total',compute_subset='successful',ai_attempts=1,compute_source='research/paper2env.md#compute; research/paper2env-inputs.json; research/paper2env-calculate.py',tokens=t,tokens_accounting='input_output',source_dataset='Paper2Env paper-derived implementation tasks',source_record=f"{d['source_url']}; train row 3; trajectory adaptive-pruning/adaptive-pruning/openrouter/anthropic/claude-3.7-sonnet/0; source_eval_run {v['source_eval_run']}; created_at {v['created_at']}; performance: verifier_output",notes='This is a paper-method implementation in a prepared repository, not a full replication. Cache counts are absent; compute assumes full-prefix processing and equal call lengths. The source cost of zero is treated as unavailable.',ai_cost_basis='not_available',human_cost_basis='not_available',attention_context=q,attention_ratio=attention/(2*n*t))
with open(a.output,'w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=h);writer.writeheader();writer.writerow(r)
print(r['compute_flops'],r['human_time'],r['tokens'],r['attention_context'])
