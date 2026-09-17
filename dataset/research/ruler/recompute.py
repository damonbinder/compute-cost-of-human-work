"""Reconstruct RULER passkey workloads; does not run a model or source program.

Dependency: tokenizers. Example:
python3 -B recompute.py --sources /path/to/sources --output /path/to/new.json
All outputs are estimates from the retained generator, not recovered run logs.
"""
import argparse
import ast
from bisect import bisect_right
from collections import Counter
import hashlib
import importlib.metadata
import json
from pathlib import Path
import random
from statistics import mean

from tokenizers import Tokenizer


def literal(path, name):
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError(name)


class WordPairs:
    """Index the original sorted unique adjective-noun product without a 6M-string set.

    Hyphen-prefix adjective groups can interleave; merge those groups explicitly.
    All remaining group prefixes are disjoint, so indexed order equals sorted(set).
    """
    def __init__(self, src):
        adjectives = sorted(set(x.rstrip() for x in (src / 'wonderwords-adjectivelist.txt').read_text().splitlines()))
        self.nouns = sorted(set(x.rstrip() for x in (src / 'wonderwords-nounlist.txt').read_text().splitlines()))
        roots = [a for a in adjectives if not any(a.startswith(other + '-') for other in adjectives if a != other)]
        self.groups, self.ends = [], []
        total = 0
        previous_maximum = None
        for root in sorted(roots, key=lambda a: a + '-'):
            members = [a for a in adjectives if a == root or a.startswith(root + '-')]
            values = sorted({a + '-' + n for a in members for n in self.nouns}) if len(members) > 1 else None
            smallest = values[0] if values else root + '-' + self.nouns[0]
            largest = values[-1] if values else root + '-' + self.nouns[-1]
            assert previous_maximum is None or previous_maximum < smallest
            previous_maximum = largest
            total += len(values) if values else len(self.nouns)
            self.groups.append((root, values))
            self.ends.append(total)
        self.count = total
        self.adjectives = len(adjectives)

    def __len__(self):
        return self.count

    def __getitem__(self, i):
        k = bisect_right(self.ends, i)
        offset = i - (self.ends[k - 1] if k else 0)
        root, values = self.groups[k]
        return values[offset] if values else root + '-' + self.nouns[offset]


def operations(n, output, cfg, square=False, all_prompt_heads=False):
    d, layers, intermediate = cfg['hidden_size'], cfg['num_hidden_layers'], cfg['intermediate_size']
    heads, kv_heads = cfg['num_attention_heads'], cfg['num_key_value_heads']
    kv_width = d * kv_heads // heads
    block_matrices = layers * (2 * d * d + 2 * d * kv_width + 3 * d * intermediate)
    output_matrix = d * cfg['vocab_size']
    # Last prefill state predicts output token 1; final emitted EOS is not fed back.
    decode = output - 1
    positions = n + decode
    linear = 2 * block_matrices * positions
    head_positions = n + decode if all_prompt_heads else output
    output_head = 2 * output_matrix * head_positions
    causal_pairs = n * (n + 1) // 2
    prefill_pairs = n * n if square else causal_pairs
    decode_pairs = decode * n + decode * (decode + 1) // 2
    attention = 4 * layers * d * (prefill_pairs + decode_pairs)
    # Conventional scalar-operation allowance: score scaling and softmax (~6/pair),
    # RMS/residual/RoPE/SwiGLU (~10d + 3(d+kv) + 5i per layer-position),
    # final RMS and output sampling. These are not measured kernel instruction counts.
    attention_scalar = 6 * layers * heads * (causal_pairs + decode_pairs)
    other_scalar = layers * positions * (10 * d + 3 * (d + kv_width) + 5 * intermediate)
    other_scalar += 4 * d * positions + 12 * cfg['vocab_size'] * output
    return {
        'input_tokens': n, 'output_tokens_assumed': output, 'text_tokens_input_output': n + output,
        'transformer_processed_positions': positions,
        'transformer_matrix_flops': linear, 'output_projection_flops': output_head,
        'attention_matrix_flops': attention, 'attention_scalar_flops_estimate': attention_scalar,
        'other_scalar_flops_estimate': other_scalar,
        'matrix_flops': linear + output_head + attention,
        'compute_flops': linear + output_head + attention + attention_scalar + other_scalar,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sources', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    src, out = a.sources.resolve(), a.output.resolve()
    if out.exists() or out == src or src in out.parents:
        p.error('output must be new and outside source evidence')
    cfg = json.loads((src / 'llama31-config.json').read_text())
    enc = Tokenizer.from_file(str(src / 'llama31-tokenizer.json'))
    encode = lambda s: enc.encode(s, add_special_tokens=False).ids
    settings = literal(src / 'ruler-2024-constants.py', 'TASKS')['niah']
    assert settings['tokens_to_generate'] == 128
    task = settings['template']
    # Exact wrapper printed in the original paper's Appendix D Table 6.
    template = ('<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n' + task
                + '<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n'
                + settings['answer_prefix'])
    for before, after in [('Some', 'A'), ('are all', 'is'), ('are', 'is'), ('answers', 'answer')]:
        template = template.replace(before, after)
    noise = 'The grass is green. The sky is blue. The sun is yellow. Here we go. There and back again.'
    assert len(encode(noise)) == 24
    words = WordPairs(src)
    results = []
    for length in [4096, 131072]:
        rng = random.Random(42)

        def generate(repetitions):
            key = rng.choice(words)
            value = str(rng.randint(1000000, 9999999))
            # A single-needle Random(42).shuffle does not change RNG state.
            position = rng.sample(range(repetitions), 1)[0]
            rng.sample(range(1), 1)  # original query-index selection consumes RNG
            needle = f'One of the special magic numbers for {key} is: {value}.'
            sentences = [noise] * repetitions
            sentences.insert(position, needle)
            prompt = template.format(type_needle_v='number', context='\n'.join(sentences), query=key)
            return prompt, value, key, position

        repetitions, total = 25, 0
        probes = []
        while total + 128 < length:
            prompt, value, key, pos = generate(repetitions)
            total = len(encode(prompt + value))
            probes.append({'repetitions': repetitions, 'input_plus_answer_tokens': total})
            if total + 128 > length:
                repetitions -= 25
                break
            repetitions += 25
        rows, example = [], None
        for i in range(500):
            used = repetitions
            while True:
                prompt, value, key, position = generate(used)
                measured = len(encode(prompt))
                if measured + 128 <= length:
                    break
                assert used > 25
                used -= 25
            # Serving's normal tokenizer encoding adds one BOS beyond the explicit
            # source wrapper; retain both lengths and a no-extra-BOS sensitivity.
            processed = len(enc.encode(prompt, add_special_tokens=True).ids)
            assert processed == measured + 1
            payload = ' ' + value + '.'
            output = len(encode(payload)) + 1  # generated end-of-turn token
            assert output == 6
            op = operations(processed, output, cfg)
            rows.append({'reconstruction_index': i, 'key': key, 'answer': value,
                         'noise_repetitions': used, 'needle_insertion_index': position,
                         'generator_prompt_tokens': measured,
                         'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(), **op})
            if example is None:
                example = {'input': prompt, 'expected_answer': value, 'assumed_completion': payload + '<|eot_id|>'}
        scalar_fields = ['input_tokens', 'output_tokens_assumed', 'text_tokens_input_output',
                         'transformer_processed_positions', 'transformer_matrix_flops',
                         'output_projection_flops', 'attention_matrix_flops',
                         'attention_scalar_flops_estimate', 'other_scalar_flops_estimate',
                         'matrix_flops', 'compute_flops']
        center = {f: mean(r[f] for r in rows) for f in scalar_fields}
        alternatives = {}
        for label, options in [('bare_number_and_eos', {'output': 4}),
                               ('twenty_output_tokens', {'output': 20}),
                               ('full_128_output_cap', {'output': 128}),
                               ('square_prefill_attention', {'square': True}),
                               ('all_prompt_output_heads', {'all_prompt_heads': True}),
                               ('no_additional_bos', {'remove_bos': True})]:
            vals = []
            for r in rows:
                kw = dict(options)
                n = r['input_tokens'] - int(kw.pop('remove_bos', False))
                output = kw.pop('output', 6)
                vals.append(operations(n, output, cfg, **kw)['compute_flops'])
            alternatives[label] = mean(vals)
        results.append({'point_id': f'memo-ruler-passkey-{length}-llama31-8b',
                        'nominal_total_context_limit': length, 'generator_seed_assumed': 42,
                        'reconstructed_examples': 500, 'source_performance_examples': 500,
                        'source_recall_percent': 100.0, 'human_seconds_assumed': 10,
                        'human_seconds_scenarios': [5, 25],
                        'noise_repetition_counts': dict(Counter(r['noise_repetitions'] for r in rows)),
                        'generator_prompt_min': min(r['generator_prompt_tokens'] for r in rows),
                        'generator_prompt_max': max(r['generator_prompt_tokens'] for r in rows),
                        'central': center, 'scenario_flops': alternatives,
                        'length_probes': probes, 'reconstructed_example': example, 'rows': rows})
        print(length, 'mean input', center['input_tokens'], 'FLOPs', center['compute_flops'], flush=True)
    d, l, kv = cfg['hidden_size'], cfg['num_hidden_layers'], cfg['hidden_size'] * cfg['num_key_value_heads'] // cfg['num_attention_heads']
    matrices = l * (2 * d * d + 2 * d * kv + 3 * d * cfg['intermediate_size'])
    total_p = matrices + 2 * d * cfg['vocab_size'] + (2 * l + 1) * d
    names = ['ruler-2024-niah.py', 'ruler-2024-constants.py', 'ruler-2024-prepare.py',
             'ruler-2024-synthetic.yaml', 'ruler-paper.pdf', 'llama31-config.json',
             'llama31-tokenizer.json', 'wonderwords-adjectivelist.txt', 'wonderwords-nounlist.txt']
    result = {'kind': 'reconstructed workload estimate, not original response logs',
              'dependencies': {'tokenizers': importlib.metadata.version('tokenizers')},
              'source_sha256': {n: hashlib.sha256((src / n).read_bytes()).hexdigest() for n in names},
              'word_product_unique_count': len(words), 'architecture': cfg,
              'transformer_matrix_parameters': matrices, 'total_architecture_parameters': total_p,
              'points': results}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
