#!/usr/bin/env python3
"""Emit the TextQuests candidate points.csv, models.csv and dispositions.csv.

Reads only research/textquests/calculations.json and the retained leaderboard extract, so it
reruns after publication from the repository layout alone.

Usage:
  python3 research/textquests/build_rows.py \
      --calculations research/textquests/calculations.json \
      --leaderboard agent-work/sources/textquests/textquests-leaderboard-2026-09-13.json \
      --outdir candidates/textquests
"""
import argparse, csv, json, os

POINT_FIELDS = ['point_id','task','task_category','task_description','model_id','compute_scope',
 'compute_flops','human_skill','human_time_scope','human_time','performance_vs_human',
 'comparison_issues','compute_evidence','human_time_evidence','performance_evidence',
 'human_time_statistic','human_time_subset','human_attempts','human_time_source',
 'human_time_method','compute_method','compute_statistic','compute_subset','ai_attempts',
 'compute_source','tokens','tokens_accounting','source_dataset','source_record','notes',
 'ai_cost_usd','ai_cost_basis','ai_cost_date','human_cost_usd','human_cost_basis']

MODEL_FIELDS = ['model_id','model','company','model_release_date','model_release_source',
 'flops_per_token','flops_per_token_method','active_parameters','active_parameters_basis',
 'encoder_parameters','encoder_parameters_basis','decoder_parameters','decoder_parameters_basis',
 'parameter_source','notes']

SLUG = {'o3':'o3','gemini-2.5-pro':'gemini25pro','claude-opus-4.0':'claudeopus4',
        'claude-sonnet-4.0':'claudesonnet4','gpt-4.1':'gpt41','gpt-4.1-mini':'gpt41mini'}
BOARD_NAME = {'o3':'o3','gemini-2.5-pro':'Gemini 2.5 Pro','claude-opus-4.0':'Claude Opus 4',
 'claude-sonnet-4.0':'Claude Sonnet 4','gpt-4.1':'GPT-4.1','gpt-4.1-mini':'GPT-4.1-mini'}
PRETTY = {'o3':'o3','gemini-2.5-pro':'Gemini 2.5 Pro','claude-opus-4.0':'Claude Opus 4',
 'claude-sonnet-4.0':'Claude Sonnet 4','gpt-4.1':'GPT-4.1','gpt-4.1-mini':'GPT-4.1-mini'}

TASK_DESCRIPTION = (
 "Play all 25 Infocom interactive fiction games in TextQuests, one session per game, up to 500 "
 "parser commands each, stopping early on completion. Each turn the agent gets the game's latest "
 "text output appended to its full untruncated history and returns a short reasoning and one "
 "parser command; the printed feelies and the complete official InvisiClues hint booklet are in "
 "the opening context, no external tools are allowed, and any earlier step can be restored. "
 "Scored by mean game progress, the highest labelled checkpoint percentage reached in each game.")

EXTRA_NOTE = {
 'gemini-2.5-pro': ("This model cannot switch thinking off, yet its largest response in the suite "
   "is 1.4K tokens, so thoughts are probably outside the output counter; 500 to 2,000 hidden "
   "tokens a call would give 9.7e18 to 1.3e19. "),
 'claude-opus-4.0': ("The source's Sonnet 4 With Clues column duplicates its No Clues column, so "
   "the two Claude cells are read together. "),
 'claude-sonnet-4.0': ("The source prints this model's With Clues totals identical to its No Clues "
   "ones; Claude Opus 4's difference is 2M in both modes too. "),
}
# The rounding band is only stated where it moves the value by more than 5 per cent.
BAND_THRESHOLD = 0.05


def suite_disposition(model, mode, progress, finished, tokens_published, ratio, max_se, se_below, pid, keep):
    if keep:
        reason = ("Mean game progress %.1f per cent is %.0f per cent of the human completer's 100 per cent, "
                  "above the half-of-human guide" % (progress, progress))
    elif tokens_published == 'no':
        reason = ("No published token counts: the paper's token table covers six models and the run "
                  "trajectories are not released, so no compute can be formed for this cell"
                  + ("; its progress would otherwise clear the half-of-human guide" if ratio >= 0.5 else
                     "; its progress is %.0f per cent of the human completer's 100 per cent in any case" % progress))
    else:
        reason = ("Mean game progress %.1f per cent is %.0f per cent of the human completer's 100 per cent, "
                  "%.2f standard errors below the half-of-human guide even at the largest dispersion the "
                  "unpublished per-game scores could have" % (progress, progress, se_below))
    return {'model': model, 'mode': 'With Clues' if mode == 'with_clues' else 'No Clues',
            'unit': '25-game suite run', 'game': '', 'tokens_published': tokens_published,
            'progress_pct': progress, 'completed_games': finished, 'human_score_pct': 100,
            'ratio_to_human': round(ratio, 3), 'max_se_of_ratio': round(max_se, 3),
            'standard_errors_below_guide': round(se_below, 2), 'point_id': pid,
            'outcome': 'row' if keep else 'not a row', 'reason': reason}


def per_game_disposition(model, game, votes, n_games_timed):
    if votes:
        why = ("human time for this game rests on %d IFDB completion vote%s" % (votes, '' if votes == 1 else 's')
               + " and per-game compute would be the 25-game total split evenly, which overstates a game the "
                 "agent finished before the 500-step cap by an unpublished factor")
    else:
        why = ("no IFDB member has voted a completion time for this game, and per-game compute would be the "
               "25-game total split evenly over games whose step counts are unpublished")
    return {'model': model, 'mode': 'With Clues', 'unit': 'one game played to completion', 'game': game,
            'tokens_published': 'suite total only', 'progress_pct': 100, 'completed_games': 1,
            'human_score_pct': 100, 'ratio_to_human': 1.0, 'max_se_of_ratio': '', 'standard_errors_below_guide': '',
            'point_id': '', 'outcome': 'not a row',
            'reason': 'Both sides finish the game, so this would be a match row, but ' + why}


def fmt(x, sig=4):
    return f"{x:.{sig}g}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--calculations', required=True)
    ap.add_argument('--leaderboard', required=True)
    ap.add_argument('--ifdb', required=True)
    ap.add_argument('--outdir', required=True)
    a = ap.parse_args()
    calc = json.load(open(a.calculations))
    board = {e['model']: e for e in json.load(open(a.leaderboard))}
    human_s = round(calc['human']['suite_seconds'])
    votes = calc['human']['votes']
    os.makedirs(a.outdir, exist_ok=True)

    points, disp = [], []
    for c in calc['cells']:
        label, mode = c['model_label'], c['mode']
        pid = f"game-textquests-{'clues' if mode=='with_clues' else 'noclues'}-{SLUG[label]}"
        e = board[BOARD_NAME[label]]
        finished = c['completed_games']
        games = ', '.join(e.get('completedGames') or []) if mode == 'with_clues' and e.get('completedGames') else 'none'
        lo, hi = c['compute_flops_rounding_band']
        att = c['attention_ratio_to_central']
        if c['outcome'] == 'row':
            perf = (f"Mean game progress over the 25 games, the highest labelled checkpoint percentage each "
                    f"run reached: {c['progress_pct']} per cent, finishing {finished} of 25. A player who "
                    f"finishes a game reaches 100 per cent by construction, and the human timing sample is "
                    f"members reporting how long it took them to finish. The weakest entry on the board "
                    f"scores 7.7 per cent.")
            band = (f"Source rounding puts the result between {fmt(lo,3)} and {fmt(hi,3)}. "
                    if (hi - lo) / 2 / c['compute_flops'] > BAND_THRESHOLD else "")
            notes = (f"Counted tokens are the source table's total input minus its cache tokens, plus "
                     f"output, so cache reads are excluded. " + band +
                     f"Omitted cached-context attention would add {att['L=64, d=8192']:.2f}x to "
                     f"{att['L=96, d=12288']:.2f}x. " + EXTRA_NOTE.get(label, '') +
                     f"Progress is a position on the critical path, not a share of effort; the agent "
                     f"finished {finished} of 25 games against the sample's 25. Human time is {votes} IFDB "
                     f"completion votes over 18 of the 25 games, 7 imputed.")
            points.append({
             'point_id': pid,
             'task': 'TextQuests 25-game Infocom suite with clues',
             'task_category': 'games',
             'task_description': TASK_DESCRIPTION,
             'model_id': c['model_id'],
             'compute_scope': 'inference',
             'compute_flops': fmt(c['compute_flops']),
             'human_skill': 'typical',
             'human_time_scope': 'task_performance',
             'human_time': str(human_s),
             'performance_vs_human': 'below',
             'comparison_issues': 'different_task; different_inputs_or_tools; different_attempt_selection',
             'compute_evidence': 'derived_assumed_inputs',
             'human_time_evidence': 'task_timings',
             'performance_evidence': perf,
             'human_time_statistic': 'mean',
             'human_time_subset': 'successful',
             'human_attempts': str(votes),
             'human_time_source': 'IFDB member completion-time votes for the 25 TextQuests games, https://ifdb.org; research/textquests.md#human-baseline',
             'human_time_method': 'other_calculation',
             'compute_method': 'params_tokens',
             'compute_statistic': 'total',
             'compute_subset': 'all',
             'ai_attempts': '25',
             'compute_source': f'arXiv:2507.23701v3 Table 5, With Clues column; research/textquests.md#{pid}',
             'tokens': fmt(c['counted_tokens'], 6),
             'tokens_accounting': 'input_cache_creation_output',
             'source_dataset': 'TextQuests',
             'source_record': (f"arXiv:2507.23701v3, Appendix E Table 5 and Appendix C Table 4, With Clues column "
                               f"for {PRETTY[label]}; textquests.ai leaderboard entry {BOARD_NAME[label]}, games "
                               f"finished: {games}; harness github.com/centerforaisafety/textquests at commit "
                               f"18dc472618cc522dfaad04fec19fae775a87860f; performance: Table 4"),
             'notes': notes,
             'ai_cost_usd': f"{c['ai_cost_usd']:.2f}",
             'ai_cost_basis': 'list_price',
             'ai_cost_date': c['ai_cost_date'],
             'human_cost_usd': '',
             'human_cost_basis': 'not_available',
            })
        disp.append(suite_disposition(BOARD_NAME[label], mode, c['progress_pct'], finished, 'yes',
                                      c['ratio_to_human_progress'], c['max_se_of_ratio'],
                                      c['standard_errors_below_half_guide'],
                                      pid if c['outcome'] == 'row' else '', c['outcome'] == 'row'))

    # Every other leaderboard cell, so the source's records reconcile to rows or dispositions.
    covered = {(d['model'], d['mode']) for d in disp}
    ifdb_votes = {g: len(r['votes']) for g, r in
                  json.load(open(a.ifdb))['games'].items()}
    for e in board.values():
        for mode, side in (('no_clues', e['noClues']), ('with_clues', e['withClues'])):
            name = e['model']
            key = (name, 'With Clues' if mode == 'with_clues' else 'No Clues')
            if key in covered:
                continue
            progress = side['progress']
            finished = side['completed'] if mode == 'with_clues' else (
                len(e['noCluesCompletedGames']) if e.get('noCluesCompletedGames') is not None else 0)
            max_sd = (progress * (100.0 - progress)) ** 0.5
            max_se = max_sd / 5.0 / 100.0
            ratio = progress / 100.0
            disp.append(suite_disposition(name, mode, progress, finished, 'no', ratio, max_se,
                                          (0.5 - ratio) / max_se, '', False))
    for c in calc['cells']:
        if c['mode'] != 'with_clues':
            continue
        for game in board[BOARD_NAME[c['model_label']]].get('completedGames') or []:
            disp.append(per_game_disposition(BOARD_NAME[c['model_label']], game, ifdb_votes[game], 18))

    with open(os.path.join(a.outdir, 'points.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, POINT_FIELDS, lineterminator='\r\n'); w.writeheader(); w.writerows(points)
    with open(os.path.join(a.outdir, 'models.csv'), 'w', newline='') as f:
        csv.DictWriter(f, MODEL_FIELDS, lineterminator='\r\n').writeheader()
    with open(os.path.join(a.outdir, 'dispositions.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, list(disp[0].keys()), lineterminator='\r\n'); w.writeheader(); w.writerows(disp)
    print(f"{len(points)} points, {len(disp)} token-bearing cells recorded")
    for p in points:
        for k in ['notes', 'task_description', 'performance_evidence', 'source_record', 'compute_source', 'human_time_source']:
            print(f"  {p['point_id']:38} {k:20} {len(p[k])}")


if __name__ == '__main__':
    main()
