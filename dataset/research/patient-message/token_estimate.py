#!/usr/bin/env python3
"""Retokenize published examples to estimate the reported mean word workload.
Requires pypdf, pdfplumber and tiktoken. No network/model calls.
"""
import argparse,io,json,re,hashlib
from pathlib import Path
from pypdf import PdfReader,PdfWriter
import pdfplumber,tiktoken
from tiktoken.load import load_tiktoken_bpe
p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();src=a.sources.resolve();out=a.output.resolve()
if out.exists() or out==src or src in out.parents:raise SystemExit('Output must be new and outside sources')
reader=PdfReader(src/'paper.pdf');writer=PdfWriter()
for i in (3,4):writer.add_page(reader.pages[i].rotate(90))
buf=io.BytesIO();writer.write(buf);buf.seek(0)
rows=[]
with pdfplumber.open(buf) as doc:
 for i,page in enumerate(doc.pages):
  tops=[w['top'] for w in page.extract_words(x_tolerance=1) if w['x0']<100 and w['text']=='Question']
  assert len(tops)==3
  bottoms=tops[1:]+[511]
  for j,(top,bottom) in enumerate(zip(tops,bottoms)):
   answer=' '.join(page.crop((276,top-.5,610,bottom-2)).extract_text(x_tolerance=1).split())
   question=' '.join(page.crop((69,top-.5,144,bottom-2)).extract_text(x_tolerance=1).split())
   rows.append(dict(page=i+4,example=i*3+j+1,answer=answer,question_summary=question))
assert all('October 2022' not in r['answer'] for r in rows)
# Use official tiktoken family definitions, loading retained ranks offline.
import tiktoken_ext.openai_public as definitions
def local_ranks(url,expected_hash=None):
 return load_tiktoken_bpe(str(src/Path(url).name),expected_hash=expected_hash)
definitions.load_tiktoken_bpe=local_ranks
results={}
for name in ('cl100k_base','p50k_base'):
 enc=tiktoken.Encoding(**getattr(definitions,name)())
 counts=[]
 for r in rows:
  counts.append(dict(example=r['example'],answer_words=len(r['answer'].split()),answer_tokens=len(enc.encode(r['answer'])),question_words=len(r['question_summary'].split()),question_tokens=len(enc.encode(r['question_summary']))))
 out_ratio=sum(r['answer_tokens'] for r in counts)/sum(r['answer_words'] for r in counts)
 in_ratio=sum(r['question_tokens'] for r in counts)/sum(r['question_words'] for r in counts)
 inp=180*in_ratio;ot=211*out_ratio;wrapper=50
 results[name]=dict(examples=counts,input_tokens_estimate=inp,output_tokens_estimate=ot,system_wrapper_allowance=wrapper,tokens=inp+ot+wrapper,answer_token_word_ratio=out_ratio,question_token_word_ratio=in_ratio,flops_at_175B=(inp+ot+wrapper)*350000000000)
result=dict(source_pdf_sha256=hashlib.sha256((src/'paper.pdf').read_bytes()).hexdigest(),estimates=results,notes='Six published examples are selected; questions are edited summaries. Ratios transfer to reported full-195 mean lengths, not native token counters. Unknown early ChatGPT tokenizer and system prompt: cl100k central, p50k sensitivity, 50 system/wrapper positions assumed.')
primary=results['cl100k_base']['tokens']
helper=results['p50k_base']['input_tokens_estimate']+results['p50k_base']['output_tokens_estimate']+4
result['compute']={
 'primary_tokens':primary,'primary_parameters':175e9,
 'moderation_tokens':helper,'moderation_parameters':1.3e9,
 'tokens':primary+helper,
 'primary_flops':primary*350e9,'moderation_flops':helper*2.6e9,
 'compute_flops':primary*350e9+helper*2.6e9,
 'moderation_assumption':'One scan of the question and one scan of the answer, four total special positions; 1.3B lightweight GPT proxy, not disclosed deployment size.',
 'primary_size_scenarios':{str(n):primary*2*n+helper*2.6e9 for n in (7e9,44e9,175e9,350e9)},
 'moderation_size_scenarios':{str(n):primary*350e9+helper*2*n for n in (0.1e9,1.3e9,6.7e9,175e9)},
 'moderation_scan_scenarios':{str(n):primary*350e9+helper*2.6e9*n for n in (1,5,20)},
 'wrapper_scenarios':{str(n):(primary-50+n)*350e9+helper*2.6e9 for n in (0,50,200)},
 'p50k_primary_sensitivity':results['p50k_base']['tokens']*350e9+helper*2.6e9
}
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['compute'],indent=2))
