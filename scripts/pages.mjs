// Static SEO pages next to the icon browser, all generated from build/icons.json:
//   icon/<name>/          one page per icon with every weight, downloads and code
//   categories/[<slug>/]  category index and one page per category
//   <platform>-icons/     install and usage guides for each package
//   getting-started/, license/
// Pages share site.css and link to the SVG files GitHub Pages serves from svg/.
import { mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { header, HEADER_CSS, HEADER_JS, HEADER_THEME } from './chrome.mjs';

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const pascal = (n) => n.split('-').map((p) => p[0].toUpperCase() + p.slice(1)).join('');
const camel = (n) => { const p = pascal(n); return p[0].toLowerCase() + p.slice(1); };
// Which main-nav link a page sits under: icon pages under Icons, platform guides under Get started.
const navKey = (path) => path.startsWith('icon/') ? 'icons' : path.startsWith('categories') ? 'categories'
  : path.startsWith('getting-started') || PLATFORMS.some((p) => p.path === path) ? 'start' : '';
const slug = (c) => c.toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const title = (n) => n.split('-').map((p) => p[0].toUpperCase() + p.slice(1)).join(' ');
const svgFile = (name, w) => `svg/${w}/${name}${w === 'regular' ? '' : '-' + w}.svg`;
const ld = (o) => `<script type="application/ld+json">${JSON.stringify({ '@context': 'https://schema.org', ...o }).replace(/</g, '\\u003c')}</script>`;

export function buildPages({ root, data, SITE, REPO, count, version }) {
  const icons = data.icons;
  const byName = Object.fromEntries(icons.map((i) => [i.name, i]));
  const cats = [...new Set(icons.map((i) => i.category))];
  const inCat = Object.fromEntries(cats.map((c) => [c, icons.filter((i) => i.category === c)]));
  const urls = [];

  const write = (path, html) => {
    mkdirSync(new URL(path, root), { recursive: true });
    writeFileSync(new URL(`${path}index.html`, root), html);
    urls.push(SITE + path);
  };

  // depth = how many directories below the site root the page sits, for relative links that work on any host.
  const page = ({ path, depth, title: t, description, h1, lede, crumbs, body, jsonld = [], image }) => {
    const up = '../'.repeat(depth);
    const url = SITE + path;
    const trail = [['Icon Monks', ''], ...crumbs];
    const breadcrumb = { '@type': 'BreadcrumbList', itemListElement: trail.map(([name, p], k) => ({ '@type': 'ListItem', position: k + 1, name, item: SITE + p })) };
    const og = image ? SITE + image : `${SITE}og-image.png`;
    return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(t)}</title>
<meta name="description" content="${esc(description)}">
<link rel="canonical" href="${url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Icon Monks">
<meta property="og:title" content="${esc(t)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:url" content="${url}">
<meta property="og:image" content="${og}">
<meta name="twitter:card" content="${image ? 'summary' : 'summary_large_image'}">
<meta name="twitter:title" content="${esc(t)}">
<meta name="twitter:description" content="${esc(description)}">
<meta name="twitter:image" content="${og}">
<link rel="icon" href="${up}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="${up}apple-touch-icon.png">
${HEADER_THEME}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Funnel+Display:wght@400;500&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="${up}site.css">
${ld({ '@graph': [breadcrumb, ...jsonld] })}
</head>
<body>
${header({ byName, up, REPO, current: navKey(path) })}
<main class="wrap">
  <ol class="crumbs">${trail.map(([name, p], k) => k === trail.length - 1 ? `<li aria-current="page">${esc(name)}</li>` : `<li><a href="${up}${p}">${esc(name)}</a></li>`).join('')}</ol>
  <h1>${h1}</h1>
  ${lede ? `<p class="lede">${lede}</p>` : ''}
  ${body(up)}
</main>
<footer><div class="wrap foot">
  <div><h2>Icon Monks</h2><p>${count} free, open source icons in six weights by Design Monks, released under the MIT license.</p></div>
  <nav aria-label="Popular categories"><h2>Categories</h2><ul>${['Interface', 'Arrows', 'Commerce', 'Media', 'Communication', 'Weather'].map((c) => `<li><a href="${up}categories/${slug(c)}/">${c} icons</a></li>`).join('')}<li><a href="${up}categories/">All categories</a></li></ul></nav>
  <nav aria-label="Platforms"><h2>Platforms</h2><ul>${PLATFORMS.map((p) => `<li><a href="${up}${p.path}">${p.short}</a></li>`).join('')}</ul></nav>
  <nav aria-label="Resources"><h2>Resources</h2><ul><li><a href="${up}getting-started/">Get started</a></li><li><a href="${up}license/">License</a></li><li><a href="${REPO}/releases">Releases</a></li><li><a href="${REPO}/issues">Request an icon</a></li><li><a href="${REPO}">GitHub</a></li></ul></nav>
</div></footer>
${HEADER_JS}
</body>
</html>
`;
  };

  // A category's preview row: popular-looking icons (short names, no slashed variants) instead of the alphabetical first five.
  const preview = (list) => list.filter((i) => !i.name.endsWith('-slash')).sort((a, b) => a.name.length - b.name.length || a.name.localeCompare(b.name)).slice(0, 5);
  const tile = (i, up) => `<li><a href="${up}icon/${i.name}/"><img src="${up}${svgFile(i.name, 'regular')}" alt="${esc(title(i.name))} icon" width="32" height="32" loading="lazy"><span>${i.name}</span></a></li>`;

  // Code samples per platform, matching the snippets in the icon browser.
  const SNIP = {
    React: (n, w) => `import { ${pascal(n)} } from '@icon-monks/react';\n\n<${pascal(n)}${w !== 'regular' ? ` weight="${w}"` : ''} size={24} />`,
    Vue: (n, w) => `<script setup>\nimport { ${pascal(n)} } from '@icon-monks/vue';\n</script>\n\n<${pascal(n)}${w !== 'regular' ? ` weight="${w}"` : ''} :size="24" />`,
    'Web component': (n, w) => `<icon-monks name="${n}"${w !== 'regular' ? ` weight="${w}"` : ''} size="24"></icon-monks>`,
    'Icon font': (n) => `<i class="im im-${n}"></i>`,
    Flutter: (n) => `Icon(IconMonks.${camel(n)})`,
    SwiftUI: (n) => `Image(iconMonks: .${camel(n)})`,
    Compose: (n) => `Icon(IconMonks.Regular.${pascal(n)}, contentDescription = null)`,
  };

  // Icon pages. Clear the folder first so renamed or removed icons leave no stale pages behind.
  rmSync(new URL('icon/', root), { recursive: true, force: true });
  for (const i of icons) {
    const T = title(i.name);
    const tags = i.tags.filter((g) => g !== i.name);
    // Related: same category, ranked by shared name parts and tags, so house-* variants and homes come first.
    const parts = i.name.split('-');
    const related = inCat[i.category].filter((r) => r !== i)
      .map((r) => [r, 3 * r.name.split('-').filter((p) => parts.includes(p)).length + 2 * r.tags.filter((g) => i.tags.includes(g)).length])
      .sort((a, b) => b[1] - a[1]).slice(0, 18).map(([r]) => r);
    const path = `icon/${i.name}/`;
    write(path, page({
      path, depth: 2,
      title: `${T} Icon: Free SVG in 6 Weights | Icon Monks`,
      description: `Free ${T.toLowerCase()} icon in thin, light, regular, bold, fill and duotone. Download SVG or use it in React, Vue, Flutter, SwiftUI and Jetpack Compose. MIT licensed.`,
      h1: `${esc(T)} icon`,
      lede: `A free ${esc(T.toLowerCase())} icon from the ${esc(i.category)} set${tags.length ? `, useful for ${esc(tags.slice(0, 4).join(', '))}` : ''}. It comes in six weights and is free for personal and commercial use under the MIT license.`,
      crumbs: [[`${i.category} icons`, `categories/${slug(i.category)}/`], [T, path]],
      jsonld: [{ '@type': 'ImageObject', name: `${T} icon`, contentUrl: SITE + svgFile(i.name, 'regular'), encodingFormat: 'image/svg+xml',
        license: 'https://opensource.org/licenses/MIT', acquireLicensePage: `${SITE}license/`, creditText: 'Icon Monks', creator: { '@type': 'Organization', name: 'Design Monks' }, copyrightNotice: 'Design Monks' }],
      body: (up) => `
  <section class="weights" aria-label="Weights">
    ${data.weights.map((w) => `<figure><img src="${up}${svgFile(i.name, w)}" alt="${esc(T)} icon, ${w} weight" width="64" height="64"><figcaption>${w[0].toUpperCase() + w.slice(1)}</figcaption><a class="dl" href="${up}${svgFile(i.name, w)}" download>SVG</a></figure>`).join('\n    ')}
  </section>
  <p class="actions"><a class="btn primary" href="${up}?icon=${i.name}">Open in the icon browser</a><span class="hint">Customize size and color, then download PNG, WebP or PDF.</span></p>
  <h2>Use the ${esc(T.toLowerCase())} icon in your code</h2>
  <div class="codes">${Object.entries(SNIP).map(([k, f]) => `<div class="code"><h3>${k}</h3><pre><code>${esc(f(i.name, 'regular'))}</code></pre></div>`).join('')}</div>
  <p>Need setup steps? See the <a href="${up}getting-started/">getting started guide</a> or the page for <a href="${up}react-icons/">React</a>, <a href="${up}flutter-icons/">Flutter</a>, <a href="${up}swiftui-icons/">SwiftUI</a> or <a href="${up}jetpack-compose-icons/">Jetpack Compose</a>.</p>
  ${tags.length ? `<h2>Tags</h2><ul class="tags">${tags.map((g) => `<li><a href="${up}?q=${encodeURIComponent(g)}">${esc(g)}</a></li>`).join('')}</ul>` : ''}
  <h2>Related ${esc(i.category.toLowerCase())} icons</h2>
  <ul class="tiles">${related.map((r) => tile(r, up)).join('')}</ul>
  <p><a href="${up}categories/${slug(i.category)}/">See all ${inCat[i.category].length} ${esc(i.category.toLowerCase())} icons</a></p>`,
    }));
  }

  // Category pages.
  for (const c of cats) {
    const list = inCat[c];
    const path = `categories/${slug(c)}/`;
    const blurb = CATEGORY_BLURBS[c] || `${c.toLowerCase()} interfaces`;
    write(path, page({
      path, depth: 2,
      title: `${list.length} Free ${c} Icons: SVG, React, Flutter & More | Icon Monks`,
      description: `Browse ${list.length} free ${c.toLowerCase()} icons in six weights. Download SVG or install for React, Vue, Flutter, SwiftUI and Jetpack Compose. MIT licensed.`,
      h1: c === 'Brands' ? 'Brand logos' : `${esc(c)} icons`,
      lede: `${list.length} free ${c === 'Brands' ? 'brand logos and products' : esc(c.toLowerCase()) + ' icons'} for ${esc(blurb)}. Every icon comes in thin, light, regular, bold, fill and duotone, drawn on the same 256-unit grid as the rest of Icon Monks.`,
      crumbs: [['Categories', 'categories/'], [`${c} icons`, path]],
      jsonld: [{ '@type': 'CollectionPage', name: `${c} icons`, url: SITE + path, isPartOf: { '@id': `${SITE}#website` },
        mainEntity: { '@type': 'ItemList', numberOfItems: list.length, itemListElement: list.slice(0, 100).map((i, k) => ({ '@type': 'ListItem', position: k + 1, url: `${SITE}icon/${i.name}/`, name: `${title(i.name)} icon` })) } }],
      body: (up) => `
  <p class="actions"><a class="btn primary" href="${up}?category=${encodeURIComponent(c)}">Open in the icon browser</a><span class="hint">Switch weights, change color and download in bulk-friendly formats.</span></p>
  <ul class="tiles">${list.map((i) => tile(i, up)).join('')}</ul>
  <h2>Other categories</h2>
  <ul class="cats">${cats.filter((o) => o !== c).map((o) => `<li><a href="${up}categories/${slug(o)}/">${esc(o)} icons <span>${inCat[o].length}</span></a></li>`).join('')}</ul>`,
    }));
  }
  write('categories/', page({
    path: 'categories/', depth: 1,
    title: `Icon Categories: ${count} Free Icons in ${cats.length} Sets | Icon Monks`,
    description: `Explore ${count} free open source icons grouped into ${cats.length} categories, from interface and arrows to commerce, health, weather and emoji.`,
    h1: 'Icon categories',
    lede: `${count} icons grouped into ${cats.length} categories. Pick a set to see every icon in it, or search them all in the <a href="../">icon browser</a>.`,
    crumbs: [['Categories', 'categories/']],
    body: (up) => `
  <div class="catcards">${cats.slice().sort((a, b) => inCat[b].length - inCat[a].length).map((c) => `<a class="catcard" href="${up}categories/${slug(c)}/"><span class="row">${preview(inCat[c]).map((i) => `<img src="${up}${svgFile(i.name, 'regular')}" alt="" width="28" height="28" loading="lazy">`).join('')}</span><b>${esc(c)} icons</b><span class="n">${inCat[c].length} icons</span></a>`).join('')}</div>`,
  }));

  // Platform guides.
  for (const p of PLATFORMS) {
    write(p.path, page({
      path: p.path, depth: 1,
      title: p.title(count), description: p.description(count),
      h1: p.h1, lede: p.lede(count),
      crumbs: [[p.short, p.path]],
      jsonld: [{ '@type': 'TechArticle', headline: p.h1, description: p.description(count), url: SITE + p.path, author: { '@type': 'Organization', name: 'Design Monks' },
        about: { '@type': 'SoftwareSourceCode', name: p.pkg, codeRepository: REPO, license: 'https://opensource.org/licenses/MIT', programmingLanguage: p.lang, version } },
      faq(p.faq)],
      body: (up) => `
  ${p.sections.map(([h, html]) => `<h2>${h}</h2>${html}`).join('\n  ')}
  <h2>Popular icons</h2>
  <ul class="tiles">${POPULAR.filter((n) => byName[n]).map((n) => tile(byName[n], up)).join('')}</ul>
  <p class="actions"><a class="btn primary" href="${up}">Browse all ${count} icons</a><a class="btn" href="${up}categories/">Browse by category</a></p>
  <h2>Frequently asked questions</h2>
  <div class="faq">${p.faq.map(([q, a]) => `<details><summary><h3>${esc(q)}</h3></summary><p>${a}</p></details>`).join('')}</div>
  <h2>Other platforms</h2>
  <ul class="cats">${PLATFORMS.filter((o) => o !== p).map((o) => `<li><a href="${up}${o.path}">${o.short}</a></li>`).join('')}</ul>`,
    }));
  }

  write('getting-started/', page({
    path: 'getting-started/', depth: 1,
    title: 'Getting Started with Icon Monks: Install Free Icons on Any Platform',
    description: 'Add Icon Monks to a website, React or Vue app, Flutter project, iOS app or Android app in a few steps. Free, open source and MIT licensed.',
    h1: 'Getting started with Icon Monks',
    lede: `Pick the setup that matches your project. Every option uses the same ${count} icons and six weights, so you can mix platforms freely.`,
    crumbs: [['Get started', 'getting-started/']],
    jsonld: [{ '@type': 'HowTo', name: 'Add Icon Monks to a project', step: [
      { '@type': 'HowToStep', name: 'Choose a package', text: 'Pick the package for your platform: React, Vue, Web Components, icon font, SVG, Flutter, SwiftUI or Jetpack Compose.' },
      { '@type': 'HowToStep', name: 'Install it', text: 'Install with npm, flutter pub, Swift Package Manager or Gradle, or link the stylesheet or SVG file directly.' },
      { '@type': 'HowToStep', name: 'Use an icon', text: 'Import the icon by name and set its size, color and weight.' }] }],
    body: (up) => `
  <h2>1. Choose your platform</h2>
  <div class="cards">${PLATFORMS.map((p) => `<a class="card" href="${up}${p.path}"><h3>${p.short}</h3><p>${p.blurb}</p><code>${esc(p.install)}</code></a>`).join('')}</div>
  <h2>2. No build step? Link a file</h2>
  <p>Every icon is served as a standalone SVG, and the icon font ships with a ready-made stylesheet:</p>
  <pre><code>${esc(`<link rel="stylesheet" href="${SITE}packages/font/dist/index.css">\n<i class="im im-house"></i>\n\n<img src="${SITE}svg/bold/heart-bold.svg" alt="" width="24" height="24">`)}</code></pre>
  <h2>3. Pick a weight</h2>
  <p>Thin, light, regular and bold are outlines with 8, 12, 16 and 24-unit strokes on a 256-unit grid. Fill is solid and duotone layers the outline over a 20% tint. Regular is the default; use bold for small sizes and fill for selected states.</p>
  <h2>4. Find icons</h2>
  <p>Search all ${count} icons by name or tag in the <a href="${up}">icon browser</a>, or explore <a href="${up}categories/">${cats.length} categories</a>. Each icon has its own page with every weight, downloads and code for each platform.</p>`,
  }));

  write('license/', page({
    path: 'license/', depth: 1,
    title: 'Icon Monks License: Free Icons for Commercial Use (MIT)',
    description: 'Icon Monks icons are free for personal and commercial projects under the MIT license. See what you can do, what attribution is needed and the full license text.',
    h1: 'License',
    lede: 'Icon Monks is open source under the MIT license. You can use every icon for free in personal, client and commercial work.',
    crumbs: [['License', 'license/']],
    jsonld: [faq(LICENSE_FAQ)],
    body: () => `
  <div class="cards">
    <div class="card"><h3>You can</h3><p>Use the icons in websites, apps, products, templates, presentations, print and merchandise. Modify them, recolor them and redistribute them, including in paid products.</p></div>
    <div class="card"><h3>You don't need to</h3><p>Pay, sign up, or credit Icon Monks in your interface. A mention is always appreciated but never required.</p></div>
    <div class="card"><h3>Please</h3><p>Keep the license file when you redistribute the icon files or packages themselves, for example in an open source project or another icon set.</p></div>
  </div>
  <h2>Frequently asked questions</h2>
  <div class="faq">${LICENSE_FAQ.map(([q, a]) => `<details><summary><h3>${esc(q)}</h3></summary><p>${a}</p></details>`).join('')}</div>
  <h2>Full license text</h2>
  <pre class="license"><code>MIT License

Copyright (c) Design Monks

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.</code></pre>`,
  }));

  writeFileSync(new URL('site.css', root), CSS + HEADER_CSS);
  return { urls, slug, PLATFORMS };
}

const faq = (items) => ({ '@type': 'FAQPage', mainEntity: items.map(([q, a]) => ({ '@type': 'Question', name: q, acceptedAnswer: { '@type': 'Answer', text: a.replace(/<[^>]+>/g, '') } })) });

const POPULAR = ['house', 'magnifying-glass', 'gear', 'user', 'bell', 'heart', 'star', 'envelope', 'shopping-cart', 'calendar', 'trash', 'plus', 'x', 'check', 'arrow-right', 'download', 'lock', 'camera'];

const CATEGORY_BLURBS = {
  Brands: 'sign-in buttons, footers, share menus and integrations',
  Interface: 'buttons, menus, toolbars and app navigation', Design: 'design tools, editors and creative apps', Devices: 'hardware, gadgets and connected devices',
  Arrows: 'navigation, direction, sorting and movement', Media: 'audio, video, playback and streaming controls', Editor: 'text editing, formatting and writing tools',
  Files: 'documents, folders, file types and storage', Commerce: 'shops, carts, payments and checkout flows', Maps: 'locations, navigation and travel apps',
  Objects: 'everyday objects and illustrations', Communication: 'chat, email, calls and notifications', Home: 'household, furniture and smart home apps',
  Development: 'code, terminals, version control and developer tools', People: 'users, avatars, teams and accessibility', Food: 'restaurants, recipes and delivery apps',
  'Letters & Numbers': 'labels, badges, counters and alphabets', Transport: 'vehicles, transit and logistics', Sports: 'fitness, games and sports apps',
  Health: 'medical, wellness and healthcare apps', Science: 'labs, education and research tools', Security: 'locks, privacy, authentication and safety',
  Symbols: 'common signs, shapes and status marks', Time: 'clocks, calendars, timers and scheduling', Nature: 'plants, landscapes and the outdoors',
  Weather: 'forecasts, conditions and climate apps', Business: 'finance, offices and productivity', Emoji: 'reactions, feedback and expressive UI',
  Charts: 'dashboards, analytics and data visualization', Education: 'learning platforms, schools and courses', Animals: 'pets, wildlife and playful interfaces',
};

const code = (t) => `<pre><code>${esc(t)}</code></pre>`;
const SITE_URL = 'https://designmonks.github.io/icon-monks/';

const PLATFORMS = [
  { path: 'react-icons/', short: 'React icons', pkg: '@icon-monks/react', lang: 'TypeScript', install: 'npm i @icon-monks/react',
    blurb: 'Typed, tree-shakeable components with an IconContext for defaults.',
    title: (n) => `React Icons: ${n} Free, Tree-Shakeable SVG Icon Components | Icon Monks`,
    description: (n) => `Install ${n} free React icon components in six weights. Typed, tree-shakeable, with size, color and weight props and an IconContext for defaults. MIT licensed.`,
    h1: 'React icons', lede: (n) => `${n} free icon components for React, each in six weights. Typed for TypeScript, tree-shakeable, and styled with plain props.`,
    sections: [
      ['Install', code('npm install @icon-monks/react')],
      ['Use an icon', code(`import { House, Heart } from '@icon-monks/react';\n\nexport function Nav() {\n  return (\n    <>\n      <House />\n      <Heart size={32} color="crimson" weight="fill" />\n    </>\n  );\n}`)],
      ['Set defaults for a whole tree', code(`import { IconContext, House, Bell } from '@icon-monks/react';\n\n<IconContext.Provider value={{ size: 24, weight: 'duotone' }}>\n  <House /> <Bell />\n</IconContext.Provider>`)],
      ['Props', '<table><tr><th>Prop</th><th>Values</th></tr><tr><td><code>size</code></td><td>Number or CSS length, default <code>1em</code></td></tr><tr><td><code>color</code></td><td>Any CSS color, default <code>currentColor</code></td></tr><tr><td><code>weight</code></td><td><code>thin</code> <code>light</code> <code>regular</code> <code>bold</code> <code>fill</code> <code>duotone</code></td></tr><tr><td><code>mirrored</code></td><td>Flips the icon for right-to-left layouts</td></tr></table><p>Any other SVG attribute, such as <code>aria-label</code> or <code>className</code>, passes through to the <code>&lt;svg&gt;</code>. Every icon is also exported with an <code>Icon</code> suffix (<code>HouseIcon</code>) and as a deep import (<code>@icon-monks/react/icons/House</code>).</p>'],
    ],
    faq: [['Does it work with Next.js and server components?', 'Yes. Icons are plain SVG components with no browser-only code, so they render on the server, in static exports and in client components.'],
      ['Will importing one icon bundle all of them?', 'No. Each icon is its own ES module, so bundlers such as Vite, webpack and Next.js include only the icons you import.'],
      ['Is it typed?', 'Yes. The package ships TypeScript declarations for every component and prop.']] },
  { path: 'vue-icons/', short: 'Vue icons', pkg: '@icon-monks/vue', lang: 'TypeScript', install: 'npm i @icon-monks/vue',
    blurb: 'Vue 3 components with provide/inject defaults.',
    title: (n) => `Vue Icons: ${n} Free Vue 3 Icon Components | Icon Monks`,
    description: (n) => `${n} free Vue 3 icon components in six weights, with size, color and weight props and app-wide defaults through provide/inject. Tree-shakeable and MIT licensed.`,
    h1: 'Vue icons', lede: (n) => `${n} free icon components for Vue 3 and Nuxt, each in six weights, tree-shakeable and fully typed.`,
    sections: [
      ['Install', code('npm install @icon-monks/vue')],
      ['Use an icon', code(`<script setup>\nimport { House, Heart } from '@icon-monks/vue';\n</script>\n\n<template>\n  <House />\n  <Heart :size="32" color="crimson" weight="fill" />\n</template>`)],
      ['Set defaults', code(`<script setup>\nimport { provide } from 'vue';\nimport { IconContextKey } from '@icon-monks/vue';\n\nprovide(IconContextKey, { size: 24, weight: 'bold' });\n</script>`)],
      ['Props', '<p><code>size</code>, <code>color</code>, <code>weight</code> (<code>thin</code>, <code>light</code>, <code>regular</code>, <code>bold</code>, <code>fill</code>, <code>duotone</code>) and <code>mirrored</code>. Other attributes fall through to the <code>&lt;svg&gt;</code>.</p>'],
    ],
    faq: [['Does it work with Nuxt?', 'Yes. The components render on the server and in the browser, so they work in Nuxt pages, layouts and components.'],
      ['Does it support Vue 2?', 'The package targets Vue 3. For Vue 2 projects, use the web component or the SVG files.'],
      ['Is it tree-shakeable?', 'Yes. Each icon is a separate module, so only the icons you import end up in your bundle.']] },
  { path: 'web-components/', short: 'Web components', pkg: '@icon-monks/web', lang: 'JavaScript', install: 'npm i @icon-monks/web',
    blurb: 'An <icon-monks> element for plain HTML, Angular, Svelte, Astro and WordPress.',
    title: (n) => `Icon Web Component: ${n} Free Icons for HTML, Angular & Svelte | Icon Monks`,
    description: (n) => `Use ${n} free icons anywhere with one dependency-free <icon-monks> custom element. Works in plain HTML, Angular, Svelte, Astro and WordPress. MIT licensed.`,
    h1: 'Icons as a web component', lede: (n) => `One dependency-free <code>&lt;icon-monks&gt;</code> element gives any page access to all ${n} icons, with no framework required.`,
    sections: [
      ['Install', code(`npm install @icon-monks/web\n\n// once, anywhere in your app\nimport '@icon-monks/web';`)],
      ['Use an icon', code(`<icon-monks name="house"></icon-monks>\n<icon-monks name="heart" weight="fill" size="32" color="crimson" label="Favorite"></icon-monks>`)],
      ['Attributes', '<p><code>name</code>, <code>weight</code>, <code>size</code>, <code>color</code>, <code>mirrored</code> and <code>label</code>. Icons are hidden from screen readers unless you set <code>label</code>, which becomes the accessible name.</p>'],
    ],
    faq: [['Does it work in Angular?', 'Yes. Add CUSTOM_ELEMENTS_SCHEMA to the module or standalone component that uses it, then use the element in templates.'],
      ['Can I use it in WordPress?', 'Yes. Load the script once in your theme, then use the element in any block that accepts HTML.'],
      ['How big is the script?', 'About 3 KB. Each icon is fetched the first time a page uses it, about 1 KB per icon and weight, and cached. For offline use, import <code>@icon-monks/web/all</code>, which holds every icon up front.']] },
  { path: 'icon-font/', short: 'Icon font', pkg: '@icon-monks/font', lang: 'CSS', install: 'npm i @icon-monks/font',
    blurb: 'OTF and WOFF2 fonts with CSS classes in five weights.',
    title: (n) => `Free Icon Font: ${n} Icons as WOFF2 with CSS Classes | Icon Monks`,
    description: (n) => `Use ${n} free icons as a web font with simple CSS classes. WOFF2 and OTF in thin, light, regular, bold and fill, with stable codepoints. MIT licensed.`,
    h1: 'Icon font', lede: (n) => `All ${n} icons as a web font, in five weights, with one CSS class per icon.`,
    sections: [
      ['Link the stylesheet', code(`<link rel="stylesheet" href="${SITE_URL}packages/font/dist/index.css">`) + '<p>Or install it with <code>npm install @icon-monks/font</code> and import <code>@icon-monks/font/dist/index.css</code>.</p>'],
      ['Use an icon', code(`<i class="im im-house"></i>        <!-- regular -->\n<i class="im-bold im-house"></i>   <!-- also im-thin, im-light, im-fill -->`)],
      ['Load only what you use', '<p>Each weight has its own stylesheet (<code>regular.css</code>, <code>bold.css</code> and so on), so you can skip the weights you don\'t need. Glyphs live in the Private Use Area from U+E000, and codepoints never change between releases.</p>'],
    ],
    faq: [['Is duotone available in the font?', 'No. Fonts are single-color, so duotone is offered in the SVG, React, Vue, web component and native packages instead.'],
      ['Can I size and color the icons with CSS?', 'Yes. Icons follow font-size and color like text.'],
      ['Which formats are included?', 'WOFF2 for the web and OTF for desktop apps and design tools.']] },
  { path: 'svg-icons/', short: 'SVG icons', pkg: '@icon-monks/core', lang: 'JavaScript', install: 'npm i @icon-monks/core',
    blurb: 'Raw SVG files, sprites, metadata and a toSvg() helper.',
    title: (n) => `Free SVG Icons: Download ${n} Open Source SVG Icons | Icon Monks`,
    description: (n) => `Download ${n} free SVG icons in six weights, or use SVG sprites and a toSvg() helper. Single-path, currentColor, MIT licensed and free for commercial use.`,
    h1: 'SVG icons', lede: (n) => `${n} clean, single-path SVG icons in six weights that use currentColor, so they take your text color anywhere.`,
    sections: [
      ['Download or link a file', `<p>Open any icon's page to download it, or link the file directly:</p>` + code(`<img src="${SITE_URL}svg/regular/house.svg" alt="Home" width="24" height="24">`)],
      ['Install the package', code(`npm install @icon-monks/core\n\nimport { toSvg } from '@icon-monks/core';\ndocument.body.innerHTML = toSvg('house', { weight: 'bold', size: 32, color: '#6d28d9' });`)],
      ['Sprites and metadata', '<p>The package also includes one SVG sprite per weight (<code>&lt;use href="sprite/regular.svg#house"/&gt;</code>) and <code>icons.json</code> with names, categories and tags for building your own search.</p>'],
    ],
    faq: [['Are the SVGs optimized?', 'Yes. Each icon is a single flat path on a 256-unit viewBox with no strokes, so it renders the same everywhere and stays small.'],
      ['Can I change the color?', 'Inline SVGs use currentColor and follow your CSS color. For <img> tags, pick a color in the icon browser and download a recolored file.'],
      ['Can I use them in Figma?', 'Yes. Download the SVG or copy the markup from the icon browser and paste it onto your canvas.']] },
  { path: 'flutter-icons/', short: 'Flutter icons', pkg: 'icon_monks', lang: 'Dart', install: 'flutter pub add icon_monks',
    blurb: 'IconData constants backed by bundled fonts.',
    title: (n) => `Flutter Icons: ${n} Free IconData Icons for Flutter Apps | Icon Monks`,
    description: (n) => `Add ${n} free icons to Flutter with the icon_monks package. IconData constants in thin, light, regular, bold and fill that work with the standard Icon widget.`,
    h1: 'Flutter icons', lede: (n) => `${n} free icons for Flutter as <code>IconData</code> constants that work with the standard <code>Icon</code> widget on every platform.`,
    sections: [
      ['Install', code('flutter pub add icon_monks')],
      ['Use an icon', code(`import 'package:icon_monks/icon_monks.dart';\n\nIcon(IconMonks.house)                          // regular\nIcon(IconMonks.bold.heart, color: Colors.red)\nIcon(IconMonks.fill.star, size: 32)`)],
      ['Weights', '<p><code>thin</code>, <code>light</code>, <code>regular</code>, <code>bold</code> and <code>fill</code>. Each weight is a bundled font, so icons scale cleanly and take <code>IconTheme</code> colors.</p>'],
    ],
    faq: [['Does it work on iOS, Android, web and desktop?', 'Yes. The icons are fonts bundled with the package, so they work on every platform Flutter supports.'],
      ['Is duotone available?', 'Not in Flutter, because icon fonts are single-color. Use the SVG files with flutter_svg if you need duotone.'],
      ['Does tree shaking remove unused icons?', 'Yes. Flutter\'s font tree shaking keeps only the glyphs your release build uses.']] },
  { path: 'swiftui-icons/', short: 'SwiftUI icons', pkg: 'IconMonks', lang: 'Swift', install: '.package(url: "https://github.com/designmonks/icon-monks", from: "0.3.0")',
    blurb: 'A Swift package with vector assets for SwiftUI and UIKit.',
    title: (n) => `SwiftUI Icons: ${n} Free Icons for iOS and macOS | Icon Monks`,
    description: (n) => `${n} free icons for SwiftUI and UIKit as a Swift package. Vector assets in six weights with template rendering for iOS, macOS, tvOS and watchOS.`,
    h1: 'SwiftUI and iOS icons', lede: (n) => `${n} free vector icons for SwiftUI and UIKit on iOS, macOS, tvOS and watchOS, in all six weights including duotone.`,
    sections: [
      ['Install', '<p>In Xcode choose File &gt; Add Package Dependencies and enter the repository URL, or add it to <code>Package.swift</code>:</p>' + code('.package(url: "https://github.com/designmonks/icon-monks", from: "0.3.0")')],
      ['Use an icon', code(`import IconMonks\n\nImage(iconMonks: .house)\n    .resizable()\n    .frame(width: 24, height: 24)\n    .foregroundStyle(.purple)\n\nImage(iconMonks: .heart, weight: .fill)\nlet tabIcon = IconMonk.gear.uiImage(.bold)   // UIKit`)],
      ['How it works', '<p>Icons ship as vector assets with preserved vector data and template rendering, so they stay sharp at any size and take the tint color, just like SF Symbols.</p>'],
    ],
    faq: [['Which platforms are supported?', 'iOS, iPadOS, macOS, tvOS and watchOS through Swift Package Manager.'],
      ['Can I use them alongside SF Symbols?', 'Yes. They render as template images, so they follow foregroundStyle and tint the same way.'],
      ['Is duotone included?', 'Yes. All six weights, including duotone, are available.']] },
  { path: 'jetpack-compose-icons/', short: 'Android icons', pkg: 'com.github.designmonks:icon-monks', lang: 'Kotlin', install: 'implementation("com.github.designmonks:icon-monks:v0.3.0")',
    blurb: 'Jetpack Compose ImageVectors and XML VectorDrawables.',
    title: (n) => `Jetpack Compose & Android Icons: ${n} Free ImageVector Icons | Icon Monks`,
    description: (n) => `${n} free Android icons as Jetpack Compose ImageVectors and XML VectorDrawables in six weights. Only the icons you import are compiled into your app.`,
    h1: 'Jetpack Compose and Android icons', lede: (n) => `${n} free icons for Android, as Jetpack Compose <code>ImageVector</code>s and classic XML <code>VectorDrawable</code>s.`,
    sections: [
      ['Install', code(`// settings.gradle.kts\ndependencyResolutionManagement { repositories { google(); mavenCentral(); maven("https://jitpack.io") } }\n\n// app/build.gradle.kts\nimplementation("com.github.designmonks:icon-monks:v0.3.0")`)],
      ['Jetpack Compose', code(`import com.designmonks.icons.IconMonks\nimport com.designmonks.icons.regular.House\nimport com.designmonks.icons.bold.Heart\n\nIcon(IconMonks.Regular.House, contentDescription = "Home")\nIcon(IconMonks.Bold.Heart, contentDescription = null, tint = Color.Red)`)],
      ['Views and XML', code(`<ImageView android:src="@drawable/im_house" app:tint="@color/brand" />\n<ImageView android:src="@drawable/im_heart_fill" />`) + '<p>Drawables use <code>?android:attr/colorControlNormal</code> as their tint, matching Material icons.</p>'],
    ],
    faq: [['Will all icons be added to my APK?', 'No. Each Compose icon is a separate extension property, so only the icons you reference are compiled in, and R8 removes unused drawables.'],
      ['Can I use them with Material 3?', 'Yes. They are standard ImageVectors, so they work with Icon, IconButton, NavigationBar and any Material 3 component.'],
      ['Is there a version for Kotlin Multiplatform?', 'Not yet. The package targets Android; the SVG files work in other Kotlin targets.']] },
];

const LICENSE_FAQ = [
  ['Can I use Icon Monks in commercial projects?', 'Yes. The MIT license allows use in commercial products, client work, paid apps and templates at no cost.'],
  ['Do I have to credit Icon Monks?', 'No credit is needed in your product or interface. If you redistribute the icon files or packages themselves, keep the license notice with them.'],
  ['Can I modify the icons?', 'Yes. You can change their shapes, colors and sizes, and combine them with your own artwork.'],
  ['Can I use the icons in a logo or trademark?', 'You may, but other people can use the same icons too, so an icon on its own is not a distinctive mark. We recommend customizing it.'],
  ['Can I include the icons in an icon pack or UI kit I sell?', 'Yes, as long as the license notice is included with the redistributed icons.'],
];

const CSS = `:root{--paper:#f4f5f8;--sheet:#fff;--ink:#1b1e3a;--muted:#5d6280;--rule:#dfe2ec;--saffron:#c96a00;--fill:#a85600;--on-fill:#fff;--display:'Funnel Display','Space Grotesk','Helvetica Neue',Arial,sans-serif;--body:'DM Sans',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;--mono:'IBM Plex Mono',ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#11132a;--sheet:#191c38;--ink:#e8e9f4;--muted:#a0a4c4;--rule:#2c3058;--saffron:#f5a53a;--fill:#f5a53a;--on-fill:#1b1e3a;color-scheme:dark}:root:not([data-theme="light"]) img[src*="/svg/"]{filter:invert(1) hue-rotate(180deg)}}
:root[data-theme="dark"]{--paper:#11132a;--sheet:#191c38;--ink:#e8e9f4;--muted:#a0a4c4;--rule:#2c3058;--saffron:#f5a53a;--fill:#f5a53a;--on-fill:#1b1e3a;color-scheme:dark}:root[data-theme="dark"] img[src*="/svg/"]{filter:invert(1) hue-rotate(180deg)}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.tiles span{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:2.4em}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 var(--body)}a{color:inherit}
.wrap{max-width:1120px;margin:0 auto;padding:0 16px}
main{padding-block:24px 64px}.crumbs{list-style:none;display:flex;flex-wrap:wrap;gap:6px;padding:0;margin:0 0 20px;font-size:13px;color:var(--muted)}.crumbs li+li::before{content:"/";margin-right:6px}.crumbs a{text-decoration:none}.crumbs a:hover{text-decoration:underline}
h1{font:400 clamp(34px,5vw,56px)/1.05 var(--display);margin:0 0 12px;letter-spacing:-.01em}h2{font:400 28px/1.2 var(--display);margin:48px 0 14px}h3{font:600 16px var(--body);margin:0 0 6px}
.lede{font-size:18px;color:var(--muted);max-width:68ch;margin:0 0 24px}p{max-width:72ch}p a,.faq a{color:var(--saffron)}
pre{margin:0 0 12px;background:var(--sheet);border:1px solid var(--rule);border-radius:10px;padding:14px;overflow-x:auto;font:13px/1.6 var(--mono)}code{font-family:var(--mono);font-size:.92em}
table{border-collapse:collapse;width:100%;max-width:720px;background:var(--sheet);border:1px solid var(--rule);border-radius:10px;overflow:hidden;font-size:14px}th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--rule)}
.btn{display:inline-flex;align-items:center;font:600 14px var(--body);text-decoration:none;border-radius:10px;padding:10px 16px;border:1px solid var(--rule);background:var(--sheet)}.btn.primary{background:var(--fill);border-color:var(--fill);color:var(--on-fill)}
.actions{display:flex;flex-wrap:wrap;gap:10px 14px;align-items:center;max-width:none}.hint{font-size:14px;color:var(--muted)}
.weights{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px;margin:8px 0 20px}.weights figure{margin:0;background:var(--sheet);border:1px solid var(--rule);border-radius:14px;padding:20px 12px 12px;display:grid;justify-items:center;gap:8px}.weights figcaption{font-size:13px;color:var(--muted)}
.dl{font:500 12px var(--mono);color:var(--saffron);text-decoration:none}.dl:hover{text-decoration:underline}
.codes{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}.code{min-width:0}
.tiles{list-style:none;padding:0;margin:0 0 16px;display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px}.tiles a{display:flex;flex-direction:column;align-items:center;gap:10px;padding:18px 6px 10px;background:var(--sheet);border:1px solid transparent;border-radius:12px;text-decoration:none}.tiles a:hover{border-color:var(--saffron)}.tiles span{font:11px/1.2 var(--mono);color:var(--muted);text-align:center;overflow-wrap:anywhere}
.tags{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:6px}.tags a{display:inline-block;font-size:13px;text-decoration:none;border:1px solid var(--rule);border-radius:99px;padding:4px 12px;background:var(--sheet)}
.cats{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:8px}.cats a{display:flex;justify-content:space-between;gap:8px;text-decoration:none;background:var(--sheet);border:1px solid var(--rule);border-radius:10px;padding:10px 12px;font-weight:500}.cats a:hover{border-color:var(--saffron)}.cats span{font:12px var(--mono);color:var(--muted);align-self:center}
.catcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px}.catcard{display:grid;gap:6px;padding:18px;background:var(--sheet);border:1px solid var(--rule);border-radius:14px;text-decoration:none}.catcard:hover{border-color:var(--saffron)}.catcard .row{display:flex;gap:10px;margin-bottom:8px;overflow:hidden}.catcard .n{font-size:13px;color:var(--muted)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}.card{display:grid;gap:6px;align-content:start;padding:18px;background:var(--sheet);border:1px solid var(--rule);border-radius:14px;text-decoration:none;min-width:0}a.card:hover{border-color:var(--saffron)}.card p{margin:0;color:var(--muted);font-size:14px}.card code{font-size:12px;overflow-x:auto;white-space:nowrap;display:block;color:var(--muted)}
.faq{display:grid;gap:8px;max-width:820px}.faq details{background:var(--sheet);border:1px solid var(--rule);border-radius:12px;padding:0 16px}.faq summary{cursor:pointer;padding:14px 0;list-style:none;display:flex;justify-content:space-between;gap:12px}.faq summary::-webkit-details-marker{display:none}.faq summary::after{content:"+";color:var(--saffron);font:500 20px/1 var(--mono)}.faq details[open] summary::after{content:"\\2212"}.faq summary h3{margin:0;font-size:15px}.faq details p{margin:0 0 16px;color:var(--muted)}
.license{white-space:pre-wrap}
a:focus-visible,summary:focus-visible{outline:2px solid var(--saffron);outline-offset:2px}
footer{border-top:1px solid var(--rule);padding-block:32px 40px;color:var(--muted);font-size:13px}.foot{display:grid;grid-template-columns:minmax(0,2fr) repeat(3,minmax(0,1fr));gap:24px}.foot h2{font:500 12px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink);margin:0 0 12px}.foot ul{list-style:none;margin:0;padding:0;display:grid;gap:6px}.foot a{text-decoration:none}.foot a:hover{color:var(--ink);text-decoration:underline}.foot p{margin:0;max-width:46ch}
@media (max-width:720px){.foot{grid-template-columns:repeat(2,minmax(0,1fr))}.foot>div:first-child{grid-column:1/-1}}
`;
