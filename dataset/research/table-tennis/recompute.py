#!/usr/bin/env python3
"""Recompute one minute of competitive robot table tennis; Python 3.10+ stdlib.

Accepts explicit retained-source, recipe and new-output paths. Never runs a robot,
downloads data, changes evidence, or overwrites an existing output.
"""
import argparse
import hashlib
import json
from pathlib import Path


def calculate(r):
    seconds = r['duration_seconds']
    frames = seconds * r['camera_pairs_per_second']
    detector = []
    for layer in r['detector_layers']:
        n = r['cameras'] * layer['height'] * layer['width']
        weights = layer['kernel'] ** 2 * layer['input_channels'] * layer['output_channels']
        biases = layer['output_channels'] if layer['bias'] else 0
        assert weights + biases == layer['reported_parameters']
        activations = n * layer['output_channels']
        mac_flops = 2 * n * weights
        bias_ops = activations if layer['bias'] else 0
        batch_norm_ops = 2 * activations if layer['batch_norm'] else 0
        relu_ops = activations
        detector.append(dict(name=layer['name'], weights=weights,
            paired_frame_mac_flops=mac_flops, paired_frame_bias_ops=bias_ops,
            paired_frame_batch_norm_ops=batch_norm_ops,
            paired_frame_relu_ops=relu_ops,
            minute_flops=frames*(mac_flops+bias_ops+batch_norm_ops+relu_ops)))
    detector_flops = sum(x['minute_flops'] for x in detector)
    llc = []
    length = r['llc_input_steps']
    channels = r['llc_input_channels']
    parameters = 0
    for layer in r['llc_layers']:
        out_length = length - layer['dilation'] * (layer['kernel']-1)
        filters = layer['filters']
        weights = layer['kernel'] * channels * filters
        parameters += weights + filters
        mac_flops = 2 * out_length * weights
        bias_ops = out_length * filters
        # tanh=one operation; sigmoid=negate/exp/add/divide, plus gate multiply.
        # This elementary-operation allowance is small and is not a timing claim.
        nonlinear_ops = out_length*filters//2 * 6 if layer['gate'] else out_length*filters
        llc.append(dict(output_steps=out_length, conv_filters=filters,
            weights=weights, biases=filters, mac_flops=mac_flops,
            bias_ops=bias_ops, nonlinear_ops=nonlinear_ops))
        length = out_length
        channels = filters//2 if layer['gate'] else filters
    assert parameters == 10676
    assert (length, channels) == (1, 8)
    llc_per_call = sum(x['mac_flops']+x['bias_ops']+x['nonlinear_ops'] for x in llc)
    llc_calls = seconds * r['llc_calls_per_second']
    # Published FiLM/style layer widths are incomplete. Their explicit temporal
    # reuse allowances are retained in the recipe, instead of invented widths.
    film_per_call = 2*r['film_parameters']*r['film_parameter_uses'] + 2*8
    style_per_call = 2*r['style_parameters']*r['style_parameter_uses']
    spin_widths = r['spin_widths']
    spin_weights = sum(a*b for a,b in zip(spin_widths,spin_widths[1:]))
    spin_bias_ops = sum(spin_widths[1:])
    spin_hidden_ops = sum(spin_widths[1:-1])
    spin_softmax_ops = 3*spin_widths[-1]-1
    spin_per_call = 2*spin_weights + spin_bias_ops + spin_hidden_ops + spin_softmax_ops
    events = seconds*r['incoming_balls_per_second']
    style_calls = events
    spin_calls = events*r['spin_queries_per_incoming_ball']
    components = dict(detector=detector_flops, selected_llc=llc_per_call*llc_calls,
        film=film_per_call*llc_calls, style=style_per_call*style_calls,
        spin=spin_per_call*spin_calls)
    total = sum(components.values())
    # Deliberately broad small-module stress case: tenfold LLC work, all FiLM
    # parameters at all eight positions, and both HLC nets at every camera step.
    stress = detector_flops + 10*components['selected_llc'] + (
        (2*r['film_parameters']*8+16)*llc_calls
        + (style_per_call+spin_per_call)*frames)
    return dict(point_id=r['point_id'], duration_seconds=seconds,
        paired_frames=frames, detector_layers=detector,
        detector_parameters=sum(x['reported_parameters'] for x in r['detector_layers'])+64,
        llc_layers=llc, llc_parameters=parameters, llc_flops_per_call=llc_per_call,
        llc_calls=llc_calls, film_flops_per_call=film_per_call,
        style_flops_per_call=style_per_call, style_calls=style_calls,
        spin_flops_per_call=spin_per_call, spin_calls=spin_calls,
        components=components, compute_flops=total,
        detector_share=detector_flops/total,
        sensitivity=dict(detector_mac_only=frames*sum(x['paired_frame_mac_flops'] for x in detector),
            all_helpers_omitted=detector_flops, small_module_stress=stress,
            stress_change_percent=(stress/total-1)*100))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sources', required=True, type=Path)
    p.add_argument('--recipe', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    source_dir, recipe, output = a.sources.resolve(), a.recipe.resolve(), a.output.resolve()
    if output.exists() or output == recipe or output.is_relative_to(source_dir):
        p.error('output must be a new file outside retained sources and the recipe')
    manifest = json.loads((source_dir/'source-manifest.json').read_text())
    hashes = {}
    for entry in manifest:
        path = (source_dir/entry['file']).resolve()
        if not path.is_relative_to(source_dir):
            p.error('source path escapes source directory')
        value = hashlib.sha256(path.read_bytes()).hexdigest()
        if value != entry['sha256']:
            p.error('source hash differs: '+entry['file'])
        hashes[entry['file']] = value
    result = calculate(json.loads(recipe.read_text()))
    result['source_hashes'] = hashes
    result['recipe_sha256'] = hashlib.sha256(recipe.read_bytes()).hexdigest()
    with output.open('x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print(json.dumps({'compute_flops':result['compute_flops'],
        'human_time':result['duration_seconds'], 'output':str(output)}))


if __name__ == '__main__':
    main()
