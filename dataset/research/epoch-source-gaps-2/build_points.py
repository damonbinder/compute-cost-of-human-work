#!/usr/bin/env python3
"""Build CSV cell matrices from reviewed schemas and retained calculations."""
import argparse,csv,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,required=True);p.add_argument('--research',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
with (a.dataset/'points.csv').open(newline='') as f:headers=next(csv.reader(f))
calc=json.load(open(a.research/'calculations.json'));sel=json.load(open(a.research/'selection.json'));rows=[]
for spec in sel:
 id=spec['point_id'];v=calc['points'][id];score=float(v['source_row']['Best score (across scorers)']);r={h:'' for h in headers}
 desc='Answer one question from the 198-question GPQA Diamond set, using the question and four choices in one AI generation. Human baseline is a researcher from another scientific domain using non-AI web research, listing useful sources and optionally giving feedback.'
 if spec['identifier']=='o1-2024-12-17_high':desc+=' AI uses high reasoning effort.'
 if spec['identifier']=='open-mixtral-8x7b':desc+=' AI is the source table API configuration, distinct from its HF-style Instruct v0.1 record.'
 notes='Input is reconstructed from the author evaluator plus 12 assumed wrapper positions; native input/cache/retry counters are absent. All input is treated as fresh. Diamond selection partly uses these human validators\' errors.'
 if any(word in spec['tokenizer_qualification'].lower() for word in ['proxy','mirror','unresolved']):notes+=' '+spec['tokenizer_qualification']
 r.update(point_id=id,task='GPQA Diamond question',task_category='research_analysis',task_description=desc,model_id=spec['model_id'],compute_scope='inference',compute_flops=v['compute_flops'],human_skill='novice',human_time_scope='task_performance',human_time=calc['human']['mean_seconds'],performance_vs_human=v['performance_vs_human'],comparison_issues='different_task; different_inputs_or_tools; different_assessment',compute_evidence='derived_assumed_inputs',human_time_evidence='task_timings',performance_evidence=f"AI accuracy {score*100:.4f}%; domain-novice human validators answered 131/594 correctly (22.05%). Four-choice guessing is 25%.",human_time_statistic='mean',human_time_subset='all',human_attempts=594,human_time_source='research/gpqa-source-gaps-2.md#human-baseline',human_time_method='other_calculation',compute_method='params_tokens',compute_statistic='mean',compute_subset='not_applicable',ai_attempts='not_applicable',compute_source='research/gpqa-source-gaps-2.md#'+id,tokens=v['tokens'],tokens_accounting='input_output',source_dataset='Epoch AI original output-length table / GPQA Diamond',source_record=f"https://epoch.ai/data-insights/output-length; scatter_data.csv Identifier={spec['identifier'].strip()}, Benchmark=GPQA diamond; performance: Best score (across scorers); human validation fields in https://openaipublic.blob.core.windows.net/simple-evals/gpqa_diamond.csv",notes=notes)
 rows.append([r[h] for h in headers])
with a.output.open('x') as f:json.dump({'points':[headers]+rows},f,indent=2);f.write('\n')
