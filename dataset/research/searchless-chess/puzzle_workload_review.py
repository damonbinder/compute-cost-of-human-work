#!/usr/bin/env python3
"""Independent reference-path and model-matrix count. No weights/model execution.
Python3 + chess (pip install chess). Reads retained PGN/FEN/moves and source files.
Usage: python3 -B puzzle_workload_review.py --sources /path/to/sources --output /path/to/new.json
"""
import argparse, collections, csv, hashlib, io, json, math, struct
from pathlib import Path
import chess
import chess.pgn

def action_vocabulary():
    moves = set()
    for a in chess.SQUARES:
        for b in chess.SQUARES:
            dx = abs(chess.square_file(a)-chess.square_file(b)); dy = abs(chess.square_rank(a)-chess.square_rank(b))
            if a != b and (dx==0 or dy==0 or dx==dy or (dx,dy) in [(1,2),(2,1)]):
                moves.add(chess.square_name(a)+chess.square_name(b))
    for r,nr in [(1,0),(6,7)]:
        for f in range(8):
            for nf in [f-1,f,f+1]:
                if 0<=nf<8:
                    for p in 'qrbn':moves.add(chess.square_name(chess.square(f,r))+chess.square_name(chess.square(nf,nr))+p)
    assert len(moves)==1968
    return moves

def count_model(layers, width):
    S=79; F=4*width; O=128
    parameter_ledger={'token_embeddings':1968*width,'position_embeddings':S*width,'attention_qkvo':layers*4*width**2,'gated_mlp':layers*3*width*F,'layer_norms':layers*4*width+2*width,'output_weight_bias':width*O+O}
    flop_ledger={'attention_projections':layers*4*2*S*width**2,'attention_qk_and_av':layers*2*2*S*S*width,'gated_mlp_matrices':layers*3*2*S*width*F,'output_matrix_all_positions':2*S*width*O}
    return {'parameters':sum(parameter_ledger.values()),'parameter_ledger':parameter_ledger,'matrix_flops_per_action':sum(flop_ledger.values()),'matrix_flop_ledger':flop_ledger}

def bag_positions(file):
    b=file.read_bytes(); start=int.from_bytes(b[-8:],'little'); limits=[int.from_bytes(b[x:x+8],'little') for x in range(start,len(b),8)]
    assert limits[-1]==start and len(limits)==len(set(limits))
    hist=collections.Counter();begin=0;wins=[]
    for end in limits:
        rec=b[begin:end];begin=end;i=0;length=0
        while rec[i]&128:length+=(rec[i]&127)<<(7*i);i+=1
        length+=rec[i]<<(7*i);i+=1
        fen=rec[i:i+length].decode();assert i+length+8==len(rec)
        board=chess.Board(fen);assert board.is_valid()
        wins.append(struct.unpack('>d',rec[-8:])[0]);hist[len(list(board.legal_moves))]+=1
    return {'positions':len(limits),'total_legal_actions':sum(k*v for k,v in hist.items()),'legal_action_histogram':dict(sorted(hist.items())),'state_win_prob_above_99_percent':sum(x>.99 for x in wins)}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();src=a.sources.resolve();out=a.output.resolve()
    if out==src or src in out.parents:p.error('output must be outside sources')
    vocab=action_vocabulary();records=[];mismatches=[];early_mates=[]
    with (src/'puzzles.csv').open(newline='') as f:
        rows=list(csv.DictReader(f))
    for index,row in enumerate(rows):
        game=chess.pgn.read_game(io.StringIO(row['PGN']));assert game is not None and not game.errors
        board=game.end().board();assert board.is_valid()
        fen_board=chess.Board(row['FEN']);assert fen_board.is_valid()
        if board.fen()!=fen_board.fen():mismatches.append({'index':index,'id':row['PuzzleId'],'pgn_fen':board.fen(),'source_fen':fen_board.fen()})
        assert board.board_fen()==fen_board.board_fen() and board.turn==fen_board.turn and board.castling_rights==fen_board.castling_rights and board.fen().split()[3]==fen_board.fen().split()[3]
        counts=[];moves=row['Moves'].split();assert len(moves)%2==0
        for i,u in enumerate(moves):
            move=chess.Move.from_uci(u);assert move in board.legal_moves
            if i%2:
                legal=list(board.legal_moves);assert all(x.uci() in vocab for x in legal)
                counts.append(len(legal))
                # Successful alternative mate can end early; inspect that case.
                if i<len(moves)-1:
                    mating=[]
                    for other in legal:
                        board.push(other)
                        if board.is_checkmate():mating.append(other.uci())
                        board.pop()
                    if mating:early_mates.append({'index':index,'id':row['PuzzleId'],'solver_step':len(counts),'mate_moves':mating,'reference':u})
            board.push(move)
        records.append({'index':index,'puzzle_id':row['PuzzleId'],'rating':int(row['Rating']),'actions_by_solver_step':counts})
    assert len(records)==10000 and len({r['puzzle_id'] for r in records})==10000
    n=len(records);full=sum(sum(r['actions_by_solver_step']) for r in records);first=sum(r['actions_by_solver_step'][0] for r in records)
    hist=collections.Counter(len(r['actions_by_solver_step']) for r in records);stages=collections.Counter()
    for r in records:
        for j,c in enumerate(r['actions_by_solver_step']):stages[j+1]+=c
    models={}
    for name,L,D,accuracy in [('9M',8,256,.889),('136M',8,1024,.945),('270M',16,1024,.954)]:
        model=count_model(L,D);lo=0.;hi=1.
        for _ in range(70):
            q=(lo+hi)/2
            success=sum(count*q**k for k,count in hist.items())/n
            if success<accuracy:lo=q
            else:hi=q
        q=(lo+hi)/2;effective=sum(total*q**(j-1) for j,total in stages.items())
        failure_n=round(n*(1-accuracy));savings=sorted([sum(r['actions_by_solver_step'][1:]) for r in records],reverse=True);worst_min=(full-sum(savings[:failure_n]))/n
        unit=model['matrix_flops_per_action']
        model.update({'source_success_fraction':accuracy,'constant_per_decision_correct_probability':q,'calibrated_success_fraction':sum(count*q**k for k,count in hist.items())/n,'full_reference_mean_actions':full/n,'hazard_adjusted_mean_actions':effective/n,'hazard_to_full_ratio':effective/full,'nominal_failed_puzzles':failure_n,'adversarial_first_failure_min_mean_actions':worst_min,'full_reference_mean_flops':unit*full/n,'hazard_adjusted_mean_flops':unit*effective/n,'adversarial_first_failure_min_mean_flops':unit*worst_min})
        models[name]=model
    files=['puzzles.csv','state_value_test.bag','transformer.py','initial-transformer.py','neural_engines.py','initial-neural-engines.py','engine-constants.py','initial-engine-constants.py','tokenizer.py','initial-tokenizer.py','puzzles.py','initial-puzzles.py','utils.py','engine.py']
    result={'sources_sha256':{f:hashlib.sha256((src/f).read_bytes()).hexdigest() for f in files},'chess_version':chess.__version__,'puzzles':n,'mean_rating':sum(r['rating'] for r in records)/n,'rating_min':min(r['rating'] for r in records),'rating_max':max(r['rating'] for r in records),'solver_decisions':sum(k*c for k,c in hist.items()),'solver_decision_histogram':dict(sorted(hist.items())),'reference_legal_action_evaluations':full,'first_decision_legal_action_evaluations':first,'legal_actions_by_stage':dict(sorted(stages.items())),'pgn_fen_mismatches':mismatches,'early_mate_reference_states':early_mates,'held_out_bag_audit':bag_positions(src/'state_value_test.bag'),'models':models,'records':records}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['records','sources_sha256','held_out_bag_audit']},indent=2))
if __name__=='__main__':main()
