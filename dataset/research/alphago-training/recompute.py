"""Reconstruct one AlphaGo Zero40-day run. Standard library; no model execution."""
import argparse, hashlib, json, re, statistics, zipfile
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--sources',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();a.sources=a.sources.resolve();a.output=a.output.resolve()
if a.output.exists() or a.output==a.sources or a.sources in a.output.parents:p.error('Output must be new and outside sources.')
manifest=json.loads((a.sources/'manifest.json').read_text())
for row in manifest:
 if 'sha256' in row:
  assert hashlib.sha256((a.sources/row['file']).read_bytes()).hexdigest()==row['sha256']
games=[]
with zipfile.ZipFile(a.sources/'supplementary-games.zip') as z:
 for name in sorted(z.namelist()):
  if 'Extended Data Figure 5' in name and name.endswith('.sgf') and not '__MACOSX' in name:
   s=z.read(name).decode();games.append({'member':name,'moves':len(re.findall(r';[BW]\[',s)),'result':re.search(r'RE\[([^]]+)',s).group(1)})
assert len(games)==20 and all('R' in g['result'] or 'Resign'in g['result'] for g in games)
S=19*19;C=256
parts={'stem':2*S*17*C*9,'residual_tower':39*2*2*S*C*C*9,
       'policy_conv':2*S*C*2,'policy_dense':2*(S*2)*(S+1),
       'value_conv':2*S*C,'value_dense':2*S*C,'value_output':2*C}
fwd=sum(parts.values()); mean=statistics.mean(g['moves'] for g in games)
selfplay_games=29_000_000;updates=3_100_000;batch=2048
checkpoints=updates//1000;eval_games=checkpoints*400
moves=.9*mean+.1*350
train=3*fwd*updates*batch
selfplay=fwd*selfplay_games*moves*1600
evaluation=fwd*eval_games*mean*1600
# 3x forward approximates forward + parameter/input-gradient passes. Small
# scalar optimizer, normalization and search-control arithmetic are omitted.
out={'architecture_flops':parts,'forward_flops':fwd,'reference_games':games,
     'resigned_reference_mean_moves':mean,'assumed_nonresigned_mean_moves':350,
     'weighted_selfplay_mean_moves':moves,'selfplay_games':selfplay_games,
     'simulations_per_move':1600,'fresh_evaluation_fraction_assumed':1,
     'updates':updates,'positions_per_update':batch,'update_flops':train,
     'evaluations':checkpoints,'evaluation_games':eval_games,
     'selfplay_flops':selfplay,'evaluation_flops':evaluation,'compute_flops':train+selfplay+evaluation,
     'scenarios':{},'human_hours':22000,'human_seconds':22000*3600,
     'human_phase_judgments_hours':{'age5_to9_home':4*300*1,'age9_to12_dojo':3*330*8,'age12_to19_professional':7*300*6}}
for length in [200,mean,moves,350]:
 for fresh in [0.5,0.75,1]:
  out['scenarios'][f'moves={length};fresh={fresh}']=train+fresh*fwd*1600*(selfplay_games*length+eval_games*mean)
out['nonresigning_length_scenarios']={str(n):train+evaluation+fwd*selfplay_games*(.9*mean+.1*n)*1600 for n in [300,350,722]}
with a.output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({k:out[k]for k in ['forward_flops','weighted_selfplay_mean_moves','update_flops','selfplay_flops','evaluation_flops','compute_flops','human_seconds']},indent=2))
