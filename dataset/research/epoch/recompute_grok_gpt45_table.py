"""Recount retained GPT-4.5/Grok task text and Grok-2 tensor metadata.

python -B recompute_grok_gpt45_table.py /path/to/epoch/sources --output counts.json
Requires tiktoken and pyarrow. No network calls or production writes.
"""
import argparse,ast,csv,hashlib,importlib.util,json,math,re,statistics
from pathlib import Path
import tiktoken
from tiktoken.load import load_tiktoken_bpe
import pyarrow.parquet as pq

PREFIX=("Answer the following multiple choice question. The last line of your "
        "response should be of the following format: 'ANSWER: $LETTER' "
        "(without quotes) where LETTER is one of A,B,C,D. Think step by step "
        "before answering.\n\n")
CHOICES=['Correct Answer','Incorrect Answer 1','Incorrect Answer 2','Incorrect Answer 3']

def parameter_count(s):
    folder=s/'grok-gpt45-models'
    config=json.loads((folder/'grok2-config.json').read_text())
    assert (config['num_hidden_layers'],config['num_local_experts'],config['num_experts_per_tok'])==(64,8,2)
    assert config['residual_moe'] is True
    shared=expert_total=0;groups={};expert_pieces={}
    manifest=json.loads((folder/'grok2-headers/manifest.json').read_text())
    for row in manifest:
        path=s/Path(row['file']).relative_to('sources')
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
        for name,tensor in json.loads(path.read_text()).items():
            if name=='__metadata__':continue
            size=math.prod(tensor['shape'])
            assert tensor['dtype']=='BF16'
            key=re.sub(r'\.\d+','.#',name)
            groups[key]=groups.get(key,0)+size
            if '.experts.' in name:
                expert_total+=size
                expert_pieces[name]=expert_pieces.get(name,0)+size
            else:shared+=size
    # The eight TP files contain pieces of each expert, not eight copies.
    assert len(expert_pieces)==64*8*3
    assert set(expert_pieces.values())=={8192*16384}
    dense_ffn=64*3*8192*32768
    assert sum(v for k,v in groups.items() if '.mlp.' in k)==dense_ffn
    active=shared+expert_total*config['num_experts_per_tok']//config['num_local_experts']
    assert (shared,expert_total,active)==(63357067264,206158430208,114896674816)
    return {'shared':shared,'routed_expert_total':expert_total,'routed_fraction':2/8,
            'active_parameters':active,'total_parameters':shared+expert_total,'groups':groups,
            'tensor_header_count':len(manifest)}

def compute(sources):
    s=Path(sources);folder=s/'grok-gpt45-models';hashes={}
    for name,expected in [
      ('small-models/openai_public.py','954392738e60d0fb6dca1dad80872efc47c8e2733babecbbf0a23970ed66c2cb'),
      ('small-models/o200k_base.tiktoken','446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d')]:
        actual=hashlib.sha256((s/name).read_bytes()).hexdigest();assert actual==expected;hashes[name]=actual
    spec=importlib.util.spec_from_file_location('retained_openai_public',s/'small-models/openai_public.py')
    definitions=importlib.util.module_from_spec(spec);spec.loader.exec_module(definitions)
    definitions.load_tiktoken_bpe=lambda url,expected_hash=None:load_tiktoken_bpe(str(s/'small-models'/url.rsplit('/',1)[1]),expected_hash=expected_hash)
    openai=tiktoken.Encoding(**definitions.o200k_base())
    original_code=ast.parse((folder/'sglang-tokenizer.py').read_text())
    pattern=next(ast.literal_eval(n.value) for n in original_code.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAT_STR_B' for t in n.targets))
    vocabulary=json.loads((folder/'grok2-tokenizer.tok.json').read_text());assert vocabulary['word_split']=='V1'
    grok=tiktoken.Encoding(name='retained_grok2',pat_str=pattern,
         mergeable_ranks={bytes(x['bytes']):x['token'] for x in vocabulary['regular_tokens']},
         special_tokens={bytes(x['bytes']).decode():x['token'] for x in vocabulary['special_tokens']},
         explicit_n_vocab=vocabulary['vocab_size'])
    gpqa=list(csv.DictReader((s/'gpqa_diamond.csv').open()))
    math_paths=sorted(s.glob('math-test-*.parquet'))
    math_rows=[r for p in math_paths for r in pq.read_table(p).to_pylist() if r['level']=='Level 5']
    otis=json.loads((s/'otis-original-question-text.json').read_text())['questions']
    assert (len(gpqa),len(math_rows),len(otis))==(198,1324,45)
    prompts={'gpqa':[PREFIX+r['Question']+'\n\n'+'\n'.join(f'{chr(65+i)}) {r[k]}' for i,k in enumerate(CHOICES)) for r in gpqa],
             'mathl5':[r['problem'] for r in math_rows],
             'otis':[r['observed_instruction_before']+r['question']+r['observed_instruction_after'] for r in otis]}
    wrappers={'gpqa':12,'mathl5':50,'otis':12}
    counts={key:{b:[len(tok.encode(t,disallowed_special=()))+wrappers[b] for t in texts] for b,texts in prompts.items()} for key,tok in [('o200k',openai),('grok2',grok)]}
    files=[s/'gpqa_diamond.csv',s/'gpqa-gist.json',s/'otis-original-question-text.json',s/'scatter_data.csv',*math_paths,
           folder/'grok2-config.json',folder/'grok2-tokenizer.tok.json',folder/'sglang-tokenizer.py',folder/'grok2-hf-api.json']
    for f in files:hashes[str(f.relative_to(s))]=hashlib.sha256(f.read_bytes()).hexdigest()
    return {'tiktoken_version':tiktoken.__version__,'sha256':hashes,'assumed_wrapper_positions':wrappers,
            'gpqa_instruction':PREFIX,'gpqa_fixed_choice_order':CHOICES,'otis_question_ids':[r['id'] for r in otis],
            'otis_wrapper_is_transferred_from_later_same_benchmark_log':True,
            'means':{k:{b:statistics.mean(x) for b,x in rows.items()} for k,rows in counts.items()},
            'counts_including_wrapper':counts,'grok2_parameters':parameter_count(s)}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('sources',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=compute(args.sources)
    if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'means':result['means'],'grok2_parameters':result['grok2_parameters']},indent=2))
