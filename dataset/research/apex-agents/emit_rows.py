#!/usr/bin/env python3
"""Emit the APEX-Agents-AA candidate rows from the retained calculation file.

Dependencies: Python 3.9+ standard library only.

Usage:
  python3 emit_rows.py \
      --calculations <research/apex-agents/calculations.json> \
      --points-out   <candidates/apex-agents/points.csv> \
      --models-out   <candidates/apex-agents/models.csv>

Reads only calculations.json (itself produced by build_rows.py from the retained
source extracts) and writes two new CSV files. Field-length limits from
DECISIONS.md are enforced; the script fails rather than truncating.
"""
import argparse, csv, json

POINT_HEADER = ['point_id','task','task_category','task_description','model_id','compute_scope',
 'compute_flops','human_skill','human_time_scope','human_time','performance_vs_human',
 'comparison_issues','compute_evidence','human_time_evidence','performance_evidence',
 'human_time_statistic','human_time_subset','human_attempts','human_time_source',
 'human_time_method','compute_method','compute_statistic','compute_subset','ai_attempts',
 'compute_source','tokens','tokens_accounting','source_dataset','source_record','notes']

MODEL_HEADER = ['model_id','model','company','model_release_date','model_release_source',
 'flops_per_token','flops_per_token_method','active_parameters','active_parameters_basis',
 'encoder_parameters','encoder_parameters_basis','decoder_parameters','decoder_parameters_basis',
 'parameter_source','notes']

LIMITS = {'notes':586,'task_description':560,'performance_evidence':337,'source_record':455,
          'compute_source':220,'human_time_source':205}

SHORT = {'gemini-3-5-flash':'gemini35flash','kimi-k3':'kimik3','gpt-5-6-terra':'gpt56terra',
         'gpt-5-5':'gpt55','gpt-5-6-luna':'gpt56luna','glm-5-2':'glm52','gpt-5-4':'gpt54',
         'claude-opus-4-6-adaptive':'opus46','gpt-oss-120b':'gptoss120b'}

TASK_DESCRIPTION = (
 "Complete one APEX-Agents professional services task, as the average over the 452-task subset "
 "Artificial Analysis evaluates: 132 investment banking, 160 corporate law and 160 consulting "
 "tasks set in 33 simulated firm worlds of ~166 files. Input: one single-turn "
 "instruction plus the world. Tools: file system, documents, spreadsheets, PDFs, email, chat, "
 "calendar and code execution; web search disabled. Output: a console answer, or for 12% of tasks a "
 "created or edited file. Done when every binary rubric criterion is met, mean 4.16 per "
 "task on this subset.")

NOTES = {
 'provider_default': (
  "Counted positions exclude cache reads at an implied {cr:.0%} of input. This endpoint caches by "
  "default, so no reuse is not a live branch; the central is the geometric mean of full reuse of the "
  "{s:.1%} cacheable input AA measures for {donor} on its other Stirrup runs, and of that prefix "
  "served at a 60% floor. Range {lo:.2f}x-{hi:.2f}x; gross {g:.2f}x. Human time rescales the card's "
  "domain means by the ratio 1.37/1.70 h; readings 4932-5454 s. Omitted upward: attention "
  "{a20:.1f}x-{a50:.1f}x at 20-50k.{extra}"),
 'uncached_harness': (
  "Central is gross input. The published Stirrup harness sets no Anthropic cache_control breakpoints "
  "anywhere in its tree and Anthropic caches nothing without them, so no input position was served "
  "from cache; AA's cacheableInput is its own eligibility computation, not a provider counter. At "
  "the {s:.1%} eligible share AA measures for other Anthropic models it would fall to {lo:.2f}x. "
  "Human time rescales the card's domain means by the ratio 1.37/1.70 h; readings 4932-5454 s. "
  "Omitted upward: attention {a20:.1f}x-{a50:.1f}x.{extra}"),
 'undetermined': (
  "Counted positions exclude cache reads at an implied {cr:.0%} of input, the geometric mean of no "
  "reuse and full reuse of the {s:.1%} cacheable input AA measures for {donor} on its other Stirrup "
  "runs. Provider-default caching is not established for AA's serving path here, and its near-flat "
  "cache-hit price argues for the no-reuse edge at {hi:.2f}x. Human time rescales the card's domain "
  "means by the ratio 1.37/1.70 h; readings 4932-5454 s. Omitted upward: attention "
  "{a20:.1f}x-{a50:.1f}x at 20-50k.{extra}"),
}

PERF_TEMPLATE = (
 "Pass@1 {p:.1f}% over 3 runs of each of 452 tasks: the share meeting every binary rubric criterion, "
 "mean 4.16 per task. {crit} No human was scored; the human arm is the expert-written gold output "
 "passing by construction, plus 96 tasks executed by experts who did not write them.")
CRIT_YES = "Criterion-level, Mercor's board has it meeting {c:.1f}% of criteria."
CRIT_NO = "No criterion-level score is published for it on any board."

SOURCE_RECORD = (
 "https://artificialanalysis.ai/evaluations/apex-agents-aa model_slug={slug}, 452-task subset, "
 "Stirrup harness, 3 runs per task; https://huggingface.co/datasets/mercor/apex-agents; "
 "https://arxiv.org/abs/2601.14242 v3 Sections 3.5, 4.1, 4.3, Table 4; "
 "agent-work/sources/apex-agents/aa-apex-agents-model-records.json; performance: AA page pass@1, "
 "criterion-level Mercor board via agent-work/sources/apex-agents/epoch-apex-agents-mean-scores.csv")

# Mean percentage of rubric criteria met per task, Mercor's board, from Epoch's
# apex_agents_external.csv. None where no criterion-level score is published anywhere.
CRITERION_SCORE = {
    'kimi-k3': 0.554, 'gpt-5-5': 0.555, 'gpt-5-4': 0.527, 'glm-5-2': 0.522,
    'claude-opus-4-6-adaptive': 0.484, 'gpt-oss-120b': 0.145,
    'gemini-3-5-flash': None, 'gpt-5-6-terra': None, 'gpt-5-6-luna': None,
}
EPOCH_PASS_AT_1 = {
    'kimi-k3': 0.393, 'gpt-5-5': 0.385, 'gpt-5-4': 0.360, 'glm-5-2': 0.356,
    'claude-opus-4-6-adaptive': 0.321, 'gpt-oss-120b': 0.047,
}

EXTRA = {
 'gpt-5-6-luna': " AA's own cache-hit rate exceeds this model's eligible share, so it is not used.",
 'gpt-5-6-terra': " The 20B mini-tier prior drives the low value; OpenAI states a tier, not a size.",
 'claude-opus-4-6-adaptive': "",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--calculations', required=True)
    ap.add_argument('--points-out', required=True)
    ap.add_argument('--models-out', required=True)
    a = ap.parse_args()
    d = json.load(open(a.calculations))
    ht = round(d['human_time']['calibrated_seconds'])

    rows = []
    for slug, m in sorted(d['models'].items(), key=lambda kv: -kv[1]['pass_at_1']):
        sc = m['scenario_flops_multiple_of_central']
        ad = d['cached_context_attention_multiple_of_recorded'][slug]
        key = next(k for k in ad if k.startswith('mid') or k.startswith('disclosed'))
        att = ad[key]
        rule = m['central_rule']
        lo = sc['full_eligible_reuse']
        hi = sc['hit_share_floor'] if rule == 'provider_default' else sc['no_reuse']
        donor = ('this model' if m['cacheable_share_donor_basis'] == 'own_model'
                 else 'other %s models' % m['company'])
        rows.append({
         'point_id': 'work-apex-agents-' + SHORT[slug],
         'task': 'APEX-Agents professional services task',
         'task_category': 'research_analysis',
         'task_description': TASK_DESCRIPTION,
         'model_id': m['model_id'],
         'compute_scope': 'inference',
         'compute_flops': repr(m['compute_flops']),
         'human_skill': 'expert',
         'human_time_scope': 'task_performance',
         'human_time': ht,
         'performance_vs_human': 'below',
         'comparison_issues': 'different_inputs_or_tools; different_assessment',
         'compute_evidence': 'derived_assumed_inputs',
         'human_time_evidence': 'transferred_timings',
         'performance_evidence': PERF_TEMPLATE.format(
             p=100 * m['pass_at_1'],
             crit=(CRIT_NO if CRITERION_SCORE[slug] is None
                   else CRIT_YES.format(c=100 * CRITERION_SCORE[slug]))),
         'human_time_statistic': 'mean',
         'human_time_subset': 'all',
         'human_attempts': 96,
         'human_time_source': 'research/apex-agents.md#human-time',
         'human_time_method': 'estimated',
         'compute_method': 'params_tokens',
         'compute_statistic': 'mean',
         'compute_subset': 'all',
         'ai_attempts': 1356,
         'compute_source': 'research/apex-agents.md#compute; research/apex-agents/calculations.json',
         'tokens': repr(m['counted_tokens_per_task']),
         'tokens_accounting': 'input_cache_creation_output',
         'source_dataset': 'APEX-Agents, Artificial Analysis implementation',
         'source_record': SOURCE_RECORD.format(slug=slug),
         'notes': NOTES[rule].format(
             cr=m['implied_cache_read_share_of_input'], s=m['cacheable_share_donor'],
             donor=donor, lo=lo, hi=hi, g=sc['no_reuse'],
             a20=att['20000'], a50=att['50000'],
             extra=EXTRA.get(slug, '') + (
                 '' if CRITERION_SCORE[slug] is None else
                 " The criterion score is Mercor's board; its pass@1 differs by %.3f from AA's."
                 % abs(m['pass_at_1'] - EPOCH_PASS_AT_1[slug]))),
        })

    for r in rows:
        for f, lim in LIMITS.items():
            if len(str(r[f])) > lim:
                raise SystemExit('%s %s is %d chars, limit %d' % (r['point_id'], f, len(str(r[f])), lim))
        assert set(r) == set(POINT_HEADER), set(r) ^ set(POINT_HEADER)

    with open(a.points_out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=POINT_HEADER); w.writeheader(); w.writerows(rows)

    models = [
     {'model_id':'kimi-k3','model':'Kimi K3','company':'Moonshot AI','model_release_date':'2026-07-16',
      'model_release_source':'https://artificialanalysis.ai/models/kimi-k3; https://epoch.ai/data/all_ai_models.csv',
      'flops_per_token':'208000000000','flops_per_token_method':'two_active_parameters',
      'active_parameters':'104000000000','active_parameters_basis':'estimated',
      'encoder_parameters':'not_applicable','encoder_parameters_basis':'not_applicable',
      'decoder_parameters':'not_applicable','decoder_parameters_basis':'not_applicable',
      'parameter_source':'https://epoch.ai/data/all_ai_models.csv; https://artificialanalysis.ai/models/kimi-k3; https://huggingface.co/moonshotai/Kimi-K3; research/apex-agents.md#model-records',
      'notes':'Open weights. The safetensors index gives 2.78T total, matching the 2.8T both aggregators publish; 104B active is their figure, recorded by Epoch at Speculative confidence, and was not reproduced from the public config, whose latent-MoE experts do not take the standard gate/up/down form. The repository predates the published release date.'},
     {'model_id':'gpt-5-6-terra','model':'GPT-5.6 Terra','company':'OpenAI','model_release_date':'2026-07-09',
      'model_release_source':'https://developers.openai.com/api/docs/changelog; https://developers.openai.com/api/docs/models/gpt-5.6-terra',
      'flops_per_token':'40000000000','flops_per_token_method':'two_active_parameters',
      'active_parameters':'20000000000','active_parameters_basis':'estimated',
      'encoder_parameters':'not_applicable','encoder_parameters_basis':'not_applicable',
      'decoder_parameters':'not_applicable','decoder_parameters_basis':'not_applicable',
      'parameter_source':'https://developers.openai.com/api/docs/models/gpt-5.6-terra; research/apex-agents.md#model-records; the shared small-tier assumption carried by o1-mini-2024-09-12, o3-mini-2025-01-31, o4-mini-2025-04-16, gpt-5-mini-2025-08-07 and grok-3-mini-beta',
      'notes':"OpenAI's model page states Terra 'roughly corresponds to the mini model tier used in earlier GPT-5 families', which licenses the registry's 20B mini prior; the tier is OpenAI's, the size is not. Range 8-60B. The serving ladder against o4-mini's $1.10/$4.40 would give 20B x sqrt(2.7) = 33B, not applied because the report holds the nano tier in this situation."},
     {'model_id':'gpt-5-5','model':'GPT-5.5','company':'OpenAI','model_release_date':'2026-04-23',
      'model_release_source':'https://developers.openai.com/api/docs/models/gpt-5.5; https://developers.openai.com/api/docs/changelog',
      'flops_per_token':'346000000000','flops_per_token_method':'two_active_parameters',
      'active_parameters':'173000000000','active_parameters_basis':'estimated',
      'encoder_parameters':'not_applicable','encoder_parameters_basis':'not_applicable',
      'decoder_parameters':'not_applicable','decoder_parameters_basis':'not_applicable',
      'parameter_source':'https://developers.openai.com/api/docs/models/gpt-5.5; https://epochai.substack.com/p/notes-on-gpt-5-training-compute; research/apex-agents.md#model-records; the GPT-5-family prior carried by gpt-5, gpt-5.1-2025-11-13, gpt-5.2-2025-12-11 and gpt-5.4-2026-03-05',
      'notes':"173B active applies the serving-ladder method of research/model-priors/openai.md to a new ID with no inherited prior: square-root shrinkage on the $30 output price against GPT-5's $10 gives 100B x sqrt(3) = 173B. The same report reads GPT-5.5 as the GPT-5 family's genuine scale-up. Range 70-400B. The changelog entry is dated one day after the 2026-04-23 snapshot."},
    ]
    for m in models:
        if len(m['notes']) > 365:
            raise SystemExit('%s notes %d chars, limit 365' % (m['model_id'], len(m['notes'])))
        assert set(m) == set(MODEL_HEADER)
    with open(a.models_out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=MODEL_HEADER); w.writeheader(); w.writerows(models)
    print('wrote %d points, %d models' % (len(rows), len(models)))


if __name__ == '__main__':
    main()
