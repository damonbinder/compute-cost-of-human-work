"""Interpret the released calendar task templates; no model or clock inference."""
import re

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
DAY_PATTERN = '(' + '|'.join(DAYS) + ')'
RANGE = r'(\d{1,2}:\d{2}) to (\d{1,2}:\d{2})'


def slot(t):
    h, m = map(int, t.split(':'))
    assert m in (0, 30), t
    return 2 * h + m // 30


def answer(response, tolerant=False):
    if tolerant:
        response = response.replace('*', '').replace('`', '').replace('_', '')
    m = re.search(DAY_PATTERN + r', (\d{1,2}:\d{2}) - (\d{1,2}:\d{2})', response)
    if not m:
        return None
    return (m[1], slot(m[2]), slot(m[3]))


def task_details(row):
    target = row['prompt_0shot'].rsplit('TASK: ', 1)[1].rsplit('SOLUTION: ', 1)[0].strip()
    assert row['prompt_5shot'].rsplit('TASK: ', 1)[1].rsplit('SOLUTION: ', 1)[0].strip() == target
    paras = target.split('\n\n')
    assert len(paras) == 3, paras
    header, calendars, preferences = paras
    days = re.findall(DAY_PATTERN, header)
    assert len(days) == int(row['num_days'])
    people_text = re.search(r'meeting for (.+?) for (?:half an hour|one hour)', header)[1]
    people = re.split(r', | and ', people_text)
    assert len(people) == int(row['num_people'])
    lines = [x.strip() for x in calendars.splitlines()[1:] if x.strip()]
    assert len(lines) == len(people)
    busy = {day: set() for day in days}
    schedule_blocks = []
    person_days = []
    for name, line in zip(people, lines):
        assert line.startswith(name), (name, line)
        dayparts = list(re.finditer(DAY_PATTERN + ' during ', line))
        if not dayparts:
            assert any(x in line for x in ['no meetings', 'wide open', 'is free']), line
        for i, match in enumerate(dayparts):
            day = match[1]
            stop = dayparts[i + 1].start() if i + 1 < len(dayparts) else len(line)
            tail = line[match.end():stop]
            spans = re.findall(RANGE, tail)
            assert spans, tail
            person_days.append({'person': name, 'day': day, 'blocks': len(spans)})
            for lo, hi in spans:
                a, b = slot(lo), slot(hi)
                assert 18 <= a < b <= 34
                busy[day].update(range(a, b))
                schedule_blocks.append({'person': name, 'day': day, 'start': a, 'end': b})
    pref_text = preferences.replace("Find a time that works for everyone's schedule and constraints.", '').strip()
    exclusions = []
    for match in re.finditer(DAY_PATTERN + r'(?: (before|after) (\d{1,2}:\d{2}))?', pref_text):
        day, direction, time = match.groups()
        if direction == 'before':
            a, b = 18, slot(time)
        elif direction == 'after':
            a, b = slot(time), 34
        else:
            a, b = 18, 34
        busy[day].update(range(a, b))
        exclusions.append({'day': day, 'direction': direction or 'whole_day', 'start': a, 'end': b})
    earliest = bool(re.search(r'earl(?:i|ie)st', pref_text))
    duration = int(float(row['duration']) * 2)
    assert duration in (1, 2)
    feasible = [(day, start, start + duration) for day in days for start in range(18, 35 - duration)
                if not set(range(start, start + duration)) & busy[day]]
    valid = feasible[:1] if earliest else feasible
    return dict(target=target, people=people, days=days, schedule_blocks=schedule_blocks,
                person_days=person_days, preferences=pref_text, exclusions=exclusions,
                earliest=earliest, duration_slots=duration, feasible=feasible, valid=valid)
