import csv,json
from pathlib import Path
b=Path(__file__).parent
# (name, output spatial width, input channels, output channels, kernel width)
layers=[('conv1',110,3,64,7),('conv2a',55,64,64,1),('conv2',55,64,192,3),('conv3a',28,192,192,1),('conv3',28,192,384,3),('conv4a',14,384,384,1),('conv4',14,384,256,3),('conv5a',14,256,256,1),('conv5',14,256,256,3),('conv6a',14,256,256,1),('conv6',14,256,256,3)]
mac={name:s*s*ci*co*k*k for name,s,ci,co,k in layers}
mac.update(fc1=12544*8192,fc2=4096*8192,fc7=4096*128)
core=4*sum(mac.values())
# A small explicit allowance for elementwise arithmetic, normalization and resizing.
flops=round(core*1.01)
(b/'calculation.json').write_text(json.dumps({'mac_per_image_by_layer':mac,'matrix_flops_per_pair':core,'elementwise_allowance_fraction':.01,'compute_flops':flops,'human_judgments_per_pair':10,'assumed_seconds_per_judgment':3,'human_time':30},indent=2)+'\n')
