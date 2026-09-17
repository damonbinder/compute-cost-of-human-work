"""Replay Sabiá candidate arithmetic; writes JSON only to an explicitly new path."""
import argparse, json
from pathlib import Path
INPUTS=Path(__file__).resolve().parent / "inputs"
def parameters(c):
 h=c['hidden_size'];m=c['intermediate_size'];l=c['num_hidden_layers'];v=c['vocab_size']
 return 2*v*h+l*(4*h*h+3*h*m+2*h)+h
# Paper Table 1: test examples, mean input characters, few-shot examples.
TASKS=[('AGNews',7600,282.34,12),('ASSINRTE',2448,139.99,18),('ASSINSTS',2448,139.99,15),('BLUEX',178,1228.08,1),('BoolQ',3270,562.30,4),('ENEM',916,1286.68,1),('ENEM2022',118,1170.24,1),('FaQuAD',63,1056.47,4),('IMDB',25000,1114.56,2),('MASSIVE',2974,68.35,36),('MKQA',6758,80.32,40),('SST2',872,84.19,34),('TweetSentBR',2010,93.32,30),('WSC',285,102.15,18)]
def compute(config,checkpoint=1,suites=3,chars_per_token=3,output_tokens=16):
 p=parameters(config);l=config['num_hidden_layers'];h=config['hidden_size'];t=10000*512*2048;c=1024.5
 # One training step is three forward equivalents; full rematerialization adds one.
 train_weights=(6+2*checkpoint)*p*t
 train_attention=(12+4*checkpoint)*l*h*c*t
 eval_positions=eval_attention=eval_weights=0
 details=[]
 for name,n,chars,k in TASKS:
  prompt=min(2048-output_tokens,(k+1)*chars/chars_per_token+128)
  positions=prompt+output_tokens;context=(positions+1)/2
  eval_positions+=n*positions*suites
  eval_weights+=2*p*n*positions*suites
  eval_attention+=4*l*h*context*n*positions*suites
  details.append(dict(task=name,test_examples=n,positions_per_example=positions,mean_context=context))
 # Unfactored AdaFactor+momentum, clipping, weight decay; conservative scalar-op allowance.
 optimizer=20*p*10000
 weights=train_weights+eval_weights
 attention=train_attention+eval_attention
 context=(train_weights*c+sum(2*p*d['test_examples']*d['positions_per_example']*suites*d['mean_context'] for d in details))/weights
 return dict(parameters=p,training_tokens=t,training_weight_flops=train_weights,training_attention_flops=train_attention,evaluation_positions=eval_positions,evaluation_weight_flops=eval_weights,evaluation_attention_flops=eval_attention,optimizer_flops=optimizer,total_flops=weights+attention+optimizer,attention_context=context,attention_ratio=attention/weights,eval_tasks=details)
def main():
 result={}
 for label,file,hours in [('7b','original-config.json',200),('65b','llama65-config.json',100)]:
  config=json.loads((INPUTS/file).read_text())
  result[label]=dict(central=compute(config),human_hours=hours,human_seconds=hours*3600,scenarios={
   'no_rematerialization_one_final_suite':compute(config,checkpoint=0,suites=1)['total_flops'],
   'half_forward_rematerialization_three_suites':compute(config,checkpoint=.5,suites=3)['total_flops'],
   'full_rematerialization_eleven_suites':compute(config,checkpoint=1,suites=11)['total_flops'],
   'dense_attention_full_square_three_suites':None})
  # Full-square causal attention implementation would double training attention, not weights.
  r=result[label]['central'];result[label]['scenarios']['dense_attention_full_square_three_suites']=r['total_flops']+r['training_attention_flops']
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args()
 with open(args.output,'x') as f: json.dump(result,f,indent=2);f.write('\n')
if __name__=='__main__': main()
