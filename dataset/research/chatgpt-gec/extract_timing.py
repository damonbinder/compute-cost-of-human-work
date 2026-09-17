"""Extract published PEET timing records; permit only inspected data constructors."""
import importlib
import json
import pickle
from pathlib import Path

ALLOWED = {
    ('pandas.core.frame', 'DataFrame'),
    ('pandas.core.internals.managers', 'BlockManager'),
    ('pandas._libs.internals', '_unpickle_block'),
    ('numpy.core.numeric', '_frombuffer'),
    ('numpy', 'dtype'),
    ('builtins', 'slice'),
    ('numpy.core.multiarray', '_reconstruct'),
    ('numpy', 'ndarray'),
    ('pandas.core.indexes.base', '_new_Index'),
    ('pandas.core.indexes.base', 'Index'),
    ('pandas.core.indexes.range', 'RangeIndex'),
}

class DataOnly(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) not in ALLOWED:
            raise ValueError(f'Unapproved constructor: {module}.{name}')
        return getattr(importlib.import_module(module), name)


import argparse,hashlib
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.exists() or a.source.resolve().parent in a.output.resolve().parents:p.error('new output outside sources required')
with a.source.open('rb') as stream: frame=DataOnly(stream).load()
r=frame[frame['ID']=='C14_17_S'][['ID','SRC','TRG','Time','NumWordsS','use250','use_MO_TRG','time_avg_MO_TRG']].to_dict('records')
assert len(r)==1
out={'original_sha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'records':r}
a.output.write_text(json.dumps(out,indent=2,default=str)+'\n')
