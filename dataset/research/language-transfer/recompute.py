#!/usr/bin/env python3
"""Source architecture/workload reconstruction; no training or benchmark execution.
Requires sentencepiece only for the optional retained AceGPT evaluation audit.
Usage: python recompute.py --source-dir SOURCES [--output NEW.json]
"""
import argparse, hashlib, json, pathlib

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=pathlib.Path,required=True);ap.add_argument('--output',type=pathlib.Path);a=ap.parse_args();p=a.source_dir
    cfg=json.loads((p/'swallow7-config.json').read_text());h=cfg['hidden_size'];i=cfg['intermediate_size'];L=cfg['num_hidden_layers'];V=cfg['vocab_size'];S=4096;T=100_000_000_000
    projections=L*(4*h*h+3*h*i)+V*h
    params=projections+V*h+(2*L+1)*h
    # Six operations per learned linear weight/token (forward plus two gradients).
    linear_train=6*projections*T
    # Causal QK/AV forward/backward plus FlashAttention score recomputation.
    # Approximate triangular term; elementwise softmax/norm/optimizer omitted.
    attention_train=7*L*(S+1)*h*T
    jp_instances=sum([1119,120,198,4442,766,250,1000,993])
    # English multiple-choice candidate scoring is counted separately.
    en_sequences=500*4+17944+11873+10042*4+2325*2+1319
    # Six Japanese checkpoints including diagnostic starting model, and two English.
    benchmark_tokens=(6*jp_instances+2*en_sequences)*4096
    # Explicit unreported monitoring scenario: 1% of training tokens evaluated without updates.
    monitoring_tokens=.01*T
    eval_per_token=2*projections+2*L*(S+1)*h
    benchmark_flops=benchmark_tokens*eval_per_token
    monitoring_flops=monitoring_tokens*eval_per_token
    result={'swallow7':{'parameters':params,'linear_projection_parameters':projections,'training_tokens':T,'linear_training_flops':linear_train,'causal_attention_training_flops':attention_train,'japanese_instances':jp_instances,'english_scored_sequences':en_sequences,'assumed_benchmark_eval_tokens':benchmark_tokens,'assumed_monitoring_tokens':monitoring_tokens,'benchmark_flops':benchmark_flops,'monitoring_flops':monitoring_flops,'compute_flops':linear_train+attention_train+benchmark_flops+monitoring_flops,'human_seconds':360000,'human_scenario_hours':[30,100,300],'additional_full_linear_forward_recomputation_flops':2*projections*T,'monitoring_0_to_5pct_flops':[0,.05*T*eval_per_token]}}
    if (p/'ace-mmlu13b').exists():
        import sentencepiece as spm
        tok=spm.SentencePieceProcessor(model_file=str(p/'ace-tokenizer.model'));n=correct=nt=0;sub=[]
        for f in sorted((p/'ace-mmlu13b').glob('*.jsonl')):
            r=[json.loads(s) for s in f.read_text().splitlines()];k=sum(x['response_answer']==x['answer'] for x in r);tokens=sum(len(tok.encode(x['prompted_query']))+len(tok.encode(x['response']))+1 for x in r);n+=len(r);correct+=k;nt+=tokens;sub.append({'subject':f.stem,'n':len(r),'correct':k,'tokens_unpadded_plus_one':tokens})
        result['ace13_source_audit']={'n':n,'correct':correct,'micro_accuracy':correct/n,'macro_subject_accuracy':sum(x['correct']/x['n'] for x in sub)/len(sub),'unpadded_tokens_plus_one_per_item':nt,'subjects':sub,'warning':'Retained outputs do not reproduce paper Table 8 40.45%; not an accepted learning endpoint. Token total omits batching padding and unretained evaluations.'}
    result['source_sha256']={str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.rglob('*')) if f.is_file() and f.name!='manifest.json'}
    text=json.dumps(result,indent=2)+'\n'
    if a.output:
        if a.output.resolve().is_relative_to(p.resolve()):raise ValueError('Do not write into evidence directory')
        with a.output.open('x') as f:f.write(text)
    else:print(text)
if __name__=='__main__':main()
