#!/usr/bin/env python3
"""Original corpus/benchmark workload reconstruction. Requires tokenizers; no model execution."""
import argparse,pathlib,json,collections,math,hashlib,statistics
from tokenizers import Tokenizer
p=argparse.ArgumentParser();p.add_argument('--sources',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();s=a.sources.resolve();out=a.output.resolve();assert not out.exists() and s not in out.parents
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
tok=Tokenizer.from_file(str(s/'data__tokenizers__babyberta.json'));tok.no_truncation();tok.no_padding()
raw=(s/'data__corpora__aochildes.txt').read_text().splitlines();eligible=[x for x in raw if x.count(' ')>=2];hist=collections.Counter();unweighted=collections.Counter();filtered=0
for start in range(0,len(eligible),4096):
 for e in tok.encode_batch(eligible[start:start+4096],add_special_tokens=False):
  n=len(e.ids)
  if n>126:filtered+=1;continue
  copies=min(math.comb(n,2),10);hist[n+2]+=copies;unweighted[n+2]+=1
N=sum(hist.values());cum=0;previous=0.;pmf={}
for length,count in sorted(hist.items()):
 cum+=count;cdf=math.prod((cum-i)/(N-i) for i in range(16)) if cum>=16 else 0.;pmf[length]=cdf-previous;previous=cdf
EM=sum(k*v for k,v in pmf.items());EM2=sum(k*k*v for k,v in pmf.items());steps=260000;batch=16;d=256;f=1024;L=8;V=8192
# RoBERTa full-vocab masked-LM head is evaluated at ALL padded positions before selecting loss positions.
def F(S,S2=None):
 S2=S*S if S2 is None else S2
 return L*(8*S*d*d+4*S*d*f+4*S2*d)+2*S*d*d+2*S*d*V
params=V*d+130*d+2*d+2*d+L*(4*d*d+2*d*f+9*d+f)+d*d+d+2*d+V
forward=steps*batch*F(EM,EM2);training=3*forward;optimizer=steps*params*14
monitor=[];one=0;monitor_tokens=0
for file in sorted((s/'zorro').glob('*.txt')):
 texts=file.read_text().splitlines();enc=tok.encode_batch(texts,add_special_tokens=True);lens=[len(x.ids) for x in enc];assert len(lens)==4000 and max(lens)<=256
 work=0;positions=0
 for i in range(0,len(lens),32):
  group=lens[i:i+32];m=max(group);work+=len(group)*F(m);positions+=len(group)*m
 monitor.append({'file':file.name,'sentences':len(texts),'length_mean':statistics.mean(lens),'length_max':max(lens),'forward_flops':work,'padded_positions':positions,'first_pair':texts[:2]});one+=work;monitor_tokens+=positions
assert len(monitor)==23
endpoint={}
for run in sorted((s/'endpoint-results').iterdir()):
 good=n=0;paradigms={}
 for file in sorted(run.glob('*.txt')):
  lines=file.read_text().splitlines();name=file.name.removeprefix('probing_').removesuffix('_results_260000.txt');original=(s/'zorro'/(name+'.txt')).read_text().splitlines();assert len(lines)==len(original)==4000
  assert all(line.rsplit(' ',1)[0]==sentence for line,sentence in zip(lines,original))
  count=sum(float(lines[i+1].rsplit(' ',1)[1])<float(lines[i].rsplit(' ',1)[1]) for i in range(0,len(lines),2));good+=count;n+=len(lines)//2;paradigms[name]=count/(len(lines)//2)
 endpoint[run.name]={'correct':good,'pairs':n,'accuracy':good/n,'paradigms':paradigms}
result={'endpoint_results':endpoint,'raw_sentences':len(raw),'after_space_filter':len(eligible),'over126_tokens_excluded':filtered,'eligible_sentences':sum(unweighted.values()),'mask_pattern_examples':N,'sentence_lengths':dict(sorted(unweighted.items())),'weighted_lengths':dict(sorted(hist.items())),'expected_batch_max':EM,'expected_batch_max_squared':EM2,'unpadding_length_mean':sum(k*v for k,v in hist.items())/N,'steps':steps,'training_positions':steps*batch*EM,'train_forward_flops':forward,'training_forward_backward_flops':training,'parameters':params,'optimizer_flops_assumed':optimizer,'monitoring_checks':14,'monitoring_one_check_flops':one,'monitoring_flops':14*one,'monitoring_positions':14*monitor_tokens,'compute_flops':training+optimizer+14*one,'monitoring':monitor,'scenarios':{'unpadding_training_flops':3*steps*batch*sum(F(k)*v for k,v in hist.items())/N,'all128_training_flops':3*steps*batch*F(128)},'source_hashes':{str(f.relative_to(s)):sha(f) for f in sorted(s.rglob('*')) if f.is_file()}}
result['single_trajectory_compute_flops']=result['compute_flops'];result['single_trajectory_training_positions']=result['training_positions'];result['selection_training_runs']=3;result['compute_flops']*=3;result['training_positions']*=3
# Other operation components remain explicitly per trajectory; totals above include best-of-three selection.
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['sentence_lengths','weighted_lengths','source_hashes','monitoring']},indent=2))
