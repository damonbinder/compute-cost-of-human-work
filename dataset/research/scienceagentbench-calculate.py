#!/usr/bin/env python3
"""Rebuild candidates from retained task-specific response counters.
Python 3 standard library only. Example:
python scienceagentbench-calculate.py --inputs scienceagentbench-inputs.json --headers scienceagentbench-headers.json --output /tmp/sab-rebuilt.csv
Does not run the retained model-generated programs or make API calls.
"""
import argparse,csv,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--inputs',required=True);p.add_argument('--headers',required=True);p.add_argument('--output',required=True);a=p.parse_args()
if Path(a.output).resolve() in {Path(a.inputs).resolve(),Path(a.headers).resolve()}:
 p.error('output must differ from retained inputs and headers')
d=json.loads(Path(a.inputs).read_text());headers=json.loads(Path(a.headers).read_text());m=d['model'];rows=[]
for v in d['rows']:
 ids=[c['response_id'] for c in v['calls']];assert len(ids)==len(set(ids))
 positions=0; attention_pairs=0
 for c in v['calls']:
  u=c['usage'];prompt=u['prompt_tokens'];completion=u['completion_tokens'];cache=u['prompt_tokens_details']['cached_tokens'];assert cache==0
  # Each call separately processes its prompt and output; hidden reasoning
  # is included in completion_tokens. Full prompt forwards are charged because
  # native cache counters report zero. Causal mean context=(positions+1)/2.
  q=prompt+completion;positions+=q;attention_pairs+=q*(q+1)/2
 context=attention_pairs/positions
 n=float(m['active_parameters']);L=float(m['attention_layers']);width=float(m['attention_width'])
 weights=2*n*positions;attn=4*L*width*attention_pairs;total=weights+attn
 def bound(n):
  dense=(n/196608)**(1/3);return 2*n*positions+4*d['attention_full_layer_share']*dense*(128*dense)*attention_pairs
 r=dict.fromkeys(headers,'');r.update(point_id=v['point_id'],task=v['task'],task_category='research_analysis',task_description=v['task_description'],model_id=m['model_id'],compute_scope='inference',compute_flops=total,compute_flops_low=bound(float(m['active_parameters_low'])),compute_flops_high=bound(float(m['active_parameters_high'])),human_skill='expert',human_time_scope='task_performance',human_time=v['human_time'],performance_vs_human='match',comparison_issues='none_identified',compute_evidence='derived_assumed_inputs',human_time_evidence='llm_estimate_judgment',human_time_statistic='point_estimate',human_time_subset='not_applicable',human_attempts='not_applicable',human_time_source='research/scienceagentbench.md#'+v['point_id'],compute_method='params_tokens',compute_statistic='total',compute_subset='all',ai_attempts=1,compute_source='research/scienceagentbench.md; research/scienceagentbench-inputs.json; research/scienceagentbench-calculate.py',tokens=positions,tokens_accounting='input_output',source_dataset='ScienceAgentBench',source_record=f"HAL scienceagentbench_sab_selfdebug_o3_medium_1745186112; task {v['task_id']}; {d['trace_url']}; performance: raw_eval_results.eval_result[{v['task_id']}]",ai_cost_usd=v['reported_cost'],ai_cost_basis='reported',ai_cost_date='2025-04-21',human_cost_basis='not_available',attention_context=context,attention_ratio=attn/weights)
 scores=re.findall(r'FINAL SCORE\]:\s*(\d+)',str(v['evaluation']['log_info']))
 r['performance_evidence']=f"One executed submission passed the task evaluator; three visual comparisons scored {', '.join(scores)} out of 100. Human baseline assumes an expert produces an analysis program and plot of comparable quality."
 r['notes']='Human time estimates the inspected program and reported output quality; the original plot was unavailable for direct inspection.'
 if v['task_id']=='83':r['notes']+=' Visual judges reported a lower, narrower temperature range than the reference.'
 if v['task_id']=='84':r['notes']+=' The source judged the map, not the scientific validity of the band-selection and polygon-threshold heuristics.'
 rows.append(r)
with open(a.output,'w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=headers);w.writeheader();w.writerows(rows)
for r in rows:print(r['point_id'],r['compute_flops'],r['human_time'],r['tokens'])
