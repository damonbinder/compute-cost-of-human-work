"""Count the released BCS BP-only recipe without executing models or pickle code.

Python 3.9+, standard library only. Required: --sources DIR --output NEW_JSON.
The output must be new and outside the source tree. No evidence is modified.
"""
import argparse
import collections
import csv
import hashlib
import html
import json
import pathlib
import pickletools
import re
import string
import struct


def checkpoint_metadata(path):
    data = path.read_bytes()
    name_len, extra_len = struct.unpack_from('<HH', data, 26)
    # Inspect pickle opcodes, never unpickle the checkpoint.
    ops = list(pickletools.genops(data[30 + name_len + extra_len:]))
    start = next(i for i, x in enumerate(ops) if x[1] == 'encoder_params')
    values = {}
    for key in ['pretrained_model_cfg', 'projection_dim', 'sequence_length']:
        i = next(i for i in range(start, len(ops)) if ops[i][1] == key)
        values[key] = ops[i + 2][1]
    assert values == {'pretrained_model_cfg': 'bert-base-uncased',
                      'projection_dim': 0, 'sequence_length': 32}
    return values


def puzzle(path):
    data = path.read_bytes()
    w, h = data[44:46]
    n = struct.unpack_from('<H', data, 46)[0]
    grid = data[52:52+w*h].decode('latin1')
    fields = data[52+2*w*h:].split(b'\0')
    clues = [x.decode('latin1') for x in fields[3:3+n]]
    answers = []
    number = 0
    for y in range(h):
        for x in range(w):
            pos = y*w+x
            if grid[pos] == '.':
                continue
            across = (x == 0 or grid[pos-1] == '.') and x+1 < w and grid[pos+1] != '.'
            down = (y == 0 or grid[pos-w] == '.') and y+1 < h and grid[pos+w] != '.'
            if across or down:
                number += 1
            for flag, direction, dx, dy in [(across, 'A', 1, 0), (down, 'D', 0, 1)]:
                if not flag:
                    continue
                cells, letters = [], []
                xx, yy = x, y
                while xx < w and yy < h and grid[yy*w+xx] != '.':
                    cells.append([yy, xx]); letters.append(grid[yy*w+xx])
                    xx += dx; yy += dy
                answers.append({'id': str(number)+direction, 'answer': ''.join(letters),
                                'length': len(letters), 'cells': cells})
    assert len(answers) == len(clues) == n
    for row, clue in zip(answers, clues):
        row['clue'] = clue
    crossings = collections.Counter(tuple(c) for a in answers for c in a['cells'])
    assert set(crossings.values()) == {2}
    return {'title': fields[0].decode('latin1'), 'author': fields[1].decode('latin1'),
            'width': w, 'height': h, 'clues': n, 'letters': len(crossings), 'entries': answers}


def domains(path):
    # Reproduce DPRForCrossword.load_passages: ID dictionary then column-3 normalization.
    with path.open(newline='') as f:
        docs = {r[0]: r[2] for r in csv.reader(f, delimiter='\t') if r[0] != 'id'}
    words = [''.join(c.upper() for c in t if c.upper() in string.ascii_uppercase)
             for t in docs.values()]
    raw = collections.Counter(map(len, words))
    unique = collections.Counter(map(len, set(words)))
    return len(docs), raw, unique


def operations(p, cfg, sequence, raw, unique, index_count, iterations=10, special=1):
    # Matmuls count two operations per multiply-add; scalar exp/log/erf/tanh/sqrt
    # count special operations each. Comparisons, integer/string work and moves excluded.
    d = cfg['hidden_size']; f = cfg['intermediate_size']; heads = cfg['num_attention_heads']
    layers = cfg['num_hidden_layers']; s = sequence; c = p['clues']; cells = p['letters']
    softmax = lambda n: 3*n - 1 + n*special
    log_softmax = lambda n: 3*n - 1 + (n+1)*special
    layer_norm = lambda n: 7*n + 2 + special
    bert_matrix_per_clue = layers*(8*s*d*d + 4*s*d*f + 4*s*s*d) + 2*d*d
    # Embedding position/type additions, attention mask, LN, and executed unused pooler.
    bert_scalar_per_clue = 2*s*d + s*layer_norm(d) + 2*s + d + d*special
    per_layer = (5*d+f)*s + 2*s*d + 2*s*layer_norm(d)
    per_layer += s*f*(4+special)  # exact GELU expression
    per_layer += 2*heads*s*s + heads*s*softmax(s)
    bert_scalar_per_clue += layers*per_layer
    retrieval = c*index_count*(2*d)
    candidate_init = sum((2*raw[a['length']] + softmax(raw[a['length']])
                          + raw[a['length']]*special) for a in p['entries'])
    var_init = sum(unique[a['length']] + 2*log_softmax(unique[a['length']]) for a in p['entries'])
    cell_init = cells*26*(1+special)
    var_message = 0
    var_sync = 0
    for a in p['entries']:
        length = a['length']; n = unique[length]
        var_message += length*(n + softmax(n) + 26*n + 26*(n-1) + 26
                               + 1 + 52 + 26 + 26*special)
        # Python sum starts at zero; NumPy executes the initial zero-array addition too.
        var_sync += (length+1)*n + log_softmax(n)
    cell_sync = cells*(2*26 + log_softmax(26))
    greedy = 2*sum(unique[a['length']] + 1 + special for a in p['entries'])
    # DPR defaults to 6,000 clues per batch; the sample is one batch. The Python
    # attention scale sqrt is computed once per layer per batch, not per clue.
    bert_scalar = c*bert_scalar_per_clue + ((c+5999)//6000)*layers*special
    parts = {'bert_matrix': c*bert_matrix_per_clue, 'bert_scalar': bert_scalar,
             'flat_retrieval': retrieval, 'candidate_score_normalization': candidate_init,
             'bp_initialization': var_init+cell_init, 'bp_variable_messages': iterations*var_message,
             'bp_variable_normalization': iterations*var_sync, 'bp_cell_normalization': iterations*cell_sync,
             'two_greedy_decodes': greedy}
    return {'components_flops': parts, 'total_flops': sum(parts.values()),
            'bp_iterations': iterations, 'special_function_cost': special}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', required=True, type=pathlib.Path)
    parser.add_argument('--output', required=True, type=pathlib.Path)
    args = parser.parse_args(); s = args.sources.resolve(); o = args.output.resolve()
    if o.exists() or o == s or s in o.parents:
        raise SystemExit('Output must be new and outside the source tree')
    meta = checkpoint_metadata(s/'dpr-checkpoint-prefix.bin')
    p = puzzle(s/'master/solver/Mar2321.puz')
    index_count, raw, unique = domains(s/'wordlist.tsv')
    assert index_count < 500000
    for a in p['entries']:
        a['raw_length_candidates'] = raw[a['length']]
        a['unique_length_candidates'] = unique[a['length']]
    cfg = json.loads((s/'bert-base-config.json').read_text())
    assert (cfg['hidden_size'], cfg['intermediate_size'], cfg['num_hidden_layers'],
            cfg['num_attention_heads'], cfg['vocab_size']) == (768, 3072, 12, 12, 30522)
    code = (s/'master/solver/BPSolver.py').read_text()
    assert 'batch_size=6000' in (s/'master/models.py').read_text()
    assert code.index('if iterative_improvement_steps < 1:') < code.index('self.reranker, self.tokenizer =')
    assert 'num_iters=10' in code
    c = operations(p, cfg, meta['sequence_length'], raw, unique, index_count)
    d = cfg['hidden_size']; f = cfg['intermediate_size']
    params = (cfg['vocab_size']+cfg['max_position_embeddings']+cfg['type_vocab_size'])*d + 2*d
    params += cfg['num_hidden_layers']*(4*d*d+2*d*f+9*d+f)
    params += d*d+d  # pooler computes before the wrapper discards its output
    human_html = (s/'amy-2021-03-23.html').read_text()
    text = html.unescape(re.sub(r'<[^>]*>', ' ', human_html))
    assert re.search(r'NYT\s+4:00\s+\(Amy\)', text)
    release = json.loads((s/'hf-model-commits.json').read_text())
    release_date = next(x['date'][:10] for x in release if x['id'] == '9d9f8b8173a41c36aa1032cdaa8eda45d58a937a')
    out = {'point_id': 'crossword-nyt-2021-03-23-berkeley-bp', 'puzzle': p,
           'checkpoint': meta, 'answer_index_entries': index_count,
           'model_encoder_parameters': params, 'model_release_date': release_date,
           'tokens': p['clues']*meta['sequence_length'], 'tokens_accounting': 'encoder_processed',
           'central': c, 'human_time_seconds': 4*60, 'human_attempts': 1,
           'sensitivity': {
               'special_functions_twenty_flops': operations(p,cfg,32,raw,unique,index_count,special=20),
               'five_bp_iterations': operations(p,cfg,32,raw,unique,index_count,iterations=5),
               'twenty_bp_iterations': operations(p,cfg,32,raw,unique,index_count,iterations=20)},
           'source_sha256': {str(f.relative_to(s)): hashlib.sha256(f.read_bytes()).hexdigest()
                             for f in sorted(s.rglob('*')) if f.is_file()}}
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({k: out[k] for k in ['point_id','answer_index_entries','model_encoder_parameters',
                                         'model_release_date','tokens','central','human_time_seconds']},indent=2))


if __name__ == '__main__':
    main()
