// Builds the icon browser from docs/template.html and build/icons.json:
//   index.html           full page served by GitHub Pages (repo root)
//   build/artifact.html  page fragment for the claude.ai preview artifact
//   data/<weight>.json   path data per weight, fetched by the page (publish next to the artifact)
//   sitemap.xml, robots.txt, site.webmanifest for search engines (brand images come from scripts/brand.cjs)
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';

const root = new URL('..', import.meta.url);
const data = JSON.parse(readFileSync(new URL('build/icons.json', root)));
// The page inlines only names, categories and tags; path data goes to data/<weight>.json, fetched on demand.
mkdirSync(new URL('data/', root), { recursive: true });
for (const w of data.weights) writeFileSync(new URL(`data/${w}.json`, root), JSON.stringify(data.icons.map((i) => i.paths[w])));
const meta = {
  weights: data.weights,
  searchPath: data.icons.find((i) => i.name === 'magnifying-glass').paths.bold,
  icons: data.icons.map((i, n) => ({ i: n, name: i.name, category: i.category, tags: i.tags })),
};
const page = readFileSync(new URL('docs/template.html', root), 'utf8').replace('/*__ICONS__*/null', JSON.stringify(meta))
  .replace('<b id="stat-icons">0</b>', `<b id="stat-icons">${data.icons.length}</b>`);

const split = page.indexOf('</style>') + '</style>'.length;
const SITE = 'https://designmonks.github.io/icon-monks/';
const n = data.icons.length;
const cats = [...new Set(data.icons.map((i) => i.category))];
const title = `Icon Monks: ${n} Free Open Source Icons for React, Vue, Flutter, iOS and Android`;
const description = `${n} free, MIT-licensed icons in six weights (thin, light, regular, bold, fill, duotone). Download SVG, PNG or PDF, or install for React, Vue, Web Components, Flutter, SwiftUI and Jetpack Compose.`;
const esc = (t) => t.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
const ld = {
  '@context': 'https://schema.org',
  '@graph': [
    { '@type': 'WebSite', '@id': `${SITE}#website`, name: 'Icon Monks', url: SITE, description, inLanguage: 'en',
      publisher: { '@id': `${SITE}#org` },
      potentialAction: { '@type': 'SearchAction', target: { '@type': 'EntryPoint', urlTemplate: `${SITE}?q={search_term_string}` }, 'query-input': 'required name=search_term_string' } },
    { '@type': 'Organization', '@id': `${SITE}#org`, name: 'Design Monks', url: 'https://github.com/designmonks', logo: `${SITE}icon-512.png` },
    { '@type': 'SoftwareSourceCode', '@id': `${SITE}#code`, name: 'Icon Monks', description, url: SITE,
      codeRepository: 'https://github.com/designmonks/icon-monks', license: 'https://opensource.org/licenses/MIT',
      programmingLanguage: ['TypeScript', 'Dart', 'Kotlin', 'Swift'], version: JSON.parse(readFileSync(new URL('package.json', root))).version, author: { '@id': `${SITE}#org` },
      keywords: ['icons', 'icon library', 'svg icons', 'react icons', 'vue icons', 'flutter icons', 'swiftui icons', 'jetpack compose icons', ...cats.map((c) => `${c.toLowerCase()} icons`)].join(', '),
      image: `${SITE}og-image.png` },
  ],
};
const head = `<title>${esc(title)}</title>
<meta name="description" content="${esc(description)}">
<link rel="canonical" href="${SITE}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="Design Monks">
<meta name="keywords" content="icons, icon library, open source icons, free icons, svg icons, react icons, vue icons, flutter icons, swiftui icons, jetpack compose icons, icon font">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Icon Monks">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:url" content="${SITE}">
<meta property="og:image" content="${SITE}og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Icon Monks: ${n} open source icons in six weights">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(title)}">
<meta name="twitter:description" content="${esc(description)}">
<meta name="twitter:image" content="${SITE}og-image.png">
<meta name="twitter:image:alt" content="Icon Monks: ${n} open source icons in six weights">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" href="favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<meta name="theme-color" content="#f4f5f8" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#11132a" media="(prefers-color-scheme: dark)">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<script type="application/ld+json">${JSON.stringify(ld).replace(/</g, '\\u003c')}</script>`;
const noscript = `<noscript><p class="wrap">Icon Monks has ${n} icons in ${cats.length} categories: ${cats.join(', ')}. The icon browser needs JavaScript; every icon is also on <a href="https://github.com/designmonks/icon-monks/tree/main/svg">GitHub as SVG</a>.</p></noscript>`;
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
</urlset>
`);
writeFileSync(new URL('robots.txt', root), `User-agent: *\nAllow: /\n\nSitemap: ${SITE}sitemap.xml\n`);
writeFileSync(new URL('site.webmanifest', root), JSON.stringify({
  name: 'Icon Monks', short_name: 'Icon Monks', description, start_url: './', scope: './', display: 'standalone',
  background_color: '#f4f5f8', theme_color: '#c96a00',
  icons: [{ src: 'icon-192.png', sizes: '192x192', type: 'image/png' }, { src: 'icon-512.png', sizes: '512x512', type: 'image/png' }, { src: 'favicon.svg', sizes: 'any', type: 'image/svg+xml' }],
}, null, 2) + '\n');
writeFileSync(new URL('index.html', root), full);
writeFileSync(new URL('build/artifact.html', root), page);
console.log(`index.html + build/artifact.html: ${data.icons.length} icons`);
