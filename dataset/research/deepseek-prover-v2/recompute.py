"""Read original theorem/text sources and reconstruct two whole-proof workloads.
Requires tokenizers, never runs Lean or a model. Output must be new.
"""
import argparse,collections,csv,hashlib,json,re,statistics,zipfile
from pathlib import Path
from tokenizers import Tokenizer
p=argparse.ArgumentParser();p.add_argument('--sources',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();s=a.sources.resolve();o=a.output.resolve()
if o.exists() or o.is_relative_to(s):raise SystemExit('Output must be new and outside sources')
original=[json.loads(x) for x in (s/'minif2f-v15.jsonl').read_text().splitlines()];original=[x for x in original if x['split']=='test'];assert len(original)==244
z=zipfile.ZipFile(s/'minif2f-solutions.zip');proofs={Path(n).stem:z.read(n).decode() for n in z.namelist() if n.startswith('test/') and n.endswith('.lean')};assert len(proofs)==217
# The exact revised source theorem/description is available for 217 successes.
# Use predecessor statements for the other 27 only as an input-length proxy.
tok=Tokenizer.from_file(str(s/'model-tokenizer.json'));tok.no_padding();tok.no_truncation()
cfg=json.loads((s/'model-tokenizer-config.json').read_text())
readme=(s/'README.md').read_text();prompt=re.search(r'prompt = """\n(.*?)\n"""\.strip\(\)',readme,re.S)[1]
noncot=prompt[:prompt.index('\n\nBefore producing')]
rows=[];modes={}
for mode,pr,out,score in [('noncot',noncot,761.8,73.8),('cot',prompt,6751.9,82.4)]:
 counts=[];sourcecounts=collections.Counter()
 for q in original:
  if q['name'] in proofs:
   # Stop before the proof body; include the supplied statement and original header.
   txt=proofs[q['name']];match=re.search(r':=\s*by\b',txt);assert match
   stmt=txt[:match.end()]+'\n  sorry'
   kind='v2_released_statement'
  else:stmt=q['header']+q['informal_prefix']+q['formal_statement']+'  sorry';kind='v15_unresolved_input_proxy'
  # Exact one-user/no-system branch of the original chat template.
  assert "'<｜User｜>' + message['content'] + '<｜Assistant｜>'" in cfg['chat_template']
  bos=cfg['bos_token']['content'] if isinstance(cfg['bos_token'],dict) else cfg['bos_token']
  text=bos+'<｜User｜>'+pr.format(stmt.strip())+'<｜Assistant｜>'
  count=len(tok.encode(text,add_special_tokens=False).ids);counts.append(count);sourcecounts[kind]+=1
  if mode=='cot':rows.append({'name':q['name'],'input_tokens':count,'input_source':kind,'statement':stmt})
 mean=statistics.mean(counts);tokens=32*(mean+out)
 modes[mode]={'input_tokens_mean':mean,'input_tokens_max':max(counts),'input_source_counts':dict(sourcecounts),'reported_generated_tokens_mean':out,'sample_budget':32,'reported_pass32_percent':score,'input_output_positions':tokens,'flops':tokens*74e9,'shared_prefill_flops':(mean+32*out)*74e9,'half_output_mean_flops':32*(mean+out/2)*74e9,'double_output_mean_flops':32*(mean+out*2)*74e9,'input_proxy_plus25pct_flops':32*(mean*1.25+out)*74e9}
human_groups={'MATH':{'n':130,'minutes_assumed':20},'AMC':{'n':45,'minutes_assumed':60},'AIME':{'n':15,'minutes_assumed':120},'custom':{'n':34,'minutes_assumed':60},'IMO':{'n':20,'minutes_assumed':240}}
assert sum(x['n'] for x in human_groups.values())==len(original)
weighted_minutes=sum(x['n']*x['minutes_assumed'] for x in human_groups.values())/len(original)
result={'human':{'component_judgments':human_groups,'weighted_minutes':weighted_minutes,'rounded_seconds':3600,'half_double_seconds':[1800,7200],'timing_donor_attempts':21},'active_parameters_reported_architecture':37000000000,'flops_per_token':74000000000,'modes':modes,'task_inputs':rows,'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(s.iterdir()) if p.is_file()}}
o.write_text(json.dumps(result,indent=2)+'\n')
