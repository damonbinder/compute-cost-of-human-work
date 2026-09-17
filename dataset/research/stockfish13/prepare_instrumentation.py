"""Prepare original and NNUE-counting Stockfish 13 trees without changing evidence.

Python standard library only. Build each src directory with:
make -j2 build COMP=clang ARCH=apple-silicon
Instrumentation requires single-thread NEON execution. The replay of saved counts
is platform-independent; generating new observations requires a compatible engine.
"""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import zipfile


HEADER = r'''// Dataset instrumentation; Stockfish 13 source remains GPL-3.0-or-later.
#ifndef DATASET_NNUE_COUNTERS_H
#define DATASET_NNUE_COUNTERS_H
#include <cstdint>
#include <sstream>
#if !defined(USE_NEON)
#error "This operation counter requires the inspected NEON implementation."
#endif
namespace DatasetNNUE {
struct Counters {
  std::uint64_t evaluations = 0, affine_calls = 0;
  std::uint64_t affine_multiplies = 0, affine_additions = 0;
  std::uint64_t refreshes = 0, incremental_updates = 0, cache_hits = 0;
  std::uint64_t feature_additions = 0, feature_subtractions = 0;
  std::uint64_t clipped_values = 0, activation_shifts = 0, output_divisions = 0;
};
inline Counters count;
inline void reset() { count = Counters{}; }
inline std::string json(std::uint64_t search_nodes) {
  std::ostringstream s;
  s << "{\"search_nodes\":" << search_nodes << ",";
#define FIELD(name) s << "\"" #name "\":" << count.name << ",";
  FIELD(evaluations) FIELD(affine_calls) FIELD(affine_multiplies) FIELD(affine_additions)
  FIELD(refreshes) FIELD(incremental_updates) FIELD(cache_hits)
  FIELD(feature_additions) FIELD(feature_subtractions)
  FIELD(clipped_values) FIELD(activation_shifts)
#undef FIELD
  s << "\"output_divisions\":" << count.output_divisions << "}";
  return s.str();
}
}
#endif
'''


def replace(path, before, after, count=1):
    text = path.read_text()
    assert text.count(before) == count, (path, before[:80], text.count(before))
    path.write_text(text.replace(before, after))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive', required=True, type=Path)
    p.add_argument('--net', required=True, type=Path)
    p.add_argument('--workdir', required=True, type=Path)
    a = p.parse_args()
    archive, net, work = a.archive.resolve(), a.net.resolve(), a.workdir.resolve()
    if work.exists() or work in [archive, net] or any(source.parent == work or source.parent in work.parents for source in [archive, net]):
        p.error('workdir must be new and outside the source evidence directories')
    assert hashlib.sha256(net.read_bytes()).hexdigest() == '62ef826d1a6d11b9e814188025aa02a60815c037292e0ef9bbb9bf4f724e5e63'
    work.mkdir(parents=True)
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            assert not item.filename.startswith('/') and '..' not in Path(item.filename).parts
        z.extractall(work / 'unpacked')
    original = next((work / 'unpacked').iterdir())
    for name in ['baseline', 'instrumented']:
        shutil.copytree(original, work / name)
        src = work / name / 'src'
        replace(src / 'Makefile', '-fexperimental-new-pass-manager', '')
        shutil.copy2(net, src / net.name)
    src = work / 'instrumented/src'
    (src / 'nnue/dataset_counters.h').write_text(HEADER)
    replace(src / 'nnue/evaluate_nnue.cpp', '#include "evaluate_nnue.h"', '#include "evaluate_nnue.h"\n#include "dataset_counters.h"')
    replace(src / 'nnue/evaluate_nnue.cpp', '  Value evaluate(const Position& pos) {',
            '  Value evaluate(const Position& pos) {\n    ++DatasetNNUE::count.evaluations;\n    ++DatasetNNUE::count.output_divisions;')
    replace(src / 'nnue/layers/affine_transform.h', '#include "../nnue_common.h"', '#include "../nnue_common.h"\n#include "../dataset_counters.h"')
    target = '      const auto input = previous_layer_.Propagate(\n          transformed_features, buffer + kSelfBufferSize);'
    replace(src / 'nnue/layers/affine_transform.h', target, target + '''
      ++DatasetNNUE::count.affine_calls;
      DatasetNNUE::count.affine_multiplies += std::uint64_t(kPaddedInputDimensions) * kOutputDimensions;
      // NEON: N products, N additions in pairwise/accumulate operations,
      // then three scalar additions reducing four lanes for each output.
      DatasetNNUE::count.affine_additions += std::uint64_t(kPaddedInputDimensions + 3) * kOutputDimensions;
''')
    replace(src / 'nnue/layers/clipped_relu.h', '#include "../nnue_common.h"', '#include "../nnue_common.h"\n#include "../dataset_counters.h"')
    replace(src / 'nnue/layers/clipped_relu.h', target, target + '''
      DatasetNNUE::count.clipped_values += kInputDimensions;
      DatasetNNUE::count.activation_shifts += kInputDimensions;
''')
    f = src / 'nnue/nnue_feature_transformer.h'
    replace(f, '#include "nnue_common.h"', '#include "nnue_common.h"\n#include "dataset_counters.h"')
    replace(f, '    void Transform(const Position& pos, OutputType* output) const {',
            '    void Transform(const Position& pos, OutputType* output) const {\n      DatasetNNUE::count.clipped_values += kOutputDimensions;')
    replace(f, '        if (next == nullptr)\n          return;', '''        if (next == nullptr)
        {
          ++DatasetNNUE::count.cache_hits;
          return;
        }''')
    marker = '          { next, next == pos.state() ? nullptr : pos.state(), nullptr };'
    replace(f, marker, marker + '''
        // Count each actual accumulator update once, before SIMD tiling.
        for (IndexType i = 0; info[i]; ++i)
        {
          ++DatasetNNUE::count.incremental_updates;
          DatasetNNUE::count.feature_subtractions += std::uint64_t(removed[i].size()) * kHalfDimensions;
          DatasetNNUE::count.feature_additions += std::uint64_t(added[i].size()) * kHalfDimensions;
        }
''')
    marker = '        Features::HalfKP<Features::Side::kFriend>::AppendActiveIndices(pos, c, &active);'
    replace(f, marker, marker + '''
        ++DatasetNNUE::count.refreshes;
        DatasetNNUE::count.feature_additions += std::uint64_t(active.size()) * kHalfDimensions;
''')
    f = src / 'search.cpp'
    replace(f, '#include "evaluate.h"', '#include "evaluate.h"\n#include "nnue/dataset_counters.h"')
    replace(f, 'void MainThread::search() {', '''void MainThread::search() {
  if (Threads.size() != 1) { std::cerr << "Counter requires Threads=1" << std::endl; std::exit(2); }
  DatasetNNUE::reset();''')
    marker = '  sync_cout << "bestmove " << UCI::move(bestThread->rootMoves[0].pv[0], rootPos.is_chess960());'
    replace(f, marker, '  sync_cout << "info string neural_counters " << DatasetNNUE::json(Threads.nodes_searched()) << sync_endl;\n' + marker)
    patch = []
    for f in sorted(src.rglob('*')):
        if not f.is_file() or f.name.endswith('.nnue'):
            continue
        relative = f.relative_to(src)
        old = work / 'baseline/src' / relative
        before = old.read_text() if old.exists() else ''
        after = f.read_text()
        if before != after:
            patch.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                             fromfile='a/src/' + str(relative), tofile='b/src/' + str(relative)))
    (work / 'instrumentation.patch').write_text(''.join(patch))
    manifest = {'source_archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
                'net_sha256': hashlib.sha256(net.read_bytes()).hexdigest(),
                'compatibility_change': 'Remove obsolete clang -fexperimental-new-pass-manager option only.',
                'instrumentation_patch_sha256': hashlib.sha256((work / 'instrumentation.patch').read_bytes()).hexdigest()}
    (work / 'preparation.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
