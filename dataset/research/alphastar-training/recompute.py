#!/usr/bin/env python3
"""AlphaStar training reconstruction. Python 3 standard library only.

Read-only inputs: --sources DIR --recipe FILE. --output must be a new file outside DIR.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
from pathlib import Path
import statistics
import zipfile


def network(p):
    n = p['entity_slots']
    terms = {'policy_weights_once': 2 * p['policy_parameters']}
    def repeat(name, weights, applications):
        # The first application of these weights is already in 2P.
        terms[name] = 2 * weights * (applications - 1)
    repeat('entity_input_projection', p['entity_input_width'] * 256, n)
    repeat('entity_attention_and_mlp', 3 * (2*3*256*128 + 2*128*256 + 2*256*1024), n)
    terms['entity_qk_and_av'] = 3 * 2 * 2 * 2 * n * n * 128
    repeat('entity_embedding', 256*256, n)
    repeat('entity_scatter_projection', 256*32, n)
    for name, side, ci, co, kernel, copies in [
        ('spatial_projection',128,52,32,1,1), ('spatial_down1',64,32,64,4,1),
        ('spatial_down2',32,64,128,4,1), ('spatial_down3',16,128,128,4,1),
        ('spatial_residual',16,128,128,3,8), ('location_projection',16,132,128,1,1),
        ('location_residual',16,128,128,3,8), ('location_up1',16,128,128,4,1),
        ('location_up2',32,128,64,4,1), ('location_up3',64,64,16,4,1),
        ('location_up4',128,16,1,4,1)]:
        repeat(name, ci*co*kernel*kernel*copies, side*side)
        # Transposed conv applications use the input grid, not the larger output grid.
        if name.startswith('location_'):
            terms[name] *= p['location_head_fraction']
    repeat('selected_and_target_keys',2*256*32,n)
    selected_weights = 1024*256 + 256*32 + 4*(32+32)*32 + 32*1024
    repeat('selected_unit_recurrence',selected_weights,p['selected_units_unroll'])
    terms['selected_unit_attention'] = p['selected_units_unroll'] * n * 32 * 4
    terms['other_operations_allowance'] = sum(terms.values()) * p['forward_other_operations_fraction']
    policy = sum(terms.values())
    # Training-only value network processing is largely scalar; retain the full
    # reported non-policy parameter remainder as a single-application allowance.
    critic = 2 * (p['training_parameters'] - p['policy_parameters'])
    return {'policy_forward_flops':policy,'critic_forward_allowance_flops':critic,'terms':terms}


def compute(p):
    net=network(p); f=net['policy_forward_flops']; c=net['critic_forward_allowance_flops']
    processed=p['league_learners']*p['league_days']*86400*p['learner_processed_steps_per_second']*p['learner_rate_fraction']
    generated=processed/p['replay_uses_per_generated_step']
    opt=processed*p['training_to_forward_ratio']*(f+c)
    student=generated*f
    opponent=student*p['opponent_steps_per_home_step']
    teacher=student*p['teacher_steps_per_home_step']
    eval_fraction=p['evaluator_tasks']/(p['league_learners']*p['training_game_tasks_per_learner'])
    evaluation=generated*eval_fraction*p['evaluator_progress_relative_to_training']*2*f
    sl_steps=p['supervised_replays']*p['players_per_supervised_replay']*p['supervised_steps_per_player_replay']*p['supervised_passes']
    ft_steps=p['fine_tuning_winning_replays']*p['supervised_steps_per_player_replay']*p['fine_tuning_passes']
    sl=sl_steps*p['training_to_forward_ratio']*f
    ft=ft_steps*p['training_to_forward_ratio']*f
    held_out=(sl+ft)*p['held_out_policy_training_allowance_sl_copies']
    parts={'league_optimization':opt,'rollout_student':student,'rollout_opponent':opponent,
           'rollout_frozen_teacher':teacher,'league_evaluation':evaluation,
           'supervised_initialization':sl,'winning_replay_fine_tuning':ft,
           'held_out_validation_policy_training_allowance':held_out}
    total=sum(parts.values())
    peak=p['tpu_v3_cores_per_learner']*p['tpu_v3_teraflops_per_core']*1e12
    return {'compute_flops':total,'parts':parts,'network':net,'processed_learner_steps':processed,
            'generated_home_steps':generated,'supervised_steps':sl_steps,'fine_tuning_steps':ft_steps,
            'policy_initialization_share':(sl+ft)/total,'validation_policy_allowance_share':held_out/total,
            'approx_learner_hardware_utilization':p['learner_processed_steps_per_second']*p['training_to_forward_ratio']*(f+c)/peak,
            'approx_actor_hardware_utilization':p['learner_processed_steps_per_second']/p['replay_uses_per_generated_step']*(2+p['opponent_steps_per_home_step'])*f/peak,
            'implied_home_steps_per_source_130m_league_games':generated/130000000}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sources',type=Path,required=True);ap.add_argument('--recipe',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();s=a.sources.resolve();r=a.recipe.resolve();o=a.output.resolve()
    if o.exists() or o==s or s in o.parents or o==r:ap.error('Output must be a new file outside the evidence directory.')
    hashes={}
    for x in json.loads((s/'source-manifest.json').read_text())['files']:
        f=(s/x['path']).resolve()
        if s not in f.parents:raise ValueError('Source path escape')
        h=hashlib.sha256(f.read_bytes()).hexdigest()
        if h!=x['sha256']:raise ValueError('Hash mismatch: '+x['path'])
        hashes[x['path']]=h
    p=json.loads(r.read_text())
    with zipfile.ZipFile(s/'skillcraft.zip') as z:
        all_rows=list(csv.DictReader(io.StringIO(z.read('SkillCraft1_Dataset.csv').decode())))
    selected=[x for x in all_rows if int(x['LeagueIndex'])==p['human_selected_league']]
    hours=[float(x['TotalHours']) for x in selected]
    with zipfile.ZipFile(s/'alphastar-supp-data.zip') as z:
        bnet=json.loads(z.read('Supplementary Information/bnet.json'))['data']
    final=[x for x in bnet if x['Experiment name']=='AlphaStar Final']
    result={'point_id':'game-sc2-train-alphastar','source_hashes':hashes,
            'recipe_sha256':hashlib.sha256(r.read_bytes()).hexdigest(),
            'central':compute(p),'human_rows':selected,'human_count':len(selected),
            'human_mean_hours':statistics.mean(hours),'human_median_hours':statistics.median(hours),
            'human_hours_range':[min(hours),max(hours)],
            'human_time':statistics.mean(hours)*3600*p['human_specialists_required'],
            'human_median_synthesis_seconds':statistics.median(hours)*3600*p['human_specialists_required'],
            'human_without_largest_report_seconds':statistics.mean(sorted(hours)[:-1])*3600*p['human_specialists_required'],
            'native_final_results':{race:dict(collections.Counter(x['Outcome'] for x in final if x['AlphaStar race']==race)) for race in ['terran','protoss','zerg']},
            'native_final_count':len(final),'scenarios':{}}
    for name,changes in p['scenarios'].items():result['scenarios'][name]=compute(p|changes)
    result['scenarios']['combined_low']=compute(p|p['scenarios']['compact_execution']|p['scenarios']['low_training'])
    result['scenarios']['combined_high']=compute(p|p['scenarios']['large_execution']|p['scenarios']['high_training'])
    o.parent.mkdir(parents=True,exist_ok=True);o.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
