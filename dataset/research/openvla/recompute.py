#!/usr/bin/env python3
"""Replay OpenVLA video workload and architecture arithmetic. No weights or model calls.
Dependencies: av, sentencepiece, Pillow. All paths are explicit; output must be new.
"""
import argparse
import hashlib
import json
from pathlib import Path
import av
import sentencepiece as spm
from PIL import Image, ImageDraw


def vision(h, m, depth, prefix, layerscale=False, pool=False):
    patches = 256
    s = patches + prefix
    # Stored parameters, including the unused final norm and optional pooling head.
    block_parameters = 4*h*h + 2*h*m + 9*h + m + (2*h if layerscale else 0)
    pool_parameters = 4*h*h + 2*h*m + 8*h + m if pool else 0
    parameters = 3*14*14*h + h + patches*h + prefix*h + depth*block_parameters + 2*h + pool_parameters
    patch = 2*patches*3*14*14*h
    dense = depth*2*s*(4*h*h + 2*h*m)
    attention = depth*4*s*s*h
    # Scalar convention: transcendental = one operation; explicit coarse fused-kernel recipe.
    # Biases; two layer norms; GELU; residuals; score scaling/softmax; optional LayerScale.
    scalar = 2*patches*h + depth*(s*(5*h+m) + s*(14*h+4) + 5*s*m + 2*s*h + 6*16*s*s + (2*s*h if layerscale else 0))
    return dict(parameters=parameters, positions=s, blocks=depth, patch_flops=patch,
                dense_flops=dense, attention_flops=attention, scalar_flops=scalar,
                flops=patch+dense+attention+scalar, unused_pool_parameters=pool_parameters)


def policy(text_positions, full_square_attention=False, no_generation_cache=False, action_dimensions=7):
    dino=vision(1024,4096,24,5,True)
    siglip=vision(1152,int(1152*3.7362),27,0,pool=True)
    v=2176; h=4096; m=11008; layers=32; vocab=32064
    projector_parameters=v*(4*v)+(4*v)+(4*v)*h+h+h*h+h
    projector_matrix=2*256*(v*4*v+4*v*h+h*h)
    projector_scalar=256*(4*v+h+h)+5*256*(4*v+h)
    s=256+text_positions
    if no_generation_cache:
        positions=sum(s+j for j in range(action_dimensions))
        pairs=sum((s+j)**2 if full_square_attention else (s+j)*(s+j+1)//2 for j in range(action_dimensions))
    else:
        positions=s+action_dimensions-1
        pairs=(s*s if full_square_attention else s*(s+1)//2)+sum(s+j for j in range(1,action_dimensions))
    dense=2*layers*positions*(4*h*h+3*h*m)
    attention=4*layers*h*pairs
    # Transformers 4.40.1 projects every returned hidden position, including prefill.
    head=2*positions*h*vocab
    scalar=layers*(positions*(8*h+4)+9*positions*h+6*positions*m+2*positions*h+6*32*pairs)+positions*(4*h+2)
    decoder_parameters=2*vocab*h+layers*(4*h*h+3*h*m+2*h)+h
    parts=dict(dino=dino,siglip=siglip,projector_parameters=projector_parameters,
               projector_flops=projector_matrix+projector_scalar,decoder_parameters=decoder_parameters,
               decoder_processed_positions=positions,attention_query_key_pairs=pairs,
               decoder_matrix_flops=dense,decoder_attention_flops=attention,
               decoder_head_flops=head,decoder_scalar_flops=scalar)
    vision_evaluations = action_dimensions if no_generation_cache else 1
    parts['vision_evaluations'] = vision_evaluations
    parts['encoder_parameters']=dino['parameters']+siglip['parameters']+projector_parameters
    parts['total_parameters']=parts['encoder_parameters']+decoder_parameters
    parts['matrix_attention_flops']=vision_evaluations*(dino['flops']-dino['scalar_flops']+siglip['flops']-siglip['scalar_flops']+projector_matrix)+dense+attention+head
    parts['flops']=vision_evaluations*(dino['flops']+siglip['flops']+projector_matrix+projector_scalar)+dense+attention+head+scalar
    return parts


def main(source, output):
    source=source.resolve();output=output.resolve()
    assert source.is_dir() and not output.is_relative_to(source)
    assert not output.exists(), 'Output directory must be new'
    manifest=json.loads((source/'manifest.json').read_text())
    for row in manifest:
        assert hashlib.sha256((source/row['file']).read_bytes()).hexdigest()==row['sha256'],row['file']
    config=json.loads((source/'model/release-config.json').read_text())
    assert config==json.loads((source/'model/config.json').read_text())
    assert config['image_sizes']==[224,224]
    assert config['timm_model_ids']==['vit_large_patch14_reg4_dinov2.lvd142m','vit_so400m_patch14_siglip_224']
    assert len(config['norm_stats']['bridge_orig']['action']['q01'])==7
    tokenizer=spm.SentencePieceProcessor(model_file=str(source/'model/tokenizer.model'))
    prompt='In: What action should the robot take to put yellow corn on pink plate?\nOut:'
    # Released tokenizer adds BOS, not EOS; June 13 predict_action appends empty token.
    ids=[tokenizer.bos_id()]+tokenizer.encode(prompt)+[29871]
    assert len(ids)==22 and ids[-2]==29901
    operation=policy(len(ids))
    native_total=json.loads((source/'model/api-metadata.json').read_text())['safetensors']['total']
    assert operation['total_parameters']==native_total==7541237184
    output.mkdir(parents=True)
    videos=[]
    names=['openvla--put_corn_on_plate--clutter.mp4','openvla--put_corn_on_plate--clutter--2.mp4']
    for name in names:
        with av.open(str(source/'videos'/name)) as container:
            stream=container.streams.video[0];frames=list(container.decode(stream))
            n=len(frames);assert n in [38,47]
            record=dict(file=name,frames=n,encoded_fps=str(stream.average_rate),encoded_seconds=float(stream.duration*stream.time_base),
                        assumed_policy_calls=n,text_tokens=n*len(ids),flops=n*operation['flops'])
            videos.append(record)
            indices=sorted(set([0,1,5]+[int(j*(n-1)/11) for j in range(1,12)]))
            sheet=Image.new('RGB',(1280,266*((len(indices)+3)//4)),'white')
            for k,i in enumerate(indices):
                tile=Image.new('RGB',(320,266),'white');im=frames[i].to_image();im.thumbnail((320,240));tile.paste(im,(0,26))
                ImageDraw.Draw(tile).text((5,5),f'Frame {i} of {n}',fill='black');sheet.paste(tile,((k%4)*320,(k//4)*266))
            sheet.save(output/(Path(name).stem+'-inspection.jpg'))
    calls=sum(v['assumed_policy_calls'] for v in videos)/len(videos)
    result=dict(point_id='phys-openvla-corn-placement-demos',selection='Both published corn-on-pink-plate clutter demonstration clips; successful sample.',
                prompt=prompt,prompt_token_ids=ids,text_tokens_per_call=len(ids),image_positions_per_call=256,
                generated_action_positions_per_call=7,incremental_action_positions_processed_per_call=6,
                operation=operation,video_attempts=videos,mean_assumed_calls=calls,
                tokens=calls*len(ids),compute_flops=calls*operation['flops'],
                human_time=5,human_calibration={'healthy_people':20,'retained_trials_each':3,'donor_attempts':60,
                'reach_seconds':1.00,'transport_seconds':1.32,'assumed_instruction_and_target_search_seconds':2,
                'assumed_release_and_check_seconds':0.7,'unrounded_sum_seconds':5.02,'rounded_target_seconds':5},
                performance_context={'evaluation_trials':10,'total_fractional_points':9,'partial_credit':0.5,'full_success_count':'unreported'},
                sensitivities={
                    'caption_time_times_5hz_calls':sum(v['encoded_seconds']*1.5*5 for v in videos)/2,
                    'caption_time_times_5hz_flops':0.75*calls*operation['flops'],
                    'double_calls_per_encoded_frame_flops':2*calls*operation['flops'],
                    'one_fewer_call_each_clip_flops':(calls-1)*operation['flops'],
                    'one_additional_call_each_clip_flops':(calls+1)*operation['flops'],
                    'full_square_prefill_attention_flops':calls*policy(len(ids),full_square_attention=True)['flops'],
                    'no_generation_kv_cache_flops':calls*policy(len(ids),no_generation_cache=True)['flops'],
                    'prompt_minus_four_text_positions_flops':calls*policy(len(ids)-4)['flops'],
                    'prompt_plus_four_text_positions_flops':calls*policy(len(ids)+4)['flops'],
                    'human_seconds_low':3,'human_seconds_high':8})
    (output/'calculations.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['point_id','mean_assumed_calls','tokens','compute_flops','human_time']},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args();main(a.source_dir,a.output_dir)
