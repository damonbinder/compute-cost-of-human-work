#!/usr/bin/env python3
"""Read this source pickle symbolically. Never imports or invokes pickle globals."""
import pickletools
from pathlib import Path

def read(path):
 stack=[];memo={};mark=object()
 for op,arg,pos in pickletools.genops(Path(path).read_bytes()):
  n=op.name
  if n in {'PROTO','FRAME'}:continue
  if n in {'SHORT_BINUNICODE','BINUNICODE','BININT','BININT1','BININT2','SHORT_BINBYTES','BINBYTES'}:stack.append(arg)
  elif n=='NONE':stack.append(None)
  elif n in {'NEWTRUE','NEWFALSE'}:stack.append(n=='NEWTRUE')
  elif n=='MARK':stack.append(mark)
  elif n=='MEMOIZE':memo[len(memo)]=stack[-1]
  elif n in {'BINGET','LONG_BINGET'}:stack.append(memo[arg])
  elif n=='EMPTY_DICT':stack.append({})
  elif n=='EMPTY_LIST':stack.append([])
  elif n=='EMPTY_TUPLE':stack.append(())
  elif n=='STACK_GLOBAL':name=stack.pop();module=stack.pop();stack.append({'global':module+'.'+name})
  elif n in {'NEWOBJ','REDUCE'}:args=stack.pop();fn=stack.pop();stack.append({'constructor':fn,'args':args})
  elif n=='BUILD':state=stack.pop();stack[-1]['state']=state
  elif n=='SETITEM':v=stack.pop();k=stack.pop();stack[-1][k]=v
  elif n in {'TUPLE1','TUPLE2','TUPLE3'}:count=int(n[-1]);t=tuple(stack[-count:]);del stack[-count:];stack.append(t)
  elif n in {'TUPLE','APPENDS','SETITEMS'}:
   k=next(i for i in range(len(stack)-1,-1,-1) if stack[i] is mark);items=stack[k+1:];del stack[k:]
   if n=='TUPLE':stack.append(tuple(items))
   elif n=='APPENDS':stack[-1].extend(items)
   else:stack[-1].update(zip(items[::2],items[1::2]))
  elif n=='STOP':assert len(stack)==1;return stack[0]
  else:raise ValueError((n,pos))
 raise ValueError('Missing STOP')
if __name__=='__main__':
 import sys,pprint
 tree=read(sys.argv[1])
 def compact(x):
  if isinstance(x,bytes):return '<bytes '+str(len(x))+'>'
  if isinstance(x,list) and len(x)>15:return ['<list '+str(len(x))+'>']+[compact(y) for y in x[:3]]
  if isinstance(x,(list,tuple)):return [compact(y) for y in x]
  if isinstance(x,dict):return {k:compact(v) for k,v in x.items()}
  return x
 pprint.pp(compact(tree))

def records(path):
 import struct,math
 tree=read(path);blocks,axes=tree['state']['_mgr']['args']
 def array(x):
  _,shape,dtype,fortran,data=x['state'];assert not fortran
  typ=dtype['args'][0]
  if typ=='O8':values=data
  elif typ in {'i8','f8'}:
   assert dtype['state'][1]=='<';values=list(struct.unpack('<'+('q' if typ=='i8' else 'd')*math.prod(shape),data))
  else:raise ValueError(typ)
  assert len(values)==math.prod(shape);return shape,values
 _,cols=array(axes[0]['args'][1]['data']);shape,index=array(axes[1]['args'][1]['data']);out=[{} for _ in index]
 for block in blocks:
  values,positions=block['args'];shape,vals=array(values)
  if positions.get('constructor',{}).get('global')=='builtins.slice':where=list(range(*positions['args']))
  else:_,where=array(positions)
  assert shape==(len(where),len(out))
  for j,k in enumerate(where):
   for i,r in enumerate(out):r[cols[k]]=vals[j*len(out)+i]
 assert all(len(r)==len(cols) for r in out);return out
