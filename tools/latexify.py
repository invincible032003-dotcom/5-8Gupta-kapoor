"""Make every piece of mathematics in the PYQ / forecast banks real LaTeX.

    python3 tools/latexify.py                  # rewrite the dashboard in place
    python3 tools/latexify.py --report FILE    # write what would change to FILE
    python3 tools/latexify.py --try "text"     # convert one string (for testing)

The explanations in UPSC-ISS-Statistics-Dashboard-STANDALONE.html were written
partly in ASCII maths ("n - 1", "x^2", "sqrt(3)", "P(A)", "<=") and partly in
$...$ LaTeX, and an earlier automatic pass left some formulas cut in half
("from 0 to $1 = 2x$").  This script

  1. applies the hand-written corrections in latex_fixes.py (semantic repairs
     that no rule can make safely, and clean rewrites of the topic notes);
  2. repairs recurring broken patterns inside and around $...$ by rule;
  3. wraps the maths left in running text in $...$, turning ASCII operators
     into LaTeX ones and merging a formula with maths written next to it.

Words stay words: only variables, numbers joined by operators, function calls
and operators move into maths.  Code, option labels such as "(c)", question ids
such as 2018-Q35, IEEE names, units and year ranges are left alone, and in the
Computer Applications unit only lower-case variables are converted.  Running the
script a second time changes nothing.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / 'UPSC-ISS-Statistics-Dashboard-STANDALONE.html'
sys.path.insert(0, str(Path(__file__).resolve().parent))

SEG_RE = re.compile(r'\$\$([\s\S]*?)\$\$|\$([^$]*)\$')
UNBALANCED = []          # (text of a run) that was left alone because its brackets do not match


# ---------------------------------------------------------------- segments
def split(text):
    """-> list of ('t', text) | ('m', tex, display)."""
    out, last = [], 0
    for m in SEG_RE.finditer(text):
        if m.start() > last:
            out.append(('t', text[last:m.start()]))
        if m.group(1) is not None:
            out.append(('m', m.group(1), True))
        else:
            out.append(('m', m.group(2), False))
        last = m.end()
    if last < len(text):
        out.append(('t', text[last:]))
    return out


def join(segs):
    return ''.join(s[1] if s[0] == 't' else ('$$%s$$' if s[2] else '$%s$') % s[1] for s in segs)


# ------------------------------------------------------------ vocabulary
GREEK = set('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi rho sigma '
            'tau upsilon phi chi psi omega Gamma Delta Theta Lambda Sigma Phi Psi Omega'.split())
FUNCS = {
    'sqrt': r'\sqrt', 'exp': r'\exp', 'log': r'\log', 'ln': r'\ln', 'max': r'\max', 'min': r'\min',
    'sin': r'\sin', 'cos': r'\cos', 'tan': r'\tan', 'tanh': r'\tanh', 'det': r'\det',
    'E': r'\operatorname{E}', 'Var': r'\operatorname{Var}', 'Cov': r'\operatorname{Cov}',
    'Corr': r'\operatorname{Corr}', 'P': r'\operatorname{P}', 'Pr': r'\operatorname{P}',
    'V': 'V', 'f': 'f', 'F': 'F', 'g': 'g', 'G': 'G', 'h': 'h', 'M': 'M', 'K': 'K', 'L': 'L',
    'u': 'u', 'v': 'v', 'w': 'w', 'y': 'y', 'p': 'p', 'q': 'q', 'r': 'r', 'H': 'H', 'N': 'N',
    'phi': r'\phi', 'Phi': r'\Phi', 'psi': r'\psi',
}
WORDFUNCS = set('mean median mode arctanh sinh cosh prod sgn sign logit erf floor ceil'.split())
OPS = {'<=': r'\le', '>=': r'\ge', '!=': r'\ne', '==': '=', '->': r'\to', '=>': r'\Rightarrow',
       '<->': r'\leftrightarrow', '+/-': r'\pm', '+-': r'\pm', 'plus or minus': r'\pm',
       '{': r'\{', '}': r'\}', '=': '=', '<': '<', '>': '>', '+': '+', '-': '-',
       '*': r'\times', '/': '/', '^': '^', '\u2212': '-', '\u00d7': r'\times', '\u00b7': r'\cdot',
       '\u00b1': r'\pm', '\u2192': r'\to', '\u2264': r'\le', '\u2265': r'\ge', '\u2260': r'\ne',
       '\u2248': r'\approx', '~': r'\sim'}
# short letter-products that are always maths in these explanations
MWORDS = set('np nq pq npq nqp xy yx xz yz uv ad bc ab ac bd mn nx dx dy dt du dv dr ds dz dw'.split())
# words next to which a lone "x" is a variable ("values of x"), not a times sign
PREP = set('of for when where at in if and or that then with on to from by as is are was be '
           'the each all over respect about than into between below above under per any every '
           'some no only both either neither whether given let put set take write so must can will '
           'would should may might shall has have had does do did lies equals gives takes becomes tends '
           'increases decreases goes runs appears satisfies hence thus not'.split())
# what may follow an event / variable called "A" (otherwise "A" is the article)
AFOLLOW = set('and or is are occurs occur happens happen has have then given but alone only not '
              'fails lies means denotes be was were with implies if when to in of'.split())

TOKEN_RE = re.compile(r'''
   (?P<code>```[\s\S]*?```|`[^`]*`)
 | (?P<keep>\b(?:19|20)\d\d\s*[-\u2013]\s*(?:Q\d+|(?:19|20)?\d\d)\b|\bF[PS]-\d+\b|\bQ\d+\b
      |\b0-1\b|\b\w+'s\b|(?:(?<=[\w$])|^)'s\b|\b\d+\.\d+[a-z]{1,2}\b|\b\d+s\b|\b\d[A-Z]\b|\b\d-D\b|\b[A-D]-\d\b
      |\b\d+(?:\.\d+)?\s(?:m|cm|km|mm|kg|K|s|ms|kB|MB|GB|TB)\b(?=\s+[a-z]|[,.;:)]|$)
      |(?<=[A-Za-z])\((?:s|es)\)|\b\d+(?:st|nd|rd|th)\b|\b\d+(?:\.\d+)?%)
 | (?P<pm>\bplus\ or\ minus\b)
 | (?P<capfunc>\b(?!(?:I{1,3}|IV|VI{0,3}|IX|X{1,3})\b)[A-Z]{2,5}(?=\())
 | (?P<caps>\b[A-Z]{2,}[0-9A-Z]*\b)
 | (?P<optlabel>\((?:[a-dA-D]|i{1,3}|iv|v|vi{0,3})\))
 | (?P<abbr>\b(?:[A-Za-z]\.){2,}|\b(?:vs|etc|cf|viz|approx|resp|eq|Eq|Fig|No|no)\.)
 | (?P<ellipsis>\.\.\.|\u2026)
 | (?P<var2>\b[A-Za-z]{2,4}_(?:\{[^{}]*\}|[A-Za-z0-9]+))
 | (?P<numvar>\b\d+(?:\.\d+)?[a-zA-Z](?![A-Za-z0-9']))
 | (?P<hyph>\b[A-Za-z](?=-[A-Za-z]{2,}))
 | (?P<word>[A-Za-z][A-Za-z']*[A-Za-z]|[A-Za-z](?=')|\b[A-Za-z]{2,}\b)
 | (?P<var>[A-Za-z](?:_\{[^{}]*\}|_[A-Za-z0-9]+|\d{1,2}(?![A-Za-z0-9.]))?'*)
 | (?P<num>\d+(?:\.\d+)?)
 | (?P<op><->|<=|>=|!=|==|->|=>|\+/-|\+-(?=\s*\d)|[=<>+\-*/^\u2212\u00d7\u00b7\u00b1\u2192\u2264\u2265\u2260\u2248~])
 | (?P<lp>[(\[{])
 | (?P<rp>[)\]}])
 | (?P<comma>,)
 | (?P<space>\s+)
 | (?P<other>.)
''', re.X)


class Tok:
    __slots__ = ('kind', 'text', 'tex')

    def __init__(self, kind, text, tex=None):
        self.kind, self.text, self.tex = kind, text, tex

    def __repr__(self):
        return f'{self.kind}:{self.text!r}'


def tokenize(segs):
    toks = []
    for s in segs:
        if s[0] == 'm':
            toks.append(Tok('dmath' if s[2] else 'math', ('$$%s$$' if s[2] else '$%s$') % s[1], s[1]))
            continue
        for m in TOKEN_RE.finditer(s[1]):
            kind = m.lastgroup
            if kind in ('code', 'keep', 'optlabel', 'abbr', 'caps'):
                kind = 'word'
            elif kind == 'pm':
                kind = 'op'
            toks.append(Tok(kind, m.group(0)))
    return toks


def sig(toks, i, step):
    j = i + step
    while 0 <= j < len(toks) and toks[j].kind == 'space':
        j += step
    return toks[j] if 0 <= j < len(toks) else None


def sig_index(toks, i, step):
    j = i + step
    while 0 <= j < len(toks) and toks[j].kind == 'space':
        j += step
    return j if 0 <= j < len(toks) else None


def is_letter_var(t):
    return t is not None and t.kind == 'var' and len(t.text) >= 1 and t.text[0].isalpha()


def classify(toks, comp=False):
    """Refine token kinds: which letters are variables, which 'x' is a times
    sign, which '-' is a hyphen, which Greek names and function names are maths."""
    n = len(toks)
    option_list = False
    for i, t in enumerate(toks):
        nx = toks[i + 1] if i + 1 < n else None
        p, q = sig(toks, i, -1), sig(toks, i, 1)
        # "option c", "options a and d"
        if t.kind == 'word' and t.text.lower() in ('option', 'options'):
            option_list = True
            continue
        if option_list and not (t.kind in ('space', 'comma') or t.text in ('and', 'or')
                                or (t.kind in ('var', 'hyph') and t.text in 'abcdABCD')):
            option_list = False
        if option_list and t.kind in ('var', 'hyph') and t.text in 'abcdABCD':
            t.kind = 'word'
            continue

        if t.kind == 'var2':
            t.kind = 'word' if comp else 'var'
        elif t.kind == 'capfunc':
            t.kind = 'func' if not comp else 'word'
        elif t.kind == 'var':
            letter = t.text[0]
            if comp and letter.isupper():
                t.kind = 'word'
                continue
            if t.text in FUNCS and nx is not None and nx.kind == 'lp':
                t.kind = 'func'
                continue
            if t.text == 'I':
                t.kind = 'word'
                continue
            if t.text == 'A':
                if not (q is None or q.kind in ('op', 'comma', 'rp')
                        or (p is not None and p.kind == 'other' and p.text == '|')
                        or (q.kind == 'other' and q.text == '|')
                        or (q.kind == 'other' and q.text in '.;:?!')
                        or (q.kind == 'word' and q.text in AFOLLOW)
                        or (p is not None and p.kind == 'op')):
                    t.kind = 'word'
                continue
            if t.text == 'a':
                pp = sig(toks, sig_index(toks, i, -1), -1) if sig_index(toks, i, -1) is not None else None
                qi = sig_index(toks, i, 1)
                qq = sig(toks, qi, 1) if qi is not None else None
                if not (q is None or (q.kind in ('rp',) or (q.kind == 'other' and q.text in '.;:|'))
                        or (p is not None and p.kind == 'other' and p.text == '|')
                        or (q.kind == 'word' and q.text == 'over' and is_letter_var(qq))
                        or (q is not None and q.kind == 'op' and q.text != '-')
                        or (p is not None and p.kind == 'op' and p.text != '-')
                        or (nx is not None and nx.kind == 'lp')
                        or (q is not None and (q.kind == 'comma' or q.text in ('and', 'or')) and is_letter_var(qq))
                        or (p is not None and (p.kind == 'comma' or p.text in ('and', 'or')) and is_letter_var(pp))
                        or (p is not None and p.kind == 'word' and p.text in ('over', 'shape', 'scale', 'constant', 'constants', 'parameter', 'parameters')
                            and (q is None or q.kind != 'word'))):
                    t.kind = 'word'
                continue
            if t.text == 'x' and not comp:
                spaced = (i > 0 and toks[i - 1].kind == 'space') and (nx is not None and nx.kind == 'space')

                def hard(tok, left):
                    return tok is not None and (tok.kind in ('num', 'numvar') or tok.kind == ('rp' if left else 'lp'))

                def soft(tok):
                    return tok is not None and tok.kind == 'word' and len(tok.text) > 1 and tok.text.lower() not in PREP
                # "2 x 3", "(height) x (width)", "4 x mean": a number or bracket on at least one side
                if spaced and ((hard(p, True) and (hard(q, False) or soft(q))) or (soft(p) and hard(q, False))):
                    t.kind = 'times'
        elif t.kind == 'word':
            if nx is not None and nx.kind == 'lp' and nx.text == '(' and t.text in WORDFUNCS and not comp:
                t.kind = 'func'
            elif t.text in MWORDS and not comp:
                t.kind = 'var'
            elif t.text in FUNCS and t.text in ('sqrt', 'exp', 'log', 'ln', 'max', 'min', 'tanh') and nx is not None and nx.kind == 'lp':
                t.kind = 'func'
            elif t.text in GREEK and not comp:
                def op_near(tok, j, step):
                    if tok is None or tok.kind != 'op':
                        return False
                    # "chi-square": a hyphen glued to a word is not an operator
                    k = j + step
                    return not (tok.text == '-' and 0 <= k < n and toks[k].kind == 'word')
                j1, j2 = sig_index(toks, i, -1), sig_index(toks, i, 1)
                if (j1 is not None and op_near(toks[j1], j1, -1)) or (j2 is not None and op_near(toks[j2], j2, 1)):
                    t.kind = 'greek'
        elif t.kind == 'op':
            if t.text == '-':
                left = toks[i - 1] if i > 0 else None
                if left is not None and nx is not None and left.kind != 'space' and nx.kind != 'space':
                    if left.kind == 'word' or nx.kind == 'word' or (left.kind == 'num' and nx.kind == 'num'):
                        t.kind = 'other'          # a hyphen ("base-8") or a range ("5-10")
            elif comp and t.text in ('*', '/', '+', '<', '>', '=', '~'):
                pass
        elif t.kind == 'numvar' and comp:
            t.kind = 'word'
        elif t.kind == 'hyph':
            t.kind = 'word' if (comp and t.text.isupper()) or t.text in ('e', 'I', 'a', 'A') else 'var'
        elif t.kind == 'ellipsis':
            t.kind = 'op' if (p is not None and p.kind in ('comma', 'var', 'math', 'num')) else 'other'
    return toks


PM = ('plus or minus', '+/-', '+-')
ARROWS = ('->', '=>', '<->', '\u2192')
COMPARE = ('<=', '>=', '<', '>', '!=', '\u2264', '\u2265', '\u2260')
MATHY = {'var', 'numvar', 'num', 'op', 'lp', 'rp', 'times', 'math', 'func', 'greek', 'comma', 'space'}
CORE = {'var', 'numvar', 'func', 'times', 'greek'}


def var_tex(text):
    if text in MWORDS:
        return text
    m2 = re.match(r'([A-Za-z]{2,4})_(?:\{([^{}]*)\}|([A-Za-z0-9]+))$', text)
    if m2:
        return r'\mathit{%s}_{%s}' % (m2.group(1), m2.group(2) or m2.group(3))
    m = re.match(r"([A-Za-z])(?:_\{([^{}]*)\}|_([A-Za-z0-9]+)|(\d{1,2}))?('*)$", text)
    base, sub = m.group(1), m.group(2) or m.group(3) or m.group(4)
    out = base
    if sub:
        out += '_{%s}' % sub if len(sub) > 1 else '_%s' % sub
    return out + m.group(5)


def tok_tex(t):
    k = t.kind
    if k == 'var':
        return var_tex(t.text)
    if k in ('num', 'numvar'):
        return t.text
    if k == 'greek':
        return '\\' + t.text
    if k == 'times':
        return r'\times'
    if k == 'math':
        return t.tex.strip()
    if k == 'op':
        return r'\dots' if t.text in ('...', '\u2026') else OPS[t.text]
    if k == 'func':
        if t.text in FUNCS:
            return FUNCS[t.text]
        return r'\operatorname{%s}' % t.text
    if k == 'comma':
        return ','
    if k == 'space':
        return ' '
    if k in ('lp', 'rp') and t.text in '{}':
        return OPS[t.text]
    return t.text


def matching(run, i):
    depth = 0
    for j in range(i, len(run)):
        if run[j].kind == 'lp':
            depth += 1
        elif run[j].kind == 'rp':
            depth -= 1
            if depth == 0:
                return j
    return len(run) - 1


def run_tex(run):
    """TeX for a run of math-like tokens: sqrt(...) -> \\sqrt{...},
    x^(...) -> x^{...}, x^2 -> x^{2}; words inside brackets become \\text{...}."""
    out = []
    i, n = 0, len(run)
    while i < n:
        t = run[i]
        if t.kind == 'func' and t.text == 'sqrt' and i + 1 < n and run[i + 1].kind == 'lp':
            j = matching(run, i + 1)
            out.append(r'\sqrt{' + run_tex(run[i + 2:j]).strip() + '}')
            i = j + 1
            continue
        if t.kind == 'op' and t.text == '^':
            j = i + 1
            if j < n and run[j].kind == 'lp':
                k = matching(run, j)
                out.append('^{' + run_tex(run[j + 1:k]).strip() + '}')
                i = k + 1
                continue
            if j < n and run[j].kind in ('num', 'var', 'numvar', 'greek'):
                out.append('^{' + tok_tex(run[j]) + '}')
                i = j + 1
                continue
            if j + 1 < n and run[j].kind == 'op' and run[j].text == '-' and run[j + 1].kind in ('num', 'var'):
                out.append('^{-' + tok_tex(run[j + 1]) + '}')
                i = j + 2
                continue
        if t.kind == 'word' and re.fullmatch(r'[A-Z]{2,3}', t.text):
            out.append(t.text)
            i += 1
            continue
        if t.kind in ('word', 'other'):
            j = i
            while j < n and run[j].kind in ('word', 'space', 'comma', 'other'):
                j += 1
            while j > i + 1 and run[j - 1].kind == 'space':
                j -= 1
            words = ''.join(tk.text for tk in run[i:j])
            k0 = i - 1
            while k0 >= 0 and run[k0].kind == 'space':
                k0 -= 1
            k1 = j
            while k1 < n and run[k1].kind == 'space':
                k1 += 1
            before = ' ' if k0 >= 0 and run[k0].kind != 'lp' else ''
            after = ' ' if k1 < n and run[k1].kind != 'rp' else ''
            words = words.replace('\\', r'\textbackslash{}').replace('{', r'\{').replace('}', r'\}')
            words = words.replace('%', r'\%').replace('&', r'\&').replace('#', r'\#')
            out.append(r'\text{%s%s%s}' % (before, words, after))
            i = j
            continue
        tx = tok_tex(t)
        if out and re.match(r'[A-Za-z]', tx) and re.search(r'\\[A-Za-z]+$', out[-1]):
            out.append(' ')
        out.append(tx)
        i += 1
    return re.sub(r'\s+', ' ', ''.join(out))


def func_extent(toks, i):
    """For a function token at i followed by a bracket, the index of the matching
    bracket if it closes within a short span (words inside are allowed)."""
    depth = 0
    j = i + 1
    while j < len(toks) and j - i < 40:
        k = toks[j].kind
        if k == 'lp':
            depth += 1
        elif k == 'rp':
            depth -= 1
            if depth == 0:
                return j
        elif k == 'dmath' or (k == 'other' and toks[j].text in '.;:!?'):
            return None
        j += 1
    return None


def depth_of(run):
    d = 0
    for tk in run:
        if tk.kind == 'lp':
            d += 1
        elif tk.kind == 'rp':
            d -= 1
            if d < 0:
                return -1
    return d


def needs_wrap(run, comp):
    kinds = [t.kind for t in run]
    sig_ = [t for t in run if t.kind != 'space']
    # a lone arrow, comparison or ellipsis between words: "Ready -> Waiting", "HM <= GM", ", ..."
    if len(sig_) == 1 and sig_[0].kind == 'op' and sig_[0].text in ARROWS + COMPARE + ('...', '\u2026'):
        return True
    if comp:
        return (any(t.kind == 'var' for t in run) or any(t.kind == 'op' and t.text in ('^',) + ARROWS for t in run))
    if any(k in CORE for k in kinds):
        return True
    # a set written with braces: {1, 2, 3}
    if sig_ and sig_[0].kind == 'lp' and sig_[0].text == '{' and sig_[-1].kind == 'rp' and sig_[-1].text == '}':
        return True
    if 'math' in kinds:
        # merge a formula with maths written next to it: "$a$ + 2", "mean plus or minus $2\sigma$", "(ABC) <= $x$"
        return any(t.kind == 'op' for t in sig_) and (
            any(t.kind == 'num' for t in sig_)
            or any(t.kind == 'op' and t.text in PM + ARROWS + COMPARE + ('...', '\u2026') for t in sig_))
    # a bound ("at least >= 5")
    if sig_ and sig_[0].kind == 'op' and sig_[0].text in COMPARE and len(sig_) >= 2 and all(
            t.kind in ('num', 'op', 'comma') for t in sig_):
        return True
    if any(t.kind == 'op' for t in sig_) and any(t.kind == 'num' for t in sig_):
        if len(sig_) == 2 and sig_[0].kind == 'op' and sig_[0].text in ('-', '\u2212', 'plus or minus', '+/-', '+-') and sig_[1].kind == 'num':
            return True                     # a negative number
        return sum(t.kind == 'num' for t in sig_) >= 2
    return False


def wrap_runs(toks, comp):
    out = []
    i, n = 0, len(toks)
    while i < n:
        t = toks[i]
        if t.kind not in MATHY or t.kind in ('space', 'comma'):
            out.append(t.text)
            i += 1
            continue
        j = i
        while j < n:
            k = toks[j].kind
            if k == 'func':
                end = func_extent(toks, j) if j + 1 < n and toks[j + 1].kind == 'lp' else None
                if end is None:
                    break
                j = end + 1
                continue
            if k in MATHY:
                j += 1
                continue
            break
        if j == i:                          # a function name without a closing bracket
            out.append(t.text)
            i += 1
            continue
        span = toks[i:j]
        # a closing bracket that belongs to the prose ends the run: "(layer $3/4$) -> ..."
        depth = 0
        for k, tk in enumerate(span):
            depth += (tk.kind == 'lp') - (tk.kind == 'rp')
            if depth < 0:
                if k > 0:
                    span = span[:k]
                    j = i + k
                break
        a, b = 0, len(span)

        def trim_end():
            nonlocal b
            while b > a and (span[b - 1].kind in ('space', 'comma', 'lp')
                             or (span[b - 1].kind == 'op' and span[b - 1].text not in ('...', '\u2026')
                                 and not (span[b - 1].text in ARROWS + COMPARE + ('...', '\u2026')
                                          and (b - 1 == a or any(tk.kind in ('math', 'var') for tk in span[a:b - 1]))))):
                b -= 1

        def trim_start():
            nonlocal a
            while a < b:
                tk = span[a]
                if tk.kind in ('space', 'comma', 'rp'):
                    a += 1
                elif tk.kind == 'op' and tk.text in ('plus or minus', '+/-', '+-'):
                    break
                elif tk.kind == 'op' and tk.text in ('-', '\u2212'):
                    # keep a minus glued to its operand ("-1"), drop a dash (" - ")
                    if a + 1 < b and span[a + 1].kind != 'space':
                        break
                    a += 1
                elif tk.kind == 'op' and (tk.text in ARROWS or tk.text in COMPARE):
                    break
                elif tk.kind == 'op' and tk.text not in ('...', '\u2026'):
                    a += 1
                else:
                    break
        trim_start()
        trim_end()
        # unmatched brackets at the edges belong to the prose: "(see $X$)"
        changed = True
        while changed and a < b:
            changed = False
            if depth_of(span[a:b]) != 0:
                if span[b - 1].kind == 'rp' and depth_of(span[a:b]) < 0:
                    b -= 1
                    trim_end()
                    changed = True
                elif span[a].kind == 'lp':
                    a += 1
                    trim_start()
                    changed = True
        run = span[a:b]
        out.extend(tk.text for tk in span[:a])
        if run and depth_of(run) == 0 and needs_wrap(run, comp):
            if all(tk.kind in ('math', 'space', 'comma') for tk in run):
                out.extend(tk.text for tk in run)
            else:
                out.append('$' + run_tex(run).strip() + '$')
        else:
            if run and depth_of(run) != 0 and needs_wrap(run, comp):
                UNBALANCED.append(''.join(tk.text for tk in run))
            out.extend(tk.text for tk in run)
        out.extend(tk.text for tk in span[b:])
        i = j
    return ''.join(out)


def latexify_prose(text, comp=False):
    return wrap_runs(classify(tokenize(split(text)), comp=comp), comp)


# ------------------------------------------------- rule-based repairs
_LIM = r'(?P<{0}>\$[^$]*\$|[^\s$]+)'
_TAIL = (r'(?:\$(?P<b>[^$=]*?)\s*=\s*(?P<rest>[^$]*)\$|\$(?P<b2>[^$]*)\$'
         r'|(?P<b3>[^\s$,;:]+?)(?=[\s,;:]|\.\s|\.$|$))')
EVAL_FROM_TO = re.compile(r'\$(?P<pre>[^$]*?)\[(?P<body>[^$\[\]]*)\]\$\s+from\s+' + _LIM.format('a') + r'\s+to\s+' + _TAIL)
INT_FROM_TO = re.compile(r'\$(?P<pre>[^$]*?)\\int(?![_^a-zA-Z])\s*(?P<body>[^$]*?)\$\s+from\s+' + _LIM.format('a') + r'\s+to\s+' + _TAIL)
INTEGRAL_WORDS = re.compile(r'(?:the\s+)?integral\s+(?:over\s+\S+\s+)?from\s+' + _LIM.format('a') + r'\s+to\s+'
                            + _LIM.format('b') + r'\s+of\s+\$(?P<body>[^$]*)\$')
INT_OVER = re.compile(r'\$(?P<pre>[^$]*?)\\int(?![_^a-zA-Z])\s*(?P<body>[^$]*?)\$\s+over\s+'
                      r'\$\((?P<a>[^,()$]+),\s*(?P<b>[^()$]+?)\)(?P<rest>\s*=[^$]*)?\$')
INTEGRAL_OVER_WORDS = re.compile(r'(?:the\s+)?integral\s+over\s+(?:\S+\s+in\s+)?\$\((?P<a>[^,()$]+),\s*(?P<b>[^()$]+?)\)\$'
                                 r'\s+of\s+\$(?P<body>[^$]*)\$')
SUM_WORDS = re.compile(r'(?:the\s+)?sum\s+(?:over|of\s+\S+\s+for)\s+\$(?P<a>[^$]*=[^$]*)\$\s+to\s+'
                       r'(?P<b>\$[^$]*\$|[^\s$,;:.]+)\s+of\s+\$(?P<body>[^$]*)\$')


def _lim(x):
    x = x.strip()
    if x.startswith('$') and x.endswith('$'):
        return x[1:-1].strip()
    return latexify_prose(x).strip('$').strip()


def _brace(x):
    x = _lim(x)
    return x if len(x) == 1 else '{%s}' % x


def _tail(m, pre, core):
    if m.group('b') is not None:
        return '$%s%s = %s$' % (pre, core(_brace(m.group('b'))), m.group('rest').strip())
    b = m.group('b2') if m.group('b2') is not None else m.group('b3')
    return '$%s%s$' % (pre, core(_brace(b)))


def fix_integrals(text):
    def eval_sub(m):
        a, body = _brace(m.group('a')), m.group('body').strip()
        return _tail(m, m.group('pre'), lambda b: r'\left[%s\right]_%s^%s' % (body, a, b))

    def int_sub(m):
        body = m.group('body').strip()
        if '\\int' in body or re.search(r'\]\s*$', body):
            return m.group(0)
        a = _brace(m.group('a'))
        return _tail(m, m.group('pre'), lambda b: r'\int_%s^%s %s' % (a, b, body))

    def words_sub(m):
        return r'$\int_%s^%s %s$' % (_brace(m.group('a')), _brace(m.group('b')), m.group('body').strip())

    def over_sub(m):
        body = m.group('body').strip()
        if '\\int' in body:
            return m.group(0)
        return r'$%s\int_{%s}^{%s} %s%s$' % (m.group('pre'), m.group('a').strip(), m.group('b').strip(), body,
                                            m.group('rest') or '')

    def over_words_sub(m):
        return r'$\int_{%s}^{%s} %s$' % (m.group('a').strip(), m.group('b').strip(), m.group('body').strip())

    def sum_sub(m):
        return r'$\sum_{%s}^%s %s$' % (m.group('a').strip(), _brace(m.group('b')), m.group('body').strip())

    prev = None
    while prev != text:
        prev = text
        text = EVAL_FROM_TO.sub(eval_sub, text)
        text = INT_FROM_TO.sub(int_sub, text)
        text = INTEGRAL_WORDS.sub(words_sub, text)
        text = SUM_WORDS.sub(sum_sub, text)
        text = INT_OVER.sub(over_sub, text)
        text = INTEGRAL_OVER_WORDS.sub(over_words_sub, text)
    return text


ACRONYM_ONLY = re.compile(r"^[\w\s()/.,'-]*$")


def fix_segments(text, comp):
    """Repairs inside and at the edges of existing $...$ segments."""
    out = []
    quotes_open = False
    for s in split(text):
        if s[0] == 't':
            out.append(s)
            if len(re.findall(r"(?<![A-Za-z0-9])'|'(?![A-Za-z0-9])", s[1])) % 2 == 1:
                quotes_open = not quotes_open
            continue
        tex, disp = s[1], s[2]
        # a closing quotation mark swallowed by the formula: 'z goes with $n-3'$
        after = ''
        if quotes_open and tex.endswith("'") and not tex.endswith("''"):
            tex, after = tex[:-1], "'"
            quotes_open = False
        # an article swallowed at the end: "... = 1, a$ valid density"
        m = re.fullmatch(r'([\s\S]*?),\s*(a|an)\s*', tex)
        if m and m.group(1).strip():
            tex, after = m.group(1), ', ' + m.group(2) + after
        # question citations typeset as maths: $2018 Q_{35}$ -> 2018-Q35
        m = re.fullmatch(r'\s*((?:19|20)\d\d)\s*Q_\{?(\d+)\}?\s*', tex)
        if m:
            out.append(('t', '%s-Q%02d' % (m.group(1), int(m.group(2))) + after))
            continue
        # acronyms, codes or years wrapped as maths: $(I/O)$, $3 (MP3)$, $(2021)$
        plain = re.sub(r'\\text\{([^{}]*)\}', r'\1', tex)
        if (ACRONYM_ONLY.match(plain) and not re.search(r'[=<>+^_\\]', tex)
                and (re.search(r'[A-Z]{2,}|[A-Z]/[A-Z]', plain)
                     or re.fullmatch(r'\s*\(?\s*(?:19|20)\d\d(?:\s*,\s*(?:19|20)\d\d)*\s*\)?\s*', plain)
                     or (after and re.fullmatch(r'\s*\d+\s*', plain)))):
            out.append(('t', plain + after))
            continue
        # the word "partial" once turned into the symbol
        if tex.strip() == r'\partial':
            out.append(('t', 'partial' + after))
            continue
        # question references: $Q_{78}$ -> Q78
        m = re.fullmatch(r'\s*Q_\{?(\d{2,})\}?\s*', tex)
        if m:
            out.append(('t', 'Q' + m.group(1) + after))
            continue
        tex = re.sub(r'_\{(\d+)\}\.(\d)', r'_{\1.\2}', tex)
        tex = re.sub(r'(?<![A-Za-z\\])inf(?![A-Za-z])', r'\\infty', tex)
        tex = re.sub(r'\\inf(?![A-Za-z_])', r'\\infty', tex)
        tex = re.sub(r'(\d)\s*sqrt\s*(\d+)', r'\1\\sqrt{\2}', tex)
        tex = re.sub(r'(?<![A-Za-z\\{])(BVN|BN)\(', r'\\operatorname{\1}(', tex)
        if comp:
            tex = re.sub(r'\((?=[0-9A-F.]*[A-F])([0-9A-F.]+)\)', r'(\\mathrm{\1})', tex)
        out.append(('m', tex, disp))
        if after:
            out.append(('t', after))
    return join(out)


def stage_rules(text, comp):
    # "$r_{12}$.3" -> "$r_{12.3}$"; shared-stem ranges "$Q_1$–$Q_3$" -> "Q1–Q3"
    text = re.sub(r'_\{(\d+)\}\$\.(\d)(?!\d)', r'_{\1.\2}$', text)
    text = re.sub(r'\$Q_\{?(\d+)\}?\$(\s*[\u2013-]\s*)\$?Q_?\{?(\d+)\}?\$?', r'Q\1\2Q\3', text)
    text = fix_integrals(text)
    # "$A$ = the $\int ...$" -> "$A = \int ...$"
    text = re.sub(r'\$([^$]+)\$\s*=\s*the\s+\$(\\(?:int|sum)[^$]*)\$', r'$\1 = \2$', text)
    text = fix_segments(text, comp)
    text = re.sub(r'\bA \$?n B\$?(?![A-Za-z])', r'$A \\cap B$', text)     # "A n B" for the intersection
    return text


def stage_prose(text, comp):
    return latexify_prose(text, comp)


# ------------------------------------------------------------ dashboard I/O
def load(html):
    out = {}
    for name in ('quizData', 'forecastData'):
        start = html.index(f'window.{name} = [\n') + len(f'window.{name} = [\n')
        end = html.index('\n];', start)
        out[name] = (start, end, [json.loads(l.rstrip(',')) for l in html[start:end].split('\n')])
    i = html.index('window.quizMeta = ') + len('window.quizMeta = ')
    j = html.index('\n};', i) + 2
    out['quizMeta'] = (i, j, json.loads(html[i:j]))
    return out


def dump(html, data):
    for name, (start, end, obj) in sorted(data.items(), key=lambda kv: -kv[1][0]):
        if name == 'quizMeta':
            text = json.dumps(obj, ensure_ascii=False, indent=1)
        else:
            text = ',\n'.join(json.dumps(o, ensure_ascii=False, separators=(',', ':')) for o in obj)
        html = html[:start] + text + html[end:]
    return html


def text_slots(q):
    """(label, container, key) for every rendered text field of a question."""
    slots = [('question', q, 'question'), ('sharedStem', q, 'sharedStem'), ('examShortcut', q, 'examShortcut')]
    slots += [(f'options[{i}]', q['options'], i) for i in range(len(q.get('options') or []))]
    slots += [(f'tipsTricks[{i}]', q['tipsTricks'], i) for i in range(len(q.get('tipsTricks') or []))]
    slots += [(f'solution[{i}]', s, 'text') for i, s in enumerate(q.get('solution') or [])]
    return [(lab, c, k) for lab, c, k in slots if isinstance(c[k], str) and c[k]]


def apply_fixes(q, fixes, log):
    """Hand corrections: (old, new) replacements anywhere in the item's text."""
    for old, new in fixes:
        hit = False
        for lab, c, k in text_slots(q):
            if old in c[k]:
                c[k] = c[k].replace(old, new)
                hit = True
        if not hit and not any(new in c[k] for lab, c, k in text_slots(q)):
            log.append((q['id'], old))


def main(argv):
    import latex_fixes
    target = Path(argv[argv.index('--target') + 1]) if '--target' in argv else TARGET
    html = target.read_text(encoding='utf-8')
    data = load(html)
    changes, missed = [], []
    for name in ('quizData', 'forecastData'):
        for q in data[name][2]:
            before = {lab: c[k] for lab, c, k in text_slots(q)}
            apply_fixes(q, latex_fixes.FIXES.get(q['id'], []), missed)
            comp = str(q.get('unit', '')).startswith('Computer') or q['id'] in latex_fixes.COMPUTER_STYLE
            for lab, c, k in text_slots(q):
                new = c[k]
                if q['id'] not in latex_fixes.NO_AUTO:
                    for _ in range(4):            # later rules can enable earlier ones
                        prev, new = new, stage_prose(stage_rules(new, comp), comp)
                        if new == prev:
                            break
                c[k] = new
                if new != before.get(lab):
                    changes.append((q['id'], lab, before.get(lab), new))
    intel = data['quizMeta'][2]['topicIntel']
    first_run = any(intel[c][k] != v[k] for c, v in latex_fixes.TOPIC_NOTES.items() for k in ('pattern', 'mustKnow'))
    if not first_run:
        missed = []                  # on a re-run the hand fixes are already in place
    for code, notes in latex_fixes.TOPIC_NOTES.items():
        for key in ('pattern', 'mustKnow'):
            if intel[code][key] != notes[key]:
                changes.append((f'intel:{code}', key, intel[code][key], notes[key]))
                intel[code][key] = notes[key]
    if '--report' in argv:
        out = Path(argv[argv.index('--report') + 1])
        out.write_text('\n'.join(f'{i}\t{lab}\n  - {o}\n  + {n}' for i, lab, o, n in changes), encoding='utf-8')
        print(f'{len(changes)} field(s) would change; report in {out}')
    else:
        target.write_text(dump(html, data), encoding='utf-8')
        print(f'{len(changes)} field(s) changed')
    for i, old in missed:
        print(f'note: fix for {i} not applied (text not found): {old[:60]!r}')
    for u in sorted(set(UNBALANCED)):
        print(f'unbalanced (left as text): {u[:90]!r}')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--try':
        for s in sys.argv[2:]:
            print(stage_prose(stage_rules(s, False), False))
    else:
        main(sys.argv[1:])
