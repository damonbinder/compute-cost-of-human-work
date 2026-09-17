#!/usr/bin/env python3
"""SDXL drawing operation recipe, meta tensors only. No weights or generation.
Python3.10+, torch2.8.0, diffusers0.35.1, transformers4.56.1, accelerate1.10.1.
Required --sources DIR --assumptions JSON --output NEW_JSON.
"""
import argparse,collections,hashlib,json,math
from pathlib import Path
import torch
from torch.utils._python_dispatch import TorchDispatchMode
from torch.utils.flop_counter import FlopCounterMode
from diffusers import UNet2DConditionModel,ControlNetModel,AutoencoderKL
from transformers import CLIPTextConfig,CLIPTextModel,CLIPTextModelWithProjection


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


class ScalarOps(TorchDispatchMode):
    """Additional scalar arithmetic; matrix/convolution FMA counted separately.
    Nonlinear primitive evaluations count one operation each. Comparisons, table
    lookup, indexing, shape changes and memory movement are not neural FLOPs.
    """
    def __init__(self):self.elements=collections.Counter();self.flops=collections.Counter()
    def __torch_dispatch__(self,func,types,args=(),kwargs=None):
        out=func(*args,**(kwargs or {}));name=str(func)
        t=out if isinstance(out,torch.Tensor) else out[0] if isinstance(out,tuple) and out and isinstance(out[0],torch.Tensor) else None
        if t is None or not t.is_floating_point():return out
        n=t.numel();self.elements[name]+=n;count=0
        if name.startswith(('aten.add.','aten.add_.','aten.sub.','aten.rsub.','aten.mul.','aten.div.','aten.neg.','aten.exp.','aten.log.','aten.sin.','aten.cos.','aten.pow.','aten.sqrt.','aten.rsqrt.')):count=n
        elif name.startswith(('aten.silu.','aten.sigmoid.')):count=4*n
        elif name.startswith('aten.gelu.'):count=5*n
        elif name.startswith(('aten._safe_softmax.','aten._softmax.')):count=4*n
        elif name.startswith(('aten.native_layer_norm.','aten.native_group_norm.')):count=7*n+4*out[1].numel()
        elif name.startswith('aten.addmm.') and (kwargs or {}).get('beta',1)!=0:count=n
        elif name.startswith('aten.convolution.') and args[2] is not None:count=n
        if count:self.flops[name]+=count
        return out


def profile(fn,model):
    with torch.no_grad(),ScalarOps() as scalar,FlopCounterMode(display=False) as fc:out=fn()
    primary=fc.get_total_flops();extra=sum(scalar.flops.values())
    summary={'parameters':sum(x.numel() for x in model.parameters()),'matrix_convolution_attention_flops':primary,
             'additional_scalar_flops':extra,'flops':primary+extra,
             'primary_operation_flops':{str(k):v for k,v in fc.get_flop_counts()['Global'].items()},
             'scalar_operation_flops':dict(sorted(scalar.flops.items()))}
    return summary,out


def lora_merge(model,kind,rank):
    # Kohya's conventional Transformer2DModel/CLIP-attention-and-MLP targets.
    selected=[]
    for name,module in model.named_modules():
        if not isinstance(module,torch.nn.Linear):continue
        if (kind=='unet' and '.attentions.' in name) or (kind=='clip' and '.encoder.layers.' in name):
            p=module.weight.numel();selected.append({'name':name,'weight_elements':p,'rank':rank,'merge_flops':(2*rank+2)*p})
    return {'layers':len(selected),'target_weight_elements':sum(x['weight_elements'] for x in selected),
            'merge_flops':sum(x['merge_flops'] for x in selected),'targets':selected}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ['sources','assumptions','output']:ap.add_argument('--'+key,required=True,type=Path)
    a=ap.parse_args();s=a.sources.resolve();out=a.output.resolve();ass=a.assumptions.resolve()
    if out.exists() or out==s or s in out.parents or out==ass:raise SystemExit('Output must be new and outside retained sources and inputs.')
    cfg=json.loads(ass.read_text())
    if (s/'source-manifest.json').exists():
        for rec in json.loads((s/'source-manifest.json').read_text())['files']:assert sha(s/rec['path'])==rec['sha256'],rec['path']
    def conf(path):return json.loads((s/path).read_text())
    with torch.device('meta'):
        unet=UNet2DConditionModel.from_config(conf('sdxl/unet/config.json')).eval()
        vae=AutoencoderKL.from_config(conf('sdxl/vae/config.json')).eval()
        cn={k:ControlNetModel.from_config(conf(f'controlnet-canny-{k}/config.json')).eval() for k in ['full','small']}
        clip1=CLIPTextModel(CLIPTextConfig(**conf('sdxl/text_encoder/config.json'))).eval()
        clip2=CLIPTextModelWithProjection(CLIPTextConfig(**conf('sdxl/text_encoder_2/config.json'))).eval()
        ids=torch.empty(cfg['cfg_branches'],77,dtype=torch.long)
    c1,_=profile(lambda:clip1(input_ids=ids,output_hidden_states=True),clip1)
    c2,_=profile(lambda:clip2(input_ids=ids,output_hidden_states=True),clip2)
    lora={'unet':lora_merge(unet,'unet',cfg['lora_rank']),'clip1':lora_merge(clip1,'clip',cfg['lora_rank']),'clip2':lora_merge(clip2,'clip',cfg['lora_rank'])}
    lora_total=sum(x['merge_flops'] for x in lora.values());text_total=c1['flops']+c2['flops']
    result={'assumptions_sha256':sha(ass),'environment':{'torch':torch.__version__,'diffusers':__import__('diffusers').__version__,'transformers':__import__('transformers').__version__},
            'text_encoders':{'clip1':c1,'clip2':c2},'text_encoder_positions_per_fresh_conditioning':2*cfg['cfg_branches']*77,
            'lora_one_time_merge':lora,'profiles':{},'scenarios':[]}
    for res in cfg['resolution_scenarios']:
        with torch.device('meta'):
            latent=torch.empty(cfg['cfg_branches'],4,res//8,res//8);prompt=torch.empty(cfg['cfg_branches'],77,2048)
            hint=torch.empty(1,3,res,res)
            extra={'text_embeds':torch.empty(cfg['cfg_branches'],1280),'time_ids':torch.empty(cfg['cfg_branches'],6)}
        u,_=profile(lambda:unet(latent,999,encoder_hidden_states=prompt,added_cond_kwargs=extra),unet)
        v,_=profile(lambda:vae.decode(latent[:1]),vae)
        controls={}
        for k,model in cn.items():
            c,residuals=profile(lambda:model(latent,999,encoder_hidden_states=prompt,controlnet_cond=hint,added_cond_kwargs=extra,conditioning_scale=cfg['control_weight']),model)
            # Hook adds each scaled residual into accumulation and then UNet residuals.
            c['external_residual_add_flops']=2*sum(t.numel() for t in (*residuals.down_block_res_samples,residuals.mid_block_res_sample))
            c['flops']+=c['external_residual_add_flops'];controls[k]=c
        result['profiles'][str(res)]={'unet_cfg_evaluation':u,'vae_decode':v,'controlnet_cfg_evaluation':controls}
        for k,c in controls.items():
            for end in cfg['control_end_scenarios']:
                active=sum(i/cfg['steps'] <= end for i in range(cfg['steps']))
                scheduler_allowance=cfg['scheduler_scalar_ops_per_latent_position_step']*4*(res//8)**2*cfg['steps']
                total=cfg['steps']*u['flops']+active*c['flops']+v['flops']+text_total+lora_total+scheduler_allowance
                result['scenarios'].append({'resolution':res,'controlnet':k,'control_end':end,'active_control_calls':active,'unet_flops':cfg['steps']*u['flops'],'controlnet_flops':active*c['flops'],'vae_flops':v['flops'],'fresh_text_flops':text_total,'one_time_lora_merge_flops':lora_total,'sampler_and_cfg_scalar_allowance':scheduler_allowance,'compute_flops':total,'warm_model_and_text_flops':total-text_total-lora_total})
    chosen=next(x for x in result['scenarios'] if x['resolution']==cfg['resolution'] and x['controlnet']==cfg['controlnet'] and x['control_end']==cfg['control_end'])
    result['central']=chosen
    result['human']={'seconds':sum(cfg['human_components_seconds'].values()),'components_seconds':cfg['human_components_seconds'],'range_seconds':cfg['human_range_seconds'],'recorded_attempts':None}
    result['discard_sensitivity_only']=[{'discard_fraction':d,'expected_flops_per_retained_image':chosen['compute_flops']/(1-d)} for d in cfg['discard_fraction_scenarios']]
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'central':chosen,'human':result['human'],'clip_positions':result['text_encoder_positions_per_fresh_conditioning']},indent=2))

if __name__=='__main__':main()
