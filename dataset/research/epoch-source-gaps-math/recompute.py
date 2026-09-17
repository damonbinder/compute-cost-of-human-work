#!/usr/bin/env python3
"""Read-only reconstruction of four original Epoch source-table gaps.
Requires tokenizers, sentencepiece, tiktoken and pyarrow. No model inference.
"""
import argparse,csv,json,re,statistics,hashlib
from pathlib import Path
from tokenizers import Tokenizer
import sentencepiece as spm
import tiktoken
from tiktoken.load import load_tiktoken_bpe
import pyarrow.parquet as pq

p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--models',type=Path,required=True);p.add_argument('--selection',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=a.sources
if a.output.resolve().is_relative_to(s.resolve()):raise ValueError('Output must be outside source directory')
sel=json.load(open(a.selection));models={r['model_id']:r for r in csv.DictReader(open(a.models))};table=list(csv.DictReader(open(s/'scatter_data.csv')))
questions=json.load(open(s/'otis-original-question-text.json'))['questions'];assert len(questions)==45
otis=[r['observed_instruction_before']+r['question']+r['observed_instruction_after'] for r in questions]
mathrows=[r for f in sorted(s.glob('math-test-*.parquet')) for r in pq.read_table(f).to_pylist() if r['level']=='Level 5'];assert len(mathrows)==1324
v24=[(int(i),int(n)) for i,n in re.findall(r'Total score = (\d+)\s+(\d+)',(s/'otis-2024-report.txt').read_text())];assert len(v24)==16 and [i for i,n in v24]==list(range(16))
v25=[tuple(map(int,x)) for x in re.findall(r'Total score = (\d+)\s+(\d+)\s+Total score = (\d+)\s+(\d+)',(s/'otis-2025-report.txt').read_text())];assert len(v25)==16 and all(i==j for i,n,j,m in v25)
freq=[[n for i,n in v24],[n for i,n,j,m in v25],[m for i,n,j,m in v25]];human_accuracy=statistics.mean(sum(i*n for i,n in enumerate(f))/sum(f)/15 for f in freq)
definition=json.load(open(s/'o200k-definition.json'));definition.pop('source')
enc=tiktoken.Encoding(name='retained_o200k',mergeable_ranks=load_tiktoken_bpe(str(s/'o200k_base.tiktoken')),**definition)
sp=spm.SentencePieceProcessor(model_file=str(s/'llama2-tokenizer.model'))
deep=Tokenizer.from_file(str(s/'deepseek-tokenizer.json'));mix=Tokenizer.from_file(str(s/'mixtral-tokenizer.json'))
counts={'llama2':lambda t:len(sp.encode(t)), 'o200k':lambda t:len(enc.encode(t,disallowed_special=())), 'deepseek':lambda t:len(deep.encode(t,add_special_tokens=False).ids), 'mixtral':lambda t:len(mix.encode(t,add_special_tokens=False).ids)}
result={'otis_score_frequencies':freq,'otis_human_accuracy':human_accuracy,'otis_human_time':3*3600/15,'math_question_counts':dict(sorted(__import__('collections').Counter(r['type'] for r in mathrows).items())),'points':{}}
for x in sel:
 hits=[r for r in table if r['Identifier'].strip()==x['identifier'] and r['Benchmark']==x['benchmark']];assert len(hits)==1
 r=hits[0];isotis=x['benchmark'].startswith('OTIS');texts=otis if isotis else [r['problem'] for r in mathrows];wrapper=12 if isotis else 50
 ns=[counts[x['tokenizer']](t)+wrapper for t in texts];inp=statistics.mean(ns);out=float(r['Output tokens per question']);co=float(models[x['model_id']]['flops_per_token']);assert co==2*float(models[x['model_id']]['active_parameters'])
 result['points'][x['point_id']]={**x,'source_row':r,'input_tokens':inp,'output_tokens':out,'tokens':inp+out,'coefficient':co,'compute_flops':(inp+out)*co,'human_time':720 if isotis else 600,'input_counts':ns,'wrapper':wrapper,'twenty_position_sensitivity_fraction':20/(inp+out)}
result['source_sha256']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in s.iterdir() if f.is_file()}
with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print({k:{q:v for q,v in r.items() if q in ['input_tokens','output_tokens','compute_flops','human_time']} for k,r in result['points'].items()})
