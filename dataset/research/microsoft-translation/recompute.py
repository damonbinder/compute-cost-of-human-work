"""Read-only Microsoft Combo-6 reconstruction. Requires jieba, sacremoses, openpyxl.
--sources retained originals; --assumptions explicit JSON; --output NEW outside sources.
No model execution. Outputs assumed processing, source counts, examples and scenarios.
"""
import argparse,csv,hashlib,io,json,math,re,statistics,tarfile,zipfile
from pathlib import Path
from html.parser import HTMLParser
import jieba,openpyxl
from sacremoses import MosesTokenizer

class Segments(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.inside=False
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if tag=='doc':self.doc=attrs
  if tag=='seg':self.inside=True;self.text='';self.sid=attrs['id']
 def handle_data(self,data):
  if self.inside:self.text+=data
 def handle_endtag(self,tag):
  if tag=='seg':self.rows.append(dict(self.doc,segment_id=self.sid,text=self.text));self.inside=False

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mean(xs):return statistics.mean(xs)
D=1024;L=6

def encoder(s,ff):return L*(2*s*(4*D*D+2*D*ff)+4*D*s*s)
def decoder(s,t,ff,vocab,beam=8,kv_repeat=True,extra_memory=0,teacher=False):
 # Self QKV/out, cross Q/out, FFN. Cross K/V added separately.
 local=2*L*t*(6*D*D+2*D*ff)
 self_attention=4*L*D*(t*t if teacher else t*(t+1)/2)
 cross_attention=4*L*D*t*s
 cross_kv=4*L*D*D*s*(t if kv_repeat and not teacher else 1)
 extra=0
 if extra_memory:
  extra=4*L*D*D*t+4*L*D*t*extra_memory+4*L*D*D*extra_memory*(t if kv_repeat and not teacher else 1)
 return beam*(local+self_attention+cross_attention+cross_kv+extra+2*D*vocab*t)

def compute(s,e,a,scale=1,extra=None,backbeam=None,topfactor=None,kv=None,bidirections=2,candidates=72):
 s=max(1,math.ceil(s*scale));e=max(1,math.ceil(e*scale))
 n=candidates;b=8;extra=a['nbest_decode_extra'] if extra is None else extra
 f=a['top1_decode_length_factor'] if topfactor is None else topfactor
 backbeam=a['backtranslation_beam'] if backbeam is None else backbeam
 kv=a['cross_kv_each_step'] if kv is None else kv
 t=s+extra;draft=math.ceil(e*f);back=math.ceil(s*f)
 # Three SV, three ARJT, DLDN2, DLDN3, DLDN4; latter two directions share encoder.
 components={
 'sv_three':3*(encoder(s,8192)+decoder(s,t,8192,33000,kv_repeat=kv)),
 'arjt_three':3*(encoder(s,4096)+decoder(s,t,4096,33000,kv_repeat=kv)),
 'dldn2':encoder(s,4096)+decoder(s,draft,4096,33000,kv_repeat=kv)+decoder(s,t,4096,33000,kv_repeat=kv,extra_memory=e),
 'dldn3':encoder(s,4096)+decoder(s,t,4096,33000,kv_repeat=kv),
 'dldn4':encoder(s,4096)+bidirections*decoder(s,t,4096,33000,kv_repeat=kv),
 'r2l_scoring':encoder(s,4096)+decoder(s,e,4096,33000,beam=n,kv_repeat=False,teacher=True),
 'r2l_best_generation':decoder(s,draft,4096,33000,kv_repeat=kv),
 # Reuse each candidate English encoding from backtranslation for reverse likelihood.
 'e2z_scoring':n*decoder(e,s,4096,44000,beam=1,kv_repeat=False,teacher=True),
 'backtranslation':n*(encoder(e,4096)+decoder(e,back,4096,44000,beam=backbeam,kv_repeat=kv)),
 # Four-layer LSTM: first bidirectional d each; second2d->d; upper two d->d.
 'sentence_vector_encoders':88*D*D*(s+n*e+e+n*s),
 'ranker_scalar':2*n*e+((2*n)*2*D+(2*n+2)*2*D)+5*n*2
 }
 positions=3*b*t+3*b*t+b*(draft+t)+b*t+bidirections*b*t+n*e+b*draft+n*backbeam*back+n*s
 return {'flops':sum(components.values()),'components':components,'decoder_processed':positions,'source_positions':s,'target_positions':e,'nbest_steps':t,'top1_target_steps':draft,'backtranslation_steps':back}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',type=Path,required=True);p.add_argument('--assumptions',type=Path,required=True);p.add_argument('--output',type=Path,required=True);x=p.parse_args();src=x.sources.resolve();out=x.output.resolve()
 if out.exists() or out==src or src in out.parents or out==x.assumptions.resolve():p.error('output must be new, outside sources and not an input')
 a=json.loads(x.assumptions.read_text());sgm=tarfile.open(src/'wmt17-test.tgz').extractfile('test/newstest2017-zhen-src.zh.sgm').read().decode();h=Segments();h.feed(sgm);assert len(h.rows)==2001
 base=src/'released-data/Translator-HumanParityData';mt=(base/'Translations/Translator-HumanParityData-Combo-6.txt').read_text().splitlines();ht=(base/'References/Translator-HumanParityData-Reference-HT.txt').read_text().splitlines();assert len(mt)==len(ht)==2001
 tokenizer=MosesTokenizer(lang='en');jieba.setLogLevel(40);rows=[]
 for i,r in enumerate(h.rows):
  if r['origlang']!='zh':continue
  jt=[t for t in jieba.cut(r['text']) if t.strip()];et=tokenizer.tokenize(mt[i],escape=False)
  s=math.ceil(len(jt)*a['source_bpe_per_jieba_token'])+1;e=math.ceil(len(et)*a['target_bpe_per_moses_token'])+1
  rows.append(dict(source_index=i,source_segment_number=i+1,doc_id=r['docid'],source=r['text'],translation=mt[i],human_reference=ht[i],jieba_tokens=len(jt),moses_tokens=len(et),human_reference_words=len(ht[i].split()),calculation=compute(s,e,a)))
 assert len(rows)==1000
 wb=openpyxl.load_workbook(src/'weng2026-data.xlsx',read_only=True,data_only=True);records=list(wb.active.values);donors=[dict(zip(records[0],v)) for v in records[1:]];donors=[r for r in donors if r['Group']=='Experienced' and r['Condition']=='Free'];assert len(donors)==30 and len({r['SubjectID'] for r in donors})==30
 duration=mean(r['TotalDur_Ms']/1000 for r in donors);english_words=mean(r['human_reference_words'] for r in rows);human_raw=duration/201*english_words*a['human_rate_transfer_factor'];human=round(human_raw/a['human_seconds_round_to'])*a['human_seconds_round_to']
 cmean={k:mean(r['calculation']['components'][k] for r in rows) for k in rows[0]['calculation']['components']}
 scenarios={}
 for label,opts in [('kv_hoisted',{'kv':False}),('shorter_top1',{'topfactor':1.0}),('longer_top1',{'topfactor':1.75}),('bpe_minus25pct',{'scale':.75}),('bpe_plus25pct',{'scale':1.25}),('extra25',{'extra':25}),('extra100',{'extra':100}),('backtranslation_greedy',{'backbeam':1}),('binmt_one_direction',{'bidirections':1}),('half_unique_rerank_candidates',{'candidates':36})]:
  scenarios[label]=mean(compute(r['calculation']['source_positions'],r['calculation']['target_positions'],a,**opts)['flops'] for r in rows)
 result={'assumptions':a,'source_hashes':{str(f.relative_to(src)):sha(f) for f in sorted(src.rglob('*')) if f.is_file()},'assumptions_sha256':sha(x.assumptions),'rows':rows,'summary':{'source_sentences':1000,'native_chinese_docs':len({r['doc_id'] for r in rows}),'mean_jieba_tokens':mean(r['jieba_tokens'] for r in rows),'mean_moses_tokens':mean(r['moses_tokens'] for r in rows),'mean_source_positions':mean(r['calculation']['source_positions'] for r in rows),'mean_target_positions':mean(r['calculation']['target_positions'] for r in rows),'mean_decoder_processed':mean(r['calculation']['decoder_processed'] for r in rows),'mean_flops':sum(cmean.values()),'components':cmean,'scenarios_flops':scenarios,'human_donor_attempts':30,'human_donor_ids':[r['SubjectID'] for r in donors],'human_donor_mean_seconds':duration,'human_reference_mean_words':english_words,'human_unrounded_seconds':human_raw,'human_seconds':human,'human_seconds_scenarios':[human*z for z in a['human_duration_scenario_multipliers']]}}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result['summary'],indent=2))
if __name__=='__main__':main()
