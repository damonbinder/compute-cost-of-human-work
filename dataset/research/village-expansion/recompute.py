#!/usr/bin/env python3
"""Replay bounded Village artifact tasks; never execute commands from the logs.

Dependency: tiktoken. All paths are arguments. Original sources are read-only.
"""
import argparse
import collections
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
import tiktoken

ENC = tiktoken.get_encoding('cl100k_base')
GUI = {'mouse_move', 'screenshot', 'left_click', 'right_click', 'double_click',
       'triple_click', 'type', 'key', 'scroll', 'wait', 'left_click_drag'}


def tok(text):
    return len(ENC.encode(text or '', disallowed_special=()))


def stamp(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()


def patch_file(old, stderr):
    diff = stderr.rsplit('file update:\n', 1)[1].split('\ntokens used\n')[0]
    assert len(re.findall(r'^diff --git ', diff, re.M)) == 1
    lines, output, cursor = old.splitlines(), [], 0
    chunks = re.split(r'(?m)^@@ ', diff)[1:]
    for chunk in chunks:
        header, body = chunk.split('\n', 1)
        m = re.match(r'-(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', header)
        start, oldn, _, newn = [int(v) if v is not None else 1 for v in m.groups()]
        start = start - 1 if oldn else start
        assert start >= cursor
        output.extend(lines[cursor:start]); cursor = start
        used = made = 0
        for line in body.splitlines():
            if not line or line.startswith('\\ No newline'): continue
            assert line[0] in ' +-'
            if line[0] in ' -':
                assert lines[cursor] == line[1:]
                cursor += 1; used += 1
            if line[0] in ' +': output.append(line[1:]); made += 1
        assert (used, made) == (oldn, newn)
    output.extend(lines[cursor:])
    content = ('\n'.join(output) + '\n').encode()
    digest = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
    assert digest == re.search(r'(?m)^index \w+\.\.(\w+)', diff).group(1)
    return content.decode()


def vision_crop(config):
    c = config['vision_config']
    h, p, size, layers, mlp = [c[k] for k in ['hidden_size', 'patch_size', 'image_size', 'num_hidden_layers', 'intermediate_size']]
    patches = (size // p) ** 2; s = patches + 1
    return 2 * patches * (p*p*3) * h + layers * (8*s*h*h + 4*s*h*mlp + 4*s*s*h) + 2*h*config['projection_dim']


def main(source, selection_file, output):
    source, output = source.resolve(), output.resolve()
    assert source.is_dir() and not output.is_relative_to(source)
    assert source != output and selection_file.resolve().parent != output
    assert not output.exists(), 'Output directory must be new'
    selection = json.loads(selection_file.read_text()); a = selection['assumptions']
    manifest = json.loads((source/'manifest.json').read_text())
    for row in manifest:
        assert hashlib.sha256((source/row['file']).read_bytes()).hexdigest() == row['sha256'], row['file']
    output.mkdir(parents=True, exist_ok=False)
    dates = {ep['date'] for p in selection['points'] for ep in p['episodes']}
    sessions, events = {}, {}
    for date in sorted(dates):
        sessions[date] = json.loads((source/f'village/sessions-{date}.json').read_text())['sessions']
        events[date] = json.loads((source/f'village/events-{date}.json').read_text())['events']
    turns = {t['id']:t for ss in sessions.values() for s in ss for t in s['turns']}
    first = patch_file('', turns['39d93d1b-67fc-4686-8b17-f7b52f44cac4']['error'])
    first = patch_file(first, turns['8a874479-0fee-4352-9ace-22dd237956b5']['error'])
    (output/'gemini-first-site.html').write_text(first)
    puzzle = (source/'artifacts/puzzle-initial-index.html').read_text()
    assert len(puzzle.encode()) == 27653  # Original terminal screenshot corroborates this exact byte count.
    sm = json.loads((source/'artifacts/screener-main.js.map').read_text())
    app_files = {n:t for n,t in zip(sm['sources'], sm['sourcesContent']) if n in ['data/programs.js','components/EligibilityWizard.js','components/ProgramRecommendations.js','App.js']}
    assert len(app_files) == 4
    for name, text in app_files.items(): (output/('screener-'+name.replace('/','_'))).write_text(text)
    written = {
        '16b478db-bcbb-44df-b8ae-de57b35ce6d6': {'tokens':tok(puzzle),'basis':'Exact original 27,653-byte game HTML.'},
        '165ee7e5-32b2-4b92-a954-27762b028a3e': {'tokens':sum(tok(t) for t in app_files.values()),'basis':'Four original application sources from surviving deployment source map, corroborated against October screenshots; excludes React/vendor code.'},
        'c0ea374d-0e6d-419a-9716-e3f24e0ae77e': {'tokens':1800,'basis':'Twelve detailed JSON-Logic program records, estimated 150 text tokens each; final original file unavailable.'},
        '6670b035-c366-4e0e-91d8-6f46649591fd': {'tokens':1000,'basis':'Native session reports a 3.5 KB programs.json; estimated 1,000 tokens, broad sensitivity retained.'},
        'fbc4cb8c-7418-4080-9ac8-37d3694a357b': {'tokens':150,'basis':'One short Jest presence test explicitly specified in the original command.'},
    }
    for tid in ['baf608a6-6304-4709-be58-376c14b1a9ef','8b2d9c90-0e53-48e2-83f0-089f699e2d5b']:
        command=turns[tid]['agentAction']['text']
        code=command.split('component code:\n\n',1)[1].rsplit('" --skip-git-repo-check',1)[0]
        written[tid]={'tokens':tok(code),'basis':'Actual requested component code in terminal command.'}
    crop_flops=vision_crop(json.loads((source/'models/clip-vit-large-patch14-336.json').read_text()))
    results=[]
    for p in selection['points']:
        ss=[]; ee=[]
        for ep in p['episodes']:
            selected=[s for s in sessions[ep['date']] if s['id'] in ep['sessions']]
            assert len(selected)==len(ep['sessions'])
            ss.extend(selected)
            ee.extend(e for e in events[ep['date']] if ep['start']<=e['createdAt']<=ep['end'] and e['data'].get('agentId',e['data'].get('speakerId'))==p['agent_id'])
        ee.sort(key=lambda e:e['createdAt'])
        native=[]; summaries=[]; helpers=[]; coord=[]; session_details=[]; seen=set(); increments=[]
        for s in ss:
            last=None; spans=[]; own=[]; screenshots=0
            for t in s['turns']:
                m=t.get('agentMessage') or {}; action=t.get('agentAction') or {}
                if p['provider']=='gemini':
                    u=m.get('usageMetadata',{})
                    if not u: continue  # Synthetic initial mouse move.
                    assert m['modelVersion']=='gemini-2.5-pro-preview-06-05'
                    prompt=u['promptTokenCount']; out=u.get('candidatesTokenCount',0); thinking=u.get('thoughtsTokenCount',0); read=u.get('cachedContentTokenCount',0)
                    assert u['totalTokenCount']==prompt+out+thinking
                    modes={r['modality']:r['tokenCount'] for r in u['promptTokensDetails']}
                    cache={r['modality']:r['tokenCount'] for r in u.get('cacheTokensDetails',[])}
                    assert sum(modes.values())==prompt and sum(cache.values())==read
                    image=modes.get('IMAGE',0); fresh_image=image-cache.get('IMAGE',0)
                    assert fresh_image>=0
                    row={'turn_id':t['id'],'full_input':prompt,'fresh_input':prompt-read,'cache_read':read,'cache_creation':0,'output':out+thinking,'reasoning':thinking,'full_image':image,'fresh_image':fresh_image,'image_basis':'native_modality_counts'}
                    if action.get('action')=='get_pixel_coords_of_element':
                        text=a['coordinate_helper_system_text_tokens']+tok(action['description'])+a['coordinate_helper_output_tokens']
                        coord.append({'turn_id':t['id'],'text_tokens':text,'image_positions':a['coordinate_helper_image_positions'],'active_parameters':p['active_parameters'],'basis':'Unidentified coordinate helper; one screenshot and short locator prompt/result, primary-model coefficient proxy.'})
                else:
                    u=m.get('usage',{})
                    i,c,r,o=[u.get(k,0) for k in ['input_tokens','cache_creation_input_tokens','cache_read_input_tokens','output_tokens']]
                    if i+c+r+o==0: continue
                    mid=m['id']; assert mid not in seen;seen.add(mid)
                    full=i+c+r
                    if last is None or last['action'] in GUI:
                        lower=last['full_input']+last['output'] if last else 0
                        # Output may contain thinking not returned in the next input.
                        lower=min(lower, full)
                        spans.append((max(lower,full-a['anthropic_image_positions_per_screenshot']),full));screenshots+=1
                        if last: increments.append(full-last['full_input']-last['output'])
                    assert all(end<=full for _,end in spans), 'Inspect actual context trimming before applying span approximation.'
                    image=sum(end-start for start,end in spans)
                    fresh_image=sum(max(0,end-max(start,r)) for start,end in spans)
                    assert fresh_image<=i+c
                    row={'turn_id':t['id'],'full_input':full,'fresh_input':i+c,'cache_read':r,'cache_creation':c,'output':o,'reasoning':0,'full_image':image,'fresh_image':fresh_image,'image_basis':'Estimated screenshot spans intersected with native cache boundary.'}
                row['action']=action.get('action','bash'); row['model']=p['model_id'];native.append(row);own.append(row);last=row
                cmd=action.get('command',action.get('text','')) or ''
                if re.search(r'\bcodex\s+exec\b',cmd):
                    stderr=t.get('error') or '';hit=re.search(r'tokens used\s+([\d,]+)\s*$',stderr)
                    if hit:
                        assert 'model: gpt-5-codex' in stderr and 'v0.46.0' in stderr
                        helpers.append({'turn_id':t['id'],'text_tokens':int(hit.group(1).replace(',','')),'basis':'Native Codex v0.46.0 blended_total: noncached input plus output.'})
                    else:
                        w=written[t['id']]
                        helpers.append({'turn_id':t['id'],'text_tokens':a['unlogged_helper_setup_and_reasoning_tokens']+tok(cmd)+a['unlogged_helper_written_code_multiplier']*w['tokens'],'written_tokens':w['tokens'],'command_tokens':tok(cmd),'basis':w['basis'],'assumed':True})
            assert own
            stops=[e for e in ee if e['data'].get('actionType')=='STOP_USING_COMPUTER' and e['createdAt']>=s['turns'][-1]['createdAt']]
            assert stops
            stop=stops[0]
            # Summary prose is separate from the brief STOP tool output. Its prompt/cache usage is absent.
            summaries.append({'session_id':s['id'],'stop_event':stop['id'],'input_positions':last['full_input']+last['output'],'output_tokens':tok(stop['data']['summary']),'image_positions':last['full_image'],'basis':'Full last context plus last output; separate summary call inferred from original scaffolding description and long summary/short STOP output.'})
            session_details.append({'session_id':s['id'],'native_calls':len(own),'last_row':last,'stop_event':stop['id'],'new_screenshot_estimate':screenshots})
        mirrors=[]; rawcontroller=[]
        selected_turns=[t for s in ss for t in s['turns']]
        for e in ee:
            d=e['data']; matches=[t for t in selected_turns if (t.get('agentAction') or {}).get('action')=='send_message_back_to_chat' and (t.get('agentAction') or {}).get('content')==d.get('content') and abs(stamp(t['createdAt'])-stamp(e['createdAt']))<10]
            if matches: mirrors.append({'event_id':e['id'],'turn_id':matches[0]['id']})
            elif 'inputTokens' in d:rawcontroller.append(e)
        controller=[];duplicates=[]
        for e in rawcontroller:
            d=e['data'];same=[v for v in controller if v['input']==d['inputTokens'] and v['output']==d['outputTokens'] and abs(stamp(v['createdAt'])-stamp(e['createdAt']))<1]
            if same:duplicates.append({'event_id':e['id'],'same_call_as':same[0]['event_id']});continue
            image=0
            if d['actionType']=='STOP_USING_COMPUTER':
                sd=next(v for v in session_details if v['stop_event']==e['id'])
                # Gemini event prompt counters include images. Anthropic event input counter omits cache fields;
                # retain its reported fresh counter and transfer the last call's fresh image share, capped by input.
                image=sd['last_row']['full_image'] if p['provider']=='gemini' else min(d['inputTokens'],sd['last_row']['fresh_image'])
            controller.append({'event_id':e['id'],'createdAt':e['createdAt'],'type':d['actionType'],'input':d['inputTokens'],'output':d['outputTokens'],'image_positions_estimate':image,'reasoning_estimate':a['controller_reasoning_tokens_per_gemini_call'] if p['provider']=='gemini' else 0})
        native_fresh=sum(x['fresh_input']+x['output'] for x in native)
        native_images=sum(x['fresh_image'] for x in native)
        controller_positions=sum(x['input']+x['output']+x['reasoning_estimate'] for x in controller)
        controller_images=sum(x['image_positions_estimate'] for x in controller)
        summary_positions=sum(x['input_positions']+x['output_tokens'] for x in summaries)
        summary_images=sum(x['image_positions'] for x in summaries)
        primary_positions=native_fresh+controller_positions+summary_positions
        primary_images=native_images+controller_images+summary_images
        helper_tokens=sum(h['text_tokens'] for h in helpers)
        coordinate_positions=sum(x['text_tokens']+x['image_positions'] for x in coord)
        image_size=258 if p['provider']=='gemini' else a['anthropic_image_positions_per_screenshot']
        image_equivalents=primary_images/image_size+len(coord)
        frontend=crop_flops*a['vision_crops_per_image']*image_equivalents
        primary_flops=2*p['active_parameters']*primary_positions
        helper_flops=2*a['helper_active_parameters']*helper_tokens+2*p['active_parameters']*coordinate_positions
        flops=primary_flops+helper_flops+frontend
        assumed_helper=sum(h['text_tokens'] for h in helpers if h.get('assumed'))
        sensitivity={
            'full_native_prefix_including_known_cache_reads':flops+2*p['active_parameters']*sum(n['cache_read'] for n in native),
            'no_separate_summary_calls':flops-2*p['active_parameters']*summary_positions-crop_flops*a['vision_crops_per_image']*summary_images/image_size,
            'twice_summary_input':flops+2*p['active_parameters']*sum(x['input_positions'] for x in summaries),
            'half_unlogged_Codex_work':flops-a['helper_active_parameters']*assumed_helper,
            'double_unlogged_Codex_work':flops+2*a['helper_active_parameters']*assumed_helper,
            'no_coordinate_helper':flops-2*p['active_parameters']*coordinate_positions-crop_flops*a['vision_crops_per_image']*len(coord),
            'one_frontend_crop_per_image':flops-frontend+frontend/a['vision_crops_per_image'],
            'double_frontend_crops':flops+frontend,
            'half_all_active_parameter_priors':(flops-frontend)/2+frontend,
            'double_all_active_parameter_priors':(flops-frontend)*2+frontend,
            'no_unexported_controller_prompt_work':flops-2*p['active_parameters']*sum(c['input'] for c in controller),
            'double_unexported_controller_prompt_work':flops+2*p['active_parameters']*sum(c['input'] for c in controller),
        }
        results.append({**p,'native_calls':len(native),'native_rows':native,'native_fresh_positions':native_fresh,'native_fresh_image_positions':native_images,'native_cache_reads':sum(n['cache_read'] for n in native),'controller':controller,'controller_duplicates':duplicates,'chat_mirrors':mirrors,'controller_positions':controller_positions,'summaries':summaries,'summary_positions':summary_positions,'helpers':helpers,'helper_text_tokens':helper_tokens,'coordinate_helpers':coord,'primary_positions':primary_positions,'primary_image_positions':primary_images,'primary_flops':primary_flops,'helper_flops':helper_flops,'frontend_flops':frontend,'compute_flops':flops,'tokens':primary_positions-primary_images+helper_tokens+sum(c['text_tokens'] for c in coord),'human_time':60*sum(p['human_minutes'].values()),'sensitivity_flops':sensitivity,'graphical_increments_net_of_output':increments})
    report={'points':results,'flops_per_CLIP_crop':crop_flops,'helper_written_code_inputs':written,'artifact_metrics':{'gemini_first_bytes':len(first.encode()),'gemini_first_tokens':tok(first),'gemini_current_equals_first':first==(source/'artifacts/gemini-site.html').read_text(),'puzzle_bytes':len(puzzle.encode()),'puzzle_tokens':tok(puzzle),'screener_application_tokens':sum(tok(t) for t in app_files.values()),'screener_program_count':len(re.findall(r"(?m)^    id: '",app_files['data/programs.js']))}}
    (output/'calculations.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps([{k:p[k] for k in ['point_id','native_calls','native_fresh_positions','helper_text_tokens','tokens','compute_flops','human_time']} for p in results],indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,required=True);ap.add_argument('--selection',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args()
    main(args.source_dir,args.selection,args.output_dir)
