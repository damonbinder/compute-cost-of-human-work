#!/usr/bin/env python3
"""Reproduce code-learning operation and human-time estimates. No network access."""
import argparse
import json
from pathlib import Path
from tokenizers import Tokenizer  # pip install -r requirements.txt


def calculate(source_dir):
    x = json.loads((source_dir / 'inputs.json').read_text())
    tokenizer_path = source_dir / 'multipl-t' / 'tokenizer-15b.json'
    assert tokenizer_path.read_bytes() == (source_dir / 'multipl-t' / 'tokenizer-1b.json').read_bytes(), 'Study tokenizers differ'
    tokenizer = Tokenizer.from_file(str(tokenizer_path))
    tokenizer.no_truncation()
    tokenizer.no_padding()
    result = {}
    for name, p in x['points'].items():
        params, tokens = p['parameters'], p['training_tokens']
        training = 6 * params * tokens
        monitoring = 2 * params * tokens * .01
        helpers = 0
        detail = {}
        if p['family'] == 'multipl-t':
            lang = p['language']
            sample = [json.loads(line) for line in (source_dir / 'multipl-t' / f'{lang}-translation-sample.jsonl').read_text().splitlines()]
            prompt_chars = sum(len(row['prompt']) for row in sample) / len(sample)
            prompt_counts = [len(tokenizer.encode(row['prompt'], add_special_tokens=False).ids) for row in sample]
            prompt_tokens = sum(prompt_counts) / len(prompt_counts)
            m = x['multipl-t']
            tests = m['test_functions'] * m['test_suites'] * (m['test_prompt_tokens'] + m['test_output_tokens'])
            translations = m['translation_functions'] * p['translations_per_function'] * (prompt_tokens + p['translation_output_tokens'])
            helpers = 2 * m['helper_parameters'] * (tests + translations)
            evaluation_tokens = p['epochs'] * p['benchmark_problems'] * 20 * 512
            # 512 is a maximum total length, including prompt; EOS may stop earlier.
            # The initial callback returns without inference when checkpoint_dir is None.
            # For 15B use the same cap as a small conservative allowance, not a measured log.
            monitoring = 2 * params * evaluation_tokens
            detail = dict(test_generation_tokens=tests, translation_tokens=translations,
                          sampled_prompts=len(sample), mean_prompt_characters=prompt_chars,
                          sampled_prompt_token_total=sum(prompt_counts), mean_prompt_tokens=prompt_tokens,
                          prompt_token_min=min(prompt_counts), prompt_token_max=max(prompt_counts),
                          evaluation_tokens=evaluation_tokens,
                          training_only_flops=training)
            scenarios = []
            for input_scale, out_scale, test_scale in [(.8, .5, .5), (1.2, 2.5, 2)]:
                tr = m['translation_functions'] * p['translations_per_function'] * (prompt_tokens * input_scale + p['translation_output_tokens'] * out_scale)
                scenarios.append(training + monitoring + 2*m['helper_parameters']*(tests*test_scale+tr))
        elif p['family'] == 'kotlin':
            k = x['kotlin']
            # Allocate creation of the 15k selected source exercises, plus their Kotlin translations.
            source_creation = k['examples'] * (k['creation_prompt_tokens'] + k['python_output_tokens'])
            translation = k['examples'] * (k['translation_prompt_overhead'] + k['python_output_tokens']) + k['kotlin_output_tokens']
            helper_tokens = (source_creation + translation) * k['helper_retry_factor']
            helpers = 2*k['helper_parameters']*helper_tokens
            # Four epoch checks of 630 source-defined completion examples + HumanEval.
            monitoring = 2*params*4*(630+161)*512
            detail = dict(source_creation_tokens=source_creation, translation_tokens=translation,
                          helper_tokens_with_allowance=helper_tokens, evaluation_tokens=4*(630+161)*512,
                          training_only_flops=training)
            scenarios = [training+monitoring+helpers/1.25, training*1.15+monitoring+helpers*(175/7)*2]
        else:
            # The paper does not report monitoring counters. Central allowance is one forward
            # token per100 update tokens; scenarios include0–10 plus up to30% attention cost.
            scenarios = [training, training*1.30 + 2*params*tokens*.10]
        result[name] = dict(training_tokens=tokens, training_flops=training,
                            monitoring_flops=monitoring, helper_flops=helpers,
                            total_flops=training+monitoring+helpers,
                            flops_sensitivity=scenarios,
                            human_hours=p['human_hours'],human_seconds=3600*p['human_hours'],
                            human_hours_sensitivity=p['human_hours_sensitivity'],**detail)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source_dir', type=Path)
    parser.add_argument('output_dir', type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir/'calculations.json').write_text(json.dumps(calculate(args.source_dir),indent=2)+'\n')
