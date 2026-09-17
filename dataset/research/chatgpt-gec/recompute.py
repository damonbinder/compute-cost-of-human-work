"""Reconstruct one printed ChatGPT correction; requires tiktoken. No API calls."""
import argparse,base64,csv,hashlib,json
from pathlib import Path
import tiktoken
p=argparse.ArgumentParser()
for k in ['sources','inputs','timing','models','output']:p.add_argument('--'+k,type=Path,required=True)
a=p.parse_args();o=a.output.resolve();s=a.sources.resolve()
if o.exists() or s in o.parents:p.error('new output outside source evidence required')
j=json.loads(a.inputs.read_text());t=json.loads(a.timing.read_text())['records'][0]
assert j['source_sentence']==t['SRC'] and t['ID']=='C14_17_S'
ranks={base64.b64decode(x.split()[0]):int(x.split()[1]) for x in (s/'cl100k_base.tiktoken').read_bytes().splitlines()}
e=tiktoken.Encoding(name='retained-cl100k',pat_str=j['tokenizer_pattern'],mergeable_ranks=ranks,special_tokens={})
nt=lambda x:len(e.encode(x))
text=nt(j['instruction']+'\n'+j['source_sentence'])+nt(j['correction'])
total=text+j['estimated_system_and_chat_framing_tokens']+j['estimated_unprinted_response_tokens']
models=list(csv.DictReader(a.models.open()));m=next(x for x in models if x['model_id']=='chatgpt-gpt35-2022');coefficient=int(m['flops_per_token'])
r={'printed_text_tokens':text,'instruction_and_source_tokens':nt(j['instruction']+'\n'+j['source_sentence']),'printed_output_tokens':nt(j['correction']),'system_framing_assumption':j['estimated_system_and_chat_framing_tokens'],'unprinted_response_assumption':j['estimated_unprinted_response_tokens'],'tokens':total,'flops_per_token':coefficient,'compute_flops':total*coefficient,'human_time':t['Time'],'human_record':t,'scenarios_flops':{'printed_text_only':text*coefficient,'100_extra_system_tokens':(total+100)*coefficient,'one_additional_full_attempt':total*coefficient*2},'source_sha256':{str(x.relative_to(s)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(s.rglob('*')) if x.is_file()}}
o.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['source_sha256','human_record']},indent=2))
