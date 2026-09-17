"""Instrument a fresh original Tesseract 5.5.1 source tree.

Usage: python3 instrument.py ENGINE_SOURCE_DIR
Counters measure logical neural arithmetic, independent of fused instructions.
Build without OpenMP: counters are intentionally single-threaded.
"""
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('engine_source_dir', type=Path)
args = parser.parse_args()
p = args.engine_source_dir / 'src/lstm'
files = {n: (p / n).read_text() for n in ['weightmatrix.cpp','functions.h','lstm.cpp','fullyconnected.cpp','lstmrecognizer.cpp']}
assert all('DATASET_' not in s for s in files.values()), 'Start from unmodified original source'

def replace(name, old, new, count=1):
    assert old in files[name], (name,old)
    files[name] = files[name].replace(old,new,count)

header = r'''#ifndef DATASET_AUDIT_H
#define DATASET_AUDIT_H
#include <cstdio>
namespace tesseract {
struct DatasetNeuralAudit {
  unsigned long long dot_mac=0,bias_add=0,peep_mac=0,matrix_calls=0;
  unsigned long long tanh_calls=0,logistic_calls=0,nonlinear_arithmetic=0;
  unsigned long long vector_arithmetic=0,softmax_arithmetic=0,exp_calls=0;
  unsigned long long hidden_state_positions=0,lstm_timesteps=0,lstm_2d_timesteps=0;
  unsigned long long fc_positions[64]={0};
  ~DatasetNeuralAudit() {
    fprintf(stderr,"DATASET_OPS dot_mac=%llu bias_add=%llu peep_mac=%llu calls=%llu\n",dot_mac,bias_add,peep_mac,matrix_calls);
    fprintf(stderr,"DATASET_EXTRA tanh_calls=%llu logistic_calls=%llu nonlinear_arithmetic=%llu vector_arithmetic=%llu softmax_arithmetic=%llu exp_calls=%llu hidden_state_positions=%llu lstm_timesteps=%llu lstm_2d_timesteps=%llu\n",tanh_calls,logistic_calls,nonlinear_arithmetic,vector_arithmetic,softmax_arithmetic,exp_calls,hidden_state_positions,lstm_timesteps,lstm_2d_timesteps);
    for (int i=0;i<64;++i) if(fc_positions[i]) fprintf(stderr,"DATASET_FC type=%d positions=%llu\n",i,fc_positions[i]);
  }
};
extern DatasetNeuralAudit dataset_neural_audit;
}
#endif
'''
(p / 'dataset_audit.h').write_text(header)
for name in files:
    # Include inside the file before its namespace, not inside that namespace.
    replace(name, 'namespace tesseract {', '#include "dataset_audit.h"\n\nnamespace tesseract {')
replace('weightmatrix.cpp','namespace tesseract {','namespace tesseract {\nDatasetNeuralAudit dataset_neural_audit;')
replace('weightmatrix.cpp','int extent = w.dim2() - add_bias_fwd;', 'int extent = w.dim2() - add_bias_fwd;\n  dataset_neural_audit.dot_mac += static_cast<unsigned long long>(num_results)*extent;\n  dataset_neural_audit.bias_add += static_cast<unsigned long long>(num_results)*add_bias_fwd;\n  ++dataset_neural_audit.matrix_calls;')
replace('weightmatrix.cpp','int n = wf_.dim2();\n  const TFloat *u','int n = wf_.dim2();\n  dataset_neural_audit.peep_mac += n;\n  const TFloat *u')
replace('functions.h','inline TFloat Tanh(TFloat x) {','inline TFloat Tanh(TFloat x) {\n  ++dataset_neural_audit.tanh_calls;')
replace('functions.h','return -Tanh(-x);','dataset_neural_audit.nonlinear_arithmetic += 2;\n    return -Tanh(-x);')
replace('functions.h','inline TFloat Logistic(TFloat x) {','inline TFloat Logistic(TFloat x) {\n  ++dataset_neural_audit.logistic_calls;')
replace('functions.h','return 1 - Logistic(-x);','dataset_neural_audit.nonlinear_arithmetic += 2;\n    return 1 - Logistic(-x);')
replace('functions.h','x *= kScaleFactor;','++dataset_neural_audit.nonlinear_arithmetic;\n  x *= kScaleFactor;',count=2)
replace('functions.h','// Linear interpolation.','// Linear interpolation.\n  dataset_neural_audit.nonlinear_arithmetic += 4;',count=2)
replace('functions.h','inline void FuncMultiply(const TFloat *u, const TFloat *v, int n, TFloat *out) {','inline void FuncMultiply(const TFloat *u, const TFloat *v, int n, TFloat *out) {\n  dataset_neural_audit.vector_arithmetic += n;')
replace('functions.h','T prob = inout[i] - max_output;', '++dataset_neural_audit.softmax_arithmetic;\n    T prob = inout[i] - max_output;')
replace('functions.h','prob = std::exp(', '++dataset_neural_audit.exp_calls;\n    prob = std::exp(')
replace('functions.h','prob_total += prob;', '++dataset_neural_audit.softmax_arithmetic;\n    prob_total += prob;')
replace('functions.h','inout[i] /= prob_total;', '++dataset_neural_audit.softmax_arithmetic;\n      inout[i] /= prob_total;')
replace('functions.h','inline void AccumulateVector(int n, const TFloat *src, TFloat *dest) {','inline void AccumulateVector(int n, const TFloat *src, TFloat *dest) {\n  dataset_neural_audit.vector_arithmetic += n;')
replace('functions.h','inline void MultiplyVectorsInPlace(int n, const TFloat *src, TFloat *inout) {','inline void MultiplyVectorsInPlace(int n, const TFloat *src, TFloat *inout) {\n  dataset_neural_audit.vector_arithmetic += n;')
replace('functions.h','inline void MultiplyAccumulate(int n, const TFloat *u, const TFloat *v, TFloat *out) {','inline void MultiplyAccumulate(int n, const TFloat *u, const TFloat *v, TFloat *out) {\n  dataset_neural_audit.vector_arithmetic += 2ULL*n;')
replace('lstm.cpp','// True if there is a valid old state for the 2nd dimension.','dataset_neural_audit.hidden_state_positions += ns_;\n    ++dataset_neural_audit.lstm_timesteps;\n    if (Is2D()) ++dataset_neural_audit.lstm_2d_timesteps;\n    // True if there is a valid old state for the 2nd dimension.')
replace('lstm.cpp','curr_state[i] = temp_lines[GFS][i] * stepped_state[i];','++dataset_neural_audit.vector_arithmetic;\n            curr_state[i] = temp_lines[GFS][i] * stepped_state[i];')
replace('fullyconnected.cpp','void FullyConnected::ForwardTimeStep(int t, TFloat *output_line) {','void FullyConnected::ForwardTimeStep(int t, TFloat *output_line) {\n  dataset_neural_audit.fc_positions[type_] += no_;')
replace('lstmrecognizer.cpp','network_->SetRandomizer(&randomizer_);','tprintf("DATASET_MODEL weights=%d\\n", network_->num_weights());\n  network_->SetRandomizer(&randomizer_);')
for name, text in files.items(): (p / name).write_text(text)
print('Instrumented',args.engine_source_dir)
