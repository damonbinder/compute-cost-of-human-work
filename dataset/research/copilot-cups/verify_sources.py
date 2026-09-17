"""Verify retained CUPS source objects and bounded archive members.

Python standard library only. Pass --sources and a new --output JSON outside
that directory. Does not extract or execute any original study code.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sources', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    src, out = a.sources.resolve(), a.output.resolve()
    if out.exists() or out == src or src in out.parents:
        p.error('output must be new and outside source evidence')
    trees = {name: {x['path']: x for x in json.loads((src / name).read_text())['tree']}
             for name in ['tree.json', 'copilot-vim-tree-aug2022.json']}
    git_checks = []
    mappings = [('data_labeled_study.pkl', 'data/data_labeled_study.pkl', 'tree.json'),
                ('copilot-agent-aug2022.js', 'copilot/dist/agent.js', 'copilot-vim-tree-aug2022.json')]
    mappings += [(str(x.relative_to(src)), str(x.relative_to(src / 'repo')), 'tree.json')
                 for x in sorted((src / 'repo').rglob('*')) if x.is_file()]
    mappings += [(str(x.relative_to(src)), str(x.relative_to(src / 'historical-client')), 'copilot-vim-tree-aug2022.json')
                 for x in sorted((src / 'historical-client').rglob('*')) if x.is_file()]
    for local, original, tree in mappings:
        raw = (src / local).read_bytes()
        assert blob(raw) == trees[tree][original]['sha'], local
        git_checks.append({'path': local, 'original_path': original, 'git_blob': blob(raw)})
    raw = (src / 'original-archive-code-logs.zip.part').read_bytes()
    archive_checks = []
    members = {x['name']: x for x in json.loads((src / 'original-archive-members.json').read_text())}
    for local in sorted((src / 'archive').rglob('*')):
        if not local.is_file():
            continue
        member = str(local.relative_to(src / 'archive'))
        item = members[member]
        pos = item['header_offset']
        signature, version, flags, method, tm, dt, crc, compressed_size, size, name_len, extra_len = struct.unpack_from('<IHHHHHIIIHH', raw, pos)
        assert signature == 0x04034B50 and not flags & 1
        assert raw[pos + 30:pos + 30 + name_len].decode() == member
        start = pos + 30 + name_len + extra_len
        payload = raw[start:start + item['compressed_bytes']]
        extracted = zlib.decompress(payload, -15) if method == 8 else payload
        assert method in (0, 8) and extracted == local.read_bytes()
        assert zlib.crc32(extracted) == crc and len(extracted) == item['bytes']
        archive_checks.append({'path': str(local.relative_to(src)), 'zip_offset': pos,
                               'crc32': f'{crc:08x}', 'bytes': len(extracted)})
    result = {'git_objects': git_checks, 'archive_members': archive_checks,
              'git_object_count': len(git_checks), 'archive_member_count': len(archive_checks)}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k.endswith('_count')}))


if __name__ == '__main__':
    main()
