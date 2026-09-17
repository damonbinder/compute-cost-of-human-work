"""Read-only BLiMP learning reconstruction. Needs tokenizers and sentencepiece."""
from pathlib import Path
import argparse,json,zipfile,hashlib,statistics,collections,random
import tokenizers,sentencepiece
ap=argparse.ArgumentParser();ap.add_argument('--sources',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();src=args.sources.resolve();out=args.output.resolve()
if out.exists() or out==src or src in out.parents:raise ValueError('Output must be new and outside source evidence')
archive=zipfile.ZipFile(src/'filter_data.zip');groups={}
for n in archive.namelist():
 if '/blimp_filtered/' in n and n.endswith('.json'):groups[Path(n).stem]=[json.loads(l) for l in archive.read(n).decode().splitlines()]
assert len(groups)==12 and sum(map(len,groups.values()))==57812
rows=[r for a in groups.values() for r in a];uids=sorted(set(r['UID'] for r in rows));assert len(uids)==62
vocab=sorted(set(w.lower().strip('.,?!') for r in rows for key in ['sentence_good','sentence_bad'] for w in r[key].split()))
z=zipfile.ZipFile(src/'dynabench_results.zip');native=[r for n in z.namelist() for r in json.loads(z.read(n))]
scores={}
for mid in [1583,1623]:
 a=[r for r in native if r['model_id']==mid and 'blimp-' in r['dataset_name']];assert len(a)==12
 vals={json.loads(r['metadata_json'])['sub_task']:json.loads(r['metadata_json'])['perf'] for r in a};assert len(vals)==12
 scores[str(mid)]={'model_name':a[0]['model_name'],'category_scores':vals,'category_macro':statistics.mean(vals.values())}
rt=tokenizers.Tokenizer.from_file(str(src/'roberta-tokenizer.json'));rt.no_truncation();rt.no_padding();sp=sentencepiece.SentencePieceProcessor(model_file=str(src/'llama2-tokenizer.model'))
texts=[r[key] for r in rows for key in ['sentence_good','sentence_bad']]
rl=[len(e.ids) for e in rt.encode_batch(texts)];ll=[len(sp.encode(t)) for t in texts]
# Fairseq has no trainable token-type embedding; converted HF model adds 768 zero parameters.
d=768;f=3072;L=12;V=50265
rp=V*d+514*d+2*d+L*(4*d*d+2*d*f+9*d+f)+d*d+d+2*d+V

def rf(n,head_fraction=1):return L*(8*n*d*d+4*n*d*f+4*n*n*d)+head_fraction*(2*n*d*d+2*n*d*V)
steps=500000;batch=8192;S=512;rpositions=steps*batch*S
rtrain=3*steps*batch*rf(S,.15);ropt=14*rp*steps
# Final HF PLL masks every non-special token and returns full-sequence logits.
reval=sum((n-2)*rf(n) for n in rl)
# Explicit small accounting allowance: 500 checks each consuming 2M token positions.
monitor_positions=500*2000000;rmonitor=monitor_positions/S*rf(S,.15)
rmain=rtrain+ropt+reval+rmonitor
D=8192;F=28672;NL=80;KV=1024;NV=32000
lp=2*NV*D+NL*(2*D*D+2*D*KV+3*D*F+2*D)+D

def lf(n,triangular=False):
 att=(2*n*(n+1)*D if triangular else 4*n*n*D)
 return NL*(4*n*D*D+4*n*D*KV+6*n*D*F+att)+2*n*D*NV
lpositions=2000000000000;LS=4096;lsteps=lpositions/4194304
# Llama1 causal/FlashAttention implementation transferred to Llama2 pretraining.
# One triangular QK matrix recomputation in attention backward, no repeated linears.
lqk_recompute=lpositions/LS*NL*LS*(LS+1)*D
ltrain=3*lpositions/LS*lf(LS,True)+lqk_recompute
lopt=14*lp*lsteps;leval=sum(lf(n) for n in ll)
lmonitor=monitor_positions/LS*lf(LS,True);lmain=ltrain+lopt+leval+lmonitor
rng=random.Random(381);examples={k:rng.sample(a,min(3,len(a))) for k,a in sorted(groups.items())}
res={'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(src.iterdir()) if p.is_file()},'filtered_pairs':len(rows),'surviving_paradigms':uids,'category_pair_counts':{k:len(v) for k,v in groups.items()},'surface_forms':len(vocab),'surface_vocabulary':vocab,'examples':examples,'native_endpoints':scores,'gpt2_corrected_macro':statistics.mean(json.loads(l)['gpt2'] for l in (src/'blimp-model-summary.jsonl').read_text().splitlines() if json.loads(l)['UID']!='overall'),'roberta':{'training_parameters':rp,'hf_model_parameters':rp+768,'training_steps':steps,'batch_assumed_binary_8K':batch,'training_context':S,'training_positions':rpositions,'training_flops':rtrain,'optimizer_flops':ropt,'monitoring_assumed_positions':monitor_positions,'monitoring_flops':rmonitor,'final_blimp_flops':reval,'compute_flops':rmain,'score':scores['1583']['category_macro'],'eval_token_lengths':dict(collections.Counter(rl)),'scenarios':{'literal_8000_batch_total':rtrain*8000/8192+ropt+rmonitor+reval,'training_full_MLM_head_total':3*steps*batch*rf(S,1)+ropt+rmonitor+reval,'full_forward_recomputation_total':rmain+rtrain/3,'no_periodic_monitoring_total':rmain-rmonitor,'100x_monitoring_total':rmain+99*rmonitor}},'llama2':{'parameters':lp,'attention_backward_QK_recomputation_flops':lqk_recompute,'training_positions':lpositions,'training_context':LS,'assumed_optimizer_steps':lsteps,'training_flops':ltrain,'optimizer_flops':lopt,'monitoring_assumed_positions':monitor_positions,'monitoring_flops':lmonitor,'final_blimp_flops':leval,'compute_flops':lmain,'score':scores['1623']['category_macro'],'eval_token_lengths':dict(collections.Counter(ll)),'scenarios':{'dense_attention_training_total':3*lpositions/LS*lf(LS)+lqk_recompute+lopt+monitor_positions/LS*lf(LS)+leval,'full_forward_recomputation_total':lmain+lpositions/LS*lf(LS,True),'no_periodic_monitoring_total':lmain-lmonitor,'100x_monitoring_total':lmain+99*lmonitor}},'human_duration':{'central_hours':150,'low_scenario_hours':50,'high_scenario_hours':400,'mini_french_training_seconds_approx':3600,'word_pair_full_ST_learning_seconds':40*4*(5+8),'word_pair_ST_with_unrelated_distractors_seconds':40*4*(5+8)+4*30,'word_pair_items':40,'note':'150 h is a judgment-based targeted-learning estimate, not an observed BLiMP learning curve or linear lexical scaling.'}}
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(res,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:{q:v for q,v in res[k].items() if q in ['compute_flops','training_flops','monitoring_flops','final_blimp_flops','score','training_positions','parameters','hf_model_parameters']} for k in ['roberta','llama2']},indent=2))
