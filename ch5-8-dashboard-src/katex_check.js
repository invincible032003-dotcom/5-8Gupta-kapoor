// Render every math segment with the vendored KaTeX; print one line per failure.
const fs = require('fs');
const path = require('path');
const katex = require(path.join(__dirname, 'vendor', 'katex.min.js'));

const segs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
let bad = 0;
for (const s of segs) {
  try {
    katex.renderToString(s.tex, { displayMode: s.display, throwOnError: true, strict: 'ignore' });
  } catch (e) {
    bad++;
    console.log(`${s.id}: ${e.message.split('\n')[0]} :: ${s.tex.slice(0, 100)}`);
  }
}
process.exit(bad ? 1 : 0);
