"""Renderer and theme patches for UPSC-ISS-Statistics-Dashboard-STANDALONE.html.

    python3 tools/patch_dashboard.py

1. Strict LaTeX.  KaTeX runs with strict:'error', so a formula that is not
   valid LaTeX is reported (window.ISSApp.mathErrors()) instead of being
   quietly accepted, and the old fallback that turned ASCII "x^2" in prose into
   <sup> is removed: all mathematics in the data is LaTeX
   (see tools/latexify.py and tools/check_latex.py).
2. Colour theme.  A top-bar button cycles Auto -> Dark -> Light.  Auto follows
   the operating system; the choice is remembered in this browser only.  The
   dark palette is the page's own; the header gets a calmer dark variant and
   the option-letter badges keep their contrast in both themes.

Safe to re-run: each patch is applied once, and the theme block is replaced
between its markers.
"""
import re
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / 'UPSC-ISS-Statistics-Dashboard-STANDALONE.html'

SUP_HACK = """    /* the AI-derived explanations are written in ASCII maths (x^2, 10^-6);
       render the exponents as real superscripts for readability */
    h = h.replace(/([A-Za-z0-9\\)\\]])\\^(-?\\d+|[a-z])(?![A-Za-z0-9])/g,
                  '$1<sup>$2</sup>');
"""
SUP_NOTE = """    /* all mathematics in the data is LaTeX inside $...$ (checked by
       tools/check_latex.py), so prose needs no ASCII-maths fallback */
"""

PATCHES = [
    ("    displayMode: false, throwOnError: true, strict: 'ignore', trust: false,",
     "    displayMode: false, throwOnError: true, strict: 'error', trust: false,"),
    ("    displayMode: true, throwOnError: true, strict: 'ignore', trust: false,",
     "    displayMode: true, throwOnError: true, strict: 'error', trust: false,"),
    (SUP_HACK, SUP_NOTE),
    # restore the saved theme before first paint
    ('<meta name="color-scheme" content="light dark">\n',
     '<meta name="color-scheme" content="light dark">\n'
     '<script>/* colour theme chosen with the top-bar button (per browser) */\n'
     "try { var t = localStorage.getItem('upsc.iss.theme'); if (t === 'dark' || t === 'light') "
     "document.documentElement.setAttribute('data-theme', t); } catch (e) {}\n"
     '</script>\n'),
    # the OS dark palette applies unless the reader forced the light theme
    ('@media (prefers-color-scheme: dark) {\n  :root {',
     '@media (prefers-color-scheme: dark) {\n  :root:not([data-theme="light"]) {'),
    # top-bar button
    ('    <button type="button" data-act="go" data-r="gk" title="Gupta Kapoor Ch 5–8 problem bank">Gupta Kapoor</button>',
     '    <button type="button" id="themeBtn" class="theme-btn" title="Colour theme" aria-label="Colour theme">'
     '<span aria-hidden="true">&#9680;</span><span class="tlabel"> Auto</span></button>\n'
     '    <button type="button" data-act="go" data-r="gk" title="Gupta Kapoor Ch 5–8 problem bank">Gupta Kapoor</button>'),
]

THEME_CSS_BEGIN, THEME_CSS_END = '/* THEME-CSS-BEGIN */', '/* THEME-CSS-END */'
THEME_JS_BEGIN, THEME_JS_END = '<!--THEME-JS-BEGIN-->', '<!--THEME-JS-END-->'

THEME_JS = r"""<script>
/* colour theme: Auto (follow the system) -> Dark -> Light */
(function () {
  var KEY = 'upsc.iss.theme';
  var ORDER = ['auto', 'dark', 'light'];
  var ICON = { auto: '◐', dark: '☾', light: '☀' };
  var NAME = { auto: 'Auto', dark: 'Dark', light: 'Light' };
  var btn = document.getElementById('themeBtn');
  var mode = 'auto';
  try { mode = localStorage.getItem(KEY) || 'auto'; } catch (e) {}
  if (ORDER.indexOf(mode) < 0) mode = 'auto';
  function apply() {
    var root = document.documentElement;
    if (mode === 'auto') root.removeAttribute('data-theme');
    else root.setAttribute('data-theme', mode);
    if (!btn) return;
    btn.innerHTML = '<span aria-hidden="true">' + ICON[mode] + '</span><span class="tlabel"> ' + NAME[mode] + '</span>';
    btn.title = 'Colour theme: ' + NAME[mode] + ' (click to change)';
    btn.setAttribute('aria-label', 'Colour theme: ' + NAME[mode]);
  }
  apply();
  if (btn) btn.addEventListener('click', function () {
    mode = ORDER[(ORDER.indexOf(mode) + 1) % ORDER.length];
    try { localStorage.setItem(KEY, mode); } catch (e) {}
    apply();
  });
})();
</script>
"""


def dark_tokens(html):
    m = re.search(r'@media \(prefers-color-scheme: dark\) \{\n  :root(?::not\(\[data-theme="light"\]\))? \{\n(.*?)\n  \}\n\}', html, re.S)
    if not m:
        raise SystemExit('dark palette not found')
    return m.group(1)


def theme_css(tokens):
    return f"""{THEME_CSS_BEGIN}
/* colour theme: :root[data-theme] is set by the top-bar button; without it the
   page follows the operating system */
:root {{ color-scheme: light; --topbar-bg: var(--brand); --topbar-ink: var(--brand-ink); }}
:root[data-theme="dark"] {{
{tokens}
  color-scheme: dark; --topbar-bg: #15263c; --topbar-ink: #e7ecf3;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{ color-scheme: dark; --topbar-bg: #15263c; --topbar-ink: #e7ecf3; }}
}}
#topbar {{ background: var(--topbar-bg); color: var(--topbar-ink); }}
#topbar button {{ color: var(--topbar-ink); }}
#topbar .theme-btn {{ min-width: 42px; }}
@media (max-width: 480px) {{ #topbar .theme-btn .tlabel {{ display: none; }} }}
.opt.correct .k, .opt.wrong .k {{ color: var(--surface); }}
.pyq-badge {{ color: var(--ink-3); }}
{THEME_CSS_END}
"""


def put_block(html, begin, end, body, anchor):
    if begin in html:
        a = html.index(begin)
        b = html.index(end, a) + len(end) + 1
        return html[:a] + body + html[b:]
    if html.count(anchor) != 1:
        raise SystemExit(f'anchor not found once: {anchor[:40]!r}')
    return html.replace(anchor, body + anchor)


def main():
    html = TARGET.read_text(encoding='utf-8')
    for old, new in PATCHES:
        if new in html:
            continue
        if html.count(old) != 1:
            raise SystemExit(f'patch anchor found {html.count(old)} times: {old[:60]!r}')
        html = html.replace(old, new)
    html = put_block(html, THEME_CSS_BEGIN, THEME_CSS_END, theme_css(dark_tokens(html)),
                     '</style>\n<!--KATEX-BUNDLE-START-->')
    html = put_block(html, THEME_JS_BEGIN, THEME_JS_END,
                     f'{THEME_JS_BEGIN}\n{THEME_JS}{THEME_JS_END}\n', '</body>\n</html>')
    TARGET.write_text(html, encoding='utf-8')
    print(f'{TARGET.name}: strict KaTeX, no ASCII-maths fallback, Auto/Dark/Light theme toggle')


if __name__ == '__main__':
    sys.exit(main())
