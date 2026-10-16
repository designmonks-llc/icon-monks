// Builds the icon browser from docs/template.html and build/icons.json:
//   index.html           full page served by GitHub Pages (repo root)
//   build/artifact.html  page fragment for the claude.ai preview artifact
import { readFileSync, writeFileSync } from 'node:fs';

const root = new URL('..', import.meta.url);
const data = JSON.parse(readFileSync(new URL('build/icons.json', root)));
const page = readFileSync(new URL('docs/template.html', root), 'utf8').replace('/*__ICONS__*/null', JSON.stringify(data));

const split = page.indexOf('</style>') + '</style>'.length;
const gear = data.icons.find((i) => i.name === 'gear').paths.bold;
const favicon = `data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="#c96a00"><path d="${gear}"/></svg>`)}`;
const full = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Icon Monks: ${data.icons.length} open source icons in six weights for React, Vue, Web Components, fonts, Flutter, Android and iOS.">
<link rel="icon" href="${favicon}">
${page.slice(0, split)}
</head>
<body>
${page.slice(split)}
</body>
</html>
`;
writeFileSync(new URL('index.html', root), full);
writeFileSync(new URL('build/artifact.html', root), page);
console.log(`index.html + build/artifact.html: ${data.icons.length} icons`);
