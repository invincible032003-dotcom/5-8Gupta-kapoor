"""Check that everything the dashboard renders is strict LaTeX.

    python3 tools/check_latex.py [path/to/dashboard.html]

Covers every text the page renders through its maths renderer: the 720 PYQs,
the forecast bank, the topic notes and the Gupta Kapoor bank with its sheets.

  1. Every $...$ / $$...$$ segment is typeset by the dashboard's own KaTeX build
     in strict mode (throwOnError, strict:'error', the page's macro table),
     after the same masking and trimming the page applies.
  2. Outside maths there is no maths left: no Unicode maths symbols, no ASCII
     operators such as <=, ->, x^2, sqrt(, +/-, and nothing that
     tools/latexify.py would still convert (a bare variable, "n - 1", ...).
     Code in backticks is exempt.
  3. Dollar signs balance in every field.

Exit status 1 on any failure.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import latexify as L          # noqa: E402

KATEX_CHECK = HERE.parent / 'ch5-8-dashboard-src' / 'katex_check.js'
UNICODE_MATH = re.compile('[Ͱ-Ͽ⁰-₟←-⇿∀-⋿⟰-⟿'
                          '⤀-⥿±²³¹¼-¾×÷…]')
ASCII_MATH = re.compile(r'<=|>=|!=|->|=>|\+/-|\bplus or minus\b|(?<=[A-Za-z0-9)\]])\^|\bsqrt\s*\(|\b[A-Za-z]_\{?\w')


def gk_blocks(html):
    m = re.search(r'window\.gkMeta = (.*?);\nwindow\.gkData = \[\n(.*?)\n\];', html, re.S)
    if not m:
        return None, []
    return json.loads(m.group(1)), [json.loads(l.rstrip(',')) for l in m.group(2).split('\n')]


def fields(html):
    """(owner, text, convertible) for every rendered text."""
    import latex_fixes
    data = L.load(html)
    out = []
    for name in ('quizData', 'forecastData'):
        for q in data[name][2]:
            comp = str(q.get('unit', '')).startswith('Computer') or q['id'] in latex_fixes.COMPUTER_STYLE
            for lab, c, k in L.text_slots(q):
                out.append((f'{q["id"]}:{lab}', c[k], 'comp' if comp else 'std'))
    for code, ti in data['quizMeta'][2].get('topicIntel', {}).items():
        out.append((f'intel:{code}:pattern', ti['pattern'], None))
        out.append((f'intel:{code}:mustKnow', ti['mustKnow'], None))
    meta, items = gk_blocks(html)
    for q in items:
        texts = [('question', q['question']), ('ask', q.get('ask', '')), ('examShortcut', q['examShortcut'])]
        texts += [(f'stmts[{i}]', s) for i, s in enumerate(q.get('stmts') or [])]
        texts += [(f'options[{i}]', s) for i, s in enumerate(q['options'])]
        texts += [(f'tipsTricks[{i}]', s) for i, s in enumerate(q['tipsTricks'])]
        texts += [(f'solution[{i}]', s['text']) for i, s in enumerate(q['solution'])]
        out += [(f'{q["id"]}:{lab}', t, None) for lab, t in texts if t]
    for sh in (meta or {}).get('sheets', []):
        for b in sh['blocks']:
            cells = [b.get('text')] + (b.get('items') or []) + (b.get('head') or []) + [c for r in b.get('rows') or [] for c in r]
            out += [(f'sheet:{sh["title"]}', t, None) for t in cells if t]
    return out


def main(argv):
    target = Path(argv[0]) if argv else L.TARGET
    html = target.read_text(encoding='utf-8')
    fails, segs = [], []
    all_fields = fields(html)
    for owner, text, convertible in all_fields:
        if text.replace('$$', '').count('$') % 2:
            fails.append(f'{owner}: unbalanced $')
        for m in L.SEG_RE.finditer(text):
            tex = m.group(1) if m.group(1) is not None else m.group(2)
            segs.append({'id': owner, 'tex': tex, 'display': m.group(1) is not None})
        # the page applies *italic* before `code`, so an asterisk in code breaks it
        for cm in re.finditer(r'```[\s\S]*?```|`[^`]*`', L.SEG_RE.sub(' ', text)):
            if '*' in cm.group(0):
                fails.append(f'{owner}: asterisk inside a code span: {cm.group(0)[:60]!r}')
        plain = re.sub(r'```[\s\S]*?```|`[^`]*`', ' ', L.SEG_RE.sub(' ', text))
        bad = sorted(set(UNICODE_MATH.findall(plain)))
        if bad:
            fails.append(f'{owner}: Unicode maths outside $...$ {bad}: {plain[:100]!r}')
        m = ASCII_MATH.search(plain)
        if m:
            fails.append(f'{owner}: ASCII maths outside $...$ {m.group(0)!r}: {plain[max(0, m.start() - 50):m.end() + 40]!r}')
        if convertible:
            comp = convertible == 'comp'
            if L.stage_prose(L.stage_rules(text, comp), comp) != text:
                fails.append(f'{owner}: maths left in the prose: {text[:120]!r}')
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(segs, f)
    r = subprocess.run(['node', str(KATEX_CHECK), f.name], capture_output=True, text=True)
    if r.returncode not in (0, 1):
        fails.append('katex_check.js crashed: ' + r.stderr[:300])
    fails += [ln for ln in r.stdout.splitlines() if ln.strip()]
    print(f'{len(all_fields)} rendered texts, {len(segs)} formulas checked in KaTeX strict mode')
    for x in fails[:200]:
        print('FAIL', x)
    print('OK' if not fails else f'{len(fails)} failure(s)')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
