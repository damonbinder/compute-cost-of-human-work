"""Read-only Llammas calculation. Requires sentencepiece; no model execution."""
import argparse,csv,json,hashlib,random,statistics
from pathlib import Path
import sentencepiece as spm

def main():
 p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=a.sources.resolve();o=a.output.resolve()
 if o.exists() or o==s or s in o.parents:p.error('new output outside sources required')
 c=json.loads((s/'base-config.json').read_text());d=c['hidden_size'];f=c['intermediate_size'];L=c['num_hidden_layers'];v=c['vocab_size'];seq=1024;steps=19080;batch=256
 matrix=L*(4*d*d+3*d*f);P=matrix+2*v*d+2*L*d+d;tokens=steps*batch*seq
 # Full dense attention; full decoder block recomputed once, head not checkpointed.
 def block(n,tri=False):return 2*n*matrix+4*L*d*(n*(n+1)/2 if tri else n*n)
 def head(n):return 2*n*d*v
 training=steps*batch*(4*block(seq)+3*head(seq))
 optimizer=10*P*steps
 # Validation corpus missing: 1024 packed-length sequences per check, 15 checks.
 validation=15*1024*(block(seq)+head(seq))
 tok=spm.SentencePieceProcessor(model_file=str(s/'base-tokenizer.model'))
 data=list(csv.DictReader(next(s.rglob('belebele-est_Latn-test.csv')).open()))
 evalrows=[]
 for i,r in enumerate(data):
  prompt='Given a passage and a question, select the correct answer from the given choices.\n\nP: '+r['flores_passage']+'\nQ: '+r['question'].strip()+'\nOptions:\n'+'\n'.join(f'{x}. '+r['mc_answer'+str(j)] for j,x in enumerate('ABCD',1))+'\nAnswer:'
  n=len(tok.encode(prompt))+1
  # Four independently scored single-letter alternatives; conservative full-vocab head.
  cost=4*(block(n)+head(n));evalrows.append({'index':i,'prompt_positions':n,'flops':cost})
 evaluation=sum(r['flops'] for r in evalrows)
 total=training+optimizer+validation+evaluation
 inspection=[dict(index=i,**data[i]) for i in random.Random(42).sample(range(len(data)),16)]
 result={'source_sha256':{str(x.relative_to(s)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(s.rglob('*')) if x.is_file()},'parameters':P,'matrix_parameters':matrix,'training_positions':tokens,'training_steps':steps,'batch':batch,'training_flops':training,'optimizer_flops':optimizer,'validation_flops':validation,'endpoint_evaluation_flops':evaluation,'total_flops':total,'validation_assumption':{'checks':15,'sequences_per_check':1024,'positions_per_sequence':1024},'scenarios_flops':{'validation_0':total-validation,'validation_16384':total+15*validation,'no_checkpoint':total-steps*batch*block(seq),'triangular_attention':total-training+steps*batch*(4*block(seq,True)+3*head(seq))},'endpoint':{'questions':len(data),'passages':len({r['flores_passage'] for r in data}),'mean_passage_words':statistics.mean(len(r['flores_passage'].split()) for r in data),'initial_correct':28,'final_correct':48},'evaluation_rows':evalrows,'task_inspection':inspection,'human_assumptions':{'hours':150,'components_hours':{'reading_prerequisites':90,'guided_news_question_practice':60},'scenarios_hours':[50,400],'method':'assumed, not observed or transferred timing'}}
 o.parent.mkdir(parents=True,exist_ok=True);o.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['source_sha256','evaluation_rows','task_inspection']},indent=2))
if __name__=='__main__':main()
