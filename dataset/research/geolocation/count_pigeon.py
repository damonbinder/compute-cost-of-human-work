"""Reconstruct PIGEON inference arithmetic. Python standard library only.
Usage: python count_pigeon.py SOURCE_DIR OUTPUT_JSON
SOURCE_DIR contains clip-config.json from the original CLIP configuration.
"""
import argparse,hashlib,json,math,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('source_dir',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
a.source_dir=a.source_dir.resolve();a.output=a.output.resolve()
if a.output.exists():
    p.error('output already exists; choose a new output file')
if a.output==a.source_dir or a.source_dir in a.output.parents:
    p.error('output must be outside the evidence directory')
c=json.loads((a.source_dir/'clip-config.json').read_text())['vision_config']
bot_path=a.source_dir/'bot__chrome_extension__scripts__duel.js'
bot=bot_path.read_text()
# Only the initial capture sequence, excluding comments and helper functions.
capture=re.sub(r'//[^\n]*', '', bot.split('const apiResp = await fetch',1)[0])
random_waits=re.findall(r'await wait\(randomIntFromInterval\((\d+),\s*(\d+)\)\)',capture)
fixed_waits=[int(x) for x in re.findall(r'await wait\((\d+)\)',capture)]
if len(random_waits)!=1 or len(re.findall(r'await screenshot\(\)',capture))!=4:
    p.error('unexpected bot capture sequence; inspect source before calculating')
delay_low_ms,delay_high_ms=map(int,random_waits[0])
fixed_delay_s=sum(fixed_waits)/1000
delay_low_s=delay_low_ms/1000+fixed_delay_s
delay_high_s=delay_high_ms/1000+fixed_delay_s
mean_delay_s=(delay_low_s+delay_high_s)/2
# Supplement H.2: up to 15 seconds for the second player after the first guess.
# Full active use and bot-first ordering are assumptions, not observed timings.
response_window_s=15
available_time_s=mean_delay_s+response_window_s
human_estimate_s=5*math.ceil(available_time_s/5)
d=c['hidden_size'];m=c['intermediate_size'];L=c['num_hidden_layers'];q=c['image_size']//c['patch_size'];n=q*q+1
patch=2*q*q*c['patch_size']**2*c['num_channels']*d
# All four Q/K/V/output projections, then two MLP projections; bidirectional attention.
projections=L*(8*n*d*d+4*n*d*m)
attention=L*4*n*n*d
# Explicit small arithmetic convention: transcendental calls count once.
# QuickGELU x*sigmoid(1.702*x): 6 ops; layer norm approximately 8 per position;
# biases, residuals and score softmax are included separately.
small=L*(6*n*m+16*n*d+2*n*d+4*n*d+n*m+n*d+5*c['num_attention_heads']*n*n)
small+=8*n*d+8*d+n*d
per_image=patch+projections+attention+small
head=2*d*2203+2203+5*2203+4*d
# All training panoramas is a conservative retrieval-work allowance, not an
# asserted observed candidate count. Top-5 cells contain a subset of these.
# At most N cluster vectors plus N member vectors, 3*d distance arithmetic,
# plus four-view averaging of each member. N is ~100k per paper section 4.1.
retrieval_upper=100000*(2*(3*d+1)+4*d)
audit=dict(image_size=c['image_size'],image_positions=n,embedding_dim=d,layers=L,
           patch_flops=patch,projection_flops=projections,attention_flops=attention,
           small_arithmetic_flops=small,per_image_flops=per_image,images_per_guess=4,
           head_flops=head,neural_flops=4*per_image+head,
           retrieval_allowance_upper_flops=retrieval_upper,
           total_with_retrieval_allowance=4*per_image+head+retrieval_upper,
           reported_compute_flops=float(f'{(4*per_image+head+retrieval_upper):.3g}'),
           human_time_seconds=human_estimate_s,human_sensitivity_seconds=[5,60],
           bot_programmed_fixed_capture_seconds=fixed_delay_s,
           bot_programmed_delay_range_seconds=[delay_low_s,delay_high_s],
           bot_programmed_delay_mean_seconds=mean_delay_s,
           second_player_response_window_seconds=response_window_s,
           full_window_available_time_before_unmeasured_overhead_seconds=available_time_s,
           human_time_assumptions=['Released bot timing represents the experiment.',
                                   'Bot usually guesses first.',
                                   'Human works actively until the response deadline.',
                                   'Round available time up to the next five seconds; overhead is unmeasured.'],
           source_sha256={name:hashlib.sha256((a.source_dir/name).read_bytes()).hexdigest()
                          for name in ['clip-config.json',bot_path.name]})
with a.output.open('x') as out:
    out.write(json.dumps(audit,indent=2)+'\n')
print(json.dumps(audit,indent=2))
