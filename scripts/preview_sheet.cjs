// Used by preview.py: node preview_sheet.cjs data.json out.png
let playwright;
try { playwright = require('playwright'); } catch { playwright = require('/opt/node22/lib/node_modules/playwright'); }
const data = require(require('path').resolve(process.argv[2]));
(async () => {
  const svg = (ic, w, s) => {
    const p = ic.paths[w];
    const inner = w === 'duotone' ? `<path d="${p[0]}" opacity=".2"/><path d="${p[1]}"/>` : `<path d="${p}"/>`;
    return `<svg viewBox="0 0 256 256" width="${s}" height="${s}" fill="#111">${inner}</svg>`;
  };
  const rows = data.icons.map((ic) => `<div class=r><span>${ic.name}</span>` + data.weights.map((w) => svg(ic, w, 48)).join('') +
    svg(ic, 'regular', 24) + svg(ic, 'regular', 16) + '</div>').join('');
  const html = `<style>body{font:11px sans-serif;margin:8px;display:grid;grid-template-columns:repeat(2,1fr);gap:6px 24px;background:#fff}.r{display:flex;align-items:center;gap:10px}.r span{width:130px;overflow-wrap:anywhere}</style>${rows}`;
  const b = await playwright.chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1100, height: 300 } });
  await pg.setContent(html);
  await pg.screenshot({ path: process.argv[3], fullPage: true });
  await b.close();
})();
