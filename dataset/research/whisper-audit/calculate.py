#!/usr/bin/env python3
"""Reproduce the speech audit. Python3 standard library only; no network access.
Usage: python3 calculate.py SOURCE_DIR OUTPUT_DIR
"""
import argparse
import json
from pathlib import Path


def encoder(d, layers, s=1500):
    conv = 2 * ((2*s)*3*80*d + s*3*d*d)
    transformer = layers*(24*s*d*d + 4*s*s*d)
    return dict(convolution_flops=conv, encoder_transformer_flops=transformer,
                encoder_flops=conv+transformer)


def whisper(d, layers, vocab, text, prompt):
    s, t = 1500, text+prompt
    e = encoder(d,layers,s)
    # Prompt prefill uses a full masked p*p matrix; later steps use cached keys/values.
    pairs = prompt*prompt + (t*(t+1)-prompt*(prompt+1))//2
    cross_kv = layers*4*s*d*d
    decoder = cross_kv + layers*(28*t*d*d + 4*t*s*d + 4*d*pairs) + 2*t*d*vocab
    return dict(**e, cross_attention_kv_flops=cross_kv, decoder_flops=decoder,
                processed_text_positions=t, total_flops=e['encoder_flops']+decoder)


def calculate(src):
    inputs=json.loads((src/'inputs.json').read_text());out={}
    for point,p in inputs['whisper'].items():
        out[point]=whisper(p['width'],p['layers'],p['vocabulary'],p['lexical_tokens'],p['prompt_positions'])
        out[point]['lexical_token_sensitivity']={str(n):whisper(p['width'],p['layers'],p['vocabulary'],n,p['prompt_positions'])['total_flops'] for n in p['lexical_token_scenarios']}
        out[point]['human_seconds']=p['human_seconds'];out[point]['human_sensitivity_seconds']=p['human_sensitivity_seconds']
    p=inputs['gpt4o'];rate=p['provider_input_price_per_minute']/p['provider_input_price_per_million']*1e6
    audio=rate*p['audio_seconds']/60
    acoustic=encoder(1280,32)['encoder_flops']*(p['audio_seconds']/30)
    text=p['text_instruction_and_framing_tokens']+p['text_output_tokens']
    backbone=2*p['active_parameters']*(audio+text)
    out['perc-asr-gpt4o']=dict(audio_billing_positions_per_minute=rate,assumed_audio_backbone_positions=audio,
        text_tokens=text, backbone_flops=backbone,acoustic_frontend_proxy_flops=acoustic,total_flops=backbone+acoustic,
        human_seconds=p['audio_seconds']*p['human_work_ratio'],human_sensitivity_seconds=[180,360],
        low_scenario_flops=2*25e9*(audio*.5+20+150)+acoustic*.5,
        high_scenario_flops=2*100e9*(audio*2+20+300)*1.10+acoustic*2)
    return out


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('source_dir',type=Path);parser.add_argument('output_dir',type=Path)
    args=parser.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/'calculations.json').write_text(json.dumps(calculate(args.source_dir),indent=2)+'\n')
