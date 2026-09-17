#!/usr/bin/env python3
"""Analytic likelihood-negotiator recipe; standard library; no model execution."""
import argparse,collections,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=a.sources.resolve();out=a.output.resolve()
if out.exists() or out.is_relative_to(s):p.error('Output must be new and outside sources')
freq=collections.Counter();items=set();ctx=set()
for line in (s/'repo-2017/src/data/negotiate/train.txt').read_text().splitlines():
 t=line.split()
 def tag(x):return t[t.index('<'+x+'>')+1:t.index('</'+x+'>')]
 freq.update(tag('dialogue'));items.update(tag('output'));ctx.update(tag('input'))
V=len({x for x,n in freq.items() if n>20}|{'<eos>','<unk>','<selection>','<pad>'});J=len(items);C=len(ctx)
def gru(d,h):return 6*h*(d+h)+12*h # matrix MAC=2, approximate bias/gate scalar ops
def recipe(turns,rollouts=False,remaining_factor=1,lexical_convention=False):
 # Adopt original dialog.py summary convention: all turns include selection;
 # sent_len includes EOS/selection. Alternate treats7.6 as lexical words.
 T=turns*(7.6+1) if not lexical_convention else (turns-1)*(7.6+2)+2
 own_turns=turns/2; output=(T-turns)/2
 dialogue=T;generated=output;selection_calls=1;selection_positions=T
 if rollouts:
  # Ten candidate turns per own turn; five continuation/selection evaluations each.
  # Source-sized continuation prior: half of all nonterminal turns remain on average.
  candidate_positions=10*own_turns*(T/turns)
  candidate_outputs=10*output
  continuation_calls=50*(turns-1)/2
  remaining=min(100,(turns-1)/2*(T/turns)*remaining_factor)
  continuation_positions=continuation_calls*remaining
  dialogue=T/2+candidate_positions+continuation_positions
  generated=candidate_outputs+continuation_positions
  selection_calls=50*own_turns+1
  # Every rollout selection re-encodes real history+candidate+continuation.
  # For extended/shortened imagined endings, adjust completion length by the same extra remaining tokens.
  full_selection_length=T+remaining-(turns-1)/2*(T/turns)
  selection_positions=T+50*own_turns*full_selection_length
 c={'context':6*gru(64,64),'dialogue_reader_writer':dialogue*gru(320,128),'word_projection':generated*(2*128*256+2*256*V+8*V),'selection_birnn':selection_positions*2*gru(384,256),'selection_attention':selection_positions*(2*512*256+2*256+2*512),'selection_encoder':selection_calls*2*576*256,'selection_outputs':selection_calls*6*(2*256*J+J)}
 return {'flops':sum(c.values()),'components':c,'dialogue_positions':dialogue,'generated_tokens':generated,'selection_positions':selection_positions,'selection_calls':selection_calls,'ordinary_dialogue_positions':T}
# Unique trained matrices, reader/writer tied.
params=V*256+C*64+(3*64*(64+64)+6*64)+(3*128*(320+128)+6*128)+(128*256+256)+2*(3*256*(384+256)+6*256)+(512*256+256+256+1)+(576*256+256)+6*(256*J+J)
def human(turns):
 # Remove one EOS per spoken turn and terminal selection from reported sentence token totals.
 lexical=turns*7.6-turns
 own=lexical/2
 c={'scenario_valuation':20,'read_partner_words':own*60/240,'type_own_words':own*60/40,'plan_and_compose_turns':(turns-1)/2*5,'enter_final_allocation':5}
 return {'seconds':sum(c.values()),'components':c,'words_per_person':own,'quick':10+own*60/300+own*60/60+(turns-1)/2*2+3,'deliberate':40+own*60/180+own*60/25+(turns-1)/2*10+10}
r={'vocabulary':V,'output_labels':J,'context_symbols':C,'parameters_reconstructed':params,'likelihood':recipe(5.3),'rl_rollouts':recipe(7.2,True),'human_likelihood':human(5.3),'human_rl_rollouts':human(7.2),'scenarios':{'likelihood_lexical_words_convention':recipe(5.3,lexical_convention=True)['flops'],'rl_half_remaining':recipe(7.2,True,.5)['flops'],'rl_double_remaining':recipe(7.2,True,2)['flops'],'rl_cap100remaining':recipe(7.2,True,100)['flops']},'hashes':{str(f.relative_to(s)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(s.rglob('*')) if f.is_file()}}
out.write_text(json.dumps(r,indent=2)+'\n');print({k:v for k,v in r.items() if k!='hashes'})
