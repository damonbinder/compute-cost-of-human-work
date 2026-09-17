"""Estimate one original Operand run without executing notebook or model code.

Requires tiktoken. Explicit source/assumption paths and a new JSON output path.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import tiktoken


def main(sources, assumptions, output):
    s, o = sources.resolve(), output.resolve()
    if o.exists() or o == s or s in o.parents or o == assumptions.resolve():
        raise ValueError('Output must be new and outside sources and assumptions')
    A = json.loads(assumptions.read_text())
    manifest = json.loads((s / 'retained-manifest.json').read_text())
    for name, metadata in manifest['files'].items():
        assert hashlib.sha256((s / name).read_bytes()).hexdigest() == metadata['sha256'], name
    b = s / 'operand/MLE_Submission/detecting-insults-in-social-commentary' / A['run']
    history = json.loads((b / 'full_history.json').read_text())
    notebook = json.loads((b / 'main.ipynb').read_text())
    task = (s / 'insults-description.md').read_text()
    enc = tiktoken.get_encoding('o200k_base')
    def nt(text):
        return len(enc.encode(text))

    def cell_output(cell, traceback_mode):
        parts = []
        for item in cell.get('outputs', []):
            if 'text' in item:
                parts.append(''.join(item['text']) if isinstance(item['text'], list) else item['text'])
            elif item.get('output_type') == 'error':
                if traceback_mode == 'summary':
                    parts.append(item['ename'] + ': ' + item['evalue'])
                else:
                    trace = '\n'.join(item['traceback'])
                    if traceback_mode == 'rendered':
                        trace = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', trace)
                    parts.append(trace)
        return '\n'.join(parts)

    def reconstruct(traceback_mode):
        cells, previous_history, turns = [], '', []
        reviews = []
        for turn in history:
            raw = turn['llm_json']; action = json.loads(raw[raw.index('{'):])
            number = turn['turn_number']
            state = '\n\n'.join(cells)
            # Source observations establish completion by these turns.
            if number >= 6:
                state += '\n' + cell_output(notebook['cells'][1], traceback_mode)
            if number >= 8:
                state += '\n' + cell_output(notebook['cells'][2], traceback_mode)
            turns.append(dict(turn=number, tool=action['tool'], task_tokens=nt(task),
                              prior_history_tokens=nt(previous_history), notebook_state_tokens=nt(state),
                              output_tokens=nt(raw), visible_reasoning_prefix_tokens=nt(raw[:raw.index('{')]),
                              preview_tokens=A['additional_file_preview_tokens'] if number >= 9 else 0))
            if action['tool'] == 'request_expert_review':
                reviews.append((task + '\n' + state + '\n' + action['explanation'], turn['outcome']))
            if action['tool'] == 'edit_notebook':
                edit = action['file_edit_payload']; assert edit['action'] == 'insert_cell'
                native = ''.join(notebook['cells'][edit['cell_index']]['source'])
                assert '\n'.join(edit['source']) == native
                cells.insert(edit['cell_index'], native)
            previous_history += raw + '\n' + turn['outcome'] + '\n'
        assert len(turns) == 10 and len(cells) == 4 and len(reviews) == 1
        return turns, *reviews[0]

    def calculate(wrapper=None, reason=None, repeat_notebook=True, review_reasoning_factor=1,
                  stable_cache=False, nnz=None, passes=None, traceback_mode=None,
                  separate_coach=None, reviewer_proxy=None, coach_reads_synthesis=None):
        wrapper = A['primary_fixed_wrapper_tokens'] if wrapper is None else wrapper
        reason = A['primary_extra_reasoning_tokens_per_turn'] if reason is None else reason
        traceback_mode = A['traceback_mode'] if traceback_mode is None else traceback_mode
        separate_coach = A['separate_coach'] if separate_coach is None else separate_coach
        reviewer_proxy = A['reviewer_output_proxy'] if reviewer_proxy is None else reviewer_proxy
        coach_reads_synthesis = A['coach_reads_synthesis'] if coach_reads_synthesis is None else coach_reads_synthesis
        turns, context, review = reconstruct(traceback_mode)
        marker = '**Independent Kaggle Coach Feedback:**'
        pos = review.index(marker); core, coach = review[:pos], review[pos:]
        core_n, coach_n, combined_n = nt(core), nt(coach), nt(review)
        proxy_n = core_n if reviewer_proxy == 'main_section' else combined_n
        usage = {k: dict(input=0, output=0) for k in A['active_parameters']}
        previous_history_tokens = 0
        for t in turns:
            history_n = t['prior_history_tokens']
            charged_history = max(0, history_n - previous_history_tokens) if stable_cache else history_n
            usage[A['primary_model_id']]['input'] += charged_history + t['preview_tokens']
            usage[A['primary_model_id']]['input'] += t['notebook_state_tokens'] if repeat_notebook else 0
            if not stable_cache or t['turn'] == 1:
                usage[A['primary_model_id']]['input'] += t['task_tokens'] + wrapper
            usage[A['primary_model_id']]['output'] += t['output_tokens'] + reason
            previous_history_tokens = history_n
        helper_wrapper = A['helper_fixed_wrapper_tokens']
        for model in A['reviewers']:
            usage[model]['input'] += nt(context) + helper_wrapper
            usage[model]['output'] += proxy_n * (A['reviewer_visible_output_times_proxy'] +
                A['reviewer_extra_reasoning_times_proxy'] * review_reasoning_factor)
        synthesis = A['synthesis_model']
        usage[synthesis]['input'] += nt(context) + helper_wrapper + len(A['reviewers']) * proxy_n * A['reviewer_visible_output_times_proxy']
        # If coach is part of the ensemble, keep both visible sections in synthesis.
        synthesis_n = core_n if separate_coach else combined_n
        usage[synthesis]['output'] += synthesis_n * (1 + A['synthesis_extra_reasoning_times_output'] * review_reasoning_factor)
        coach_context = context + '\n' + core if coach_reads_synthesis else context
        if separate_coach:
            usage[A['coach_model']]['input'] += nt(coach_context) + helper_wrapper
            usage[A['coach_model']]['output'] += coach_n * (1 + A['coach_extra_reasoning_times_output'] * review_reasoning_factor)
        llm = sum((u['input'] + u['output']) * 2 * A['active_parameters'][m] for m, u in usage.items())
        nnz = A['classifier_nonzeros_per_comment'] if nnz is None else nnz
        passes = A['classifier_training_passes'] if passes is None else passes
        n, ntest = 3947, 2647
        classifier = dict(
            sparse_training=5*n*nnz*passes*A['classifier_operations_per_nonzero_per_pass'],
            dense_epoch_allowance=6*A['classifier_features']*passes*10,
            feature_transforms=(6*n+ntest)*nnz*10,
            predictions=(n+ntest)*nnz*2)
        return dict(configuration=dict(wrapper=wrapper, primary_hidden=reason,
                    repeat_notebook=repeat_notebook, review_reasoning_factor=review_reasoning_factor,
                    stable_cache=stable_cache, classifier_nonzeros=nnz, classifier_passes=passes,
                    traceback_mode=traceback_mode, separate_coach=separate_coach,
                    reviewer_proxy=reviewer_proxy, coach_reads_synthesis=coach_reads_synthesis),
                    model_usage=usage, text_tokens=sum(u['input']+u['output'] for u in usage.values()),
                    llm_flops=llm, classifier_components=classifier, classifier_flops=sum(classifier.values()),
                    total_flops=llm+sum(classifier.values()))

    turns, context, review = reconstruct(A['traceback_mode'])
    pos=review.index('**Independent Kaggle Coach Feedback:**')
    result = dict(assumptions=A, assumptions_sha256=hashlib.sha256(assumptions.read_bytes()).hexdigest(),
        source_sha256={str(f.relative_to(s)): hashlib.sha256(f.read_bytes()).hexdigest() for f in
            [b/'full_history.json',b/'main.ipynb',b/'competition_results.json',s/'insults-description.md',s/'original-leaderboard-readme.md']},
        retained_source_hashes_checked=len(manifest['files']), recovered_turns=turns,
        review_context_tokens=nt(context), main_review_tokens=nt(review[:pos]), coach_tokens=nt(review[pos:]),
        combined_review_tokens=nt(review), coach_context_tokens_with_wrapper=nt(context+'\n'+review[:pos])+A['helper_fixed_wrapper_tokens'],
        primary_notebook_tokens=sum(t['notebook_state_tokens'] for t in turns),
        primary_history_tokens=sum(t['prior_history_tokens'] for t in turns),
        primary_visible_output_tokens=sum(t['output_tokens'] for t in turns),
        central=calculate(), scenarios={
            'no_extra_reasoning':calculate(reason=0,review_reasoning_factor=0),
            'high_reasoning':calculate(reason=8192,review_reasoning_factor=4),
            'wrapper_500':calculate(wrapper=500),'wrapper_4000':calculate(wrapper=4000),
            'no_repeated_notebook':calculate(repeat_notebook=False),
            'stable_prefix_cache_reuse':calculate(stable_cache=True),
            'classifier_small':calculate(nnz=100,passes=20),
            'classifier_cap_large':calculate(nnz=5000,passes=5000),
            'coach_within_ensemble':calculate(separate_coach=False),
            'combined_reviewer_output_proxy':calculate(reviewer_proxy='combined_sections'),
            'error_summary_only':calculate(traceback_mode='summary'),
            'raw_ansi_traceback':calculate(traceback_mode='raw'),
            'coach_without_main_synthesis_input':calculate(coach_reads_synthesis=False)})
    o.parent.mkdir(exist_ok=True,parents=True)
    # Exclusive creation also protects against a concurrent writer after the initial check.
    with o.open('x') as stream:
        stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['central'],indent=2))


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sources',type=Path,required=True)
    p.add_argument('--assumptions',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();main(a.sources,a.assumptions,a.output)
