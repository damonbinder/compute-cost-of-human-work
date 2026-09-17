"""Operation estimates; prints JSON without editing candidate records."""
import json
# AlphaStar: start with all55M deployed weights used once, then add their spatial/entity reuse.
# This avoids reconstructing minor scalar-input widths from arbitrary one-hot vocabularies.
def alphastar(n=512,entity_input=1856,location_fraction=.75,selections=8,interval=.369):
 parts={'single_use_deployed_weights_mac':55e6}
 # Transformer3 layers: QKV, per-head128->256 projection summed across2heads,
 # feedforward256->1024->256. Input projection width is an explicit approximation.
 entity_weights=entity_input*256+3*(3*256*256+2*128*256+2*256*1024)+256*256+256*32
 parts['entity_linear_reuse_mac']=(n-1)*entity_weights
 parts['attention_mac']=3*2*n*n*256
 # Spatial encoder: concatenated52planes, stem1x1, downsample4x4,4two-convresblocks.
 convs=[(128,52,32,1),(64,32,64,4),(32,64,128,4),(16,128,128,4)]+[(16,128,128,3)]*8
 parts['spatial_reuse_mac']=sum((s*s-1)*a*b*k*k for s,a,b,k in convs)
 # Location decoder:128-channelstem,4resblocks, then transposedconv at input-grid sizes.
 loc=[(16,132,128,1)]+[(16,128,128,3)]*8+[(16,128,128,4),(32,128,64,4),(64,64,16,4),(128,16,1,4)]
 parts['location_reuse_mac']=location_fraction*sum((s*s-1)*a*b*k*k for s,a,b,k in loc)
 # Small recurrent pointer repeated unit selections; first use included in55M baseline.
 parts['pointer_repeats_mac']=(selections-1)*(1024*256+256*32+4*(32+32)*32+32*1024+n*32)
 # 2% allowance for BN/LN, nonlinearities, softmax, small gating and packing arithmetic.
 f=2*sum(parts.values())*1.02
 return dict(parts,flops_per_observation=f,observations_per_minute=60/interval,flops_per_minute=f*60/interval)
def llama(n):
 dense=2*405e9*n
 attention=2*126*16384*n*(n+1) # causal QK and AV, multiply+add separate
 return dict(tokens=n,dense=dense,causal_attention=attention,total=dense+attention)
# NoLiMa visible question specificity: diet, city, museum, broad country/region.
human=(16*60+12*240+6*180+24*480)/58
out={'alphastar':alphastar(),'alphastar_sensitivity':{'256_entities_half_location':alphastar(n=256,location_fraction=.5)['flops_per_minute'],'512_entities_all_location':alphastar(location_fraction=1)['flops_per_minute'],'latency_added_interval':alphastar(interval=.482)['flops_per_minute']},'literal_128k':llama(128020),'nolima_32k':llama(32110),'nolima_human_weighted_seconds':human,'nolima_human_selected_seconds':300}
print(json.dumps(out,indent=2))
