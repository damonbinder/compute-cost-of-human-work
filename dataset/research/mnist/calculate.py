import json
terms={'C1':2*6*28*28*25,'S2':5*6*14*14,'C3':2*60*25*100,'S4':5*16*5*5,'C5':2*120*16*25,'F6':2*84*120,'scaled_tanh':7*8084,'RBF':10*(84+84+83),'normalization':2*32*32}
print(json.dumps({'terms':terms,'total_flops':sum(terms.values())},indent=2))
