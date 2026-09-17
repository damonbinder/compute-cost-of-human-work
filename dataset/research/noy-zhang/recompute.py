from pathlib import Path
import pandas as pd,numpy as np,re,json,itertools
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--sources',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();p=args.sources.resolve();out=args.output.resolve()
if out==p or p in out.parents or out in p.parents:raise SystemExit('Output must be separate from sources')
if out.exists() and any(out.iterdir()):raise SystemExit('Output directory must be new or empty')
out.mkdir(parents=True,exist_ok=True)
s=pd.read_csv(p/'fullsurvey.csv',low_memory=False)
print('survey raw',len(s))
s=s[(s.finished!=0)&(s.consent!=2)&(s.consent_exact!=2)].copy()
s['date']=pd.to_datetime(s.startdate,errors='coerce').dt.normalize()
dates=s.groupby('prolific_pid').date.min()
g=pd.read_csv(p/'grading_long_complete.csv');g['date']=pd.to_datetime(g.StartDate,errors='coerce').dt.normalize()
g=g[(g.grader_id!='043a718774c572bd8a25adbeb1bfcd5c0256ae11cecf9f9c3f925d0e52beaf89')&(g.retry!=1)].copy()
g=g[~(g.date>g.grader_id.map(dates))&g.overall.notna()].copy()
print('grades before reliability',len(g),'pure',g.prolific_pid.str.lower().eq('chatgpt').sum())
pairs={}
for _,a in g[~g.prolific_pid.isin(['chatGPT','ChatGPT'])].groupby(['prolific_pid','essaynum']):
 if len(a)<2:continue
 for x,y in itertools.combinations(a[['grader_id','overall']].itertuples(index=False,name=None),2):
  pairs.setdefault(x[0],[]).append((y[1],x[1]));pairs.setdefault(y[0],[]).append((x[1],y[1]))
bad=[]
for k,ps in pairs.items():
 a=np.array(ps);slope=np.cov(a[:,0],a[:,1],ddof=0)[0,1]/np.var(a[:,0]) if np.var(a[:,0]) else 0
 if slope<.1:bad.append(k)
g=g[~g.grader_id.isin(bad)].copy()
print('bad graders',len(bad),'grades after',len(g),'pure',g.prolific_pid.str.lower().eq('chatgpt').sum())
print(g[g.prolific_pid.str.lower().eq('chatgpt')].groupby('occupation').overall.agg(['count','mean']).to_string())
# Original first-response and quality filters.
clean=(p/'clean.do').read_text();section=clean[clean.index('gen plagiarism'):clean.index('* dropping bad responses')]
manual=set(re.findall(r'"([0-9a-f]{64})"',section))
s=s.sort_values(['prolific_pid','startdate']).drop_duplicates('prolific_pid');s=s[~s.prolific_pid.isin(manual)]
qs=[]
for f in ['grading.xlsx','grading_retry.xlsx']:
 q=pd.read_excel(p/f);q['qcheck']=q.qcheck.replace(3,1);q=q.groupby('prolific_pid').qcheck.agg(['min','max']);qs.append(q)
q=pd.concat(qs);q=q[~q.index.duplicated(keep='first')]
s=s.join(q,on='prolific_pid');s=s[~((s['max']>1)|(s['min']<1))]
rawg=pd.read_csv(p/'grading_long_complete.csv');rawg['date']=pd.to_datetime(rawg.StartDate,errors='coerce').dt.normalize();gd=rawg.groupby('grader_id').date.min();s=s[~(s.date>s.prolific_pid.map(gd))]
print('clean humans',len(s),'treatment',s.treatment.value_counts().to_dict(),'outcomes',s.outcome.value_counts().to_dict())
# Each participant has two tasks, self-reported minutes and objective page time.
records=[]
for _,r in s.iterrows():
 for n in [1,2]:
  task='a' if (n==1)==(r.a_first==1) else 'b'
  reported=sum(r[f'time{n}_{j}'] for j in [4,5,6,7])
  ai=r.usedgpt_first if n==1 else r.usedgpt
  records.append(dict(pid=r.prolific_pid,responseid=r.responseid,occupation=r.occupation,task=task.upper(),n=n,treatment=r.treatment,incentive_arm=r.incentive_arm,ai=ai,time_reported=reported*60,time_page=r[f'task_{task}_timespent_pagesubmit']))
r=pd.DataFrame(records);r.to_csv(out/'noy-human-timings.csv',index=False);g.to_csv(out/'noy-filtered-grades.csv',index=False)
print('first AI responses',r[r.n==1].ai.value_counts(dropna=False).to_dict(),'second',r[r.n==2].ai.value_counts(dropna=False).to_dict())
print(r[(r.n==1)|(r.treatment==0)].groupby(['occupation','task']).agg(n=('time_reported','count'),median_reported=('time_reported','median'),median_page=('time_page','median')).to_string())
# Self-reported no-ChatGPT baseline; first-task blanks are a questionnaire skip.
f=pd.read_csv(p/'fullsurvey_fulltext.csv',low_memory=False).set_index('responseid')
assert f.index.is_unique
assert set(s.responseid).issubset(set(f.index))
for _, selected in s.iterrows():
 actual=f.loc[selected.responseid]
 assert actual.prolific_pid==selected.prolific_pid and actual.occupation==selected.occupation
 assert actual.StartDate==selected.startdate
software=f.software.fillna('').astype(str)
ai_other=software.str.split(',').apply(lambda x: bool(set(x)&{'1','3'})) | f.software_6_TEXT.fillna('').str.contains('you.com',case=False,regex=False)
r=r[(((r.n==1)&(r.ai!=1))|((r.n==2)&r.ai.isin([2,4]))) & ~r.responseid.map(ai_other).fillna(False) & r.time_reported.notna() & r.incentive_arm.isin(['linear','convex'])].copy()
# Use the common original raw grader set for both groups, as in published pure-GPT table.
w=pd.read_csv(p/'grading_wide_complete.csv');w=w[(w.grader_id!='043a718774c572bd8a25adbeb1bfcd5c0256ae11cecf9f9c3f925d0e52beaf89')&(w.retry_a!=1)&(w.retry_b!=1)]
raw=pd.read_csv(p/'grades.csv');raw=raw[raw.grader_id.isin(w.grader_id)]
rawrows=[]
for _,a in raw.iterrows():
 for n in range(1,8):
  for t in ['A','B']:
   suf=f'{n}{t}';grade=a.get('overall'+suf)
   if pd.isna(grade):continue
   rawrows.append(dict(pid=a.get('prolific_pid.'+suf),occupation=a.occupation,task=t,text=a.get('essay.'+suf),grade=float(grade),grader=a.grader_id,prompt=a.get('task'+t),retry=a.get('retry.'+suf)))
a=pd.DataFrame(rawrows);a=a[a.retry!=1]
ai=a[a.pid.eq('ChatGPT')].copy()
# Match the actual selected survey response, not merely repeated participant IDs.
from html.parser import HTMLParser
class SourceTextParser(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,data):self.parts.append(data)
def source_text(value):
 if pd.isna(value):return None
 parser=SourceTextParser();parser.feed(str(value));return ' '.join(' '.join(parser.parts).split())
selected_by_pid=s.set_index('prolific_pid')
eligible=set(zip(r.pid,r.task))
matched=[];audit=[]
for idx,row in a[~a.pid.eq('ChatGPT')].iterrows():
 if (row.pid,row.task) not in eligible:continue
 selected=selected_by_pid.loc[row.pid];actual=f.loc[selected.responseid]
 expected=source_text(actual['task_'+row.task.lower()]);shown=source_text(row.text)
 status='unmatched_text'
 if row.occupation!=selected.occupation:status='different_occupation_response'
 elif shown is None or not shown:status='missing_displayed_text'
 elif shown==expected:status='matched'
 elif expected and shown.replace('"','')==expected.replace('"',''):status='matched_quote_formatting'
 elif shown==source_text(actual['task_'+('b' if row.task=='A' else 'a')]):status='wrong_task_displayed'
 elif shown==source_text(actual['task-retry']):status='retry_text_displayed'
 else:
  other=f[f.prolific_pid.eq(row.pid)]
  if any(shown==source_text(v) for v in other['task_'+row.task.lower()]):status='different_survey_response'
 keep=status in ['matched','matched_quote_formatting']
 if keep:matched.append(idx)
 audit.append(dict(pid=row.pid,responseid=selected.responseid,occupation=selected.occupation,task=row.task,grader=row.grader,grade=row.grade,status=status,retained=keep))
(out/'human-grade-mapping-audit.json').write_text(json.dumps(dict(selected_responses=s[['prolific_pid','responseid','startdate','occupation']].to_dict('records'),slots=audit),indent=2)+'\n')
human=a.loc[matched].groupby(['pid','task','grader']).grade.mean().groupby(['pid','task']).mean().rename('grade')
r=r.join(human,on=['pid','task']);print('human with no grade',r.grade.isna().sum());r=r[r.grade.notna()]
print('final human',len(r));print(r.groupby(['occupation','task']).agg(n=('time_reported','count'),mean=('time_reported','mean'),median=('time_reported','median'),grade=('grade','mean')).round(3).to_string())
print('AI answer-balanced quality');print(ai.drop_duplicates(['occupation','task','text','grader']).groupby(['occupation','task','text']).grade.mean().groupby(['occupation','task']).agg(['count','mean']).to_string())
r.to_csv(out/'noy-human-unaided.csv',index=False);ai.to_json(out/'noy-ai-valid.json',orient='records',indent=2)
# The same AI email occurs under both prompts in some grading sheets.
# Keep only ratings under the matching company/task. No answer is discarded.
def actual_task(row):
 if row.occupation in ['manager','HR professional']:
  if 'AccureCo' in row.text:return 'B'
  if 'WorkCo' in row.text or 'virtual office' in row.text.lower():return 'A'
 return row.task
ai['actual_task']=ai.apply(actual_task,axis=1)
misplaced=ai[ai.task!=ai.actual_task].copy();ai=ai[ai.task==ai.actual_task].copy()
print('misplaced AI ratings',len(misplaced));print(ai.groupby(['occupation','task','text']).grade.mean().groupby(['occupation','task']).agg(['count','mean']).to_string())
misplaced.to_json(out/'misplaced-ai-ratings.json',orient='records',indent=2)
ai.to_json(out/'noy-ai-correct-prompt.json',orient='records',indent=2)
# Direct source HTML rendered to text; ChatGPT request logs were not released.
from html.parser import HTMLParser
class TextParser(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,data):self.parts.append(data)
import tiktoken,hashlib
import os
cache=out/'tokenizer-cache';cache.mkdir(exist_ok=True)
for name in ['cl100k_base','p50k_base']:
 url='https://openaipublic.blob.core.windows.net/encodings/'+name+'.tiktoken'
 (cache/hashlib.sha1(url.encode()).hexdigest()).write_bytes((p/(name+'.tiktoken')).read_bytes())
os.environ['TIKTOKEN_CACHE_DIR']=str(cache)
enc=tiktoken.get_encoding('cl100k_base');helper_enc=tiktoken.get_encoding('p50k_base')
def plain(x):
 parser=TextParser();parser.feed(str(x));return ' '.join(' '.join(parser.parts).split())
results=[];texts=[]
for (occupation,task),group in ai.groupby(['occupation','task']):
 if occupation=='consultant':continue # Original pasted reference documents still need recovery.
 human=r[(r.occupation==occupation)&(r.task==task)]
 per_grader=group.groupby(['text','grader'],sort=True).agg(grade=('grade','mean'),prompt=('prompt','first')).reset_index()
 unique=per_grader.groupby('text',sort=True).agg(grade=('grade','mean'),prompt=('prompt','first')).reset_index()
 token_counts=[];primary_counts=[];helper_counts=[]
 for _,x in unique.iterrows():
  prompt=plain(x.prompt);answer=plain(x.text)
  #50 system/wrapper tokens, shared with the early ChatGPT patient-message recipe.
  primary=len(enc.encode(prompt))+len(enc.encode(answer))+50
  helper=len(helper_enc.encode(prompt))+len(helper_enc.encode(answer))+4
  tok=primary+helper;primary_counts.append(primary);helper_counts.append(helper)
  token_counts.append(tok)
  texts.append(dict(occupation=occupation,task=task,prompt=prompt,answer=answer,grade=x.grade,tokens=tok,primary_tokens=primary,moderation_tokens=helper,answer_sha256=hashlib.sha256(answer.encode()).hexdigest()))
 results.append(dict(occupation=occupation,task=task,human_attempts=len(human),human_time=human.time_reported.mean(),human_median=human.time_reported.median(),human_page_mean=human.time_page.mean(),human_grade=human.grade.mean(),ai_attempts=len(unique),ai_grade=unique.grade.mean(),ai_grade_count=len(group),tokens=float(np.mean(token_counts)),primary_tokens=float(np.mean(primary_counts)),moderation_tokens=float(np.mean(helper_counts)),compute_flops=float(np.mean(primary_counts))*350e9+float(np.mean(helper_counts))*2.6e9))
(out/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
(out/'task-texts.json').write_text(json.dumps(texts,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(results,indent=2))

scenarios=[]
for row in results:
 selected=[x for x in texts if x['occupation']==row['occupation'] and x['task']==row['task']]
 primary=row['primary_tokens'];helper=row['moderation_tokens']
 alternate=float(np.mean([len(helper_enc.encode(x['prompt']))+len(helper_enc.encode(x['answer']))+50 for x in selected]))
 scenarios.append({'occupation':row['occupation'],'task':row['task'],'primary_parameters_flops':{str(n):primary*2*n+helper*2.6e9 for n in [7e9,44e9,175e9,350e9]},'system_wrapper_flops':{str(n):(primary-50+n)*350e9+helper*2.6e9 for n in [0,50,200]},'p50k_primary_flops':alternate*350e9+helper*2.6e9,'moderation_parameters_flops':{str(n):primary*350e9+helper*2*n for n in [0.1e9,1.3e9,6.7e9]},'moderation_scans_flops':{str(n):primary*350e9+helper*2.6e9*n for n in [1,5,20]},'human_page_mean':row['human_page_mean'],'human_self_reported_mean':row['human_time'],'human_self_reported_median':row['human_median']})
(out/'sensitivity.json').write_text(json.dumps(scenarios,indent=2)+'\n')
