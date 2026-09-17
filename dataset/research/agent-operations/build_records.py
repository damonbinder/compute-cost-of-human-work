#!/usr/bin/env python3
"""Build CSV matrices for the original schema; spreadsheet exporter writes CSVs."""
import argparse
import csv
import json
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument('--dataset-dir',type=Path,required=True)
ap.add_argument('--research-dir',type=Path,required=True)
ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args()
with (a.dataset_dir/'points.csv').open() as f: point_headers=next(csv.reader(f))
with (a.dataset_dir/'models.csv').open() as f:
    reader=csv.DictReader(f);model_headers=reader.fieldnames;registry={r['model_id']:r for r in reader}
calc=json.loads((a.research_dir/'calculations.json').read_text())
rows=[]
for c in calc['points']:
    opus=c['model_id']=='claude-opus-4-1'
    artifact='221-line page with biography, four project cards and skills' if opus else '433-line page with personality bars, six portfolio cards and two technical-project cards'
    row=dict.fromkeys(point_headers,'')
    row.update(point_id=c['point_id'],task='Build and hand off a personal website',task_category='coding',
      task_description='Build one static personal website from existing biography, personality and project material. Includes planning, code, browser checks, first hosting upload and URL handoff on 2025-10-13. '+('Initial Opus 4.1 page and Netlify deployment.' if opus else 'Initial Sonnet 4.5 page and password-protected Netlify deployment; unrestricted public access was not achieved at this endpoint.'),
      model_id=c['model_id'],compute_scope='inference',compute_flops=c['compute_flops'],human_skill='expert',human_time_scope='task_performance',human_time=c['human_time'],performance_vs_human='match',comparison_issues='none_identified',compute_evidence='derived_assumed_inputs',human_time_evidence='assumed',
      performance_evidence='Assumed expert baseline reproduces the delivered '+artifact+' and initial URL handoff at comparable quality. '+('The deployed HTML matches the reconstructed source-time artifact.' if opus else 'One portfolio link was disabled and a human administrator found password protection on the initial deployment. Later repairs are outside the comparison.'),
      human_time_statistic='point_estimate',human_time_subset='not_applicable',human_attempts='not_applicable',human_time_source='research/village-websites.md#work-delivered-and-human-effort',human_time_method='estimated',compute_method='operation_count',compute_statistic='total',compute_subset='all',ai_attempts=1,
      compute_source='research/village-websites.md; research/recompute.py; research/calculations.json',tokens=c['text_tokens_estimate'],tokens_accounting='input_cache_creation_output',source_dataset='AI Village',
      source_record='https://theaidigest.org/village/goal/each-agent-build-your-own-personal-website; agent-work/sources/agent-operations/village/sessions-2025-10-13.json; agent-work/sources/agent-operations/village/events-2025-10-13-1.json; research/selection.json; performance: research/'+('opus41' if opus else 'sonnet45')+'-first-site.html',
      notes='Includes GPT-5-Codex helper work and estimated session consolidation. Native computer cache reads are excluded; controller cache decomposition is unavailable. Text-only tokens use a screenshot-position estimate; compute retains native combined text/image positions and an explicit visual-encoder proxy. Human time covers these pages, not creation of the earlier projects they describe.'+('' if opus else ' Includes 10,000 estimated fresh tokens for one coding-helper timeout.'))
    assert set(row)==set(point_headers)
    rows.append(row)
models=[registry['claude-opus-4-1'],registry['claude-sonnet-4-5']]
helper=dict.fromkeys(model_headers,'not_applicable')
helper.update(model_id='gpt-5-codex',model='GPT-5-Codex',company='OpenAI',model_release_date='2025-09-15',model_release_source='https://openai.com/index/introducing-upgrades-to-codex/',flops_per_token=200000000000,flops_per_token_method='two_active_parameters',active_parameters=100000000000,active_parameters_basis='estimated',parameter_source='https://openai.com/index/introducing-upgrades-to-codex/; https://epochai.substack.com/p/notes-on-gpt-5-training-compute; research/village-websites.md#coding-helper',notes='GPT-5 family transfer of the existing 100B active-parameter estimate; not disclosed by OpenAI. First available through Codex subscription access on September 15, before API-key access on September 23. Native October 2025 logs use the moving gpt-5-codex alias, so the exact underlying snapshot is unresolved.')
models.append(helper)
matrices={name:[headers]+[[r[h] for h in headers] for r in values] for name,headers,values in [('points',point_headers,rows),('models',model_headers,models)]}
a.output.write_text(json.dumps(matrices,ensure_ascii=False,indent=2)+'\n')
