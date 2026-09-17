"""Extract original CUPS data with a restricted pandas/numpy pickle reader.

Dependencies: pandas and numpy. Accepts explicit original --source pickle and a
new --output JSON outside the source directory. No study/client code is executed.
"""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import pickle


ALLOWED = {
    'pandas.core.frame.DataFrame', 'pandas.core.internals.managers.BlockManager',
    'pandas._libs.internals._unpickle_block', 'numpy.core.multiarray._reconstruct',
    'numpy.ndarray', 'numpy.dtype', 'builtins.slice',
    'pandas.core.indexes.base._new_Index', 'pandas.core.indexes.base.Index',
    'pandas.core.indexes.range.RangeIndex',
}


class Reader(pickle.Unpickler):
    def find_class(self, module, name):
        if module + '.' + name not in ALLOWED:
            raise ValueError('Unexpected pickle global: ' + module + '.' + name)
        return getattr(importlib.import_module(module), name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    if output.exists() or output == source or source.parent in output.parents:
        parser.error('output must be new and outside source evidence')
    data = source.read_bytes()
    git_blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    assert git_blob == 'a0ec747fd7f74c79206b937f786c9690bb5816d6'
    with source.open('rb') as stream:
        sessions = Reader(stream).load()
    rows = []
    for session_index, frame in enumerate(sessions):
        session = []
        for index, record in enumerate(frame.to_dict(orient='records')):
            record['session_index'] = session_index
            record['event_index'] = index
            session.append(record)
        rows.append(session)
    result = {'original_pickle_sha256': hashlib.sha256(data).hexdigest(),
              'original_git_blob': git_blob, 'sessions': rows}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    print(json.dumps({'sessions': len(rows), 'events': sum(map(len, rows)), 'source_git_blob_verified': True}))


if __name__ == '__main__':
    main()
