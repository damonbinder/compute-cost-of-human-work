#!/usr/bin/env python3
"""Build candidate CSVs. Python3 standard library; no network or external execution.
Usage: python3 build_candidates.py --source benchmark.csv --models dataset/models.csv --points-schema dataset/points.csv --output-dir OUT
Reads native telemetry and fixed reviewed human estimates; writes new CSVs only.
"""
import argparse,csv,math,pathlib,json
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--models',required=True);p.add_argument('--points-schema',required=True);p.add_argument('--output-dir',required=True);a=p.parse_args()
def read(f):
 with open(f,newline='') as h:
  r=csv.DictReader(h);return r.fieldnames,list(r)
def write(f,fields,rows):
 with open(f,'w',newline='') as h:
  w=csv.DictWriter(h,fields);w.writeheader();w.writerows(rows)
fields,_=read(a.points_schema);mf,models=read(a.models);models={m['model_id']:m for m in models};_,raw=read(a.source)
out=pathlib.Path(a.output_dir);out.mkdir(parents=True,exist_ok=True);(out/'research').mkdir(exist_ok=True)
# Minutes: layout/helpers, cabin construction, surroundings/props, materials/lighting/camera, QA/export.
work={
'gpt-5.5-xhigh':([45,75,60,45,45],'Detailed log cabin, shingles, masonry chimney and porch; sparse surroundings and oversized cabin.'),
'gpt-5.6-luna-light':([15,25,20,15,15],'Simple boxy cabin and sparse primitive trees; no visible chimney in the author’s render audit and an inaccurate roof silhouette.'),
'gpt-5.6-luna-high':([30,45,45,35,25],'Compact coherent cabin, shingles, rocks, mountains and water; limited path and scene coverage.'),
'gpt-5.6-luna-extra-high':([30,55,65,35,25],'Complete prop set and forest on simple terrain; oversized roof and underexposed narrow composition.'),
'gpt-5.6-terra-high':([25,40,35,25,25],'Compact cabin, custom faceted ground, path and props; sparse background and tree occlusion.'),
'gpt-5.6-terra-extra-high':([35,60,80,40,25],'Rich terrain, forest and props; crossed braces and a protruding beam remain.'),
'gpt-5.6-terra-ultra':([35,65,65,45,30],'Clean cabin shell and roof, height-field terrain and vegetation; cabin base visibly floats.'),
'gpt-5.6-sol-light':([25,50,50,30,25],'Coherent cabin, porch, chimney, path and props with simple lighting and coarse materials.'),
'gpt-5.6-sol-extra-high':([40,70,75,50,35],'Coherent steep roof, custom terrain, mountains, path and nearly complete props; repeated trees and shallow atmosphere.'),
'gpt-5.6-sol-ultra':([50,90,100,75,45],'Coherent detailed cabin, shingles, chimney, terrain, water, layered mountains, varied vegetation and placed props; refined lighting and haze.')}
reasons={
'gpt-5.6-luna-medium':'The source audit identifies a detached roof and failed primary cabin silhouette.',
'gpt-5.6-terra-light':'Severe stacked roof slabs and floating ridge dominate the scene; core cabin geometry fails.',
'gpt-5.6-terra-medium':'Foreground tree hides the main cabin and shadows obscure it; useful completion is not established.',
'gpt-5.6-sol-medium':'Roof panels, beams and planes visibly separate; source identifies failure of the principal assembly.',
'gpt-5.6-sol-high':'Exploded floating roof is a core modelling failure despite attractive surroundings.'}
notes=['# Pixels to Polygons calculations','', '| point_id | processed decoder positions | cache reads | context | FLOPs | human hours | list-price USD |','|---|---:|---:|---:|---:|---:|---:|']
rows=[];details=[];image_scenarios=[]
for r in raw:
 if r['run'] not in work:continue
 mid=r['model'].replace('.','-');m=models[mid];N=float(m['active_parameters']);L=float(m['attention_layers']);D=float(m['attention_width'])
 I=int(r['input_tokens']);C=int(r['cached_input_tokens']);O=int(r['output_tokens']);native=I-C+O
 ultra=r['effort']=='ultra'
 checks=math.ceil(int(r['tool_calls'])/10) if ultra else 1
 w,h=map(int,r['render_dimensions'].split('x'))
 refpatch=math.ceil(1672/32)*math.ceil(941/32)
 renderpatch=math.ceil(w/32)*math.ceil(h/32)
 imagepatch=refpatch+checks*renderpatch
 imagebilled=math.ceil(refpatch*1.2)+checks*math.ceil(renderpatch*1.2)
 texttokens=native-imagebilled;P=texttokens+imagepatch
 Q=min(C/P*2800,P/2,200000)
 def shape(n):
  d=max(8,round((n/196608)**(1/3)));return max(1,round(d*.65)),128*d
 def calc(n,k):
  l,d=shape(n);q=min(C/P*k,P/2,200000);return 2*n*P+4*l*d*q*P
 F=2*N*P+4*L*D*Q*P;lo=calc(float(m['active_parameters_low']),1976);hi=calc(float(m['active_parameters_high']),19088)
 mins,scope=work[r['run']];h=sum(mins)/60
 pid='media-blender-cabin-'+r['run'].replace('.','-').replace('extra-high','xhigh').replace('light','low')
 locator='research/blender-bench.md#'+pid
 ultra=r['effort']=='ultra'
 rate={'gpt-5-5':(5,.5,30),'gpt-5-6-luna':(1,.1,6),'gpt-5-6-terra':(2.5,.25,15),'gpt-5-6-sol':(5,.5,30)}[mid]
 cost=((I-C)*rate[0]+C*rate[1]+O*rate[2])/1e6
 note=f'Assumed one reference image plus {checks} render inspections; image positions counted separately from text. Vision encoder work remains unpriced.'
 if ultra:note+=' Child usage is included; unidentified helper models use the primary-model coefficient.'
 else:note+=' Dollar figure is standard API list-price equivalent, not subscription spending; unreported cache writes and long-context premiums are excluded.'
 row={f:'' for f in fields};row.update(point_id=pid,task='Create a low-poly cabin scene ('+r['model']+' '+r['effort']+')',task_category='writing_media',task_description='From one cabin-and-forest reference image, autonomously produce one editable Blender scene, procedural Python builder and final still render. Match the delivered scene, not exact reconstruction of the reference. '+scope,model_id=mid,compute_scope='inference',compute_flops=f'{F:.12g}',compute_flops_low=f'{lo:.12g}',compute_flops_high=f'{hi:.12g}',human_skill='expert',human_time_scope='task_performance',human_time=str(sum(mins)*60),performance_vs_human='match',comparison_issues='none_identified',compute_evidence='derived_assumed_inputs',human_time_evidence='llm_estimate_judgment',performance_evidence='One autonomous run delivered an editable scene, builder and nonblank render. Human baseline assumes a Blender artist competent in procedural scripting produces an equivalent scene and builder at the delivered quality.',human_time_statistic='point_estimate',human_time_subset='not_applicable',human_attempts='not_applicable',human_time_source=locator,compute_method='operation_count',compute_statistic='total',compute_subset='all',ai_attempts='1',compute_source=locator,tokens=str(texttokens),tokens_accounting='input_cache_creation_output',source_dataset='Pixels to Polygons (2026)',source_record='https://github.com/ralfboltshauser/gpt-5-6-blender-benchmark/tree/b56cfa88c469cce6f7e62191d16c2e4f89527edc/'+r['run']+'; performance: source per-run audit in site/app.js; configuration '+r['effort'],notes=note,ai_cost_usd='' if ultra else f'{cost:.8g}',ai_cost_basis='not_available' if ultra else 'list_price',ai_cost_date='' if ultra else '2026-07-10',human_cost_basis='not_available',attention_context=f'{Q:.12g}',attention_ratio=f'{2*L*D*Q/N:.12g}')
 def image_case(render_checks):
  pos=native-(math.ceil(refpatch*1.2)-refpatch)-render_checks*(math.ceil(renderpatch*1.2)-renderpatch)
  return pos*(2*N+4*L*D*min(C/pos*2800,pos/2,200000))
 image_scenarios.append({'point_id':pid,'native_units_as_positions_flops':native*(2*N+4*L*D*min(C/native*2800,native/2,200000)), 'reference_only_flops':image_case(0),'one_render_per_tool_call_flops':image_case(int(r['tool_calls'])),'central_flops':F,'assumed_render_inspections':checks,'image_patch_positions':imagepatch,'billable_image_units':imagebilled,'text_tokens':texttokens})
 rows.append(row);notes.append(f'| {pid} | {P} | {C} | {Q:.1f} | {F:.6g} | {h:g} | {row["ai_cost_usd"]} |')
 details.append(f'\n## {pid}\n\nSource run `{r["run"]}`; reported input {I}, cache reads {C}, output {O}, reasoning subset {r["reasoning_output_tokens"]}; native total {r["total_tokens"]}. AI elapsed time {int(r["duration_ms"])/1000:g} seconds is not human time.\n\nWork: {scope}\n\nHuman estimate: {sum(mins)} minutes ({h:g} hours): layout and geometry helpers {mins[0]}; cabin {mins[1]}; surroundings and props {mins[2]}; materials, lighting and camera {mins[3]}; testing, corrections and export {mins[4]}. These are judgment allocations, not observed stage timings. Half to twice this total is a useful human-time sensitivity scenario, not a measured interval.\n\nNative uncached input plus output = {native}; assumed image billable units {imagebilled}, image patch positions {imagepatch}. Text tokens = {native} - {imagebilled} = {texttokens}; processed workload P = {texttokens} + {imagepatch} = {P}; context = min({C}/{P} * 2800, {P}/2, 200000) = {Q:g}. Registry N={N:g}, L={L:g}, width={D:g}; F={F:g}, range [{lo:g}, {hi:g}].\n')
assert len({r['point_id'] for r in rows})==len(rows)
write(out/'points.csv',fields,rows);write(out/'models.csv',mf,[])
write(out/'dispositions.csv',['source_run','disposition','reason'],[{'source_run':r['run'],'disposition':'candidate' if r['run'] in work else 'withheld','reason':'Matched-quality reproduction estimate; independent review required.' if r['run'] in work else reasons[r['run']]} for r in raw])
(out/'research'/'image-scenarios.json').write_text(json.dumps(image_scenarios,indent=2))
(out/'research'/'calculations.md').write_text('\n'.join(notes+details))
print(f'{len(rows)} candidate rows, {len(raw)-len(rows)} withheld, {len(fields)} columns; no new models')
