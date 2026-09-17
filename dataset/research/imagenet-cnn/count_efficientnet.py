"""Dominant matrix MACs, original EfficientNet-B7 at 600x600. No inference run."""
import math,json
stages=[(1,3,1,1,16),(2,3,2,6,24),(2,5,2,6,40),(3,3,2,6,80),(3,5,1,6,112),(4,5,2,6,192),(1,3,1,6,320)]
h=300; ci=64
parts=[dict(layer="stem",macs=h*h*3*ci*9)]
for stage,(repeats,kernel,stride,expand,out) in enumerate(stages):
 co=out*2
 for block in range(math.ceil(repeats*3.1)):
  st=stride if block==0 else 1; hidden=ci*expand; ho=math.ceil(h/st)
  expansion=h*h*ci*hidden if expand!=1 else 0
  depthwise=ho*ho*hidden*kernel*kernel
  squeeze=max(1,int(ci*0.25)); se=2*hidden*squeeze
  project=ho*ho*hidden*co
  parts.append(dict(layer=f"stage{stage+1}/block{block+1}",macs=expansion+depthwise+se+project))
  h=ho;ci=co
parts.append(dict(layer="head",macs=h*h*ci*2560+2560*1000))
print(json.dumps(dict(macs=sum(x['macs'] for x in parts),flops=2*sum(x['macs'] for x in parts),parts=parts),indent=2))
