"""Read-only VITS LJ architecture/workload audit; Python standard library only.
python recompute_vits.py --sources SOURCE_DIR [--output NEW_JSON]
Counts two operations per MAC. No weights, torch, or speech generation required.
"""
import argparse, ast, json, struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--output',type=Path);a=p.parse_args();s=a.sources
ids=['LJ003-0011','LJ016-0117','LJ001-0096','LJ031-0189','LJ002-0171']
def filelist(name):
    return {Path(l.split('|')[0]).stem:l.split('|')[1] for l in (s/name).read_text().splitlines()}
texts=filelist('filelists__ljs_audio_text_test_filelist.txt');phones=filelist('filelists__ljs_audio_text_test_filelist.txt.cleaned')
# Source string constants only; do not execute downloaded code.
constants={}
for node in ast.parse((s/'text__symbols.py').read_text()).body:
    if isinstance(node,ast.Assign) and isinstance(node.value,ast.Constant):
        constants[node.targets[0].id]=node.value.value
symbols=''.join(constants[k] for k in ['_pad','_punctuation','_letters','_letters_ipa'])
C=192;F=768
def conv_params(cin,cout,k,bias=True):return cin*cout*k+(cout if bias else 0)
encoder_params=len(symbols)*C+6*(4*conv_params(C,C,1)+2*9*(C//2)+conv_params(C,F,3)+conv_params(F,C,3)+4*C)+conv_params(C,2*C,1)
decoder_params=conv_params(192,512,7)+conv_params(32,1,7,False)
for cin,cout,k in [(512,256,16),(256,128,16),(128,64,4),(64,32,4)]:
    decoder_params+=conv_params(cin,cout,k)
    decoder_params+=sum(6*conv_params(cout,cout,rk) for rk in [3,7,11])
rows=[]
for i,id in enumerate(ids,1):
    h=(s/f'ss_{i:02d}_vits.wav.header').read_bytes()
    assert h[:4]==b'RIFF' and h[8:12]==b'WAVE'
    at=12;fmt=None;data=None
    while at+8<=len(h):
        tag=h[at:at+4];size=struct.unpack_from('<I',h,at+4)[0]
        if tag==b'fmt ':fmt=struct.unpack_from('<HHIIHH',h,at+8)
        if tag==b'data':data=size;break
        at+=8+size+(size%2)
    format,ch,sr,_,align,bits=fmt
    assert (format,ch,sr,align,bits)==(1,1,22050,2,16)
    samples=data//align;assert samples%256==0
    frames=samples//256;assert all(x in symbols for x in phones[id])
    N=2*len(phones[id])+1 # add_blank: blank before, between and after symbols
    # Six text-encoder layers: projections, conv FFN, ordinary/relative attention.
    text_encoder=6*(2*N*(4*C*C+2*3*C*F)+4*C*N*N+4*C*N*(2*N-1))+2*N*C*(2*C)
    dds_weights=3*(3*C+C*C)
    # Reverse removes one of four ConvFlow blocks; no posterior duration network.
    duration=2*N*(2*C*C+dds_weights+3*(C+dds_weights+C*29))
    # Two explicit dense alignment matmuls, each frames x N times N x C.
    alignment=4*frames*N*C
    # Four mean-only residual couplings, each with 4-layer WN (kernel 5).
    coupling_weights=96*C+C*96+4*(C*2*C*5)+3*(C*2*C)+C*C
    prior_flow=2*frames*4*coupling_weights
    decoder=2*frames*192*512*7;length=frames;stages=[]
    for cin,cout,k,u in [(512,256,16,8),(256,128,16,8),(128,64,4,2),(64,32,4,2)]:
        transposed=2*length*cin*cout*k
        length*=u
        residual=2*length*sum(6*cout*cout*rk for rk in [3,7,11])
        decoder+=transposed+residual
        stages.append({'output_positions':length,'channels':cout,'transpose_flops':transposed,'residual_flops':residual})
    decoder+=2*length*32*7
    parts={'text_encoder':text_encoder,'stochastic_duration':duration,'alignment':alignment,'prior_flow':prior_flow,'waveform_decoder':decoder}
    rows.append({'id':id,'text':texts[id],'cleaned_symbols':phones[id],'symbol_count':len(phones[id]),'text_positions':N,'samples':samples,'sample_rate':sr,'audio_seconds':samples/sr,'latent_frames':frames,'flops':parts,'total_flops':sum(parts.values()),'decoder_stages':stages})
out={'scope':'one synthesis per each of five original single-speaker demo texts at their released output lengths','encoder_parameters_folded':encoder_params,'waveform_decoder_parameters_folded':decoder_params,'total_text_positions':sum(r['text_positions']for r in rows),'total_audio_seconds':sum(r['audio_seconds']for r in rows),'total_latent_frames':sum(r['latent_frames']for r in rows),'total_flops':sum(r['total_flops']for r in rows),'rows':rows}
out['component_totals']={k:sum(r['flops'][k]for r in rows)for k in rows[0]['flops']}
out['human_component_estimate_seconds']=3*out['total_audio_seconds']+60
text=json.dumps(out,indent=2,ensure_ascii=False)
if a.output:
    with a.output.open('x')as f:f.write(text+'\n')
else:print(text)
