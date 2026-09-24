"""Add the Gupta & Kapoor Ch 5-8 bank to the main offline dashboard.

    python3 verify.py && python3 integrate.py

Patches ../UPSC-ISS-Statistics-Dashboard-STANDALONE.html in place, adding a
"Gupta Kapoor" tab (chapter tabs, then one tab per subtopic) next to the PYQ
features.  Safe to re-run: the data block and the two code blocks are replaced
between their markers, and each small patch to the existing app code is applied
only once.

What goes in:
  * window.gkMeta / window.gkData  - the problem bank (bank/ch*.txt) converted to
    the dashboard's question schema, plus the key-result sheets (formulas.py).
  * dashboard/gk.css, dashboard/gk.js - the tab itself.
  * a handful of small hooks into the existing app (see PATCHES).

The bank is authored with the key mostly in position A; here each item's options
are permuted deterministically so the keys spread evenly over (a)-(d), and any
"Option X" reference in the text is rewritten to the new label.
"""
import json
import random
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

import bankparse
from formulas import SECTIONS

HERE = Path(__file__).parent
TARGET = HERE.parent / 'UPSC-ISS-Statistics-Dashboard-STANDALONE.html'
SOURCE = "S.C. Gupta & V.K. Kapoor, Fundamentals of Mathematical Statistics, Chapters 5–8"
OPTION_REF = re.compile(r'\b([Oo]ption) ([A-D])\b')
MATH_RE = re.compile(r'\$\$(.+?)\$\$|\$(.+?)\$', re.S)

CHAPTER_SHORT = {
    5: 'Random variables',
    6: 'Expectation & generating functions',
    7: 'Discrete distributions',
    8: 'Continuous distributions',
}

# syllabus lines (README) quoted on each subtopic tab
SYL = {
    'rv': 'Discrete and continuous random variables. Distribution functions and their properties.',
    'loc': 'Measures of location, dispersion, skewness and kurtosis.',
    'joint': 'Random vectors, Joint and marginal distributions, conditional distributions.',
    'fun': 'Distributions of functions of random variables.',
    'exp': 'Mathematical expectation and conditional expectation.',
    'gf': 'Characteristic function, moment and probability generating functions, Inversion, '
          'uniqueness and continuity theorems.',
    'ineq': "Tchebycheff's and Kolmogorov's inequalities.",
    'conv': 'Modes of convergences of sequences of random variables - in distribution, in '
            'probability, with probability one and in mean square.',
    'lln': "Borel 0-1 law, Kolmogorov's 0-1 law. Laws of large numbers and central limit "
           'theorems for independent variables.',
    'disc': 'Standard discrete and continuous probability distributions - Bernoulli, Uniform, '
            'Binomial, Poisson, Geometric, Hyper geometric, Multinomial, Negative binomial.',
    'cont': 'Standard discrete and continuous probability distributions - Rectangular, '
            'Exponential, Normal, Cauchy, Laplace, Beta, Gamma, Lognormal.',
    'clt': 'Laws of large numbers and central limit theorems for independent variables.',
    'skew': 'Measures of location, dispersion, skewness and kurtosis.',
    'ord': 'Order statistics-minimum, maximum, range and median.',
}

P3 = ('Probability', 'P3', 'Random Variables & Distribution Functions')
P4 = ('Probability', 'P4', 'Standard Discrete Distributions')
P5 = ('Probability', 'P5', 'Standard Continuous Distributions')
P6 = ('Probability', 'P6', 'Random Vectors: Joint, Marginal & Conditional Distributions')
P7 = ('Probability', 'P7', 'Distributions of Functions of Random Variables')
P8 = ('Probability', 'P8', 'Mathematical Expectation & Conditional Expectation')
P9 = ('Probability', 'P9', 'Characteristic Function, MGF & PGF; Inversion, Uniqueness, Continuity')
P10 = ('Probability', 'P10', 'Modes of Convergence of Sequences of Random Variables')
P12 = ('Probability', 'P12', "Tchebycheff's & Kolmogorov's Inequalities")
P13 = ('Probability', 'P13', 'Laws of Large Numbers & Central Limit Theorems')
S2 = ('Statistical Methods', 'S2', 'Measures of Location & Dispersion')
S3 = ('Statistical Methods', 'S3', 'Skewness & Kurtosis (Moments)')
S13 = ('Statistical Methods', 'S13', 'Order Statistics - Minimum, Maximum, Range, Median')

# Gupta-Kapoor subtopic -> (PYQ unit/topic, PYQ subtopic, related-PYQ topic codes,
#                          related-PYQ subtopics, syllabus line)
TOPIC_MAP = {
    '5A': (P3, 'Distribution Functions & Their Properties', [], ['Distribution Functions & Their Properties'], 'rv'),
    '5B': (P3, 'Discrete & Continuous Random Variables', [], ['Discrete & Continuous Random Variables'], 'rv'),
    '5C': (P3, 'Discrete & Continuous Random Variables', [], ['Discrete & Continuous Random Variables'], 'rv'),
    '5D': (S2, 'Measures of Location', ['S2', 'S3'], [], 'loc'),
    '5E': (P6, 'Random Vectors & Joint Distributions', ['P6'], [], 'joint'),
    '5F': (P6, 'Random Vectors & Joint Distributions', ['P6'], [], 'joint'),
    '5G': (P7, 'Distributions of Functions of Random Variables', ['P7'], ['Distributions of Functions of Random Variables'], 'fun'),
    '5H': (P7, 'Distributions of Functions of Random Variables', ['P7'], ['Distributions of Functions of Random Variables'], 'fun'),
    '6A': (P8, 'Mathematical Expectation', [], ['Mathematical Expectation'], 'exp'),
    '6B': (P8, 'Mathematical Expectation', [], ['Mathematical Expectation'], 'exp'),
    '6C': (P8, 'Mathematical Expectation', [], ['Mathematical Expectation'], 'exp'),
    '6D': (P8, 'Conditional Expectation', [], ['Conditional Expectation'], 'exp'),
    '6E': (P9, 'Moment Generating Function', [], ['Moment Generating Function'], 'gf'),
    '6F': (P9, 'Moment Generating Function', [], ['Moment Generating Function'], 'gf'),
    '6G': (P9, 'Characteristic Function', [], ['Characteristic Function'], 'gf'),
    '6H': (P9, 'Probability Generating Function', [], ['Probability Generating Function'], 'gf'),
    '6I': (P12, "Tchebycheff's Inequality", ['P12'], ["Tchebycheff's Inequality"], 'ineq'),
    '6J': (P10, 'Modes of Convergence', ['P10'], ['Modes of Convergence'], 'conv'),
    '6K': (P13, 'Laws of Large Numbers', ['P11'], ['Laws of Large Numbers', 'Borel & Kolmogorov 0-1 Laws'], 'lln'),
    '7A': (P4, 'Binomial Distribution', [], ['Binomial Distribution'], 'disc'),
    '7B': (P4, 'Binomial Distribution', [], ['Binomial Distribution'], 'disc'),
    '7C': (P4, 'Poisson Distribution', [], ['Poisson Distribution'], 'disc'),
    '7D': (P4, 'Poisson Distribution', [], ['Poisson Distribution'], 'disc'),
    '7E': (P4, 'Negative Binomial Distribution', [], ['Negative Binomial Distribution'], 'disc'),
    '7F': (P4, 'Geometric Distribution', [], ['Geometric Distribution'], 'disc'),
    '7G': (P4, 'Standard Discrete Distributions', [], ['Standard Discrete Distributions'], 'disc'),
    '7H': (P4, 'Standard Discrete Distributions', [], ['Standard Discrete Distributions'], 'disc'),
    '7I': (P4, 'Standard Discrete Distributions', [], ['Standard Discrete Distributions', 'Probability Generating Function'], 'disc'),
    '8A': (P5, 'Uniform / Rectangular Distribution', [], ['Uniform / Rectangular Distribution'], 'cont'),
    '8B': (P5, 'Normal Distribution', [], ['Normal Distribution'], 'cont'),
    '8C': (P5, 'Normal Distribution', [], ['Normal Distribution'], 'cont'),
    '8D': (P5, 'Gamma Distribution', [], ['Gamma Distribution', 'Chi-square Distribution'], 'cont'),
    '8E': (P5, 'Beta Distribution', [], ['Beta Distribution'], 'cont'),
    '8F': (P5, 'Exponential Distribution', [], ['Exponential Distribution'], 'cont'),
    '8G': (P5, 'Cauchy Distribution', [], ['Cauchy Distribution', 'Laplace Distribution'], 'cont'),
    '8H': (P13, 'Central Limit Theorem', ['P13'], ['Central Limit Theorem'], 'clt'),
    '8I': (P5, 'Standard Continuous Distributions', [], ['Standard Continuous Distributions'], 'cont'),
    '8J': (S3, 'Skewness', ['S3'], [], 'skew'),
    '8K': (S13, 'Order Statistics - Minimum, Maximum & Median', ['S13'], ['Order Statistics - Minimum, Maximum & Median'], 'ord'),
}

QTYPE = {'Numerical': 'Numerical', 'Conceptual': 'Conceptual', 'Statement': 'Statement-based'}


class IntegrateError(Exception):
    pass


# ----------------------------------------------------------------- text helpers
def md(text):
    """Author markup -> the dashboard's markdown-lite (it escapes all HTML)."""
    out = re.sub(r'<b>(.*?)</b>', r'**\1**', text)
    out = re.sub(r'<i>(.*?)</i>', r'*\1*', out)
    if re.search(r'</?[a-z]+\s*/?>', MATH_RE.sub(' ', out)):
        raise IntegrateError(f'unconverted HTML in {text[:80]!r}')
    return out


def split_question(q, where):
    """'stem<br>1. ...<br>2. ...<br>Which are correct?' -> stem, [statements], ask."""
    parts = re.split(r'<br\s*/?>', q)
    if len(parts) == 1:
        return q, [], ''
    stem, stmts, ask = parts[0].strip(), [], ''
    for i, part in enumerate(parts[1:], 1):
        m = re.match(r'\s*(\d+)\.\s+(.*)$', part, re.S)
        if m and not ask:
            if int(m.group(1)) != len(stmts) + 1:
                raise IntegrateError(f'{where}: statements not numbered 1, 2, 3, ...')
            stmts.append(m.group(2).strip())
        elif i == len(parts) - 1 and stmts:
            ask = part.strip()
        else:
            raise IntegrateError(f'{where}: unexpected <br> layout in the question')
    return stem, stmts, ask


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
        it['tips'] = [fix(t) for t in it['tips']]


# ------------------------------------------------------------- sheets -> blocks
class SheetParser(HTMLParser):
    """Turn a formulas.py card (trusted HTML) into p / ul / table blocks whose
    cells are markdown-lite + $math$ strings for the dashboard's renderer."""

    def __init__(self, maths):
        super().__init__(convert_charrefs=True)
        self.maths = maths
        self.blocks = []
        self.buf = None
        self.table = None
        self.row = None
        self.in_head = False
        self.lst = None

    def unmask(self, s):
        s = re.sub(r'\x00(\d+)\x00', lambda m: self.maths[int(m.group(1))], s)
        return re.sub(r'\s+', ' ', s).strip()

    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'li', 'td', 'th'):
            self.buf = ''
        elif tag == 'b':
            self.buf = (self.buf or '') + '**'
        elif tag == 'i':
            self.buf = (self.buf or '') + '*'
        elif tag == 'br':
            self.buf = (self.buf or '') + ' '
        elif tag in ('ul', 'ol'):
            self.lst = []
        elif tag == 'table':
            self.table = {'t': 'table', 'head': [], 'rows': []}
        elif tag == 'thead':
            self.in_head = True
        elif tag == 'tbody':
            self.in_head = False
        elif tag == 'tr':
            self.row = []
        else:
            raise IntegrateError(f'sheet: unsupported tag <{tag}>')

    def handle_endtag(self, tag):
        if tag == 'p':
            self.blocks.append({'t': 'p', 'text': self.unmask(self.buf)})
            self.buf = None
        elif tag == 'li':
            self.lst.append(self.unmask(self.buf))
            self.buf = None
        elif tag in ('ul', 'ol'):
            self.blocks.append({'t': 'ul', 'items': self.lst})
            self.lst = None
        elif tag in ('td', 'th'):
            self.row.append(self.unmask(self.buf))
            self.buf = None
        elif tag == 'tr':
            (self.table['head'].extend if self.in_head else self.table['rows'].append)(self.row)
            self.row = None
        elif tag == 'table':
            self.blocks.append(self.table)
            self.table = None
        elif tag == 'b':
            self.buf += '**'
        elif tag == 'i':
            self.buf += '*'

    def handle_data(self, data):
        if self.buf is not None:
            self.buf += data
        elif data.strip():
            raise IntegrateError(f'sheet: text outside a block: {data.strip()[:60]!r}')


def sheet_blocks(html):
    maths = []

    def mask(m):
        maths.append(m.group(0))
        return f'\x00{len(maths) - 1}\x00'
    p = SheetParser(maths)
    p.feed(MATH_RE.sub(mask, html))
    p.close()
    return p.blocks


# ------------------------------------------------------------------ data build
def build():
    chapters = bankparse.load_all(HERE / 'bank')
    items, chs, n_verified = [], [], 0
    gid = 200000
    for ch in chapters:
        verified = {it['id']: bool(it['_chk']) for it in ch['items']}
        permute_options(ch)
        counts = Counter(it['topic'] for it in ch['items'])
        topics = []
        for t in ch['topics']:
            if t['code'] not in TOPIC_MAP:
                raise IntegrateError(f'no syllabus mapping for subtopic {t["code"]}')
            (unit, code, ptopic), sub, rel_codes, rel_subs, syl = TOPIC_MAP[t['code']]
            topics.append({
                'code': t['code'], 'title': t['title'], 'ch': ch['num'], 'n': counts[t['code']],
                'unit': unit, 'topicCode': code, 'pyqTopic': ptopic, 'subtopic': sub,
                'relCodes': rel_codes, 'relSubs': rel_subs, 'syllabus': SYL[syl],
            })
        tmeta = {t['code']: t for t in topics}
        chs.append({'num': ch['num'], 'title': ch['title'], 'short': CHAPTER_SHORT[ch['num']],
                    'n': len(ch['items']), 'topics': topics})
        for n, it in enumerate(ch['items'], 1):
            where = it['_where']
            tm = tmeta[it['topic']]
            stem, stmts, ask = split_question(it['q'], where)
            tips = ([f'**Trap:** {md(it["tr"])}'] if it['tr'] else []) + [md(t) for t in it['tips']]
            gid += 1
            n_verified += verified[it['id']]
            items.append({
                'id': f'GK-{it["id"]}',
                'globalId': gid,
                'isGK': True,
                'provenance': 'GUPTA & KAPOOR TEXTBOOK BANK',
                'year': 'G&K',
                'questionNumber': n,
                'unit': tm['unit'], 'topicCode': tm['topicCode'], 'topic': tm['pyqTopic'],
                'subtopic': tm['subtopic'],
                'form': 'MSA' if stmts else 'PLAIN',
                'sharedStem': '',
                'question': md(stem), 'stmts': [md(s) for s in stmts], 'ask': md(ask),
                'options': [md(o) for o in it['opts']],
                'correctAnswer': it['ans'],
                'questionType': QTYPE[it['type']],
                'answerConfidence': 'high',
                'sourceIssue': '',
                'examShortcut': md(it['sc']),
                'tipsTricks': tips,
                'solution': [{'step': i + 1, 'text': md(s)} for i, s in enumerate(it['steps'])],
                'gkChapter': ch['num'], 'gkTopic': it['topic'], 'gkTopicTitle': tm['title'],
                'gkTopicLabel': f'{it["topic"]} {tm["title"]}',
                'gkSection': it['sec'], 'gkPage': it['page'],
                'difficultyLevel': it['diff'], 'difficulty': bankparse.DIFF_NAMES[it['diff']],
                'gkVerified': verified[it['id']],
            })
    sheets = [{'ch': s['ch'], 'title': s['title'], 'blocks': sheet_blocks(s['html'])} for s in SECTIONS]
    meta = {
        'label': 'GUPTA & KAPOOR TEXTBOOK BANK',
        'source': SOURCE,
        'total': len(items),
        'nTopics': sum(len(c['topics']) for c in chs),
        'nVerified': n_verified,
        'provenance': (
            f'Every problem here was written for this dashboard from {SOURCE}, in the style of the '
            'ISS objective paper, to cover the theorems, remarks, results and formulas the paper '
            'draws on. None is a previous-year question, and none enters a year, sectional, topic, '
            f'subtopic or custom PYQ mock. {n_verified} answer keys are confirmed by exact or '
            'numerical computation (sympy / scipy); the conceptual and statement items are checked '
            "by hand against the book's theorems."),
        'chapters': chs,
        'sheets': sheets,
    }
    return meta, items


def data_script(meta, items):
    def js(obj):
        return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    lines = ['<script id="gk-data">',
             '/* Gupta & Kapoor Ch 5-8 textbook problem bank - generated by',
             ' * ch5-8-dashboard-src/integrate.py from bank/ch*.txt; do not edit by hand. */',
             'window.gkMeta = ' + js(meta) + ';',
             'window.gkData = [']
    lines += [js(it) + (',' if i < len(items) - 1 else '') for i, it in enumerate(items)]
    lines += ['];', '</script>']
    return '\n'.join(lines) + '\n'


# ------------------------------------------------------------------ app patches
Q_OLD = "'<div class=\"qtext\">' + R(q.question) + '</div>'"
Q_NEW = "'<div class=\"qtext\">' + qBody(q) + '</div>'"
S_OLD = "'<div class=\"small\">' + R(q.question) + '</div>'"
S_NEW = "'<div class=\"small\">' + qBody(q) + '</div>'"

PATCHES = [
    # top bar
    ('<small>2018–2026 PYQ · 2027 Forecast Bank · 100% offline</small>',
     '<small>2018–2026 PYQ · 2027 Forecast Bank · Gupta Kapoor Ch 5–8 · 100% offline</small>'),
    ('    <button type="button" data-act="go" data-r="search" title="Search (S)">Search</button>',
     '    <button type="button" data-act="go" data-r="gk" title="Gupta Kapoor Ch 5–8 problem bank">Gupta Kapoor</button>\n'
     '    <button type="button" data-act="go" data-r="search" title="Search (S)">Search</button>'),
    # data wiring
    ('var ALL = DATA.concat(FDATA);',
     'var GDATA = window.gkData || [];          /* GUPTA & KAPOOR Ch 5-8 textbook bank */\n'
     'var GMETA = window.gkMeta || null;\n'
     'var ALL = DATA.concat(FDATA, GDATA);'),
    ("  return (q.id + ' ' + (q.isForecast ? 'forecast 2027' : q.year) + ' ' + q.unit + ' ' +",
     "  return (q.id + ' ' + (q.isForecast ? 'forecast 2027' : q.isGK ? 'gupta kapoor chapter ' +\n"
     "          q.gkChapter + ' ' + q.gkTopicLabel + ' ' + q.gkSection + ' ' + q.difficulty : q.year) + ' ' + q.unit + ' ' +"),
    ("          ML.strip(q.sharedStem) + ' ' + ML.strip(q.question) + ' ' +",
     "          ML.strip(q.sharedStem) + ' ' + ML.strip(q.question) + ' ' +\n"
     "          (q.stmts || []).map(ML.strip).join(' ') + ' ' + ML.strip(q.ask) + ' ' +"),
    # provenance, meta line, reveal order
    ("  return q.isForecast ? '<span class=\"fc-badge\">FORECAST &middot; AI-generated</span>'",
     "  if (q.isGK) return '<span class=\"gk-badge\">GUPTA KAPOOR &middot; Ch ' + q.gkChapter + ' &middot; not PYQ</span>';\n"
     "  return q.isForecast ? '<span class=\"fc-badge\">FORECAST &middot; AI-generated</span>'"),
    ("    '</span><span>' + E(q.questionType) + '</span></div>';",
     "    '</span><span>' + E(q.questionType) + '</span>' +\n"
     "    (q.isGK ? '<span>' + E(q.gkTopicLabel) + '</span><span>\\u00a7' + E(q.gkSection) + '</span>' : '') + '</div>';"),
    ('function revealPanes(q, chosenOriginal, opts) {\n  opts = opts || {};',
     'function revealPanes(q, chosenOriginal, opts) {\n  opts = opts || {};\n'
     '  if (q.isGK) return gkRevealPanes(q, chosenOriginal, opts);'),
    # home
    ("  h += '<h2 class=\"mt\">Review &amp; track</h2><div class=\"grid g3\">';",
     "  h += gkHomeSection();\n\n"
     "  h += '<h2 class=\"mt\">Review &amp; track</h2><div class=\"grid g3\">';"),
    # result breakdown
    ("  h += breakdownCard(r.perQ, 'questionType', 'Performance by question type');",
     "  h += breakdownCard(r.perQ, 'questionType', 'Performance by question type');\n"
     "  if (S.kind === 'gk') h += breakdownCard(r.perQ, 'gkTopicLabel', 'Performance by Gupta Kapoor subtopic');"),
    ("(field === 'unit' ? 'Unit' : field === 'topic' ? 'Topic' : 'Type')",
     "(field === 'unit' ? 'Unit' : field === 'topic' ? 'Topic' : field === 'gkTopicLabel' ? 'Subtopic' : 'Type')"),
    # study card source line
    ("  h += '<div class=\"tiny muted mb\">Source: ' + E(q.sourceFile) + ' \\u00b7 original question number ' +",
     "  if (q.isGK) h += '<div class=\"tiny muted mb\">Source: ' + gkSourceLine(q) + '.</div>';\n"
     "  else h += '<div class=\"tiny muted mb\">Source: ' + E(q.sourceFile) + ' \\u00b7 original question number ' +"),
    # bookmarks filter indexed the wrong array (forecast bookmarks broke the filter)
    ('    var idx = DATA.indexOf(q);\n    if (qq && SEARCH_INDEX[idx].indexOf(qq) < 0) return;',
     '    var idx = ALL.indexOf(q);\n    if (qq && SEARCH_INDEX[idx].indexOf(qq) < 0) return;'),
    # search
    ("    'question id across all ' + META.totalQuestions + ' authentic PYQs' +",
     "    'question id across all ' + META.totalQuestions + ' authentic PYQs' +\n"
     "    (GMETA ? ', the ' + GMETA.total + ' Gupta Kapoor textbook problems' : '') +"),
    ("        '>Forecast (AI-generated) only</option></select></label>';",
     "        '>Forecast (AI-generated) only</option>' +\n"
     "      (GMETA ? '<option value=\"gk\"' + (SEARCH.bank === 'gk' ? ' selected' : '') +\n"
     "        '>Gupta Kapoor (Ch 5\\u20138) only</option>' : '') + '</select></label>';"),
    ("    if (SEARCH.bank === 'pyq' && q.isForecast) continue;\n    if (SEARCH.bank === 'fc' && !q.isForecast) continue;",
     "    if (SEARCH.bank === 'pyq' && (q.isForecast || q.isGK)) continue;\n"
     "    if (SEARCH.bank === 'fc' && !q.isForecast) continue;\n"
     "    if (SEARCH.bank === 'gk' && !q.isGK) continue;"),
    ("      (q.isForecast ? '<span class=\"fc-badge\">FORECAST</span>' : '') +",
     "      (q.isForecast ? '<span class=\"fc-badge\">FORECAST</span>' : '') +\n"
     "      (q.isGK ? '<span class=\"gk-badge\">GUPTA KAPOOR</span>' : '') +"),
    # audit
    ("  var flagged = DATA.filter(function (q) { return q.sourceIssue; });",
     "  if (GMETA) {\n"
     "    h += '<div class=\"card\"><h3>Gupta Kapoor textbook bank</h3><p class=\"small\">' + GK_AUDIT.total +\n"
     "      ' problems, kept apart from the PYQs above \\u00b7 ' + (GK_AUDIT.ok ? 'all structural checks passed'\n"
     "      : GK_AUDIT.errors.length + ' error(s)') + '.</p>' + (GK_AUDIT.errors.length ? '<ul class=\"small\">' +\n"
     "      GK_AUDIT.errors.slice(0, 50).map(function (e) { return '<li>' + E(e) + '</li>'; }).join('') + '</ul>' : '') +\n"
     "      '</div>';\n"
     "  }\n\n"
     "  var flagged = DATA.filter(function (q) { return q.sourceIssue; });"),
    # clicks
    ("  switch (act) {\n    case 'go':",
     "  if (gkClick(act, t)) return;\n  switch (act) {\n    case 'go':"),
    # console hook
    ('    mathErrors: ML.mathErrors,',
     '    mathErrors: ML.mathErrors,\n    gk: { total: GDATA.length, audit: GK_AUDIT },'),
]

CSS_BEGIN, CSS_END = '/* GK-CSS-BEGIN */', '/* GK-CSS-END */'
JS_BEGIN, JS_END = '/* GK-JS-BEGIN */', '/* GK-JS-END */'
CSS_ANCHOR = '</style>\n<!--KATEX-BUNDLE-START-->'
JS_ANCHOR = ('/* ======================================================================\n'
             '   9.  RENDER + EVENTS')
APP_ANCHOR = ('<script>\n/* ==========================================================================\n'
              '   UPSC ISS Statistics Paper-I — Offline Mock Engine')


def put_block(html, begin, end, body, anchor):
    block = f'{begin}\n{body.rstrip()}\n{end}\n'
    if begin in html:
        a = html.index(begin)
        b = html.index(end, a) + len(end) + 1
        return html[:a] + block + html[b:]
    if html.count(anchor) != 1:
        raise IntegrateError(f'anchor not found exactly once: {anchor[:50]!r}')
    return html.replace(anchor, block + anchor)


def apply_patches(html):
    for old, new in PATCHES:
        if new in html:
            continue
        if html.count(old) != 1:
            raise IntegrateError(f'patch anchor found {html.count(old)} times: {old[:70]!r}')
        html = html.replace(old, new)
    for old, new, n in ((Q_OLD, Q_NEW, 3), (S_OLD, S_NEW, 4)):
        found = html.count(old)
        if found and found != n:
            raise IntegrateError(f'expected {n} of {old!r}, found {found}')
        html = html.replace(old, new)
        if html.count(new) < n:
            raise IntegrateError(f'expected at least {n} of {new!r} after patching')
    return html


def main():
    meta, items = build()
    html = TARGET.read_text(encoding='utf-8')
    # data block (replaced wholesale on every run)
    ds = data_script(meta, items)
    m = re.search(r'<script id="gk-data">.*?</script>\n', html, re.S)
    if m:
        html = html[:m.start()] + ds + html[m.end():]
    else:
        if html.count(APP_ANCHOR) != 1:
            raise IntegrateError('app script anchor not found')
        html = html.replace(APP_ANCHOR, ds + APP_ANCHOR)
    html = put_block(html, CSS_BEGIN, CSS_END, (HERE / 'dashboard' / 'gk.css').read_text(encoding='utf-8'), CSS_ANCHOR)
    html = put_block(html, JS_BEGIN, JS_END, (HERE / 'dashboard' / 'gk.js').read_text(encoding='utf-8'), JS_ANCHOR)
    html = apply_patches(html)
    TARGET.write_text(html, encoding='utf-8')
    keys = Counter('abcd'[it['correctAnswer']] for it in items)
    print(f'{TARGET.name}: {len(items)} Gupta Kapoor problems in {len(meta["chapters"])} chapters, '
          f'{meta["nTopics"]} subtopics, {len(meta["sheets"])} key-result sheets; '
          f'keys {dict(sorted(keys.items()))}; {meta["nVerified"]} computed keys')


if __name__ == '__main__':
    try:
        main()
    except (IntegrateError, bankparse.BankError) as e:
        print('ERROR', e)
        sys.exit(1)
