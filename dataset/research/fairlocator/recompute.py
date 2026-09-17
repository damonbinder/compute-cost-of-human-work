#!/usr/bin/env python3
"""FairLocator analytic estimate. Requires Python 3, tiktoken, openpyxl, pypdf.

Usage: python recompute.py SOURCE_DIR NEW_OUTPUT_DIR [--assumptions FILE]
Does not query models, download data, or modify retained evidence.
"""
import argparse
import ast
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import shutil


def literal_assignment(nodes, name):
    return next(ast.literal_eval(n.value) for n in nodes
                if isinstance(n, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == name for t in n.targets))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source_dir', type=Path)
    ap.add_argument('output_dir', type=Path)
    ap.add_argument('--assumptions', type=Path,
                    default=Path(__file__).with_name('assumptions.json'))
    args = ap.parse_args()
    src, out = args.source_dir.resolve(), args.output_dir.resolve()
    if out.exists() or out == src or src in out.parents:
        raise SystemExit('Output must be new and outside source directory')
    manifest = json.loads((src / 'manifest.json').read_text())
    for row in manifest:
        assert hashlib.sha256((src / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    a = json.loads(args.assumptions.read_text())
    out.mkdir(parents=True)
    cache = out / 'tokenizer-cache'
    cache.mkdir()
    url = 'https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken'
    shutil.copyfile(src / 'o200k_base.tiktoken', cache / hashlib.sha1(url.encode()).hexdigest())
    os.environ['TIKTOKEN_CACHE_DIR'] = str(cache)
    import tiktoken
    import openpyxl
    from pypdf import PdfReader
    enc = tiktoken.get_encoding('o200k_base')

    raw_code = (src / 'Query.py').read_text()
    tree = ast.parse(raw_code)
    prefix = literal_assignment(tree.body, 'Prefix')
    extract = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'GPT4oExtract')
    magic = literal_assignment(extract.body, 'magic')
    primary = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'GPT4o')
    assert a['primary_model_id'] in ast.unparse(primary)
    assert a['helper_model_id'] in ast.unparse(extract)
    assert ast.unparse(primary).count("'type': 'image_url'") == 1
    assert 'if time == 3:' in raw_code
    assert 'GPT4oExtract(QuestionID, content, unknown_id)' in raw_code
    raw_prompt_tokens = len(enc.encode(prefix))
    raw_helper_tokens = len(enc.encode(magic))
    prompt = raw_prompt_tokens + a['message_allowance_tokens_per_call']
    helper_instruction = raw_helper_tokens + a['message_allowance_tokens_per_call']

    ws = openpyxl.load_workbook(src / 'SourceData/Human.xlsx', read_only=True, data_only=True).active
    values = list(ws.values)
    assert values[0] == ('ID', 'continent', 'country', 'city', 'Questionnaire', 'QuestionID')
    items = [dict(zip(values[0], r)) for r in values[1:] if isinstance(r[0], (int, float))]
    assert len(items) == 100
    assert sorted(int(r['ID']) for r in items) == list(range(1, 101))
    assert sorted(Counter(r['Questionnaire'] for r in items).values()) == [10] * 10
    assert [r[0] for r in values[1:] if not isinstance(r[0], (int, float))] == ['Result']
    # Illustrative four-field outputs using actual country/city labels and an
    # explicitly invented street placeholder: a format-length check, not responses.
    helper_proxies = []
    for item in items:
        text = '```json\n' + json.dumps({'continent': item['continent'], 'Country': item['country'],
                           'City': item['city'], 'Street': 'Main Street'}, ensure_ascii=False, indent=2) + '\n```'
        helper_proxies.append({'ID': item['ID'], 'tokens': len(enc.encode(text)), 'text': text})

    pdf = PdfReader(src / 'final-paper.pdf')
    assert len(pdf.pages) == 21
    dims = [{'page': 20, 'name': im.name, 'size': list(im.image.size)} for im in pdf.pages[19].images]
    assert len(dims) == 4 and all(r['size'] == [640, 537] for r in dims)
    w, h = dims[0]['size']
    tiles = math.ceil(w / 512) * math.ceil(h / 512)
    views = tiles + 1  # four high-resolution tiles plus one global view
    cfg = json.loads((src / 'clip-bigG.json').read_text())['vision_cfg']
    d, layers, patch = cfg['width'], cfg['layers'], cfg['patch_size']
    hidden = int(d * cfg['mlp_ratio'])
    patches = (cfg['image_size'] // patch) ** 2
    n = patches + 1
    assert (d, layers, hidden, patches) == (1664, 48, 8192, 256)
    frontend_components = {
        'patch_projection': 2 * patches * (patch * patch * 3) * d,
        'qkv_and_output_projections': layers * 8 * n * d * d,
        'feedforward_projections': layers * 4 * n * d * hidden,
        'attention_matrix_products': layers * 4 * n * n * d,
    }
    frontend_per_view = sum(frontend_components.values())

    def cost(output=None, helper_output=None, p=None, max_pairs=None, crops=None,
             params=None, visual_positions=None, primary_prompt=None):
        output = a['primary_output_tokens'] if output is None else output
        helper_output = a['helper_output_tokens'] if helper_output is None else helper_output
        p = a['invalid_pair_probability'] if p is None else p
        max_pairs = a['maximum_pairs'] if max_pairs is None else max_pairs
        crops = views if crops is None else crops
        params = a['active_parameters'] if params is None else params
        v = a['visual_patch_positions_per_view'] if visual_positions is None else visual_positions
        main_prompt = prompt if primary_prompt is None else primary_prompt
        expected_pairs = sum(p ** k for k in range(max_pairs))
        text_primary = main_prompt + output
        text_helper = helper_instruction + output + helper_output
        visual = crops * v
        backbone_primary = 2 * params * (text_primary + visual)
        backbone_helper = 2 * params * text_helper
        frontend = crops * frontend_per_view
        f = expected_pairs * (backbone_primary + backbone_helper + frontend)
        return {
            'compute_flops': f,
            'text_tokens': expected_pairs * (text_primary + text_helper),
            'expected_pairs': expected_pairs,
            'primary_text_input_per_pair': main_prompt,
            'primary_text_output_per_pair': output,
            'helper_text_input_per_pair': helper_instruction + output,
            'helper_text_output_per_pair': helper_output,
            'visual_positions_per_pair': visual,
            'visual_positions_including_retries': expected_pairs * visual,
            'primary_backbone_flops': expected_pairs * backbone_primary,
            'helper_backbone_flops': expected_pairs * backbone_helper,
            'frontend_flops': expected_pairs * frontend,
        }

    central = cost()
    scenarios = {
        'primary_output_200': cost(output=200),
        'primary_output_800': cost(output=800),
        'helper_output_35': cost(helper_output=35),
        'helper_output_80': cost(helper_output=80),
        'no_invalid_retries': cost(p=0),
        'invalid_rate_20_percent': cost(p=.2),
        'source_code_three_pair_cap': cost(max_pairs=3),
        'low_detail_single_view': cost(crops=1),
        'seven_views_if_enlarged_requested_936_by_537': cost(crops=7),
        'visual_positions_64_per_view': cost(visual_positions=64),
        'visual_positions_576_per_view': cost(visual_positions=576),
        'active_parameters_25b': cost(params=25_000_000_000),
        'active_parameters_100b': cost(params=100_000_000_000),
    }
    for scenario in scenarios.values():
        scenario['ratio_to_central'] = scenario['compute_flops'] / central['compute_flops']
    result = {
        'point_id': 'perc-geolocation-fairlocator-gpt4o',
        'assumptions': a,
        'source_defined_images': len(items),
        'questionnaires': dict(Counter(str(r['Questionnaire']) for r in items)),
        'protocol_individual_judgments_per_side': 300,
        'native_timing_or_response_records': 0,
        'literal_prompt_tokens': {'primary': raw_prompt_tokens, 'helper': raw_helper_tokens},
        'format_only_helper_proxy_token_mean': sum(r['tokens'] for r in helper_proxies) / len(items),
        'format_only_helper_proxy_token_min': min(r['tokens'] for r in helper_proxies),
        'format_only_helper_proxy_token_max': max(r['tokens'] for r in helper_proxies),
        'source_illustration_images': dims,
        'central_high_detail_tiles': tiles,
        'central_total_visual_views': views,
        'visual_billing_units_reference_only': 85 + 170 * tiles,
        'frontend_parameters': dict(width=d, hidden=hidden, layers=layers, patch=patch, n=n),
        'frontend_flops_per_view': frontend_per_view,
        'frontend_components_per_view': frontend_components,
        'central': central,
        'human_seconds': sum(a['human_seconds'].values()),
        'human_ten_question_form_seconds': sum(a['human_seconds'].values()) * 10,
        'reported_performance_percent': {
            'gpt4o': {'continent': 86.0, 'country': 74.0, 'city': 63.3},
            'human': {'continent': 33.7, 'country': 9.5, 'city': 1.7},
        },
        'scenarios': scenarios,
    }
    (out / 'calculations.json').write_text(json.dumps(result, indent=2) + '\n')
    (out / 'prompts.json').write_text(json.dumps({'primary': prefix, 'helper': magic}, indent=2) + '\n')
    (out / 'human-items.json').write_text(json.dumps(items, indent=2) + '\n')
    (out / 'format-only-helper-proxies.json').write_text(json.dumps(helper_proxies, indent=2) + '\n')
    print(json.dumps({'compute_flops': central['compute_flops'],
                      'tokens': central['text_tokens'], 'human_seconds': result['human_seconds']}))


if __name__ == '__main__':
    main()
