#!/usr/bin/env python3
"""Extract retained public chart literals; no JavaScript execution. Python 3 standard library.
python3 -B recompute.py --sources /path/to/sources --output /path/to/new-result.json
"""
import argparse, hashlib, json, math, re
from pathlib import Path

def literal(text, marker):
    start = text.index(marker) + len(marker) - 1
    assert text[start] == '{'
    depth = 0; quoted = False; escaped = False
    for end in range(start, len(text)):
        c = text[end]
        if quoted:
            if escaped: escaped = False
            elif c == '\\': escaped = True
            elif c == '"': quoted = False
        elif c == '"': quoted = True
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if not depth: break
    else: raise ValueError('Unterminated literal')
    # Convert only a data-only subset: quoted strings, identifiers as keys,
    # numeric literals and JSON punctuation. Reject executable JavaScript.
    raw = text[start:end+1]; pieces = []; i = 0
    decoder = json.JSONDecoder()
    while i < len(raw):
        if raw[i].isspace(): i += 1; continue
        if raw[i] == '"':
            _, n = decoder.raw_decode(raw[i:]); pieces.append(raw[i:i+n]); i += n; continue
        if raw[i] in '{}[]:,': pieces.append(raw[i]); i += 1; continue
        num = re.match(r'-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?', raw[i:])
        if num:
            token = num.group(); value = float(token)
            if not math.isfinite(value): raise ValueError('Nonfinite number')
            pieces.append(token.replace('-.', '-0.', 1) if token.startswith('-.') else '0'+token if token.startswith('.') else token)
            i += len(token); continue
        word = re.match(r'[A-Za-z_$][\w$]*', raw[i:])
        if word:
            token = word.group(); after = raw[i+len(token):].lstrip()
            if after.startswith(':'): pieces.append(json.dumps(token))
            elif token in ('true','false','null'): pieces.append(token)
            else: raise ValueError('Unsupported literal token '+token)
            i += len(token); continue
        raise ValueError('Unsupported literal character')
    return json.loads(''.join(pieces))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); src = args.sources.resolve(); out = args.output.resolve()
    if out == src or src in out.parents: parser.error('output must be outside the retained sources directory')
    if out.exists(): parser.error('output must be a new file')
    names = ['assets/26.kUxgg4v0.js','assets/DAnYm5vA.js','calculation-inputs.json']
    hashes = {n:hashlib.sha256((src/n).read_bytes()).hexdigest() for n in names}
    costs = literal((src/names[0]).read_text(), 'ct={')
    perf = literal((src/names[1]).read_text(), 'm={')['vb2']
    inputs = json.loads((src/names[2]).read_text())
    errors = {name:abs((x['avg_input_tokens']*x['price_per_mtok_in']+x['avg_output_tokens']*x['price_per_mtok_out'])/1e6-x['mean_cost']) for name,x in costs.items()}
    assert max(errors.values()) < 0.00501
    h = inputs['human_components']; unrounded = h['onboarding_hours']*3600+h['days']*h['daily_minutes']*60+h['weeks']*h['weekly_minutes']*60+h['exceptions_hours']*3600
    rows = []
    for config in inputs['models']:
        name = config['source_label']; x = costs[name]; p = perf[name]
        assert x['n'] == p['num_epochs'] == p['num_final_values']
        assert len(p['time_series']) == 365
        tokens = x['avg_input_tokens']+x['avg_output_tokens']; coefficient = 2*config['active_parameters']
        flops = tokens*coefficient
        rows.append({'point_id':config['point_id'],'model_id':config['model_id'],'source_label':name,'ai_attempts':x['n'],'input_tokens':x['avg_input_tokens'],'output_tokens':x['avg_output_tokens'],'tokens':tokens,'flops_per_token':coefficient,'compute_flops':flops,'human_time':inputs['human_central_hours']*3600,'money_balance_mean':p['final_value'],'money_balance_sem':p['final_value_sem'],'chart_input_output_cost':(x['avg_input_tokens']*x['price_per_mtok_in']+x['avg_output_tokens']*x['price_per_mtok_out'])/1e6,'parameter_scenario_flops':[tokens*2*v for v in config['parameter_scenario']],'fresh_input_fraction_scenarios':{str(f):coefficient*(x['avg_input_tokens']*f+x['avg_output_tokens']) for f in [1,0.5,0.1,0]},'one_million_unreported_output_flops':coefficient*1e6})
    result = {'source_hashes':hashes,'cost_records':len(costs),'cost_max_rounding_difference':max(errors.values()),'human_unrounded_components_seconds':unrounded,'human_scenario_seconds':[v*3600 for v in inputs['human_scenario_hours']],'rows':rows}
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'output':str(out),'rows':len(rows),'human_component_hours':unrounded/3600,'cost_records_checked':len(costs)}))
if __name__ == '__main__': main()
