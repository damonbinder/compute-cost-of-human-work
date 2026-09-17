"""Recompute task input lengths from retained original text and Google/Qwen tokenizers.

Usage: python -B recompute_final_table.py /path/to/epoch/sources --models /path/to/models.csv --output new-counts.json
--models is optional; supply it to reproduce all thirteen FLOP calculations.
Requires sentencepiece, tokenizers and pyarrow. No API calls or production writes.
"""
import argparse,csv,hashlib,json,statistics
from pathlib import Path
import sentencepiece as spm
import tokenizers
from tokenizers import Tokenizer
import pyarrow.parquet as pq

PREFIX=("Answer the following multiple choice question. The last line of your "
        "response should be of the following format: 'ANSWER: $LETTER' "
        "(without quotes) where LETTER is one of A,B,C,D. Think step by step "
        "before answering.\n\n")
CHOICES=['Correct Answer','Incorrect Answer 1','Incorrect Answer 2','Incorrect Answer 3']

def compute(sources):
    s=Path(sources)
    gpqa=list(csv.DictReader((s/'gpqa_diamond.csv').open()))
    math_paths=sorted(s.glob('math-test-*.parquet'))
    math=[r for p in math_paths for r in pq.read_table(p).to_pylist() if r['level']=='Level 5']
    otis=json.loads((s/'otis-original-question-text.json').read_text())['questions']
    assert len(gpqa)==198 and len(math)==1324 and len(otis)==45
    prompts={
      'gpqa':[PREFIX+r['Question']+'\n\n'+'\n'.join(f'{chr(65+i)}) {r[k]}' for i,k in enumerate(CHOICES)) for r in gpqa],
      'mathl5':[r['problem'] for r in math],
      'otis':[r['observed_instruction_before']+r['question']+r['observed_instruction_after'] for r in otis],
    }
    wrappers={'gpqa':12,'mathl5':50,'otis':12}
    counts={}; hashes={}
    for key,expected in [('gemma','61a7b147390c64585d6c3543dd6fc636906c9af3865a5548f27f31aee1d4c8e2'),('gemma3','1299c11d7cf632ef3b4e11937501358ada021bbdf7c47638d13c0ee982f2e79c')]:
        file=s/'gemini-table-models'/f'{key}-tokenizer.model'
        actual=hashlib.sha256(file.read_bytes()).hexdigest();assert actual==expected
        hashes[str(file.relative_to(s))]=actual
        tokenizer=spm.SentencePieceProcessor(model_file=str(file))
        counts[key]={b:[len(tokenizer.encode(text))+wrappers[b] for text in values] for b,values in prompts.items()}
    qwen=s/'final-table-models/qwen25-tokenizer.json'
    digest=hashlib.sha256(qwen.read_bytes()).hexdigest()
    assert digest=='c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539'
    hashes[str(qwen.relative_to(s))]=digest
    qt=Tokenizer.from_file(str(qwen))
    counts['qwen25']={b:[len(qt.encode(text,add_special_tokens=False).ids)+wrappers[b] for text in values] for b,values in prompts.items()}
    for f in [s/'gpqa_diamond.csv' ,s/'gpqa-gist.json',s/'otis-original-question-text.json',s/'scatter_data.csv',*math_paths]:
        hashes[str(f.relative_to(s))]=hashlib.sha256(f.read_bytes()).hexdigest()
    return {'sentencepiece_version':spm.__version__,'tokenizers_version':tokenizers.__version__,'sha256':hashes,'assumed_wrapper_positions':wrappers,
            'gpqa_instruction':PREFIX,'gpqa_fixed_choice_order':CHOICES,
            'otis_question_ids':[r['id'] for r in otis],
            'otis_wrapper_is_transferred_from_later_same_benchmark_log':True,
            'means':{key:{b:statistics.mean(x) for b,x in rows.items()} for key,rows in counts.items()},
            'counts_including_wrapper':counts}

def point_calculations(sources, model_path, inputs):
    models={r['model_id']:r for r in csv.DictReader(Path(model_path).open())}
    rows=list(csv.DictReader((Path(sources)/'scatter_data.csv').open()))
    benchmarks={'gpqa':'GPQA diamond','mathl5':'MATH level 5','otis':'OTIS Mock AIME 2024-2025'}
    selection=[('gemini10pro','gemini-1.0-pro-001','gemma',list(benchmarks)),
               ('qwenmax25','qwen-max-2025-01-25','qwen25',list(benchmarks)),
               ('qwenplus25','qwen-plus-2025-01-25','qwen25',list(benchmarks)),
               ('qwenturbo24','qwen-turbo-2024-11-01','qwen25',list(benchmarks)),
               ('gemini20pro','gemini-2.0-pro-exp-02-05','gemma3',['mathl5'])]
    result={}
    for suffix,identifier,tokenizer,tasks in selection:
        m=models[identifier];coefficient=float(m['flops_per_token'])
        assert coefficient==2*float(m['active_parameters'])
        for benchmark in tasks:
            found=[r for r in rows if r['Identifier']==identifier and r['Benchmark']==benchmarks[benchmark]]
            assert len(found)==1;row=found[0]
            inp=inputs['means'][tokenizer][benchmark];out=float(row['Output tokens per question']);total=inp+out
            result[f'reas-epoch-{benchmark}-{suffix}']={'model_id':identifier,'input':inp,'output':out,'tokens':total,
                'active_parameters':float(m['active_parameters']),'coefficient':coefficient,'compute_flops':total*coefficient,
                'source_row':row}
    assert len(result)==13
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources',type=Path)
    parser.add_argument('--models',type=Path,help='Published model registry or review candidate; enables the thirteen FLOP calculations.')
    parser.add_argument('--output',type=Path,required=True,help='New JSON file outside the retained sources directory; existing files are not overwritten.')
    args=parser.parse_args()
    if args.output.resolve().is_relative_to(args.sources.resolve()):parser.error('Output must be outside retained sources.')
    if args.output.exists():parser.error('Output already exists; choose a new output file.')
    if args.models and args.output.resolve()==args.models.resolve():parser.error('Output cannot replace the model registry.')
    result=compute(args.sources)
    if args.models:
        result['models_sha256']=hashlib.sha256(args.models.read_bytes()).hexdigest()
        result['points']=point_calculations(args.sources,args.models,result)
    with args.output.open('x') as file:file.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['means'],indent=2))
