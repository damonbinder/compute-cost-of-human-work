"""Count-weighted original human chess timing aggregates; standard library only."""
import argparse,csv,json,hashlib,collections,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=a.sources.resolve();o=a.output.resolve();assert not o.exists() and s not in o.parents and s!=o
tr=json.loads((s/'russek-tree.json').read_text());tree={x['path']:x for x in tr['tree']};prefix='VOC_Analysis/Saved_Quantities/aggregate_voc_vs_rt/'
r={};hashes={}
for tc in ['180+0','180+2','300+0','300+3']:
 groups=collections.defaultdict(lambda:[0.,0]);unsplit=[0.,0]
 for kind in ['voc_vs_RT_','voc_vs_RT_split_elo_']:
  for job in range(11):
   path=prefix+kind+tc+'_'+str(job);f=s/('russek__'+path.replace('/','__'));b=f.read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==tree[path]['sha'];hashes[f.name]=hashlib.sha256(b).hexdigest()
   for row in csv.DictReader(b.decode().splitlines()):
    n=int(float(row['rtcount']));v=float(row['rtmean']) if n else 0;assert not n or math.isfinite(v)
    if kind=='voc_vs_RT_':unsplit[0]+=n*v;unsplit[1]+=n
    else:k=row['elo_bin'];groups[k][0]+=n*v;groups[k][1]+=n
 r[tc]={'all_elo':{'move_observations':unsplit[1],'mean_own_clock_seconds':unsplit[0]/unsplit[1]},'elo_groups':{k:{'move_observations':n,'mean_own_clock_seconds':v/n} for k,(v,n) in groups.items()}}
 # Different Elo coverage at boundaries/missing ratings can prevent exact equality.
 r[tc]['split_minus_all_count']=sum(x[1] for x in groups.values())-unsplit[1]
result={'russek_commit':tr['sha'],'input_hashes':hashes,'means':r,'method':'Sum(rtmean*rtcount)/sum(rtcount) across all source VOC cells and eleven original job shards; not equal-weight means of monthly cells.','scope':'Plies15–75, own-clock interval, no opponent pondering; raw input cohorts cannot be deduplicated from aggregates.','sheridan_transfer':{'expert_participants':17,'problems_each':8,'donor_attempts':136,'reported_mean_decision_seconds':28.946,'reported_best_move_accuracy':.93,'estimated_continuation_entry_check_seconds':6,'rounded_puzzle_estimate_seconds':35,'scenario_seconds':[15,90]}}
o.parent.mkdir(parents=True,exist_ok=True);o.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(r,indent=2))
