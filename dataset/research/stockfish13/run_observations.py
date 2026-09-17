"""Collect paired original/instrumented Stockfish puzzle observations.

Dependency: python-chess. No model API, network or GPU use. Inputs are read only;
output must be a new JSONL outside input-evidence directories. --limit supports
a bounded feasibility pilot; the frozen selection still identifies the full set.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import queue
import re
import subprocess
import threading
import time

import chess
import chess.pgn


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Engine:
    def __init__(self, binary, net):
        self.process = subprocess.Popen([str(binary)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, text=True, bufsize=1)
        self.queue = queue.Queue()

        def read():
            for line in self.process.stdout:
                self.queue.put(line.rstrip('\n'))
            self.queue.put(None)

        threading.Thread(target=read, daemon=True).start()
        self.send('uci')
        self.initial = self.until('uciok')
        self.options = ['setoption name Threads value 1', 'setoption name Hash value 16',
                        'setoption name MultiPV value 1', 'setoption name Skill Level value 20',
                        'setoption name UCI_LimitStrength value false',
                        'setoption name Use NNUE value true', 'setoption name EvalFile value ' + str(net)]
        for command in self.options:
            self.send(command)
        self.send('isready')
        self.initial += self.until('readyok')

    def send(self, text):
        self.process.stdin.write(text + '\n')
        self.process.stdin.flush()

    def until(self, prefix, timeout=30):
        end = time.monotonic() + timeout
        lines = []
        while True:
            line = self.queue.get(timeout=max(0.01, end - time.monotonic()))
            if line is None:
                raise RuntimeError('Engine exited: ' + repr(lines[-10:]))
            lines.append(line)
            if line.startswith(prefix):
                return lines

    def reset(self):
        self.send('ucinewgame')
        self.send('isready')
        assert self.until('readyok')[-1] == 'readyok'

    def search(self, root_fen, moves, nodes):
        command = 'position fen ' + root_fen
        if moves:
            command += ' moves ' + ' '.join(moves)
        self.send(command)
        self.send('go nodes ' + str(nodes))
        begin = time.monotonic()
        lines = self.until('bestmove ')
        duration = time.monotonic() - begin
        infos = [line for line in lines if line.startswith('info depth ') and ' nodes ' in line]
        assert infos, lines
        info = infos[-1]
        stable = re.sub(r'\b(?:time|nps) \d+\s*', '', info)
        counters = [json.loads(line.split('neural_counters ', 1)[1]) for line in lines if 'neural_counters ' in line]
        assert len(counters) <= 1
        result = {'position_command': command, 'go_command': 'go nodes ' + str(nodes),
                  'lines': lines, 'bestmove_line': lines[-1], 'bestmove': lines[-1].split()[1],
                  'last_info_nodes': int(re.search(r'\bnodes (\d+)', info).group(1)),
                  'stable_final_info': stable, 'wall_seconds': duration}
        if counters:
            result['neural_counters'] = counters[0]
        return result

    def close(self):
        if self.process.poll() is None:
            self.send('quit')
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['puzzles', 'selection', 'baseline', 'instrumented', 'net', 'output']:
        p.add_argument('--' + name, required=True, type=Path)
    p.add_argument('--limit', type=int, default=1000)
    p.add_argument('--max-runtime-seconds', type=float, default=1800)
    a = p.parse_args()
    out = a.output.resolve()
    inputs = [getattr(a, k).resolve() for k in ['puzzles', 'selection', 'baseline', 'instrumented', 'net']]
    if out.exists() or any(out == f or f.parent == out or f.parent in out.parents for f in inputs):
        p.error('output must be new and outside input-evidence directories')
    selection = json.loads(a.selection.read_text())
    assert sha(a.puzzles) == selection['source_sha256']
    assert 0 < a.limit <= selection['sample_count'] == 1000
    puzzles = list(csv.DictReader(a.puzzles.open(newline='')))
    selected = list(zip(selection['source_indices'], selection['puzzle_ids']))[:a.limit]
    for i, ident in selected:
        assert puzzles[i]['PuzzleId'] == ident
    engines = [Engine(a.baseline.resolve(), a.net.resolve()), Engine(a.instrumented.resolve(), a.net.resolve())]
    started = time.monotonic()
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        with out.open('x') as f:
            def write(item):
                f.write(json.dumps(item, separators=(',', ':')) + '\n')
                f.flush()

            write({'type': 'metadata', 'observed_at_utc': datetime.now(timezone.utc).isoformat(),
                   'kind': 'new local benchmark observations, with paired original-engine control',
                   'input_sha256': {k: sha(getattr(a, k)) for k in ['puzzles', 'selection', 'baseline', 'instrumented', 'net']},
                   'sample_limit': a.limit, 'selection': selection,
                   'baseline_initial_uci': engines[0].initial, 'instrumented_initial_uci': engines[1].initial,
                   'uci_options': engines[0].options, 'python_chess_version': chess.__version__})
            for budget in selection['node_budgets']:
                solved = 0
                for sample_index, (source_index, ident) in enumerate(selected):
                    if time.monotonic() - started > a.max_runtime_seconds:
                        raise TimeoutError('Overall runtime guard reached; partial observations preserved.')
                    row = puzzles[source_index]
                    game = chess.pgn.read_game(io.StringIO(row['PGN']))
                    assert game is not None and not game.errors
                    board = game.end().board()
                    assert board.fen() == chess.Board(row['FEN']).fen(), ident
                    root = game.board()
                    played = [move.uci() for move in game.mainline_moves()]
                    expected = row['Moves'].split()
                    for engine in engines:
                        engine.reset()
                    decisions = []
                    success = True
                    for move_index, reference in enumerate(expected):
                        if move_index % 2 == 1:
                            before = board.fen()
                            results = [engine.search(root.fen(), played, budget) for engine in engines]
                            equal = (results[0]['bestmove_line'] == results[1]['bestmove_line']
                                     and results[0]['last_info_nodes'] == results[1]['last_info_nodes']
                                     and results[0]['stable_final_info'] == results[1]['stable_final_info'])
                            assert 'neural_counters' not in results[0] and 'neural_counters' in results[1]
                            count = results[1]['neural_counters']
                            assert count['affine_calls'] == 3 * count['evaluations']
                            assert count['affine_multiplies'] == 17440 * count['evaluations']
                            assert count['affine_additions'] == (17440 + 195) * count['evaluations']
                            assert count['clipped_values'] == 576 * count['evaluations']
                            assert count['activation_shifts'] == 64 * count['evaluations']
                            assert count['output_divisions'] == count['evaluations']
                            assert count['feature_additions'] % 256 == count['feature_subtractions'] % 256 == 0
                            predicted = results[1]['bestmove']
                            move = chess.Move.from_uci(predicted)
                            assert move in board.legal_moves
                            mating_alternative = False
                            if predicted != reference:
                                next_board = board.copy()
                                next_board.push(move)
                                mating_alternative = next_board.is_checkmate()
                            decision = {'move_index': move_index, 'fen': before, 'reference': reference,
                                        'predicted': predicted, 'mating_alternative': mating_alternative,
                                        'paired_control_equal': equal,
                                        'baseline': results[0], 'instrumented': results[1]}
                            decisions.append(decision)
                            if not equal:
                                write({'type': 'equality_failure', 'puzzle_id': ident, 'budget': budget, 'decision': decision})
                                raise AssertionError('Instrumented/control mismatch: ' + ident)
                            if predicted != reference:
                                success = mating_alternative
                                break
                        move = chess.Move.from_uci(reference)
                        assert move in board.legal_moves
                        board.push(move)
                        played.append(reference)
                    solved += int(success)
                    totals = {key: sum(z['instrumented']['neural_counters'][key] for z in decisions)
                              for key in decisions[0]['instrumented']['neural_counters']}
                    flops = sum(totals[k] for k in ['affine_multiplies', 'affine_additions', 'feature_additions', 'feature_subtractions', 'output_divisions'])
                    write({'type': 'puzzle', 'node_budget_per_decision': budget,
                           'sample_index': sample_index, 'source_index': source_index, 'puzzle_id': ident,
                           'rating': int(row['Rating']), 'success': success,
                           'required_solver_moves': len(expected) // 2, 'actual_solver_calls': len(decisions),
                           'neural_arithmetic_operations': flops, 'counters': totals, 'decisions': decisions})
                    if (sample_index + 1) % 25 == 0:
                        print(budget, sample_index + 1, 'puzzles;', solved, 'solved;', round(time.monotonic() - started, 1), 's', flush=True)
            write({'type': 'complete', 'total_attempts': len(selected) * len(selection['node_budgets']),
                   'wall_seconds': time.monotonic() - started})
    finally:
        for engine in engines:
            engine.close()


if __name__ == '__main__':
    main()
