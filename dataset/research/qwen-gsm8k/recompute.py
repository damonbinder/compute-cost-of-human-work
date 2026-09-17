"""Source-only Qwen2.5-Math later-evaluator reconstruction. Requires tokenizers.
No models, torch, benchmark solutions or downloaded code are executed.
"""
import argparse,json,statistics,hashlib,re,random,collections
from pathlib import Path
from tokenizers import Tokenizer
p=argparse.ArgumentParser();p.add_argument('--sources',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();s=a.sources.resolve();o=a.output.resolve()
if o.exists() or o.is_relative_to(s):raise SystemExit('Output must be new and outside sources')
data=[json.loads(l) for l in (s/'gsm8k-original-test.jsonl').read_text().splitlines()];assert len(data)==1319
config=json.loads((s/'model-config.json').read_text());tokenizer=Tokenizer.from_file(str(s/'model-tokenizer.json'));tokenizer.no_padding();tokenizer.no_truncation()
template=json.loads((s/'model-tokenizer-config.json').read_text())['chat_template']
assert "'<|im_start|>system\\n' + messages[0]['content'] + '<|im_end|>\\n'" in template
system='You are a helpful math tutor. Please reason step by step, and put your final answer within \\boxed{}.'
texts=['<|im_start|>system\n'+system+'<|im_end|>\n<|im_start|>user\n'+x['question']+'<|im_end|>\n<|im_start|>assistant\n' for x in data]
lengths=[len(tokenizer.encode(t,add_special_tokens=False).ids) for t in texts]
d=config['hidden_size'];L=config['num_hidden_layers'];f=config['intermediate_size'];V=config['vocab_size'];h=d//config['num_attention_heads'];kv=h*config['num_key_value_heads']
linear_block=2*d*d+2*d*kv+3*d*f
params=L*(linear_block+d+2*kv+2*d)+d+V*d
assert config['tie_word_embeddings']
# Prefill head calculates only last position; 512 emitted positions require511
# subsequent cached forwards. Finished sequences remain in the dense batch.
def estimate(prompt_lengths,batch_size=512,emitted=512,pad=True):
 total=collections.Counter();batches=[]
 for start in range(0,len(prompt_lengths),batch_size):
  ls=prompt_lengths[start:start+batch_size];mx=max(ls);batches.append({'start':start,'n':len(ls),'padded_input':mx})
  for raw in ls:
   S=mx if pad else raw;D=emitted-1
   total['decoder_positions']+=S+D
   total['transformer_linear']+=2*L*linear_block*(S+D)
   total['vocabulary_head']+=2*d*V*emitted
   total['prefill_attention_dense']+=4*L*d*S*S
   total['prefill_attention_triangular']+=4*L*d*S*(S+1)/2
   total['decode_attention']+=4*L*d*(D*S+D*(D+1)/2)
 mean={k:v/len(prompt_lengths) for k,v in total.items()}
 mean['flops']=sum(mean[k] for k in ['transformer_linear','vocabulary_head','prefill_attention_dense','decode_attention'])
 mean['causal_prefill_scenario_flops']=mean['flops']-mean['prefill_attention_dense']+mean['prefill_attention_triangular']
 return {'means':mean,'batches':batches}
main=estimate(lengths);rng=random.Random(42);shuffles=[]
for i in range(20):shuffled=list(lengths);rng.shuffle(shuffled);shuffles.append(estimate(shuffled)['means']['flops'])
sample=random.Random(20260913).sample(range(len(data)),12)
result={'model_parameters_from_config':params,'transformer_matrix_parameters':L*linear_block,'input_length_mean':statistics.mean(lengths),'input_length_max':max(lengths),'main':main,'batch32':estimate(lengths,32),'batch1':estimate(lengths,1),'unpadded512':estimate(lengths,pad=False),'readme301_processing_counterfactual':estimate(lengths,emitted=301),'emitted511point5_sensitivity':estimate(lengths,emitted=511.5),'shuffle20_flops_minmax':[min(shuffles),max(shuffles)],'human':{'source_median_batch_seconds':300,'source_questions_per_batch':5,'estimated_per_question_seconds':60,'human_original_accuracy_percent':84,'timing_donor_attempts':None},'sampled_input_inspection':[{'index':i,'question':data[i]['question'],'input_tokens':lengths[i]} for i in sample],'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(s.iterdir()) if p.is_file()}}
o.write_text(json.dumps(result,indent=2)+'\n')
