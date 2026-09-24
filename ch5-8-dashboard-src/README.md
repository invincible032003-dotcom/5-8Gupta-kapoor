# Source for the Gupta Kapoor tab

The **Gupta Kapoor** tab of `../UPSC-ISS-Statistics-Dashboard-STANDALONE.html` is generated from this folder. The dashboard stays a single offline file with no CDN, web fonts or network calls. Its maths is typeset by the KaTeX 0.16.22 already embedded in it.

| Path | What it holds |
|---|---|
| `bank/ch5.txt` … `bank/ch8.txt` | The problem bank. Each item has a question, four options, the key, the solution steps, an exam shortcut, tips and tricks (a trap note plus `TIP` lines, three or more in all) and optional `CHK` answer checks |
| `formulas.py` | The key-result sheets shown on each chapter's *Key results & formulas* tab |
| `bankparse.py` | Parser and structural validation for the bank format |
| `verify.py` | Runs every `CHK` with sympy/scipy and renders every formula with KaTeX in strict mode, using the dashboard's own macro table. Also rejects Unicode maths outside `$…$`, HTML the dashboard would not render, and items with fewer than three tips. Exits non-zero on any failure |
| `katex_check.js`, `vendor/katex.min.js` | The KaTeX renderer used by `verify.py` (the same version the dashboard embeds) |
| `integrate.py` | Converts the bank to the dashboard's question schema and writes it into the dashboard with the tab code. It spreads answer keys evenly over (a)–(d) with a fixed seed and rewrites "Option X" references. It also maps each subtopic to the ISS syllabus and PYQ taxonomy |
| `dashboard/gk.js`, `dashboard/gk.css` | The tab itself: chapter tabs, subtopic tabs, inline answering, practice sessions and the formula sheets |

```bash
pip install sympy scipy numpy          # for verify.py (node is needed too)
python3 verify.py && python3 integrate.py
```

`integrate.py` can be re-run safely. It replaces its own data block and code blocks in the dashboard and applies each small hook into the existing app only once.

## Item format

```
@@ topic=7B | sec=7·2·5 | page=7·12 | diff=2 | type=Statement
Q: stem with $inline$ and $$display$$ math<br>1. statement<br>2. statement<br>Which are correct?
A: option (a)
B: option (b)
C: option (c)
D: option (d)
ANS: A
S: solution step (repeatable)
SC: exam shortcut
TR: trap / why a distractor tempts (optional; shown first under Tips & Tricks)
TIP: tip or trick (repeatable)
CHK: python expression that must be True (optional, repeatable)
```

`diff`: 1 = Foundation, 2 = Exam-level, 3 = Elite. `sec` and `page` cite *Fundamentals of Mathematical Statistics* (S.C. Gupta & V.K. Kapoor). Pages are written as chapter·page. Outside `$…$` only `<b>`, `<i>` and (in the question) `<br>` are allowed, and all mathematics must be LaTeX.
