#!/usr/bin/env python3
"""Rebuild the 290-page analytic workload; Python 3, tiktoken and Pillow required."""
import argparse, ast, collections, hashlib, html, json, math, os, re, shutil
from pathlib import Path
from html.parser import HTMLParser

SEED='omnidocbench-gpt4o-pilot-2026-09-12'
ENCODING_URL='https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken'
class Cells(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.cells=[];self.current=None
    def handle_starttag(self,tag,attrs):
        if tag in ('td','th'):
            if self.current is not None:self.cells.append(''.join(self.current))
            self.current=[]
        elif tag=='br' and self.current is not None:self.current.append(' ')
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.current is not None:
            self.cells.append(''.join(self.current));self.current=None
    def handle_data(self,s):
        if self.current is not None:self.current.append(s)

def text_and_math(s):
    # Count actual annotation strings. Do not flatten math into plaintext keystrokes.
    matches=list(re.finditer(r'(?<!\\)\$(?!\$)(.*?)(?<!\\)\$',s,re.S))
    return len(re.sub(r'(?<!\\)\$(?!\$)(.*?)(?<!\\)\$','',s,flags=re.S)),sum(len(m.group(1)) for m in matches),len(matches)

def human(q,scenario):
    p={
      'central':dict(wpm=51.56,proof_cps=12.5,math_cps=1.5,math_start=5,math_check_fraction=.25,math_check_start=4,cell_enter=2,cell_check=2,table_setup=60,orient=30,block=2),
      'faster':dict(wpm=78,proof_cps=20,math_cps=3,math_start=3,math_check_fraction=.15,math_check_start=2,cell_enter=1,cell_check=1,table_setup=30,orient=15,block=1),
      'slower':dict(wpm=26,proof_cps=7,math_cps=.75,math_start=8,math_check_fraction=.4,math_check_start=6,cell_enter=4,cell_check=4,table_setup=120,orient=60,block=4)
    }[scenario]
    t={
      'plain_entry':q['plain_chars']/(p['wpm']*5/60),
      'plain_check':q['plain_chars']/p['proof_cps'],
      'table_entry':q['table_plain_chars']/(p['wpm']*5/60)+q['table_cells']*p['cell_enter'],
      'table_check':q['table_cells']*p['cell_check'],
      'table_structure':q['tables']*p['table_setup'],
      'formula_entry':q['formula_chars']/p['math_cps']+q['formulas']*p['math_start'],
      'formula_check':q['formula_chars']/p['math_cps']*p['math_check_fraction']+q['formulas']*p['math_check_start'],
      'orientation_structure':p['orient']+q['output_blocks']*p['block']}
    return {'seconds':sum(t.values()),'components':t,'assumptions':p}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('source_dir',type=Path);ap.add_argument('output_dir',type=Path);a=ap.parse_args()
    src=a.source_dir.resolve();out=a.output_dir.resolve()
    if out.exists() or out==src or src in out.parents:raise SystemExit('Output must be new and outside source directory')
    if (src/'manifest.json').exists():
        for entry in json.loads((src/'manifest.json').read_text()):
            assert hashlib.sha256((src/entry['path']).read_bytes()).hexdigest()==entry['sha256'], entry['path']
    out.mkdir(parents=True)
    cache=out/'tokenizer-cache';cache.mkdir();shutil.copyfile(src/'o200k_base.tiktoken',cache/hashlib.sha1(ENCODING_URL.encode()).hexdigest());os.environ['TIKTOKEN_CACHE_DIR']=str(cache)
    import tiktoken
    from PIL import Image
    enc=tiktoken.get_encoding('o200k_base')
    tree=ast.parse((src/'gpt_4o_inf.py').read_text())
    prompt=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PROMPT' for t in n.targets))
    prompt_tokens=len(enc.encode(prompt))+12 # explicit unknown message/special-token allowance
    pages=json.loads((src/'annotations-v1.json').read_text())
    en=[p for p in pages if p['page_info']['page_attribute']['language']=='english']
    assert len(pages)==981 and len(en)==290
    selected=sorted(en,key=lambda p:hashlib.sha256((SEED+'|'+p['page_info']['image_path']).encode()).hexdigest())[:10]
    names=[p['page_info']['image_path'] for p in selected]
    for p in selected:
        info=p['page_info']
        with Image.open(src/'images'/info['image_path']) as im:assert im.size==(info['width'],info['height'])
    cfg=json.loads((src/'clip-bigG.json').read_text())['vision_cfg']
    d=cfg['width'];m=int(d*cfg['mlp_ratio']);L=cfg['layers'];patch=cfg['patch_size'];n=(cfg['image_size']//patch)**2+1
    front=2*(n-1)*(patch*patch*3)*d+L*(8*n*d*d+4*n*d*m+4*n*n*d)
    rows=[];(out/'output-proxies').mkdir()
    for page in sorted(en,key=lambda p:p['page_info']['image_path']):
        q=collections.Counter();blocks=[]
        for b in sorted(page['layout_dets'],key=lambda b:(b.get('order') is None,b.get('order') or 0,b['anno_id'])):
            typ=b['category_type']
            if typ=='table':
                s=b.get('html','');parser=Cells();parser.feed(s);parser.close()
                if parser.current is not None:parser.cells.append(''.join(parser.current))
                q['tables']+=1;q['table_cells']+=len(parser.cells)
                for cell in parser.cells:
                    plain,mathchars,mcount=text_and_math(cell);q['table_plain_chars']+=plain;q['formula_chars']+=mathchars;q['formulas']+=mcount
            elif typ=='equation_isolated':
                s=b.get('latex','');q['formula_chars']+=len(s.strip('$\n '));q['formulas']+=1
            elif b.get('text'):
                s=b['text'];plain,mathchars,mcount=text_and_math(s);q['plain_chars']+=plain;q['formula_chars']+=mathchars;q['formulas']+=mcount
                if typ=='title':s='# '+s.strip('#').strip()
            else:
                q['untranscribed_'+typ]+=1;continue
            if s:blocks.append(s);q['output_blocks']+=1
        # Original block contents: HTML tables, text (including headers), display LaTeX.
        # Figure pixels and untranscribed masks/abandon boxes are not invented.
        md='\n\n'.join(blocks)+'\n';name=page['page_info']['image_path'];(out/'output-proxies'/(name+'.md')).write_text(md)
        ot=len(enc.encode(md));w=page['page_info']['width'];h=page['page_info']['height']
        scale=min(1,2048/max(w,h));ws=w*scale;hs=h*scale
        scale2=min(1,768/min(ws,hs));ws=math.floor(ws*scale2+1e-9);hs=math.floor(hs*scale2+1e-9)
        tiles=math.ceil(ws/512)*math.ceil(hs/512);crops=tiles+1;visual=(n-1)*crops
        texttokens=prompt_tokens+ot
        f=1e11*(texttokens+visual)+front*crops
        quantities={k:q[k] for k in ['plain_chars','table_plain_chars','table_cells','tables','formula_chars','formulas','output_blocks']}
        rows.append(dict(image_path=name,page_attributes=page['page_info']['page_attribute'],width=w,height=h,high_detail_dimensions=[ws,hs],crops=crops,tiles=tiles,visual_positions=visual,billing_units_reference=85+170*tiles,output_proxy_tokens=ot,text_tokens=texttokens,compute_flops=f,frontend_flops=front*crops,quantities=quantities,untranscribed={k:v for k,v in q.items() if k.startswith('untranscribed_')},human={s:human(q,s) for s in ['central','faster','slower']}))
    mean=lambda k:sum(r[k] for r in rows)/len(rows)
    hmean={s:sum(r['human'][s]['seconds'] for r in rows)/len(rows) for s in ['central','faster','slower']}
    comp={k:sum(r['human']['central']['components'][k] for r in rows)/len(rows) for k in rows[0]['human']['central']['components']}
    qmean={k:sum(r['quantities'][k] for r in rows)/len(rows) for k in rows[0]['quantities']}
    fmean=mean('compute_flops');tokmean=mean('text_tokens');vmean=mean('visual_positions');fvis=mean('frontend_flops')
    scenarios={
      'active_parameters_25B':.5e11*(tokmean+vmean)+fvis,
      'active_parameters_100B':2e11*(tokmean+vmean)+fvis,
      'pooled_64_visual_positions_per_crop':1e11*(tokmean+64*mean('crops'))+fvis,
      'native_336px_576patch_encoder_per_crop':None,
      'output_length_75percent_of_gt':1e11*(prompt_tokens+.75*mean('output_proxy_tokens')+vmean)+fvis,
      'output_length_150percent_of_gt':1e11*(prompt_tokens+1.5*mean('output_proxy_tokens')+vmean)+fvis,
      'overview_only':1e11*(tokmean+256)+front,
      'maximum_reuse_of_common_text_prompt':fmean-1e11*prompt_tokens,
      'doubled_frontend_matrix_cost':fmean+fvis,
    }
    n336=577;front336=2*576*(patch*patch*3)*d+L*(8*n336*d*d+4*n336*d*m+4*n336*n336*d)
    scenarios['native_336px_576patch_encoder_per_crop']=1e11*(tokmean+576*mean('crops'))+front336*mean('crops')
    result=dict(source_page_count=len(pages),english_page_count=len(en),selection_seed=SEED,inspection_pages=names,prompt_tokens_literal=len(enc.encode(prompt)),prompt_wrapper_assumption=12,prompt_has_formfeed='\f' in prompt,vision_proxy=dict(layers=L,width=d,mlp_width=m,positions_per_crop=n,patch_positions_per_crop=n-1,flops_per_crop=front),mean={k:mean(k) for k in ['text_tokens','output_proxy_tokens','crops','visual_positions','billing_units_reference','compute_flops','frontend_flops']},mean_quantities=qmean,human_seconds=hmean,human_central_components=comp,compute_scenarios=scenarios,pages=rows)
    (out/'calculations.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['pages','inspection_pages']},indent=2))
if __name__=='__main__':main()
