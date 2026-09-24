"""Validate the problem bank.

1. Structure (via bankparse): four distinct options, a valid key, steps and a shortcut.
2. Every CHK line is executed with sympy / scipy in scope and must come out True.
   A CHK is either one expression, or statements that set `ok`.
3. Every $...$ / $$...$$ segment is rendered with the vendored KaTeX (throwOnError),
   and the text outside math may only use a small whitelist of HTML tags.

Run:  python3 verify.py            (exit status 1 on any failure)
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import bankparse

HERE = Path(__file__).parent
MATH_RE = re.compile(r'\$\$(.+?)\$\$|\$(.+?)\$', re.S)
ALLOWED_TAG_RE = re.compile(r'</?(br|b|i|u|sub|sup|small)\s*/?>')
SHEET_TAG_RE = re.compile(r'</?(br|b|i|u|sub|sup|small|p|ul|ol|li|table|thead|tbody|tr|td|th|h4)\s*/?>')


def chk_namespace():
    import math
    import numpy as np
    import sympy
    from scipy import integrate as si
    from scipy import stats as st
    ns = {}
    exec('from sympy import *', ns)
    ns.update({
        'math': math, 'np': np, 'st': st, 'si': si, 'sp': sympy,
        'R': sympy.Rational,
        'x': sympy.Symbol('x', real=True), 'y': sympy.Symbol('y', real=True),
        'z': sympy.Symbol('z', real=True), 'u': sympy.Symbol('u', real=True),
        'v': sympy.Symbol('v', real=True),
        't': sympy.Symbol('t', real=True), 's': sympy.Symbol('s'),
        'k': sympy.Symbol('k'), 'n': sympy.Symbol('n', positive=True, integer=True),
        'p': sympy.Symbol('p', positive=True), 'q': sympy.Symbol('q', positive=True),
        'lam': sympy.Symbol('lam', positive=True), 'a': sympy.Symbol('a', positive=True),
        'b': sympy.Symbol('b', positive=True), 'th': sympy.Symbol('th', positive=True),
        'oo': sympy.oo,
    })

    def close(a, b, tol=1e-6):
        return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))
    ns['close'] = close

    def eq(a, b):
        return sympy.simplify(sympy.sympify(a) - sympy.sympify(b)) == 0
    ns['eq'] = eq
    return ns


def is_true(res):
    """Accept only genuine booleans (python, numpy or sympy), never a stray number."""
    import numpy as np
    import sympy
    if isinstance(res, (bool, np.bool_)):
        return bool(res)
    return res is sympy.true


def run_checks(chapters):
    fails, n_chk, n_items_chk = [], 0, 0
    for ch in chapters:
        for it in ch['items']:
            if it['_chk']:
                n_items_chk += 1
            for code in it['_chk']:
                n_chk += 1
                ns = chk_namespace()
                try:
                    try:
                        res = eval(compile(code, it['id'], 'eval'), ns)
                    except SyntaxError:
                        exec(compile(code, it['id'], 'exec'), ns)
                        res = ns.get('ok')
                    if not is_true(res):
                        fails.append(f'{it["id"]} ({it["_where"]}): CHK false -> {code!r} gave {res!r}')
                except Exception as e:  # noqa: BLE001
                    fails.append(f'{it["id"]} ({it["_where"]}): CHK error {type(e).__name__}: {e} in {code!r}')
    return fails, n_chk, n_items_chk


def text_fields(it):
    yield 'q', it['q']
    for i, o in enumerate(it['opts']):
        yield f'opt{i}', o
    for i, s in enumerate(it['steps']):
        yield f'step{i}', s
    yield 'sc', it['sc']
    if it['tr']:
        yield 'tr', it['tr']


def collect_math(chapters, extra_texts=()):
    segs, fails = [], []

    def scan(owner, field, text, tag_re=ALLOWED_TAG_RE):
        if text.count('$') % 2:
            fails.append(f'{owner} {field}: odd number of $')
        plain = MATH_RE.sub(' ', text)
        stripped = tag_re.sub('', plain)
        if '<' in stripped or '>' in stripped:
            fails.append(f'{owner} {field}: raw < or > outside math: {plain[:120]!r}')
        for m in MATH_RE.finditer(text):
            tex = m.group(1) if m.group(1) is not None else m.group(2)
            segs.append({'id': f'{owner}:{field}', 'tex': tex, 'display': m.group(1) is not None})

    for ch in chapters:
        for it in ch['items']:
            for field, text in text_fields(it):
                scan(it['id'], field, text)
    for owner, text in extra_texts:
        scan(owner, 'html', text, SHEET_TAG_RE)
    return segs, fails


def katex_check(segs):
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(segs, f)
        name = f.name
    r = subprocess.run(['node', str(HERE / 'katex_check.js'), name], capture_output=True, text=True)
    if r.returncode not in (0, 1):
        return [f'katex_check.js crashed: {r.stderr}']
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


def main():
    chapters = bankparse.load_all(HERE / 'bank')
    total = sum(len(c['items']) for c in chapters)
    fails, n_chk, n_items_chk = run_checks(chapters)
    from formulas import SECTIONS
    extra = [(f'sheet:{sec["title"]}', sec['html']) for sec in SECTIONS]
    segs, mfails = collect_math(chapters, extra)
    kfails = katex_check(segs)
    for c in chapters:
        print(f'Chapter {c["num"]}: {len(c["items"])} items')
    print(f'{total} items; {n_items_chk} with numeric/symbolic checks ({n_chk} checks); {len(segs)} math segments')
    allf = fails + mfails + kfails
    for f in allf:
        print('FAIL', f)
    print('OK' if not allf else f'{len(allf)} failure(s)')
    sys.exit(1 if allf else 0)


if __name__ == '__main__':
    main()
