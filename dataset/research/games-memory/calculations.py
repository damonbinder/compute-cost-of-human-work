"""Analytic neural operation recipes; run from this batch directory. No model execution."""
import json

def conv(side, ci, co, k=3): return 2*side*side*ci*co*k*k
def fc(a,b): return 2*a*b

def calculate():
    dqn_f=conv(20,4,32,8)+conv(9,32,64,4)+conv(7,64,64)+fc(3136,512)+fc(512,18)
    dqn_updates=(50_000_000-50_000)//4
    # Validation schedule transferred from original paper's ablations; conservative allowance.
    dqn_core=(4*32*dqn_updates+50_000_000+200*135_000+30*300*15)*dqn_f
    dqn_total=dqn_core*1.03
    h=conv(48,12,32)+2*conv(48,32,32)+2*conv(24,32,64)+conv(24,64,64)+2*conv(24,64,64)+2*conv(12,64,64)+2*conv(6,64,64)
    p=2*conv(6,64,64)+2*conv(6,64,16,1)+2*fc(576,32)+fc(32,601)+fc(32,18)
    reward=conv(6,64,16,1)+4*(fc(576,512)+fc(512,512))+fc(512,32)+fc(32,601)
    dynamics=conv(6,65,64)+2*conv(6,64,64)
    recurrent=dynamics+reward+p
    initial=h+p
    projection=fc(2304,1024)+2*fc(1024,1024)
    predictor=fc(1024,512)+fc(512,1024)
    train_example=3*(initial+5*(recurrent+projection+predictor))+5*(initial+projection)
    roots=120_000*6*(256+int(256*.99))
    search=initial+50*recurrent
    training=120_000*256*train_example
    collection=100_000*search
    evaluation=(13*32*3000+32*27000)*search
    efficient_total=1.03*(roots*search+training+collection+evaluation)
    alpha_core=conv(8,119,256)+40*conv(8,256,256)
    alpha_total=60*80_000*alpha_core*1.02
    return {'dqn':{'forward':dqn_f,'updates':dqn_updates,'core':dqn_core,'total':dqn_total},
      'efficientzero':{'representation':h,'prediction':p,'reward':reward,'dynamics':dynamics,'initial':initial,'recurrent':recurrent,'projection':projection,'predictor':predictor,'train_example':train_example,'reanalysis_roots':roots,'reanalysis_nodes':roots*50,'search_root':search,'reanalysis':roots*search,'learner':training,'collection':collection,'evaluation_allowance':evaluation,'total':efficient_total},
      'alphazero':{'trunk_forward':alpha_core,'forward_allowance':alpha_core*1.02,'evaluations':4_800_000,'total':alpha_total}}
if __name__=='__main__': print(json.dumps(calculate(),indent=2))
