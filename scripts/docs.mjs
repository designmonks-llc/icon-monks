// Builds docs/index.html (the icon browser) from docs/template.html and build/icons.json.
import { readFileSync, writeFileSync } from 'node:fs';

const root = new URL('..', import.meta.url);
const data = JSON.parse(readFileSync(new URL('build/icons.json', root)));
const template = readFileSync(new URL('docs/template.html', root), 'utf8');
writeFileSync(new URL('docs/index.html', root), template.replace('/*__ICONS__*/null', JSON.stringify(data)));
console.log(`docs/index.html: ${data.icons.length} icons`);
