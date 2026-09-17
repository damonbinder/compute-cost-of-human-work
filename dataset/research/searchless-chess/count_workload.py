"""Count original held-out legal actions and released-model matrix operations.
Requires chess. Reads BAG index and Beam UTF-8 length prefix, no model execution.
"""
import argparse,struct,json,hashlib,collections
from pathlib import Path
import chess
p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
assert not a.output.exists()
assert a.sources.resolve() not in a.output.resolve().parents and a.sources.resolve()!=a.output.resolve()
f=a.sources/'state_value_test.bag';b=f.read_bytes();start=struct.unpack('<Q',b[-8:])[0];ends=struct.unpack('<'+str((len(b)-start)//8)+'Q',b[start:]);hist=collections.Counter();begin=0;wins=[]
for end in ends:
 rec=b[begin:end];begin=end;i=n=shift=0
 while True:
  v=rec[i];i+=1;n|=(v&127)<<shift
  if v<128:break
  shift+=7
 assert len(rec)==i+n+8
 fen=rec[i:i+n].decode();board=chess.Board(fen);assert board.is_valid(),fen
 win=struct.unpack('>d',rec[i+n:])[0];assert 0<=win<=1
 wins.append(win);hist[board.legal_moves.count()]+=1
N=sum(hist.values());moves=sum(n*c for n,c in hist.items());S=79;V=1968;O=128
models={}
for name,L,D in [('9M',8,256),('136M',8,1024),('270M',16,1024)]:
 F=4*D;params=L*(4*D*D+3*D*F+4*D)+V*D+S*D+2*D+D*O+O
 per=L*(8*S*D*D+6*S*D*F+4*S*S*D)+2*S*D*O
 models[name]={'parameters':params,'flops_per_legal_action':per,'mean_flops_per_test_position':per*moves/N}
r={'source_sha256':hashlib.sha256(b).hexdigest(),'positions':N,'total_legal_actions':moves,'mean_legal_actions':moves/N,'legal_action_histogram':dict(sorted(hist.items())),'state_win_prob_above_99_percent':sum(w>.99 for w in wins),'models':models,'scope':'Released builder batch_size=1;79positions per legal action; full noncausal attention. Matrix ops only; Stockfish helper not included. These held-out positions are not the174 human games.'}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='legal_action_histogram'},indent=2))
