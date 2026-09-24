"""Parser for the plain-text problem bank (bank/ch*.txt).

Format (one item):

    @@ topic=5A | sec=5·2 | page=5·4 | diff=2 | type=Numerical
    Q: question text, $inline math$ and $$display math$$
       (indented / untagged lines continue the previous field)
    A: option (a)
    B: option (b)
    C: option (c)
    D: option (d)
    ANS: C
    S: solution step            (repeatable, in order)
    SC: exam shortcut
    TR: trap / why the distractors tempt   (optional)
    CHK: python expression that must be True   (optional, repeatable)

File-level lines:
    #CHAPTER 5 | Random Variables & Distribution Functions
    #TOPIC 5A | Distribution function & its properties
    // comment
"""
import re
import sys
from pathlib import Path

FIELD_RE = re.compile(r'^(Q|A|B|C|D|ANS|S|SC|TR|CHK):\s?(.*)$')
DIFF_NAMES = {1: 'Foundation', 2: 'Exam-level', 3: 'Elite'}


class BankError(Exception):
    pass


def parse_file(path):
    chapter = None
    topics = {}
    items = []
    cur = None
    last = None
    lines = Path(path).read_text(encoding='utf-8').splitlines()
    for ln, raw in enumerate(lines, 1):
        line = raw.rstrip()
        where = f'{path}:{ln}'
        if not line.strip() or line.lstrip().startswith('//'):
            continue
        if line.startswith('#CHAPTER'):
            num, title = [x.strip() for x in line[len('#CHAPTER'):].split('|', 1)]
            chapter = {'num': int(num), 'title': title}
            continue
        if line.startswith('#TOPIC'):
            code, title = [x.strip() for x in line[len('#TOPIC'):].split('|', 1)]
            topics[code] = title
            continue
        if line.startswith('@@'):
            if cur:
                items.append(cur)
            meta = {}
            for part in line[2:].split('|'):
                if not part.strip():
                    continue
                k, v = part.split('=', 1)
                meta[k.strip()] = v.strip()
            if meta.get('topic') not in topics:
                raise BankError(f'{where}: unknown topic {meta.get("topic")!r}')
            cur = {'meta': meta, 'Q': '', 'opts': {}, 'ANS': '', 'S': [], 'SC': '',
                   'TR': '', 'CHK': [], 'line': ln, 'file': str(path)}
            last = None
            continue
        m = FIELD_RE.match(line)
        if m and cur is not None:
            tag, val = m.group(1), m.group(2).strip()
            if tag in 'ABCD' and len(tag) == 1:
                cur['opts'][tag] = val
                last = ('opt', tag)
            elif tag in ('S', 'CHK'):
                cur[tag].append(val)
                last = (tag, len(cur[tag]) - 1)
            else:
                cur[tag] = val
                last = (tag, None)
            continue
        if cur is None or last is None:
            raise BankError(f'{where}: stray line {line!r}')
        # continuation line
        text = line.strip()
        kind, idx = last
        if kind == 'opt':
            cur['opts'][idx] += ' ' + text
        elif kind in ('S', 'CHK'):
            joiner = '\n' if kind == 'CHK' else ' '
            cur[kind][idx] += joiner + text
        else:
            cur[kind] += ' ' + text
    if cur:
        items.append(cur)
    if chapter is None:
        raise BankError(f'{path}: missing #CHAPTER line')
    return chapter, topics, items


def normalise(chapter, topics, items):
    out = []
    for n, it in enumerate(items, 1):
        where = f'{it["file"]}:{it["line"]}'
        meta = it['meta']
        if sorted(it['opts']) != ['A', 'B', 'C', 'D']:
            raise BankError(f'{where}: need exactly options A-D, got {sorted(it["opts"])}')
        opts = [it['opts'][k] for k in 'ABCD']
        if len(set(o.replace(' ', '') for o in opts)) != 4:
            raise BankError(f'{where}: duplicate options')
        if it['ANS'] not in ('A', 'B', 'C', 'D'):
            raise BankError(f'{where}: bad ANS {it["ANS"]!r}')
        if not it['Q'] or not it['S'] or not it['SC']:
            raise BankError(f'{where}: missing Q / S / SC')
        diff = int(meta.get('diff', 2))
        if diff not in DIFF_NAMES:
            raise BankError(f'{where}: bad diff')
        out.append({
            'id': f'{chapter["num"]}.{n:03d}',
            'ch': chapter['num'],
            'topic': meta['topic'],
            'sec': meta.get('sec', ''),
            'page': meta.get('page', ''),
            'diff': diff,
            'type': meta.get('type', 'Numerical'),
            'q': it['Q'],
            'opts': opts,
            'ans': 'ABCD'.index(it['ANS']),
            'steps': it['S'],
            'sc': it['SC'],
            'tr': it['TR'],
            '_chk': it['CHK'],
            '_where': where,
        })
    return out


def load_all(bank_dir):
    chapters = []
    for path in sorted(Path(bank_dir).glob('ch*.txt')):
        chapter, topics, items = parse_file(path)
        chapter['topics'] = [{'code': c, 'title': t} for c, t in topics.items()]
        chapter['items'] = normalise(chapter, topics, items)
        chapters.append(chapter)
    return chapters


if __name__ == '__main__':
    chs = load_all(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / 'bank')
    for c in chs:
        print(f'Chapter {c["num"]}: {len(c["items"])} items, {len(c["topics"])} topics')
