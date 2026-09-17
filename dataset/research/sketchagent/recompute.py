#!/usr/bin/env python3
"""Reconstruct reported-price SketchAgent compute and transferred human time.
Python3 + tiktoken. No model calls. All source paths explicit; output new.
"""
import argparse,ast,hashlib,json,subprocess,sys,tempfile,unicodedata,statistics
from pathlib import Path
import tiktoken
from tiktoken.load import load_tiktoken_bpe
p=argparse.ArgumentParser();p.add_argument('--sources',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();s=a.sources.resolve();out=a.output.resolve()
if out.exists() or out.is_relative_to(s):p.error('Output must be new and outside sources.')
for x in json.loads((s/'manifest.json').read_text()):
 f=(s/x['path']).resolve();assert f.is_relative_to(s);assert hashlib.sha256(f.read_bytes()).hexdigest()==x['sha256']
with tempfile.TemporaryDirectory(prefix='sketchagent-human-') as tmp:
 hp=Path(tmp)/'human.json';subprocess.run([sys.executable,str(Path(__file__).with_name('audit_human.py')),'--sources',str(s/'human'),'--output',str(hp)],check=True,capture_output=True);human=json.loads(hp.read_text())
c=json.loads((s/'anthropic-legacy-claude.json').read_text());e=tiktoken.Encoding(name='retained_legacy',pat_str=c['pat_str'],mergeable_ranks=load_tiktoken_bpe(str(s/'anthropic-legacy-claude.tiktoken')),special_tokens=c['special_tokens'],explicit_n_vocab=c['explicit_n_vocab'])
tree=ast.parse((s/'prompts.py').read_text());v={x.targets[0].id:ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign)}
count=lambda t:len(e.encode(unicodedata.normalize('NFKC',t),allowed_special='all'))
system=count(v['system_prompt'].format(res=50));cats=json.loads((s/'human/selected-timing-categories.json').read_text());counts={cat:system+count(v['sketch_first_prompt'].format(concept=cat,gt_sketches_str=v['gt_example']))+12 for cat in cats};inp=statistics.mean(counts.values())
def budget(cost=.05,input_positions=inp,calls=1,active=100e9):
 pin=input_positions*calls;output=(cost-pin*3e-6)/15e-6;assert output>0
 return {'input':pin,'output_price_inferred':output,'tokens':pin+output,'flops':2*active*(pin+output)}
b=budget();assert b['output_price_inferred']<=3000
r={'human':human,'input_counts':counts,'system_tokens_proxy':system,'mean_input_tokens_proxy_including12wrapper':inp,'reported_mean_dollars':.05,'input_dollars_per_million':3,'output_dollars_per_million':15,'central':b,'human_time':human['mean_plus2seconds_initial_planning'],'scenarios':{'cost_rounded_low':budget(.045),'cost_rounded_high':budget(.055),'input_tokenizer_80percent':budget(input_positions=inp*.8),'input_tokenizer_120percent':budget(input_positions=inp*1.2),'two_input_prefixes_same_reported_total_cost':budget(calls=2),'three_input_prefixes_same_reported_total_cost':budget(calls=3),'active50B':budget(active=50e9),'active200B':budget(active=200e9)}}
out.write_text(json.dumps(r,indent=2)+'\n');print({k:v for k,v in r.items() if k not in ['human','input_counts']})
