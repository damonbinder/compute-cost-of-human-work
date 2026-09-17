#!/usr/bin/env python3
"""Replay two first-deployment records. Original logs are never executed.

Requires tiktoken. Arguments identify all input/output roots; no cwd dependency.
"""
import argparse
import collections
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
import tiktoken

GUI = {'key', 'left_click', 'right_click', 'type', 'scroll', 'screenshot', 'wait', 'mouse_move'}
ENC = tiktoken.get_encoding('cl100k_base')


def tok(s):
    return len(ENC.encode(s or '', disallowed_special=()))


def stamp(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()


def final_diff(stderr):
    assert 'file update:\ndiff --git ' in stderr
    return stderr.rsplit('file update:\n', 1)[1].split('\ntokens used\n')[0].strip('\n')


def apply_diff(old, diff):
    """Strict unified-diff application, including old/new hunk length checks."""
    lines = old.splitlines()
    out, cursor = [], 0
    patches = diff.splitlines()
    j = 0
    while j < len(patches):
        m = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', patches[j])
        if not m:
            j += 1
            continue
        oldpos, oldn, newpos, newn = [int(v) if v is not None else 1 for v in m.groups()]
        start = oldpos - 1 if oldn else oldpos
        assert start >= cursor
        out.extend(lines[cursor:start]); cursor = start
        consumed = produced = 0
        j += 1
        while j < len(patches) and not patches[j].startswith('@@ '):
            s = patches[j]
            if not s or s.startswith('diff --git'):
                break
            if s[0] in ' -':
                assert cursor < len(lines) and lines[cursor] == s[1:], (cursor, lines[cursor:cursor+1], s)
                cursor += 1; consumed += 1
            if s[0] in ' +':
                out.append(s[1:]); produced += 1
            j += 1
        assert (consumed, produced) == (oldn, newn), (consumed, produced, oldn, newn)
    out.extend(lines[cursor:])
    result = '\n'.join(out) + '\n'
    expected = re.search(r'^index [0-9a-f]+\.\.([0-9a-f]{40})', diff, re.M)
    assert expected, 'Expected original full git-blob hash in Codex diff'
    blob = result.encode()
    actual = hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()
    assert actual == expected.group(1), (actual, expected.group(1))
    return result


def vision_proxy():
    # Original CLIP ViT-L/14-336 configuration. One 336px crop, MAC=2.
    h, s, layers, mlp = 1024, 577, 24, 4096
    return 2*576*(14*14*3)*h + layers*(8*s*h*h + 4*s*h*mlp + 4*s*s*h) + 2*h*768


def run(source, selection, out):
    assert source.is_dir()
    assert out.resolve() != source.resolve() and not out.resolve().is_relative_to(source.resolve()), 'Output directory must be outside retained sources'
    config=json.loads((source/'models/clip-vit-large-patch14-336.json').read_text())['vision_config']
    assert [config[k] for k in ['hidden_size','intermediate_size','num_hidden_layers','image_size','patch_size']]==[1024,4096,24,336,14]
    image_size = selection['assumptions']['image_positions_per_screenshot']
    raw = json.loads((source/'village/sessions-2025-10-13.json').read_text())['sessions']
    events = json.loads((source/'village/events-2025-10-13-1.json').read_text())['events']
    byid = {s['id']: s for s in raw}
    results = []
    for p in selection['points']:
        sessions = [byid[s] for s in p['session_ids']]
        selected_events = sorted([e for e in events if e['data'].get('agentId', e['data'].get('speakerId')) == p['agent_id'] and selection['start'] <= e['createdAt'] <= p['end']], key=lambda e:e['createdAt'])
        turns = [t for s in sessions for t in s['turns'] if t['createdAt'] <= p['end']]
        native, session_detail, helpers = [], [], []
        seen = set()
        screenshots = []
        graphical_increments = []
        for s in sessions:
            call_rows, image_spans, prev = [], [], None
            for t in s['turns']:
                assert t['createdAt'] <= p['end']
                m = t['agentMessage'] or {}; u = m.get('usage', {})
                i, c, r, o = [u.get(k,0) for k in ['input_tokens','cache_creation_input_tokens','cache_read_input_tokens','output_tokens']]
                if not i+c+r+o:
                    # The synthetic initial mouse move is not a model invocation.
                    prev = (0, 0, (t.get('agentAction') or {}).get('action', 'bash'))
                    continue
                assert m.get('id') and m['id'] not in seen
                seen.add(m['id'])
                full = i+c+r
                if prev and (prev[0] == 0 or prev[2] in GUI):
                    if prev[0]: graphical_increments.append(full-prev[0]-prev[1])
                    # Native input increases after GUI actions support ~1000 image
                    # positions. Put the new screenshot at the end of this input;
                    # exact image placement and serialization are not exported.
                    # Keep estimated images disjoint and outside the previous
                    # input/output positions. A larger image-size scenario must
                    # not create impossible negative text counts.
                    lower = prev[0]+prev[1] if prev and prev[0] else 0
                    image_spans.append((max(lower, full-image_size), full))
                    screenshots.append(t['id'])
                assert all(end <= full for _,end in image_spans), 'Unexpected prompt shrink: inspect retained image history'
                image_fresh = sum(max(0, end-max(start,r)) for start,end in image_spans)
                assert image_fresh <= i+c
                row = {'turn_id':t['id'], 'message_id':m['id'], 'input':i, 'creation':c, 'read':r, 'output':o, 'image_context_estimate':sum(end-start for start,end in image_spans), 'image_fresh_estimate':image_fresh}
                native.append(row);call_rows.append(row)
                prev=(full,o,(t.get('agentAction') or {}).get('action','bash'))
                a=t.get('agentAction') or {}; command=a.get('command','')
                if re.search(r'\bcodex\s+exec\b',command):
                    stderr=t.get('error') or ''
                    usage=re.search(r'tokens used\s+([\d,]+)\s*$',stderr)
                    if usage:
                        assert 'model: gpt-5-codex' in stderr
                        fresh=int(usage.group(1).replace(',',''))
                        helpers.append({'turn_id':t['id'],'fresh_text_tokens':fresh,'basis':'native_blended_total'})
                    else:
                        assert 'timed out: bash has not returned' in stderr
                        helpers.append({'turn_id':t['id'],'fresh_text_tokens':selection['assumptions']['missing_timeout_helper_fresh_tokens'],'basis':'timeout_estimate'})
            stop = [e for e in selected_events if e['data']['actionType']=='STOP_USING_COMPUTER' and e['createdAt']>=s['turns'][-1]['createdAt']]
            assert stop
            e=stop[0];summary=e['data']['summary'];last=call_rows[-1]
            full_last=last['input']+last['creation']+last['read']+last['output']
            session_detail.append({'session_id':s['id'],'stop_event':e['id'],'calls':len(call_rows),'summary_output_tokens_estimate':tok(summary),'summary_input_positions_estimate':full_last,'summary_image_positions_estimate':last['image_context_estimate']})
        # Some computer turns send a chat copy. It is the same invocation.
        mirrors=[];outside=[]
        for e in selected_events:
            d=e['data']
            matches=[t for t in turns if (t.get('agentAction') or {}).get('action')=='send_message_back_to_chat' and (t.get('agentAction') or {}).get('content')==d.get('content') and abs(stamp(e['createdAt'])-stamp(t['createdAt']))<10]
            if matches:
                assert len(matches)==1
                u=matches[0]['agentMessage']['usage']
                assert (d['inputTokens'], d['outputTokens'])==(u['input_tokens'],u['output_tokens'])
                mirrors.append({'event_id':e['id'],'turn_id':matches[0]['id']})
            elif 'inputTokens' in d:
                outside.append(e)
        # Controller actions can emit START plus TALK for a single call. Retain
        # one usage record for matching actor/counters within one second.
        controller=[];controller_duplicates=[]
        for e in outside:
            d=e['data'];matches=[x for x in controller if (x['data']['inputTokens'],x['data']['outputTokens'])==(d['inputTokens'],d['outputTokens']) and abs(stamp(x['createdAt'])-stamp(e['createdAt']))<1]
            if matches:controller_duplicates.append({'event_id':e['id'],'same_call_as':matches[0]['id']})
            else:controller.append(e)
        totals={k:sum(r[k] for r in native) for k in ['input','creation','read','output','image_fresh_estimate']}
        control_tokens=sum(e['data']['inputTokens']+e['data']['outputTokens'] for e in controller)
        summary_positions=sum(s['summary_input_positions_estimate']+s['summary_output_tokens_estimate'] for s in session_detail)
        summary_images=sum(s['summary_image_positions_estimate'] for s in session_detail)
        helper_tokens=sum(h['fresh_text_tokens'] for h in helpers)
        native_fresh=totals['input']+totals['creation']+totals['output']
        primary_positions=native_fresh+control_tokens+summary_positions
        image_positions=totals['image_fresh_estimate']+summary_images
        text_tokens=primary_positions-image_positions+helper_tokens
        # 1024x768 screenshots, represented by twelve336px tiles with this proxy.
        frontend=vision_proxy()*selection['assumptions']['vision_crops_per_computer_call']*image_positions/image_size
        flops=2*p['active_parameters']*primary_positions+2*selection['helper']['active_parameters']*helper_tokens+frontend
        sensitivity={
            'full_native_prefix_including_known_reads':flops+2*p['active_parameters']*totals['read'],
            'no_extra_consolidation_inference':flops-2*p['active_parameters']*summary_positions-vision_proxy()*12*summary_images/image_size,
            'double_consolidation_input':flops+2*p['active_parameters']*sum(s['summary_input_positions_estimate'] for s in session_detail),
            'unexported_controller_cache_creation_add_one_mean_observed_controller_input_per_call':flops+2*p['active_parameters']*sum(e['data']['inputTokens'] for e in controller),
            'frontend_one_crop':flops-frontend+frontend/12,
            'frontend_24_crops':flops+frontend,
            'half_all_active_parameters':(flops-frontend)*0.5+frontend,
            'double_all_active_parameters':(flops-frontend)*2+frontend,
        }
        missing=sum(h['basis']=='timeout_estimate' for h in helpers)
        for n in selection['assumptions']['missing_timeout_helper_fresh_tokens_sensitivity']:
            sensitivity[f'helper_timeout_{n}_fresh_tokens']=flops+2*selection['helper']['active_parameters']*missing*(n-selection['assumptions']['missing_timeout_helper_fresh_tokens'])
        results.append({**p,'native_calls':len(native),'native_totals':totals,'native_rows':native,'chat_mirrors':mirrors,'controller_duplicate_events':controller_duplicates,'controller_events':[{'id':e['id'],'type':e['data']['actionType'],'input':e['data']['inputTokens'],'output':e['data']['outputTokens']} for e in controller], 'controller_tokens':control_tokens,'sessions':session_detail,'helpers':helpers,'helper_text_tokens':helper_tokens,'summary_positions':summary_positions,'primary_positions':primary_positions,'image_positions_estimate':image_positions,'text_tokens_estimate':text_tokens,'frontend_flops_estimate':frontend,'compute_flops':flops,'human_time':sum(p['human_minutes'].values())*60,'screenshot_insertions':len(screenshots),'graphical_input_increments_net_of_previous_output':graphical_increments,'sensitivity_flops':sensitivity})
    # Reconstruct the actual initial artifacts, never execute their scripts.
    allturns={t['id']:t for s in raw for t in s['turns']}
    opus=apply_diff('',final_diff(allturns['b4b2eea4-1c8a-4f3d-ba9c-08a24a95360c']['error']))
    assert opus.encode() == (source/'village/opus41-site-current.html').read_bytes()
    sonnet=allturns['f44c8f49-96cb-44a0-9b1f-9c79b0e719ec']['output'].rstrip('\n')+'\n'
    for tid in ['df96c52c-72b0-45b7-b0cf-e42ffdaa7c16','5c870fa1-e02c-461d-a46d-ca9f13d4fb06','6d1d96cd-8510-4335-a157-7bce8a8e9e72','442c249a-1488-4fc9-a3a0-796b000246b7','fdbdb892-e8d3-4215-b050-7ccd039c672f']:
        sonnet=apply_diff(sonnet,final_diff(allturns[tid]['error']))
    out.mkdir(parents=True,exist_ok=True)
    for name,content in [('opus41-first-site.html',opus),('sonnet45-first-site.html',sonnet)]:
        (out/name).write_text(content)
    result={'points':results,'vision_proxy_flops_per_crop':vision_proxy(),'artifact_sha256':{n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ['opus41-first-site.html','sonnet45-first-site.html']}}
    (out/'calculations.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps([{k:r[k] for k in ['point_id','native_calls','controller_tokens','helper_text_tokens','summary_positions','primary_positions','image_positions_estimate','text_tokens_estimate','compute_flops','human_time']} for r in results],indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,required=True);ap.add_argument('--selection',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);a=ap.parse_args()
    run(a.source_dir,json.loads(a.selection.read_text()),a.output_dir)
