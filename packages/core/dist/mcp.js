#!/usr/bin/env node
// Icon Monks MCP server: search icons, get SVG and get import code from AI assistants. Zero dependencies.
import { readFileSync } from 'node:fs';
import { createInterface } from 'node:readline';
import { icons, weights, toSvg } from './index.js';

const { version } = JSON.parse(readFileSync(new URL('../package.json', import.meta.url), 'utf8'));
const byName = new Map(icons.map((i) => [i.name, i]));
const pascal = (n) => n.split('-').map((p) => p[0].toUpperCase() + p.slice(1)).join('');
const camel = (n) => { const p = pascal(n); return p[0].toLowerCase() + p.slice(1); };

function search(query, category, limit = 20) {
  const q = String(query || '').toLowerCase().trim();
  const words = q.split(/[\s-]+/).filter(Boolean);
  const scored = [];
  for (const i of icons) {
    if (category && i.category.toLowerCase() !== String(category).toLowerCase()) continue;
    const parts = i.name.split('-');
    const tags = i.tags.map((t) => t.toLowerCase());
    let s = 0;
    if (!q) s = 1;
    else {
      if (i.name === q.replace(/\s+/g, '-')) s += 100;
      for (const w of words) {
        if (parts.includes(w)) s += 20;
        else if (i.name.includes(w)) s += 8;
        if (tags.includes(w) || tags.includes(q)) s += 10;
        else if (tags.some((t) => t.includes(w))) s += 4;
      }
      if (words.length > 1 && !words.every((w) => i.name.includes(w) || tags.some((t) => t.includes(w)))) s = Math.floor(s / 3);
    }
    if (s > 0) scored.push([s, i]);
  }
  scored.sort((a, b) => b[0] - a[0] || a[1].name.length - b[1].name.length || a[1].name.localeCompare(b[1].name));
  return scored.slice(0, Math.max(1, Math.min(100, limit))).map(([, i]) => i);
}

const CODE = {
  react: (n, w) => `import { ${pascal(n)} } from '@icon-monks/react';\n\n<${pascal(n)}${w !== 'regular' ? ` weight="${w}"` : ''} size={24} />`,
  vue: (n, w) => `<script setup>\nimport { ${pascal(n)} } from '@icon-monks/vue';\n</script>\n\n<${pascal(n)}${w !== 'regular' ? ` weight="${w}"` : ''} :size="24" />`,
  html: (n, w) => `<script src="https://cdn.jsdelivr.net/npm/@icon-monks/web@${version}"></script>\n\n<icon-monks name="${n}"${w !== 'regular' ? ` weight="${w}"` : ''} size="24"></icon-monks>`,
  font: (n, w) => w === 'duotone' ? 'Duotone is not in the icon font; use SVG or a component package.' : `<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@icon-monks/font@${version}/dist/index.css">\n\n<i class="${w === 'regular' ? 'im' : 'im-' + w} im-${n}"></i>`,
  flutter: (n, w) => w === 'duotone' ? 'Duotone is not in the Flutter package.' : `// flutter pub add icon_monks\nimport 'package:icon_monks/icon_monks.dart';\n\nIcon(IconMonks.${w === 'regular' ? '' : w + '.'}${camel(n)})`,
  swiftui: (n, w) => `import IconMonks\n\nImage(iconMonks: .${camel(n)}${w !== 'regular' ? `, weight: .${w}` : ''})\n    .resizable()\n    .frame(width: 24, height: 24)`,
  compose: (n, w) => `import com.designmonks.icons.IconMonks\nimport com.designmonks.icons.${w}.${pascal(n)}\n\nIcon(IconMonks.${pascal(w)}.${pascal(n)}, contentDescription = null)`,
  svg: (n, w) => toSvg(n, { weight: w }),
};

const WEIGHT = { type: 'string', enum: weights, description: 'Visual weight. Default regular.' };
const TOOLS = [
  { name: 'search_icons', description: 'Search the Icon Monks library (free, MIT, six weights) by name, concept or tag. Returns icon names with category and tags.',
    inputSchema: { type: 'object', properties: { query: { type: 'string', description: 'What the icon should show, e.g. "settings", "upload file", "credit card".' },
      category: { type: 'string', description: 'Optional category filter, e.g. Interface, Commerce, Arrows. See list_categories.' },
      limit: { type: 'integer', minimum: 1, maximum: 100, description: 'Maximum results. Default 20.' } }, required: ['query'] } },
  { name: 'get_icon_svg', description: 'Get the SVG markup of an Icon Monks icon in any weight, size and color.',
    inputSchema: { type: 'object', properties: { name: { type: 'string', description: 'Icon name from search_icons, e.g. "house".' }, weight: WEIGHT,
      size: { type: 'integer', minimum: 8, maximum: 1024, description: 'Width and height in px. Default 24.' },
      color: { type: 'string', description: 'Fill color. Default currentColor.' } }, required: ['name'] } },
  { name: 'get_icon_code', description: 'Get install-ready code to use an Icon Monks icon in React, Vue, plain HTML, the icon font, Flutter, SwiftUI, Jetpack Compose or inline SVG.',
    inputSchema: { type: 'object', properties: { name: { type: 'string', description: 'Icon name from search_icons.' },
      platform: { type: 'string', enum: Object.keys(CODE), description: 'Where the icon will be used.' }, weight: WEIGHT }, required: ['name', 'platform'] } },
  { name: 'list_categories', description: 'List Icon Monks icon categories with how many icons each has.', inputSchema: { type: 'object', properties: {} } },
];

const text = (t, isError = false) => ({ content: [{ type: 'text', text: t }], ...(isError && { isError: true }) });
function unknown(name) {
  const near = search(String(name || '').replace(/-/g, ' '), null, 5).map((i) => i.name);
  return text(`No icon named "${name}".${near.length ? ` Did you mean: ${near.join(', ')}?` : ''} Use search_icons to find names.`, true);
}
function call(name, a = {}) {
  const w = weights.includes(a.weight) ? a.weight : 'regular';
  switch (name) {
    case 'search_icons': {
      const hits = search(a.query, a.category, a.limit || 20);
      if (!hits.length) return text(`No icons match "${a.query}". Try a simpler word or another synonym.`);
      return text(hits.map((i) => `${i.name} (${i.category}): ${i.tags.join(', ')}`).join('\n') + `\n\nPage for any icon: https://www.iconmonks.co/icon/<name>/`);
    }
    case 'get_icon_svg':
      if (!byName.has(a.name)) return unknown(a.name);
      return text(toSvg(a.name, { weight: w, size: a.size || 24, color: a.color || 'currentColor' }));
    case 'get_icon_code':
      if (!byName.has(a.name)) return unknown(a.name);
      if (!CODE[a.platform]) return text(`Unknown platform "${a.platform}". Use one of: ${Object.keys(CODE).join(', ')}.`, true);
      return text(CODE[a.platform](a.name, w));
    case 'list_categories': {
      const n = {};
      for (const i of icons) n[i.category] = (n[i.category] || 0) + 1;
      return text(Object.entries(n).sort((x, y) => y[1] - x[1]).map(([c, k]) => `${c}: ${k}`).join('\n'));
    }
    default: return null;
  }
}

const send = (msg) => process.stdout.write(JSON.stringify({ jsonrpc: '2.0', ...msg }) + '\n');
createInterface({ input: process.stdin }).on('line', (line) => {
  if (!line.trim()) return;
  let m;
  try { m = JSON.parse(line); } catch { return send({ id: null, error: { code: -32700, message: 'Parse error' } }); }
  const { id, method, params = {} } = m;
  if (id === undefined || id === null) return; // notifications need no reply
  if (method === 'initialize') return send({ id, result: { protocolVersion: params.protocolVersion || '2025-06-18', capabilities: { tools: {} },
    serverInfo: { name: 'icon-monks', version }, instructions: `Icon Monks: ${icons.length} free MIT icons in six weights. Search first, then get SVG or code by name.` } });
  if (method === 'ping') return send({ id, result: {} });
  if (method === 'tools/list') return send({ id, result: { tools: TOOLS } });
  if (method === 'tools/call') {
    const r = call(params.name, params.arguments);
    return r ? send({ id, result: r }) : send({ id, error: { code: -32602, message: `Unknown tool: ${params.name}` } });
  }
  send({ id, error: { code: -32601, message: `Method not found: ${method}` } });
});
