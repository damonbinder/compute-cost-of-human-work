"""Recompute native usage means. Requires pyarrow; no model calls."""
import argparse,json,statistics
from pathlib import Path
import pyarrow.parquet as pq
cli=argparse.ArgumentParser();cli.add_argument('source_dir',type=Path);cli.add_argument('--output',type=Path);args=cli.parse_args()
out=[]
for f in sorted((args.source_dir/'runs').rglob('full_records/dataset.parquet')):
 a=pq.read_table(f).to_pylist();sc=next(f.parent.parent.glob('*Match_records/dataset.parquet'));scores=pq.read_table(sc).to_pylist();by={r['uid']:r for r in scores}
 assert len(by)==len(a) and set(by)=={r['uid'] for r in a}
 z={'task':a[0]['task_name'],'model':a[0]['model_name'],'records':len(a),'completed':sum(r['completed'] for r in a),'queries':len({r['input_idx'] for r in a}),'prompt_mean':statistics.mean(r['num_prompt_tokens'] for r in a),'completion_mean':statistics.mean(r['num_completion_tokens'] for r in a),'correct':sum(by[r['uid']]['metric_score'] for r in a),'n_calls':sorted({len(r['prompts']) for r in a}),'filepath':str(f.relative_to(args.source_dir))}
 z['tokens']=z['prompt_mean']+z['completion_mean'];z['accuracy']=z['correct']/len(a)
 assert all(r['num_prompt_tokens']>0 and r['num_completion_tokens']>0 for r in a)
 out.append(z)
result=json.dumps(out,indent=2)
if args.output: args.output.write_text(result)
else: print(result)
