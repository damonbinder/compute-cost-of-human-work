#!/usr/bin/env python3
"""Original ARC2 response/human-pair reconstruction. No generated code execution."""
import argparse,csv,json,pathlib,hashlib,re,collections,importlib.util
spec=importlib.util.spec_from_file_location('arc_native_helpers',pathlib.Path(__file__).with_name('recompute-v1-remaining.py'));H=importlib.util.module_from_spec(spec);spec.loader.exec_module(H)
p=argparse.ArgumentParser()
for x in ['sources','human-sources','models','manifest','human-manifest','output']:p.add_argument('--'+x,type=pathlib.Path,required=True)
a=p.parse_args();s=a.sources.resolve();hs=a.human_sources.resolve();o=a.output.resolve()
if o.exists() or s in o.parents or hs in o.parents:raise SystemExit('Output must be new and outside sources')
for path,base in [(a.manifest,s),(a.human_manifest,hs)]:
 for x in json.loads(path.read_text()):
  f=(base/x['file']).resolve();assert base in f.parents and H.sha256(f)==x['sha256'],f
models={x['model_id']:x for x in csv.DictReader(a.models.open())};tasks={f.stem:json.loads(f.read_text()) for f in (hs/'tasks').glob('*.json')};assert len(tasks)==120
humans=collections.defaultdict(list);excluded=collections.defaultdict(list)
for h in csv.DictReader((hs/'human-attempts.csv').open()):
 if h['task_set']!='Public Eval':continue
 key=(h['task_ID'],int(h['test_index']));assert key[0] in tasks
 (humans if float(h['duration_seconds'])>5 else excluded)[key].append(h)
assert len({(h['session_ID'],h['task_ID'],h['test_index']) for rows in humans.values() for h in rows})==sum(map(len,humans.values())), 'Repeated human view identity'
out={'points':[]}
for endpoint,pid in [('gemini-3-deep-think-preview','reas-arcagi-v2-gemini3dt'),('grok-4.20-beta-0309b-reasoning','reas-arcagi-v2-grok420')]:
 pairs=collections.defaultdict(list);missing=[];diagnostics=[];found=set();all_responses=[]
 for f in sorted((s/'runs/v2'/endpoint).glob('*.json')):
  if not re.fullmatch('[0-9a-f]{8}',f.stem):continue
  task=tasks[f.stem];found.add(f.stem)
  for idx,pair in enumerate(json.loads(f.read_text())):
   for slot in ['attempt_1','attempt_2']:
    ans=pair.get(slot)
    if not ans or not ans.get('metadata'):missing.append({'task_id':f.stem,'array_index':idx,'slot':slot});continue
    m=ans['metadata'];assert m['model']==endpoint and m['task_id']==f.stem
    prompt,test,train=H.prompt_data(m);assert train==task['train'];ix=[i for i,t in enumerate(task['test']) if test==t['input']];assert len(ix)==1;(i,)=ix
    correct=ans['answer']==task['test'][i]['output'];assert ans.get('correct',correct)==correct
    u=H.usage(m);r={'task_id':f.stem,'actual_index':i,'array_index':idx,'metadata_index':m.get('pair_index'),'slot':slot,'correct':correct,'usage':u,'kwargs':m['kwargs'],'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'start':m['start_timestamp']}
    pairs[(f.stem,i)].append(r);all_responses.append(r)
    def scan(x,path=''):
     if isinstance(x,dict):
      for k,v in x.items():
       if 'cache' in k.lower() or (v and any(y in k.lower() for y in ['error','status','finish_reason','tool_calls','num_turns'])):diagnostics.append({'task_id':f.stem,'slot':slot,'path':path+'/'+k,'value':v})
       scan(v,path+'/'+k)
     elif isinstance(x,list):
      for j,v in enumerate(x):scan(v,path+'/'+str(j))
    scan(ans)
    if u['native_total']==0:diagnostics.append({'task_id':f.stem,'slot':slot,'zero_total_response':True})
 records=[];omitted=[]
 for task_id,t in tasks.items():
  for i in range(len(t['test'])):
   key=(task_id,i);rs=pairs[key];hh=humans[key]
   if len(rs)!=2 or {r['slot'] for r in rs}!={'attempt_1','attempt_2'} or not hh:
    omitted.append({'task_id':task_id,'test_index':i,'responses':rs,'human_n':len(hh),'reason':'No complete response pair or no eligible human views'});continue
   assert len({r['prompt_sha256'] for r in rs})==1
   records.append({'task_id':task_id,'test_index':i,'responses':rs,'tokens':sum(r['usage']['counted_tokens'] for r in rs),'correct':any(r['correct'] for r in rs),'human_n':len(hh),'human_seconds_sum':sum(float(h['duration_seconds']) for h in hh),'human_correct_n':sum(int(h['correct_submissions'])>0 for h in hh),'human_submissions_histogram':dict(collections.Counter(h['submissions'] for h in hh)),'human_sessions':hh,'excluded_short_views':excluded[key]})
 n=sum(r['human_n'] for r in records);assert n
 tokens=sum(r['tokens']*r['human_n'] for r in records)/n;coef=float(models[endpoint]['flops_per_token']);outputs=sum(sum(x['usage']['output_including_reasoning'] for x in r['responses'])*r['human_n'] for r in records)/n;second=sum(next(x['usage']['prompt_tokens'] for x in r['responses'] if x['slot']=='attempt_2')*r['human_n'] for r in records)/n
 out['points'].append({'point_id':pid,'model_id':endpoint,'task_files':len(found),'included_pairs':len(records),'included_tasks':len({r['task_id'] for r in records}),'human_attempts':n,'human_time':sum(r['human_seconds_sum'] for r in records)/n,'human_score':sum(r['human_correct_n'] for r in records)/n,'ai_score':sum(r['correct']*r['human_n'] for r in records)/n,'tokens':tokens,'compute_flops':tokens*coef,'input_tokens':tokens-outputs,'output_tokens':outputs,'excluded_short_views':sum(len(r['excluded_short_views']) for r in records),'responses_all':len(all_responses),'retained_tokens_all':sum(r['usage']['counted_tokens'] for r in all_responses),'omitted_tokens':sum(sum(q['usage']['counted_tokens'] for q in r['responses']) for r in omitted),'cache_sensitivity':{'all_input_cached_tokens':outputs,'second_input_cached_tokens':tokens-second},'metadata_index_mismatches':[r for r in all_responses if r['actual_index']!=r['array_index'] or r['metadata_index']!=r['actual_index']],'diagnostics':diagnostics,'missing_slots':missing,'included':records,'omitted':omitted})
out['source_manifest_sha256']=H.sha256(a.manifest);out['human_manifest_sha256']=H.sha256(a.human_manifest);out['models_sha256']=H.sha256(a.models)
o.parent.mkdir(parents=True,exist_ok=True);o.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps([{k:v for k,v in r.items() if k not in ['included','omitted','diagnostics','missing_slots','metadata_index_mismatches']} for r in out['points']],indent=2))
