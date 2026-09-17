"""Reconstruct original sample evidence and estimated Minerva workloads; no model calls.
Dependencies: tiktoken, pyarrow. Explicit source directory and new output file.
"""
import argparse,json,re,statistics,hashlib,base64,collections
from pathlib import Path
import tiktoken
import pyarrow.parquet as pq
p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=a.sources.resolve();o=a.output.resolve()
if o.exists() or o.is_relative_to(s):raise SystemExit('Output must be new, outside sources')
raw=json.loads((s/'explorer.js.map').read_text());c=raw['sourcesContent'][raw['sources'].index('webpack:///./src/examples.js')]
# Original source array includes disabled whole-line and block-commented examples.
c='\n'.join(l for l in c.splitlines() if not l.lstrip().startswith('//'));c=re.sub(r'/\*.*?\*/','',c,flags=re.S);c=c[c.index('['):c.rfind(']')+1];examples=json.loads(re.sub(r',\s*]',']',c))
assert len(examples)==326
math=[]
for f in sorted(s.glob('math-test-*.parquet')):math+=pq.read_table(f).to_pylist()
assert len(math)==5000
text=(s/'paper.txt').read_text();part=text[text.index('1 Problem:\n2 Find the domain'):text.index('Listing 2: 4-shot')];lines=[];n=1
for line in part.splitlines():
 m=re.match(r'^(\d+)(?: (.*))?$',line)
 if m and int(m[1])==n:lines.append(m[2] or '');n+=1
assert n==52
prompt='\n'.join(lines)+'\n\nProblem:\n'
result={'model_parameters_reported':62500000000,'prompt_reconstructed':prompt,'native_input_cap':1024,'native_output_cap':512,'human_seconds':180,'human_interpretation':'Estimated active use of one allotted60-minute20-question paper; no individual completion timestamps.','tokenizer_results':{}}
for name in ['cl100k_base','p50k_base']:
 definition=json.loads((s/'tokenizer-definitions.json').read_text())[name]; ranks={base64.b64decode(x.split()[0]):int(x.split()[1]) for x in (s/(name+'.tiktoken')).read_bytes().splitlines()};enc=tiktoken.Encoding(name=name,pat_str=definition['pattern'].replace(r'\p{N}{1,3}',r'\p{N}').replace(r'\p{N}+',r'\p{N}'),mergeable_ranks=ranks,special_tokens={});counts=[min(1024,len(enc.encode(prompt+x['problem']+'\n\nSolution:\n'))) for x in math];groups={}
 for model in ['64b','540b']:
  for kind in ['all','Correct','Incorrect','False Positive']:
   b=[x for x in examples if x['source']=='MATH' and x['model']==model and (kind=='all' or x['type']==kind)]
   if b:groups[model+'_'+kind]={'n':len(b),'mean_output_proxy_tokens':statistics.mean(len(enc.encode(x['output'])) for x in b),'max_output_proxy_tokens':max(len(enc.encode(x['output'])) for x in b)}
 result['tokenizer_results'][name]={'input_mean':statistics.mean(counts),'input_cap_count':sum(x==1024 for x in counts),'output_groups':groups}
i=result['tokenizer_results']['cl100k_base']['input_mean'];coef=125e9
# Tail/selection reconstruction uses distinct540B question outputs, not duplicate gallery records.
definition=json.loads((s/'tokenizer-definitions.json').read_text())['cl100k_base']
ranks={base64.b64decode(x.split()[0]):int(x.split()[1]) for x in (s/'cl100k_base.tiktoken').read_bytes().splitlines()}
enc=tiktoken.Encoding(name='digitwise-proxy',pat_str=definition['pattern'].replace(r'\p{N}{1,3}',r'\p{N}').replace(r'\p{N}+',r'\p{N}'),mergeable_ranks=ranks,special_tokens={})
groups=collections.defaultdict(dict)
for x in examples:
 if x['source']=='MATH' and x['model']=='540b':groups[x['question']][x['output']]=len(enc.encode(x['output']))
lengths=[statistics.mean(v.values()) for v in groups.values()]
longest=lambda factor:statistics.mean(min(512,factor*n) for n in lengths)
paired=[{'question':q,'distinct_output_lengths':list(v.values()),'long_short_ratio':max(v.values())/min(v.values())} for q,v in groups.items() if len(v)>1]
result.update(input_tokens_estimated=i,output_tokens_per_sample_estimated=170,configurations={},gallery_length_evidence={'unique540b_questions':len(groups),'unique540b_outputs':sum(len(v) for v in groups.values()),'question_weighted_mean_length':statistics.mean(lengths),'paired_examples':paired,'tail_factor_assumed':2,'longest_group_steps_assumed':longest(2)})
# Source-era T5X: one padded prefill before num_decodes fanout, then all branches
# remain in the batch until the longest ends. Both choices are transferred execution assumptions.
for k in [1,256]:
 steps=170 if k==1 else longest(2)
 positions=1536+k*steps
 result['configurations'][str(k)]={'tokens':positions,'flops':coef*positions,'prefill_groups_assumed':1,'prefill_positions_per_group_assumed':1536,'decode_steps_per_branch_assumed':steps,'unpadded_shared_prefill_flops':coef*(i+k*steps),'no_tail_inflation_flops':coef*(1536+k*(170 if k==1 else longest(1))),'longer_output_flops':coef*(1536+k*(320 if k==1 else longest(3))),'native512cap_flops':coef*(1536+k*512),'four_prefill_groups_same_tail_flops':coef*(min(k,4)*1536+k*steps),'sixteen_prefill_groups_same_tail_flops':coef*(min(k,16)*1536+k*steps),'independent_calls_padded_prefill_flops':coef*k*(1536+170),'old_compact_full_prefix_flops':coef*k*(i+170),'position_proxy_minus25pct_flops':coef*(1536+k*(127.5 if k==1 else longest(1.5))),'position_proxy_plus25pct_flops':coef*(1536+k*(212.5 if k==1 else longest(2.5)))}
result['source_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(s.iterdir()) if p.is_file() and p.suffix in ['.parquet','.map','.pdf','.txt','.py','.tiktoken']}
o.write_text(json.dumps(result,indent=2)+'\n')
