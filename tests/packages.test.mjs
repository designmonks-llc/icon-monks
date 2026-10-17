import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { createSSRApp, h, provide } from 'vue';
import { renderToString } from '@vue/server-renderer';

import { icons, toSvg, weights } from '../packages/core/dist/index.js';
import * as React from '../packages/react/dist/index.js';
import * as Vue from '../packages/vue/dist/index.js';

const pascal = (n) => n.split('-').map((p) => p[0].toUpperCase() + p.slice(1)).join('');
const sources = readdirSync(new URL('../icons/', import.meta.url)).filter((f) => f.endsWith('.svg'));

test('every source icon is built in every weight', () => {
  assert.equal(icons.length, sources.length);
  for (const w of weights) {
    for (const { name } of icons) {
      const file = new URL(`../svg/${w}/${name}${w === 'regular' ? '' : '-' + w}.svg`, import.meta.url);
      assert.ok(existsSync(file), `${w}/${name}`);
      assert.match(readFileSync(file, 'utf8'), /<path d="M/);
    }
  }
});

test('core toSvg renders options and escapes titles', () => {
  const svg = toSvg('house', { weight: 'bold', size: 32, color: 'red', title: '<x>', mirrored: true });
  assert.match(svg, /width="32"/);
  assert.match(svg, /fill="red"/);
  assert.match(svg, /scale\(-1, 1\)/);
  assert.match(svg, /<title>&lt;x><\/title>/);
  assert.equal((toSvg('house', { weight: 'duotone' }).match(/<path/g) || []).length, 2);
  assert.throws(() => toSvg('nope'));
});

test('react exports a component per icon, with Icon alias', () => {
  for (const { name } of icons) {
    assert.ok(React[pascal(name)], name);
    assert.equal(React[pascal(name)], React[pascal(name) + 'Icon']);
  }
});

test('react renders props and context', () => {
  const plain = renderToStaticMarkup(createElement(React.House));
  assert.match(plain, /^<svg[^>]*width="1em"[^>]*fill="currentColor"/);
  const ctx = renderToStaticMarkup(createElement(React.IconContext.Provider, { value: { size: 20, weight: 'duotone' } },
    createElement(React.Heart, { color: 'pink', 'aria-label': 'Like' })));
  assert.match(ctx, /width="20"/);
  assert.match(ctx, /fill="pink"/);
  assert.match(ctx, /aria-label="Like"/);
  assert.match(ctx, /opacity="0.2"/);
  const bold = renderToStaticMarkup(createElement(React.Heart, { weight: 'bold' }));
  const regular = renderToStaticMarkup(createElement(React.Heart));
  assert.notEqual(bold, regular);
});

test('vue renders props and injected defaults', async () => {
  const app = createSSRApp({
    setup() {
      provide(Vue.IconContextKey, { size: 18, weight: 'fill' });
      return () => h('div', [h(Vue.House), h(Vue.Star, { color: 'gold', weight: 'thin', size: 40 })]);
    },
  });
  const html = await renderToString(app);
  assert.match(html, /width="18"/);
  assert.match(html, /width="40"[^>]*fill="gold"/);
  assert.equal((html.match(/<svg/g) || []).length, 2);
});

test('font codepoints are stable and unique', () => {
  const cps = JSON.parse(readFileSync(new URL('../codepoints.json', import.meta.url)));
  const values = Object.values(cps);
  assert.equal(new Set(values).size, values.length);
  for (const { name } of icons) assert.ok(cps[name] >= 0xe000, name);
});

// Size budgets: the outlines write round caps and joins as arcs (scripts/build.py, to_d). A build that falls back to
// chains of short curves roughly doubles these numbers and fails here.
test('svg outputs stay within their size budget', () => {
  for (const w of weights) {
    const dir = new URL(`../svg/${w}/`, import.meta.url);
    const sizes = readdirSync(dir).map((f) => readFileSync(new URL(f, dir)).length);
    const avg = sizes.reduce((a, b) => a + b, 0) / sizes.length;
    assert.ok(avg <= (w === 'duotone' ? 1150 : 1000), `${w}: average ${Math.round(avg)} bytes`);
    assert.ok(Math.max(...sizes) <= 6144, `${w}: largest ${Math.max(...sizes)} bytes`);
  }
});
