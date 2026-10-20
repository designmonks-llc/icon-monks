// Builds the icon browser from docs/template.html and build/icons.json:
//   index.html           full page served by GitHub Pages (repo root)
//   build/artifact.html  page fragment for the claude.ai preview artifact
//   data/<weight>/<n>.json  path data per weight in shards, fetched by the page (publish next to the artifact)
//   sitemap.xml, robots.txt, site.webmanifest for search engines (brand images come from scripts/brand.cjs)
import { mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { buildPages } from './pages.mjs';
import { header, icon, HEADER_CSS, HEADER_JS, HEADER_THEME, STUDIO, STUDIO_LINK, CREDIT } from './chrome.mjs';

const root = new URL('..', import.meta.url);
const data = JSON.parse(readFileSync(new URL('build/icons.json', root)));
// The browser groups icons under category headings, largest category first, so data is stored in that order.
const catSize = {};
for (const i of data.icons) catSize[i.category] = (catSize[i.category] || 0) + 1;
const ordered = [...data.icons].sort((a, b) => catSize[b.category] - catSize[a.category] || a.category.localeCompare(b.category) || a.name.localeCompare(b.name));
// The page inlines only names, categories and tags; path data goes to data/<weight>/<n>.json in shards, so the
// first screen of icons arrives in one small file and the rest follow in parallel.
const SHARDS = [0, 240];
while (SHARDS[SHARDS.length - 1] < ordered.length) SHARDS.push(Math.min(ordered.length, SHARDS[SHARDS.length - 1] + 1000));
rmSync(new URL('data/', root), { recursive: true, force: true });
for (const w of data.weights) {
  mkdirSync(new URL(`data/${w}/`, root), { recursive: true });
  for (let k = 0; k < SHARDS.length - 1; k++) writeFileSync(new URL(`data/${w}/${k}.json`, root), JSON.stringify(ordered.slice(SHARDS[k], SHARDS[k + 1]).map((i) => i.paths[w])));
}
const meta = {
  weights: data.weights,
  // The homepage specimen steps these icons through all six weights, so their paths ship with the page.
  specimen: { names: ['bell', 'heart', 'rocket', 'cloud-sun'], paths: Object.fromEntries(['bell', 'heart', 'rocket', 'cloud-sun'].map((n) => [n, data.icons.find((i) => i.name === n).paths])) },
  shards: SHARDS,
  icons: ordered.map((i, n) => ({ i: n, name: i.name, category: i.category, tags: i.tags })),
};
const SITE = 'https://designmonks.github.io/icon-monks/';
const REPO = 'https://github.com/designmonks/icon-monks';
// Headline icon count shown across the site and package docs
const count = '70,000+';
const cats = [...new Set(data.icons.map((i) => i.category))];
const esc = (t) => t.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');

// Static sections, rendered at build time so search engines see them without running the icon browser.
const byName = Object.fromEntries(data.icons.map((i) => [i.name, i]));
const draw = (name, w) => {
  const d = byName[name].paths[w];
  const body = w === 'duotone' ? (d[0] ? `<path d="${d[0]}" opacity="0.2"/>` : '') + `<path d="${d[1]}"/>` : `<path d="${d}"/>`;
  return `<svg viewBox="0 0 256 256" width="40" height="40" fill="currentColor" aria-hidden="true">${body}</svg>`;
};
const WEIGHT_NOTES = {
  thin: '8-unit stroke for large, quiet display sizes.',
  light: '12-unit stroke for airy interfaces and marketing pages.',
  regular: 'The 16-unit default, tuned for 24 px UI.',
  bold: '24-unit stroke that holds up at 16 px and on busy screens.',
  fill: 'Solid shapes for selected states and tab bars.',
  duotone: 'An outline over a 20% tint for illustrations and empty states.',
};
const weightsHtml = data.weights.map((w) => `<div class="weight"><div class="weight-row">${['house', 'heart', 'bell', 'camera'].map((i) => draw(i, w)).join('')}</div><h3>${w[0].toUpperCase() + w.slice(1)}</h3><p>${WEIGHT_NOTES[w]}</p></div>`).join('\n    ');
const catCounts = cats.map((c) => [c, data.icons.filter((i) => i.category === c).length]).sort((a, b) => b[1] - a[1]);
const version = JSON.parse(readFileSync(new URL('package.json', root))).version;
const pages = buildPages({ root, data, SITE, REPO, count, version });
const catsHtml = catCounts.map(([c, k]) => `<li><a href="categories/${pages.slug(c)}/">${esc(c)} icons <span>${k}</span></a></li>`).join('\n    ');
const FAQ = [
  ['Is Icon Monks free for commercial projects?',
    'Yes. Every icon is released under the MIT license, so you can use it in personal, client and commercial work, modify it and ship it in paid products. No credit is needed in your interface; keep the license file if you redistribute the source.'],
  ['How many icons are in Icon Monks?',
    `There are ${count} icons in ${cats.length} categories, and each one comes in six weights: thin, light, regular, bold, fill and duotone.`],
  ['Which frameworks and platforms does it support?',
    'There are packages for React, Vue 3, Web Components (plain HTML, Angular, Svelte, Astro, WordPress), an icon font, Flutter, Android (Jetpack Compose and VectorDrawable) and Apple platforms through a Swift package for SwiftUI and UIKit. Raw SVG files work everywhere else.'],
  ['What are the six weights?',
    'Thin, light, regular and bold are outlines with 8, 12, 16 and 24 unit strokes on a 256 unit grid. Fill is a solid version and duotone layers the outline over a soft tint. Every weight shares the same shapes, so you can mix them in one product.'],
  ['Can I change the size and color of the icons?',
    'Yes. Icons draw in currentColor and scale as vectors, so they take the text color and size of their surroundings. The React, Vue and web component packages also accept size, color and weight props.'],
  ['Can I use the icons in Figma, Sketch or Illustrator?',
    'Yes. Pick an icon on this page and download it as SVG or PDF, or copy the SVG markup and paste it straight onto your canvas. PNG and WebP exports go up to 1024 px.'],
  ['Will the packages make my app bigger?',
    'Only by the icons you use. The React and Vue packages export each icon as its own module, so bundlers drop the rest, and the native packages ship vector assets rather than images.'],
  ['Who makes Icon Monks?',
    `Icon Monks is a product of <a href="${STUDIO.url}">Design Monks</a>, a product design studio. We draw the icons for the interfaces we design and release them free under the MIT license.`],
  ['How do I request or contribute an icon?',
    `Open an issue on <a href="${REPO}/issues">GitHub</a> to request one. To contribute, draw a source SVG on the 256 unit grid; the build generates every weight and package from it.`],
];
const faqHtml = FAQ.map(([q, a]) => `<details><summary><h3>${esc(q)}</h3></summary><p>${a}</p></details>`).join('\n    ');

// Shared chrome and inline UI icons: <!--__HEADER_THEME__-->, __HEADER__, /*__HEADER_CSS__*/, <!--__HEADER_JS__-->, __STUDIO__, __CREDIT__ and __ICON:name:size[:weight]__.
const chrome = (html, opts = {}) => html
  .replace('<!--__HEADER_THEME__-->', HEADER_THEME)
  .replace('__HEADER__', header({ byName, REPO, ...opts }))
  .replace('/*__HEADER_CSS__*/', HEADER_CSS)
  .replace('<!--__HEADER_JS__-->', HEADER_JS)
  .replaceAll('__STUDIO__', STUDIO_LINK)
  .replace('__CREDIT__', CREDIT)
  .replace(/__ICON:([a-z0-9-]+):(\d+)(?::([a-z]+))?__/g, (_, n, size, w) => {
    if (!byName[n]) throw new Error(`unknown UI icon: ${n}`);
    return icon(byName, n, +size, w || 'regular');
  });
const page = chrome(readFileSync(new URL('docs/template.html', root), 'utf8'), { current: 'icons' }).replace('/*__ICONS__*/null', JSON.stringify(meta))
  .replace('<b id="stat-icons">0</b>', `<b id="stat-icons">${count}</b>`)
  .replace('<b id="stat-cats">0</b>', `<b id="stat-cats">${cats.length}</b>`)
  .replaceAll('__COUNT__', count)
  .replace('<!--__WEIGHTS__-->', weightsHtml)
  .replace('<!--__CATEGORIES__-->', catsHtml)
  .replace('<!--__FAQ__-->', faqHtml);

const split = page.indexOf('</style>') + '</style>'.length;
const title = `Icon Monks: ${count} Free Icons for Websites, Web Apps & Mobile Apps`;
const description = `${count} free, open source SVG icons in 6 weights, MIT licensed. Download SVG, PNG or PDF, or install for React, Vue, Flutter, SwiftUI and Jetpack Compose.`;
const ld = {
  '@context': 'https://schema.org',
  '@graph': [
    { '@type': 'WebSite', '@id': `${SITE}#website`, name: 'Icon Monks', url: SITE, description, inLanguage: 'en',
      publisher: { '@id': `${SITE}#org` }, creator: { '@id': `${SITE}#org` },
      potentialAction: { '@type': 'SearchAction', target: { '@type': 'EntryPoint', urlTemplate: `${SITE}?q={search_term_string}` }, 'query-input': 'required name=search_term_string' } },
    { '@type': 'Organization', '@id': `${SITE}#org`, name: STUDIO.name, url: STUDIO.url, logo: `${SITE}icon-512.png`, sameAs: ['https://github.com/designmonks', REPO] },
    { '@type': 'FAQPage', '@id': `${SITE}#faq`, mainEntity: FAQ.map(([q, a]) => ({ '@type': 'Question', name: q, acceptedAnswer: { '@type': 'Answer', text: a.replace(/<[^>]+>/g, '') } })) },
    { '@type': 'SoftwareSourceCode', '@id': `${SITE}#code`, name: 'Icon Monks', description, url: SITE,
      codeRepository: REPO, license: 'https://opensource.org/licenses/MIT',
      programmingLanguage: ['TypeScript', 'Dart', 'Kotlin', 'Swift'], version, author: { '@id': `${SITE}#org` },
      keywords: ['icons', 'free icons', 'open source icons', 'icon library', 'svg icons', 'react icons', 'vue icons', 'flutter icons', 'swiftui icons', 'jetpack compose icons', ...cats.map((c) => `${c.toLowerCase()} icons`)].join(', '),
      image: `${SITE}og-image.png` },
  ],
};
const head = `<title>${esc(title)}</title>
<meta name="description" content="${esc(description)}">
<link rel="canonical" href="${SITE}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="Design Monks">
<meta name="publisher" content="Design Monks">
<meta name="keywords" content="free icons, open source icons, svg icons, icon library, react icons, vue icons, flutter icons, swiftui icons, jetpack compose icons, android icons, icon font, figma icons">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Icon Monks">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:url" content="${SITE}">
<meta property="og:image" content="${SITE}og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Icon Monks: ${count} open source icons in six weights, a product of Design Monks">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(title)}">
<meta name="twitter:description" content="${esc(description)}">
<meta name="twitter:image" content="${SITE}og-image.png">
<meta name="twitter:image:alt" content="Icon Monks: ${count} open source icons in six weights, a product of Design Monks">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" href="favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<meta name="theme-color" content="#f4f5f8" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#11132a" media="(prefers-color-scheme: dark)">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<script type="application/ld+json">${JSON.stringify(ld).replace(/</g, '\\u003c')}</script>`;
const noscript = `<noscript><p class="wrap">Icon Monks has ${count} icons in ${cats.length} categories: ${cats.join(', ')}. The icon browser needs JavaScript; every icon is also on <a href="https://github.com/designmonks/icon-monks/tree/main/svg">GitHub as SVG</a>.</p></noscript>`;
const full = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
${head}
${page.slice(0, split).replace(/<title>[^<]*<\/title>\n?/, '')}
</head>
<body>
${noscript}
${page.slice(split)}
</body>
</html>
`;
const today = new Date().toISOString().slice(0, 10);
writeFileSync(new URL('sitemap.xml', root), `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>${SITE}</loc>
    <lastmod>${today}</lastmod>
  </url>
  <url><loc>${SITE}showcase/</loc></url>
${pages.urls.map((u) => `  <url><loc>${u}</loc></url>`).join('\n')}
</urlset>
`);
writeFileSync(new URL('robots.txt', root), `User-agent: *\nAllow: /\n\nSitemap: ${SITE}sitemap.xml\n`);
writeFileSync(new URL('site.webmanifest', root), JSON.stringify({
  name: 'Icon Monks', short_name: 'Icon Monks', description, start_url: './', scope: './', display: 'standalone',
  background_color: '#f4f5f8', theme_color: '#aeacff',
  icons: [{ src: 'icon-192.png', sizes: '192x192', type: 'image/png' }, { src: 'icon-512.png', sizes: '512x512', type: 'image/png' }, { src: 'favicon.svg', sizes: 'any', type: 'image/svg+xml' }],
}, null, 2) + '\n');
writeFileSync(new URL('index.html', root), full);

// Showcase: docs/showcase.html with the path data for just the icons it uses inlined, so the page works on its own.
const showcase = chrome(readFileSync(new URL('docs/showcase.html', root), 'utf8'), { up: '../', current: 'showcase' });
const used = new Set(['plus', ...[...showcase.matchAll(/data-(?:i|tab)="([a-z0-9-]+)"/g)].map((m) => m[1])]);
const pathsByName = Object.fromEntries(data.icons.map((i) => [i.name, i.paths]));
const missingIcons = [...used].filter((n) => !pathsByName[n]);
if (missingIcons.length) throw new Error(`docs/showcase.html uses unknown icons: ${missingIcons.join(', ')}`);
const showcaseIcons = Object.fromEntries([...used].sort().map((n) => [n, pathsByName[n]]));
mkdirSync(new URL('showcase/', root), { recursive: true });
writeFileSync(new URL('showcase/index.html', root), showcase
  .replace('/*ICONS*/', `const ICONS = ${JSON.stringify(showcaseIcons).replace(/</g, '\\u003c')};`)
  .replace('__COUNT__', count));
writeFileSync(new URL('build/artifact.html', root), page);
console.log(`index.html + build/artifact.html: ${data.icons.length} icons; ${pages.urls.length} static pages`);
