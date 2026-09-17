#!/usr/bin/env python3
"""Read-only reconstruction; tokenizers and tiktoken required. Never executes completions."""
import argparse, ast, csv, gzip, hashlib, json
from pathlib import Path
from tokenizers import Tokenizer
import tiktoken


def constants(path):
    out={}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node,ast.Assign):
            try:v=ast.literal_eval(node.value)
            except (ValueError,TypeError):continue
            for target in node.targets:
                if isinstance(target,ast.Name):out[target.id]=v
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--model-inputs',type=Path,default=Path(__file__).with_name('model-inputs.csv'));a=ap.parse_args()
    s=a.source_dir.resolve();o=a.output.resolve()
    if o==s or s in o.parents:raise SystemExit('Output must be outside source evidence')
    if o.exists():raise SystemExit('Refusing to overwrite existing output')
    files=['qwen-null-generations.json','qwen-null-results.json','gpt4o-evalperf-brief.json','qwen-tokenizer.json','qwen-tokenizer_config.json','qwen-config.json','qwen-model-info.json','partialorder-2-evaluation-code-generation-generations-generate_python.py','HumanEvalPlus-v0.1.10.jsonl.gz']
    manifest={f:hashlib.sha256((s/f).read_bytes()).hexdigest() for f in files}
    q={r['name']:r for r in json.loads((s/files[0]).read_text())}; qr={r['name']:r for r in json.loads((s/files[1]).read_text())};g=json.loads((s/files[2]).read_text())
    tok=Tokenizer.from_file(str(s/'qwen-tokenizer.json'));tok.no_truncation();tok.no_padding()
    qt=lambda text:len(tok.encode(text,add_special_tokens=False).ids)
    ot=tiktoken.get_encoding('o200k_base');gt=lambda text:len(ot.encode(text))
    c=json.loads((s/'qwen-config.json').read_text());d=c['hidden_size'];f=c['intermediate_size'];L=c['num_hidden_layers'];V=c['vocab_size'];kv=c['num_key_value_heads']*(d//c['num_attention_heads'])
    params=2*V*d+L*(2*d*d+2*d*kv+3*d*f+2*d+d+2*kv)+d
    assert params==json.loads((s/'qwen-model-info.json').read_text())['safetensors']['total']==7615616512
    pc=constants(s/'partialorder-2-evaluation-code-generation-generations-generate_python.py');out=[]
    he={r['task_id']:r for r in map(json.loads,gzip.open(s/'HumanEvalPlus-v0.1.10.jsonl.gz','rt'))}
    for i,slug,human in [(26,'duplicate-filter',180),(59,'prime-factor',420),(119,'parentheses',300)]:
        r=q[f'humaneval_{i}']; rr=qr[r['name']];assert len(r['completion'])==len(rr['results'])==1
        prompt=r['prompt'];assert prompt==he[f'HumanEval/{i}']['prompt'];body=r['completion'][0];status=rr['results'][0]['status']
        full='<|im_start|>system\n'+pc['SYSTEM_MESSAGE']+'<|im_end|>\n<|im_start|>user\n'+pc['PROMPT_FORMAT'].format(prompt)+'<|im_end|>\n<|im_start|>assistant\n'
        inp=qt(full);rawproxy='```python\n'+body+'\n```';baseout=qt(rawproxy)+1
        qtotal=inp+baseout+25
        row={'point_id':f'code-function-{slug}-qwen25coder7b','source_id':r['name'],'model_id':'qwen2.5-coder-7b-instruct','input_tokens':inp,'retained_body_tokens':qt(body),'fenced_response_plus_eos_tokens':baseout,'assumed_extra_output_tokens':25,'tokens':qtotal,'flops':2*params*qtotal,'human_seconds':human,'source_status':status,'source_stderr':rr['results'][0]['stderr'],'scenarios':{'no_extra_text_flops':2*params*(inp+baseout),'extra_100_tokens_flops':2*params*(inp+baseout+100),'output_cap_8192_diagnostic_flops':2*params*(inp+8192)}}
        out.append(row)
        gr=g['eval'][f'HumanEval/{i}'];code=gr['profiled'][0]['solution']
        user='Please provide a self-contained Python script that solves the following problem in a markdown code block:'+'\n```python\n'+prompt.strip()+'\n```'
        gin=gt('You are a helpful assistant good at coding.')+gt(user)+12
        gout=gt('```python\n'+code.rstrip()+'\n```')+1
        allocated_input=gin/32
        total=allocated_input+gout+40
        out.append({'point_id':f'code-function-{slug}-gpt4o','source_id':f'HumanEval/{i}','model_id':'gpt-4o-2024-08-06','input_tokens':gin,'allocated_input_tokens':allocated_input,'assumed_shared_choices':32,'retained_code_tokens':gt(code),'fenced_response_plus_eos_tokens':gout,'assumed_extra_output_tokens':40,'tokens':total,'flops':100000000000*total,'human_seconds':human,'source_profile_index':0,'source_retained_profiles':len(gr['profiled']),'source_all_sample_pass_percent':gr['pass@1'],'scenarios':{'no_extra_text_flops':1e11*(allocated_input+gout),'extra_160_tokens_flops':1e11*(allocated_input+gout+160),'full_prefill_flops':1e11*(gin+gout+40),'aggregate_four_prefills_per_100_flops':1e11*(gin*4/100+gout+40),'output_cap_768_diagnostic_flops':1e11*(allocated_input+768),'active_25B_flops':5e10*total,'active_100B_flops':2e11*total}})
    models={r['model_id']:r for r in csv.DictReader(a.model_inputs.open())}
    manifest['model-inputs.csv']=hashlib.sha256(a.model_inputs.read_bytes()).hexdigest()
    for row in out:
        m=models[row['model_id']];N=float(m['active_parameters']);L=float(m['attention_layers']);D=float(m['attention_width'])
        is_gpt=row['model_id'].startswith('gpt-')
        I=row['input_tokens'];O=row['fenced_response_plus_eos_tokens']+row['assumed_extra_output_tokens'];sharing=32 if is_gpt else 1
        def calc(n, layers, width, output=O, divisor=sharing):
            positions=I/divisor+output
            # Allocate causal prefill across branches; each output attends the full prefix.
            context_sum=I*(I+1)/2/divisor+output*I+output*(output+1)/2
            weights=2*n*positions;attention=4*layers*width*context_sum
            return {'positions':positions,'attention_context':context_sum/positions,'weights_flops':weights,'attention_flops':attention,'attention_ratio':attention/weights,'flops':weights+attention}
        row.update(calc(N,L,D))
        row['flops_low']=row['flops_high']=None
        if m['active_parameters_basis']=='estimated':
            def endpoint(n):
                z=max(8,round((n/196608)**(1/3)))
                return calc(n,max(1,round(.65*z)),128*z)['flops']
            row['flops_low']=endpoint(float(m['active_parameters_low']))
            row['flops_high']=endpoint(float(m['active_parameters_high']))
        row['scenarios']={
            'no_omitted_text':calc(N,L,D,output=row['fenced_response_plus_eos_tokens']),
            'more_omitted_text':calc(N,L,D,output=row['fenced_response_plus_eos_tokens']+(160 if is_gpt else 100)),
            'full_prefill':calc(N,L,D,divisor=1),
        }
        if is_gpt:row['scenarios']['four_prefills_per_100']=calc(N,L,D,divisor=25)
    result={'source_hashes':manifest,'qwen_parameters':params,'selection':[26,59,119],'scope':'One retained function attempt per row; GPT4o uses first retained successful profile, not the 100-sample mean.','rows':out}
    o.parent.mkdir(parents=True,exist_ok=True);o.write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
