"""Build the single-file offline dashboard.

    python3 verify.py && python3 build.py

Reads bank/ch*.txt (problems), formulas.py (sheets), src/ (UI) and vendor/ (KaTeX),
and writes ../GuptaKapoor-Ch5-8-ISS-Objective-Dashboard.html with everything inlined.

The bank is authored with the key mostly in position A; here every item's options are
permuted deterministically so that the keys are spread evenly over (a)-(d), and any
"Option X" references inside solutions are rewritten to the new labels.
"""
import datetime
import json
import random
import re
from collections import Counter
from pathlib import Path

import bankparse
from formulas import SECTIONS

HERE = Path(__file__).parent
OUT = HERE.parent / 'GuptaKapoor-Ch5-8-ISS-Objective-Dashboard.html'
OPTION_REF = re.compile(r'\b([Oo]ption) ([A-D])\b')
SOURCE = 'S.C. Gupta & V.K. Kapoor, Fundamentals of Mathematical Statistics — Chapters 5–8'


def permute_options(chapter):
    items = chapter['items']
    rng = random.Random(f'gk58-ch{chapter["num"]}')
    targets = ([0, 1, 2, 3] * (len(items) // 4 + 1))[:len(items)]
    rng.shuffle(targets)
    for it, target in zip(items, targets):
        r = random.Random(it['id'])
        wrong = [i for i in range(4) if i != it['ans']]
        r.shuffle(wrong)
        order = wrong[:]
        order.insert(target, it['ans'])          # order[new_position] = old_position
        new_label = {'ABCD'[old]: 'abcd'[new] for new, old in enumerate(order)}
        it['opts'] = [it['opts'][old] for old in order]
        it['ans'] = target

        def fix(text):
            return OPTION_REF.sub(lambda m: f'{m.group(1)} ({new_label[m.group(2)]})', text)
        it['q'] = fix(it['q'])
        it['steps'] = [fix(s) for s in it['steps']]
        it['sc'] = fix(it['sc'])
        it['tr'] = fix(it['tr'])


def build_data(chapters):
    items, chs = [], []
    for ch in chapters:
        permute_options(ch)
        counts = Counter(it['topic'] for it in ch['items'])
        chs.append({
            'num': ch['num'], 'title': ch['title'],
            'topics': [{'code': t['code'], 'title': t['title'], 'n': counts[t['code']]}
                       for t in ch['topics']],
            'n': len(ch['items']),
        })
        for it in ch['items']:
            items.append({k: v for k, v in it.items() if not k.startswith('_')})
    return {
        'meta': {
            'title': 'Gupta & Kapoor Ch 5–8 · ISS Objective Problem Bank',
            'source': SOURCE,
            'built': datetime.date.today().isoformat(),
            'total': len(items),
        },
        'chapters': chs,
        'items': items,
        'sheets': SECTIONS,
    }


def script_safe(text):
    return text.replace('</', '<\\/')


def main():
    chapters = bankparse.load_all(HERE / 'bank')
    data = build_data(chapters)
    keys = Counter('abcd'[it['ans']] for it in data['items'])
    tpl = (HERE / 'src' / 'template.html').read_text(encoding='utf-8')
    parts = {
        '{{KATEX_CSS}}': (HERE / 'vendor' / 'katex.min.css').read_text(encoding='utf-8'),
        '{{APP_CSS}}': (HERE / 'src' / 'app.css').read_text(encoding='utf-8'),
        '{{KATEX_JS}}': (HERE / 'vendor' / 'katex.min.js').read_text(encoding='utf-8'),
        '{{DATA_JS}}': 'window.BANK = ' + script_safe(json.dumps(data, ensure_ascii=False)) + ';',
        '{{APP_JS}}': (HERE / 'src' / 'app.js').read_text(encoding='utf-8'),
    }
    html = tpl
    for k, v in parts.items():
        assert k in html, k
        html = html.replace(k, v)
    OUT.write_text(html, encoding='utf-8')
    print(f'wrote {OUT.name}: {len(html)/1e6:.2f} MB, {len(data["items"])} items, '
          f'{len(data["sheets"])} sheet cards, keys {dict(sorted(keys.items()))}')


if __name__ == '__main__':
    main()
