#!/usr/bin/env python3
"""Recompute four source-table GPQA gaps from retained original evidence.
Requires tokenizers; no inference or API calls. Writes a new file outside sources.
"""
import argparse,csv,json,statistics,hashlib
from pathlib import Path
from tokenizers import Tokenizer
p=argparse.ArgumentParser();p.add_argument('sources',type=Path);p.add_argument('--models',type=Path,required=True);p.add_argument('--selection',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=a.sources
if a.output.resolve().is_relative_to(s.resolve()):raise ValueError('Output must be outside source directory')
gp=list(csv.DictReader(open(s/'gpqa_diamond.csv')));assert len(gp)==198
prefix="Answer the following multiple choice question. The last line of your response should be of the following format: 'ANSWER: $LETTER' (without quotes) where LETTER is one of A,B,C,D. Think step by step before answering.\n\n"
choices=['Correct Answer','Incorrect Answer 1','Incorrect Answer 2','Incorrect Answer 3']
qs=[prefix+r['Question']+'\n\n'+'\n'.join(chr(65+i)+') '+r[k] for i,k in enumerate(choices)) for r in gp]
times=[float(r[f'Self-reported time (minutes)_NEV_{i}'])*60 for r in gp for i in [1,2,3]];correct=sum(float(r[f'Validator Answered Correctly_NEV_{i}']) for r in gp for i in [1,2,3]);table=list(csv.DictReader(open(s/'scatter_data.csv')));models={r['model_id']:r for r in csv.DictReader(open(a.models))};sel=json.load(open(a.selection));results={}
for r in sel:
 tok=Tokenizer.from_file(str(s/r['tokenizer']));counts=[len(tok.encode(q,add_special_tokens=False).ids)+12 for q in qs];found=[x for x in table if x['Identifier']==r['identifier'] and x['Benchmark']=='GPQA diamond'];assert len(found)==1;x=found[0];inp=statistics.mean(counts);out=float(x['Output tokens per question']);coef=float(models[r['model_id']]['flops_per_token']);assert coef==2*float(models[r['model_id']]['active_parameters'])
 results[r['point_id']]={'model_id':r['model_id'],'source_row':x,'input_tokens':inp,'output_tokens':out,'tokens':inp+out,'coefficient':coef,'compute_flops':(inp+out)*coef,'input_counts':counts,'twenty_wrapper_positions_sensitivity_fraction':20/(inp+out)}
result={'human_attempts':len(times),'human_time':statistics.mean(times),'human_median':statistics.median(times),'human_correct':correct,'human_accuracy':correct/len(times),'times_below15minutes':sum(x<900 for x in times),'points':results,'source_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in s.iterdir() if f.is_file()}}
with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print({k:{q:v for q,v in x.items() if q!='input_counts'} for k,x in results.items()})
