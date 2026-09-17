#!/usr/bin/env python3
"""Reconstruct selected source records and bounded PEGASUS inference costs.
Requires sentencepiece. Does not unpickle objects, generate text, or load weights.
"""
import argparse,json,statistics,hashlib
from pathlib import Path
import sentencepiece as spm
from read_pickle_data import records

def main():
 p=argparse.ArgumentParser();p.add_argument('source_dir',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=a.source_dir
 if a.output.resolve().is_relative_to(s.resolve()):raise ValueError('Output must be outside source evidence')
 raw=records(s/'summaries_and_ratings.p');selected=[r for r in raw if r['task_id']==1];assert len(selected)==720
 ai=[r for r in selected if r['cond_str']=='AI-generated'];human=[r for r in selected if r['cond_str']=='Manual'];assert len(ai)==len(human)==120;assert {r['text_id'] for r in ai}=={r['text_id'] for r in human}
 for tid in {r['text_id'] for r in selected}:assert len({r['document'] for r in selected if r['text_id']==tid})==1
 cfg=json.loads((s/'hf-2021-config.json').read_text());h=cfg['d_model'];l=cfg['encoder_layers'];assert cfg['decoder_layers']==l;assert cfg['encoder_ffn_dim']==cfg['decoder_ffn_dim']==4*h;v=cfg['vocab_size'];b=cfg['num_beams'];cap=cfg['max_length']-1
 tok=spm.SentencePieceProcessor(model_file=str(s/'hf-spiece.model'))
 def flops(n,d):
  # Encoder runs once before expansion to beams. Cross-KV is cached per beam.
  enc=l*(24*n*h*h+4*n*n*h)
  crosskv=b*l*4*n*h*h
  dec=b*(l*(28*d*h*h+4*h*d*(d+1)/2+4*n*h*d)+2*h*v*d)
  return enc+crosskv+dec
 items=[]
 for r in ai:
  n=len(tok.encode(r['document']))+1;d=len(tok.encode(r['summary']))+1;assert n<=512 and d<=cap
  low=flops(n,d);high=flops(n,cap);items.append({'text_id':r['text_id'],'encoder_tokens':n,'winner_tokens_proxy':d,'lower_flops':low,'upper_flops':high,'midpoint_flops':(low+high)/2,'padded512_midpoint_flops':(flops(512,d)+flops(512,cap))/2,'decoder_positions_midpoint':b*(d+cap)/2})
 result={'selection':'task_id == 1, verified XSum half; task_str is corrupted for the other half','source_sha256':hashlib.sha256((s/'summaries_and_ratings.p').read_bytes()).hexdigest(),'documents':120,'human_attempts':120,'human_seconds':4.05*60,'human_time_statistic':'mean reported in Figure3','human_quality_mean':statistics.mean(r['overall'] for r in human),'ai_quality_mean':statistics.mean(r['overall'] for r in ai),'human_mean_summary_words':statistics.mean(len(r['summary'].split()) for r in human),'ai_mean_summary_words':statistics.mean(len(r['summary'].split()) for r in ai),'mean_document_words':statistics.mean(len(r['document'].split()) for r in ai),'compute_flops':statistics.mean(r['midpoint_flops'] for r in items),'lower_flops':statistics.mean(r['lower_flops'] for r in items),'upper_flops':statistics.mean(r['upper_flops'] for r in items),'padded512_midpoint_flops':statistics.mean(r['padded512_midpoint_flops'] for r in items),'tokens_decoder_processed':statistics.mean(r['decoder_positions_midpoint'] for r in items),'encoder_tokens_mean':statistics.mean(r['encoder_tokens'] for r in items),'winner_tokens_mean':statistics.mean(r['winner_tokens_proxy'] for r in items),'beam_size':b,'max_decoder_steps':cap,'judgment':'Midpoint of source-supported operation bounds, not an observed stopping-time expectation; model/library version, batching and original tokenization are not logged.','items':items}
 with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print({k:v for k,v in result.items() if k!='items'})
if __name__=='__main__':main()
