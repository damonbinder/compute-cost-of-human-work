"""Reconstruct published sentence-by-sentence prompts; no API calls or pickle loading.
Requires nltk==3.8.1 and tiktoken with cl100k_base.
"""
import argparse,json,collections,hashlib
from pathlib import Path
from nltk.tokenize.punkt import PunktParameters,PunktSentenceTokenizer
import tiktoken
p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.exists():p.error('Output must be new')
r=a.sources/'BooookScore-094bf69bc55317b728b4b2bb679c287e0176ae6c';t=a.sources/'punkt-english'
params=PunktParameters()
params.abbrev_types=set((t/'abbrev_types.txt').read_text().splitlines())
params.sent_starters=set((t/'sent_starters.txt').read_text().splitlines())
params.collocations=set(tuple(s.split('\t')) for s in (t/'collocations.tab').read_text().splitlines())
params.ortho_context=collections.defaultdict(int,{k:int(v) for k,v in (s.split('\t') for s in (t/'ortho_context.tab').read_text().splitlines())})
split=PunktSentenceTokenizer(params).tokenize;enc=tiktoken.get_encoding('cl100k_base');count=lambda s:len(enc.encode(s))
template=(r/'prompts/get_annotations.txt').read_text();out={'template_tokens':count(template),'framing_tokens_per_request_assumed':7,'canonical_output_note':'Parsed annotations serialized in requested two-line format; raw responses absent.','collections':{}}
for kind in ['hier','inc']:
 summaries=json.loads((r/f'summaries/gpt4-4096-{kind}-cleaned.json').read_text());annots=json.loads((r/f'annotations/gpt4-4096-{kind}.json').read_text());humans=json.loads((r/f'annotations/human_annotations/summary-gpt4-4096-{kind}.json').read_text())
 items=[];unmatched=[]
 for book,annotations in sorted(annots.items()):
  summary=summaries[book];assert summary==humans[book]['summary'];sentences=split(summary);annotations=annotations or {}
  missing=[s for s in annotations if s not in sentences];unmatched += [(book,s) for s in missing]
  inp=output=0
  for sent in sentences:
   prompt=template.format(summary,sent);inp+=count(prompt)+7
   rec=annotations.get(sent)
   response=('Questions: '+str(rec['questions'])+'\nTypes: '+', '.join(rec['types'])) if rec else 'Questions: no confusion\nTypes: no confusion'
   output+=count(response)
  items.append({'book':book,'summary_words':len(summary.split()),'summary_tokens':count(summary),'sentences':len(sentences),'flagged_sentences':len(annotations),'input_tokens':inp,'canonical_output_tokens':output,'output_100_per_sentence':100*len(sentences)})
 n=len(items);sums={k:sum(x[k] for x in items) for k in ['summary_words','summary_tokens','sentences','flagged_sentences','input_tokens','canonical_output_tokens','output_100_per_sentence']}
 tokens=(sums['input_tokens']+sums['canonical_output_tokens'])/n
 out['collections'][kind]={'books':n,'omitted_books':sorted(set(summaries)-set(annots)),'unmatched_annotation_sentences':unmatched,'sums':sums,'mean_tokens':tokens,'compute_flops':tokens*550_000_000_000,'output_cap_mean_tokens':(sums['input_tokens']+sums['output_100_per_sentence'])/n,'items':items}
validation=json.loads((r/'annotations/human_annotations/annotations-gpt4-4096-inc.json').read_text())
counts=collections.defaultdict(collections.Counter)
for record in validation.values():
 for item in record['annotations']:counts[item['source']][item['agreement']]+=1
out['incremental_validation_counts']={k:dict(v) for k,v in counts.items()}
aligned=collections.defaultdict(collections.Counter)
for book,record in validation.items():
 if book in out['collections']['inc']['omitted_books']:continue
 for item in record['annotations']:aligned[item['source']][item['agreement']]+=1
out['incremental_validation_counts_without_demo_books']={k:dict(v) for k,v in aligned.items()}
with a.output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({k:{f:v[f]for f in ['books','mean_tokens','compute_flops','unmatched_annotation_sentences']} for k,v in out['collections'].items()},indent=2))
