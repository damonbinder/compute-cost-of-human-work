import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='3'
import tensorflow as tf,numpy as np,tflite,json,math,collections
from pathlib import Path
import argparse
parser=argparse.ArgumentParser(description="Recompute BirdNET graph operations from retained TFLite files.")
parser.add_argument("source_dir",type=Path,help="Directory containing audio-model.tflite and meta-model.tflite")
parser.add_argument("--output",type=Path,help="Optional JSON result path")
args=parser.parse_args()
names={v:k for k,v in vars(tflite.BuiltinOperator).items() if isinstance(v,int)}
results={}
for fn in ['audio-model','meta-model']:
 raw=(args.source_dir/(fn+'.tflite')).read_bytes();m=tflite.Model.GetRootAsModel(raw,0);g=m.Subgraphs(0)
 r=tf.lite.Interpreter(model_content=raw,experimental_preserve_all_tensors=True,experimental_op_resolver_type=tf.lite.experimental.OpResolverType.BUILTIN_WITHOUT_DEFAULT_DELEGATES)
 r.allocate_tensors(); inp=r.get_input_details()[0]
 r.set_tensor(inp['index'],np.ones(inp['shape'],dtype=np.float32)*0.1);r.invoke()
 details={x['index']:x for x in r.get_tensor_details()}
 def shape(i):return list(map(int,details[int(i)]['shape']))
 def size(i):return math.prod(shape(i))
 records=[]
 for i in range(g.OperatorsLength()):
  o=g.Operators(i);op=names[m.OperatorCodes(o.OpcodeIndex()).BuiltinCode()];ins=[int(x) for x in o.InputsAsNumpy() if x>=0];outs=list(map(int,o.OutputsAsNumpy()));n=size(outs[0]);val=0
  floating=details[outs[0]]['dtype'] in [np.float32,np.complex64]
  if op=='CONV_2D':val=2*n*math.prod(shape(ins[1])[1:])
  elif op=='DEPTHWISE_CONV_2D':val=2*n*math.prod(shape(ins[1])[1:3])
  elif op=='FULLY_CONNECTED':val=2*n*shape(ins[1])[-1]
  elif op=='RFFT2D':
   length=shape(ins[0])[-1];val=2.5*length*math.log2(length)*(size(ins[0])/length)
  elif op in ['MUL','ADD','SUB','DIV'] and floating:val=n
  elif op=='LOGISTIC':val=4*n
  elif op in ['POW','SIN']:val=n
  elif op=='MEAN':val=size(ins[0])
  elif op=='AVERAGE_POOL_2D':
   b=o.BuiltinOptions();p=tflite.Pool2DOptions();p.Init(b.Bytes,b.Pos);val=n*p.FilterHeight()*p.FilterWidth()
  # Min/max/Relu comparisons and integer shape operations are not floating-point arithmetic.
  if op=='CONV_2D':
   b=o.BuiltinOptions();p=tflite.Conv2DOptions();p.Init(b.Bytes,b.Pos)
  records.append({'i':i,'op':op,'inputs':[shape(x) for x in ins],'outputs':[shape(x) for x in outs],'flops':val})
 groups=collections.defaultdict(float)
 for z in records:groups[z['op']]+=z['flops']
 results[fn]={'total':sum(groups.values()),'by_op':dict(groups),'operations':records}
 print(fn,results[fn]['total'],dict(groups))
if args.output: args.output.write_text(json.dumps(results,indent=2)+'\n')
