#!/usr/bin/env python3
"""Reconstruct book-name cloze workload. Requires tiktoken; no API calls."""
import argparse,ast,hashlib,json,statistics
from pathlib import Path
import tiktoken
from tiktoken.load import load_tiktoken_bpe
p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=a.sources.resolve();out=a.output.resolve()
if out.exists() or out.is_relative_to(s):p.error('Output must be new and outside sources.')
manifest=json.loads((s/'manifest.json').read_text())
for x in manifest:
 f=(s/x['path']).resolve();assert f.is_relative_to(s);assert hashlib.sha256(f.read_bytes()).hexdigest()==x['sha256']
definition=json.loads((s/'tokenizer-definition.json').read_text());enc=tiktoken.Encoding(name='retained_cl100k',mergeable_ranks=load_tiktoken_bpe(str(s/'cl100k_base.tiktoken')),**definition)
tree=ast.parse((s/'scripts--openai_predict_name_cloze.py').read_text());fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='predict');template=ast.literal_eval(fn.body[0].value.left)
git={x['path']:x for x in json.loads((s/'tree.json').read_text())['tree']};records=[];files={}
for f in sorted((s/'gpt4-results').glob('*.txt')):
 b=f.read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==git['data/model_output/gpt4_results/'+f.name]['sha']
 rows=[x.split('\t') for x in f.read_text().splitlines()];assert all(len(x)==4 for x in rows);files[f.name]=len(rows)
 for i,(raw,pred,truth,passage) in enumerate(rows):
  records.append({'file':f.name,'row':i+1,'input':len(enc.encode(template%passage,disallowed_special=()))+8,'output':len(enc.encode(raw,disallowed_special=())),'words':len(passage.split()),'exact_correct':pred==truth,'casefold_correct':pred.casefold()==truth.casefold()})
assert len(files)==91 and len(records)==9057
means={k:statistics.mean(x[k] for x in records) for k in ['input','output','words','exact_correct','casefold_correct']};tokens=means['input']+means['output'];reading=means['words']*60/260
r={'files':files,'n':len(records),'means':means,'tokens':tokens,'coefficient':550000000000,'compute_flops':tokens*550000000000,'human_time':reading+12+3,'human_components':{'reading_seconds_at_260wpm':reading,'retrieval_and_guess_seconds_assumed':12,'enter_name_seconds_assumed':3},'human_scenarios':{'quick_at_320wpm_plus_5_seconds':means['words']*60/320+5,'deliberative_at_180wpm_plus_35_seconds':means['words']*60/180+35},'compute_scenarios':{'wrapper_4':(tokens-4)*550000000000,'wrapper_16':(tokens+8)*550000000000,'active_100B':tokens*200000000000,'active_550B':tokens*1100000000000},'records':records}
out.write_text(json.dumps(r,indent=2)+'\n');print({k:v for k,v in r.items() if k not in ['files','records']})
