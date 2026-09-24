# Source for `GuptaKapoor-Ch5-8-ISS-Objective-Dashboard.html`

The dashboard is one offline HTML file. It has no CDN, web fonts or network calls.
KaTeX 0.16.22 (MIT) is inlined from `vendor/`.

| Path | What it holds |
|---|---|
| `bank/ch5.txt` … `bank/ch8.txt` | The problem bank. Each item has a question, four options, the key, solution steps, an exam shortcut, an optional trap note and an optional `CHK` answer check |
| `formulas.py` | The formula & shortcut sheet cards |
| `src/` | UI template, stylesheet and app logic |
| `bankparse.py` | Parser and structural validation for the bank format |
| `verify.py` | Runs every `CHK` with sympy/scipy and renders every formula with KaTeX; exits non-zero on any failure |
| `build.py` | Spreads answer keys evenly over (a)–(d) with a fixed seed and rewrites "Option X" references. Then writes the single HTML file to the repo root |

```bash
pip install sympy scipy numpy      # for verify.py
python3 verify.py && python3 build.py
```

## Item format

```
@@ topic=7B | sec=7·2·5 | page=7·12 | diff=2 | type=Statement
Q: question text with $inline$ and $$display$$ math
A: option (a)
B: option (b)
C: option (c)
D: option (d)
ANS: A
S: solution step (repeatable)
SC: exam shortcut
TR: trap / why the distractors tempt (optional)
CHK: python expression that must be True (optional, repeatable)
```

`diff`: 1 = Foundation, 2 = Exam-level, 3 = Elite. `sec` and `page` cite *Fundamentals of Mathematical Statistics* (S.C. Gupta & V.K. Kapoor). Pages are written as chapter·page.
