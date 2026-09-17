"""Read retained sources; print audit or write a NEW --output. Requires tiktoken.
python recompute_workplace.py --sources SOURCE_DIR --models MODELS_CSV [--output NEW_JSON]
"""
import argparse, ast, base64, csv, gzip, json, math, re, statistics
from pathlib import Path
import tiktoken

p = argparse.ArgumentParser()
p.add_argument('--sources', type=Path, required=True)
p.add_argument('--models', type=Path, required=True)
p.add_argument('--output', type=Path)
a = p.parse_args()
src = a.sources
models = {x['model_id']: x for x in csv.DictReader(a.models.open())}
coef = lambda mid: float(models[mid]['flops_per_token'])
load = lambda n: json.loads((src/n).read_text())
mean = statistics.mean
enc = tiktoken.Encoding(name='retained_cl100k', pat_str=r"'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}++|\p{N}{1,3}+| ?[^\s\p{L}\p{N}]++[\r\n]*+|\s++$|\s*[\r\n]|\s+(?!\S)|\s", mergeable_ranks={base64.b64decode(t): int(v) for t,v in (l.split() for l in (src/'cl100k_base.tiktoken').read_bytes().splitlines())}, special_tokens={})
nt = lambda s: len(enc.encode(s))
schemas = []
for f in sorted(src.glob('tau-tool-*.py')):
    tree = ast.parse(f.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'get_info':
            ret = next(n for n in ast.walk(node) if isinstance(n, ast.Return))
            schemas.append(ast.literal_eval(ret.value))
schema_tokens = nt(json.dumps(schemas, separators=(',',':')))
retail=[]
for row in load('tau-sonnet-retail.json'):
    history=0; inputs=outputs=calls=0
    for m in row['traj']:
        # Concrete message text, names and tool-call arguments; wrapper is estimated.
        body = str(m.get('content') or '')
        if m.get('tool_calls'):
            body += json.dumps([x['function'] for x in m['tool_calls']],separators=(',',':'))
        if m.get('name'): body += m['name']
        n=nt(body)+4
        if m['role']=='assistant':
            inputs += history+schema_tokens+3
            outputs += n
            calls += 1
        history += n
    retail.append({'task_id':row['task_id'],'trial':row['trial'],'reward':row['reward'],'input':inputs,'output':outputs,'calls':calls})
rt=mean(x['input']+x['output'] for x in retail)
telecom=load('tau2-telecom.json'); tel=[]
for row in telecom['simulations']:
    counts={r:{'input':0,'cached_input':0,'fresh_input':0,'output':0,'calls':0} for r in ['assistant','user']}
    for m in row['messages']:
        if m.get('usage'):
            c=counts[m['role']];u=m['usage']
            # Original release records completion_cost(response), then drops the
            # cache detail from usage. Invert only that known accounting equation;
            # this does not convert dollars to FLOPs or infer total token usage.
            cache=(2*u['prompt_tokens']+8*u['completion_tokens']-1e6*m['cost'])/1.5
            assert abs(cache-round(cache))<1e-6 and round(cache)%128==0
            cache=round(cache)
            assert 0 <= cache <= u['prompt_tokens']
            c['input']+=u['prompt_tokens'];c['output']+=u['completion_tokens'];c['calls']+=1
            c['cached_input']+=cache;c['fresh_input']+=u['prompt_tokens']-cache
    tel.append({'task_id':row['task_id'],'trial':row['trial'],'reward':row['reward_info']['reward'],**counts})
tt_full=mean(x['assistant']['input']+x['assistant']['output'] for x in tel)
tt=mean(x['assistant']['fresh_input']+x['assistant']['output'] for x in tel)
events=json.loads(gzip.decompress((src/'company-admin-employee-info-reconciliation-trajectories.json').read_bytes()))
responses={}
for e in events:
    if e.get('tool_call_metadata'):
        r=e['tool_call_metadata']['model_response']
        if r['id'] in responses: assert responses[r['id']]==r
        responses[r['id']]=r
company=[]
for r in responses.values():
    u=r['usage'];company.append({'id':r['id'],'model':r['model'],'prompt':u['prompt_tokens'],'creation':u.get('cache_creation_input_tokens',0),'read':u.get('cache_read_input_tokens',0),'output':u['completion_tokens']})
# LiteLLM's recorded prompt includes cache reads, but excludes cache creation.
# Read positions do not receive another full parameter pass.
assert all(x['prompt'] >= x['read'] for x in company)
ct_full=sum(x['prompt']+x['creation']+x['output'] for x in company)
ct=sum(x['prompt']-x['read']+x['creation']+x['output'] for x in company)
log=(src/'osworld-dnt-runtime.log').read_text()
calls=[]
for u in re.findall(r'usage=BetaUsage\((.*?)\)\)',log):
    fields={k:int(v) for k,v in re.findall(r'\b(cache_creation_input_tokens|cache_read_input_tokens|input_tokens|output_tokens)=(\d+)',u)}
    calls.append(fields)
assert len(calls)==15
native=sum(sum(x.values()) for x in calls)
# All 14 increments add the prior response and exactly 1270 new input positions.
# This independently supports retention of one screenshot/result per turn.
increments=[calls[i]['input_tokens']-calls[i-1]['input_tokens']-calls[i-1]['output_tokens'] for i in range(1,len(calls))]
assert increments==[1270]*14
# The nearby public adapter is a proxy, not the unreleased exact Sonnet 4.5 revision.
images=sum(range(1,16)); visual_per_image=math.ceil(1280/28)*math.ceil(720/28)
visual=images*visual_per_image; text=native-visual
# ViT-L/16 architecture proxy, including quadratic encoder attention.
patches=80*45+1
encoder_per_image=2*307e6*patches + 4*24*patches**2*1024
encoder=images*encoder_per_image
backbone=native*coef('claude-sonnet-4-5')
out={
 'retail':{'attempts':len(retail),'unique_tasks':len({x['task_id'] for x in retail}),'successes':sum(x['reward'] for x in retail),'mean_tokens':rt,'compute_flops':rt*coef('claude-3-5-sonnet-20241022'),'schema_tokens':schema_tokens,'tool_count':len(schemas),'mean_calls':mean(x['calls'] for x in retail),'runs':retail},
 'telecom':{'attempts':len(tel),'unique_tasks':len(telecom['tasks']),'successes':sum(x['reward'] for x in tel),'mean_tokens':tt,'compute_flops':tt*coef('gpt-4.1-2025-04-14'),'full_prefix_mean_tokens':tt_full,'full_prefix_flops':tt_full*coef('gpt-4.1-2025-04-14'),'worker_cached_input':sum(x['assistant']['cached_input'] for x in tel),'simulator_mean_tokens':mean(x['user']['fresh_input']+x['user']['output'] for x in tel),'simulator_full_prefix_mean_tokens':mean(x['user']['input']+x['user']['output'] for x in tel),'mean_calls':mean(x['assistant']['calls'] for x in tel),'mean_underlying_issues':mean(len(t['id'].split(']')[1].split('[PERSONA:')[0].split('|')) for t in telecom['tasks']),'runs':tel},
 'company':{'calls':len(company),'tokens':ct,'compute_flops':ct*coef('claude-3-7-sonnet'),'full_prefix_tokens':ct_full,'full_prefix_flops':ct_full*coef('claude-3-7-sonnet'),'responses':company},
 'osworld':{'calls':len(calls),'native_multimodal_positions':native,'image_presentations':images,'image_positions':visual,'text_tokens':text,'backbone_flops':backbone,'encoder_proxy_flops':encoder,'encoder_share':encoder/(backbone+encoder),'compute_flops':backbone+encoder,'encoder_unique_images_scenario':15*encoder_per_image,'input_growth_beyond_previous_output':increments,'calls_usage':calls}}
s=json.dumps(out,indent=2)
if a.output:
    with a.output.open('x') as f:f.write(s+'\n')
else: print(s)
