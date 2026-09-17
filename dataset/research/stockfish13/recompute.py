"""Audit/regrade saved Stockfish observations without executing an engine.

Dependency: python-chess. Inputs: --sources directory with original puzzles.csv,
local-observations.jsonl.gz and net; --selection the frozen sample JSON.
Writes a new --output outside the evidence/input directories.
"""
import argparse
from collections import Counter
import csv
from decimal import Decimal
import gzip
import hashlib
import io
import json
from pathlib import Path
import re

import chess
import chess.pgn


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sources', type=Path, required=True)
    p.add_argument('--selection', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    src, out = a.sources.resolve(), a.output.resolve()
    if out.exists() or src == out or src in out.parents or out == a.selection.resolve():
        p.error('output must be new and outside source evidence and input files')
    selection = json.loads(a.selection.read_text())
    assert sha(src / 'puzzles.csv') == selection['source_sha256']
    puzzles = list(csv.DictReader((src / 'puzzles.csv').open(newline='')))
    raw = gzip.decompress((src / 'local-observations.jsonl.gz').read_bytes())
    records = [json.loads(line) for line in raw.decode().splitlines()]
    assert records[0]['type'] == 'metadata' and records[-1]['type'] == 'complete'
    assert records[0]['selection'] == selection
    assert records[0]['input_sha256']['selection'] == sha(a.selection)
    assert records[0]['input_sha256']['net'] == sha(src / 'nn-62ef826d1a6d.nnue')
    assert len(records[1:-1]) == records[-1]['total_attempts'] == 2000
    assert all(r['type'] == 'puzzle' for r in records[1:-1])
    identifiers = set()
    details, means = [], []
    for budget in selection['node_budgets']:
        group = [r for r in records[1:-1] if r['node_budget_per_decision'] == budget]
        assert len(group) == 1000
        corrected, counts, control_checks, alternative_mates = 0, Counter(), 0, 0
        for r in group:
            i = r['sample_index']
            assert r['source_index'] == selection['source_indices'][i]
            assert r['puzzle_id'] == selection['puzzle_ids'][i]
            assert (budget, r['puzzle_id']) not in identifiers
            identifiers.add((budget, r['puzzle_id']))
            source = puzzles[r['source_index']]
            game = chess.pgn.read_game(io.StringIO(source['PGN']))
            assert game and not game.errors
            board = game.end().board()
            assert board.fen() == chess.Board(source['FEN']).fen()
            expected = source['Moves'].split()
            di, success, total = 0, True, Counter()
            for move_index, reference in enumerate(expected):
                if move_index % 2:
                    decision = r['decisions'][di]
                    di += 1
                    assert decision['move_index'] == move_index and decision['fen'] == board.fen()
                    assert decision['reference'] == reference
                    original, instrumented = decision['baseline'], decision['instrumented']
                    assert original['bestmove_line'] == instrumented['bestmove_line']
                    assert original['stable_final_info'] == instrumented['stable_final_info']
                    assert original['last_info_nodes'] == instrumented['last_info_nodes']
                    control_checks += 1
                    exported = [line for line in instrumented['lines'] if line.startswith('info string neural_counters ')]
                    assert len(exported) == 1
                    native = json.loads(exported[0].split('neural_counters ', 1)[1])
                    assert native == instrumented['neural_counters']
                    assert native['search_nodes'] == instrumented['last_info_nodes']
                    evals = native['evaluations']
                    assert native['affine_calls'] == 3 * evals
                    assert native['affine_multiplies'] == 17440 * evals
                    assert native['affine_additions'] == 17635 * evals
                    assert native['clipped_values'] == 576 * evals
                    assert native['activation_shifts'] == 64 * evals
                    assert native['output_divisions'] == evals
                    assert native['feature_additions'] % 256 == native['feature_subtractions'] % 256 == 0
                    total.update(native)
                    predicted = instrumented['lines'][-1].split()[1]
                    assert predicted == decision['predicted'] == instrumented['bestmove']
                    move = chess.Move.from_uci(predicted)
                    assert move in board.legal_moves
                    if predicted != reference:
                        board.push(move)
                        success = board.is_checkmate()
                        alternative_mates += int(success)
                        assert decision['mating_alternative'] == success
                        break
                board.push(chess.Move.from_uci(reference))
            assert di == len(r['decisions']) == r['actual_solver_calls']
            assert success == r['success']
            assert dict(total) == r['counters']
            neural = sum(total[k] for k in ['affine_multiplies', 'affine_additions',
                                          'feature_additions', 'feature_subtractions', 'output_divisions'])
            assert neural == r['neural_arithmetic_operations']
            counts.update(total)
            corrected += int(success)
            details.append({'node_budget': budget, 'puzzle_id': r['puzzle_id'], 'success': success,
                            'neural_operations': neural, 'solver_calls': di})
        required_moves = [len(puzzles[i]['Moves'].split()) // 2 for i in selection['source_indices']]
        ratings = [int(puzzles[i]['Rating']) for i in selection['source_indices']]
        total_neural = sum(r['neural_arithmetic_operations'] for r in group)
        means.append({'point_id': f'game-stockfish13-puzzle-nodes{budget}', 'node_budget_per_solver_decision': budget,
                      'attempts': 1000, 'successful': corrected, 'success_percent': str(Decimal(corrected) / 10),
                      'total_neural_operations': total_neural,
                      'mean_neural_operations': str(Decimal(total_neural) / 1000),
                      'zero_neural_attempts': sum(r['counters']['evaluations'] == 0 for r in group),
                      'mean_search_nodes': str(Decimal(counts['search_nodes']) / 1000),
                      'mean_nnue_evaluations': str(Decimal(counts['evaluations']) / 1000),
                      'mean_solver_calls': str(Decimal(sum(r['actual_solver_calls'] for r in group)) / 1000),
                      'required_solver_moves_mean': str(Decimal(sum(required_moves)) / 1000),
                      'puzzle_rating_mean': str(Decimal(sum(ratings)) / 1000),
                      'puzzle_rating_min_max': [min(ratings), max(ratings)],
                      'control_decisions_checked': control_checks, 'accepted_mating_alternatives': alternative_mates,
                      'counter_totals': dict(counts),
                      'canonical_affine_mac_operations': 2 * counts['affine_multiplies'],
                      'neon_reduction_additions': 195 * counts['evaluations'],
                      'sparse_accumulator_operations': counts['feature_additions'] + counts['feature_subtractions'],
                      'output_divisions': counts['output_divisions'],
                      'human_seconds_estimated': 35, 'human_scenario_seconds': [15, 90],
                      'human_donor_decision_seconds': 28.946, 'human_donor_attempts': 17 * 8})
    result = {'source_sha256': {'puzzles.csv': sha(src / 'puzzles.csv'),
                               'local-observations.jsonl.gz': sha(src / 'local-observations.jsonl.gz'),
                               'uncompressed_observations': hashlib.sha256(raw).hexdigest(),
                               'selection': sha(a.selection)},
              'observation_date_utc': records[0]['observed_at_utc'], 'all_control_checks_passed': True,
              'scoring_disagreements': 0, 'points': means, 'regraded_attempts': details}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(means, indent=2))


if __name__ == '__main__':
    main()
