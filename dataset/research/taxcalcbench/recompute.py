#!/usr/bin/env python3
"""Read-only TaxCalcBench reconstruction. Python 3.10+ and tiktoken; no API calls.

Required: --sources DIR --models CSV --assumptions JSON --output NEW_JSON
"""
import argparse
import ast
import base64
import csv
import hashlib
import json
from pathlib import Path
import re
import statistics
import xml.etree.ElementTree as ET
import tiktoken


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def literal(path, name):
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            return ast.literal_eval(node.value)
    raise ValueError(f'Missing literal {name}')


def money(raw):
    try:
        return float(raw.replace('$', '').replace(',', '').strip())
    except ValueError:
        return 0.0


def native_value(text, label):
    if label not in text:
        return 0.0
    tail = text.split(label)[1].split('\n')[0]
    return money(tail.split('|')[-1].strip()) if '|' in tail else 0.0


def grade(text, xml, mapping, report):
    tree = ET.fromstring(xml)
    results = []
    for label, xpath in mapping.items():
        node = tree.find('./' + xpath.removeprefix('/Return/'))
        expected = money(node.text or '') if node is not None else 0.0
        actual = native_value(text, label)
        line = label.split(':')[0]
        # Independent line-number join, tolerating a changed description.
        hits = re.findall(r'^' + re.escape(line) + r':[^\n]*', text, re.MULTILINE)
        assert len(hits) == 1, (line, hits)
        alternative = money(hits[0].split('|')[-1])
        assert alternative == actual, (line, actual, alternative)
        report_hit = re.search(r'^' + re.escape(line) + r': .*?expected: ([^,]+), actual: ([^\n]+)', report, re.MULTILINE)
        assert report_hit and float(report_hit[1]) == expected and float(report_hit[2]) == actual
        results.append({'line': line, 'expected': expected, 'actual': actual, 'correct': actual == expected})
    correct = sum(x['correct'] for x in results)
    lenient = sum(abs(x['actual'] - x['expected']) <= 5 for x in results)
    assert f'Strictly correct return: {correct == len(results)}' in report
    assert f'Correct (by line): {correct / len(results) * 100:.2f}%' in report
    return {'correct_lines': correct, 'scored_lines': len(results), 'strict_success': correct == len(results),
            'within_5_dollars_success': lenient == len(results), 'line_values': results}


def task_arithmetic(data, case, expected):
    fields = data['input']['return_data']
    w2 = fields['w2']
    wages = sum(x['wages']['value'] for x in w2)
    withheld = sum(x['withholding']['value'] for x in w2)
    if case == 'single-w2-balance-due-no-state-income-tax':
        assert fields['irs1040']['filing_status']['value'] == 'single'
        deduction = 14600
        tax_unrounded = (wages - deduction) * 0.24 - 6957.50  # 2024 IRS worksheet, p76 section A
        tax = int(tax_unrounded + 0.5)
        extra = 0
    elif case == 'hoh-multiple-w2-box12-codes':
        assert fields['irs1040']['filing_status']['value'] == 'head_of_household'
        assert fields['irs1040']['hoh_planning_to_claim_child_or_dependent_credit']['value'] is False
        deduction = 21900
        assert wages - deduction == 26000
        tax = 2792  # Original IRS 2024 tax table p67, HOH $26,000–26,050
        tax_unrounded = None
        extra = sum(g['box_12_amount']['value'] for x in w2 for g in x.get('employers_use_grp', []) if g['box_12_code']['value'] in {'A', 'B', 'M', 'N'})
    else:
        raise ValueError(case)
    total = tax + extra
    result = {'w2_count': len(w2), 'wages': wages, 'withholding': withheld, 'standard_deduction': deduction,
              'taxable_income': wages - deduction, 'income_tax_unrounded': tax_unrounded, 'income_tax': tax,
              'schedule2_line13': extra, 'total_tax': total, 'refund': max(0, withheld - total), 'amount_owed': max(0, total - withheld)}
    for name, tag in {'wages':'WagesAmt', 'standard_deduction':'TotalItemizedOrStandardDedAmt','taxable_income':'TaxableIncomeAmt','income_tax':'TaxAmt','total_tax':'TotalTaxAmt','refund':'RefundAmt','amount_owed':'OwedAmt'}.items():
        node = ET.fromstring(expected).find('./ReturnData/IRS1040/' + tag)
        actual = float(node.text) if node is not None else 0
        assert result[name] == actual, (name, result[name], actual)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for n in ('sources', 'models', 'assumptions', 'output'):
        ap.add_argument('--' + n, type=Path, required=True)
    args = ap.parse_args()
    src = args.sources.resolve(); output = args.output.resolve()
    inputs = [args.models.resolve(), args.assumptions.resolve()]
    if output == src or src in output.parents or output in inputs or output.exists():
        raise SystemExit('Output must be a new file outside sources and input files.')
    assumptions = json.loads(args.assumptions.read_text())
    models = {x['model_id']: x for x in csv.DictReader(args.models.open())}
    manifest = json.loads((src / 'selected-original-manifest.json').read_text())
    assert manifest['commit'] == assumptions['repository_commit']
    for rec in manifest['files']:
        file = src / rec['path']; raw = file.read_bytes()
        assert digest(file) == rec['sha256']
        assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == rec['git_blob_sha1']
    root = src / assumptions['source_root']; code = root / 'tax_calc_bench'
    template = literal(code / 'tax_return_generation_prompt.py', 'TAX_RETURN_GENERATION_PROMPT')
    mapping = literal(code / 'tax_return_evaluator.py', 'LINES_TO_XPATH_VALUES')
    ranks_path = src / assumptions['tokenizer_proxy']
    assert digest(ranks_path) == '223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7'
    ranks = {base64.b64decode(x): int(y) for x, y in (line.split() for line in ranks_path.read_bytes().splitlines())}
    enc = tiktoken.Encoding(name='retained_cl100k_proxy', pat_str=r"""'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}++|\p{N}{1,3}+| ?[^\s\p{L}\p{N}]++[\r\n]*+|\s++$|\s*[\r\n]|\s+(?!\S)|\s""", mergeable_ranks=ranks, special_tokens={})
    result = {'repository_commit': assumptions['repository_commit'], 'assumptions_sha256': digest(args.assumptions),
              'models_sha256': digest(args.models), 'original_files_verified': len(manifest['files']), 'points': []}
    for case in assumptions['cases']:
        case_id = case['case_id']; case_dir = code / 'ty24/test_data' / case_id
        data = json.loads((case_dir / 'input.json').read_text()); xml = (case_dir / 'output.xml').read_text()
        serialized = json.dumps(data)  # Exact original generator defaults, including ensure_ascii=True.
        prompt = template.format(tax_year=assumptions['tax_year'], input_data=serialized)
        input_tokens = len(enc.encode(prompt)); frame = assumptions['framing_input_tokens']
        task = task_arithmetic(data, case_id, xml)
        for config in assumptions['configurations']:
            model = models[config['model_id']]; coeff = float(model['flops_per_token']); assert coeff == 2 * float(model['active_parameters'])
            runs = []
            for i in range(1, 5):
                path = code / 'ty24/results' / case_id / config['native'] / f'model_completed_return_lobotomized_{i}.md'
                text = path.read_text(); out = len(enc.encode(text)); report = path.with_name(f'evaluation_result_lobotomized_{i}.md').read_text()
                cache = input_tokens * config['repeated_prompt_cache_fraction'] if i > 1 else 0.0
                processed = input_tokens + frame - cache + out + assumptions['termination_output_tokens']
                runs.append({'run': i, 'source': str(path.relative_to(src)), 'output_sha256': digest(path),
                             'raw_prompt_proxy_tokens': input_tokens, 'framing_input_tokens': frame, 'raw_output_proxy_tokens': out,
                             'termination_output_tokens': assumptions['termination_output_tokens'], 'estimated_cache_read_tokens': cache,
                             'processed_tokens': processed, 'compute_flops': coeff * processed, **grade(text, xml, mapping, report)})
            tokens = statistics.mean(x['processed_tokens'] for x in runs)
            raw_outputs = statistics.mean(x['raw_output_proxy_tokens'] for x in runs)
            full = input_tokens + frame + raw_outputs + assumptions['termination_output_tokens']
            first_only = input_tokens / 4 + frame + raw_outputs + assumptions['termination_output_tokens']
            param_low, param_high = config['parameter_scenario_billions']; tok_low, tok_high = assumptions['tokenizer_length_scenario']
            result['points'].append({'point_id': f"admin-taxcalc2024-{case['short']}-{config['short']}", 'case_id': case_id,
                'native_model': config['native'], 'model_id': config['model_id'], 'human_seconds': case['human_seconds'],
                'human_scenario_seconds': case['human_scenario_seconds'], 'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
                'serialized_json_characters': len(serialized), 'prompt_characters': len(prompt), 'raw_prompt_proxy_tokens': input_tokens,
                'mean_output_proxy_tokens': raw_outputs, 'mean_estimated_cache_read_tokens': statistics.mean(x['estimated_cache_read_tokens'] for x in runs),
                'tokens': tokens, 'compute_flops': tokens * coeff, 'ai_attempts': len(runs), 'strict_successes': sum(x['strict_success'] for x in runs),
                'within_5_dollars_successes': sum(x['within_5_dollars_success'] for x in runs),
                'mean_correct_line_percent': statistics.mean(x['correct_lines'] / x['scored_lines'] * 100 for x in runs),
                'compute_scenarios': {'all_prompts_fresh': full * coeff, 'only_first_prompt_fresh': first_only * coeff if config['repeated_prompt_cache_fraction'] else None,
                    'tokenizer_0_75': (tokens - frame - assumptions['termination_output_tokens']) * tok_low * coeff + (frame + assumptions['termination_output_tokens']) * coeff,
                    'tokenizer_1_25': (tokens - frame - assumptions['termination_output_tokens']) * tok_high * coeff + (frame + assumptions['termination_output_tokens']) * coeff,
                    'parameters_low': tokens * 2 * param_low * 1e9, 'parameters_high': tokens * 2 * param_high * 1e9},
                'expected_return_arithmetic': task, 'runs': runs})
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as f:
        json.dump(result, f, indent=2, allow_nan=False); f.write('\n')
    print(json.dumps([{'point_id': p['point_id'], 'tokens': p['tokens'], 'compute_flops': p['compute_flops'], 'strict': p['strict_successes'], 'line_percent': p['mean_correct_line_percent']} for p in result['points']], indent=2))


if __name__ == '__main__':
    main()
