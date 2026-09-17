"""Recompute OCR human-time review from retained text and assumptions.

Usage: python3 review_human.py SOURCE_DIR NEW_OUTPUT_JSON
Python standard library only. Does not alter inputs; output must not exist.
"""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source_dir', type=Path)
parser.add_argument('output_json', type=Path)
args = parser.parse_args()
x = json.loads((args.source_dir / 'human-review-inputs.json').read_text())
text = ' '.join((args.source_dir / 'phototest.gold.txt').read_text().split())
phrase = x['repeated_sentence']
count = text.count(phrase)
assert count == 4
prefix = text[:text.index(phrase)]
assert prefix + ' '.join([phrase] * count) == text
unique_text = prefix + phrase

def seconds(characters, wpm):
    return characters / x['standard_word_characters'] / wpm * 60

mean = x['typing_mean_standard_wpm']
sd = x['typing_sd_standard_wpm']
full_typing = seconds(len(text), mean)
unique_typing = seconds(len(unique_text), mean)
reading = x['initial_reading_seconds_assumed']
checking = x['comparison_and_correction_seconds_assumed']
copying = x['copy_paste_seconds_assumed']
# Second-order delta-method sensitivity, not recovered empirical mean time.
inverse_rate_factor = 1 + (sd / mean) ** 2
out = {
    'normalized_characters': len(text),
    'words': len(text.split()),
    'repeated_sentence_characters': len(phrase),
    'repetitions': count,
    'fresh_characters_with_copy_paste': len(unique_text),
    'copy_paste_avoids_characters': len(text) - len(unique_text),
    'typing_at_mean_rate_seconds': full_typing,
    'typing_unique_at_mean_rate_seconds': unique_typing,
    'ordinary_reading_rate_transfer_seconds': len(text.split()) / x['reported_adult_english_nonfiction_mean_reading_wpm'] * 60,
    'copy_paste_workflow_seconds': unique_typing + reading + copying + checking,
    'fresh_typing_workflow_seconds': full_typing + reading + checking,
    'delta_method_inverse_rate_factor': inverse_rate_factor,
    'copy_paste_delta_method_seconds': unique_typing * inverse_rate_factor + reading + copying + checking,
    'fresh_typing_delta_method_seconds': full_typing * inverse_rate_factor + reading + checking,
    'fast_copy_paste_scenario_seconds': seconds(len(unique_text), x['typing_90th_percentile_approx_standard_wpm']) + 10 + 7 + 20,
    'slow_fresh_typing_scenario_seconds': seconds(len(text), x['typing_10th_percentile_approx_standard_wpm']) + 15 + 25,
    'central_human_seconds_rounded': x['central_human_seconds_rounded'],
    'sensitivity_seconds': x['sensitivity_seconds'],
    'human_time_statistic': 'point_estimate',
    'human_time_evidence': 'transferred_timings',
    'human_time_method': 'estimated',
    'human_attempts': 'not_applicable'
}
with args.output_json.open('x') as f:
    json.dump(out, f, indent=2)
    f.write('\n')
print(json.dumps(out, indent=2))
