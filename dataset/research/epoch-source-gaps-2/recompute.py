#!/usr/bin/env python3
"""Offline GPQA workload reconstruction. Requires tokenizers, sentencepiece, tiktoken.
Run with explicit sources, selection, models CSV and a new output path.
Source files and existing output files are never overwritten.
"""
import argparse,ast,base64,csv,hashlib,json,statistics
from pathlib import Path
import tokenizers,sentencepiece,tiktoken

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read_csv(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))
def openai_encoding(s,name):
    # Read only literal regex nodes from the retained official implementation.
    tree=ast.parse((s/'openai_public.py').read_text())
    fun=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==name)
    if name=='cl100k_base':
        ret=next(x for x in fun.body if isinstance(x,ast.Return)).value
        pattern=ast.literal_eval(next(v for k,v in zip(ret.keys,ret.values) if isinstance(k,ast.Constant) and k.value=='pat_str'))
    else:
        call=next(x.value for x in fun.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='pat_str' for t in x.targets))
        pattern='|'.join(ast.literal_eval(call.args[0]))
    ranks={base64.b64decode(a):int(b) for a,b in (line.split() for line in (s/(name+'.tiktoken')).read_bytes().splitlines())}
    return tiktoken.Encoding(name=name,pat_str=pattern,mergeable_ranks=ranks,special_tokens={})
def tokenizer(s,item):
    kind=item['tokenizer_type'];name=item['tokenizer']
    if kind=='tiktoken':
        enc=openai_encoding(s,name);return lambda q:len(enc.encode_ordinary(q))
    if kind=='sentencepiece':
        enc=sentencepiece.SentencePieceProcessor(model_file=str(s/name));return lambda q:len(enc.encode(q,out_type=int))
    enc=tokenizers.Tokenizer.from_file(str(s/name));return lambda q:len(enc.encode(q,add_special_tokens=False).ids)
def main():
    p=argparse.ArgumentParser();p.add_argument('sources',type=Path);p.add_argument('--selection',required=True,type=Path);p.add_argument('--models',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();s=a.sources.resolve()
    if a.output.resolve().is_relative_to(s):raise ValueError('Output must be outside source directory')
    if a.output.exists():raise FileExistsError(a.output)
    gp=read_csv(s/'gpqa_diamond.csv');assert len(gp)==198 and len({r['Record ID'] for r in gp})==198
    gist=json.load(open(s/'gpqa-gist.json'));code=gist['files']['gpqa.py']['content']
    tree=ast.parse(code);assign=next(x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SIMPLE_COT_TEMPLATE' for t in x.targets));template=ast.literal_eval(assign.value.func.value).strip()
    keys=['Correct Answer','Incorrect Answer 1','Incorrect Answer 2','Incorrect Answer 3']
    prompts=[template.format(letters='A,B,C,D',question=r['Question'],choices='\n'.join(chr(65+i)+') '+r[k] for i,k in enumerate(keys))) for r in gp]
    mins=[float(r[f'Self-reported time (minutes)_NEV_{i}']) for r in gp for i in (1,2,3)];correct=[int(float(r[f'Validator Answered Correctly_NEV_{i}'])) for r in gp for i in (1,2,3)]
    assert all(v>0 for v in mins) and set(correct)<={0,1}
    table=read_csv(s/'scatter_data.csv');models={r['model_id']:r for r in read_csv(a.models)};sel=json.load(open(a.selection));cache={};points={}
    for spec in sel:
        found=[r for r in table if r['Identifier']==spec['identifier'] and r['Benchmark']=='GPQA diamond'];assert len(found)==1;row=found[0]
        tk=(spec['tokenizer_type'],spec['tokenizer'])
        if tk not in cache:
            enc=tokenizer(s,spec);cache[tk]=[enc(q)+12 for q in prompts]
        counts=cache[tk];inp=statistics.mean(counts);out=float(row['Output tokens per question']);coef=float(models[spec['model_id']]['flops_per_token']);assert coef==2*float(models[spec['model_id']]['active_parameters'])
        score=float(row['Best score (across scorers)']);human=statistics.mean(correct)
        label='match' if abs(score-human)<=0.05 else ('above' if score>human else 'below')
        points[spec['point_id']]={'source_row':row,'model_id':spec['model_id'],'input_tokens':inp,'output_tokens':out,'tokens':inp+out,'coefficient':coef,'compute_flops':(inp+out)*coef,'input_counts':counts,'performance_vs_human':label,'wrapper_plusminus20_fraction':20/(inp+out),'half_input_fraction':.5*inp/(inp+out),'half_input_flops':(0.5*inp+out)*coef,'onepointfive_input_flops':(1.5*inp+out)*coef}
    qwen={}
    for size in [32,72]:
        c=json.load(open(s/f'models/Qwen--Qwen1.5-{size}B-Chat--config.json'));h=c['hidden_size'];l=c['num_hidden_layers'];kv=h//c['num_attention_heads']*c['num_key_value_heads'];d=c['intermediate_size'];v=c['vocab_size'];assert c['model_type']=='qwen2' and not c['tie_word_embeddings']
        # Decoder Q/K/V/O, SwiGLU, QKV biases, RMS norms and untied embeddings/head.
        params=2*v*h+l*(2*h*h+2*h*kv+3*h*d+h+2*kv+2*h)+h
        qwen[str(size)]={'config_dimensions':{k:c[k] for k in ['hidden_size','num_hidden_layers','num_attention_heads','num_key_value_heads','intermediate_size','vocab_size']},'architecture_parameter_check':params,'shared_coefficient_uses_rounded_reported_count':size*10**9}
    result={'human':{'attempts':len(mins),'mean_seconds':statistics.mean([60*x for x in mins]),'median_seconds':60*statistics.median(mins),'correct':sum(correct),'accuracy':statistics.mean(correct),'times_below15minutes':sum(x<15 for x in mins)},'points':points,'qwen_architecture':qwen,'evaluator_revision':gist['history'][0]['version'],'source_sha256':{str(f.relative_to(s)):sha(f) for f in sorted(s.rglob('*')) if f.is_file()},'versions':{'tokenizers':tokenizers.__version__,'sentencepiece':sentencepiece.__version__,'tiktoken':tiktoken.__version__}}
    with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'human':result['human'],'points':{k:{q:v[q] for q in ['tokens','compute_flops','performance_vs_human']} for k,v in points.items()},'qwen_architecture':qwen},indent=2))
if __name__=='__main__':main()
