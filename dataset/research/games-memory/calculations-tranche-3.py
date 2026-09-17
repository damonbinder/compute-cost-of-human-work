"""Recompute tranche3 estimates without modifying candidate records."""
import json
# 2 FLOPs/MAC, explicit small elementwise allowances.
def mlp(d,w,l):
 mac=d*w+(l-1)*w*w+w*4
 return 2*mac+2*l*w+4+100
agz_mac=361*17*256*9+38*361*256*256*9+361*256*2+722*362+361*256+361*256+256
agz_elementwise=39*361*256*3+19*361*256+3*361*3+256+362*5
agz_forward=2*agz_mac+agz_elementwise
calc={'gt2020_reported_input_width':32,'gt2020_forward':mlp(32,256,2),'gt2020_minute':mlp(32,256,2)*3600,'sophy_input_assumption':640,'sophy_forward':mlp(640,2048,4),'sophy_minute':mlp(640,2048,4)*600,'sophy_sensitivity_568_740_inputs':[mlp(i,2048,4)*600 for i in [568,740]],'agz_forward':agz_forward,'agz_1600_search':agz_forward*1600}
calc.update(go_human_own_clock=(120-83)*60/37, go_human_half_pondering=((120-83)+0.5*(120-78))*60/37, go_human_full_engagement=((120-83)+(120-78))*60/37, go_human_selected_estimate=120)
print(json.dumps(calc,indent=2))
