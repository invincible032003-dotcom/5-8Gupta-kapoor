/* ======================================================================
   GK.  GUPTA & KAPOOR  —  Chapters 5–8 textbook problem bank
   Injected by ch5-8-dashboard-src/integrate.py; edit it there, not here.
   The bank lives in window.gkData / window.gkMeta and is kept apart from
   the authentic PYQs: it never enters a year, sectional, topic, subtopic
   or custom mock, and the PYQ data audit ignores it.
   ====================================================================== */
var GK = { ch: 0, t: '', diff: 0, pick: {}, open: {} };
var GK_BY_TOPIC = {};
GDATA.forEach(function (q) { (GK_BY_TOPIC[q.gkTopic] = GK_BY_TOPIC[q.gkTopic] || []).push(q); });
var GK_DIFF = ['', 'Foundation', 'Exam-level', 'Elite'];

/* question body shared by every screen: the stem, then (for multiple-
   statement items) the numbered statements and the closing question */
function qBody(q) {
  var h = R(q.question);
  if (q.stmts && q.stmts.length) {
    h += '<ol class="stmts">';
    q.stmts.forEach(function (s) { h += '<li>' + R(s) + '</li>'; });
    h += '</ol>';
    if (q.ask) h += '<div class="ask">' + R(q.ask) + '</div>';
  }
  return h;
}

function gkChapter(num) {
  var out = null;
  (GMETA ? GMETA.chapters : []).forEach(function (c) { if (c.num === +num) out = c; });
  return out;
}

function gkTopic(code) {
  var out = null;
  (GMETA ? GMETA.chapters : []).forEach(function (c) {
    c.topics.forEach(function (t) { if (t.code === code) out = t; });
  });
  return out;
}

function gkRelatedPyqs(tm) {
  return DATA.filter(function (q) {
    return tm.relCodes.indexOf(q.topicCode) >= 0 || tm.relSubs.indexOf(q.subtopic) >= 0;
  });
}

function gkSourceLine(q) {
  return 'Gupta &amp; Kapoor, <i>Fundamentals of Mathematical Statistics</i>, Chapter ' +
    q.gkChapter + ', §' + E(q.gkSection) + ', p. ' + E(q.gkPage) + ' · subtopic ' +
    E(q.gkTopic) + ' ' + E(q.gkTopicTitle);
}

/* reveal order for the textbook bank:
   verdict -> Step-by-Step Solution -> Exam Shortcut -> Tips & Tricks */
function gkRevealPanes(q, chosen, opts) {
  opts = opts || {};
  if (ROUTE.name === 'study') opts.peek = true;     /* study card: show the key, no verdict */
  var h = '';
  var answered = chosen !== null && chosen !== undefined;
  var ok = answered && chosen === q.correctAnswer;
  var cls = !answered ? (opts.peek ? 'verdict-ok' : 'verdict-skip') : (ok ? 'verdict-ok' : 'verdict-bad');
  var verdict = !answered ? (opts.peek ? 'Answer' : 'Not answered') : (ok ? 'Correct' : 'Incorrect');
  h += '<div class="pane ' + cls + '"><div class="hd"><span class="step">1</span>' + E(verdict) +
    '</div><div class="bd">';
  if (!opts.peek) {
    h += '<div class="small"><b>Your answer:</b> ' +
      (answered ? '(' + LET[chosen] + ') ' + R(q.options[chosen])
                : '<span class="muted">not attempted</span>') + '</div>';
  }
  h += '<div class="small' + (opts.peek ? '' : ' mt') + '"><b>Correct answer:</b> (' +
    LET[q.correctAnswer] + ') ' + R(q.options[q.correctAnswer]) + '</div>';
  h += '</div></div>';

  var note = '<div class="ai-note">Gupta &amp; Kapoor practice problem written for this ' +
    'dashboard (not a previous-year question). ' + (q.gkVerified
      ? 'The key is confirmed by an exact or numerical computation.'
      : 'The key is checked by hand against the stated theorem or definition.') + '</div>';

  h += '<div class="pane"><div class="hd"><span class="step">2</span>Step-by-Step Solution</div>' +
    '<div class="bd"><ol>';
  (q.solution || []).forEach(function (s) { h += '<li>' + R(s.text) + '</li>'; });
  h += '</ol></div></div>';

  h += '<div class="pane"><div class="hd"><span class="step">3</span>Exam Shortcut ' +
    '<span class="chip">~30 sec</span></div><div class="bd">' + R(q.examShortcut) + '</div></div>';

  h += '<div class="pane"><div class="hd"><span class="step">4</span>Tips &amp; Tricks</div>' +
    '<div class="bd"><ul>';
  (q.tipsTricks || []).forEach(function (t) { h += '<li>' + R(t) + '</li>'; });
  h += '</ul>' + note + '</div></div>';

  if (opts.topic !== false) {
    var tm = gkTopic(q.gkTopic);
    h += '<div class="pane"><div class="hd">Source &amp; syllabus</div><div class="bd small">' +
      '<p>' + gkSourceLine(q) + '</p>' +
      (tm ? '<p><b>Syllabus.</b> ' + E(tm.unit) + ' › ' + E(tm.topicCode) + ' ' +
        E(tm.pyqTopic) + ' › ' + E(tm.subtopic) + '</p>' : '') + '</div></div>';
  }
  return h;
}

function gkOptionList(q, pick) {
  var done = pick !== undefined && pick !== null;
  var h = '<ul class="opts">';
  for (var i = 0; i < q.options.length; i++) {
    var cls = 'opt';
    if (done) {
      if (i === q.correctAnswer) cls += ' correct';
      else if (i === pick) cls += ' wrong';
    }
    h += '<li><button type="button" class="' + cls + '"' + (done ? ' disabled' : '') +
      ' data-act="gkOpt" data-qid="' + E(q.id) + '" data-i="' + i + '">' +
      '<span class="k">' + LET[i] + '</span><span class="v">' + R(q.options[i]) + '</span></button></li>';
  }
  return h + '</ul>';
}

function gkItem(q, n) {
  var pick = GK.pick.hasOwnProperty(q.id) ? GK.pick[q.id] : null;
  var open = pick !== null || !!GK.open[q.id];
  var h = '<li class="gk-item" id="gk-' + E(q.id.replace(/[^A-Za-z0-9-]/g, '-')) + '">' +
    '<div class="top"><span class="gk-n">' + n + '</span><span class="id">' + E(q.id) + '</span>' +
    '<span class="chip' + (q.difficulty === 'Elite' ? ' mark' : q.difficulty === 'Foundation' ? '' : ' brand') +
    '">' + E(q.difficulty) + '</span>' +
    '<span class="chip">' + E(q.questionType) + '</span>' +
    '<span class="chip">§' + E(q.gkSection) + ' · p. ' + E(q.gkPage) + '</span>' +
    (q.gkVerified ? '<span class="chip ok" title="Answer confirmed by an exact or numerical computation">computed ✓</span>' : '') +
    '</div>' +
    '<div class="qtext">' + qBody(q) + '</div>' + gkOptionList(q, pick) +
    '<div class="btnrow">' +
    (open ? '<button type="button" class="btn sm" data-act="gkHide" data-qid="' + E(q.id) + '">' +
            (pick !== null ? 'Try again' : 'Hide solution') + '</button>'
          : '<button type="button" class="btn sm" data-act="gkShow" data-qid="' + E(q.id) + '">Show solution</button>') +
    bookmarkBtn(q.id) +
    '<button type="button" class="btn sm ghost" data-act="study" data-qid="' + E(q.id) +
    '" data-back="gk">Study card</button></div>';
  if (open) {
    h += '<div class="reveal">' + gkRevealPanes(q, pick, { peek: pick === null, topic: false }) + '</div>';
  }
  return h + '</li>';
}

function gkSheetBlock(b) {
  if (b.t === 'p') return '<p>' + R(b.text) + '</p>';
  if (b.t === 'ul') {
    return '<ul>' + b.items.map(function (x) { return '<li>' + R(x) + '</li>'; }).join('') + '</ul>';
  }
  if (b.t === 'table') {
    var h = '<div class="scrollx"><table class="dt gk-dt">';
    if (b.head && b.head.length) {
      h += '<thead><tr>' + b.head.map(function (c) { return '<th>' + R(c) + '</th>'; }).join('') + '</tr></thead>';
    }
    h += '<tbody>' + b.rows.map(function (r) {
      return '<tr>' + r.map(function (c) { return '<td>' + R(c) + '</td>'; }).join('') + '</tr>';
    }).join('') + '</tbody></table></div>';
    return h;
  }
  return '';
}

function gkSheetView(ch) {
  var sheets = GMETA.sheets.filter(function (s) { return s.ch === ch.num; });
  var h = '<div class="card"><h2>Key results &mdash; Chapter ' + ch.num + '</h2>' +
    '<p class="card-sub">Theorems, remarks and formulas of ' + E(ch.title) + ' that the ' +
    'objective paper draws on, with the one-line shortcuts used in the solutions.</p></div>';
  h += '<div class="grid g2 gk-sheets">';
  sheets.forEach(function (s) {
    h += '<div class="card gk-sheet"><h3>' + E(s.title) + '</h3><div class="sheet-body">' +
      s.blocks.map(gkSheetBlock).join('') + '</div></div>';
  });
  return h + '</div>';
}

function gkTopicView(ch, tm) {
  var qs = GK_BY_TOPIC[tm.code] || [];
  var shown = GK.diff ? qs.filter(function (q) { return q.difficultyLevel === GK.diff; }) : qs;
  var rel = gkRelatedPyqs(tm);
  var h = '<div class="card gk-topic">' +
    '<h2><span class="gk-code">' + E(tm.code) + '</span> ' + E(tm.title) + '</h2>' +
    '<p class="small"><b>Syllabus link:</b> ' + E(tm.unit) + ' › ' + E(tm.topicCode) + ' ' +
    E(tm.pyqTopic) + ' › ' + E(tm.subtopic) + '</p>' +
    '<p class="small muted">“' + E(tm.syllabus) + '”</p>' +
    '<div class="btnrow">' +
    '<button type="button" class="btn primary" data-act="gkPractice" data-scope="topic" data-mode="learn">' +
      'Practise ' + qs.length + ' (Learning)</button>' +
    '<button type="button" class="btn" data-act="gkPractice" data-scope="topic" data-mode="exam">Strict Exam</button>' +
    (rel.length ? '<button type="button" class="btn ghost" data-act="gkPyq">Related PYQs (' + rel.length + ')</button>' : '') +
    '</div>' +
    '<div class="btnrow mt gk-filter">';
  [0, 1, 2, 3].forEach(function (d) {
    var n = d ? qs.filter(function (q) { return q.difficultyLevel === d; }).length : qs.length;
    h += '<button type="button" class="btn sm' + (GK.diff === d ? ' primary' : '') +
      '" data-act="gkDiff" data-d="' + d + '"' + (n ? '' : ' disabled') + '>' +
      (d ? GK_DIFF[d] : 'All') + ' ' + n + '</button>';
  });
  h += '</div></div>';
  if (!shown.length) return h + '<div class="empty">No problems at this level.</div>';
  h += '<ul class="list gk-list">';
  shown.forEach(function (q, i) { h += gkItem(q, i + 1); });
  return h + '</ul>';
}

V.gk = function () {
  var h = crumb(['Home', 'Gupta Kapoor']);
  if (!GMETA || !GDATA.length) {
    return h + '<div class="card"><h1>Gupta Kapoor bank not loaded</h1></div>';
  }
  var ch = gkChapter(GK.ch) || GMETA.chapters[0];
  GK.ch = ch.num;
  var tm = GK.t === 'sheet' ? null : gkTopic(GK.t);
  if (GK.t !== 'sheet' && (!tm || tm.ch !== ch.num)) { tm = ch.topics[0]; GK.t = tm.code; }

  h = crumb(['Home', 'Gupta Kapoor', 'Chapter ' + ch.num, tm ? tm.code + ' ' + tm.title : 'Key results']);
  h += '<div class="card gk-head"><h1>Gupta &amp; Kapoor <span class="gk-badge">CH 5–8 · TEXTBOOK BANK</span></h1>' +
    '<p class="card-sub">' + GMETA.total + ' ISS-standard objective problems built from every theorem, ' +
    'remark, result and formula of ' + E(GMETA.source) + '. Each one opens with the verdict, then the ' +
    'step-by-step solution, the exam shortcut and the tips &amp; tricks.</p>' +
    '<div class="kpis">' +
    '<div class="kpi"><div class="v">' + GMETA.total + '</div><div class="l">Problems</div></div>' +
    '<div class="kpi"><div class="v">' + GMETA.chapters.length + '</div><div class="l">Chapters</div></div>' +
    '<div class="kpi"><div class="v">' + GMETA.nTopics + '</div><div class="l">Subtopics</div></div>' +
    '<div class="kpi ok"><div class="v">' + GMETA.nVerified + '</div><div class="l">Computed keys</div></div>' +
    '</div>' +
    '<div class="banner info mt"><b>Not previous-year questions.</b> ' + E(GMETA.provenance) + '</div></div>';

  h += '<div class="gk-tabs" role="tablist" aria-label="Chapters">';
  GMETA.chapters.forEach(function (c) {
    var on = c.num === ch.num;
    h += '<button type="button" role="tab" aria-selected="' + on + '" class="gk-tab' + (on ? ' on' : '') +
      '" data-act="gkCh" data-ch="' + c.num + '"><b>Chapter ' + c.num + '</b><span>' + E(c.short) +
      '</span><small>' + c.n + ' problems</small></button>';
  });
  h += '</div>';

  h += '<div class="card gk-chap"><div class="gk-chap-hd"><h2>Chapter ' + ch.num + ' · ' + E(ch.title) + '</h2>' +
    '<div class="btnrow">' +
    '<button type="button" class="btn sm" data-act="gkPractice" data-scope="chapter" data-mode="learn">Practise chapter (' + ch.n + ')</button>' +
    '<button type="button" class="btn sm" data-act="gkPractice" data-scope="chapter" data-mode="exam">Chapter mock</button>' +
    '</div></div>' +
    '<div class="gk-subtabs" role="tablist" aria-label="Subtopics">';
  ch.topics.forEach(function (t) {
    var on = tm && t.code === tm.code;
    h += '<button type="button" role="tab" aria-selected="' + on + '" class="gk-sub' + (on ? ' on' : '') +
      '" data-act="gkTopic" data-t="' + E(t.code) + '"><b>' + E(t.code) + '</b> ' + E(t.title) +
      ' <span class="gk-count">' + t.n + '</span></button>';
  });
  h += '<button type="button" role="tab" aria-selected="' + !tm + '" class="gk-sub gk-sheet-tab' + (!tm ? ' on' : '') +
    '" data-act="gkTopic" data-t="sheet"><b>∑</b> Key results &amp; formulas</button>';
  h += '</div></div>';

  h += tm ? gkTopicView(ch, tm) : gkSheetView(ch);
  return h;
};

function gkHomeSection() {
  if (!GMETA || !GDATA.length) return '';
  var h = '<h2 class="mt">Gupta Kapoor · Chapters 5–8 <span class="gk-badge">TEXTBOOK BANK &middot; NOT PYQ</span></h2>';
  h += '<div class="grid g3">';
  GMETA.chapters.forEach(function (c) {
    h += tile('gkGo', { ch: c.num }, 'Chapter ' + c.num + ' · ' + E(c.short),
      E(c.title), c.n + ' problems · ' + c.topics.length + ' subtopics');
  });
  h += tile('gkGo', { ch: GMETA.chapters[0].num, t: 'sheet' }, 'Key results &amp; formula sheets',
    'Theorems, remarks and shortcuts for last-day revision, chapter by chapter.', GMETA.sheets.length + ' sheets');
  h += tile('gkPractice', { scope: 'all', mode: 'exam' }, 'Gupta Kapoor full mock',
    'Every chapter, shuffled, under strict exam conditions.', GMETA.total + ' problems');
  h += '</div>';
  return h;
}

function gkPractice(scope, mode) {
  var qs, label;
  if (scope === 'all') { qs = GDATA.slice(); label = 'Chapters 5–8'; }
  else if (scope === 'chapter') {
    qs = GDATA.filter(function (q) { return q.gkChapter === GK.ch; });
    label = 'Chapter ' + GK.ch;
  } else {
    var tm = gkTopic(GK.t);
    if (!tm) return;
    qs = (GK_BY_TOPIC[tm.code] || []).slice();
    label = tm.code + ' ' + tm.title;
  }
  if (!qs.length) return;
  var st = Store.d().settings;
  var exam = mode === 'exam';
  buildSession({
    kind: 'gk',
    name: 'Gupta Kapoor · ' + label,
    desc: 'GUPTA & KAPOOR TEXTBOOK BANK (not PYQ) · ' + qs.length + ' questions · mode: ' +
          (exam ? 'Strict Exam' : 'Learning'),
    mode: exam ? 'exam' : 'learn',
    questions: qs,
    shuffleQ: exam, shuffleO: false,
    timed: st.timerOn,
    minutes: Math.round(qs.length * st.minutesPerQuestion),
    authentic: false
  });
}

/* delegated clicks for this tab; returns true when handled */
function gkClick(act, t) {
  var qid = t.getAttribute('data-qid');
  switch (act) {
    case 'gkGo':
      GK.ch = +t.getAttribute('data-ch');
      GK.t = t.getAttribute('data-t') || '';
      GK.diff = 0;
      go('gk');
      return true;
    case 'gkCh':
      GK.ch = +t.getAttribute('data-ch'); GK.t = ''; GK.diff = 0;
      render();
      return true;
    case 'gkTopic':
      GK.t = t.getAttribute('data-t'); GK.diff = 0;
      render();
      return true;
    case 'gkDiff': GK.diff = +t.getAttribute('data-d'); render(); return true;
    case 'gkOpt': GK.pick[qid] = +t.getAttribute('data-i'); render(); return true;
    case 'gkShow': GK.open[qid] = true; render(); return true;
    case 'gkHide': delete GK.open[qid]; delete GK.pick[qid]; render(); return true;
    case 'gkPractice':
      if (S && !S.finished && ROUTE.name === 'exam') return true;
      gkPractice(t.getAttribute('data-scope'), t.getAttribute('data-mode'));
      return true;
    case 'gkPyq': {
      var tm = gkTopic(GK.t);
      if (!tm) return true;
      practiceFromIds(gkRelatedPyqs(tm).map(function (q) { return q.id; }),
        'Related PYQs · ' + tm.code + ' ' + tm.title, 'custom');
      return true;
    }
  }
  return false;
}

/* consistency check of the textbook bank, reported on the audit screen */
var GK_AUDIT = (function () {
  var errs = [], ids = {};
  GDATA.forEach(function (q) {
    if (ids[q.id]) errs.push(q.id + ': duplicate id');
    ids[q.id] = 1;
    if (!q.options || q.options.length !== 4) errs.push(q.id + ': needs four options');
    if (!scorable(q) || q.correctAnswer < 0 || q.correctAnswer > 3) errs.push(q.id + ': bad key');
    if (!q.solution || !q.solution.length) errs.push(q.id + ': solution missing');
    if (!q.examShortcut) errs.push(q.id + ': exam shortcut missing');
    if (!q.tipsTricks || q.tipsTricks.length < 3) errs.push(q.id + ': fewer than three tips');
    if (!gkTopic(q.gkTopic)) errs.push(q.id + ': unknown subtopic ' + q.gkTopic);
  });
  return { ok: !errs.length, errors: errs, total: GDATA.length };
})();
