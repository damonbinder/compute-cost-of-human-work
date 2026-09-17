#!/usr/bin/env python3
"""Reconstruct released WMT NLLB outputs; no model generation. Requires sentencepiece."""
import argparse,csv,json,pathlib,hashlib,collections,statistics,math
import sentencepiece as spm
p=argparse.ArgumentParser();p.add_argument('--sources',type=pathlib.Path,required=True);p.add_argument('--divemt-sources',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();s=a.sources.resolve();ds=a.divemt_sources.resolve();out=a.output.resolve()
assert not out.exists() and s not in out.parents and ds not in out.parents,'New output outside source directories required'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for q in json.loads((s/'manifest.json').read_text()):assert sha(s/q['file'])==q['sha256'],q
shared=json.loads((s/'divemt-manifest.json').read_text());assert sha(ds/'main.tsv')==shared['sha256']
rows=list(csv.DictReader((s/'chat-submissions-nl.csv').open()));groups=collections.defaultdict(list)
for x in rows:groups[x['doc_id']].append(x)
ratings=list(csv.DictReader((s/'chat-human-nl.csv').open()));dedup={x['model_app']:x for x in ratings};selected=[]
for x in dedup.values():
 if x['model']!='submission_baseline' or x['is_doc']!='False':continue
 y=groups[x['doc_id']][int(x['sent_id'])]
 if y['source_language']=='en':
  assert y['target_language']=='nl'
  selected.append({'doc_id':x['doc_id'],'sent_id':int(x['sent_id']),'source':y['source'],'reference':y['reference'],'output':y['submission_baseline'],'score':float(x['score'])})
assert len(selected)==389 and len({(x['doc_id'],x['sent_id']) for x in selected})==389
sp=spm.SentencePieceProcessor(model_file=str(s/'sentencepiece.bpe.model'));cfg=json.loads((s/'model-config.json').read_text());d=cfg['d_model'];f=cfg['encoder_ffn_dim'];L=cfg['encoder_layers'];V=cfg['vocab_size'];B=4
assert (d,f,L,V)==(2048,8192,24,256206)
def ops(S,T,B=4):
 # encoder once. Decoder self QKV/out + cross Q/out + FF each step;
 # cross K/V cached after first projection per beam. Full output vocabulary.
 return {'encoder':L*(8*S*d*d+4*S*d*f+4*S*S*d),'cross_kv':L*B*4*S*d*d,'decoder_linear':L*B*T*(12*d*d+4*d*f),'decoder_self_attention':L*B*4*d*T*(T+1)/2,'decoder_cross_attention':L*B*T*4*S*d,'output_head':B*T*2*d*V}
for x in selected:
 x['source_words']=len(x['source'].split());x['source_positions']=len(sp.encode(x['source']))+2
 # start EOS is a processed position generating forced language; then target pieces and EOS.
 x['winning_steps']=len(sp.encode(x['output']))+2
 x['components']=ops(x['source_positions'],x['winning_steps']);x['flops']=sum(x['components'].values())
mean=lambda key:statistics.mean(x[key] for x in selected)
data=list(csv.DictReader((ds/'main.tsv').open(),delimiter='\t'));excluded={x['item_id'] for x in data if float(x['time_s'])>=2700};h=[x for x in data if x['lang_id']=='nld' and x['task_type']=='ht' and x['item_id'] not in excluded];assert len(h)==413
X=[len(x['src_text'].split()) for x in h];Y=[float(x['time_s']) for x in h];xm=statistics.mean(X);ym=statistics.mean(Y);slope=sum((x-xm)*(y-ym) for x,y in zip(X,Y))/sum((x-xm)**2 for x in X);intercept=ym-slope*xm
res={'selected':selected,'n':len(selected),'documents':len({x['doc_id'] for x in selected}),'quality_mean':mean('score'),'quality_histogram':dict(collections.Counter(x['score'] for x in selected)),'source_words':mean('source_words'),'source_positions':mean('source_positions'),'winning_steps':mean('winning_steps'),'max_winning_steps':max(x['winning_steps'] for x in selected),'decoder_processed_tokens':B*mean('winning_steps'),'compute_flops':mean('flops'),'components_mean':{k:statistics.mean(x['components'][k] for x in selected) for k in selected[0]['components']},'scenarios':{},'human':{'donor_n':len(h),'donor_people':len({x['subject_id'] for x in h}),'excluded_items':sorted(excluded),'source_words_mean':xm,'time_seconds_mean':ym,'ols_intercept':intercept,'ols_slope':slope,'ols_target':intercept+slope*mean('source_words'),'ratio_target':ym/xm*mean('source_words'),'chosen_estimated_seconds':60,'scenario_seconds':[30,65.36935840656422,90],'short_examples':[{'source':x['src_text'],'seconds':float(x['time_s'])} for x in h if len(x['src_text'].split())<=10]},'parameter_counts':{'encoder_including_shared_embedding':V*d+L*(4*d*d+2*d*f+9*d+f)+2*d,'decoder_excluding_shared_embedding':L*(8*d*d+2*d*f+15*d+f)+2*d},'source_manifest_sha256':sha(s/'manifest.json'),'shared_manifest_sha256':sha(s/'divemt-manifest.json')}
assert 4*(sum(res['parameter_counts'].values())+3*V*d)==json.loads((s/'weight-index.json').read_text())['metadata']['total_size'], 'Original stored alias count disagrees'
for name,fn in [('beam_steps_25pct_longer',lambda x:(x['source_positions'],math.ceil(1.25*x['winning_steps']))),('beam_steps_50pct_longer',lambda x:(x['source_positions'],math.ceil(1.5*x['winning_steps']))),('configured_199_steps',lambda x:(x['source_positions'],max(199,x['winning_steps']))),('encoder_padding_to_longest_selected',lambda x:(max(y['source_positions'] for y in selected),x['winning_steps']))]:res['scenarios'][name]=statistics.mean(sum(ops(*fn(x)).values()) for x in selected)
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({k:v for k,v in res.items() if k not in ['selected','human']},indent=2));print('human',res['human']['ols_target'])
