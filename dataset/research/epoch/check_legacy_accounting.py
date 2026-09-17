#!/usr/bin/env python3
"""Read-only replay of native counter arithmetic with retained reviewed corrections.
Does not redo tokenizer reconstruction, research judgments, or error classification.
Python standard library. No network, generators, or input mutations.
"""
import argparse,collections,csv,hashlib,json,math,re
from pathlib import Path

def main():
 a=argparse.ArgumentParser(description=__doc__)
 a.add_argument('--sources',type=Path,required=True)
 a.add_argument('--points',type=Path,required=True)
 a.add_argument('--models',type=Path,required=True)
 a.add_argument('--output',type=Path,required=True)
 v=a.parse_args();s=v.sources.resolve();out=v.output.resolve()
 if out.exists() or out==s or s in out.parents or out in [v.points.resolve(),v.models.resolve()]:a.error('Output must be new and outside evidence.')
 def read(p):return json.loads(p.read_text())
 arc=s/'legacy-accounting'
 for x in read(arc/'manifest.json'):
  assert hashlib.sha256((arc/x['path']).read_bytes()).hexdigest()==x['sha256']
 rows={r['point_id']:r for r in csv.DictReader(v.points.open())};models={r['model_id']:r for r in csv.DictReader(v.models.open())}
 prior={r['point_id']:r for r in read(arc/'native-audit-corrections/calculations.json')}
 glm=read(arc/'expansion-04/usage-recovery.json');retry=read(arc/'native-audit-corrections/glm5-retry-calculations.json')
 # These four original native collections define this bounded replay.
 names=['simpleqa.md','epoch-expansion-logged.md','swebench.md','epoch-expansion-glm-kimi.md']
 ids=[]
 for name in names:
  ids += re.findall(r'^## ([a-z]+-epoch-\S+)$',(Path(__file__).parent/name).read_text(),re.M)
 result=[]
 for pid in dict.fromkeys(ids):
  h=read(s/pid/'header.json');records=read(s/pid/'summaries.json');primary=h['eval']['model'];u=collections.Counter()
  for record in records:u.update(record.get('model_usage',{}).get(primary,{}))
  if primary.startswith('anthropic/'):
   recorded=u['input_tokens']+u['input_tokens_cache_write']+u['output_tokens']
  else:
   recorded=u['input_tokens']-u['input_tokens_cache_read']+u['output_tokens']
   if primary.startswith('google/'):recorded+=u['reasoning_tokens']
  included=recorded;correction='none'
  if pid in glm:
   assert math.isclose(recorded,glm[pid]['recorded_included_tokens'])
   included=glm[pid]['corrected_included_tokens'];correction='retained tokenizer/native-error recovery and imputation'
  if pid in prior:
   assert math.isclose(recorded,prior[pid]['recorded_included_tokens'])
   included=recorded+prior[pid]['extra_tokens'];correction='retained failure imputation'
  if pid==retry['point_id']:
   included=retry['observed_and_tokenized_tokens']+retry['counts']['potentially_executed_failed_calls']*retry['mean_known_response_tokens'];correction='retained full-run read-failure audit'
  denominator=h['results']['completed_samples'];tokens=included/denominator;r=rows[pid];flops=tokens*float(models[r['model_id']]['flops_per_token'])
  assert math.isclose(tokens,float(r['tokens']),rel_tol=1e-9),(pid,tokens,r['tokens'])
  assert math.isclose(flops,float(r['compute_flops']),rel_tol=1e-9),(pid,flops,r['compute_flops'])
  result.append(dict(point_id=pid,recorded_tokens=recorded,corrected_tokens=included,completed_samples=denominator,tokens=tokens,compute_flops=flops,correction=correction))
 out.write_text(json.dumps({'scope':'native counter arithmetic with frozen reviewed correction artifacts; not full source re-extraction','points':result},indent=2)+'\n')
 print(f'{len(result)} current rows reproduced')
if __name__=='__main__':main()
