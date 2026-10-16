// Renders the social card and app icons from build/icons.json with Playwright:
//   og-image.png (1200x630), apple-touch-icon.png (180), icon-192.png, icon-512.png, favicon-32.png, favicon.svg
// Run after `npm run build`: NODE_PATH=$(npm root -g) node scripts/brand.cjs
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const root = path.join(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(root, 'build/icons.json'), 'utf8'));
const by = Object.fromEntries(data.icons.map((i) => [i.name, i]));
const p = (n, w) => { const d = by[n].paths[w]; return Array.isArray(d) ? (d[0] ? `<path d="${d[0]}" opacity=".2"/>` : '') + `<path d="${d[1]}"/>` : `<path d="${d}"/>`; };
const ico = (n, w, s, c) => `<svg viewBox="0 0 256 256" width="${s}" height="${s}" fill="${c}">${p(n, w)}</svg>`;

const gear = by.gear.paths.bold;
const mark = (bg) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><rect width="256" height="256" rx="${bg ? 56 : 0}" fill="${bg || 'none'}"/><g transform="translate(36 36) scale(.72)" fill="#ffffff"><path d="${gear}"/></g></svg>`;
fs.writeFileSync(path.join(root, 'favicon.svg'), `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="#c96a00"><path d="${gear}"/></svg>\n`);

const names = ['house', 'heart', 'camera', 'bell', 'gear', 'rocket', 'cloud-sun', 'music-note', 'chat-circle', 'shopping-cart', 'airplane', 'leaf',
  'lightning', 'globe', 'lock', 'star', 'calendar', 'folder', 'code', 'map-pin', 'coffee', 'trophy', 'palette', 'game-controller'].filter((n) => by[n]);
const weights = ['thin', 'light', 'regular', 'bold', 'fill', 'duotone'];
const tiles = names.map((n, i) => `<div class="t">${ico(n, weights[i % 6], 56, '#1b1e3a')}</div>`).join('');
const og = `<!doctype html><html><head><style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700&family=Figtree:wght@500&display=swap');
body{margin:0;width:1200px;height:630px;background:#f4f5f8;font-family:Figtree,sans-serif;color:#1b1e3a;display:grid;grid-template-columns:560px 1fr;overflow:hidden}
.l{padding:72px 0 0 72px}.e{font:500 20px/1 monospace;letter-spacing:.08em;text-transform:uppercase;color:#c96a00}
h1{font:700 104px/.95 'Bricolage Grotesque',sans-serif;letter-spacing:-.03em;margin:22px 0 22px}
p{font-size:30px;line-height:1.35;color:#5d6280;margin:0}.n{margin-top:40px;font:700 34px 'Bricolage Grotesque';}.n span{color:#c96a00}
.g{display:grid;grid-template-columns:repeat(4,128px);gap:16px;padding:44px 0 0 24px;transform:rotate(-6deg);transform-origin:top left;margin-top:30px}
.t{width:128px;height:128px;background:#fff;border:2px solid #dfe2ec;border-radius:24px;display:grid;place-items:center}
</style></head><body><div class="l"><div class="e">Open source · MIT</div><h1>Icon<br>Monks</h1>
<p>Free icons in six weights for React, Vue, Flutter, iOS, Android and the web.</p>
<div class="n"><span>${data.icons.length}</span> icons · 6 weights</div></div><div class="g">${tiles}</div></body></html>`;

(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1200, height: 630 } });
  await pg.setContent(og, { waitUntil: 'networkidle' });
  await pg.screenshot({ path: path.join(root, 'og-image.png') });
  for (const [file, size, bg] of [['apple-touch-icon.png', 180, '#c96a00'], ['icon-192.png', 192, '#c96a00'], ['icon-512.png', 512, '#c96a00'], ['favicon-32.png', 32, null]]) {
    const q = await b.newPage({ viewport: { width: size, height: size } });
    const svg = bg ? mark(bg).replace('rx="56"', `rx="${bg && file.startsWith('apple') ? 0 : 56}"`) : fs.readFileSync(path.join(root, 'favicon.svg'), 'utf8');
    await q.setContent(`<style>html,body{margin:0;background:transparent}svg{display:block;width:${size}px;height:${size}px}</style>${svg}`);
    await q.screenshot({ path: path.join(root, file), omitBackground: true });
  }
  await b.close();
  console.log('wrote og-image.png, apple-touch-icon.png, icon-192.png, icon-512.png, favicon-32.png, favicon.svg');
})();
