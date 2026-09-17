"""Recount original OTIS inputs. Python dependencies: tokenizers,tiktoken; Node: tiktoken.
Usage: python recompute_otis_inputs.py SOURCE_DIR OUTPUT_DIR
No API calls or production writes.
"""
import argparse,csv,hashlib,importlib.util,json,statistics,subprocess
from pathlib import Path
from tokenizers import Tokenizer
import tiktoken
from tiktoken.load import load_tiktoken_bpe
ap=argparse.ArgumentParser();ap.add_argument('source_dir',type=Path);ap.add_argument('output_dir',type=Path);a=ap.parse_args();S=a.source_dir;D=a.output_dir;D.mkdir(parents=True,exist_ok=True)
questions=json.loads((S/'otis-original-question-text.json').read_text())['questions']
prompts=[r['observed_instruction_before']+r['question']+r['observed_instruction_after'] for r in questions]
assert len(prompts)==45
(D/'prompts.json').write_text(json.dumps(prompts))
keys={'cl100k','o200k','deepseek','hermes70','llama','llama31','mistral3','nemo','phi4','qwen','r1distill','tulu3','three_tokenizer_mean','claude_legacy'}
counts={};hashes={}
def remember(file):hashes[str(file.relative_to(S))]=hashlib.sha256(file.read_bytes()).hexdigest()
f=S/'small-models/openai_public.py';spec=importlib.util.spec_from_file_location('retained_defs',f);defs=importlib.util.module_from_spec(spec);spec.loader.exec_module(defs);remember(f)
defs.load_tiktoken_bpe=lambda url,expected_hash=None:load_tiktoken_bpe(str(S/'small-models'/url.rsplit('/',1)[1]),expected_hash=expected_hash)
for key in sorted(keys|{'cl100k','o200k','mistral3'}):
 if key in ['three_tokenizer_mean','claude_legacy']:continue
 if key in ['cl100k','o200k']:
  f=S/'small-models'/f'{key}_base.tiktoken';tok=tiktoken.Encoding(**getattr(defs,key+'_base')());length=lambda text:len(tok.encode(text,disallowed_special=()))
 else:
  f=S/f'{key}-tokenizer.json';tok=Tokenizer.from_file(str(f));length=lambda text:len(tok.encode(text,add_special_tokens=False).ids)
 remember(f);counts[key]=[length(text)+12 for text in prompts]
counts['three_tokenizer_mean']=[statistics.mean(x) for x in zip(counts['cl100k'],counts['o200k'],counts['mistral3'])]
# Reproduce Anthropic's original legacy tokenizer with its documented NFKC normalization.
node_script="""const fs=require('fs'),{Tiktoken}=require('tiktoken/lite');const c=JSON.parse(fs.readFileSync(process.argv[1])),t=new Tiktoken(c.bpe_ranks,c.special_tokens,c.pat_str),p=JSON.parse(fs.readFileSync(process.argv[2]));console.log(JSON.stringify(p.map(s=>t.encode(s.normalize('NFKC'),'all').length+12)));t.free();"""
r=subprocess.run(['node','-e',node_script,str(S/'anthropic-legacy-claude.json'),str(D/'prompts.json')],check=True,capture_output=True,text=True)
counts['claude_legacy']=json.loads(r.stdout);remember(S/'anthropic-legacy-claude.json')
for f in [S/'otis-original-question-text.json',S/'scatter_data.csv']:remember(f)
means={k:statistics.mean(v) for k,v in counts.items()}
(D/'input-counts.json').write_text(json.dumps({'means':means,'counts':counts,'sha256':hashes,'assumed_chat_positions':12},indent=2));print(json.dumps(means,indent=2))
