// Static SEO pages next to the icon browser, all generated from build/icons.json:
//   icon/<name>/          one page per icon with every weight, downloads and code
//   categories/[<slug>/]  category index and one page per category
//   <platform>-icons/     install and usage guides for each package
//   getting-started/, license/, about/
//   guides/[<slug>/]      how-to articles for questions people ask search and AI engines
// Each page names a social card under og/; scripts/brand.cjs draws them from build/og.json.
// Pages share site.css and link to the SVG files GitHub Pages serves from svg/.
import { mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { header, HEADER_CSS, HEADER_JS, HEADER_THEME, STUDIO, STUDIO_LINK, CREDIT, ABOUT, PRODUCT_SAME_AS, orgLd, founderLd } from './chrome.mjs';

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const pascal = (n) => n.split('-').map((p) => p[0].toUpperCase() + p.slice(1)).join('');
const camel = (n) => { const p = pascal(n); return p[0].toLowerCase() + p.slice(1); };
// Which main-nav link a page sits under: icon pages under Icons, platform guides under Get started.
const navKey = (path) => path.startsWith('icon/') ? 'icons' : path.startsWith('categories') ? 'categories'
  : path.startsWith('getting-started') || PLATFORMS.some((p) => p.path === path) ? 'start'
  : path.startsWith('guides') ? 'guides' : path.startsWith('about') ? 'about' : '';
const slug = (c) => c.toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const title = (n) => n.split('-').map((p) => p[0].toUpperCase() + p.slice(1)).join(' ');
const svgFile = (name, w) => `svg/${w}/${name}${w === 'regular' ? '' : '-' + w}.svg`;
const ld = (o) => `<script type="application/ld+json">${JSON.stringify({ '@context': 'https://schema.org', ...o }).replace(/</g, '\\u003c')}</script>`;

// '2026-10-28' -> '28 October 2026'
const longDate = (d) => new Date(d + 'T00:00:00Z').toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' });

export function buildPages({ root, data, SITE, REPO, count, version, released, unique, files }) {
  // The maker named in structured data on every page.
  const ORG = orgLd(SITE);
  // Social cards for scripts/brand.cjs: og/<name>.png with a title, a line of text and a few icons.
  const cards = [];
  const card = (name, title, sub, icons, kind = 'wide') => { cards.push({ name, title, sub, icons, kind }); return `og/${name}.png`; };
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
  const page = ({ path, depth, title: t, description, h1, lede, crumbs, body, jsonld = [], image, square = false, type = 'website' }) => {
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
<meta name="author" content="Design Monks">
<meta name="publisher" content="Design Monks">
<meta property="og:type" content="${type}">
<meta property="og:site_name" content="Icon Monks">
<meta property="og:title" content="${esc(t)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:url" content="${url}">
<meta property="og:image" content="${og}">
<meta name="twitter:card" content="${square ? 'summary' : 'summary_large_image'}">
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
  ${path === '404.html' ? '' : `<p class="updated">Last updated <time datetime="${released}">${longDate(released)}</time> with version ${version}. <a href="${REPO}/releases">Release notes</a></p>`}
</main>
<footer><div class="wrap foot">
  <div><h2>Icon Monks</h2><p>${count} free, open source icons in six weights by ${STUDIO_LINK}, released under the MIT license.</p></div>
  <nav aria-label="Popular categories"><h2>Categories</h2><ul>${['Interface', 'Arrows', 'Commerce', 'Media', 'Communication', 'Weather'].map((c) => `<li><a href="${up}categories/${slug(c)}/">${c} icons</a></li>`).join('')}<li><a href="${up}categories/">All categories</a></li></ul></nav>
  <nav aria-label="Platforms"><h2>Platforms</h2><ul>${PLATFORMS.map((p) => `<li><a href="${up}${p.path}">${p.short}</a></li>`).join('')}</ul></nav>
  <nav aria-label="Resources"><h2>Resources</h2><ul><li><a href="${up}getting-started/">Get started</a></li><li><a href="${up}guides/">Guides</a></li><li><a href="${up}about/">About</a></li><li><a href="${up}license/">License</a></li><li><a href="${REPO}/releases">Releases</a></li><li><a href="${REPO}/issues">Request an icon</a></li><li><a href="${REPO}">GitHub</a></li></ul></nav>
</div>
<div class="wrap">${CREDIT}</div></footer>
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
    Compose: (n) => `import com.designmonks.icons.IconMonks\nimport com.designmonks.icons.regular.${pascal(n)}\n\nIcon(IconMonks.Regular.${pascal(n)}, contentDescription = null)`,
  };

  // Icon pages. Clear the folder first so renamed or removed icons leave no stale pages behind.
  rmSync(new URL('icon/', root), { recursive: true, force: true });
  // Name parts and tags -> icons, for "similar icons in other categories".
  const words = (i) => new Set([...i.name.split('-'), ...i.tags.flatMap((g) => g.split(/[\s-]+/))].filter((w) => w.length > 2 && !STOP.has(w)));
  const wordsOf = new Map(icons.map((i) => [i, words(i)]));
  const byWord = new Map();
  for (const i of icons) for (const w of wordsOf.get(i)) (byWord.get(w) || byWord.set(w, []).get(w)).push(i);
  const list = (xs) => xs.length < 2 ? xs.join('') : `${xs.slice(0, -1).join(', ')} and ${xs[xs.length - 1]}`;
  for (const i of icons) {
    const T = title(i.name);
    const t = T.toLowerCase();
    const tags = i.tags.filter((g) => g !== i.name);
    // Related: same category, ranked by shared name parts and tags, so house-* variants and homes come first.
    const parts = i.name.split('-');
    const related = inCat[i.category].filter((r) => r !== i)
      .map((r) => [r, 3 * r.name.split('-').filter((p) => parts.includes(p)).length + 2 * r.tags.filter((g) => i.tags.includes(g)).length])
      .sort((a, b) => b[1] - a[1]).slice(0, 18).map(([r]) => r);
    // Similar: other categories, ranked by shared words (rarer words count more).
    const score = new Map();
    for (const w of wordsOf.get(i)) { const hits = byWord.get(w); if (hits.length > 400) continue; for (const r of hits) if (r.category !== i.category) score.set(r, (score.get(r) || 0) + 1 / Math.log2(hits.length + 1)); }
    const similar = [...score].sort((a, b) => b[1] - a[1] || a[0].name.localeCompare(b[0].name)).slice(0, 12).map(([r]) => r);
    const blurb = CATEGORY_BLURBS[i.category] || `${i.category.toLowerCase()} interfaces`;
    const searches = tags.filter((g) => !STOP.has(g)).slice(0, 6);
    const qa = [
      [`Is the ${t} icon free for commercial use?`, `Yes. The ${t} icon is released under the MIT license, so you can use it in personal, client and commercial projects without paying or adding credit in your interface.`],
      [`How do I change the color and size of the ${t} icon?`, `The icon draws in currentColor, so it takes the text color around it. In React, Vue and the web component, set the size and color props; in the icon browser, pick a color and size before you download a PNG, WebP, SVG or PDF.`],
      [`Which weight of the ${t} icon should I use?`, `Use regular at 24 px for most interfaces, bold at 16 px or on busy screens, thin or light for large display sizes, fill for a selected or active state, and duotone for illustrations and empty states.`],
    ];
    const path = `icon/${i.name}/`;
    write(path, page({
      path, depth: 2,
      title: `${T} Icon: Free SVG in 6 Weights | Icon Monks`,
      description: `Free ${t} icon in thin, light, regular, bold, fill and duotone. Download SVG or use it in React, Vue, Flutter, SwiftUI and Jetpack Compose. MIT licensed.`,
      h1: `${esc(T)} icon`,
      lede: `The ${esc(t)} icon is a free ${esc(i.category.toLowerCase())} icon from Icon Monks, drawn as one clean path on a 256-unit grid in six weights. It is free for personal and commercial use under the MIT license.`,
      crumbs: [[`${i.category} icons`, `categories/${slug(i.category)}/`], [T, path]],
      image: card(`icon/${i.name}`, `${T} icon`, '', [i.name], 'square'), square: true,
      jsonld: [{ '@type': 'ImageObject', name: `${T} icon`, contentUrl: SITE + svgFile(i.name, 'regular'), encodingFormat: 'image/svg+xml', dateModified: released,
        license: 'https://opensource.org/licenses/MIT', acquireLicensePage: `${SITE}license/`, creditText: 'Icon Monks', creator: ORG, copyrightNotice: 'Design Monks' }, faq(qa)],
      body: (up) => `
  <section class="weights" aria-label="Weights">
    ${data.weights.map((w) => `<figure><img src="${up}${svgFile(i.name, w)}" alt="${esc(T)} icon, ${w} weight" width="64" height="64"><figcaption>${w[0].toUpperCase() + w.slice(1)}</figcaption><a class="dl" href="${up}${svgFile(i.name, w)}" download>SVG</a></figure>`).join('\n    ')}
  </section>
  <p class="actions"><a class="btn primary" href="${up}?icon=${i.name}">Open in the icon browser</a><span class="hint">Customize size and color, then download PNG, WebP or PDF.</span></p>
  <h2>When to use the ${esc(t)} icon</h2>
  <p>It belongs to the <a href="${up}categories/${slug(i.category)}/">${esc(i.category.toLowerCase())} set</a>, made for ${esc(blurb)}.${searches.length ? ` People find it by searching for ${esc(list(searches.map((g) => `“${g}”`)))}.` : ''} Pair it with the related icons below so a screen stays in one visual style.</p>
  <h2>Use the ${esc(t)} icon in your code</h2>
  <div class="codes">${Object.entries(SNIP).map(([k, f]) => `<div class="code"><h3>${k}</h3><pre><code>${esc(f(i.name, 'regular'))}</code></pre></div>`).join('')}</div>
  <p>Need setup steps? See the <a href="${up}getting-started/">getting started guide</a> or the page for <a href="${up}react-icons/">React</a>, <a href="${up}flutter-icons/">Flutter</a>, <a href="${up}swiftui-icons/">SwiftUI</a> or <a href="${up}jetpack-compose-icons/">Jetpack Compose</a>.</p>
  ${tags.length ? `<h2>Tags</h2><ul class="tags">${tags.map((g) => `<li><a href="${up}?q=${encodeURIComponent(g)}">${esc(g)}</a></li>`).join('')}</ul>` : ''}
  <h2>Related ${esc(i.category.toLowerCase())} icons</h2>
  <ul class="tiles">${related.map((r) => tile(r, up)).join('')}</ul>
  <p><a href="${up}categories/${slug(i.category)}/">See all ${inCat[i.category].length} ${esc(i.category.toLowerCase())} icons</a></p>
  ${similar.length ? `<h2>Similar icons in other categories</h2>
  <ul class="tiles">${similar.map((r) => tile(r, up)).join('')}</ul>` : ''}
  <h2>Questions about the ${esc(t)} icon</h2>
  <div class="faq">${qa.map(([q, a]) => `<details><summary><h3>${esc(q)}</h3></summary><p>${esc(a)}</p></details>`).join('')}</div>`,
    }));
  }

  // Category pages.
  for (const c of cats) {
    const list = inCat[c];
    const path = `categories/${slug(c)}/`;
    const blurb = CATEGORY_BLURBS[c] || `${c.toLowerCase()} interfaces`;
    const noun = c === 'Brands' ? 'brand logos' : `${c.toLowerCase()} icons`;
    const qa = [
      [`Are these ${noun} free?`, `Yes. All ${list.length} ${noun} are free for personal and commercial use under the MIT license, with no sign-up and no credit needed in your interface.${c === 'Brands' ? ' The logos themselves are trademarks of their owners, so follow each brand\'s guidelines.' : ''}`],
      [`How do I use these ${noun} in React, Flutter or iOS?`, `Install the package for your platform and import an icon by name, for example ${pascal(preview(list)[0].name)} in React or IconMonks.${camel(preview(list)[0].name)} in Flutter. Each icon page has copy-ready code for React, Vue, web components, the icon font, Flutter, SwiftUI and Jetpack Compose.`],
      [`Can I download all ${noun} at once?`, `Yes. Every icon is in the svg folder of the GitHub repository, and the @icon-monks/core npm package includes all of them plus one SVG sprite per weight.`],
    ];
    write(path, page({
      path, depth: 2,
      title: `${list.length} Free ${c} Icons: SVG, React, Flutter & More | Icon Monks`,
      description: `Browse ${list.length} free ${c.toLowerCase()} icons in six weights. Download SVG or install for React, Vue, Flutter, SwiftUI and Jetpack Compose. MIT licensed.`,
      h1: c === 'Brands' ? 'Brand logos' : `${esc(c)} icons`,
      lede: `${list.length} free ${c === 'Brands' ? 'brand logos and products' : esc(c.toLowerCase()) + ' icons'} for ${esc(blurb)}. Every icon comes in thin, light, regular, bold, fill and duotone, drawn on the same 256-unit grid as the rest of Icon Monks.`,
      crumbs: [['Categories', 'categories/'], [`${c} icons`, path]],
      image: card(`categories/${slug(c)}`, c === 'Brands' ? 'Brand logos' : `${c} icons`, `${list.length} free icons in six weights`, preview(list).slice(0, 4).map((x) => x.name)),
      jsonld: [faq(qa), { '@type': 'CollectionPage', name: `${c} icons`, url: SITE + path, isPartOf: { '@id': `${SITE}#website` }, dateModified: released,
        mainEntity: { '@type': 'ItemList', numberOfItems: list.length, itemListElement: list.slice(0, 100).map((i, k) => ({ '@type': 'ListItem', position: k + 1, url: `${SITE}icon/${i.name}/`, name: `${title(i.name)} icon` })) } }],
      body: (up) => `
  <p class="actions"><a class="btn primary" href="${up}?category=${encodeURIComponent(c)}">Open in the icon browser</a><span class="hint">Switch weights, change color and download in bulk-friendly formats.</span></p>
  <ul class="tiles">${list.map((i) => tile(i, up)).join('')}</ul>
  <h2>Other categories</h2>
  <ul class="cats">${cats.filter((o) => o !== c).map((o) => `<li><a href="${up}categories/${slug(o)}/">${esc(o)} icons <span>${inCat[o].length}</span></a></li>`).join('')}</ul>
  <h2>Frequently asked questions</h2>
  <div class="faq">${qa.map(([q, a]) => `<details><summary><h3>${esc(q)}</h3></summary><p>${esc(a)}</p></details>`).join('')}</div>`,
    }));
  }
  write('categories/', page({
    path: 'categories/', depth: 1,
    title: `Icon Categories: ${count} Free Icons in ${cats.length} Sets | Icon Monks`,
    description: `Explore ${count} free open source icons grouped into ${cats.length} categories, from interface and arrows to commerce, health, weather and emoji.`,
    h1: 'Icon categories',
    lede: `${count} icons grouped into ${cats.length} categories. Pick a set to see every icon in it, or search them all in the <a href="../">icon browser</a>.`,
    crumbs: [['Categories', 'categories/']],
    image: card('categories', 'Icon categories', `${cats.length} sets, from interface to emoji`, ['squares-four', 'arrow-right', 'shopping-cart', 'cloud-sun']),
    jsonld: [{ '@type': 'CollectionPage', name: 'Icon categories', url: `${SITE}categories/`, isPartOf: { '@id': `${SITE}#website` }, dateModified: released }],
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
      image: card(p.path.replace(/\/$/, ''), p.h1, p.blurb, ['code', 'house', 'heart', 'gear']),
      jsonld: [{ '@type': 'TechArticle', headline: p.h1, description: p.description(count), url: SITE + p.path, author: ORG, publisher: ORG, dateModified: released, image: `${SITE}og/${p.path.replace(/\/$/, '')}.png`,
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
    title: 'Get Started with Icon Monks: Install on Any Platform',
    description: 'Add Icon Monks to a website, React or Vue app, Flutter project, iOS app or Android app in a few steps. Free, open source and MIT licensed.',
    h1: 'Getting started with Icon Monks',
    lede: `Pick the setup that matches your project. Every option uses the same ${count} icons and six weights, so you can mix platforms freely.`,
    crumbs: [['Get started', 'getting-started/']],
    image: card('getting-started', 'Get started', 'Install Icon Monks on any platform', ['rocket', 'code', 'download', 'check']),
    jsonld: [{ '@type': 'HowTo', name: 'Add Icon Monks to a project', dateModified: released, step: [
      { '@type': 'HowToStep', name: 'Choose a package', text: 'Pick the package for your platform: React, Vue, Web Components, icon font, SVG, Flutter, SwiftUI or Jetpack Compose.' },
      { '@type': 'HowToStep', name: 'Install it', text: 'Install with npm, flutter pub, Swift Package Manager or Gradle, or link the stylesheet or SVG file directly.' },
      { '@type': 'HowToStep', name: 'Use an icon', text: 'Import the icon by name and set its size, color and weight.' }] }],
    body: (up) => `
  <h2>1. Choose your platform</h2>
  <div class="cards">${PLATFORMS.map((p) => `<a class="card" href="${up}${p.path}"><h3>${p.short}</h3><p>${esc(p.blurb)}</p><code>${esc(p.card || p.install)}</code></a>`).join('')}</div>
  <h2>2. No build step? Link a file</h2>
  <p>The web component and the icon font load from a CDN, and every icon is also a standalone SVG:</p>
  <pre><code>${esc(`<script src="https://cdn.jsdelivr.net/npm/@icon-monks/web@${VERSION}"></script>\n<icon-monks name="house"></icon-monks>\n\n<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@icon-monks/font@${VERSION}/dist/index.css">\n<i class="im im-house"></i>\n\n<img src="${SITE}svg/bold/heart-bold.svg" alt="" width="24" height="24">`)}</code></pre>
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
    image: card('license', 'MIT license', 'Free for personal and commercial use', ['scales', 'check-circle', 'shield-check', 'code']),
    jsonld: [faq(LICENSE_FAQ)],
    body: () => `
  <h2>What the license allows</h2>
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

  // About: who makes Icon Monks and why, for people and for search and AI engines checking who stands behind it.
  const founder = ABOUT.founder;
  const facts = [
    ['Icons', `${unique} unique icons in ${cats.length} categories`],
    ['Weights', `Six: thin, light, regular, bold, fill and duotone (${files} SVG files)`],
    ['Platforms', 'React, Vue 3, Web Components, icon font, SVG, Flutter, SwiftUI and UIKit, Jetpack Compose and Android XML'],
    ['License', '<a href="../license/">MIT</a>, free for personal and commercial use'],
    ['Current version', `${version}, released ${longDate(released)}`],
    ['Made by', `${STUDIO_LINK}${ABOUT.location ? `, ${esc(ABOUT.location)}` : ''}`],
    ['Source', `<a href="${REPO}">github.com/designmonks-llc/icon-monks</a>`],
    ...(ABOUT.email ? [['Contact', `<a href="mailto:${ABOUT.email}">${ABOUT.email}</a>`]] : []),
  ];
  const elsewhere = [['GitHub', REPO], ['Product Hunt', PRODUCT_SAME_AS[1]], ['npm', PRODUCT_SAME_AS[2]], ['pub.dev', PRODUCT_SAME_AS[3]], ['Facebook', PRODUCT_SAME_AS[4]], ['Design Monks', STUDIO.url]];
  write('about/', page({
    path: 'about/', depth: 1,
    title: 'About Icon Monks: Free Open Source Icons by Design Monks',
    description: `Icon Monks is a free, MIT-licensed icon library by Design Monks: ${unique} icons in six weights with native packages for web, iOS and Android. Who makes it and why.`,
    h1: 'About Icon Monks',
    lede: `Icon Monks is a free, open source icon library made by ${STUDIO_LINK}, a product design studio${founder.name ? ` founded by ${esc(founder.name)}` : ''}. It has ${unique} icons, each drawn in six weights, with native packages for the web, iOS and Android.`,
    crumbs: [['About', 'about/']],
    type: 'profile',
    image: card('about', 'About Icon Monks', 'Free, open source icons by Design Monks', ['users', 'heart', 'palette', 'code']),
    jsonld: [{ '@type': 'AboutPage', '@id': `${SITE}about/#webpage`, url: `${SITE}about/`, name: 'About Icon Monks', isPartOf: { '@id': `${SITE}#website` },
      about: { '@id': `${SITE}#org` }, mainEntity: { '@id': `${SITE}#org` }, dateModified: released,
      speakable: { '@type': 'SpeakableSpecification', cssSelector: ['.lede', '#who p'] } },
      ORG, founderLd(SITE),
      { '@type': 'SoftwareSourceCode', '@id': `${SITE}#code`, name: 'Icon Monks', url: SITE, codeRepository: REPO, license: 'https://opensource.org/licenses/MIT', version, dateModified: released, author: { '@id': `${SITE}#org` }, sameAs: PRODUCT_SAME_AS }],
    body: (up) => `
  <h2>Icon Monks at a glance</h2>
  <table class="facts">${facts.map(([k, v]) => `<tr><th scope="row">${k}</th><td>${v}</td></tr>`).join('')}</table>
  <section id="who">
  <h2>Who makes Icon Monks</h2>
  <p>Icon Monks is designed and maintained by ${STUDIO_LINK}${ABOUT.foundingDate ? `, a product design studio working since ${esc(ABOUT.foundingDate)}` : ', a product design studio'}${ABOUT.location ? ` based in ${esc(ABOUT.location)}` : ''}. ${founder.name ? `The studio was founded by ${esc(founder.name)}${founder.jobTitle ? ` (${esc(founder.jobTitle)})` : ''}, who leads the project.` : ''}</p>
  <p>Design Monks draws these icons for the websites, web apps and mobile apps it designs, and releases the same set for anyone to use.</p>
  </section>
  <h2>How the icons are drawn</h2>
  <p>Every icon starts as one source drawing on a 256-unit grid. The build turns it into six weights with 8, 12, 16 and 24-unit outline strokes plus fill and duotone, then generates every package from the same files, so an icon looks the same in React, Flutter, SwiftUI and Compose. Each icon is a single clean path with no strokes left in the file, tuned to stay sharp at 16 and 24 px. The rules are written up in the <a href="${REPO}/blob/main/STYLE.md">style guide</a>.</p>
  <h2>Why it is free</h2>
  <p>Icons are basic building blocks, and a team should not need a subscription or a legal review to use them. The MIT license lets you use, change and ship the icons in commercial work with no credit needed in your interface.</p>
  <h2>Contact and contributing</h2>
  <p>${ABOUT.email ? `Email <a href="mailto:${ABOUT.email}">${ABOUT.email}</a> for anything about Icon Monks. ` : ''}Request an icon or report a problem in <a href="${REPO}/issues">GitHub issues</a>. To contribute, draw a source SVG on the 256-unit grid and open a pull request; the build makes every weight and package from it.</p>
  <h2>Find Icon Monks elsewhere</h2>
  <ul class="cats">${[...elsewhere, ...ABOUT.studioSameAs.map((u) => [new URL(u).hostname.replace(/^www\./, ''), u]), ...founder.sameAs.map((u) => [`${founder.name} on ${new URL(u).hostname.replace(/^www\./, '').split('.')[0].replace(/^./, (c) => c.toUpperCase()).replace('Linkedin', 'LinkedIn')}`, u])].map(([k, u]) => `<li><a href="${u}" rel="noopener">${esc(k)}</a></li>`).join('')}</ul>`,
  }));

  // Guides: answers to the questions people ask about using icons, each with HowTo or FAQ data.
  for (const g of GUIDES) {
    write(g.path, page({
      path: g.path, depth: 2,
      title: g.title, description: g.description, h1: g.h1, lede: g.lede,
      crumbs: [['Guides', 'guides/'], [g.short, g.path]],
      type: 'article',
      image: card(g.path.replace(/\/$/, ''), g.h1, g.short, g.icons),
      jsonld: [{ '@type': 'TechArticle', headline: g.h1, description: g.description, url: SITE + g.path, image: `${SITE}og/${g.path.replace(/\/$/, '')}.png`,
        datePublished: g.published, dateModified: released, author: founder.name ? { '@id': `${SITE}about/#founder` } : ORG, publisher: ORG, isPartOf: { '@id': `${SITE}#website` } },
      ...(founder.name ? [founderLd(SITE)] : []),
      ...(g.steps ? [{ '@type': 'HowTo', name: g.h1, step: g.steps.map(([name, text]) => ({ '@type': 'HowToStep', name, text })) }] : []),
      faq(g.faq)],
      body: (up) => `
  ${g.steps ? `<h2>Steps</h2><ol class="steps">${g.steps.map(([name, text]) => `<li><b>${esc(name)}.</b> ${esc(text)}</li>`).join('')}</ol>` : ''}
  ${g.sections(up).map(([h, html]) => `<h2>${h}</h2>${html}`).join('\n  ')}
  <h2>Frequently asked questions</h2>
  <div class="faq">${g.faq.map(([q, a]) => `<details><summary><h3>${esc(q)}</h3></summary><p>${a}</p></details>`).join('')}</div>
  <h2>More guides</h2>
  <ul class="cats">${GUIDES.filter((o) => o !== g).map((o) => `<li><a href="${up}${o.path}">${esc(o.short)}</a></li>`).join('')}</ul>
  ${founder.name ? `<p class="byline">Written by ${esc(founder.name)}${founder.jobTitle ? `, ${esc(founder.jobTitle)}` : ''} at ${STUDIO_LINK}. <a href="${up}about/">About Icon Monks</a></p>` : ''}`,
    }));
  }
  write('guides/', page({
    path: 'guides/', depth: 1,
    title: 'Icon Guides: Figma, Color, Size, SVG vs Font and Weights | Icon Monks',
    description: 'Short, practical guides to using icons: Figma and design tools, changing color and size in every framework, SVG vs icon fonts, and choosing an icon weight.',
    h1: 'Guides',
    lede: 'Short, practical answers to the questions designers and developers ask most about icons.',
    crumbs: [['Guides', 'guides/']],
    image: card('guides', 'Icon guides', 'How to use icons well, in every tool', ['book-open', 'figma-logo', 'palette', 'code']),
    jsonld: [{ '@type': 'CollectionPage', name: 'Icon Monks guides', url: `${SITE}guides/`, isPartOf: { '@id': `${SITE}#website` }, dateModified: released,
      mainEntity: { '@type': 'ItemList', itemListElement: GUIDES.map((g, k) => ({ '@type': 'ListItem', position: k + 1, url: SITE + g.path, name: g.h1 })) } }],
    body: (up) => `
  <div class="cards">${GUIDES.map((g) => `<a class="card" href="${up}${g.path}"><h2 class="card-h">${esc(g.h1)}</h2><p>${esc(g.description)}</p></a>`).join('')}</div>`,
  }));

  const notFound = page({
    path: '404.html', depth: 0,
    title: 'Page not found | Icon Monks',
    description: 'This page does not exist. Search the Icon Monks icon browser or pick a platform to get started.',
    h1: 'Page not found',
    lede: `That page doesn't exist, or it moved. All ${count} icons are still a search away.`,
    crumbs: [['Page not found', '404.html']],
    body: (up) => `
  <div class="cards">
    <a class="card" href="${up}"><h3>Search icons</h3><p>Find any icon by name or tag in the icon browser.</p></a>
    <a class="card" href="${up}getting-started/"><h3>Get started</h3><p>Install Icon Monks for your platform.</p></a>
    <a class="card" href="${up}categories/"><h3>Browse categories</h3><p>Explore ${cats.length} categories of icons.</p></a>
  </div>`,
  });
  writeFileSync(new URL('404.html', root), notFound
    .replace('<meta charset="utf-8">', `<meta charset="utf-8">\n<base href="${SITE}">`)
    .replace(/<link rel="canonical"[^>]*>\n/, '')
    .replace('content="index, follow, max-image-preview:large"', 'content="noindex, follow"'));

  writeFileSync(new URL('site.css', root), CSS + HEADER_CSS);
  mkdirSync(new URL('build/', root), { recursive: true });
  writeFileSync(new URL('build/og.json', root), JSON.stringify(cards));
  return { urls, slug, PLATFORMS, GUIDES };
}

const faq = (items) => ({ '@type': 'FAQPage', mainEntity: items.map(([q, a]) => ({ '@type': 'Question', name: q, acceptedAnswer: { '@type': 'Answer', text: a.replace(/<[^>]+>/g, '') } })) });

// Words too common to say two icons are alike.
const STOP = new Set(['and', 'the', 'for', 'with', 'icon', 'icons', 'line', 'simple', 'circle', 'square', 'slash', 'fill', 'outline', 'main', 'new', 'one', 'two', 'three']);

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
const SITE_URL = 'https://www.iconmonks.co/';
const VERSION = JSON.parse(readFileSync(new URL('../package.json', import.meta.url))).version;

const PLATFORMS = [
  { path: 'react-icons/', short: 'React icons', pkg: '@icon-monks/react', lang: 'TypeScript', install: 'npm i @icon-monks/react',
    blurb: 'Typed, tree-shakeable components with an IconContext for defaults.',
    title: (n) => `React Icons: ${n} Free SVG Components | Icon Monks`,
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
    title: (n) => `Web Component Icons: ${n} Free Icons for HTML | Icon Monks`,
    description: (n) => `Use ${n} free icons anywhere with one dependency-free <icon-monks> custom element. Works in plain HTML, Angular, Svelte, Astro and WordPress. MIT licensed.`,
    h1: 'Icons as a web component', lede: (n) => `One dependency-free <code>&lt;icon-monks&gt;</code> element gives any page access to all ${n} icons, with no framework required.`,
    sections: [
      ['Install', '<p>From a CDN, with no build step:</p>' + code(`<script src="https://cdn.jsdelivr.net/npm/@icon-monks/web@${VERSION}"></script>`) + '<p>Or from npm:</p>' + code(`npm install @icon-monks/web\n\n// once, anywhere in your app\nimport '@icon-monks/web';`)],
      ['Use an icon', code(`<icon-monks name="house"></icon-monks>\n<icon-monks name="heart" weight="fill" size="32" color="crimson" label="Favorite"></icon-monks>`)],
      ['Attributes', '<p><code>name</code>, <code>weight</code>, <code>size</code>, <code>color</code>, <code>mirrored</code> and <code>label</code>. Icons are hidden from screen readers unless you set <code>label</code>, which becomes the accessible name.</p>'],
    ],
    faq: [['Does it work in Angular?', 'Yes. Add CUSTOM_ELEMENTS_SCHEMA to the module or standalone component that uses it, then use the element in templates.'],
      ['Can I use it in WordPress?', 'Yes. Load the script once in your theme, then use the element in any block that accepts HTML.'],
      ['How big is the script?', 'About 3 KB. Each icon is fetched the first time a page uses it, about 1 KB per icon and weight, and cached. For offline use, import <code>@icon-monks/web/all</code>, which holds every icon in every weight up front (about 23 MB).']] },
  { path: 'icon-font/', short: 'Icon font', pkg: '@icon-monks/font', lang: 'CSS', install: 'npm i @icon-monks/font',
    blurb: 'OTF and WOFF2 fonts with CSS classes in five weights.',
    title: (n) => `Icon Font: ${n} Free Icons as WOFF2 and CSS | Icon Monks`,
    description: (n) => `Use ${n} free icons as a web font with simple CSS classes. WOFF2 and OTF in thin, light, regular, bold and fill, with stable codepoints. MIT licensed.`,
    h1: 'Icon font', lede: (n) => `All ${n} icons as a web font, in five weights, with one CSS class per icon.`,
    sections: [
      ['Link the stylesheet', code(`<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@icon-monks/font@${VERSION}/dist/index.css">`) + '<p>Or install it with <code>npm install @icon-monks/font</code> and add <code>import \'@icon-monks/font\';</code> to your app.</p>'],
      ['Use an icon', code(`<i class="im im-house"></i>        <!-- regular -->\n<i class="im-bold im-house"></i>   <!-- also im-thin, im-light, im-fill -->`)],
      ['Load only what you use', '<p>Each weight has its own stylesheet (<code>regular.css</code>, <code>bold.css</code> and so on), so you can skip the weights you don\'t need. Glyphs live in the Private Use Area from U+E000, and codepoints never change between releases.</p>'],
    ],
    faq: [['Is duotone available in the font?', 'No. Fonts are single-color, so duotone is offered in the SVG, React, Vue, web component and native packages instead.'],
      ['Can I size and color the icons with CSS?', 'Yes. Icons follow font-size and color like text.'],
      ['Which formats are included?', 'WOFF2 for the web and OTF for desktop apps and design tools.']] },
  { path: 'svg-icons/', short: 'SVG icons', pkg: '@icon-monks/core', lang: 'JavaScript', install: 'npm i @icon-monks/core',
    blurb: 'Raw SVG files, sprites, metadata and a toSvg() helper.',
    title: (n) => `Free SVG Icons: ${n} Open Source Icons | Icon Monks`,
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
    title: (n) => `Flutter Icons: ${n} Free IconData Icons | Icon Monks`,
    description: (n) => `Add ${n} free icons to Flutter with the icon_monks package. IconData constants in thin, light, regular, bold and fill that work with the standard Icon widget.`,
    h1: 'Flutter icons', lede: (n) => `${n} free icons for Flutter as <code>IconData</code> constants that work with the standard <code>Icon</code> widget on every platform.`,
    sections: [
      ['Install', code('flutter pub add icon_monks')],
      ['Use an icon', code(`import 'package:icon_monks/icon_monks.dart';\n\nIcon(IconMonks.house)                          // regular\nIcon(IconMonks.bold.heart, color: Colors.red)\nIcon(IconMonks.fill.star, size: 32)`)],
      ['Weights', '<p><code>thin</code>, <code>light</code>, <code>regular</code>, <code>bold</code> and <code>fill</code>. Each weight is a bundled font, so icons scale cleanly and take <code>IconTheme</code> colors.</p>'],
    ],
    faq: [['Does it work on iOS, Android, web and desktop?', 'Yes. The icons are fonts bundled with the package, so they work on every platform Flutter supports.'],
      ['Is duotone available?', 'Not in Flutter, because icon fonts are single-color. Use the SVG files with flutter_svg if you need duotone.'],
      ['Does tree shaking remove unused icons?', 'For the regular shorthands like <code>IconMonks.house</code>, yes: Flutter keeps only the glyphs your release build uses. Using another weight, like <code>IconMonks.bold.house</code>, bundles that weight\'s whole font (about 1 MB).']] },
  { path: 'swiftui-icons/', short: 'SwiftUI icons', pkg: 'IconMonks', lang: 'Swift', install: `.package(url: "https://github.com/designmonks-llc/icon-monks", from: "${VERSION}")`, card: 'Swift Package Manager',
    blurb: 'A Swift package with vector assets for SwiftUI and UIKit.',
    title: (n) => `SwiftUI Icons: ${n} Free Icons for iOS and macOS | Icon Monks`,
    description: (n) => `${n} free icons for SwiftUI and UIKit as a Swift package. Vector assets in six weights with template rendering for iOS, macOS, tvOS and watchOS.`,
    h1: 'SwiftUI and iOS icons', lede: (n) => `${n} free vector icons for SwiftUI and UIKit on iOS, macOS, tvOS and watchOS, in all six weights including duotone.`,
    sections: [
      ['Install', '<p>In Xcode choose File &gt; Add Package Dependencies and enter the repository URL, or add it to <code>Package.swift</code>:</p>' + code(`.package(url: "https://github.com/designmonks-llc/icon-monks", from: "${VERSION}")`)],
      ['Use an icon', code(`import IconMonks\n\nImage(iconMonks: .house)\n    .resizable()\n    .frame(width: 24, height: 24)\n    .foregroundStyle(.purple)   // iOS 15+; .foregroundColor on iOS 14\n\nImage(iconMonks: .heart, weight: .fill)\nlet tabIcon = IconMonk.gear.uiImage(.bold)   // UIKit`)],
      ['How it works', '<p>Icons ship as vector assets with preserved vector data and template rendering, so they stay sharp at any size and take the tint color, just like SF Symbols.</p>'],
    ],
    faq: [['Which platforms are supported?', 'iOS, iPadOS, macOS, tvOS and watchOS through Swift Package Manager.'],
      ['Can I use them alongside SF Symbols?', 'Yes. They render as template images, so they follow foregroundStyle and tint the same way.'],
      ['Is duotone included?', 'Yes. All six weights, including duotone, are available.']] },
  { path: 'jetpack-compose-icons/', short: 'Android icons', pkg: 'com.github.designmonks-llc:icon-monks', lang: 'Kotlin', install: `implementation("com.github.designmonks-llc:icon-monks:v${VERSION}")`, card: 'Gradle, via JitPack',
    blurb: 'Jetpack Compose ImageVectors and XML VectorDrawables.',
    title: (n) => `Jetpack Compose Icons: ${n} Free Android Icons | Icon Monks`,
    description: (n) => `${n} free Android icons as Jetpack Compose ImageVectors and XML VectorDrawables in six weights. Only the icons you import are compiled into your app.`,
    h1: 'Jetpack Compose and Android icons', lede: (n) => `${n} free icons for Android, as Jetpack Compose <code>ImageVector</code>s and classic XML <code>VectorDrawable</code>s.`,
    sections: [
      ['Install', code(`// settings.gradle.kts\ndependencyResolutionManagement { repositories { google(); mavenCentral(); maven("https://jitpack.io") } }\n\n// app/build.gradle.kts\nimplementation("com.github.designmonks-llc:icon-monks:v${VERSION}")`)],
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

const CSS = `:root{--paper:#f4f5f8;--sheet:#fff;--ink:#1b1e3a;--muted:#5d6280;--rule:#dfe2ec;--saffron:#5754d4;--fill:#aeacff;--on-fill:#1b1e3a;--display:'Funnel Display','Space Grotesk','Helvetica Neue',Arial,sans-serif;--body:'DM Sans',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;--mono:'IBM Plex Mono',ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#11132a;--sheet:#191c38;--ink:#e8e9f4;--muted:#a0a4c4;--rule:#2c3058;--saffron:#aeacff;--fill:#aeacff;--on-fill:#1b1e3a;color-scheme:dark}:root:not([data-theme="light"]) img[src*="/svg/"]{filter:invert(1) hue-rotate(180deg)}}
:root[data-theme="dark"]{--paper:#11132a;--sheet:#191c38;--ink:#e8e9f4;--muted:#a0a4c4;--rule:#2c3058;--saffron:#aeacff;--fill:#aeacff;--on-fill:#1b1e3a;color-scheme:dark}:root[data-theme="dark"] img[src*="/svg/"]{filter:invert(1) hue-rotate(180deg)}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.tiles span{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:2.4em}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 var(--body)}a{color:inherit}
.wrap{max-width:1240px;margin:0 auto;padding:0 16px}
main.wrap{padding-block:32px 64px}.crumbs{list-style:none;display:flex;flex-wrap:wrap;gap:6px;padding:0;margin:0 0 20px;font-size:13px;color:var(--muted)}.crumbs li+li::before{content:"/";margin-right:6px}.crumbs a{text-decoration:none}.crumbs a:hover{text-decoration:underline}
h1{font:400 clamp(34px,5vw,56px)/1.05 var(--display);margin:0 0 12px;letter-spacing:-.01em}h2{font:400 28px/1.2 var(--display);margin:48px 0 14px}h3{font:600 16px var(--body);margin:0 0 6px}
.lede{font-size:18px;color:var(--muted);max-width:68ch;margin:0 0 24px}p{max-width:72ch}p a,.faq a{color:var(--saffron)}
pre{margin:0 0 12px;background:var(--sheet);border:1px solid var(--rule);border-radius:10px;padding:14px;overflow-x:auto;font:13px/1.6 var(--mono)}code{font-family:var(--mono);font-size:.92em}
table{border-collapse:collapse;width:100%;max-width:720px;background:var(--sheet);border:1px solid var(--rule);border-radius:10px;overflow:hidden;font-size:14px}th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--rule)}
.btn{display:inline-flex;align-items:center;font:600 14px var(--body);text-decoration:none;border-radius:10px;padding:10px 16px;border:1px solid var(--rule);background:var(--sheet)}.btn.primary{background:var(--fill);border-color:var(--fill);color:var(--on-fill)}
.actions{display:flex;flex-wrap:wrap;gap:10px 14px;align-items:center;max-width:none}.hint{font-size:14px;color:var(--muted)}
.weights{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px;margin:8px 0 20px}.weights figure{margin:0;background:var(--sheet);border:1px solid var(--rule);border-radius:14px;padding:20px 12px 12px;display:grid;justify-items:center;gap:8px}.weights figcaption{font-size:13px;color:var(--muted)}
.dl{font:500 12px var(--mono);color:var(--saffron);text-decoration:none}.dl:hover{text-decoration:underline}
.codes{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}.code{min-width:0}
.tiles{list-style:none;padding:0;margin:0 0 16px;display:grid;grid-template-columns:repeat(auto-fill,minmax(96px,1fr));gap:8px}.tiles a{display:flex;flex-direction:column;align-items:center;gap:10px;padding:18px 6px 10px;background:var(--sheet);border:1px solid transparent;border-radius:12px;text-decoration:none}.tiles a:hover{border-color:var(--saffron)}.tiles span{font:11px/1.2 var(--mono);color:var(--muted);text-align:center;overflow-wrap:anywhere}
.tags{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:6px}.tags a{display:inline-block;font-size:13px;text-decoration:none;border:1px solid var(--rule);border-radius:99px;padding:4px 12px;background:var(--sheet)}
.cats{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:8px}.cats a{display:flex;justify-content:space-between;gap:8px;text-decoration:none;background:var(--sheet);border:1px solid var(--rule);border-radius:10px;padding:10px 12px;font-weight:500}.cats a:hover{border-color:var(--saffron)}.cats span{font:12px var(--mono);color:var(--muted);align-self:center}
.catcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px}.catcard{display:grid;gap:6px;padding:18px;background:var(--sheet);border:1px solid var(--rule);border-radius:14px;text-decoration:none}.catcard:hover{border-color:var(--saffron)}.catcard .row{display:flex;gap:10px;margin-bottom:8px;overflow:hidden}.catcard .n{font-size:13px;color:var(--muted)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}.card{display:grid;gap:6px;align-content:start;padding:18px;background:var(--sheet);border:1px solid var(--rule);border-radius:14px;text-decoration:none;min-width:0}a.card:hover{border-color:var(--saffron)}.card p{margin:0;color:var(--muted);font-size:14px}.card code{font-size:12px;overflow-x:auto;white-space:nowrap;display:block;color:var(--muted)}
.faq{display:grid;gap:8px;max-width:820px}.faq details{background:var(--sheet);border:1px solid var(--rule);border-radius:12px;padding:0 16px}.faq summary{cursor:pointer;padding:14px 0;list-style:none;display:flex;justify-content:space-between;gap:12px}.faq summary::-webkit-details-marker{display:none}.faq summary::after{content:"+";color:var(--saffron);font:500 20px/1 var(--mono)}.faq details[open] summary::after{content:"\\2212"}.faq summary h3{margin:0;font-size:15px}.faq details p{margin:0 0 16px;color:var(--muted)}
.license{white-space:pre-wrap}
.updated,.byline{font-size:13px;color:var(--muted);margin-top:40px}.updated a,.byline a{color:var(--saffron)}.byline{margin-top:24px}
table.facts th{width:180px;font-weight:600;vertical-align:top}.steps{max-width:72ch;padding-left:22px}.steps li{margin-bottom:8px}.card .card-h{font:600 16px var(--body);margin:0 0 6px}
a:focus-visible,summary:focus-visible{outline:2px solid var(--saffron);outline-offset:2px}
footer{border-top:1px solid var(--rule);padding-block:32px 40px;color:var(--muted);font-size:13px}.foot{display:grid;grid-template-columns:minmax(0,2fr) repeat(3,minmax(0,1fr));gap:24px}.foot h2{font:500 12px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink);margin:0 0 12px}.foot ul{list-style:none;margin:0;padding:0;display:grid;gap:6px}.foot a{text-decoration:none}.foot a:hover{color:var(--ink);text-decoration:underline}.foot p{margin:0;max-width:46ch}
.foot-base{margin:28px 0 0;padding-top:20px;border-top:1px solid var(--rule);max-width:none}.foot p a,.foot-base a{color:var(--ink)}.foot-base a{font-weight:500}
@media (max-width:720px){.foot{grid-template-columns:repeat(2,minmax(0,1fr))}.foot>div:first-child{grid-column:1/-1}}
`;

// How-to articles. `published` is the first release date; dateModified follows each release.
const GUIDES = [
  { path: 'guides/use-icons-in-figma/', short: 'Icons in Figma', published: '2026-10-28', icons: ['figma-logo', 'copy', 'download', 'palette'],
    title: 'How to Use Free Icons in Figma, Sketch and Illustrator | Icon Monks',
    description: 'Copy or download any Icon Monks icon as SVG or PDF and use it in Figma, Sketch, Illustrator or Framer as an editable vector, in any of six weights.',
    h1: 'How to use Icon Monks icons in Figma',
    lede: 'The fastest way to get an Icon Monks icon into Figma is to copy its SVG from the icon browser and paste it onto the canvas. It arrives as one editable vector path in the weight, size and color you picked.',
    steps: [
      ['Find the icon', 'Open the icon browser at iconmonks.co and search by name or tag, or browse a category.'],
      ['Pick a weight, size and color', 'Choose thin, light, regular, bold, fill or duotone, then set the size and color in the toolbar.'],
      ['Copy the SVG', 'Select the icon and press Copy SVG in the detail panel.'],
      ['Paste into Figma', 'Click the Figma canvas and paste. The icon becomes a vector layer you can resize, recolor and turn into a component.'],
    ],
    sections: (up) => [
      ['Download instead of copying', `<p>Prefer files? In the detail panel download the icon as SVG or PDF and drag it onto the canvas. SVG and PDF stay sharp at any size; PNG and WebP exports go up to 1024 px for slides and documents. Each icon page, like the <a href="${up}icon/house/">house icon</a>, also links the SVG for every weight.</p>`],
      ['Sketch, Illustrator and Framer', '<p>The same SVG works everywhere: paste it into Sketch or Framer, or open the SVG or PDF file in Illustrator. Because every icon is one flat path with no strokes, it does not need outlining or flattening, and it looks exactly like the coded version your developers ship.</p>'],
      ['Keep design and code in sync', `<p>Use the same icon name in design and code. The <code>house</code> icon you paste in Figma is <code>&lt;House /&gt;</code> in React, <code>IconMonks.house</code> in Flutter and <code>.house</code> in SwiftUI, so handoff needs no lookup table. See <a href="${up}getting-started/">Get started</a> for each platform.</p>`],
    ],
    faq: [
      ['Is there a Figma plugin for Icon Monks?', 'Not yet. Copy SVG from the icon browser and paste it into Figma; it takes a few seconds and keeps the vector editable.'],
      ['Can I change the color after pasting into Figma?', 'Yes. The icon is a single filled path, so change its fill like any other vector layer.'],
      ['Do I need to credit Icon Monks in my designs?', 'No. The MIT license lets you use the icons in client and commercial work with no credit needed in your interface.'],
    ] },
  { path: 'guides/change-icon-color-and-size/', short: 'Color and size', published: '2026-10-28', icons: ['palette', 'arrows-out', 'paint-brush', 'sliders-horizontal'],
    title: 'How to Change Icon Color and Size in React, Vue, Flutter, SwiftUI & Compose',
    description: 'Change the color and size of Icon Monks icons in React, Vue, web components, CSS icon fonts, inline SVG, Flutter, SwiftUI and Jetpack Compose, with code for each.',
    h1: 'How to change icon color and size',
    lede: 'Every Icon Monks icon draws in currentColor, so by default it takes the text color and scales as a vector. To set them yourself, use the size and color props in React, Vue and the web component, CSS for fonts and inline SVG, and the platform\'s own icon APIs on Flutter, SwiftUI and Android.',
    sections: () => [
      ['Quick reference', '<table><tr><th>Platform</th><th>Size</th><th>Color</th></tr>'
        + '<tr><td>React</td><td><code>size={32}</code></td><td><code>color="crimson"</code></td></tr>'
        + '<tr><td>Vue</td><td><code>:size="32"</code></td><td><code>color="crimson"</code></td></tr>'
        + '<tr><td>Web component</td><td><code>size="32"</code></td><td><code>color="crimson"</code></td></tr>'
        + '<tr><td>Icon font</td><td><code>font-size: 32px</code></td><td><code>color: crimson</code></td></tr>'
        + '<tr><td>Inline SVG</td><td><code>width</code> / <code>height</code></td><td>CSS <code>color</code> (currentColor)</td></tr>'
        + '<tr><td>Flutter</td><td><code>size: 32</code></td><td><code>color: Colors.red</code></td></tr>'
        + '<tr><td>SwiftUI</td><td><code>size: 32</code></td><td><code>.foregroundStyle(.red)</code></td></tr>'
        + '<tr><td>Jetpack Compose</td><td><code>Modifier.size(32.dp)</code></td><td><code>tint = Color.Red</code></td></tr></table>'],
      ['React and Vue', code(`// React\n<Heart size={32} color="crimson" weight="fill" />\n\n<!-- Vue -->\n<Heart :size="32" color="crimson" weight="fill" />`) + '<p>Leave out <code>color</code> to inherit the text color. Set defaults for a whole tree with <code>IconContext</code> in React or <code>provide(IconContextKey, …)</code> in Vue.</p>'],
      ['Web component, icon font and SVG', code(`<icon-monks name="heart" size="32" color="crimson"></icon-monks>\n\n<i class="im im-heart" style="font-size: 32px; color: crimson"></i>\n\n<svg width="32" height="32" style="color: crimson"> … </svg>`) + '<p>Icon fonts and inline SVGs behave like text: change <code>font-size</code> or <code>width</code> and <code>color</code> in CSS, including on <code>:hover</code>.</p>'],
      ['Flutter', code(`Icon(IconMonks.heart, size: 32, color: Colors.red)\n\n// or for a whole subtree\nIconTheme(data: IconThemeData(size: 24, color: Colors.indigo), child: …)`)],
      ['SwiftUI and UIKit', code(`IconMonkImage(.heart, weight: .fill, size: 32)   // scales with Dynamic Type\n    .foregroundStyle(.red)\n\nlet image = IconMonk.heart.uiImage(.bold)          // UIKit, tint with tintColor`)],
      ['Jetpack Compose', code(`Icon(\n    IconMonks.Fill.Heart,\n    contentDescription = "Favorite",\n    tint = Color.Red,\n    modifier = Modifier.size(32.dp),\n)`)],
    ],
    faq: [
      ['Why does my icon have the wrong color?', 'Icons use currentColor, so they inherit the color of their parent. Set color on the icon itself, or on the element around it.'],
      ['Can I use a gradient?', 'Yes, with inline SVG: define a linearGradient and set the path fill to it. Fonts and the native packages support a single color.'],
      ['What size should icons be?', 'Most interfaces use 20 to 24 px. Use the bold weight at 16 px and below so lines stay readable, and thin or light at 48 px and above.'],
    ] },
  { path: 'guides/svg-vs-icon-font/', short: 'SVG vs icon font', published: '2026-10-28', icons: ['file-svg', 'text-aa', 'scales', 'code'],
    title: 'SVG Icons vs Icon Fonts: Which Should You Use? | Icon Monks',
    description: 'SVG icons and icon fonts compared on color, duotone, accessibility, performance and setup, with a clear recommendation for each kind of project.',
    h1: 'SVG icons vs icon fonts: which should you use?',
    lede: 'Use SVG icons, through a component package or inline SVG, for most modern apps: they support duotone, scale perfectly and only ship the icons you use. Use an icon font when you need icons in plain HTML or CSS with no build step and a single color is enough.',
    sections: () => [
      ['Side-by-side comparison', '<table><tr><th></th><th>SVG (components or files)</th><th>Icon font</th></tr>'
        + '<tr><td>Setup</td><td>npm package or copy a file</td><td>One stylesheet link</td></tr>'
        + '<tr><td>Colors</td><td>Any color, plus duotone</td><td>One color per icon</td></tr>'
        + '<tr><td>Weights in Icon Monks</td><td>All six</td><td>Five (no duotone)</td></tr>'
        + '<tr><td>Bundle size</td><td>Only the icons you import</td><td>Whole font per weight, cached once</td></tr>'
        + '<tr><td>Rendering</td><td>Pixel-exact vector</td><td>Text rendering, can blur slightly at odd sizes</td></tr>'
        + '<tr><td>Accessibility</td><td>aria-label / title on the SVG</td><td>Needs aria-hidden plus a text label</td></tr>'
        + '<tr><td>Best for</td><td>React, Vue, Next.js, native apps</td><td>Static sites, WordPress, CSS-only themes</td></tr></table>'],
      ['When to choose SVG', '<p>Pick SVG when you use a framework, need duotone or multicolor icons, care about bundle size, or want icons that render identically everywhere. The <a href="../../react-icons/">React</a> and <a href="../../vue-icons/">Vue</a> packages and the <a href="../../web-components/">web component</a> all render SVG.</p>'],
      ['When to choose an icon font', '<p>Pick the <a href="../../icon-font/">icon font</a> when you cannot run a build step, want icons to flow with text and inherit font-size, or are styling an existing site with CSS only. Icon Monks glyphs keep the same codepoints between releases, so upgrades do not break your CSS.</p>'],
    ],
    faq: [
      ['Are icon fonts bad for accessibility?', 'Not if you mark the icon aria-hidden="true" and give the button or link a text label. Screen readers then skip the glyph and read the label.'],
      ['Do SVG icons slow down a page?', 'No. A single Icon Monks icon is about 1 KB, and component packages include only the icons you import.'],
      ['Can I use both?', 'Yes. All Icon Monks packages share the same names and shapes, so you can use the font on a marketing site and React components in the app.'],
    ] },
  { path: 'guides/choose-icon-weight/', short: 'Choosing a weight', published: '2026-10-28', icons: ['bell', 'heart', 'star', 'house'],
    title: 'Thin, Light, Regular, Bold, Fill or Duotone: Choosing an Icon Weight',
    description: 'Which icon weight to use where: stroke widths, best sizes and typical uses for thin, light, regular, bold, fill and duotone icons, with examples.',
    h1: 'How to choose an icon weight',
    lede: 'Match the icon weight to its size and its job. Regular suits most 24 px interface icons, bold holds up at 16 px, thin and light suit large display sizes, fill marks a selected state, and duotone adds depth to illustrations and empty states.',
    sections: () => [
      ['The six weights at a glance', '<table><tr><th>Weight</th><th>Stroke on the 256 grid</th><th>Best size</th><th>Use it for</th></tr>'
        + '<tr><td>Thin</td><td>8 units</td><td>48 px and up</td><td>Large, quiet display icons and hero art</td></tr>'
        + '<tr><td>Light</td><td>12 units</td><td>32 px and up</td><td>Airy interfaces and marketing pages</td></tr>'
        + '<tr><td>Regular</td><td>16 units</td><td>20 to 24 px</td><td>The default for buttons, menus and lists</td></tr>'
        + '<tr><td>Bold</td><td>24 units</td><td>16 px and below</td><td>Small sizes, dense tables and busy screens</td></tr>'
        + '<tr><td>Fill</td><td>Solid</td><td>Any</td><td>Selected tabs, active states, toggles</td></tr>'
        + '<tr><td>Duotone</td><td>Outline over a 20% tint</td><td>32 px and up</td><td>Illustrations, onboarding and empty states</td></tr></table>'],
      ['Pair outline and fill for states', '<p>A common pattern is regular for inactive items and fill for the active one, for example in a bottom navigation bar. Because every weight shares the same shape, the switch reads as a state change rather than a different icon. The <a href="../../showcase/">showcase</a> uses exactly this.</p>'],
      ['Stay consistent', '<p>Pick one outline weight for a product and use it everywhere, then add fill for states and duotone for illustration. Mixing regular and bold outlines on one screen makes the interface look uneven.</p>'],
    ],
    faq: [
      ['What is the default weight?', 'Regular, with a 16-unit stroke on the 256-unit grid, tuned for 24 px icons.'],
      ['Which weights does the icon font include?', 'Thin, light, regular, bold and fill. Duotone needs two colors, so it is only in the SVG, React, Vue, web component and native packages.'],
      ['Can I switch weight in code?', 'Yes. Pass weight="bold" in React, Vue and the web component, IconMonks.bold.heart in Flutter, weight: .bold in SwiftUI and IconMonks.Bold.Heart in Compose.'],
    ] },
];
