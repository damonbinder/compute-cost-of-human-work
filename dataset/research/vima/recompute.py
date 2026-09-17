"""VIMA single-object episode operation estimate; reads sources, no model execution.
Requires tokenizers. All scenario workload inputs are explicit below.
"""
import argparse,json,math,hashlib
from pathlib import Path
from tokenizers import Tokenizer,AddedToken
p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=a.sources.resolve();o=a.output.resolve()
assert not o.exists() and s not in o.parents and s!=o
prompt='Put the {dragged_obj_1} into the {base_obj}.'
t=Tokenizer.from_file(str(s/'t5-tokenizer.json'));t.add_tokens([AddedToken(x,single_word=True,normalized=True) for x in ['{dragged_obj_1}','{base_obj}']]);e=t.encode(prompt)
text_tokens=[x for x in e.tokens if not x.startswith('{')];P=len(text_tokens)+4 # two views per object placeholder
D=768;L=11
# Matrix multiply+add=2; scalar/nonlinear/normalization work not profiled.
def mlp(dims):return sum(2*x*y for x,y in zip(dims,dims[1:]))
vit=2*4*3*16**2*D+4*(24*5*D**2+4*5**2*D)+2*D**2
obj=vit+mlp([4,D,D,D])+mlp([2*D,D])
t5=12*(24*P*D**2+4*P**2*D)
prompt_cost=4*obj+4*mlp([D,D,D,D])+t5
act_encode=sum(mlp([i,256,256]) for i in [2,4,2,4])+mlp([1024,D])
act_decode=sum(mlp([D,512,512,b]) for b in [50,100,50,50,50,50]*2)
def controller(N):
 # Each block: cross Q/out, cross KV, GEGLU; self QKV/out, GEGLU.
 return L*((4*N+4*P)*D**2+4*N*P*D+24*N*D**2+8*N*D**2+4*N*N*D+24*N*D**2)
def detector(H,W,proposals=1000,detections=3,classes=80):
 # Default test resize then size-divisibility32 padding is an explicit proxy.
 H=math.ceil(H/32)*32;W=math.ceil(W/32)*32
 def conv(h,w,ci,co,k):return 2*h*w*ci*co*k*k
 h,w=H//2,W//2;res=conv(h,w,3,64,7);h,w=h//2,w//2;ci=64;levels=[]
 for stage,(blocks,bottleneck) in enumerate([(3,64),(4,128),(6,256),(3,512)]):
  for b in range(blocks):
   if stage and b==0:h=math.ceil(h/2);w=math.ceil(w/2)
   co=4*bottleneck
   res+=conv(h,w,ci,bottleneck,1)+conv(h,w,bottleneck,bottleneck,3)+conv(h,w,bottleneck,co,1)
   if b==0:res+=conv(h,w,ci,co,1)
   ci=co
  levels.append((h,w,co))
 fpn=sum(conv(h,w,c,256,1)+conv(h,w,256,256,3) for h,w,c in levels)
 levels.append((math.ceil(h/2),math.ceil(w/2),256))
 rpn=sum(conv(h,w,256,256,3)+conv(h,w,256,3,1)+conv(h,w,256,12,1) for h,w,_ in levels)
 box=proposals*mlp([256*7*7,1024,1024])+proposals*(mlp([1024,classes+1])+mlp([1024,4*classes]))
 mask=detections*(4*conv(14,14,256,256,3)+2*14*14*256*256*4+conv(28,28,256,classes,1))
 return {'resnet50':res,'fpn':fpn,'rpn':rpn,'box_head':box,'mask_head':mask,'padded_hw':[H,W],'total':res+fpn+rpn+box+mask}
def episode(calls,hw=(667,1333),proposals=1000,detections=3):
 det=detector(*hw,proposals,detections)
 # Cache encoded prompt and old observation/action tokens, recompute controller history.
 observation=calls*(2*det['total']+6*obj+6*mlp([D+2,D]))
 history=sum(controller(6*k+k-1) for k in range(1,calls+1))
 action=calls*act_decode+max(0,calls-1)*act_encode
 return {'prompt':prompt_cost,'observation':observation,'history_controller':history,'actions':action,'total':prompt_cost+observation+history+action}
def central(**kwargs):return .75*episode(1,**kwargs)['total']+.25*episode(2,**kwargs)['total']
r={'source_hashes':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(s.iterdir()) if x.is_file()},'prompt':prompt,'source_tokenizer_tokens':e.tokens,'text_tokens':len(text_tokens),'prompt_object_tokens':4,'t5_total_positions':P,'vision_crop_flops':vit,'object_view_flops':obj,'t5_flops':t5,'prompt_total_flops':prompt_cost,'detector_default_proxy':detector(667,1333),'episodes':{str(n):episode(n) for n in range(1,6)},'central_correction_assumption':'75% one-call and25% two-call equivalent cost mixture; an assumption, not observed episode lengths.','compute_flops':central(),'human_time':6,'human_scenarios_seconds':[3,12],'scenarios':{'one_call':episode(1)['total'],'five_call_demo_limit':episode(5)['total'],'native_image_resolution':central(hw=(128,256)),'100_RPN_proposals':central(proposals=100),'ten_mask_detections':central(detections=10)}}
o.parent.mkdir(parents=True,exist_ok=True);o.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['text_tokens','t5_total_positions','compute_flops','scenarios']},indent=2))
