#!/usr/bin/env python3
"""Original QuickDraw stroke-clock audit. Standard library, no model execution."""
import argparse,json,hashlib,statistics,xml.etree.ElementTree as ET
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=a.sources.resolve();out=a.output.resolve()
if out.exists() or out.is_relative_to(s):p.error('Output must be new and outside sources.')
for entry in json.loads((s/'raw-source-manifest.json').read_text()):
 f=(s/entry['file']).resolve();assert f.is_relative_to(s);b=f.read_bytes();assert len(b)==entry['bytes'] and hashlib.sha256(b).hexdigest()==entry['sha256'];assert b.endswith(b'\n') and len(b.splitlines())==100
cats=(s/'quickdraw-categories.txt').read_text().splitlines();selected=sorted(cats,key=lambda x:hashlib.sha256(('sketchagent-human-duration-v1:'+x).encode()).hexdigest())[:20]
assert selected==json.loads((s/'selected-timing-categories.json').read_text())
def getrows(folder):
 rows=[]
 for f in sorted((s/folder).glob('*.ndjson')):
  raw=f.read_text().splitlines();assert len(raw)==100
  for line in raw:
   r=json.loads(line);st=r['drawing'];assert all(len(x)==3 and len(x[0])==len(x[1])==len(x[2]) for x in st)
   tt=[v for x in st for v in x[2]];assert tt
   rows.append({'category':f.stem,'key_id':r['key_id'],'recognized':r['recognized'],'country':r['countrycode'],'stroke_envelope_seconds':(max(tt)-min(tt))/1000,'pen_down_seconds':sum((max(x[2])-min(x[2]))/1000 for x in st),'strokes':len(st),'start_t':min(tt)})
 return rows
rows=getrows('quickdraw-broad');assert len(rows)==2000 and len({r['key_id'] for r in rows})==2000
assert {r['category'] for r in rows}==set(selected)
def summarize(rr):
 return {'n':len(rr),'mean_envelope_seconds':statistics.mean(x['stroke_envelope_seconds'] for x in rr),'median_envelope_seconds':statistics.median(x['stroke_envelope_seconds'] for x in rr),'mean_pen_down_seconds':statistics.mean(x['pen_down_seconds'] for x in rr),'mean_strokes':statistics.mean(x['strokes'] for x in rr),'recognized':sum(x['recognized'] for x in rr),'over20seconds':sum(x['stroke_envelope_seconds']>20 for x in rr),'maximum_seconds':max(x['stroke_envelope_seconds'] for x in rr)}
summary=summarize(rows);gallery=getrows('quickdraw-prefix')
website_git={x['path']:x for x in json.loads((s/'website-tree.json').read_text())['tree']}
svgs=[]
for f in sorted((s/'website-assets').rglob('*.svg')):
 b=f.read_bytes();rel=str(f.relative_to(s/'website-assets'));assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==website_git[rel]['sha']
 root=ET.parse(f).getroot();paths=[x for x in root.iter() if x.tag.endswith('}path') or x.tag=='path'];svgs.append({'file':str(f.relative_to(s)),'path_count':len(paths),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
r={'sampling':'20categories smallest SHA256(sketchagent-human-duration-v1:category), first100releasedrawrecords each; not exact paper cohort','summary':summary,'mean_plus2seconds_initial_planning':summary['mean_envelope_seconds']+2,'mean_plus5seconds_initial_planning':summary['mean_envelope_seconds']+5,'per_category':{cat:summarize([x for x in rows if x['category']==cat]) for cat in selected},'gallery_category_summaries':{cat:summarize([x for x in gallery if x['category']==cat]) for cat in sorted({x['category'] for x in gallery})},'rows':rows,'svg_assets':svgs,'raw_sha256':{str(f.relative_to(s)):hashlib.sha256(f.read_bytes()).hexdigest() for folder in ['quickdraw-broad','quickdraw-prefix'] for f in sorted((s/folder).glob('*.ndjson'))}}
out.write_text(json.dumps(r,indent=2)+'\n');print(summary)
