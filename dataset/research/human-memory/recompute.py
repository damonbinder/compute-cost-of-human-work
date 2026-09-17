#!/usr/bin/env python3
"""Summarize released TaskPr story runs. Requires tokenizers; never calls a model."""
import argparse, json, statistics
from pathlib import Path
from tokenizers import Tokenizer
p=argparse.ArgumentParser();p.add_argument('source_dir',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();b=a.source_dir
enc=Tokenizer.from_file(str(b/'llama-tokenizer.json'))
count=lambda text:len(enc.encode(text,add_special_tokens=False).ids)
human=[json.loads(f.read_text()) for f in sorted((b/'runs/human/semantic-memory-story-recall').glob('*.json'))]
model=[json.loads(l) for l in (b/'runs/prompting/meta-llama_llama-3-8b-instruct/tasks/semantic_story_recall.jsonl').read_text().splitlines() if l]
result={'repo_commit':json.loads((b/'tree.json').read_text())['sha'],'human_all_records':len(human),'human_completed':sum(r['status']=='completed' for r in human),'notes':'Completed session records, not paper participant cohort. Ten input chat-format tokens plus one generated end-of-turn token; no provider usage counters. Full fresh single-request prefix assumption.','stories':{}}
for name in ['Baseball','Eyespy','Pieman','Oregon Trail']:
 h=[r for r in human if r['status']=='completed' and r.get('metadata',{}).get('storyName')==name and r.get('duration_ms',0)>0]
 m=[r for r in model if r['condition']=='C1' and r['story_name']==name]
 inp=[count(r['recall_prompt'])+10 for r in m];out=[count(r['llm_recall'])+1 for r in m]
 f=m[0]['story_source_file'];text=(b/'data'/f).read_text()
 result['stories'][name]={'human_n':len(h),'human_participants':len(set(r['participant_id'] for r in h)),'human_mean_seconds':statistics.mean(r['duration_ms']/1000 for r in h),'human_median_seconds':statistics.median(r['duration_ms']/1000 for r in h),'human_range_seconds':[min(r['duration_ms']/1000 for r in h),max(r['duration_ms']/1000 for r in h)],'human_mean_embedding_similarity':statistics.mean(r['summary']['embeddingSimilarity'] for r in h),'human_mean_words':statistics.mean(len(r['payload']['recallText'].split()) for r in h),'ai_n':len(m),'ai_mean_embedding_similarity':statistics.mean(r['metrics']['embeddingSimilarity'] for r in m),'ai_mean_words':statistics.mean(len(r['llm_recall'].split()) for r in m),'input_tokens_mean':statistics.mean(inp),'output_tokens_mean':statistics.mean(out),'tokens_mean':statistics.mean(x+y for x,y in zip(inp,out)),'compute_flops':statistics.mean(x+y for x,y in zip(inp,out))*16e9,'max_total_tokens':max(x+y for x,y in zip(inp,out)),'story_words':len(text.split()),'human_records':[r['run_id'] for r in h],'ai_repeats':[r['repeat_index'] for r in m]}
s=json.dumps(result,indent=2)+'\n'
if a.output:
 if a.output.exists():raise SystemExit('Refusing to overwrite output')
 a.output.write_text(s)
else:print(s)
