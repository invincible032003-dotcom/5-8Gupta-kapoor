/* G&K Ch 5–8 ISS problem bank — dashboard logic. Runs fully offline; no network calls. */
(function () {
  'use strict';

  const B = window.BANK;
  const ITEMS = B.items;
  const BY_ID = new Map(ITEMS.map((it) => [it.id, it]));
  const CHAPTERS = B.chapters;
  const CH = new Map(CHAPTERS.map((c) => [c.num, c]));
  const TOPIC = new Map();
  CHAPTERS.forEach((c) => c.topics.forEach((t) => TOPIC.set(t.code, Object.assign({ ch: c.num }, t))));
  const DIFF = { 1: 'Foundation', 2: 'Exam-level', 3: 'Elite' };
  const TYPES = Array.from(new Set(ITEMS.map((i) => i.type))).sort();
  const LETTERS = ['a', 'b', 'c', 'd'];
  const KEY = 'gk58.iss.v1';

  const main = document.getElementById('main');
  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const pct = (x) => (x == null ? '—' : Math.round(x * 100) + '%');

  // ------------------------------------------------------------------ storage
  function loadState() {
    let s = {};
    try { s = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { s = {}; }
    return {
      att: s.att && typeof s.att === 'object' ? s.att : {},
      bm: s.bm && typeof s.bm === 'object' ? s.bm : {},
      mocks: Array.isArray(s.mocks) ? s.mocks : [],
      prefs: s.prefs && typeof s.prefs === 'object' ? s.prefs : {},
      active: s.active || null,
    };
  }
  let S = loadState();
  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { /* private mode: keep in memory */ }
  }

  // ------------------------------------------------------------------ math
  const texCache = new Map();
  function tex(src, display) {
    const k = (display ? 'D' : 'I') + src;
    let h = texCache.get(k);
    if (h === undefined) {
      try {
        h = window.katex.renderToString(src, { displayMode: display, throwOnError: false, strict: 'ignore' });
      } catch (e) {
        h = '<code>' + esc(src) + '</code>';
      }
      texCache.set(k, h);
    }
    return h;
  }
  // Bank text is trusted author HTML with $...$ / $$...$$ math.
  function rich(text) {
    return String(text).replace(/\$\$([\s\S]+?)\$\$|\$([\s\S]+?)\$/g, (m, d, i) => (d !== undefined ? tex(d, true) : tex(i, false)));
  }

  // ------------------------------------------------------------------ helpers
  function stats(ids) {
    let att = 0, ok = 0;
    ids.forEach((id) => { const a = S.att[id]; if (a) { att++; if (a.ok) ok++; } });
    return { n: ids.length, att, ok, acc: att ? ok / att : null };
  }
  function idsWhere(fn) { return ITEMS.filter(fn).map((it) => it.id); }
  function mulberry(seed) {
    let a = seed >>> 0;
    return function () {
      a = (a + 0x6d2b79f5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function shuffle(arr, seed) {
    const r = mulberry(seed), a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); const t = a[i]; a[i] = a[j]; a[j] = t; }
    return a;
  }
  function fmtTime(sec) {
    sec = Math.max(0, Math.round(sec));
    const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = sec % 60;
    const mm = String(m).padStart(2, '0'), ss = String(s).padStart(2, '0');
    return h ? h + ':' + mm + ':' + ss : mm + ':' + ss;
  }
  let toastTimer = null;
  function toast(msg) {
    let t = $('.toast');
    if (!t) { t = document.createElement('div'); t.className = 'toast'; t.setAttribute('role', 'status'); document.body.appendChild(t); }
    t.textContent = msg;
    t.classList.add('on');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove('on'), 1600);
  }
  function go(hash) { if (location.hash === hash) render(); else location.hash = hash; }
  function bar(ok, bad, total) {
    const w = (x) => (total ? (100 * x) / total : 0).toFixed(1) + '%';
    return '<div class="bar" aria-hidden="true"><span class="b-ok" style="width:' + w(ok) + '"></span><span class="b-bad" style="width:' + w(bad) + '"></span></div>';
  }
  function toggleBookmark(id) {
    if (S.bm[id]) delete S.bm[id]; else S.bm[id] = Date.now();
    save();
    toast(S.bm[id] ? 'Bookmarked ' + id : 'Bookmark removed');
  }

  // ------------------------------------------------------------------ shared question rendering
  function refText(it) {
    const parts = [];
    if (it.sec) parts.push('§' + it.sec);
    if (it.page) parts.push('p. ' + it.page);
    return parts.length ? 'G&K ' + parts.join(' · ') : '';
  }
  function qHead(it, extra) {
    const t = TOPIC.get(it.topic);
    return '<div class="qhead">' +
      (extra && extra.num ? '<span class="chip">Q ' + extra.num + '</span>' : '') +
      '<span class="qid">' + it.id + '</span>' +
      '<span class="chip" title="' + esc(t.title) + '">Ch ' + it.ch + ' · ' + esc(t.code) + ' ' + esc(t.title) + '</span>' +
      '<span class="chip d' + it.diff + '">' + DIFF[it.diff] + '</span>' +
      '<span class="chip">' + esc(it.type) + '</span>' +
      (extra && extra.last ? extra.last : '') +
      '<span class="ref">' + esc(refText(it)) + '</span>' +
      '</div>';
  }
  function optionsHTML(it, st) {
    // st: {sel, reveal, lock}
    return '<ol class="opts" role="list">' + it.opts.map((o, i) => {
      let cls = 'opt';
      if (st.reveal) {
        if (i === it.ans) cls += ' right';
        else if (i === st.sel) cls += ' wrong';
      } else if (i === st.sel) cls += ' sel';
      return '<li><button type="button" class="' + cls + '" data-opt="' + i + '"' + (st.lock ? ' disabled' : '') +
        ' aria-pressed="' + (i === st.sel) + '"><span class="lbl">' + LETTERS[i] + '</span><span class="otext">' + rich(o) + '</span></button></li>';
    }).join('') + '</ol>';
  }
  function solutionHTML(it, sel) {
    let verdict;
    if (sel == null) verdict = '<div class="verdict neutral">Answer: (' + LETTERS[it.ans] + ')</div>';
    else if (sel === it.ans) verdict = '<div class="verdict ok">✓ Correct — (' + LETTERS[it.ans] + ')</div>';
    else verdict = '<div class="verdict bad">✗ Incorrect — you chose (' + LETTERS[sel] + '); correct answer is (' + LETTERS[it.ans] + ')</div>';
    return verdict + '<div class="solution"><h4>Step-by-step solution</h4><ol class="steps">' +
      it.steps.map((s) => '<li>' + rich(s) + '</li>').join('') + '</ol>' +
      '<div class="box tip"><h4>⚡ Exam shortcut</h4>' + rich(it.sc) + '</div>' +
      (it.tr ? '<div class="box trap"><h4>⚠ Trap</h4>' + rich(it.tr) + '</div>' : '') +
      '</div>';
  }
  function staticQuestion(it, sel, extra) {
    return qHead(it, extra) + '<div class="qtext">' + rich(it.q) + '</div>' +
      optionsHTML(it, { sel: sel, reveal: true, lock: true }) + solutionHTML(it, sel);
  }

  // ------------------------------------------------------------------ keyboard
  let keyHandler = null;
  document.addEventListener('keydown', (e) => {
    if (!keyHandler || e.ctrlKey || e.metaKey || e.altKey) return;
    const tag = (e.target && e.target.tagName) || '';
    if (/INPUT|SELECT|TEXTAREA/.test(tag)) return;
    keyHandler(e);
  });
  let tick = null;
  function stopTimers() { if (tick) { clearInterval(tick); tick = null; } keyHandler = null; }

  // ------------------------------------------------------------------ router
  function parseHash() {
    const h = location.hash.replace(/^#\/?/, '');
    const qi = h.indexOf('?');
    const path = qi >= 0 ? h.slice(0, qi) : h;
    const params = new URLSearchParams(qi >= 0 ? h.slice(qi + 1) : '');
    const parts = path.split('/').filter(Boolean);
    return { name: parts[0] || 'home', arg: parts[1] || null, arg2: parts[2] || null, params: params };
  }
  const routes = { home: viewHome, practice: viewPractice, mock: viewMock, sheets: viewSheets, review: viewReview, search: viewSearch };
  function render() {
    stopTimers();
    const r = parseHash();
    const fn = routes[r.name] || viewHome;
    $$('.nav a').forEach((a) => a.classList.toggle('active', a.dataset.nav === (routes[r.name] ? r.name : 'home')));
    main.innerHTML = '';
    fn(r);
    window.scrollTo(0, 0);
  }
  window.addEventListener('hashchange', render);

  // ------------------------------------------------------------------ theme
  function applyTheme(t) {
    if (t === 'light' || t === 'dark') document.documentElement.setAttribute('data-theme', t);
    else document.documentElement.removeAttribute('data-theme');
  }
  $('#theme-btn').addEventListener('click', () => {
    const cur = document.documentElement.getAttribute('data-theme') ||
      (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    S.prefs.theme = cur === 'dark' ? 'light' : 'dark';
    applyTheme(S.prefs.theme);
    save();
  });

  // ================================================================== HOME
  function viewHome() {
    const all = ITEMS.map((i) => i.id);
    const st = stats(all);
    const nbm = Object.keys(S.bm).filter((id) => BY_ID.has(id)).length;
    const nwrong = all.filter((id) => S.att[id] && !S.att[id].ok).length;
    const lastMock = S.mocks[S.mocks.length - 1];
    const diffCounts = [1, 2, 3].map((d) => ITEMS.filter((i) => i.diff === d).length);

    let html = '<section class="hero"><div><h1>' + esc(B.meta.title) + '</h1>' +
      '<p>' + B.meta.total + ' exam-grade objective problems built on ' + esc(B.meta.source) +
      '. Every problem has four options, a step-by-step solution, an exam shortcut and (where it matters) the trap the distractors are built on.</p></div>' +
      '<div class="btn-row"><a class="btn primary" href="#/practice">▶ ' + (st.att ? 'Continue practice' : 'Start practice') + '</a>' +
      '<a class="btn" href="#/mock">⏱ Mock test</a><a class="btn" href="#/sheets">∑ Formula sheets</a></div></section>';

    html += '<div class="grid grid-4">' +
      kpi(B.meta.total, 'Problems in the bank', diffCounts[0] + ' foundation · ' + diffCounts[1] + ' exam-level · ' + diffCounts[2] + ' elite') +
      kpi(st.att, 'Attempted', pct(st.n ? st.att / st.n : 0) + ' of the bank') +
      kpi(pct(st.acc), 'Accuracy (last attempt)', st.ok + ' correct · ' + (st.att - st.ok) + ' wrong') +
      kpi(S.mocks.length, 'Mock tests taken', lastMock ? 'Last: ' + lastMock.score.toFixed(2) + ' / ' + lastMock.max.toFixed(1) : nbm + ' bookmarked · ' + nwrong + ' to revise') +
      '</div>';

    html += '<div class="section-title"><h2>Chapters</h2><span class="muted small">Book pages are cited as chapter·page, e.g. 7·29</span></div><div class="grid grid-4">';
    CHAPTERS.forEach((c) => {
      const ids = idsWhere((i) => i.ch === c.num);
      const s = stats(ids);
      html += '<div class="card ch-card"><div class="ch-num">Chapter ' + c.num + '</div><h3>' + esc(c.title) + '</h3>' +
        '<div class="meta"><span>' + c.n + ' problems · ' + c.topics.length + ' topics</span><span>' + pct(s.acc) + '</span></div>' +
        bar(s.ok, s.att - s.ok, s.n) +
        '<div class="muted small">' + s.att + ' / ' + s.n + ' attempted</div>' +
        '<div class="btn-row"><a class="btn primary" href="#/practice?ch=' + c.num + '&topic=all&status=all&reset=1">Practice</a>' +
        '<a class="btn" href="#/sheets/' + c.num + '">Sheet</a></div></div>';
    });
    html += '</div>';

    // weak topics
    const weak = [];
    TOPIC.forEach((t) => {
      const s = stats(idsWhere((i) => i.topic === t.code));
      if (s.att >= 3 && s.acc < 0.6) weak.push({ t: t, s: s });
    });
    weak.sort((a, b) => a.s.acc - b.s.acc);
    if (weak.length) {
      html += '<div class="section-title"><h2>Weak spots</h2><span class="muted small">Topics with accuracy below 60% (3+ attempts)</span></div><div class="card"><div class="btn-row">' +
        weak.slice(0, 10).map((w) => '<a class="btn" href="#/practice?topic=' + w.t.code + '&ch=' + w.t.ch + '&status=all&reset=1">' +
          esc(w.t.code) + ' · ' + esc(w.t.title) + ' <span class="chip bad">' + pct(w.s.acc) + '</span></a>').join('') + '</div></div>';
    }

    html += '<div class="section-title"><h2>Topic map</h2><span class="muted small">Click a topic to drill it</span></div>';
    CHAPTERS.forEach((c) => {
      html += '<details class="card" ' + (c.num === 5 ? 'open' : '') + '><summary><b>Chapter ' + c.num + ' — ' + esc(c.title) + '</b> <span class="muted small">(' + c.n + ')</span></summary>' +
        '<div class="scrollx"><table class="t"><thead><tr><th>Topic</th><th class="num">Qs</th><th>Level mix</th><th>Progress</th><th class="num">Accuracy</th></tr></thead><tbody>';
      c.topics.forEach((t) => {
        const ids = idsWhere((i) => i.topic === t.code);
        const s = stats(ids);
        const dc = [1, 2, 3].map((d) => ids.filter((id) => BY_ID.get(id).diff === d).length);
        html += '<tr><td><span class="code">' + t.code + '</span> <a class="topic-link" href="#/practice?topic=' + t.code + '&ch=' + c.num + '&status=all&reset=1">' + esc(t.title) + '</a></td>' +
          '<td class="num">' + t.n + '</td>' +
          '<td><span class="mini-diff" title="Foundation / Exam-level / Elite"><span>' + dc[0] + '</span><span>' + dc[1] + '</span><span>' + dc[2] + '</span></span></td>' +
          '<td style="min-width:120px">' + bar(s.ok, s.att - s.ok, s.n) + '</td>' +
          '<td class="num">' + pct(s.acc) + '</td></tr>';
      });
      html += '</tbody></table></div></details>';
    });

    html += '<div class="section-title"><h2>How to use</h2></div><div class="grid grid-2">' +
      '<div class="card"><h3>Practice mode</h3><p>Filter by chapter, topic, level, type or status (new / wrong / bookmarked). Answer to reveal the full solution, shortcut and trap. Keys: <span class="kbd">A</span>–<span class="kbd">D</span> answer, <span class="kbd">←</span> <span class="kbd">→</span> move, <span class="kbd">S</span> solution, <span class="kbd">M</span> bookmark.</p></div>' +
      '<div class="card"><h3>Mock test mode</h3><p>Defaults follow the ISS objective paper pattern used in your Paper-I bank: 80 questions in 120 minutes, +2.5 for a correct answer and −⅓ of that for a wrong one. Pick fewer questions or specific chapters for sectional tests.</p></div>' +
      '</div>';
    main.innerHTML = html;
  }
  function kpi(v, l, s) {
    return '<div class="card kpi"><div class="v">' + v + '</div><div class="l">' + esc(l) + '</div>' + (s ? '<div class="s">' + esc(s) + '</div>' : '') + '</div>';
  }

  // ================================================================== PRACTICE
  const PDEF = { ch: 'all', topic: 'all', diff: [1, 2, 3], type: 'all', status: 'all', order: 'book', seed: 1, id: null };
  function practicePrefs() { return Object.assign({}, PDEF, S.prefs.practice || {}); }

  function viewPractice(r) {
    let P = practicePrefs();
    const prm = r.params;
    if (prm.get('reset')) P = Object.assign({}, PDEF, { order: P.order, seed: P.seed });
    ['ch', 'topic', 'type', 'status', 'order'].forEach((k) => { if (prm.get(k)) P[k] = prm.get(k); });
    if (prm.get('id')) P.id = prm.get('id');
    if (P.topic !== 'all' && TOPIC.has(P.topic)) P.ch = String(TOPIC.get(P.topic).ch);
    if (P.topic !== 'all' && !TOPIC.has(P.topic)) P.topic = 'all';

    let list = [];
    let pos = 0;
    let local = { sel: null, reveal: false };

    function statusOk(it) {
      const a = S.att[it.id];
      switch (P.status) {
        case 'new': return !a;
        case 'wrong': return !!a && !a.ok;
        case 'right': return !!a && a.ok;
        case 'bm': return !!S.bm[it.id];
        default: return true;
      }
    }
    function buildList() {
      let l = ITEMS.filter((it) => (P.ch === 'all' || it.ch === +P.ch) &&
        (P.topic === 'all' || it.topic === P.topic) && P.diff.indexOf(it.diff) >= 0 &&
        (P.type === 'all' || it.type === P.type) && statusOk(it));
      if (P.order === 'shuffle') l = shuffle(l, P.seed);
      list = l.map((it) => it.id);
      pos = P.id ? Math.max(0, list.indexOf(P.id)) : 0;
    }
    function persist() {
      P.id = list[pos] || null;
      S.prefs.practice = P;
      save();
    }
    buildList();
    if (P.id && list.indexOf(P.id) < 0 && BY_ID.has(P.id)) {
      // requested item is outside the saved filters: widen to everything
      const keep = P.id;
      P = Object.assign({}, PDEF, { order: 'book', id: keep });
      buildList();
    }

    const topicOpts = () => '<option value="all">All topics</option>' + CHAPTERS.filter((c) => P.ch === 'all' || c.num === +P.ch)
      .map((c) => '<optgroup label="Chapter ' + c.num + '">' + c.topics.map((t) =>
        '<option value="' + t.code + '"' + (P.topic === t.code ? ' selected' : '') + '>' + t.code + ' · ' + esc(t.title) + ' (' + t.n + ')</option>').join('') + '</optgroup>').join('');

    main.innerHTML =
      '<div class="card"><div class="filters">' +
      '<label class="field"><span>Chapter</span><select id="f-ch"><option value="all">All chapters</option>' +
      CHAPTERS.map((c) => '<option value="' + c.num + '"' + (String(c.num) === String(P.ch) ? ' selected' : '') + '>Ch ' + c.num + ' · ' + esc(c.title) + '</option>').join('') + '</select></label>' +
      '<label class="field"><span>Topic</span><select id="f-topic">' + topicOpts() + '</select></label>' +
      '<div class="field"><span>Level</span><div class="seg" id="f-diff">' + [1, 2, 3].map((d) =>
        '<label><input type="checkbox" value="' + d + '"' + (P.diff.indexOf(d) >= 0 ? ' checked' : '') + '><span>' + DIFF[d] + '</span></label>').join('') + '</div></div>' +
      '<label class="field"><span>Type</span><select id="f-type"><option value="all">All types</option>' +
      TYPES.map((t) => '<option' + (P.type === t ? ' selected' : '') + '>' + esc(t) + '</option>').join('') + '</select></label>' +
      '<label class="field"><span>Status</span><select id="f-status">' +
      [['all', 'All'], ['new', 'Not attempted'], ['wrong', 'Got wrong'], ['right', 'Got right'], ['bm', 'Bookmarked']]
        .map((o) => '<option value="' + o[0] + '"' + (P.status === o[0] ? ' selected' : '') + '>' + o[1] + '</option>').join('') + '</select></label>' +
      '<div class="field"><span>Order</span><div class="seg" id="f-order">' +
      '<label><input type="radio" name="ord" value="book"' + (P.order === 'book' ? ' checked' : '') + '><span>Book</span></label>' +
      '<label><input type="radio" name="ord" value="shuffle"' + (P.order === 'shuffle' ? ' checked' : '') + '><span>Shuffled</span></label></div></div>' +
      '<button type="button" class="btn ghost" id="f-reset" title="Clear all filters">Reset</button>' +
      '</div></div>' +
      '<div class="practice-layout"><div id="qwrap"></div><aside class="side">' +
      '<div class="card"><div class="section-title" style="margin:0 0 8px"><h3 style="margin:0">Question set</h3><span class="muted small" id="set-count"></span></div>' +
      '<div class="palette" id="palette"></div>' +
      '<div class="legend"><span><i class="ok"></i>right</span><span><i class="bad"></i>wrong</span><span><i></i>new</span><span><i class="bm"></i>bookmarked</span></div></div>' +
      '<div class="card" id="set-stats"></div></aside></div>';

    const qwrap = $('#qwrap');

    function renderPalette() {
      const pal = $('#palette');
      $('#set-count').textContent = list.length + ' problem' + (list.length === 1 ? '' : 's');
      pal.innerHTML = list.map((id, i) => {
        const a = S.att[id];
        let cls = 'pcell';
        if (a) cls += a.ok ? ' ok' : ' bad';
        if (S.bm[id]) cls += ' bm';
        if (i === pos) cls += ' cur';
        return '<button type="button" class="' + cls + '" data-i="' + i + '" title="' + id + '">' + (i + 1) + '</button>';
      }).join('');
      const cur = pal.querySelector('.cur');
      if (cur && cur.scrollIntoView) {
        const pr = pal.getBoundingClientRect(), cr = cur.getBoundingClientRect();
        if (cr.top < pr.top || cr.bottom > pr.bottom) pal.scrollTop += cr.top - pr.top - pr.height / 2;
      }
      const s = stats(list);
      $('#set-stats').innerHTML = '<h3>This set</h3><p class="small">' + s.att + ' of ' + s.n + ' attempted · accuracy ' + pct(s.acc) + '</p>' +
        bar(s.ok, s.att - s.ok, s.n) +
        '<div class="btn-row" style="margin-top:10px"><button type="button" class="btn" id="reshuffle">⤮ New shuffle</button></div>';
      $('#reshuffle').addEventListener('click', () => {
        P.order = 'shuffle'; P.seed = (Math.random() * 1e9) >>> 0; P.id = null;
        $$('#f-order input').forEach((x) => { x.checked = x.value === 'shuffle'; });
        buildList(); local = { sel: null, reveal: false }; persist(); renderAll();
      });
    }

    function renderQuestion() {
      if (!list.length) {
        qwrap.innerHTML = '<div class="card empty"><h3>No problems match these filters</h3><p>Relax a filter or press Reset.</p></div>';
        return;
      }
      const it = BY_ID.get(list[pos]);
      const prev = S.att[it.id];
      const last = prev ? ' <span class="chip ' + (prev.ok ? 'ok' : 'bad') + '">last: ' + (prev.ok ? 'right' : 'wrong') + '</span>' : '';
      qwrap.innerHTML = '<div class="card qcard">' + qHead(it, { num: (pos + 1) + ' / ' + list.length, last: last }) +
        '<div class="qtext">' + rich(it.q) + '</div>' +
        optionsHTML(it, { sel: local.sel, reveal: local.reveal, lock: local.reveal }) +
        '<div class="qactions">' +
        '<button type="button" class="btn" id="q-prev"' + (pos === 0 ? ' disabled' : '') + '>← Prev</button>' +
        '<button type="button" class="btn" id="q-next"' + (pos >= list.length - 1 ? ' disabled' : '') + '>Next →</button>' +
        '<span class="spacer"></span>' +
        (local.reveal ? '<button type="button" class="btn" id="q-retry">↺ Try again</button>' : '<button type="button" class="btn" id="q-show">Show solution</button>') +
        '<button type="button" class="btn bm-btn' + (S.bm[it.id] ? ' on' : '') + '" id="q-bm" aria-pressed="' + !!S.bm[it.id] + '" title="Bookmark (M)">' + (S.bm[it.id] ? '★' : '☆') + '</button>' +
        '</div>' +
        (local.reveal ? solutionHTML(it, local.sel) : '') +
        '<div class="kbd-hint">Keys: <span class="kbd">A</span>–<span class="kbd">D</span> answer · <span class="kbd">←</span>/<span class="kbd">→</span> move · <span class="kbd">S</span> solution · <span class="kbd">M</span> bookmark</div>' +
        '</div>';
      $$('.opt', qwrap).forEach((b) => b.addEventListener('click', () => answer(+b.dataset.opt)));
      $('#q-prev').addEventListener('click', () => move(-1));
      $('#q-next').addEventListener('click', () => move(1));
      const show = $('#q-show');
      if (show) show.addEventListener('click', reveal);
      const retry = $('#q-retry');
      if (retry) retry.addEventListener('click', () => { local = { sel: null, reveal: false }; renderQuestion(); });
      $('#q-bm').addEventListener('click', () => { toggleBookmark(it.id); renderQuestion(); renderPalette(); });
    }
    function answer(i) {
      if (!list.length || local.reveal) return;
      const it = BY_ID.get(list[pos]);
      const prev = S.att[it.id];
      S.att[it.id] = { c: i, ok: i === it.ans, t: Date.now(), n: (prev && prev.n ? prev.n : 0) + 1 };
      save();
      local = { sel: i, reveal: true };
      renderQuestion();
      renderPalette();
    }
    function reveal() { if (!list.length) return; local = { sel: null, reveal: true }; renderQuestion(); }
    function move(d) {
      const np = pos + d;
      if (np < 0 || np >= list.length) return;
      pos = np; local = { sel: null, reveal: false }; persist();
      renderQuestion(); renderPalette();
      const top = qwrap.getBoundingClientRect().top;
      if (top < 0 || top > window.innerHeight * 0.6) qwrap.scrollIntoView({ block: 'start' });
    }
    function renderAll() { renderQuestion(); renderPalette(); }

    $('#palette').addEventListener('click', (e) => {
      const b = e.target.closest('.pcell');
      if (!b) return;
      pos = +b.dataset.i; local = { sel: null, reveal: false }; persist(); renderAll();
      qwrap.scrollIntoView({ block: 'start' });
    });
    function onFilter() {
      P.id = null;
      buildList(); local = { sel: null, reveal: false }; persist(); renderAll();
    }
    $('#f-ch').addEventListener('change', (e) => {
      P.ch = e.target.value;
      if (P.topic !== 'all' && P.ch !== 'all' && TOPIC.get(P.topic).ch !== +P.ch) P.topic = 'all';
      $('#f-topic').innerHTML = topicOpts();
      onFilter();
    });
    $('#f-topic').addEventListener('change', (e) => {
      P.topic = e.target.value;
      if (P.topic !== 'all') { P.ch = String(TOPIC.get(P.topic).ch); $('#f-ch').value = P.ch; $('#f-topic').innerHTML = topicOpts(); }
      onFilter();
    });
    $('#f-diff').addEventListener('change', () => {
      P.diff = $$('#f-diff input:checked').map((x) => +x.value);
      if (!P.diff.length) { P.diff = [1, 2, 3]; $$('#f-diff input').forEach((x) => { x.checked = true; }); }
      onFilter();
    });
    $('#f-type').addEventListener('change', (e) => { P.type = e.target.value; onFilter(); });
    $('#f-status').addEventListener('change', (e) => { P.status = e.target.value; onFilter(); });
    $('#f-order').addEventListener('change', (e) => {
      P.order = e.target.value;
      if (P.order === 'shuffle') P.seed = (Math.random() * 1e9) >>> 0;
      onFilter();
    });
    $('#f-reset').addEventListener('click', () => {
      P = Object.assign({}, PDEF);
      S.prefs.practice = P; save();
      go('#/practice');
    });

    keyHandler = (e) => {
      const k = e.key.toLowerCase();
      const map = { a: 0, b: 1, c: 2, d: 3, 1: 0, 2: 1, 3: 2, 4: 3 };
      if (k === 'arrowright' || k === 'n') { move(1); e.preventDefault(); }
      else if (k === 'arrowleft' || k === 'p') { move(-1); e.preventDefault(); }
      else if (k === 's') { if (!local.reveal) reveal(); }
      else if (k === 'm') { const id = list[pos]; if (id) { toggleBookmark(id); renderQuestion(); renderPalette(); } }
      else if (k in map) { answer(map[k]); }
    };
    persist();
    renderAll();
  }

  // ================================================================== MOCK
  const MDEF = { n: 80, chs: [5, 6, 7, 8], level: 'all', secs: 90, plus: 2.5, minus: 0.83 };
  function viewMock(r) {
    if (r.arg === 'run') return mockRun();
    if (r.arg === 'result') return mockResult(+r.arg2);
    const C = Object.assign({}, MDEF, S.prefs.mock || {});
    let html = '<div class="hero"><div><h1>Mock test</h1><p>Timed, negatively-marked tests drawn at random from the bank, stratified by chapter. Solutions open only after you submit.</p></div></div>';
    if (S.active) {
      const a = S.active;
      const left = a.dur - (Date.now() - a.start) / 1000;
      html += '<div class="card"><h3>Test in progress</h3><p>' + a.ids.length + ' questions · ' + Object.keys(a.ans).length + ' answered · ' +
        (left > 0 ? fmtTime(left) + ' left' : 'time is up') + '</p><div class="btn-row">' +
        '<a class="btn primary" href="#/mock/run">Resume</a><button type="button" class="btn danger" id="m-abandon">Abandon test</button></div></div>';
    }
    html += '<div class="card"><h3>New test</h3><div class="filters">' +
      '<div class="field"><span>Questions</span><div class="seg" id="m-n">' + [20, 40, 80].map((n) =>
        '<label><input type="radio" name="mn" value="' + n + '"' + (C.n === n ? ' checked' : '') + '><span>' + n + '</span></label>').join('') + '</div></div>' +
      '<div class="field"><span>Chapters</span><div class="seg" id="m-ch">' + CHAPTERS.map((c) =>
        '<label><input type="checkbox" value="' + c.num + '"' + (C.chs.indexOf(c.num) >= 0 ? ' checked' : '') + '><span>Ch ' + c.num + '</span></label>').join('') + '</div></div>' +
      '<label class="field"><span>Level</span><select id="m-level"><option value="all"' + (C.level === 'all' ? ' selected' : '') + '>Mixed (whole bank)</option>' +
      '<option value="hard"' + (C.level === 'hard' ? ' selected' : '') + '>Exam-level + Elite only</option>' +
      '<option value="elite"' + (C.level === 'elite' ? ' selected' : '') + '>Elite only</option></select></label>' +
      '<label class="field"><span>Seconds / question</span><input type="number" id="m-secs" min="20" max="600" step="5" value="' + C.secs + '"></label>' +
      '<label class="field"><span>Marks right</span><input type="number" id="m-plus" min="0" step="0.01" value="' + C.plus + '"></label>' +
      '<label class="field"><span>Penalty wrong</span><input type="number" id="m-minus" min="0" step="0.01" value="' + C.minus + '"></label>' +
      '</div><p class="muted small" id="m-summary"></p><div class="btn-row"><button type="button" class="btn primary" id="m-start">Start test</button></div></div>';

    if (S.mocks.length) {
      html += '<div class="section-title"><h2>History</h2></div><div class="card scrollx"><table class="t"><thead><tr><th>Date</th><th class="num">Qs</th><th class="num">Score</th><th class="num">Right</th><th class="num">Wrong</th><th class="num">Blank</th><th class="num">Time</th><th></th></tr></thead><tbody>' +
        S.mocks.map((m, i) => ({ m: m, i: i })).reverse().map((o) => '<tr><td>' + new Date(o.m.when).toLocaleString() + '</td><td class="num">' + o.m.ids.length + '</td>' +
          '<td class="num"><b>' + o.m.score.toFixed(2) + '</b> / ' + o.m.max.toFixed(1) + '</td><td class="num">' + o.m.right + '</td><td class="num">' + o.m.wrong + '</td><td class="num">' + o.m.blank + '</td>' +
          '<td class="num">' + fmtTime(o.m.used) + '</td><td><a href="#/mock/result/' + o.i + '">Review</a></td></tr>').join('') + '</tbody></table></div>';
    }
    main.innerHTML = html;

    function readCfg() {
      const n = +($('#m-n input:checked') || { value: 80 }).value;
      const chs = $$('#m-ch input:checked').map((x) => +x.value);
      const secs = Math.min(600, Math.max(20, +$('#m-secs').value || 90));
      const plus = Math.max(0, +$('#m-plus').value || 0);
      const minus = Math.max(0, +$('#m-minus').value || 0);
      return { n: n, chs: chs, level: $('#m-level').value, secs: secs, plus: plus, minus: minus };
    }
    function pool(cfg) {
      return ITEMS.filter((it) => cfg.chs.indexOf(it.ch) >= 0 &&
        (cfg.level === 'all' || (cfg.level === 'hard' ? it.diff >= 2 : it.diff === 3)));
    }
    function summary() {
      const cfg = readCfg();
      const p = pool(cfg);
      const n = Math.min(cfg.n, p.length);
      $('#m-summary').textContent = p.length ? n + ' questions from a pool of ' + p.length + ' · ' + fmtTime(n * cfg.secs) +
        ' · max ' + (n * cfg.plus).toFixed(1) + ' marks · −' + cfg.minus + ' per wrong answer' : 'Select at least one chapter.';
      $('#m-start').disabled = !p.length;
    }
    main.addEventListener('change', summary);
    main.addEventListener('input', summary);
    summary();
    $('#m-start').addEventListener('click', () => {
      const cfg = readCfg();
      const p = pool(cfg);
      if (!p.length) return;
      if (S.active && !window.confirm('Abandon the test in progress and start a new one?')) return;
      S.prefs.mock = cfg;
      const n = Math.min(cfg.n, p.length);
      // stratified by chapter, proportional to pool size (largest remainders)
      const byCh = {};
      p.forEach((it) => { (byCh[it.ch] = byCh[it.ch] || []).push(it.id); });
      const chs = Object.keys(byCh);
      const quota = chs.map((c) => ({ c: c, q: (n * byCh[c].length) / p.length }));
      quota.forEach((o) => { o.k = Math.floor(o.q); });
      let rem = n - quota.reduce((s, o) => s + o.k, 0);
      quota.slice().sort((x, y) => (y.q - y.k) - (x.q - x.k)).forEach((o) => { if (rem > 0) { o.k++; rem--; } });
      const seed = (Math.random() * 1e9) >>> 0;
      let ids = [];
      quota.forEach((o, j) => { ids = ids.concat(shuffle(byCh[o.c], seed + j).slice(0, o.k)); });
      ids = shuffle(ids, seed + 99);
      S.active = { ids: ids, ans: {}, mark: {}, seen: {}, pos: 0, start: Date.now(), dur: n * cfg.secs, cfg: cfg };
      save();
      go('#/mock/run');
    });
    const ab = $('#m-abandon');
    if (ab) ab.addEventListener('click', () => {
      if (!window.confirm('Abandon this test? Answers will be discarded.')) return;
      S.active = null; save(); render();
    });
  }

  function mockRun() {
    const A = S.active;
    if (!A) { go('#/mock'); return; }
    main.innerHTML = '<div class="mock-bar"><span class="timer" id="t-left">--:--</span><span class="muted" id="t-prog"></span>' +
      '<span style="flex:1"></span><button type="button" class="btn primary" id="t-submit">Submit test</button></div>' +
      '<div class="practice-layout"><div id="qwrap"></div><aside class="side"><div class="card"><h3>Questions</h3><div class="palette" id="palette"></div>' +
      '<div class="legend"><span><i class="ans"></i>answered</span><span><i class="mk"></i>marked</span><span><i></i>not visited</span></div></div></aside></div>';
    const qwrap = $('#qwrap');

    function left() { return A.dur - (Date.now() - A.start) / 1000; }
    function updateTimer() {
      const l = left();
      const el = $('#t-left');
      if (!el) return;
      el.textContent = fmtTime(l);
      el.classList.toggle('low', l < 300);
      if (l <= 0) finish(true);
    }
    function renderPalette() {
      $('#palette').innerHTML = A.ids.map((id, i) => {
        let cls = 'pcell';
        if (A.mark[id]) cls += ' mk';
        else if (A.ans[id] != null) cls += ' ans';
        else if (A.seen[id]) cls += ' seen';
        if (i === A.pos) cls += ' cur';
        return '<button type="button" class="' + cls + '" data-i="' + i + '">' + (i + 1) + '</button>';
      }).join('');
      $('#t-prog').textContent = 'Q ' + (A.pos + 1) + ' / ' + A.ids.length + ' · ' + Object.keys(A.ans).length + ' answered';
    }
    function renderQ() {
      const id = A.ids[A.pos];
      const it = BY_ID.get(id);
      A.seen[id] = 1;
      qwrap.innerHTML = '<div class="card qcard"><div class="qhead"><span class="chip">Q ' + (A.pos + 1) + '</span><span class="chip">Ch ' + it.ch + '</span>' +
        (A.mark[id] ? '<span class="chip" style="color:var(--mark)">marked for review</span>' : '') + '</div>' +
        '<div class="qtext">' + rich(it.q) + '</div>' + optionsHTML(it, { sel: A.ans[id], reveal: false, lock: false }) +
        '<div class="qactions"><button type="button" class="btn" id="r-prev"' + (A.pos === 0 ? ' disabled' : '') + '>← Prev</button>' +
        '<button type="button" class="btn" id="r-clear">Clear</button>' +
        '<button type="button" class="btn" id="r-mark">' + (A.mark[id] ? 'Unmark' : 'Mark for review') + '</button>' +
        '<span class="spacer"></span><button type="button" class="btn primary" id="r-next">' + (A.pos === A.ids.length - 1 ? 'Save' : 'Save &amp; next →') + '</button></div>' +
        '<div class="kbd-hint">Keys: <span class="kbd">A</span>–<span class="kbd">D</span> choose · <span class="kbd">←</span>/<span class="kbd">→</span> move · <span class="kbd">M</span> mark</div></div>';
      $$('.opt', qwrap).forEach((b) => b.addEventListener('click', () => choose(+b.dataset.opt)));
      $('#r-prev').addEventListener('click', () => move(-1));
      $('#r-next').addEventListener('click', () => move(1));
      $('#r-clear').addEventListener('click', () => { delete A.ans[id]; save(); renderQ(); renderPalette(); });
      $('#r-mark').addEventListener('click', () => { if (A.mark[id]) delete A.mark[id]; else A.mark[id] = 1; save(); renderQ(); renderPalette(); });
      save();
    }
    function choose(i) {
      const id = A.ids[A.pos];
      A.ans[id] = i; save();
      $$('.opt', qwrap).forEach((b) => { const on = +b.dataset.opt === i; b.classList.toggle('sel', on); b.setAttribute('aria-pressed', on); });
      renderPalette();
    }
    function move(d) {
      const np = A.pos + d;
      if (np < 0 || np >= A.ids.length) { renderPalette(); return; }
      A.pos = np; save(); renderQ(); renderPalette();
    }
    function finish(auto) {
      if (!S.active) return;
      if (!auto) {
        const blank = A.ids.length - Object.keys(A.ans).length;
        if (!window.confirm('Submit the test?' + (blank ? ' ' + blank + ' question(s) are unanswered.' : ''))) return;
      }
      stopTimers();
      let right = 0, wrong = 0;
      A.ids.forEach((id) => {
        const a = A.ans[id];
        if (a == null) return;
        const it = BY_ID.get(id);
        const ok = a === it.ans;
        if (ok) right++; else wrong++;
        const prev = S.att[id];
        S.att[id] = { c: a, ok: ok, t: Date.now(), n: (prev && prev.n ? prev.n : 0) + 1 };
      });
      const cfg = A.cfg;
      const rec = {
        when: Date.now(), ids: A.ids, ans: A.ans, cfg: cfg,
        used: Math.min(A.dur, (Date.now() - A.start) / 1000),
        right: right, wrong: wrong, blank: A.ids.length - right - wrong,
        score: right * cfg.plus - wrong * cfg.minus, max: A.ids.length * cfg.plus,
      };
      S.mocks.push(rec);
      if (S.mocks.length > 40) S.mocks = S.mocks.slice(-40);
      S.active = null;
      save();
      if (auto) toast('Time is up — test submitted');
      go('#/mock/result/' + (S.mocks.length - 1));
    }
    $('#palette').addEventListener('click', (e) => {
      const b = e.target.closest('.pcell');
      if (!b) return;
      A.pos = +b.dataset.i; save(); renderQ(); renderPalette();
    });
    $('#t-submit').addEventListener('click', () => finish(false));
    keyHandler = (e) => {
      const k = e.key.toLowerCase();
      const map = { a: 0, b: 1, c: 2, d: 3, 1: 0, 2: 1, 3: 2, 4: 3 };
      if (k === 'arrowright' || k === 'n') { move(1); e.preventDefault(); }
      else if (k === 'arrowleft' || k === 'p') { move(-1); e.preventDefault(); }
      else if (k === 'm') { $('#r-mark').click(); }
      else if (k in map) { choose(map[k]); }
    };
    renderQ(); renderPalette(); updateTimer();
    tick = setInterval(updateTimer, 1000);
  }

  function mockResult(idx) {
    const m = S.mocks[idx];
    if (!m) { go('#/mock'); return; }
    const answered = m.right + m.wrong;
    let html = '<div class="hero"><div><h1>Mock result</h1><p class="muted">' + new Date(m.when).toLocaleString() + ' · ' + m.ids.length +
      ' questions · +' + m.cfg.plus + ' / −' + m.cfg.minus + '</p></div><div class="btn-row"><a class="btn primary" href="#/mock">New test</a>' +
      '<a class="btn" href="#/practice?status=wrong&reset=1">Practise mistakes</a></div></div>';
    html += '<div class="card"><div class="result-kpis">' +
      '<div><div class="score-big">' + m.score.toFixed(2) + '</div><div class="muted small">of ' + m.max.toFixed(1) + ' marks (' + pct(m.max ? Math.max(0, m.score) / m.max : 0) + ')</div></div>' +
      '<div><div class="kpi"><div class="v" style="color:var(--ok)">' + m.right + '</div><div class="l">Right</div></div></div>' +
      '<div><div class="kpi"><div class="v" style="color:var(--bad)">' + m.wrong + '</div><div class="l">Wrong (−' + (m.wrong * m.cfg.minus).toFixed(2) + ')</div></div></div>' +
      '<div><div class="kpi"><div class="v">' + m.blank + '</div><div class="l">Unanswered</div></div></div>' +
      '<div><div class="kpi"><div class="v">' + pct(answered ? m.right / answered : null) + '</div><div class="l">Accuracy · ' + fmtTime(m.used) + ' used</div></div></div>' +
      '</div></div>';
    // per chapter
    html += '<div class="section-title"><h2>By chapter</h2></div><div class="card scrollx"><table class="t"><thead><tr><th>Chapter</th><th class="num">Qs</th><th class="num">Right</th><th class="num">Wrong</th><th class="num">Blank</th><th class="num">Net marks</th></tr></thead><tbody>';
    CHAPTERS.forEach((c) => {
      const ids = m.ids.filter((id) => BY_ID.get(id).ch === c.num);
      if (!ids.length) return;
      let r = 0, w = 0;
      ids.forEach((id) => { const a = m.ans[id]; if (a == null) return; if (a === BY_ID.get(id).ans) r++; else w++; });
      html += '<tr><td>Ch ' + c.num + ' · ' + esc(c.title) + '</td><td class="num">' + ids.length + '</td><td class="num">' + r + '</td><td class="num">' + w + '</td><td class="num">' +
        (ids.length - r - w) + '</td><td class="num">' + (r * m.cfg.plus - w * m.cfg.minus).toFixed(2) + '</td></tr>';
    });
    html += '</tbody></table></div>';
    html += '<div class="section-title"><h2>Question review</h2><div class="seg" id="rv-filter">' +
      [['all', 'All'], ['wrong', 'Wrong'], ['blank', 'Unanswered'], ['right', 'Right']].map((o, i) =>
        '<label><input type="radio" name="rvf" value="' + o[0] + '"' + (i === 0 ? ' checked' : '') + '><span>' + o[1] + '</span></label>').join('') + '</div></div><div id="rv-list"></div>';
    main.innerHTML = html;
    function list(f) {
      $('#rv-list').innerHTML = m.ids.map((id, i) => ({ id: id, i: i })).filter((o) => {
        const a = m.ans[o.id], it = BY_ID.get(o.id);
        if (f === 'wrong') return a != null && a !== it.ans;
        if (f === 'blank') return a == null;
        if (f === 'right') return a === it.ans;
        return true;
      }).map((o) => {
        const it = BY_ID.get(o.id), a = m.ans[o.id];
        const tag = a == null ? '<span class="chip">—</span>' : a === it.ans ? '<span class="chip ok">✓ right</span>' : '<span class="chip bad">✗ wrong</span>';
        return '<details class="rev" data-id="' + o.id + '" data-i="' + o.i + '"><summary><b>Q' + (o.i + 1) + '</b>' + tag + '<span class="code">' + o.id + '</span><span class="rev-q">' +
          esc(TOPIC.get(it.topic).title) + '</span></summary><div class="rev-body"></div></details>';
      }).join('') || '<div class="card empty">Nothing here.</div>';
    }
    $('#rv-filter').addEventListener('change', (e) => list(e.target.value));
    $('#rv-list').addEventListener('toggle', (e) => {
      const d = e.target;
      if (!d.open || d.dataset.done) return;
      d.dataset.done = '1';
      const a = m.ans[d.dataset.id];
      $('.rev-body', d).innerHTML = staticQuestion(BY_ID.get(d.dataset.id), a == null ? null : a, { num: +d.dataset.i + 1 });
    }, true);
    list('all');
  }

  // ================================================================== SHEETS
  function viewSheets(r) {
    const cur = r.arg && CH.has(+r.arg) ? +r.arg : 0;
    const secs = B.sheets.filter((s) => !cur || s.ch === cur);
    main.innerHTML = '<div class="hero"><div><h1>Formula &amp; shortcut sheets</h1><p>The results each chapter is examined on, condensed for last-day revision. Every problem’s own shortcut is in its solution.</p></div></div>' +
      '<div class="tabs"><a class="tab' + (cur ? '' : ' on') + '" href="#/sheets">All chapters</a>' +
      CHAPTERS.map((c) => '<a class="tab' + (cur === c.num ? ' on' : '') + '" href="#/sheets/' + c.num + '">Ch ' + c.num + '</a>').join('') + '</div>' +
      '<div class="sheet-grid">' + secs.map((s) => '<section class="card sheet"><h3><span class="chip">Ch ' + s.ch + '</span> ' + esc(s.title) + '</h3><div class="sheet-body">' + rich(s.html) + '</div></section>').join('') + '</div>';
  }

  // ================================================================== REVIEW
  function viewReview(r) {
    const tab = r.arg || 'bookmarks';
    const bm = ITEMS.filter((it) => S.bm[it.id]);
    const wrong = ITEMS.filter((it) => S.att[it.id] && !S.att[it.id].ok);
    let html = '<div class="hero"><div><h1>Review</h1><p>Bookmarks and mistakes are stored in this browser only.</p></div></div>' +
      '<div class="tabs"><a class="tab' + (tab === 'bookmarks' ? ' on' : '') + '" href="#/review/bookmarks">Bookmarked (' + bm.length + ')</a>' +
      '<a class="tab' + (tab === 'mistakes' ? ' on' : '') + '" href="#/review/mistakes">Mistakes (' + wrong.length + ')</a>' +
      '<a class="tab' + (tab === 'progress' ? ' on' : '') + '" href="#/review/progress">Progress data</a></div>';
    if (tab === 'progress') {
      const st = stats(ITEMS.map((i) => i.id));
      html += '<div class="card"><h3>Your data</h3><p>' + st.att + ' problems attempted, ' + Object.keys(S.bm).length + ' bookmarks, ' + S.mocks.length + ' mock tests.</p>' +
        '<p class="muted small">Export saves a small JSON file you can import on another device or browser.</p>' +
        '<div class="btn-row"><button type="button" class="btn" id="p-export">Export progress</button>' +
        '<label class="btn">Import progress<input type="file" id="p-import" accept="application/json,.json" class="hidden"></label>' +
        '<button type="button" class="btn danger" id="p-reset">Reset all progress</button></div></div>';
      main.innerHTML = html;
      $('#p-export').addEventListener('click', () => {
        const blob = new Blob([JSON.stringify(S)], { type: 'application/json' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'gk58-iss-progress.json';
        document.body.appendChild(a); a.click(); a.remove();
        setTimeout(() => URL.revokeObjectURL(a.href), 1000);
      });
      $('#p-import').addEventListener('change', (e) => {
        const f = e.target.files && e.target.files[0];
        if (!f) return;
        const rd = new FileReader();
        rd.onload = () => {
          try {
            const d = JSON.parse(rd.result);
            if (!d || typeof d !== 'object' || typeof d.att !== 'object') throw new Error('bad file');
            S = { att: d.att || {}, bm: d.bm || {}, mocks: Array.isArray(d.mocks) ? d.mocks : [], prefs: d.prefs || {}, active: null };
            save(); toast('Progress imported'); render();
          } catch (err) { toast('That file is not a progress export'); }
        };
        rd.readAsText(f);
      });
      $('#p-reset').addEventListener('click', () => {
        if (!window.confirm('Erase all attempts, bookmarks and mock history in this browser?')) return;
        S = { att: {}, bm: {}, mocks: [], prefs: { theme: S.prefs.theme }, active: null };
        save(); toast('Progress reset'); render();
      });
      return;
    }
    const items = tab === 'mistakes' ? wrong : bm;
    const status = tab === 'mistakes' ? 'wrong' : 'bm';
    if (items.length) {
      html += '<div class="btn-row" style="margin-bottom:12px"><a class="btn primary" href="#/practice?status=' + status + '&reset=1">Practise these ' + items.length + '</a></div>';
    }
    html += '<div class="list">' + (items.length ? items.map((it) =>
      '<div class="card list-item">' + qHead(it) + '<div class="qtext">' + rich(it.q) + '</div>' +
      '<div class="btn-row" style="margin-top:8px"><a class="btn" href="#/practice?id=' + it.id + '&status=' + status + '">Open</a></div></div>').join('')
      : '<div class="card empty">' + (tab === 'mistakes' ? 'No mistakes recorded yet.' : 'No bookmarks yet — press ☆ on any problem.') + '</div>') + '</div>';
    main.innerHTML = html;
  }

  // ================================================================== SEARCH
  const HAY = new Map();
  function hay(it) {
    let h = HAY.get(it.id);
    if (!h) {
      const t = TOPIC.get(it.topic);
      h = [it.id, it.q, it.opts.join(' '), it.steps.join(' '), it.sc, it.tr, t.title, t.code, it.type, DIFF[it.diff], 'ch ' + it.ch]
        .join(' ').replace(/\\[a-zA-Z]+/g, ' ').replace(/[{}$^_]/g, ' ').toLowerCase();
      HAY.set(it.id, h);
    }
    return h;
  }
  function viewSearch(r) {
    const q0 = r.params.get('q') || '';
    main.innerHTML = '<div class="hero"><div><h1>Search</h1><p>Words in questions, options, solutions or topic names — e.g. <i>memory</i>, <i>Chebychev</i>, <i>order statistic</i>, <i>6.042</i>.</p></div></div>' +
      '<div class="search-box"><input type="search" id="s-q" placeholder="Search the bank…" value="' + esc(q0) + '" aria-label="Search"></div>' +
      '<p class="muted small" id="s-count"></p><div class="list" id="s-res"></div>';
    const inp = $('#s-q');
    let timer = null;
    function run() {
      const q = inp.value.trim().toLowerCase();
      const words = q.split(/\s+/).filter(Boolean);
      if (!words.length) { $('#s-count').textContent = ''; $('#s-res').innerHTML = ''; return; }
      const res = ITEMS.filter((it) => { const h = hay(it); return words.every((w) => h.indexOf(w) >= 0); });
      $('#s-count').textContent = res.length + ' match' + (res.length === 1 ? '' : 'es') + (res.length > 40 ? ' — showing the first 40' : '');
      $('#s-res').innerHTML = res.slice(0, 40).map((it) => '<div class="card list-item">' + qHead(it) + '<div class="qtext">' + rich(it.q) + '</div>' +
        '<div class="btn-row" style="margin-top:8px"><a class="btn" href="#/practice?id=' + it.id + '&reset=1">Open in practice</a></div></div>').join('');
      history.replaceState(null, '', '#/search?q=' + encodeURIComponent(inp.value.trim()));
    }
    inp.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(run, 200); });
    inp.focus();
    run();
  }

  // ------------------------------------------------------------------ boot
  applyTheme(S.prefs.theme);
  render();
})();
