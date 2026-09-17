#!/usr/bin/env python3
"""Reconstruct 2023 completion prefixes, with explicit output/retry assumptions.
Dependencies: chess, tiktoken. No network or model calls. Source evidence read-only.
python3 -B workload_review.py --sources /path/to/sources --output /path/to/new.json
"""
import argparse, collections, csv, hashlib, importlib.metadata, json, re
from pathlib import Path
import chess, tiktoken

def max_allocated_work(count, calls, cap=4):
    # Up to four unsuccessful calls can precede a successful fifth call.
    total=0;assigned=0
    for c in sorted(calls,key=lambda x:x['input_tokens'],reverse=True):
        n=min(cap,count-assigned)
        if n<=0:break
        total+=n*(c['input_tokens']+10);assigned+=n
    return total,assigned

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();src=a.sources.resolve();out=a.output.resolve()
    if out==src or src in out.parents:p.error('output must be outside source evidence')
    enc=tiktoken.get_encoding('cl100k_base');model='gpt-3.5-turbo-instruct';games=[];tokens=[];terminals=[]
    for r in csv.DictReader((src/'logs__games.csv').open(newline='')):
        if model not in [r['player_one'],r['player_two']]:continue
        white=r['player_one']==model;color=chess.WHITE if white else chess.BLACK;side='player_one' if white else 'player_two';text=r['transcript'];first=re.search(r'(?m)^1\.',text);assert first
        audit_board=chess.Board();anomalies=[]
        for line in text.splitlines():
            lm=re.match(r'^(\d+)\.\s*(.*)$',line)
            if not lm:continue
            if audit_board.turn!=chess.WHITE or int(lm[1])!=audit_board.fullmove_number:anomalies.append({'line':line,'pre_ply':audit_board.ply()})
            parts=lm[2].split();assert len(parts)<=2
            for part in parts:
                if part not in ['1-0','0-1','1/2-1/2','*']:audit_board.push_san(part)
        clean=not anomalies
        header=text[:first.start()].removesuffix('\n');state=header;board=chess.Board();calls=[]
        for match in re.finditer(r'\S+',text[first.start():]):
            raw=match.group()
            if re.fullmatch(r'\d+\.',raw) or raw in ['1-0','0-1','1/2-1/2','*']:continue
            if board.turn==chess.WHITE:state+='\n'+str(board.fullmove_number)+'.'
            actual_prefix=text[:first.start()+match.start()].rstrip(' ')
            if clean:assert state==actual_prefix,(r['game_id'],board.ply())
            else:state=actual_prefix
            move=board.parse_san(raw)
            if board.turn==color:
                c={'game_id':r['game_id'],'pre_move_ply':board.ply(),'input_tokens':len(enc.encode(state)),'san':raw,'minimal_san_tokens':min(len(enc.encode(raw)),len(enc.encode(' '+raw))),'space_san_tokens':len(enc.encode(' '+raw)),'in_window':15<=board.ply()<=75,'clean_format':clean}
                calls.append(c);tokens.append(c)
            state+=' '+raw;board.push(move)
        # A failed white call is preceded by a move number, but no accepted SAN.
        if text!=state:
            assert board.turn==chess.WHITE and text==state+'\n'+str(board.fullmove_number)+'.',(r['game_id'],repr(text[-70:]),repr(state[-70:]))
            state=text
        terminal=(r[side+'_resignation']=='True' or r[side+'_failed_to_find_legal_move']=='True')
        reported=int(r[side+'_illegal_moves']);terminal_calls=5 if terminal else 0
        if terminal:
            assert board.turn==color and reported>=5
            term={'game_id':r['game_id'],'pre_move_ply':board.ply(),'input_tokens':len(enc.encode(state)),'assumed_wrapper_calls':5,'in_window':15<=board.ply()<=75,'flag':'resignation' if r[side+'_resignation']=='True' else 'failed_move'};terminals.append(term)
        residual=reported-terminal_calls;assert residual>=0
        mid=[c for c in calls if c['in_window']];fraction=len(mid)/len(calls)
        retry_in=residual*sum(c['input_tokens'] for c in mid)/len(calls)
        retry_n=residual*fraction;upper,n_upper=max_allocated_work(residual,mid)
        terminal_in=5*len(enc.encode(state)) if terminal and 15<=board.ply()<=75 else 0
        terminal_n=5 if terminal and 15<=board.ply()<=75 else 0
        games.append({'game_id':r['game_id'],'clean_format':clean,'format_anomalies':anomalies,'color':'white' if white else 'black','accepted_moves':len(calls),'middle_moves':len(mid),'input_tokens':sum(c['input_tokens'] for c in calls),'middle_input_tokens':sum(c['input_tokens'] for c in mid),'reported_illegal_counter':reported,'terminal_calls_at_known_prefix':terminal_calls,'nonterminal_counter_proxy':residual,'uniform_retry_middle_calls':retry_n,'uniform_retry_middle_input_tokens':retry_in,'maximum_retry_middle_total_tokens':upper,'maximum_retry_middle_calls':n_upper,'middle_terminal_input_tokens':terminal_in,'middle_terminal_calls':terminal_n})
    all_games=games;all_tokens=tokens
    games=[g for g in all_games if g['clean_format']];tokens=[c for c in all_tokens if c['clean_format']]
    middle=[c for c in tokens if c['in_window']];N=len(middle);inp=sum(c['input_tokens'] for c in middle);san=sum(c['minimal_san_tokens'] for c in middle);retry_in=sum(g['uniform_retry_middle_input_tokens'] for g in games);retry_n=sum(g['uniform_retry_middle_calls'] for g in games);terminal_in=sum(g['middle_terminal_input_tokens'] for g in games);terminal_n=sum(g['middle_terminal_calls'] for g in games)
    capout=N*10;total=inp+capout+retry_in+retry_n*10+terminal_in+terminal_n*10
    upper=inp+capout+sum(g['maximum_retry_middle_total_tokens'] for g in games)+terminal_in+terminal_n*10
    scenarios={'central_full_cap_uniform_reported_counter':total/N,'minimal_san_no_counter_work':(inp+san)/N,'cap_no_counter_work':(inp+capout)/N,'cap_half_counter_work':(inp+capout+(retry_in+retry_n*10)/2+terminal_in+terminal_n*10)/N,'cap_counter_allocated_highest_window_prefixes':upper/N,'central_plus_one_hidden_generated_position_per_call':(total+N+retry_n+terminal_n)/N}
    files=['logs__games.csv','historical-main.py','historical-gpt_query.py','historical-prompt.txt','review-early-main.py','review-early-gpt-query.py']
    result={'sources_sha256':{f:hashlib.sha256((src/f).read_bytes()).hexdigest() for f in files},'encoding':enc.name,'tiktoken_version':importlib.metadata.version('tiktoken'),'chess_version':chess.__version__,'games':len(games),'original_games':len(all_games),'excluded_format_games':[{'game_id':g['game_id'],'format_anomalies':g['format_anomalies'],'reported_illegal_counter':g['reported_illegal_counter']} for g in all_games if not g['clean_format']],'all182_color_assumption_sensitivity':{'accepted_moves':len(all_tokens),'input_tokens':sum(c['input_tokens'] for c in all_tokens),'middle_moves':sum(c['in_window'] for c in all_tokens),'middle_input_tokens':sum(c['input_tokens'] for c in all_tokens if c['in_window']),'reported_illegal_counter_total':sum(g['reported_illegal_counter'] for g in all_games),'central_tokens_per_accepted_middle_move':(sum(c['input_tokens']+10 for c in all_tokens if c['in_window'])+sum(g['uniform_retry_middle_input_tokens']+10*g['uniform_retry_middle_calls']+g['middle_terminal_input_tokens']+10*g['middle_terminal_calls'] for g in all_games))/sum(c['in_window'] for c in all_tokens)},'all_accepted_moves':len(tokens),'all_accepted_input_tokens':sum(c['input_tokens'] for c in tokens),'all_minimum_space_san_tokens':sum(c['space_san_tokens'] for c in tokens),'window_definition':'pre-move board.ply()15–75 inclusive (zero-based move index; board and API prefix before16th–76th game ply)','accepted_window_moves':N,'accepted_window_input_tokens':inp,'accepted_window_minimal_san_tokens':san,'estimated_accepted_window_output_tokens':capout,'reported_illegal_counter_total':sum(g['reported_illegal_counter'] for g in games),'nonterminal_counter_proxy_total':sum(g['nonterminal_counter_proxy'] for g in games),'terminal_known_prefix_records':terminals,'estimated_uniform_window_retry_calls':retry_n,'estimated_uniform_window_retry_input_tokens':retry_in,'estimated_uniform_window_retry_output_tokens':retry_n*10,'central_total_workload_tokens':total,'central_tokens_per_accepted_window_move':total/N,'token_scenarios_per_accepted_window_move':scenarios,'flops_by_parameter_scenario':{str(P):2*P*(total/N) for P in [7000000000,20000000000,175000000000]},'flop_workload_scenarios_at_7B':{k:2*7000000000*v for k,v in scenarios.items()},'games_records':games,'accepted_move_records':tokens}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['sources_sha256','games_records','accepted_move_records']},indent=2))
if __name__=='__main__':main()
