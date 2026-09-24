// Render every math segment exactly as the dashboard does, but in KaTeX strict
// mode: the vendored KaTeX, the dashboard's own macro table, throwOnError and
// strict:'error' (so even warnings such as Unicode text in math mode fail).
// Prints one line per failure.
const fs = require('fs');
const path = require('path');
const katex = require(path.join(__dirname, 'vendor', 'katex.min.js'));

const html = fs.readFileSync(path.join(__dirname, '..', 'UPSC-ISS-Statistics-Dashboard-STANDALONE.html'), 'utf8');
const m = html.match(/var MACROS = (\{[\s\S]*?\});/);
if (!m) { console.log('MACROS table not found in the dashboard'); process.exit(2); }
const MACROS = new Function('return ' + m[1])();

const segs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
let bad = 0;
for (const s of segs) {
  try {
    // the dashboard trims each formula before typesetting it
    katex.renderToString(s.tex.trim(), {
      displayMode: s.display, throwOnError: true, strict: 'error', trust: false,
      output: 'html', macros: Object.assign({}, MACROS), maxExpand: 2000,
    });
  } catch (e) {
    bad++;
    console.log(`${s.id}: ${e.message.split('\n')[0]} :: ${s.tex.slice(0, 100)}`);
  }
}
process.exit(bad ? 1 : 0);
