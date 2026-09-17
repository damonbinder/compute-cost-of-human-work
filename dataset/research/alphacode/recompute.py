#!/usr/bin/env python3
"""AlphaCode inference reconstruction; Python3 + pyarrow. No network/model calls."""
import argparse
import hashlib
import json
import random
import re
import statistics
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq


def model_work(model, encoder_positions, decoder_positions):
    """Dense neural matrix arithmetic, MAC=2, cached autoregressive decoder."""
    d = model['d_model']
    k = model['kv_heads'] * model['head_size']
    ne, nd = model['encoder_blocks'], model['decoder_blocks']
    e, t = encoder_positions, decoder_positions
    enc_weights = ne * (14 * d * d + 2 * d * k)
    dec_weights = nd * (16 * d * d + 4 * d * k)
    terms = {
        'encoder_projections': 2 * e * enc_weights,
        'encoder_attention': 4 * ne * e * e * d,
        'decoder_cross_kv_once': 2 * e * nd * 2 * d * k,
        'decoder_projections': 2 * t * nd * (16 * d * d + 2 * d * k),
        'decoder_self_attention': 2 * nd * d * t * (t + 1),
        'decoder_cross_attention': 4 * nd * d * e * t,
        'vocabulary_projection': 2 * t * d * 8000,
    }
    return dict(encoder_projection_weights=enc_weights,
                decoder_projection_weights=dec_weights,
                terms=terms, total=sum(terms.values()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--human-assumptions', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    s, o = args.sources.resolve(), args.output.resolve()
    if o.exists() or o == s or s in o.parents:
        raise SystemExit('Output must be a new path outside the source directory')
    for f in json.loads((s / 'manifest.json').read_text()):
        assert hashlib.sha256((s / f['path']).read_bytes()).hexdigest() == f['sha256'], f['path']
    x = json.loads((s / 'reported-inputs.json').read_text())
    rows = pq.read_table(s / 'valid.parquet').to_pylist()
    assert len(rows) == x['validation_problem_count'] == 117
    by_name = {r['name'].strip(): r for r in rows}
    buckets = {low: [r for r in rows if low <= r['cf_rating'] < low + 400]
               for low in range(800, 3501, 400)}
    assert [len(v) for v in buckets.values()] == [29, 18, 20, 19, 15, 8, 8]
    viz = s / 'alphacode_viz' / 'static'
    html = (viz / 'index.html').read_text()
    index = json.loads(re.search(r'const PROBLEMS = (\[.*?\]);', html).group(1))
    assert len(index) == 141
    lengths = []
    for entry in index:
        v = json.loads((viz / 'data' / entry['path'] / 'data.json').read_text())
        assert (v['layers'], v['heads']) == (30, 11), entry
        assert len(v['prompt']) == 1535 and len(v['solution']) == 767
        last = max(i for i, value in enumerate(v['solution']) if value) + 1
        assert all(value for value in v['solution'][:last]), entry
        lengths.append(entry | dict(
            architecture='AlphaCode1B:30 decoder blocks,11 heads',
            prompt_length=v['prompt_length'],
            encoder_array_positions=len(v['prompt']) + 1,
            decoder_array_positions=v['solution_tokens'],
            visible_code_tokens=last,
            # One extra generation step for end-of-code. Blank trailing positions
            # cannot identify EOS vs padding; the resulting 1-position allowance
            # is explicit, not a recovered native token-ID count.
            decoder_steps_with_eos_allowance=min(last + 1, 768),
            in_validation=entry['name'].strip() in by_name,
            randomly_selected_record=entry['path'].isdigit()))
    groups = {}
    for lang in ('cpp', 'python3'):
        for correct in (False, True):
            selected = [r for r in lengths if r['lang'] == lang
                        and bool(r['correct']) == correct
                        and r['in_validation'] and r['randomly_selected_record']]
            groups[f'{lang}_{"pass" if correct else "fail"}'] = dict(
                n=len(selected),
                task_names=sorted({r['name'].strip() for r in selected}),
                mean_decoder_steps=statistics.mean(r['decoder_steps_with_eos_allowance'] for r in selected),
                median_decoder_steps=statistics.median(r['decoder_steps_with_eos_allowance'] for r in selected),
                mean_prompt_positions=statistics.mean(r['prompt_length'] for r in selected))

    def total(e=1536, t=400, encoder_contexts=500000, helper_t=256, helper_model='alphacode-41b'):
        components = {}
        for mid, m in x['models'].items():
            work = model_work(m, e, t)
            terms = work['terms']
            context_work = sum(terms[k] for k in
                               ('encoder_projections', 'encoder_attention', 'decoder_cross_kv_once'))
            decoder_work = work['total'] - context_work
            components[mid] = dict(**work,
                sample_count=500000, distinct_encoder_computations=encoder_contexts,
                aggregate_flops=encoder_contexts * context_work + 500000 * decoder_work)
        h = model_work(x['models'][helper_model], e, helper_t)
        components['test_input_helper'] = dict(assumed_model=helper_model, count=50,
                                              **h, aggregate_flops=50 * h['total'])
        return dict(components=components,
                    flops=sum(c['aggregate_flops'] for c in components.values()),
                    decoder_tokens=1000000 * t + 50 * helper_t)

    # Task-informed rounded transfer from native unsuccessful1B examples. These
    # are not native9B/41B pool lengths. Encoder padding and no cross-sample reuse
    # are explicit central assumptions; alternative caching/padding below.
    central = total()
    native_fail_transfer = statistics.mean(groups[f'{l}_fail']['mean_decoder_steps']
                                           for l in ('cpp', 'python3'))
    native_prompt_transfer = statistics.mean(groups[f'{l}_fail']['mean_prompt_positions']
                                             for l in ('cpp', 'python3'))
    scenarios = {
        'decoder200': total(t=200),
        'decoder600': total(t=600),
        'decoder768_including_possible_batch_padding': total(t=768),
        'native1b_fail_length_transfer': total(t=native_fail_transfer),
        'native1b_unpadded_encoder_transfer': total(e=native_prompt_transfer),
        'all2800_metadata_contexts_encoded_once_per_model': total(encoder_contexts=2800),
        'shared_encoder_and_decoder200': total(t=200, encoder_contexts=2800),
        'helper9b128positions': total(helper_t=128, helper_model='alphacode-9b'),
        'helper41b768positions': total(helper_t=768),
    }
    for value in scenarios.values():
        value['relative_to_central'] = value['flops'] / central['flops']

    human = json.loads(args.human_assumptions.read_text())
    estimate_rows = []
    for low, bucket in buckets.items():
        chosen = random.Random(1172022 + low).sample(sorted(bucket, key=lambda r: r['name']), 2)
        names = [r['name'] for r in chosen]
        selected = [r for r in human['items'] if r['name'] in names]
        assert len(selected) == 2
        for r in selected:
            assert r['description'] == by_name[r['name'].strip()]['description']
        estimate_rows.append(dict(bucket=low, population_count=len(bucket),
            inspected_names=names,
            estimated_minutes=statistics.mean(r['estimated_active_minutes'] for r in selected),
            low_minutes=statistics.mean(r['scenario_low_minutes'] for r in selected),
            high_minutes=statistics.mean(r['scenario_high_minutes'] for r in selected)))
    weighted = lambda key: sum(r['population_count'] * r[key] for r in estimate_rows) / 117
    result = dict(
        point_id='reas-codecontests-alphacode-ensemble-1m',
        compute_flops=central['flops'], tokens=central['decoder_tokens'],
        human_time=2100, human_unrounded_weighted_seconds=weighted('estimated_minutes') * 60,
        human_low_seconds=weighted('low_minutes') * 60,
        human_high_seconds=weighted('high_minutes') * 60,
        human_longer_hard_attempts90min_seconds=(weighted('estimated_minutes') + 31 * 30 / 117) * 60,
        validation_count=len(rows), validation_names=sorted(by_name),
        rating_buckets={str(k): len(v) for k, v in buckets.items()},
        visualization_records=lengths, visualization_groups=groups,
        native_fail_mean_steps=native_fail_transfer,
        native_fail_mean_unpadded_prompt=native_prompt_transfer,
        central=central, scenarios=scenarios, human_strata=estimate_rows,
        full117problem_compute=117 * central['flops'],
        full117problem_human_seconds=117 * 2100,
        helper_fraction=central['components']['test_input_helper']['aggregate_flops'] / central['flops'],
    )
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({k: result[k] for k in ('compute_flops', 'tokens', 'human_time',
                                          'human_unrounded_weighted_seconds', 'native_fail_mean_steps',
                                          'helper_fraction')}, indent=2))


if __name__ == '__main__':
    main()
