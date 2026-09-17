"""Original WordPiece + SQuAD window workload. Usage: python recompute.py SOURCE_DIR OUTPUT_DIR.
TensorFlow's file-opening interface is replaced by Python open; tokenizer logic is unchanged.
"""
import argparse,sys,types,importlib.util,json,csv,re,string,collections
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('source_dir',type=Path);ap.add_argument('output_dir',type=Path);a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
sys.modules['tensorflow']=types.SimpleNamespace(gfile=types.SimpleNamespace(GFile=open,Open=open))
spec=importlib.util.spec_from_file_location('original_tokenization',a.source_dir/'tokenization.py');tokmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(tokmod)
tok=tokmod.FullTokenizer(str(a.source_dir/'vocab.txt'),do_lower_case=True)
def normalize(s):
 return ' '.join(re.sub(r'\b(a|an|the)\b',' ',''.join(c for c in s.lower()if c not in string.punctuation)).split())
def f1(pred,ans):
 p=normalize(pred).split();g=normalize(ans).split();n=sum((collections.Counter(p)&collections.Counter(g)).values());return 2*n/(len(p)+len(g))if n else 0
rows=[]
for article in json.loads((a.source_dir/'dev-v1.1.json').read_text())['data']:
 for para in article['paragraphs']:
  # Exact whitespace predicate in original read_squad_examples; tokenize each word separately.
  words=[];prev=True
  for c in para['context']:
   if c in ' \t\r\n' or ord(c)==0x202f:prev=True
   else:
    if prev:words.append(c)
    else:words[-1]+=c
    prev=False
  doc=[t for w in words for t in tok.tokenize(w)]
  for qa in para['qas']:
   query=tok.tokenize(qa['question'])[:64];limit=384-len(query)-3;start=0;windows=[]
   while start<len(doc):
    length=min(len(doc)-start,limit);windows.append(length+len(query)+3)
    if start+length==len(doc):break
    start+=min(length,128)
   ans=[x['text']for x in qa['answers']];human=ans[1] if len(ans)>1 else None;refs=ans[:1]+ans[2:]
   rows.append(dict(id=qa['id'],query_wordpieces=len(query),context_wordpieces=len(doc),windows=len(windows),processed_positions=len(windows)*384,unpadded_positions=sum(windows),human_f1=max(f1(human,g)for g in refs) if human is not None else None,human_em=max(normalize(human)==normalize(g)for g in refs) if human is not None else None))
with(a.output_dir/'question-counts.csv').open('w',newline='')as o:
 w=csv.DictWriter(o,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
n=len(rows);windows=sum(r['windows']for r in rows)
result={'questions':n,'questions_with_second_answer':sum(r['human_f1'] is not None for r in rows),'windows':windows,'mean_windows':windows/n,'mean_padded_positions':windows*384/n,'mean_unpadded_positions':sum(r['unpadded_positions']for r in rows)/n,'human_second_answer_F1':100*sum(r['human_f1']for r in rows if r['human_f1'] is not None)/sum(r['human_f1'] is not None for r in rows),'human_second_answer_EM':100*sum(r['human_em']for r in rows if r['human_em'] is not None)/sum(r['human_em'] is not None for r in rows),'models':{}}
for name,L,d in [('base',12,768),('large',24,1024),('large_ensemble7',24,1024)]:
 S=384;m=7 if name.endswith('7')else 1
 # 4 attention projections, 2 FFN maps (f=4d), two attention matrix multiplies.
 encoder=L*(24*S*d*d+4*S*S*d);span=4*S*d
 # Original BertModel constructs pooler even though QA fetches sequence output; pruned unused pooler excluded.
 result['models'][name]={'layers':L,'hidden':d,'members':m,'flops_per_window_per_member':encoder+span,'mean_flops':(encoder+span)*windows/n*m,'mean_processed_positions':windows*384/n*m}
(a.output_dir/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
