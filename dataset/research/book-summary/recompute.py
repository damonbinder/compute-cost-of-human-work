"""Offline replay: Python 3.10+ and tiktoken (reviewed with 0.14.0).
python recompute.py --sources SOURCE_DIR --config CONFIG_JSON --output NEW_JSON
No model calls or pickle deserialization. Outputs must be new files.
"""
import argparse, base64, hashlib, json, pickletools
from pathlib import Path
import tiktoken

R50K = r"'(?:[sdmt]|ll|ve|re)| ?\p{L}++| ?\p{N}++| ?[^\s\p{L}\p{N}]++|\s++$|\s+(?!\S)|\s"
CL100K = r"'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}++|\p{N}{1,3}+| ?[^\s\p{L}\p{N}]++[\r\n]*+|\s++$|\s*[\r\n]|\s+(?!\S)|\s"

def encoding(sources, name, pattern, expected):
    data = (sources / (name + '.tiktoken')).read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected
    ranks = {base64.b64decode(a): int(b) for a,b in (line.split() for line in data.splitlines())}
    return tiktoken.Encoding(name=name, pat_str=pattern, mergeable_ranks=ranks, special_tokens={})

def example_text(sources):
    # Inspect string opcodes only; never invoke pickle.load or constructors.
    ops = list(pickletools.genops((sources/'example_all_books.pkl').read_bytes()))
    allowed = {'PROTO','FRAME','EMPTY_DICT','SHORT_BINUNICODE','BINUNICODE','MEMOIZE','SETITEM','STOP'}
    assert all(op.name in allowed for op,_,_ in ops)
    values = [arg for op,arg,_ in ops if op.name == 'BINUNICODE']
    assert len(values) == 1
    return values[0]

def historical_chunk_lengths(text, enc, cap=4096):
    """Original token slicing and punctuation trimming, for the calibration text."""
    def truncate(value):
        original = value
        last = max(0, *(value.rfind(p) for p in '.?!'))
        if last:
            value = value[:last+1]
        while len(enc.encode(value)) > cap:
            indices = [i for i,c in enumerate(value) if c in '.?!']
            if len(indices) < 2:
                indices = [i for i,c in enumerate(value) if c in '.?!,']
            value = value[:indices[-2]+1]
        return value, original[len(value):]
    ids = enc.encode(text)
    chunks, remaining = [], ''
    for start in range(0,len(ids),cap):
        value, remaining = truncate(remaining + enc.decode(ids[start:start+cap]))
        chunks.append(value)
    while remaining:
        if len(enc.encode(remaining)) > cap:
            ids = enc.encode(remaining)
            remaining = ''
            for start in range(0,len(ids),cap):
                value, remaining = truncate(remaining + enc.decode(ids[start:start+cap]))
                chunks.append(value)
            chunks.append(remaining)
            remaining = ''
        else:
            chunks.append(remaining)
            break
    if len(chunks[-1]) < 30:
        chunks.pop()
    return [len(enc.encode(chunk)) for chunk in chunks]

def ratios(texts, gpt2, cl100k):
    g = sum(len(gpt2.encode(t)) for t in texts)
    c = sum(len(cl100k.encode(t)) for t in texts)
    w = sum(len(t.split()) for t in texts)
    return dict(gpt2_tokens=g, cl100k_tokens=c, words=w, cl100k_per_gpt2=c/g, words_per_gpt2=w/g)

def calculate(sources, config, enc, ratio, nonfinal=None, final=None, retry=None):
    count = lambda text: len(enc.encode(text))
    key = config['book']
    raw = json.loads((sources/'gpt4-4096-hier.json').read_text())[key]
    clean = json.loads((sources/'gpt4-4096-hier-cleaned.json').read_text())[key]
    bottom = raw['summaries_dict']['0']
    assert len(bottom) == 12 and len(raw['summaries_dict']['1']) == 1
    assert raw['final_summary'] == raw['summaries_dict']['1'][0] and clean != raw['final_summary']
    nonfinal = config['nonfinal_gpt2_tokens'] if nonfinal is None else nonfinal
    final = config['final_gpt2_tokens'] if final is None else final
    retry = config['discarded_hierarchical_work_fraction'] if retry is None else retry
    frame = config['chat_framing_tokens_per_call']
    source_gpt2 = 11*nonfinal + final
    source_input = source_gpt2*ratio['cl100k_per_gpt2']
    init = (sources/'prompts/init.txt').read_text()
    merge = (sources/'prompts/merge.txt').read_text()
    cleanup = (sources/'prompts/remove_artifacts.txt').read_text()
    init_overhead = count(init.format('',round(780*.65)))
    chunk_input = source_input + 12*(init_overhead+frame)
    chunk_outputs = sum(map(count,bottom))
    joined = '\n\n'.join(f'Summary {i+1}:\n\n{text}' for i,text in enumerate(bottom))
    merge_input = count(merge.format(joined,round(1200*.65)))+frame
    merge_output = count(raw['final_summary'])
    clean_input = count(cleanup.format(raw['final_summary']))+frame
    clean_output = count(clean)
    hierarchical = chunk_input+chunk_outputs+merge_input+merge_output
    discarded = retry*hierarchical
    total = hierarchical+discarded+clean_input+clean_output
    # Each API call is a fresh causal sequence; do not treat the whole book
    # workflow as one continuous 60K-token context.
    call_lengths = [(nonfinal if i < 11 else final)*ratio['cl100k_per_gpt2']
                    + init_overhead + frame + count(text)
                    for i,text in enumerate(bottom)]
    call_lengths.append(merge_input + merge_output)
    cleanup_length = clean_input + clean_output
    attended_pairs = sum(n*(n+1)/2 for n in call_lengths)*(1+retry)
    attended_pairs += cleanup_length*(cleanup_length+1)/2
    context = attended_pairs/total
    model = config['model']
    def flops(active, layers, width):
        return 2*active*total + 4*layers*width*attended_pairs
    active = float(model['active_parameters'])
    layers, width = int(model['attention_layers']), float(model['attention_width'])
    central_flops = flops(active,layers,width)
    bounds = []
    for field in ['active_parameters_low','active_parameters_high']:
        n = float(model[field])
        dense = max(8,round((n/196608)**(1/3)))
        l = max(1,round(dense*config['attention_family_share']))
        bounds.append(flops(n,l,128*dense))
    source_words = source_gpt2*ratio['words_per_gpt2']
    reading = source_words/config['human_reading_wpm']
    writing = sum(config['human_estimated_component_minutes'].values())
    rounded = round((reading+writing)/config['human_rounding_minutes'])*config['human_rounding_minutes']
    return dict(book=key, compute_statistic='total', compute_subset='all', ai_attempts=1,
        retained_hierarchical_calls=13, cleanup_calls=1,
        assumed_nonfinal_gpt2_tokens=nonfinal, assumed_final_gpt2_tokens=final,
        source_gpt2_token_estimate=source_gpt2, source_cl100k_token_estimate=source_input,
        tokenizer_ratio=ratio['cl100k_per_gpt2'], source_word_estimate=source_words,
        chat_framing_per_call=frame, chunk_prompt_overhead_tokens=init_overhead,
        chunk_input_tokens=chunk_input, retained_chunk_output_tokens=chunk_outputs,
        merge_input_tokens=merge_input, merge_output_tokens=merge_output,
        cleanup_input_tokens=clean_input, cleanup_output_tokens=clean_output, cleanup_words=len(clean.split()),
        discarded_hierarchical_work_fraction=retry, discarded_work_tokens=discarded,
        tokens=total, flops_per_token=config['flops_per_token'],
        parameter_flops=total*config['flops_per_token'], compute_flops=central_flops,
        compute_flops_low=bounds[0], compute_flops_high=bounds[1],
        attention_context=context, attention_ratio=4*layers*width*attended_pairs/(2*active*total),
        hierarchical_call_lengths=call_lengths, cleanup_call_length=cleanup_length,
        human_reading_minutes=reading, human_composition_minutes=writing,
        human_unrounded_minutes=reading+writing, human_time=rounded*60)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sources',type=Path,required=True)
    ap.add_argument('--config',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a = ap.parse_args()
    if a.output.exists():
        ap.error('output already exists; choose a new path')
    config = json.loads(a.config.read_text())
    manifest = json.loads((a.sources/'review-source-manifest.json').read_text())
    for record in manifest:
        assert hashlib.sha256((a.sources/record['file']).read_bytes()).hexdigest() == record['sha256']
    gpt2 = encoding(a.sources,'r50k_base',R50K,'306cd27f03c1a714eca7108e03d66b7dc042abe8c258b44c199a7ed9838dd930')
    cl100k = encoding(a.sources,'cl100k_base',CL100K,'223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7')
    example = example_text(a.sources)
    bottom = json.loads((a.sources/'gpt4-4096-hier.json').read_text())[config['book']]['summaries_dict']['0']
    example_ratio = ratios([example],gpt2,cl100k)
    summary_ratio = ratios(bottom,gpt2,cl100k)
    lengths = historical_chunk_lengths(example,gpt2)
    central = calculate(a.sources,config,cl100k,example_ratio)
    out = {'config':config,'calibration':{
        'author_example':example_ratio, 'same_book_chunk_summaries':summary_ratio,
        'author_example_historical_chunk_lengths':lengths,
        'author_example_nonfinal_mean':sum(lengths[:-1])/(len(lengths)-1)},
        'central':central, 'scenarios':{
        'no_discarded_generations':calculate(a.sources,config,cl100k,example_ratio,retry=0),
        'quarter_extra_hierarchical_work':calculate(a.sources,config,cl100k,example_ratio,retry=.25),
        'smaller_source':calculate(a.sources,config,cl100k,example_ratio,nonfinal=3700,final=512),
        'all_chunks_at_gpt2_cap':calculate(a.sources,config,cl100k,example_ratio,nonfinal=4096,final=4096),
        'same_book_summary_conversion':calculate(a.sources,config,cl100k,summary_ratio)},
        'human':{'human_time':central['human_time'],'human_time_evidence':'llm_estimate_from_data',
        'human_time_statistic':'point_estimate',
        'human_time_subset':'all','human_attempts':'','timing_source_participants':18573,
        'timing_source_studies':190,
        'basis':'Transferred reading rate plus estimated composition and revision; study/participant counts do not establish reading-attempt count.',
        'estimated_active_minutes_scenarios':config['human_sensitivity_minutes']},
        'source_sha256':{record['file']:record['sha256'] for record in manifest}}
    with a.output.open('x') as handle:
        handle.write(json.dumps(out,indent=2)+'\n')

if __name__ == '__main__':
    main()
