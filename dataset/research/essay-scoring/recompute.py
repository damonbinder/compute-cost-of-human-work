import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
def flops(s):
 h=768;l=12
 return {'linear_layers':l*24*s*h*h,'attention_products':l*4*s*s*h,'pooler':2*h*h,'score_head':2*h}
r={str(s):dict(flops(s),total=sum(flops(s).values())) for s in [350,448,512]}
out={'sequence_length_assumed':512,'compute_flops':r['512']['total'],'sequence_scenarios':r,'human_seconds':200,'human_seconds_scenarios':[120,300],'human_component_judgments':{'read_350_words_at_200_wpm':105,'apply_familiar_rubric':75,'check_enter_score':20},'external_GRE_mean_seconds':203.82}
with a.output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps(out,indent=2))
