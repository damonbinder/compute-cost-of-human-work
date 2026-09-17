#!/usr/bin/env python3
"""Reproduce the four language-acquisition operation estimates.

Python 3 standard library only; no network, model execution or package installation.
Example:
  python3 -B calculate.py --sources /data/sources/language-acquisition \
    --inputs /data/research/language-acquisition/calculation-inputs.json \
    --expected /data/research/language-acquisition/calculations.json \
    --output /new/path/calculations.json

--expected is optional: it checks all retained calculation fields before writing.
Output must be a new file outside the source directory. Evidence is only read.
"""
import argparse
import hashlib
import json
from pathlib import Path


def forward(h, f, v, s, kind, layers, heads, bucket, microbatch, q=1):
    dense = 2 * layers * ((5 if kind == 'gpt' else 4) * h * h + 3 * h * f)
    attention = 4 * layers * s * h + (4 * layers * s * h if kind == 'gpt' else 4 * layers * bucket * h)
    relative_projection = 4 * layers * bucket * h * h / (microbatch * s)
    mixtures = 2 * h * sum(range(2, 26) if kind == 'gpt' else range(1, 13))
    elementwise = layers * (30 * h + 12 * f + 7 * heads * s)
    output = q * (2 * (h * h + h * v) + 5 * v)
    return dict(dense=dense, attention=attention, relative_projection=relative_projection,
                mixtures=mixtures, elementwise=elementwise, output=output)


def calculate(source_dir, inputs):
    for name, digest in inputs['source_files'].items():
        path = (source_dir / name).resolve()
        if source_dir not in path.parents or not path.is_file():
            raise ValueError(f'Invalid or missing source: {name}')
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f'Source differs from reviewed version: {name}')
    out = {}
    a = inputs['assumptions']
    for key, model in inputs['models'].items():
        config = json.loads((source_dir / model['config_file']).read_text())
        h, f, v = config['hidden_size'], config['intermediate_size'], config['vocab_size']
        layers, heads = config['num_hidden_layers'], config['num_attention_heads']
        if layers != 12:
            raise ValueError('Dense layer-mixing formula is specific to the reviewed 12-layer models')
        bucket = 2 * config['position_bucket_size'] - 1
        kind, steps, tokens = model['kind'], model['training_steps'], model['training_tokens']
        s = sum(w * length for w, length in zip(model['token_phase_weights'], model['sequence_lengths']))
        q = a['masked_fraction_elc'] if kind == 'elc' else a['gpt_causal_fraction'] + (1-a['gpt_causal_fraction']) * a['masked_fraction_gpt']
        def fwd(length, fraction=1):
            return forward(h, f, v, length, kind, layers, heads, bucket,
                           a['relative_projection_microbatch'], fraction)
        parts = fwd(s, q)
        train = 3 * sum(parts.values()) * tokens
        # Full BLiMP allowance; temperature choices reuse logits, not model forwards.
        eval_tokens = a['blimp_pairs'] * 2 * a['blimp_sentence_positions'] ** 2
        evaluation = eval_tokens * sum(fwd(a['blimp_sentence_positions']).values())
        valid_tokens = ((steps // a['gpt_validation_interval'] + 1) * a['gpt_validation_workers'] *
                        a['gpt_validation_batch'] * a['gpt_validation_sequence']) if kind == 'gpt' else 0
        validation = valid_tokens * sum(fwd(a['gpt_validation_sequence'], a['masked_fraction_elc']).values())
        optimizer = a[f'{kind}_optimizer_ops'] * model['reported_parameters'] * steps
        total = round(train + evaluation + validation + optimizer)
        out[key] = dict(training_tokens=tokens, training_steps=steps, mean_sequence_length=s,
                        predicted_fraction=q, forward_parts=parts, training_flops=train,
                        blimp_evaluation_positions=eval_tokens, blimp_evaluation_flops=evaluation,
                        validation_positions=valid_tokens, validation_flops=validation,
                        optimizer_flops=optimizer, total_flops=total,
                        schedule_sensitivity_total=round(train * a['gpt_nominal_batch_ratio'] + evaluation + validation + optimizer) if kind == 'gpt' else total)
    m = inputs['lstm']
    h, v, layers = m['hidden_size'], m['vocabulary'], m['layers']
    train_tokens = m['training_tokens_per_epoch'] * m['epochs']
    parts = dict(recurrent=2 * layers * 4 * h * (h+h), output=2*h*v,
                 elementwise=layers*30*h+5*v)
    fwd = sum(parts.values())
    train = 3 * fwd * train_tokens
    valid_tokens = m['validation_tokens_per_epoch'] * m['epochs'] + m['test_tokens']
    blimp_tokens = a['blimp_pairs'] * 2 * a['blimp_sentence_positions']
    params = 2*v*h + layers*(4*h*(h+h)+8*h) + v
    updates = train_tokens / (m['batch'] * m['bptt'])
    optimizer = round(a['lstm_optimizer_ops'] * params * updates)
    out['lstm'] = dict(training_tokens=train_tokens, epochs=m['epochs'], forward_parts=parts,
                       training_flops=train, validation_positions=valid_tokens,
                       validation_flops=fwd*valid_tokens, blimp_evaluation_positions=blimp_tokens,
                       blimp_evaluation_flops=fwd*blimp_tokens, optimizer_flops=optimizer,
                       total_parameters=params, total_flops=round(train+fwd*(valid_tokens+blimp_tokens)+optimizer))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--expected', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sources, output = args.sources.resolve(), args.output.resolve()
    if output.exists() or output == sources or sources in output.parents:
        parser.error('Output must be a new file outside the source directory')
    try:
        result = calculate(sources, json.loads(args.inputs.read_text()))
        if args.expected and result != json.loads(args.expected.read_text()):
            raise ValueError('Recomputed values differ from the retained expected calculations')
    except (ValueError, KeyError, OSError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation also prevents overwriting a file created during calculation.
    with output.open('x') as handle:
        handle.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value['total_flops'] for key, value in result.items()}, indent=2))


if __name__ == '__main__':
    main()
