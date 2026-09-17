"""Replay retained public evaluation logs. Requires tokenizers==0.21.4. SOURCE_DIR OUTPUT_JSON."""
import argparse,json,re,statistics,hashlib
from pathlib import Path
from tokenizers import Tokenizer

def parse(path):
 text=path.read_text()
 # stderr progress displays interrupt stdout between field markers.
 clean=re.sub(r'(?:\r|\n)\s*\d+%\|[^\r\n]*?\]','\n',text)
 records=[]
 for block in clean.split('Input: ')[1:]:
  inp,tail=block.split('Target: ',1);target,pred=tail.split('Predicted: ',1)
  records.append(dict(input=inp.strip('\n'),target=target.strip('\n'),prediction=pred.split('\n\n')[0].strip('\n')))
 def answer(t):return t.split('####',1)[-1].strip().replace(',','')
 correct=sum(answer(r['target'])==answer(r['prediction']) for r in records)
 reported=float(re.search(r'Test Accuracy: ([0-9]+\.[0-9]+)',text)[1])
 assert abs(correct/len(records)-reported)<1e-12
 return records,correct

def calculate(s):
 tok=Tokenizer.from_file(str(s/'gpt2-tokenizer.json'));results={}
 for path in sorted(s.glob('logs*')):
  if 'phi3' in path.name or 'mistral' in path.name:continue
  medium='gpt2-medium' in path.name
  cfg=json.loads((s/('gpt2-medium-config.json' if medium else 'gpt2-config.json')).read_text())
  d,L,V,S=cfg['n_embd'],cfg['n_layer'],cfg['vocab_size'],cfg['n_positions']
  params=L*(12*d*d+13*d)+V*d+S*d+2*d
  rows,correct=parse(path)
  partial_cot='11_by_11' in path.name
  hidden_specials=2 if partial_cot else 3
  for r in rows:
   r['input_tokens']=len(tok.encode(r['input'],add_special_tokens=False).ids)+1
   r['visible_output_tokens']=len(tok.encode(r['prediction'],add_special_tokens=False).ids)
   # May2024 training retains the separator after the removed CoT. Fully
   # internalized outputs therefore begin with EOS. Stopping initializes AFTER
   # the first generated token; the logits processor initializes BEFORE it.
   # This requires a third EOS when the first token was EOS. Partial11 starts
   # with arithmetic text and needs only two EOS. Actual token IDs are absent.
   r['output_tokens']=r['visible_output_tokens']+hidden_specials
   r['tokens']=r['input_tokens']+r['output_tokens']
   r['compute_flops']=2*params*r['tokens']
  if 'mult' in path.name:
   n=int(path.name.split('__')[1].split('_')[0]);key=f'mult{n}';assert len(rows)==1000
  else:key='gsm8k-medium' if medium else 'gsm8k-small';assert len(rows)==1319
  results[key]=dict(log=path.name,parameters=params,n=len(rows),correct=correct,accuracy=correct/len(rows),
   input_tokens=statistics.mean(r['input_tokens']for r in rows),output_tokens=statistics.mean(r['output_tokens']for r in rows),
   tokens=statistics.mean(r['tokens']for r in rows),compute_flops=statistics.mean(r['compute_flops']for r in rows),
   hidden_output_special_tokens_assumed=hidden_specials,one_more_special_flops=2*params,
   two_eos_tokens=statistics.mean(r['input_tokens']+r['visible_output_tokens']+2 for r in rows),
   two_eos_flops=statistics.mean(2*params*(r['input_tokens']+r['visible_output_tokens']+2) for r in rows),
   rows=rows)
  if key.startswith('mult'):
   rounded={4:70,5:110,7:200,9:330,11:500}[n]
   results[key]['human_time']=dict(seconds=rounded,component_scale_seconds=4*n*n+n,
       written_2digit_mean_seconds=18.12,written_2digit_accuracy=.62,
       cohort_size=25,problems_per_participant=20,
       calibrated_unrounded_seconds=(4*n*n+n)*(18.12/18),
       sensitivity_seconds=[rounded/2,rounded*2])
 return dict(source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in s.iterdir() if p.is_file() and p.name not in ['calculations.json','manifest.json']},points=results)

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('source_dir',type=Path);p.add_argument('output_json',type=Path);a=p.parse_args()
 if a.output_json.resolve().is_relative_to(a.source_dir.resolve()):p.error('Write output outside retained sources.')
 with a.output_json.open('x') as f:json.dump(calculate(a.source_dir),f,indent=2)
