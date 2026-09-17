"""Read-only AceGPT source reconstruction. Requires sentencepiece, no model calls."""
import argparse,json,csv,math,statistics,hashlib,random
from pathlib import Path
import sentencepiece as spm

def aggregate(x):return statistics.mean(statistics.mean(v['average']['Accuracy'] for v in domain.values()) for domain in x.values())
def main():
 p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=a.sources.resolve();o=a.output.resolve()
 if o.exists() or o==s or s in o.parents:p.error('new output outside evidence required')
 scores={str(i):aggregate(json.loads((s/f'metrics-{i}.json').read_text())) for i in range(4)}
 c=json.loads((s/'AceGPT-7B-config.json').read_text());L=c['num_hidden_layers'];d=c['hidden_size'];f=c['intermediate_size'];v=c['vocab_size'];M=L*(4*d*d+3*d*f);P=M+2*d*v+2*L*d+d;N=30_000_000_000;S=2048
 def block(n,tri=False):return 2*n*M+4*L*d*(n*(n+1)/2 if tri else n*n)
 def head(n):return 2*n*d*v
 train=N/S*3*(block(S)+head(S));steps=math.ceil(N/(3072*S));opt=10*P*steps
 # No source monitoring size: assume a check every100 updates,1024 full-length sequences each.
 checks=steps//100+1;validation=checks*1024*(block(S)+head(S))
 tok=spm.SentencePieceProcessor(model_file=str(s/'tokenizer.model'));root=s/'repo/eval_results/Arabic MMLU';changes=[];evaluation=[];transitions={}
 for file in sorted((root/'AceGPT_7B_base/few_shot').glob('*.jsonl')):
  new=[json.loads(z) for z in file.read_text().splitlines()];old=[json.loads(z) for z in (root/'llama-2-7b-hf/few_shot'/file.name).read_text().splitlines()];up=down=0
  assert len(new)==len(old), 'paired source response lists must have identical lengths'
  for x,y in zip(new,old):
   assert x['query']==y['query'] and x['answer']==y['answer']
   n=len(tok.encode(x['prompted_query']))+1;t=len(tok.encode(x['response']))
   cost=block(n)+head(n)+sum(2*M+4*L*d*(n+k)+2*d*v for k in range(1,t))
   evaluation.append({'subject':file.stem,'query_id':x['query_id'],'input_positions':n,'visible_output_positions':t,'flops':cost})
   yes=x['response_answer']==x['answer'];before=y['response_answer']==y['answer'];up+=yes and not before;down+=before and not yes
   if yes!=before:changes.append({'subject':file.stem,'query_id':x['query_id'],'improved':yes,'query':x['query'],'answer':x['answer'],'before':y['response_answer'],'after':x['response_answer']})
  transitions[file.stem]={'n':len(new),'gained':up,'lost':down}
 totalquestions=sum(sum(1 for _ in csv.reader(p.open())) for p in (s/'repo/eval/benchmark_eval/benchmarks/MMLUArabic/test').glob('*.csv'))
 evalf=statistics.mean(x['flops'] for x in evaluation)*totalquestions;total=train+opt+validation+evalf
 r={'source_sha256':{str(p.relative_to(s)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(s.rglob('*')) if p.is_file()},'reported_nested_scores':scores,'parameters':P,'training_tokens':N,'training_sequence_length':S,'approximate_optimizer_steps':steps,'training_flops':train,'optimizer_flops':opt,'monitoring_assumption':{'checks':checks,'sequences_per_check':1024},'monitoring_flops':validation,'evaluation_proxy_subjects':len(transitions),'evaluation_proxy_questions':len(evaluation),'all_questions':totalquestions,'endpoint_evaluation_flops':evalf,'total_flops':total,'scenarios_flops':{'full_layer_checkpoint':total+N/S*block(S),'triangular_attention':total-train+N/S*3*(block(S,True)+head(S)),'no_monitoring':total-validation,'tenfold_monitoring':total+9*validation},'transitions':transitions,'changed_examples':random.Random(13).sample(changes,24),'evaluation_rows':evaluation,'human':{'hours':60,'scenarios_hours':[15,200],'components_hours':{'vocabulary_and_sentence_interpretation':24,'guided_academic_reading':24,'mixed_unseen_question_practice':12},'evidence':'assumed'}}
 o.parent.mkdir(parents=True,exist_ok=True);o.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['source_sha256','changed_examples','evaluation_rows']},indent=2))
if __name__=='__main__':main()
