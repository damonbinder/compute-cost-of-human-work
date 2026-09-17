"""Row arithmetic for the Kaggle Game Arena chess points, plus the test that fixes what the
leaderboard's Avg. Tokens/Turn column counts on each board version.

Dependencies: Python 3.9+ standard library only.

Usage:
    python3 calc.py --sources /abs/path/to/sources/game-arena --output /abs/path/to/new.json \
        [--points-csv /abs/path/to/points.csv --models-csv /abs/path/to/models.csv \
         --header-source /abs/path/to/folder-with-root-csvs]

--output must not already exist. The two CSV paths may be overwritten, since regenerating the candidate is
the point; --header-source names the folder whose root points.csv and models.csv define the column order.

--sources must contain the retained kaggle-chess-text-v1-leaderboard.json,
kaggle-chess-text-v2-leaderboard.json, kaggle-chess-text-openings-v1-leaderboard.json,
russek-move-times-by-elo-bin.json, chess-replay-usage-by-model.json and
chess-replay-durations-and-call-details-coverage.json. --output must not already exist and must not sit
inside --sources, so reproduction writes new outputs rather than modifying retained evidence.

What Avg. Tokens/Turn counts
----------------------------
Write T for the published Avg. Tokens/Turn, P for mean prompt tokens per move, and p_in, p_out for the
model's list prices. Two readings predict different costs, and their difference has a sign that does not
depend on knowing P:

    H1, T = P + output : cost = p_in*P + p_out*(T - P)  ->  cost/T < p_out
    H2, T = output only: cost = p_in*P + p_out*T        ->  cost/T > p_out

So comparing the implied price cost/T with the model's list output price settles it. On both version 1
boards cost/T exceeds p_out for every model, which rejects H1 at any non-negative prompt length; on version 2
it falls below p_out, which rejects H2. The column changed meaning between board versions.

Under H2 the prompt is then recoverable: P = (cost - p_out*T) / p_in. The openings board publishes cost to
two decimal places, which makes that solve usable; the chess-text v1 board publishes one decimal, which does
not constrain P usefully. Both uncertainties are reported.

Kaggle's API is proto3 JSON, which omits zero-valued numbers; a missing Score is therefore read as 0.
"""
import argparse, csv, json, statistics
from pathlib import Path

T1 = dict(score=396, elo=411, tokens=408, cost=409)      # chess-text version 1
T2 = dict(score=1446, elo=None, tokens=1892, cost=1891)  # chess-text version 2
O1 = dict(score=488, elo=559, tokens=561, cost=560)      # chess-text-openings version 1

# Cost column precision, in cents, as published on each board. Half of the last place is the rounding bound.
COST_DP = {'chess-text-v1': 1, 'chess-text-openings-v1': 2, 'chess-text-v2': None}

# List prices in USD per million tokens, current at the August 2025 board date.
# OpenAI https://openai.com/api/pricing ; xAI https://docs.x.ai/docs/models ;
# Google https://ai.google.dev/gemini-api/docs/pricing ; Anthropic https://www.anthropic.com/pricing
# These are inputs, but they are not taken on trust: the prompt lengths recovered below land in a plausible
# 328-1010 token band for every model, which a wrong output price would not produce.
PRICES = {
    'o3': (2.00, 8.00), 'GPT-5': (1.25, 10.00), 'Grok 4': (3.00, 15.00),
    'Gemini 2.5 Pro': (1.25, 10.00), 'o4 mini': (1.10, 4.40), 'GPT-4.1': (2.00, 8.00),
    'Claude Sonnet 4': (3.00, 15.00), 'Claude Opus 4': (15.00, 75.00), 'Gemini 2.5 Flash': (0.30, 2.50),
}
# Version 2 models used only to show the test flips sign there.
PRICES_V2 = {'o3': (2.00, 8.00), 'Grok 4': (3.00, 15.00), 'GPT-5 mini': (0.25, 2.00),
             'Claude Sonnet 4.5': (3.00, 15.00), 'Claude Opus 4.6': (5.00, 25.00)}

BINS = [((0, 1250), '625.0'), ((1250, 1525), '1387.5'), ((1525, 1800), '1662.5'), ((1800, 3000), '2400.0')]
PRIMARY_TIME_CONTROL = '300+0'

# Shared model assumptions; flops_per_token = 2 * active_parameters throughout.
# "dataset" rows reproduce AI Compute vs Human Time/dataset/models.csv verbatim and are reused unchanged.
MODELS = {
    'openai/o3-2025-04-16':               dict(model_id='o3-2025-04-16',      active=50e9,  source='dataset'),
    'openai/gpt-5-2025-08-07':            dict(model_id='gpt-5',              active=100e9, source='dataset'),
    'xai/grok-4-0709':                    dict(model_id='grok-4',             active=115e9, source='dataset'),
    'google/gemini-2.5-pro':              dict(model_id='gemini-2.5-pro',     active=100e9, source='dataset'),
    'openai/o4-mini-2025-04-16':          dict(model_id='o4-mini-2025-04-16', active=20e9,  source='dataset'),
    'openai/gpt-4.1-2025-04-14':          dict(model_id='gpt-4.1-2025-04-14', active=50e9,  source='dataset'),
    'anthropic/claude-sonnet-4@20250514': dict(model_id='claude-sonnet-4',    active=100e9, source='dataset'),
    'anthropic/claude-opus-4@20250514':   dict(model_id='claude-opus-4',      active=180e9, source='dataset'),
    'deepseek-ai/deepseek-r1-0528':       dict(model_id='deepseek-r1-0528',   active=37e9,  source='new candidate record'),
    'google/gemini-2.5-flash':            dict(model_id='gemini-2.5-flash',   active=40e9,  source='dataset'),
    '':                                   dict(model_id='kimi-k2-instruct',   active=32e9,  source='dataset'),
}

# Rows drafted, in board order. Each names the board its output-token count comes from.
ROWS = [
    ('o3', 'chess-text-v1'), ('GPT-5', 'chess-text-openings-v1'), ('Grok 4', 'chess-text-v1'),
    ('Gemini 2.5 Pro', 'chess-text-v1'), ('o4 mini', 'chess-text-v1'), ('GPT-4.1', 'chess-text-v1'),
    ('Claude Sonnet 4', 'chess-text-v1'), ('Claude Opus 4', 'chess-text-v1'), ('DeepSeek-R1', 'chess-text-v1'),
]
EXCLUDED = {
    'Gemini 2.5 Flash': 'Estimated Human Elo 314 on the Chess Text board and 282 on the Chess Openings board '
                        'are below the Lichess rating floor of 400, so no human population exists at the '
                        'matched rating to take a move time from.',
    'Kimi K2 Instruct': 'Estimated Human Elo 262 is below the Lichess rating floor of 400, same reason; its '
                        'Game Arena Elo is also 0, the bottom of the board.',
    'Grandmaster':      'Reference row supplied by Kaggle at 2500 Estimated Human Elo; not a model and '
                        'carries no token or cost figure.',
}
# Alternative prompt estimates, kept as a scenario. Same model where the model is on the version 2 board;
# otherwise the nearest sibling on the same harness, which is a weaker comparison and is labelled as such.
ALT_PROMPT = {
    'o3': ('o3', 'same model'), 'Grok 4': ('Grok 4', 'same model'),
    'GPT-5': ('GPT-5 mini', 'family sibling'), 'Gemini 2.5 Pro': ('Gemini 3.1 Pro Preview', 'family sibling'),
    'o4 mini': ('GPT-5 mini', 'family sibling'), 'GPT-4.1': ('GPT-5.2', 'family sibling'),
    'Claude Sonnet 4': ('Claude Sonnet 4.5', 'family sibling'),
    'Claude Opus 4': ('Claude Opus 4.6', 'family sibling'),
    'DeepSeek-R1': ('DeepSeek V3.2', 'same tokenizer family'),
}


def read_board(path, ids):
    d = json.loads(Path(path).read_text())
    out = {}
    for r in d['rows']:
        mv = r['modelVersion']
        res = {}
        for x in r['results']:
            nr = x.get('numericResult', {})
            res[x.get('taskVersionId')] = {'value': nr.get('value', 0.0),
                                           'ci': nr.get('unevenConfidenceInterval'),
                                           'date': x.get('evaluationDate')}
        g = lambda k: res.get(ids[k], {}) if ids[k] else {}
        out[mv['displayName']] = {
            'display_name': mv['displayName'], 'model_proxy_slug': mv.get('modelProxySlug'),
            'game_arena_elo': g('score').get('value'), 'game_arena_elo_ci': g('score').get('ci'),
            'estimated_human_elo': g('elo').get('value'), 'estimated_human_elo_ci': g('elo').get('ci'),
            'avg_tokens_per_turn': g('tokens').get('value'),
            'avg_cost_per_turn_cents': g('cost').get('value'),
            'evaluation_date': (g('elo') or g('tokens')).get('date'),
        }
    return out


def cost_test(board_name, board, prices):
    """Compare cost/T with the list output price, and solve the prompt under whichever reading survives."""
    dp = COST_DP[board_name]
    half = 0.5 * 10 ** (-dp) if dp is not None else 0.0     # cents
    out = {}
    for name, (p_in, p_out) in prices.items():
        b = board.get(name)
        if not b or not b['avg_tokens_per_turn'] or not b['avg_cost_per_turn_cents']:
            continue
        T, cost = b['avg_tokens_per_turn'], b['avg_cost_per_turn_cents']
        implied = cost / T * 1e4                            # USD per million per published token
        excess_cents = cost - p_out * T * 1e-4
        rec = {'avg_tokens_per_turn': T, 'avg_cost_per_turn_cents': cost,
               'list_price_in_usd_per_million': p_in, 'list_price_out_usd_per_million': p_out,
               'implied_usd_per_million_per_published_token': implied,
               'implied_over_list_output_price': implied / p_out,
               'excess_over_output_only_cost_cents': excess_cents,
               'h1_prompt_plus_output_possible': excess_cents < 0,
               'h2_output_only_possible': excess_cents > 0}
        if excess_cents > 0:                                # H2 holds: solve the prompt
            rec['prompt_tokens_implied'] = excess_cents * 1e-2 / (p_in * 1e-6)
            rec['prompt_tokens_implied_rounding_bound'] = half * 1e-2 / (p_in * 1e-6)
        else:                                               # H1 holds: solve the prompt under H1
            rec['prompt_tokens_implied_under_h1'] = (p_out * T * 1e-4 - cost) * 1e-2 / ((p_out - p_in) * 1e-6)
        out[name] = rec
    return out


def bin_for(elo):
    for (lo, hi), label in BINS:
        if lo < elo <= hi:
            return (lo, hi), label
    return None, None


# ---------------------------------------------------------------------------
# Candidate CSV emission.
#
# Text fields are kept inside the existing dataset's observed maxima (notes 586, task_description 560,
# performance_evidence 337, source_record 455, compute_source 220, human_time_source 205 characters) so the
# rows sit alongside the dataset's own without reformatting. Everything that does not fit is in
# research/game-arena.md; the CSV keeps only the qualifications COLUMNS.md asks it to carry. Cited paths
# never end a sentence, because the validator's path regex would swallow the period.
# ---------------------------------------------------------------------------
FIELD_MAX = {'notes': 586, 'task_description': 560, 'performance_evidence': 337, 'source_record': 455,
             'compute_source': 220, 'human_time_source': 205}
POINT_IDS = {'o3': 'game-chess-move-arena-o3', 'GPT-5': 'game-chess-move-arena-gpt5',
             'Grok 4': 'game-chess-move-arena-grok4', 'Gemini 2.5 Pro': 'game-chess-move-arena-gemini25pro',
             'o4 mini': 'game-chess-move-arena-o4mini', 'GPT-4.1': 'game-chess-move-arena-gpt41',
             'Claude Sonnet 4': 'game-chess-move-arena-sonnet4', 'Claude Opus 4': 'game-chess-move-arena-opus4',
             'DeepSeek-R1': 'game-chess-move-arena-r1'}
BOARD_LABEL = {'chess-text-v1': 'Kaggle Game Arena Chess Text leaderboard (board version 1, August 2025)',
               'chess-text-openings-v1': 'Kaggle Game Arena Chess Openings leaderboard (board version 1, September 2025)'}
BOARD_TASKS = {'chess-text-v1': ('kaggle/chess-text', 'v1 (benchmarkVersionId 129)', 396, 411, 408, 409,
                                 'kaggle-chess-text-v1-leaderboard.json',
                                 'https://www.kaggle.com/blog/chess-text-leaderboard'),
               'chess-text-openings-v1': ('kaggle/chess-text-openings', 'v1', 488, 559, 561, 560,
                                          'kaggle-chess-text-openings-v1-leaderboard.json',
                                          'https://www.kaggle.com/blog/game-arena-chess-openings')}
OPENINGS_JSON = 'agent-work/sources/game-arena/kaggle-chess-text-openings-v1-leaderboard.json'


def fmt(x):
    return '%g' % x if float(x) == int(x) else repr(round(float(x), 6))


def interval(c):
    return '' if not c else '-%g/+%g' % (c.get('minus', 0), c.get('plus', 0))


def build_point_rows(rows):
    out = []
    for r in rows:
        pid, bd = POINT_IDS[r['display_name']], r['board']
        openings = bd == 'chess-text-openings-v1'
        elo, gelo = r['estimated_human_elo'], r['game_arena_elo']
        slug, ver, t_s, t_e, t_t, t_c, retained, blog = BOARD_TASKS[bd]

        where = 'a game from an assigned opening' if openings else 'a game from the standard start'
        desc = ('One move in %s on the %s: given the position in FEN plus the moves so far as text, no '
                'legal-move list, no board image, and a one-hour ceiling per move, reason step by step and '
                'return one legal move in SAN; an illegal answer is retried and exhausting the retries '
                "forfeits the game. Quantity: one move, the board's mean over every move the model played in "
                'its all-play-all, 40 games per pair, 20 as each color. Human baseline: an online blitz '
                'player rated %g making one move in a five-minute game.'
                % (where, 'Chess Openings board' if openings else 'Chess Text board', elo))

        perf = ('Estimated Human Elo %g (%s, 500 bootstrap resamples), regressed from Stockfish matches at '
                "known human-Elo anchors; Game Arena Elo %g (%s) by Bradley-Terry over the board's "
                'all-play-all. The baseline is online blitz players at that rating, so strength is matched by '
                'selection, not by an observed result against humans.'
                % (elo, interval(r['estimated_human_elo_ci']), gelo, interval(r['game_arena_elo_ci'])))

        prompt_clause = ('the %g prompt tokens rest on the cross-model prompt pattern, no list price being '
                         'published here' % r['prompt_tokens_added']
                         if r['display_name'] == 'DeepSeek-R1' else
                         "the %g prompt tokens are solved from the Chess Openings board's cost column"
                         % r['prompt_tokens_added'])
        note = ('Avg. Tokens/Turn here is output tokens including reasoning; %s. No cache counters are logged '
                'and the prompt changes every move, so no cache read is excluded. Estimated Human Elo is '
                'Stockfish-anchored, read as a Lichess blitz rating; its anchors play stronger than nominal, '
                'so it understates the model. Human time is own-clock time in five-minute games, excluding '
                'opponent-turn thinking, transferred from a rating bin.' % prompt_clause)
        if openings:
            note += ' Games start from an assigned opening; this model is on no other Game Arena board.'
        if elo < 1347:
            note += (' Elo %g is below the 1347 floor of the published Stockfish mapping.' % elo)

        src = ('%s %s, model %s, evaluated %s; task %d Score %g, task %d Estimated Human Elo %g, task %d '
               'Avg. Tokens/Turn %s output, task %d Avg. Cost/Turn %g cents; '
               'agent-work/sources/game-arena/%s; performance: %s'
               % (slug, ver, r['model_proxy_slug'], r['evaluation_date'][:10], t_s, gelo, t_e, elo, t_t,
                  fmt(r['published_avg_tokens_per_turn_output_only']), t_c, r['avg_cost_per_turn_cents'],
                  retained, blog))
        if not openings:
            src = src.replace('; performance: ', '; prompt from %s; performance: ' % OPENINGS_JSON)

        out.append({
            'point_id': pid, 'task': 'Choose a chess move from a text board', 'task_category': 'games',
            'task_description': desc, 'model_id': r['model_id'], 'compute_scope': 'inference',
            'compute_flops': repr(r['compute_flops_per_move']), 'human_skill': r['human_skill'],
            'human_time_scope': 'task_performance', 'human_time': '%g' % r['human_time_seconds_rounded'],
            'performance_vs_human': 'match',
            'comparison_issues': 'different_inputs_or_tools; different_assessment',
            'compute_evidence': 'derived_assumed_inputs', 'human_time_evidence': 'transferred_timings',
            'performance_evidence': perf, 'human_time_statistic': 'mean', 'human_time_subset': 'all',
            'human_attempts': str(r['human_move_observations']),
            'human_time_source': ('research/game-arena.md#%s; agent-work/sources/game-arena/russek-move-times-by-elo-bin.json; '
                                  'https://doi.org/10.1111/cogs.70119' % pid),
            'human_time_method': 'estimated', 'compute_method': 'params_tokens', 'compute_statistic': 'mean',
            'compute_subset': 'all', 'ai_attempts': 'not_applicable',
            'compute_source': ('research/game-arena.md#%s; research/game-arena/calculations.json; '
                               'agent-work/sources/game-arena/%s' % (pid, retained)),
            'tokens': fmt(r['tokens_total_per_move']), 'tokens_accounting': 'input_output',
            'source_dataset': BOARD_LABEL[bd], 'source_record': src, 'notes': note,
        })
    return out


MODEL_ROW = {
    'model_id': 'deepseek-r1-0528', 'model': 'DeepSeek-R1-0528', 'company': 'DeepSeek',
    'model_release_date': '2025-05-28',
    'model_release_source': 'https://api-docs.deepseek.com/news/news250528',
    'flops_per_token': '74000000000', 'flops_per_token_method': 'two_active_parameters',
    'active_parameters': '37000000000', 'active_parameters_basis': 'reported',
    'encoder_parameters': 'not_applicable', 'encoder_parameters_basis': 'not_applicable',
    'decoder_parameters': 'not_applicable', 'decoder_parameters_basis': 'not_applicable',
    'parameter_source': ('https://huggingface.co/deepseek-ai/DeepSeek-R1-0528/raw/main/config.json; '
                         'https://github.com/deepseek-ai/DeepSeek-R1#2-model-summary; '
                         'research/game-arena.md#game-chess-move-arena-r1'),
    'notes': ("The May 2025 R1 revision, distinct from the dataset's deepseek-r1 record for the January 2025 "
              "release. Its published config.json matches DeepSeek-V3 and the original R1 on every dimension "
              "that fixes the active count, so the reported 37B active parameters carry over unchanged."),
}


p = argparse.ArgumentParser()
p.add_argument('--sources', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--points-csv', type=Path, default=None)
p.add_argument('--models-csv', type=Path, default=None)
p.add_argument('--header-source', type=Path, default=None)
a = p.parse_args()
if a.points_csv or a.models_csv:
    assert a.points_csv and a.models_csv and a.header_source, \
        '--points-csv, --models-csv and --header-source are used together'
src, out = a.sources.resolve(), a.output.resolve()
assert not out.exists(), f'output already exists: {out}'
assert src not in out.parents and src != out, 'output must not be written inside the retained sources'

boards = {
    'chess-text-v1': read_board(src / 'kaggle-chess-text-v1-leaderboard.json', T1),
    'chess-text-v2': read_board(src / 'kaggle-chess-text-v2-leaderboard.json', T2),
    'chess-text-openings-v1': read_board(src / 'kaggle-chess-text-openings-v1-leaderboard.json', O1),
}
russek = json.loads((src / 'russek-move-times-by-elo-bin.json').read_text())
usage = json.loads((src / 'chess-replay-usage-by-model.json').read_text())
durations = json.loads((src / 'chess-replay-durations-and-call-details-coverage.json').read_text())

tests = {b: cost_test(b, boards[b], PRICES if b != 'chess-text-v2' else PRICES_V2)
         for b in ('chess-text-v1', 'chess-text-openings-v1', 'chess-text-v2')}

# DeepSeek-R1-0528 has no public list price. Its two version 1 boards share a prompt and a price, so the
# marginal cost per published token gives a central output price and a residual prompt cost. Both boards'
# costs are rounded, though, and propagating both roundings widens the result until it constrains nothing:
# the interval below spans negative prompt lengths. The central value is reported, and the prompt actually
# used for the row is justified on other grounds (see DS_PROMPT_TOKENS).
d_t, d_o = boards['chess-text-v1']['DeepSeek-R1'], boards['chess-text-openings-v1']['DeepSeek-R1']
dT, dC = d_t['avg_tokens_per_turn'], d_t['avg_cost_per_turn_cents']
oT, oC = d_o['avg_tokens_per_turn'], d_o['avg_cost_per_turn_cents']
# Half the last published place on each board, in cents. The openings board publishes two decimals for
# every other model, but DeepSeek's figure there is 10.8, which cannot distinguish a two-decimal 10.80 from
# a one-decimal publication, so the wider one-decimal bound is used for it.
DS_HALF_T, DS_HALF_O = 0.05, 0.05
ds_p_out = (oC - dC) / (oT - dT) * 1e4
DS_P_IN = 3.00                                 # the $3/$7 host pair the central output price matches
prompt_extremes = []
p_out_extremes = []
for st in (-1, 1):
    for so in (-1, 1):
        ct, co = dC + st * DS_HALF_T, oC + so * DS_HALF_O
        po = (co - ct) / (oT - dT) * 1e4
        p_out_extremes.append(po)
        prompt_extremes.append((ct - dT * po * 1e-4) * 1e-2 / (DS_P_IN * 1e-6))
deepseek = {
    'central_output_price_usd_per_million': ds_p_out,
    'output_price_interval_usd_per_million': [min(p_out_extremes), max(p_out_extremes)],
    'central_prompt_cost_per_move_cents': dC - dT * ds_p_out * 1e-4,
    'assumed_input_price_usd_per_million': DS_P_IN,
    'central_prompt_tokens': (dC - dT * ds_p_out * 1e-4) * 1e-2 / (DS_P_IN * 1e-6),
    'prompt_tokens_interval': [min(prompt_extremes), max(prompt_extremes)],
    'solve_constrains_prompt': min(prompt_extremes) > 0,
    'note': ('No public list price for the hosted endpoint. The central output price matches a known $3/$7 '
             'per million host pair to within 0.4%, but both boards publish cost rounded, and propagating '
             'both roundings gives the intervals above: the output price is bounded loosely and the prompt '
             'is not bounded at all, the interval including negative lengths. The two-board solve therefore '
             'fixes no prompt length for this model.'),
}
# Prompt used for the row. The two-board solve is uninformative, so the value rests on the prompt structure
# being the same text for every model on this harness: the eight prompts solved from published list prices
# span 328 to 1010 tokens, and 328 to 520 once Grok 4's distinctive xAI tokenization is set aside. This value
# is the two-board solve's central figure, which sits just under that band. The row is insensitive to the
# choice: across the whole 328-520 band compute moves by less than 1.6%, and DeepSeek V3.2's replay-measured
# 423.7 tokens, on the same tokenizer, moves it by 0.8%.
DS_PROMPT_TOKENS = 310.4
DS_PROMPT_BASIS = ('cross-model prompt-length pattern on this harness; the two-board cost solve is '
                   'uninformative about the prompt once both roundings are propagated')

# Prompt estimates are rounded to one decimal so the published token totals and FLOP values are exact.
PROMPT = {}
for name, _ in ROWS:
    if name == 'DeepSeek-R1':
        PROMPT[name] = (DS_PROMPT_TOKENS, None, DS_PROMPT_BASIS)
    else:
        t = tests['chess-text-openings-v1'][name]
        PROMPT[name] = (round(t['prompt_tokens_implied'], 1), t['prompt_tokens_implied_rounding_bound'],
                        'chess-text-openings v1 cost column, solved at list prices')

groups = russek['means'][PRIMARY_TIME_CONTROL]['elo_groups']
rows, excluded = [], []
for name, board_name in ROWS:
    b = boards[board_name][name]
    m = MODELS[b['model_proxy_slug'] or '']
    fpt = 2 * m['active']
    out_tokens = b['avg_tokens_per_turn']
    prompt, prompt_pm, prompt_basis = PROMPT[name]
    tokens = out_tokens + prompt
    edges, label = bin_for(b['estimated_human_elo'])
    g = groups[label]
    alt_agent, alt_kind = ALT_PROMPT[name]
    alt_p = usage['by_agent'].get(alt_agent, {}).get('mean_prompt_tokens_per_move')
    other = 'chess-text-openings-v1' if board_name == 'chess-text-v1' else 'chess-text-v1'
    ob = boards[other].get(name)
    rows.append({
        'display_name': name, 'board': board_name, 'model_id': m['model_id'],
        'model_proxy_slug': b['model_proxy_slug'], 'model_assumption_source': m['source'],
        'active_parameters': m['active'], 'flops_per_token': fpt,
        'published_avg_tokens_per_turn_output_only': out_tokens,
        'prompt_tokens_added': prompt, 'prompt_tokens_rounding_bound': prompt_pm,
        'prompt_estimate_basis': prompt_basis,
        'tokens_total_per_move': tokens,
        'compute_flops_per_move': tokens * fpt,
        'game_arena_elo': b['game_arena_elo'], 'game_arena_elo_ci': b['game_arena_elo_ci'],
        'estimated_human_elo': b['estimated_human_elo'],
        'estimated_human_elo_ci': b['estimated_human_elo_ci'],
        'avg_cost_per_turn_cents': b['avg_cost_per_turn_cents'], 'evaluation_date': b['evaluation_date'],
        'human_rating_bin': f'({edges[0]},{edges[1]}]', 'human_rating_bin_label': label,
        'human_time_seconds_300+0': g['mean_own_clock_seconds'],
        'human_time_seconds_rounded': round(g['mean_own_clock_seconds'], 1),
        'human_move_observations': g['move_observations'],
        'human_time_scenarios_by_time_control': {
            tc: russek['means'][tc]['elo_groups'][label]['mean_own_clock_seconds']
            for tc in ('180+0', '180+2', '300+0', '300+3')},
        'human_skill': 'typical' if b['estimated_human_elo'] > 1250 else 'novice',
        'prompt_scenario_replay_measured': None if alt_p is None else {
            'replay_agent': alt_agent, 'relationship': alt_kind, 'mean_prompt_tokens_per_move': alt_p,
            'tokens_total_per_move': out_tokens + alt_p,
            'compute_flops_per_move': (out_tokens + alt_p) * fpt,
            'change_vs_primary': (out_tokens + alt_p) / tokens - 1},
        'other_board_cross_check': None if not ob else {
            'board': other, 'estimated_human_elo': ob['estimated_human_elo'],
            'estimated_human_elo_ci': ob['estimated_human_elo_ci'],
            'avg_tokens_per_turn': ob['avg_tokens_per_turn'],
            'elo_difference': ob['estimated_human_elo'] - b['estimated_human_elo']},
    })
for name, reason in EXCLUDED.items():
    b = boards['chess-text-v1'].get(name) or boards['chess-text-openings-v1'].get(name)
    excluded.append({'display_name': name, 'estimated_human_elo': b['estimated_human_elo'],
                     'avg_tokens_per_turn': b['avg_tokens_per_turn'], 'reason': reason})
rows.sort(key=lambda r: -r['estimated_human_elo'])

vr = list(usage['verification_subset_ratio_prompt_plus_generation'].values())
flops = [r['compute_flops_per_move'] for r in rows]
dmeans = [v['mean_seconds_per_move'] for v in durations['by_agent'].values()]
result = {
    'boards': {'chess-text-v1': 'leaderboard version 1, evaluated 2025-08-21',
               'chess-text-openings-v1': 'Chess Openings leaderboard version 1',
               'chess-text-v2': 'leaderboard version 2, evaluated 2026-09-08, used only for the token tests'},
    'work_unit': 'one move decision by the model in a complete game',
    'compute_formula': ('compute_flops = (published Avg. Tokens/Turn, which is output tokens including '
                        'reasoning on the version 1 boards, + estimated mean prompt tokens) * 2 * '
                        'active_parameters'),
    'human_formula': ('human_time = count-weighted mean own-clock seconds per move, Lichess 5+0 blitz '
                      '(time control %s), in the rating bin containing the estimated human Elo'
                      % PRIMARY_TIME_CONTROL),
    'token_column_cost_test': {
        'method': ('Sign of cost/T - list output price. Positive rejects the prompt-plus-output reading at '
                   'any non-negative prompt length; negative rejects the output-only reading.'),
        'by_board': tests,
        'verdict': {b: ('output tokens only' if all(v['h2_output_only_possible'] for v in t.values())
                        else 'prompt plus output' if all(v['h1_prompt_plus_output_possible'] for v in t.values())
                        else 'mixed') for b, t in tests.items()},
        'deepseek_r1_0528_price_recovery': deepseek,
    },
    'version_2_replay_verification': {
        'method': usage['note'], 'n_models': len(vr), 'episodes_parsed': usage['episodes_parsed'],
        'ratio_prompt_plus_generation_over_published': {
            'median': statistics.median(vr), 'min': min(vr), 'max': max(vr)},
    },
    'realized_ai_move_durations_version_2': {
        'moves_total': durations['moves_total'],
        'moves_with_duration': durations['moves_with_call_details'],
        'call_details_missing_fraction': durations['fraction_missing'],
        'per_model_mean_seconds_min': min(dmeans), 'per_model_mean_seconds_max': max(dmeans),
        'per_model_mean_seconds_median': statistics.median(dmeans),
        'o3': durations['by_agent'].get('o3'),
    },
    'compute_flops_range': {'min': min(flops), 'max': max(flops), 'ratio': max(flops) / min(flops)},
    'rows': rows,
    'excluded': excluded,
}
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, indent=2) + '\n')

if a.points_csv:
    point_header = a.header_source.joinpath('points.csv').read_text().splitlines()[0].split(',')
    model_header = a.header_source.joinpath('models.csv').read_text().splitlines()[0].split(',')
    point_rows = build_point_rows(rows)
    for row in point_rows:
        for field, limit in FIELD_MAX.items():
            assert len(row[field]) <= limit, \
                f"{row['point_id']}: {field} is {len(row[field])} characters, over the {limit} maximum"
    a.points_csv.parent.mkdir(parents=True, exist_ok=True)
    with a.points_csv.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=point_header)
        w.writeheader()
        for row in point_rows:
            w.writerow(row)
    with a.models_csv.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=model_header)
        w.writeheader()
        w.writerow(MODEL_ROW)
    print('wrote %d point rows and 1 model row' % len(point_rows))

for b, v in result['token_column_cost_test']['verdict'].items():
    print(f'{b:26s} -> {v}')
print()
for r in rows:
    print(f"{r['display_name']:16s} {r['board']:22s} elo {r['estimated_human_elo']:6.0f}  out {r['published_avg_tokens_per_turn_output_only']:9.1f}"
          f" + prompt {r['prompt_tokens_added']:7.1f} (+/-{('%5.0f' % r['prompt_tokens_rounding_bound']) if r['prompt_tokens_rounding_bound'] else '  n/a'}) = {r['tokens_total_per_move']:9.1f}"
          f"  flops {r['compute_flops_per_move']:.6g}  human {r['human_time_seconds_rounded']:4.1f}s  {r['human_skill']}")
print('\ncompute range %.4g to %.4g, ratio %.1fx' % (min(flops), max(flops), max(flops)/min(flops)))
