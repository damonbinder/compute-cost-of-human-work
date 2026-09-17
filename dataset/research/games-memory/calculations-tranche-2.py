"""Two bounded game-operation estimates. Run from the batch directory."""
import json

def conv(s,a,b,k=3):return 2*s*s*a*b*k*k
def fc(a,b):return 2*a*b

def calculate():
 h=5*conv(48,128,128)+conv(24,128,256)+6*conv(24,256,256)+6*conv(12,256,256)+32*conv(6,256,256)
 g=conv(6,274,256)+32*conv(6,256,256)
 initial=h*1.02; recurrent=g*1.02
 search=initial+50*recurrent
 actor_roots=20_000_000_000/4
 learner=1_000_000*1024*3*(initial+5*recurrent)
 # Assumed 20 full checkpoint assessments including final no-op assessment;
 # another final human-start assessment. Each allocated its full episode cap.
 evaluation_roots=(20+1)*1000*27000
 muzero=actor_roots*search+learner+evaluation_roots*search
 # Released Maia-1500 tensor shapes and original Lc0 inference architecture.
 maia_conv=conv(8,112,64)+12*conv(8,64,64)+conv(8,64,64)+conv(8,64,80)+conv(8,64,32,1)
 maia_dense=fc(2048,128)+fc(128,3)+6*(fc(64,8)+fc(8,128))
 maia=(maia_conv+maia_dense)*1.02
 return {'muzero':{'representation_trunk':h,'dynamics_trunk':g,'initial_with_heads':initial,'recurrent_with_heads':recurrent,'search_root':search,'actor_roots':actor_roots,'actor':actor_roots*search,'learner':learner,'evaluation_roots_allowance':evaluation_roots,'evaluation_allowance':evaluation_roots*search,'total':muzero},'maia':{'convolutions':maia_conv,'dense_and_se':maia_dense,'total':maia}}
if __name__=='__main__':print(json.dumps(calculate(),indent=2))
