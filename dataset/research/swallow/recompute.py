"""Read-only Swallow reconstruction. Python standard library; explicit retained inputs."""
import argparse,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
s=a.sources.resolve();o=a.output.resolve()
if o.exists() or o.is_relative_to(s):raise SystemExit('Output must be new and outside sources')
c=json.loads((s/'config.json').read_text());d=c['hidden_size'];f=c['intermediate_size'];l=c['num_hidden_layers'];v=c['vocab_size'];k=d*c['num_key_value_heads']//c['num_attention_heads'];seq=4096
linear=l*(2*d*d+2*d*k+3*d*f)+d*v
params=l*(2*d*d+2*d*k+3*d*f+2*d)+2*d*v+d
forward=2*linear+2*l*d*(seq+1)
# Paper Table 2/3 instance counts. English multiple-choice branches are explicit.
ja=[1119,120,198,4442,766,250,1000,993]
en=[500*4,17944,11873,10042*4,2325*2,1319]
# Five trained Japanese checkpoints, one baseline; final and baseline English.
# Mean 2048 processed positions/sequence is assumed, not recovered tokenization.
eval_tokens=(6*sum(ja)+2*sum(en))*2048
# Unreported loss-monitoring: one 4M-token equivalent per 1000 updates, 24 assessments.
updates=100_000_000_000/(1024*4096)
monitor_tokens=24*1024*4096
reported_training=5e22
associated=(eval_tokens+monitor_tokens)*forward
# Observed reading programs provide context, not timing donors for the target.
reading_minutes=[25*60+16,23*60+28,33*60+30,26*60+26,21*60+37,46*60+52,17*60+6,19*60+17]
result={'parameter_count':params,'forward_flops_per_token_4096':forward,'training_tokens':100_000_000_000,'implied_updates':updates,'source_reported_training_flops':reported_training,'evaluation_tokens_assumed':eval_tokens,'monitor_tokens_assumed':monitor_tokens,'associated_flops':associated,'total_flops_unrounded':reported_training+associated,'total_flops_rounded':float(f'{reported_training+associated:.2g}'),'associated_fraction':associated/reported_training,'training_crosschecks':{'three_forward':3*forward*1e11,'four_forward':4*forward*1e11},'scenarios':{'no_extra_monitoring':reported_training+eval_tokens*forward,'all_five_checkpoints_English_4096positions_and_10x_loss_monitoring':reported_training+((6*sum(ja)+6*sum(en))*4096+10*monitor_tokens)*forward},'human':{'source_reading_minutes':reading_minutes,'source_mean_hours':sum(reading_minutes)/8/60,'target_hours':60,'components_hours':{'contextual_reading':30,'focused_lexical_and_expression_practice':20,'mixed_unseen_question_practice_and_feedback':10},'scenario_hours':[20,200],'evidence':'assumed','method':'estimated','statistic':'point_estimate','time_subset':'not_applicable','timing_attempts':'not_applicable','contextual_reading_program_count':8,'contextual_timing_role':'Feasible reading-program scale; no observed or calibrated duration for the target accuracy transition','starting_cohort':'Adult learning Japanese as an additional language, already near 86.9% accuracy with remaining vocabulary, idiom and cultural-knowledge gaps','comparison_issues':['different_inputs_or_tools']},'source_sha256':{n:hashlib.sha256((s/n).read_bytes()).hexdigest() for n in ['config.json','paper.pdf','human-reading.pdf','human-modes.pdf','jcqa-valid.jsonl']}}
o.write_text(json.dumps(result,indent=2)+'\n')
