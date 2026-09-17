"""Read-only duplicate-family audit; explicit shared source path, no source edits."""
import argparse,csv,json,hashlib,statistics
from pathlib import Path
from collections import Counter

def main():
 p=argparse.ArgumentParser();p.add_argument('--shared-sources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=a.shared_sources.resolve();o=a.output.resolve()
 if o.exists() or o==s or s in o.parents:p.error('new output outside source evidence required')
 d=s/'repo/eval/benchmark_eval/benchmarks/MMLUArabic/test';data={p.stem.removesuffix('_test'):list(csv.reader(p.open())) for p in d.glob('*.csv')};m=json.loads((s/'metrics-1.json').read_text());weights={}
 for domain in m.values():
  for group in domain.values():
   subjects=[k for k in group if k not in ['average','overall']]
   for k in subjects:weights[k]=1/len(m)/len(domain)/len(subjects)
 # Five 'IP' substring hits are unrelated: leadership, MISSISSIPPI and3actual networking questions.
 exclusions={('professional_psychology',425),('college_computer_science',22),('college_computer_science',62),('college_computer_science',82),('high_school_mathematics',81)}
 family={(k,i) for k,rows in data.items() for i,r in enumerate(rows) if 'IP' in r[0] and (k,i) not in exclusions}
 totals={'questions':sum(map(len,data.values())),'ip_substring_hits':len(family)+len(exclusions),'repeated_family_items':len(family),'subjects':len({k for k,i in family}),'paper_score_weight':sum(weights[k]/len(data[k]) for k,i in family),'answer_labels':dict(Counter(data[k][i][-1] for k,i in family))}
 root=s/'repo/eval_results/Arabic MMLU';subjects=[];weighted={k:0. for k in ['weight','before_all','after_all','before_family','after_family','family_weight']}
 for file in sorted((root/'AceGPT_7B_base/few_shot').glob('*.jsonl')):
  name=file.stem;n=data[name];new=[json.loads(x) for x in file.read_text().splitlines()];old=[json.loads(x) for x in (root/'llama-2-7b-hf/few_shot'/file.name).read_text().splitlines()];assert len(new)==len(old)==len(n)
  row={'subject':name,'n':len(n),'family_n':0,'before_correct':0,'after_correct':0,'before_family_correct':0,'after_family_correct':0}
  for x,y in zip(new,old):
   i=x['query_id'];assert i==y['query_id'] and x['query']==y['query'] and x['answer']==y['answer']==n[i][-1]
   expected='سؤال: '+n[i][0]+'\n'+'\n'.join(f'{z}. '+n[i][j] for j,z in enumerate('ABCD',1));assert expected==x['query']
   be=x['answer']==y['response_answer'];af=x['answer']==x['response_answer'];row['before_correct']+=be;row['after_correct']+=af
   if (name,i) in family:row['family_n']+=1;row['before_family_correct']+=be;row['after_family_correct']+=af
  w=weights[name];weighted['weight']+=w;weighted['before_all']+=w*row['before_correct']/len(n);weighted['after_all']+=w*row['after_correct']/len(n);weighted['before_family']+=w*row['before_family_correct']/len(n);weighted['after_family']+=w*row['after_family_correct']/len(n);weighted['family_weight']+=w*row['family_n']/len(n);subjects.append(row)
 totals['raw_sample_totals']={k:sum(x[k] for x in subjects) for k in subjects[0] if k!='subject'};totals['raw_subset_weighted_contributions']=weighted
 examples=[{'subject':k,'index':i,'row':data[k][i]} for k,i in sorted(family) if k=='professional_law'][:8]
 r={'summary':totals,'paired_subjects':subjects,'family_locators':[list(x) for x in sorted(family)],'excluded_legitimate_ip_substrings':[list(x) for x in sorted(exclusions)],'examples':examples,'source_hashes':{str(x.relative_to(s)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(d.glob('*.csv'))}}
 o.parent.mkdir(parents=True,exist_ok=True);o.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(totals,indent=2));print(json.dumps(subjects,indent=2))
if __name__=='__main__':main()
