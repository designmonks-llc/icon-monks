// Renders the web component, icon fonts and sprite in Chromium and writes a screenshot.
// Usage: node tests/browser.mjs [out.png]   (needs the `playwright` package)
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import http from 'node:http';
import { readFile } from 'node:fs/promises';
import path from 'node:path';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); } catch { playwright = require('/opt/node22/lib/node_modules/playwright'); }
const root = fileURLToPath(new URL('..', import.meta.url));
const types = { '.js': 'text/javascript', '.css': 'text/css', '.woff2': 'font/woff2', '.otf': 'font/otf', '.svg': 'image/svg+xml', '.html': 'text/html' };
const page = `<!doctype html><link rel="stylesheet" href="/packages/font/dist/index.css">
<script src="/packages/web/dist/icon-monks.js"></script>
<style>body{font:14px sans-serif;margin:16px;color:#222} .row{display:flex;gap:12px;align-items:center;margin:8px 0;font-size:32px}</style>
<div class="row" id="wc">${['thin','light','regular','bold','fill','duotone'].map(w => `<icon-monks name="gear" weight="${w}" size="32"></icon-monks>`).join('')}<icon-monks name="heart" weight="fill" size="32" color="crimson" label="Like"></icon-monks></div>
<div class="row" id="font">Text <i class="im-thin im-gear"></i><i class="im-light im-gear"></i><i class="im im-gear"></i><i class="im-bold im-gear"></i><i class="im-fill im-gear"></i> baseline</div>
<div class="row" id="sprite"><svg width="32" height="32"><use href="/packages/core/dist/sprite/regular.svg#house"/></svg><svg width="32" height="32" style="color:teal"><use href="/packages/core/dist/sprite/duotone.svg#house"/></svg></div>`;

const server = http.createServer(async (req, res) => {
  if (req.url === '/') { res.end(page); return; }
  try {
    const file = path.join(root, decodeURIComponent(req.url));
    res.setHeader('content-type', types[path.extname(file)] || 'application/octet-stream');
    res.end(await readFile(file));
  } catch { res.statusCode = 404; res.end(); }
}).listen(0);
const url = `http://localhost:${server.address().port}/`;
const browser = await playwright.chromium.launch();
const p = await browser.newPage({ viewport: { width: 640, height: 220 } });
await p.goto(url);
await p.evaluate(() => document.fonts.ready);
const result = await p.evaluate(() => ({
  wc: [...document.querySelectorAll('icon-monks svg')].length,
  label: document.querySelector('icon-monks[label]').getAttribute('aria-label'),
  fonts: [...document.fonts].filter((f) => f.status === 'loaded').map((f) => f.family),
  glyphWidth: document.querySelector('.im.im-gear').getBoundingClientRect().width,
}));
await p.screenshot({ path: process.argv[2] || 'browser-test.png' });
await browser.close();
server.close();
console.log(JSON.stringify(result));
if (result.wc !== 7 || result.fonts.length < 5 || Math.abs(result.glyphWidth - 32) > 1) process.exit(1);
