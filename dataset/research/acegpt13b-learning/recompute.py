"""Read-only AceGPT13B reconstruction; sentencepiece required. No model calls."""
import argparse,json,math,hashlib,statistics,random
from pathlib import Path
import sentencepiece as spm

def main():
 p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=a.sources.resolve();o=a.output.resolve()
 if o.exists() or o==s or s in o.parents:p.error('new output outside sources required')
 c=json.loads((s/'causal-config.json').read_text());L=c['num_hidden_layers'];d=c['hidden_size'];f=c['intermediate_size'];v=c['vocab_size'];M=L*(4*d*d+3*d*f);P=M+2*d*v+2*L*d+d;N=10_000_000_000;S=2048
 assert P*4==json.loads((s/'causal-index.json').read_text())['metadata']['total_size']
 def block(n,tri=False):return 2*n*M+4*L*d*(n*(n+1)/2 if tri else n*n)
 def head(n):return 2*n*d*v
 train=N/S*3*(block(S)+head(S));steps=math.ceil(N/(3072*S));optimizer=10*P*steps;checks=steps//100+1;monitoring=checks*1024*(block(S)+head(S))
 m=json.loads((s/'metrics-0.json').read_text());domains={k:statistics.mean(z['average']['Accuracy'] for z in y.values()) for k,y in m.items()};score=statistics.mean(domains.values())
 tok=spm.SentencePieceProcessor(model_file=str(s/'tokenizer.model'));rows=[];examples=[]
 for file in sorted((s/'repo/eval_results/Arabic MMLU/AceGPT_13B_base/few_shot').glob('*.jsonl')):
  data=[json.loads(z) for z in file.read_text().splitlines()]
  for x in data:
   n=len(tok.encode(x['prompted_query']))+1;t=len(tok.encode(x['response']));cost=block(n)+head(n)+sum(2*M+4*L*d*(n+k)+2*d*v for k in range(1,t));rows.append({'subject':file.stem,'id':x['query_id'],'input_positions':n,'output_positions':t,'flops':cost});examples.append({'subject':file.stem,'query':x['query'],'answer':x['answer'],'response_answer':x['response_answer']})
 evaluation=statistics.mean(x['flops'] for x in rows)*14042;total=train+optimizer+monitoring+evaluation
 r={'source_sha256':{str(x.relative_to(s)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(s.rglob('*')) if x.is_file()},'parameters':P,'training_positions':N,'training_flops':train,'optimizer_steps_estimated':steps,'optimizer_flops':optimizer,'monitoring_assumption':{'checks':checks,'sequences_per_check':1024,'positions':2048},'monitoring_flops':monitoring,'evaluation_proxy_questions':len(rows),'evaluation_flops':evaluation,'total_flops':total,'domain_accuracies':domains,'final_source_score':score,'baseline_reported':0.3376,'baseline_domain_mean_alternative':statistics.mean([.3294,.3230,.3342,.3727]),'scenarios_flops':{'full_layer_checkpoint':total+N/S*block(S),'triangular_attention':total-train+N/S*3*(block(S,True)+head(S)),'no_monitoring':total-monitoring,'tenfold_monitoring':total+9*monitoring},'human':{'hours':100,'components':{'academic_vocabulary_and_relations':30,'guided_varied_subject_reading':40,'unseen_practice_and_review':30},'scenarios_hours':[30,300],'evidence':'assumed'},'evaluation_rows':rows,'inspected_examples':random.Random(130).sample(examples,24)}
 o.parent.mkdir(parents=True,exist_ok=True);o.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['source_sha256','evaluation_rows','inspected_examples']},indent=2))
if __name__=='__main__':main()
