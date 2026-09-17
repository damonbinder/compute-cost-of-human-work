#!/usr/bin/env python3
"""Reconstruct released SCOPE direct TravelPlanner prompts; no model calls.
Dependency: tiktoken. Usage: python recompute.py --source-dir SOURCES [--output NEW.json]
"""
import argparse, ast, copy, hashlib, json, pathlib, re, statistics
import tiktoken

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-dir',required=True,type=pathlib.Path);ap.add_argument('--output',type=pathlib.Path);args=ap.parse_args();p=args.source_dir
    code=p/'scope-baselines__run_directreasoning_travel_planner.py'
    tree=ast.parse(code.read_text())
    selected={'restructure_data','duration_to_hhmm','parse_travel_detail'}
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in selected]
    assert {n.name for n in nodes}==selected
    # These three reviewed functions only transform supplied travel dictionaries.
    # Do not import the original script: its module body changes directories and initializes API clients.
    ns={'re':re};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(code),'exec'),ns)
    prompt=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PLANNER_INSTRUCTION' for t in n.targets))
    data=json.loads((p/'scope-output__travel_planner_direct_gpt-4o.json').read_text())
    refs=[json.loads(s) for s in (p/'scope-data__travel_planner_database__test_ref_info.jsonl').read_text().splitlines()]
    assert len(data)==len(refs)==1000 and set(data)=={str(x) for x in range(1,1001)}
    enc=tiktoken.get_encoding('o200k_base');rows=[]
    for k,v in data.items():
        ref=ns['restructure_data'](copy.deepcopy(refs[int(k)-1]))
        text=prompt.replace('<text>',json.dumps(ref,ensure_ascii=False,indent=4)).replace('<query>',v['prompt_0shot'])
        it=len(enc.encode(text));ot=len(enc.encode(v['plan']))
        rows.append({'source_id':k,'input_content_tokens':it,'output_tokens':ot,'assumed_framing_tokens':7,'total_tokens':it+ot+7,'days_in_output':len(v['structured_plan']),'reference_counts':{a:len(b) for a,b in ref.items()}})
    mean=statistics.mean(r['total_tokens'] for r in rows)
    result={'n':len(rows),'mean_input_content_tokens':statistics.mean(r['input_content_tokens'] for r in rows),'mean_output_tokens':statistics.mean(r['output_tokens'] for r in rows),'mean_total_tokens':mean,'coefficient_flops_per_token':1e11,'mean_compute_flops':mean*1e11,'human_seconds':720,'rows':rows,'source_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [code,p/'scope-output__travel_planner_direct_gpt-4o.json',p/'scope-data__travel_planner_database__test_ref_info.jsonl']}}
    text=json.dumps(result,indent=2)
    if args.output:
        if args.output.resolve().is_relative_to(p.resolve()):raise ValueError('Do not write calculated outputs into retained sources')
        with args.output.open('x') as f:f.write(text+'\n')
    else:print(text)
if __name__=='__main__':main()
