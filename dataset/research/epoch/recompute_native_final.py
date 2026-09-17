"""Compute recorded workload and explicit unresolved-call scenarios for expansion 14."""
from collections import Counter, defaultdict
from pathlib import Path
import json
import math
import statistics

import argparse
cli=argparse.ArgumentParser();cli.add_argument('source_dir',type=Path);cli.add_argument('--output',type=Path,required=True);args=cli.parse_args()
P=args.source_dir
D=P/'native-final-accounting/expansion-14'
plan=json.loads((D/'native-audit-plan.json').read_text())
POST={'response_header_read_failure','response_body_read_failure','connection_reset_during_read','gateway_failure','empty_response_without_usage'}
REJECT={'rate_limit_rejection','overload_rejection','service_unavailable','connect_failure'}


def included(primary,v):
    inp=v.get('input_tokens',0);out=v.get('output_tokens',0);cr=v.get('input_tokens_cache_read',0);cw=v.get('input_tokens_cache_write',0);reason=v.get('reasoning_tokens',0);total=v.get('total_tokens',0)
    additional_reason=primary.startswith('google/') or primary=='epoch/gemini-3.5-flash'
    separate_cache=primary.startswith(('epoch/','anthropic/'))
    expected=inp+out+cw+(cr if separate_cache else 0)+(reason if additional_reason else 0)
    assert total==expected,(primary,v,expected)
    if not additional_reason:assert reason<=out,(primary,v)
    count=total-cr
    assert count>=0
    return count


out={}
for t in plan:
    pid=t['point_id'];f=P/pid;primary=t['primary']
    h=json.loads((f/'header.json').read_text());ss=json.loads((f/'summaries.json').read_text());audit=json.loads((D/(pid+'-events.json')).read_text())
    assert len({(str(s['id']),s['epoch']) for s in ss})==len(ss)
    sums=Counter();others=Counter();recorded=0;score_by=defaultdict(list)
    for s in ss:
        v=s.get('model_usage',{}).get(primary,{})
        if v:recorded+=included(primary,v);sums.update(v)
        for name,vv in s.get('model_usage',{}).items():
            if name!=primary:others[name]+=vv.get('total_tokens',0)
        for sc in s.get('scores',{}).values():
            assert sc['value'] in ['C','I','N'],(pid,sc['value'])
            score_by[str(s['id'])].append(1 if sc['value']=='C' else 0)
    if audit['scope']=='all_samples':
        assert audit['counts']['samples']==len(ss)
        assert audit['usage']==dict(sums)
    completed=h['results']['completed_samples']
    assert sum(map(len,score_by.values()))==completed
    score=statistics.mean(statistics.mean(v) for v in score_by.values())
    native_score=h['results']['scores'][0]['metrics']['accuracy']['value']
    assert math.isclose(score,native_score,abs_tol=1e-12)
    if dict(sums)==h['stats']['model_usage'][primary]:reconciliation='all summaries equal header'
    else:
        segment=[s for s in ss if s['started_at']>=h['stats']['started_at']];counter=Counter()
        for s in segment:counter.update(s['model_usage'][primary])
        assert dict(counter)==h['stats']['model_usage'][primary]
        reconciliation=f"Header matches final {len(segment)}-sample segment; full {len(ss)} summaries used."
    by=defaultdict(list);by_id=defaultdict(list);all_calls=[]
    for c in audit['successful_calls']:
        n=included(primary,c['usage']);by[(str(c['id']),c['epoch'])].append(n);by_id[str(c['id'])].append(n);all_calls.append(n)
    run_mean=statistics.mean(all_calls)
    def donor(e):
        key=(str(e['id']),e['epoch'])
        if '-swebench-' in pid and by[key]:return statistics.mean(by[key]),'same_issue_recorded_call_mean',len(by[key])
        if by_id[str(e['id'])]:return statistics.mean(by_id[str(e['id'])]),'same_question_recorded_call_mean',len(by_id[str(e['id'])])
        return run_mean,'run_recorded_call_mean',len(all_calls)
    known=Counter();corrections=[]
    for e in audit['errors']:
        assert e['kind'] in POST|REJECT,(pid,e)
        sends=1+e['sdk_retries']
        known[e['kind']]+=sends
        if e['kind'] in POST:
            n,basis,nobs=donor(e)
            corrections.append(dict(id=e['id'],epoch=e['epoch'],uuid=e['uuid'],kind=e['kind'],network_sends=sends,donor_tokens=n,donor_basis=basis,donor_calls=nobs,central_extra_tokens=0.5*sends*n,zero_to_one_call_extra_tokens=[0,sends*n]))
    post=sum(known[k] for k in POST);reject=sum(known[k] for k in REJECT)
    # Untyped retries inside an eventual successful event are separate SDK sends.
    # Use this run's exposed rejection/read-error mixture, not an assumption that all did inference.
    unresolved_fraction=post/(post+reject) if post+reject else 0.5
    hidden=0
    for e in audit['sdk_retry_events']:
        if not e['has_usage']:continue
        n,basis,nobs=donor(e);sends=e['sdk_retries'];hidden+=sends
        corrections.append(dict(id=e['id'],epoch=e['epoch'],uuid=e['uuid'],kind='untyped_sdk_retry_before_success',network_sends=sends,donor_tokens=n,donor_basis=basis,donor_calls=nobs,assumed_unresolved_fraction=unresolved_fraction,central_extra_tokens=0.5*unresolved_fraction*sends*n,zero_to_one_call_extra_tokens=[0,sends*n]))
    extra=sum(c['central_extra_tokens'] for c in corrections);upper=sum(c['zero_to_one_call_extra_tokens'][1] for c in corrections)
    all_ids={str(s['id']) for s in ss};unscored=sorted(all_ids-set(score_by))
    report={'primary':primary,'usage':dict(sums),'excluded_grader_tokens':dict(others),'recorded_included_tokens':recorded,'header_reconciliation':reconciliation,'summaries':len(ss),'completed':completed,'question_count':len(all_ids),'scored_question_count':len(score_by),'unscored_question_ids':unscored,'correct_completed_trials':sum(sum(v) for v in score_by.values()),'score':native_score,'score_reconstruction':'equal weight for each question with at least one completed trial; mean trial correctness within each question','individual_trial_accuracy':sum(sum(v) for v in score_by.values())/completed,'event_audit_scope':audit['scope'],'classified_error_network_sends':dict(known),'untyped_sdk_sends_before_success':hidden,'untyped_sdk_unresolved_fraction':unresolved_fraction,'corrections':corrections,'extra_tokens_central':extra,'extra_tokens_zero_to_one_call_scenario':[0,upper],'included_total_tokens':recorded+extra,'tokens':(recorded+extra)/completed,'tokens_zero_to_one_call_scenario':[recorded/completed,(recorded+upper)/completed],'missing_work_percent_of_recorded':100*extra/recorded,'run_recorded_call_mean':run_mean,'plan':h['plan']}
    out[pid]=report
    print(pid, 'tokens',round(report['tokens'],3),'correction',round(report['missing_work_percent_of_recorded'],2),'%', 'range', [round(v,3) for v in report['tokens_zero_to_one_call_scenario']])
args.output.write_text(json.dumps(out,indent=2)+'\n')
