"""Reconstruct four short-task averages; no API calls. Requires tiktoken."""
import argparse,csv,json,hashlib,statistics
from pathlib import Path
import tiktoken
from fractions import Fraction
p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--models',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
s=a.sources.resolve();o=a.output.resolve()
if o.exists() or o.is_relative_to(s):raise SystemExit('Output must be new and outside sources')
models={r['model_id']:r for r in csv.DictReader(a.models.open())}
enc=tiktoken.get_encoding('o200k_base');tasks={r['prompt_id']:r for r in json.load(open(s/'tasks.json'))['prompts']}
selected=['one_plus_one','bridge_torch_easy_10m'];result=[]
for filename,name,mid in [('output-gpt5.json','gpt-5','gpt-5'),('output-o3m-o1m.json','o3-mini-high','o3-mini-2025-01-31')]:
 for r in json.load(open(s/filename))['results']:
  if r['llm']!=name or r['prompt_id'] not in selected:continue
  task=tasks[r['prompt_id']];assert r['prompt']==task['prompt']
  assert len(r['output'])==len(r['tokens_completion'])==5
  assert all(x=='stop' for x in r['finish_reason'])
  assert all(x=='OpenAI' for x in r['provider'])
  prompt='Please answer the following question: '+r['prompt']+'\nAnswer:'
  # Native output already includes reasoning; do not add details again.
  out=r['tokens_completion'];reason=[x['reasoning_tokens'] for x in r['completion_tokens_details']]
  assert all(x>=y>=0 for x,y in zip(out,reason))
  # Text count is reconstructed. Seven message/frame positions are assumed.
  text_n=len(enc.encode(prompt));input_n=text_n+7
  coeff=float(models[mid]['flops_per_token']);total=[input_n+n for n in out]
  result.append(dict(point_id='short-'+r['prompt_id'].replace('_','-')+'-'+name,model_id=mid,prompt_id=r['prompt_id'],prompt=prompt,prompt_text_tokens=text_n,message_overhead_assumed=7,input_tokens_estimated=input_n,completion_tokens_native=out,reasoning_tokens_already_in_completion=reason,mean_tokens=statistics.mean(total),flops_per_token=coeff,mean_flops=float(Fraction(sum(total),len(total))*Fraction(models[mid]['flops_per_token'])),input_overhead_0_flops=(text_n+statistics.mean(out))*coeff,input_overhead_64_flops=(text_n+64+statistics.mean(out))*coeff,human_seconds_assumed=3 if r['prompt_id']=='one_plus_one' else 25,human_seconds_scenarios=[1.5,6] if r['prompt_id']=='one_plus_one' else [12,60],responses=r['output'],generation_ids=r['id'],source_timestamp=r['timestamp']))
assert len(result)==4
j={'convention':'Native completion counters include reasoning once; reconstructed single-user prompt plus seven assumed framing positions; shared parameter coefficients.','points':result,'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(s.iterdir()) if p.is_file()},'models_sha256':hashlib.sha256(a.models.read_bytes()).hexdigest()}
o.write_text(json.dumps(j,indent=2)+'\n')
