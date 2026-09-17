"""Latxa v1.1 dominant-operation reconstruction; no model execution.
Requires sentencepiece. Source configurations, not old dataset estimates, supply inputs.
"""
import argparse,collections,hashlib,json,random,re
from pathlib import Path
import sentencepiece
ap=argparse.ArgumentParser();ap.add_argument('--sources',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
src=args.sources.resolve();out=args.output.resolve()
assert not out.exists() and out!=src and src not in out.parents,'Output must be new and outside sources'
def conf(name):
 s=(src/name).read_text();s=re.sub(r'#[^\n]*','',s);s=re.sub(r',\s*([}\]])',r'\1',s);return json.loads(s)
records=[json.loads(l) for l in (src/'atarikoa.jsonl').read_text().splitlines()];assert len(records)==5169
sp=sentencepiece.SentencePieceProcessor(model_file=str(src/'tokenizer.model'))
def prompt(r):return 'Galdera: '+r['question']+'\n'+'\n'.join(f'{c}: {v}' for c,v in zip('ABCD',r['candidates']))+'\nErantzuna:'
# Exact historical five-shot identities are not released. This seeded reconstruction
# samples five distinct donor records excluding the current record; not native token telemetry.
rng=random.Random(1234);lens=[]
for i,r in enumerate(records):
 ids=rng.sample(range(len(records)-1),5);shots=[records[j+(j>=i)] for j in ids]
 context='\n\n'.join(prompt(x)+' '+'ABCD'[x['answer']] for x in shots)+'\n\n'+prompt(r)
 # Each one-token answer likelihood uses the full prompt. Four separate choices
 # are charged centrally; reuse of their shared prefix is a retained alternative.
 lens.append(1+len(sp.encode(context)))
results={}
for size in (13,70):
 hf=conf(f'hf-{size}b-config.json');h=conf(f'configs__hyperparameters__{size}B_v1.1.yml');base=conf('configs__base_config'+('_70B' if size==70 else '')+'.yml');m=conf(f'configs__models__llama-2-{size}b.yml')
 launch=(src/f'train__latxa-{size}b__latxa-{size}b-v1.1.sh').read_text()
 nodes=int(re.search(r'#SBATCH --nodes (\d+)',launch).group(1));gpus=int(re.search(r'#SBATCH --ntasks-per-node=(\d+)',launch).group(1))*nodes
 dp=gpus//(h['model_parallel_size']*max(1,h['pipe_parallel_size']));batch=dp*h['train_micro_batch_size_per_gpu']*h['gradient_accumulation_steps'];steps=h['train_iters'];S=m['seq_length'];positions=batch*steps*S
 assert batch==256 and positions==10485760000 and base['checkpoint_activations']
 d=hf['hidden_size'];f=hf['intermediate_size'];L=hf['num_hidden_layers'];v=hf['vocab_size'];kv=d*hf.get('num_key_value_heads',hf['num_attention_heads'])//hf['num_attention_heads']
 block=L*(2*d*d+2*d*kv+3*d*f);params=2*v*d+block+2*d*L+d
 def body(n,dense=False):return 2*n*block+L*(4*n*n*d if dense else 2*n*(n+1)*d)
 def head(n):return 2*n*v*d
 def forward(n):return body(n)+head(n)
 # Three forward equivalents for forward/backward, plus a full recomputed
 # transformer block (explicit checkpoint_activations). Output head is not checkpointed.
 # FlashAttention backward also rematerializes triangular QK scores once.
 train=batch*steps*(4*body(S)+3*head(S)+L*S*(S+1)*d)
 optimizer=14*params*steps
 eval_batches=steps//base['eval_interval']+2 # periodic, final validation, final test
 validation=eval_batches*batch*forward(S)
 # NeoX save_iters excludes the endpoint; final save occurs once, default linear scale.
 checkpoint_saves=(steps-1)//base['checkpoint_factor']+1
 checkpoint=checkpoint_saves*dp*h['train_micro_batch_size_per_gpu']*forward(S) if base['checkpoint_validation_with_forward_pass'] else 0
 final=4*sum(forward(n) for n in lens)
 total=train+optimizer+validation+checkpoint+final
 native=lambda family:json.loads((src/f'{family}_eus_proficiency_5-shot.json').read_text())['results']['eus_proficiency']['acc,none']
 results[str(size)]={'parameters':params,'gpus':gpus,'data_parallel_replicas':dp,'global_batch_sequences':batch,'training_steps':steps,'training_context':S,'training_positions':positions,'training_flops':train,'optimizer_flops':optimizer,'validation_batches':eval_batches,'validation_flops':validation,'checkpoint_forward_saves':checkpoint_saves if checkpoint else 0,'checkpoint_forward_flops':checkpoint,'target_assessment_flops':final,'compute_flops':total,'initial_accuracy':native(f'Llama-2-{size}b-hf'),'final_accuracy':native(f'latxa-{size}b-v1.1'),'scenarios':{'no_training_validation_or_checkpoint_checks':train+optimizer+final,'shared_choice_prefix':total-final*.75,'dense_final_assessment':total+4*sum(body(n,True)-body(n) for n in lens),'no_activation_recomputation':total-batch*steps*body(S),'dense_attention_in_training':total+batch*steps*4*(body(S,True)-body(S)),'one_extra_restarted_checkpoint_forward':total+dp*h['train_micro_batch_size_per_gpu']*forward(S),'twice_all_validation_and_final_assessment':total+validation+checkpoint+final}}
res={'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(src.iterdir()) if p.is_file()},'assumptions':['Contemporaneous GPT-NeoX commit is an implementation proxy, not a recovered training commit.','Causal FlashAttention QK rematerialization counted; scalar kernels and distributed communication not individually profiled.','Final five-shot prompt identities and prefix reuse are reconstructed, not observed.','Only target EusProficiency assessment is charged; unrelated benchmark evaluations excluded.','Training restarts beyond reconstructed configured work are not observed.'],'benchmark_records':len(records),'guessed_baseline':.25,'final_assessment_prompt_lengths':dict(collections.Counter(lens)),'models':results}
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(results,indent=2))
