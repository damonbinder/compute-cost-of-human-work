"""Recalculate logical OCR FLOPs and transcription equality from retained evidence.

Usage: python3 calculate.py SOURCE_DIR AUDIT_LOG TRANSCRIPT NEW_OUTPUT_JSON
Standard library only. Inputs are read-only; output must not already exist.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source_dir', type=Path)
parser.add_argument('audit_log', type=Path)
parser.add_argument('transcript', type=Path)
parser.add_argument('output_json', type=Path)
a = parser.parse_args()
log = a.audit_log.read_text()
assert 'read_params_file:' not in log
counters = {}
fc = {}
for line in log.splitlines():
    fields = {k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',line)}
    if line.startswith('DATASET_FC '): fc[fields['type']] = fields['positions']
    elif line.startswith('DATASET_'): counters.update(fields)
assert counters['vector_arithmetic'] == 4 * counters['hidden_state_positions']
assert counters['lstm_2d_timesteps'] == 0
assert counters['softmax_arithmetic'] == 3 * counters['exp_calls']
assert fc[22] == counters['exp_calls']
assert counters['bias_add'] == 4 * counters['hidden_state_positions'] + sum(fc.values())
components = {
    'matrix_multiply_add': 2 * counters['dot_mac'],
    'bias_add': counters['bias_add'],
    'peephole_multiply_add': 2 * counters['peep_mac'],
    'nonlinear_lookup_arithmetic': counters['nonlinear_arithmetic'],
    'recurrent_elementwise_arithmetic': counters['vector_arithmetic'],
    'softmax_arithmetic': counters['softmax_arithmetic'],
    'softmax_exp_one_operation_each': counters['exp_calls'],
}
gold = (a.source_dir/'phototest.gold.txt').read_text()
output = a.transcript.read_text()
assert output == gold
normalized = ' '.join(gold.split())
# Verify the original source image and gold bytes against retained GitHub objects.
tree = {r['path']:r for r in json.loads((a.source_dir/'test-tree.json').read_text())['tree']}
verified = {}
for name in ['phototest.tif','phototest.gold.txt']:
    blob = (a.source_dir/name).read_bytes()
    git = hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()
    assert git == tree['testing/'+name]['sha']
    verified[name] = {'git_blob':git,'sha256':hashlib.sha256(blob).hexdigest()}
full = sum(components.values())
matrix_bias = sum(components[k] for k in ['matrix_multiply_add','bias_add','peephole_multiply_add'])
result = {
    'logical_flops': full,
    'components': components,
    'matrix_bias_only_flops': matrix_bias,
    'extra_arithmetic_fraction_of_matrix_bias': (full-matrix_bias)/matrix_bias,
    'exp_100_operations_sensitivity_flops': full + 99*counters['exp_calls'],
    'counters': counters,
    'fully_connected_output_positions_by_type':fc,
    'raw_characters':len(gold),
    'normalized_characters':len(normalized),
    'words':len(normalized.split()),
    'exact_raw_transcription':True,
    'normalized_character_errors':0,
    'source_files_verified':verified,
    'scope':'Neural network arithmetic, two operations per multiply-add; exp counts once. Excludes comparisons, indexing, copies, integer bookkeeping, classical page analysis and beam decoding.'
}
with a.output_json.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
