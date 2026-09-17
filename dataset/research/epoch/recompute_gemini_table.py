"""Recompute task input lengths from retained original text and Google tokenizers.

Usage: python -B recompute_gemini_table.py /path/to/epoch/sources --output counts.json
Requires sentencepiece and pyarrow. No API calls or production writes.
"""
import argparse,csv,hashlib,json,statistics
from pathlib import Path
import sentencepiece as spm
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
    for f in [s/'gpqa_diamond.csv',s/'gpqa-gist.json',s/'otis-original-question-text.json',s/'scatter_data.csv',*math_paths]:
        hashes[str(f.relative_to(s))]=hashlib.sha256(f.read_bytes()).hexdigest()
    return {'sentencepiece_version':spm.__version__,'sha256':hashes,'assumed_wrapper_positions':wrappers,
            'gpqa_instruction':PREFIX,'gpqa_fixed_choice_order':CHOICES,
            'otis_question_ids':[r['id'] for r in otis],
            'otis_wrapper_is_transferred_from_later_same_benchmark_log':True,
            'means':{key:{b:statistics.mean(x) for b,x in rows.items()} for key,rows in counts.items()},
            'counts_including_wrapper':counts}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=compute(args.sources)
    if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['means'],indent=2))
