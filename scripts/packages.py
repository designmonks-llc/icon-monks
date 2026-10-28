#!/usr/bin/env python3
"""Generate every platform package from build/icons.json (run scripts/build.py first).

  packages/core     SVG assets, sprites, metadata, toSvg()      (npm)
  packages/react    React components                            (npm)
  packages/vue      Vue 3 components                            (npm)
  packages/web      <icon-monks> custom element + CDN bundle     (npm)
  packages/font     OTF/WOFF2 icon fonts + CSS                   (npm)
  packages/flutter  IconData constants + fonts                   (pub.dev)
  packages/android  VectorDrawables + Jetpack Compose ImageVectors
  packages/swift    Swift Package: asset catalog + SwiftUI/UIKit helpers
"""
import json
import os
import shutil

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, 'packages')
DATA = json.load(open(os.path.join(ROOT, 'build', 'icons.json')))
ICONS = DATA['icons']
WEIGHTS = DATA['weights']
SOLID_WEIGHTS = [w for w in WEIGHTS if w != 'duotone']
VERSION = json.load(open(os.path.join(ROOT, 'package.json')))['version']
CHANGELOG = ('## 0.4.1\n\n- Fuller READMEs for every package. The Flutter package documents every icon, ships an example and scores 160/160 on pub.dev. Releases publish only from tags on main.\n\n'
             '## 0.4.0\n\n- Adds 1,322 icons (6,054 total) across 31 categories, including a new Brands category with 652 logos. '
             'Variant icons share one badge pattern, every icon passes a strict lint, and the web component loads icons '
             'on demand.\n\n'
             '## 0.3.0\n\n- Adds 4,235 icons (4,732 total) across 30 categories, unifies icon families and fixes shapes '
             'that collapsed in some weights.\n\n'
             '## 0.2.0\n\n- Adds 400 icons (497 total) across 22 categories.\n\n## 0.1.0\n\n- Initial release with 97 icons.\n')
LICENSE = open(os.path.join(ROOT, 'LICENSE.md')).read()  # not LICENSE: the site's license/ page shares that name on case-insensitive disks
DUO = 0.2


def pascal(name):
    return ''.join(p.capitalize() for p in name.split('-'))


def camel(name):
    p = pascal(name)
    return p[0].lower() + p[1:]


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as fh:
        fh.write(text)


SITE = 'https://www.iconmonks.co/'
REPO = 'https://github.com/designmonks-llc/icon-monks'


def readme_head(title, badge, intro):
    """Shared top of every package README: title, badges, preview image and a short intro."""
    return f"""# {title}

{badge}
[![license: MIT](https://img.shields.io/badge/license-MIT-blue)]({REPO}/blob/main/LICENSE.md)

![Icon Monks]({SITE}og-image.png)

{intro} A product of [Design Monks](https://monks.company/). Browse and search every icon at
**[iconmonks.co]({SITE})**.
"""


def npm_badge(name):
    return f'[![npm](https://img.shields.io/npm/v/{name})](https://www.npmjs.com/package/{name})'


README_FOOT = f"""
## Links

- [Website and icon search]({SITE})
- [All platforms and source code]({REPO})
- [Request an icon or report a bug]({REPO}/issues)

MIT licensed. A product of [Design Monks](https://monks.company/).
"""


def fresh(name):
    path = os.path.join(PKG, name)
    for sub in ('dist', 'assets', 'fonts', 'lib', 'res', 'src', 'Sources'):
        shutil.rmtree(os.path.join(path, sub), ignore_errors=True)
    os.makedirs(path, exist_ok=True)
    write(os.path.join(path, 'LICENSE'), LICENSE)
    return path


def codepoints():
    path = os.path.join(ROOT, 'codepoints.json')
    cps = json.load(open(path)) if os.path.exists(path) else {}
    nxt = max(cps.values(), default=0xE000 - 1) + 1
    for ic in ICONS:  # append-only so existing glyphs never move
        if ic['name'] not in cps:
            cps[ic['name']] = nxt
            nxt += 1
    write(path, json.dumps(cps, indent=2) + '\n')
    return cps


def npm_package(path, name, description, extra):
    pkg = {
        'name': name, 'version': VERSION, 'description': description, 'license': 'MIT',
        'author': 'Design Monks (https://monks.company/)', 'homepage': 'https://www.iconmonks.co/',
        'repository': {'type': 'git', 'url': 'git+https://github.com/designmonks-llc/icon-monks.git'},
        'keywords': ['icons', 'icon', 'icon-library', 'svg', 'svg-icons', 'open-source-icons', 'icon-set', 'react-icons', 'vue-icons', 'web-components', 'icon-font', 'icon-monks'],
    }
    pkg.update(extra)
    write(os.path.join(path, 'package.json'), json.dumps(pkg, indent=2) + '\n')


META = [{'name': i['name'], 'category': i['category'], 'tags': i['tags']} for i in ICONS]
PATHS = {i['name']: i['paths'] for i in ICONS}


# ---------------------------------------------------------------------------- core
def core():
    path = fresh('core')
    shutil.copytree(os.path.join(ROOT, 'svg'), os.path.join(path, 'assets'))
    for w in WEIGHTS:
        symbols = []
        for ic in ICONS:
            d = ic['paths'][w]
            inner = (f'<path d="{d[0]}" opacity="{DUO}"/><path d="{d[1]}"/>' if w == 'duotone' else f'<path d="{d}"/>')
            symbols.append(f'<symbol id="{ic["name"]}" viewBox="0 0 256 256" fill="currentColor">{inner}</symbol>')
        write(os.path.join(path, 'dist', 'sprite', f'{w}.svg'),
              '<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor">' + ''.join(symbols) + '</svg>\n')
    write(os.path.join(path, 'dist', 'icons.json'), json.dumps(META, indent=1) + '\n')
    write(os.path.join(path, 'dist', 'index.js'), f"""export const weights = {json.dumps(WEIGHTS)};
export const icons = {json.dumps(META)};
export const paths = {json.dumps(PATHS, separators=(',', ':'))};

export function toSvg(name, {{ weight = 'regular', size = 24, color = 'currentColor', mirrored = false, title }} = {{}}) {{
  const icon = paths[name];
  if (!icon) throw new Error(`Unknown Icon Monks icon: ${{name}}`);
  const d = icon[weight] ?? icon.regular;
  const body = weight === 'duotone'
    ? (d[0] ? `<path d="${{d[0]}}" opacity="{DUO}"/>` : '') + `<path d="${{d[1]}}"/>`
    : `<path d="${{d}}"/>`;
  const t = title ? `<title>${{String(title).replace(/[<&]/g, (c) => (c === '<' ? '&lt;' : '&amp;'))}}</title>` : '';
  const flip = mirrored ? ' transform="scale(-1, 1)"' : '';
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${{size}}" height="${{size}}" viewBox="0 0 256 256" fill="${{color}}"${{flip}}>${{t}}${{body}}</svg>`;
}}
""")
    names = ' | '.join(f"'{i['name']}'" for i in ICONS)
    write(os.path.join(path, 'dist', 'index.d.ts'), f"""export type IconWeight = {' | '.join(repr(w) for w in WEIGHTS)};
export type IconName = {names};
export interface IconMeta {{ name: IconName; category: string; tags: string[]; }}
export declare const weights: IconWeight[];
export declare const icons: IconMeta[];
export declare const paths: Record<IconName, Record<Exclude<IconWeight, 'duotone'>, string> & {{ duotone: [string, string] }}>;
export interface ToSvgOptions {{ weight?: IconWeight; size?: number | string; color?: string; mirrored?: boolean; title?: string; }}
export declare function toSvg(name: IconName, options?: ToSvgOptions): string;
""")
    npm_package(path, '@icon-monks/core', 'Icon Monks: raw SVG assets, sprites, metadata and a toSvg() helper.', {
        'type': 'module', 'main': './dist/index.js', 'types': './dist/index.d.ts', 'sideEffects': False,
        'exports': {'.': {'types': './dist/index.d.ts', 'default': './dist/index.js'},
                    './icons.json': './dist/icons.json', './sprite/*': './dist/sprite/*', './assets/*': './assets/*'},
        'files': ['dist', 'assets'],
    })
    write(os.path.join(path, 'README.md'), readme_head(
        '@icon-monks/core', npm_badge('@icon-monks/core'),
        f'Framework-free Icon Monks: {len(ICONS):,} icons in {len(WEIGHTS)} weights (thin, light, regular, bold, fill, '
        'duotone) as SVG files, SVG sprites and path data, for any framework or build tool.') + f"""
## Install

```sh
npm install @icon-monks/core
```

## Usage

```js
import {{ toSvg, icons, weights }} from '@icon-monks/core';

document.body.innerHTML = toSvg('house', {{ weight: 'bold', size: 32, color: '#6d28d9' }});
toSvg('heart', {{ title: 'Favorite' }});   // adds an accessible <title>
```

`toSvg(name, options)` returns an SVG string. Options: `weight` (default `regular`), `size` (default `24`), `color`
(default `currentColor`), `mirrored` and `title`. The package also exports `icons` (name, category and tags for
every icon), `weights` and the raw `paths`. Names and weights are typed in TypeScript.

## Files

| Path | What it is |
| --- | --- |
| `assets/<weight>/<name>[-<weight>].svg` | One SVG per icon and weight (`regular` has no suffix) |
| `dist/sprite/<weight>.svg` | One sprite per weight: `<svg><use href="sprite/regular.svg#house"/></svg>` |
| `dist/icons.json` | Names, categories and tags, for building your own search |
""" + README_FOOT)


# ---------------------------------------------------------------------------- react
REACT_LIB = """import { createContext, createElement, forwardRef, useContext } from 'react';

export const IconContext = createContext({ color: 'currentColor', size: '1em', weight: 'regular', mirrored: false });

export function createIcon(displayName, paths) {
  const Icon = forwardRef(function IconMonk(props, ref) {
    const ctx = useContext(IconContext);
    const { color = ctx.color, size = ctx.size, weight = ctx.weight, mirrored = ctx.mirrored, children, ...rest } = props;
    const d = paths[weight] ?? paths.regular;
    const body = weight === 'duotone'
      ? [d[0] ? createElement('path', { key: 'a', d: d[0], opacity: %s }) : null, createElement('path', { key: 'l', d: d[1] })]
      : createElement('path', { d });
    return createElement('svg', {
      ref, xmlns: 'http://www.w3.org/2000/svg', width: size, height: size, viewBox: '0 0 256 256', fill: color,
      transform: mirrored ? 'scale(-1, 1)' : undefined, ...ctx.attrs, ...rest,
    }, children, body);
  });
  Icon.displayName = displayName;
  return Icon;
}
""" % DUO

REACT_DTS = """import type { ForwardRefExoticComponent, RefAttributes, SVGProps, Context } from 'react';

export type IconWeight = 'thin' | 'light' | 'regular' | 'bold' | 'fill' | 'duotone';
export interface IconProps extends Omit<SVGProps<SVGSVGElement>, 'ref'> {
  /** Width and height. Default `1em`. */
  size?: number | string;
  /** Icon color. Default `currentColor`. */
  color?: string;
  /** Visual weight. Default `regular`. */
  weight?: IconWeight;
  /** Flip horizontally, e.g. for right-to-left layouts. */
  mirrored?: boolean;
}
export type Icon = ForwardRefExoticComponent<IconProps & RefAttributes<SVGSVGElement>>;
export interface IconContextValue { color?: string; size?: number | string; weight?: IconWeight; mirrored?: boolean; attrs?: SVGProps<SVGSVGElement>; }
export declare const IconContext: Context<IconContextValue>;
export declare function createIcon(displayName: string, paths: Record<string, string | [string, string]>): Icon;
"""


def react():
    path = fresh('react')
    write(os.path.join(path, 'dist', 'lib.js'), REACT_LIB)
    write(os.path.join(path, 'dist', 'lib.d.ts'), REACT_DTS)
    index, dts = ["export * from './lib.js';"], ["export * from './lib.js';", "import type { Icon } from './lib.js';"]
    for ic in ICONS:
        n = pascal(ic['name'])
        write(os.path.join(path, 'dist', 'icons', f'{n}.js'),
              f"import {{ createIcon }} from '../lib.js';\n\n"
              f"export const {n} = createIcon('{n}', {json.dumps(ic['paths'], separators=(',', ':'))});\n"
              f"export {{ {n} as {n}Icon }};\nexport default {n};\n")
        write(os.path.join(path, 'dist', 'icons', f'{n}.d.ts'),
              f"import type {{ Icon }} from '../lib.js';\nexport declare const {n}: Icon;\n"
              f"export {{ {n} as {n}Icon }};\nexport default {n};\n")
        index.append(f"export {{ {n}, {n}Icon }} from './icons/{n}.js';")
        dts.append(f"export declare const {n}: Icon;\nexport declare const {n}Icon: Icon;")
    write(os.path.join(path, 'dist', 'index.js'), '\n'.join(index) + '\n')
    write(os.path.join(path, 'dist', 'index.d.ts'), '\n'.join(dts) + '\n')
    npm_package(path, '@icon-monks/react', 'Icon Monks for React: tree-shakeable components in six weights.', {
        'type': 'module', 'main': './dist/index.js', 'types': './dist/index.d.ts', 'sideEffects': False,
        'exports': {'.': {'types': './dist/index.d.ts', 'default': './dist/index.js'},
                    './icons/*': {'types': './dist/icons/*.d.ts', 'default': './dist/icons/*.js'}},
        'files': ['dist'], 'peerDependencies': {'react': '>=16.8'},
    })
    write(os.path.join(path, 'README.md'), readme_head(
        '@icon-monks/react', npm_badge('@icon-monks/react'),
        f'{len(ICONS):,} React icon components in six weights: thin, light, regular, bold, fill and duotone. Typed, '
        'tree-shakeable, and server-rendering friendly.') + """
## Install

```sh
npm install @icon-monks/react
```

## Usage

```jsx
import { House, Heart } from '@icon-monks/react';

<House />                                          // 1em, currentColor, regular
<Heart size={32} color="crimson" weight="fill" />
<House aria-label="Home" />                        // any SVG attribute is passed through
```

## Props

| Prop | Type | Default |
| --- | --- | --- |
| `size` | `number \\| string` | `1em` |
| `color` | `string` | `currentColor` |
| `weight` | `thin` `light` `regular` `bold` `fill` `duotone` | `regular` |
| `mirrored` | `boolean`, flips the icon for right-to-left layouts | `false` |

Any other prop goes to the `<svg>` element, and refs are forwarded.

## Defaults for a subtree

```jsx
import { IconContext } from '@icon-monks/react';

<IconContext.Provider value={{ size: 24, weight: 'duotone' }}>
  <House /> <Heart />
</IconContext.Provider>
```

## Imports

Only the icons you import end up in your bundle. Every icon is also exported with an `Icon` suffix (`HouseIcon`), handy
when a name clashes with your own components, and as a deep import: `import { House } from '@icon-monks/react/icons/House'`.
""" + README_FOOT)


# ---------------------------------------------------------------------------- vue
VUE_LIB = """import { defineComponent, h, inject } from 'vue';

export const IconContextKey = Symbol('icon-monks');

export function createIcon(name, paths) {
  return defineComponent({
    name,
    props: {
      size: { type: [String, Number], default: undefined },
      color: { type: String, default: undefined },
      weight: { type: String, default: undefined },
      mirrored: { type: Boolean, default: undefined },
    },
    setup(props, { slots }) {
      const ctx = inject(IconContextKey, {});
      return () => {
        const weight = props.weight ?? ctx.weight ?? 'regular';
        const size = props.size ?? ctx.size ?? '1em';
        const mirrored = props.mirrored ?? ctx.mirrored ?? false;
        const d = paths[weight] ?? paths.regular;
        const body = weight === 'duotone'
          ? [d[0] ? h('path', { d: d[0], opacity: %s }) : null, h('path', { d: d[1] })]
          : [h('path', { d })];
        return h('svg', {
          xmlns: 'http://www.w3.org/2000/svg', width: size, height: size, viewBox: '0 0 256 256',
          fill: props.color ?? ctx.color ?? 'currentColor', transform: mirrored ? 'scale(-1, 1)' : undefined,
        }, [slots.default?.(), ...body]);
      };
    },
  });
}
""" % DUO


def vue():
    path = fresh('vue')
    write(os.path.join(path, 'dist', 'lib.js'), VUE_LIB)
    write(os.path.join(path, 'dist', 'lib.d.ts'), """import type { DefineComponent, InjectionKey } from 'vue';
export type IconWeight = 'thin' | 'light' | 'regular' | 'bold' | 'fill' | 'duotone';
export interface IconProps { size?: number | string; color?: string; weight?: IconWeight; mirrored?: boolean; }
export type Icon = DefineComponent<IconProps>;
export declare const IconContextKey: InjectionKey<IconProps>;
export declare function createIcon(name: string, paths: Record<string, string | [string, string]>): Icon;
""")
    index, dts = ["export * from './lib.js';"], ["export * from './lib.js';", "import type { Icon } from './lib.js';"]
    for ic in ICONS:
        n = pascal(ic['name'])
        write(os.path.join(path, 'dist', 'icons', f'{n}.js'),
              f"import {{ createIcon }} from '../lib.js';\n\n"
              f"export const {n} = createIcon('IconMonks{n}', {json.dumps(ic['paths'], separators=(',', ':'))});\n"
              f"export {{ {n} as {n}Icon }};\nexport default {n};\n")
        index.append(f"export {{ {n}, {n}Icon }} from './icons/{n}.js';")
        dts.append(f"export declare const {n}: Icon;\nexport declare const {n}Icon: Icon;")
    write(os.path.join(path, 'dist', 'index.js'), '\n'.join(index) + '\n')
    write(os.path.join(path, 'dist', 'index.d.ts'), '\n'.join(dts) + '\n')
    npm_package(path, '@icon-monks/vue', 'Icon Monks for Vue 3: tree-shakeable components in six weights.', {
        'type': 'module', 'main': './dist/index.js', 'types': './dist/index.d.ts', 'sideEffects': False,
        'exports': {'.': {'types': './dist/index.d.ts', 'default': './dist/index.js'}, './icons/*': './dist/icons/*.js'},
        'files': ['dist'], 'peerDependencies': {'vue': '>=3.2'},
    })
    write(os.path.join(path, 'README.md'), readme_head(
        '@icon-monks/vue', npm_badge('@icon-monks/vue'),
        f'{len(ICONS):,} Vue 3 icon components in six weights: thin, light, regular, bold, fill and duotone. Typed and '
        'tree-shakeable.') + """
## Install

```sh
npm install @icon-monks/vue
```

## Usage

```vue
<script setup>
import { House, Heart } from '@icon-monks/vue';
</script>

<template>
  <House />
  <Heart :size="32" color="crimson" weight="fill" />
  <House aria-label="Home" />
</template>
```

## Props

| Prop | Type | Default |
| --- | --- | --- |
| `size` | `number \\| string` | `1em` |
| `color` | `string` | `currentColor` |
| `weight` | `thin` `light` `regular` `bold` `fill` `duotone` | `regular` |
| `mirrored` | `boolean`, flips the icon for right-to-left layouts | `false` |

Other attributes fall through to the `<svg>` element.

## Defaults for a subtree

```vue
<script setup>
import { provide } from 'vue';
import { IconContextKey } from '@icon-monks/vue';

provide(IconContextKey, { size: 24, weight: 'bold' });
</script>
```

## Imports

Only the icons you import end up in your bundle. Deep imports work too: `import { House } from '@icon-monks/vue/icons/House'`.
""" + README_FOOT)


# ---------------------------------------------------------------------------- web component
# The element itself; `lookup(name, weight)` returns path data, a promise of it, or undefined for an unknown icon.
WEB_ELEMENT = """
const ATTRS = ['name', 'weight', 'size', 'color', 'mirrored', 'label'];
const WEIGHTS = %s;

function draw(el, d, weight) {
  const size = el.getAttribute('size') || '1em';
  const color = el.getAttribute('color') || 'currentColor';
  const body = !d ? '' : weight === 'duotone'
    ? (d[0] ? '<path d="' + d[0] + '" opacity="%s"/>' : '') + '<path d="' + d[1] + '"/>'
    : '<path d="' + d + '"/>';
  const flip = el.hasAttribute('mirrored') ? ' transform="scale(-1, 1)"' : '';
  el.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="' + size + '" height="' + size +
    '" viewBox="0 0 256 256" fill="' + color + '"' + flip + ' style="display:block">' + body + '</svg>';
}

function render(el) {
  const name = el.getAttribute('name') || '';
  const asked = el.getAttribute('weight') || 'regular';
  const weight = WEIGHTS.indexOf(asked) < 0 ? 'regular' : asked;
  const label = el.getAttribute('label');
  if (label) { el.setAttribute('role', 'img'); el.setAttribute('aria-label', label); }
  else { el.removeAttribute('role'); el.removeAttribute('aria-label'); el.setAttribute('aria-hidden', 'true'); }
  const d = lookup(name, weight);
  if (d && typeof d.then === 'function') {
    draw(el, null, weight);  // holds the icon's space while its path data loads
    const ticket = el._iconMonks = {};
    d.then((v) => { if (el._iconMonks !== ticket) return; if (v) draw(el, v, weight); else el.innerHTML = ''; });
  } else {
    el._iconMonks = null;
    if (d) draw(el, d, weight); else el.innerHTML = '';
  }
}

// Importable during server rendering, where there is no HTMLElement; the element only registers in a browser.
class IconMonkElement extends (typeof HTMLElement === 'undefined' ? class {} : HTMLElement) {
  static get observedAttributes() { return ATTRS; }
  connectedCallback() { this.style.display ||= 'inline-block'; this.style.lineHeight ||= '0'; render(this); }
  attributeChangedCallback() { if (this.isConnected) render(this); }
}

if (typeof customElements !== 'undefined' && !customElements.get('icon-monks')) {
  customElements.define('icon-monks', IconMonkElement);
}
""" % (json.dumps(WEIGHTS), DUO)

# Lazy loading: each icon's path data is fetched once per weight, on first use, from dist/icons/<weight>/<name>.json.
# BASES lists where to look, in order; a base that answers with something other than JSON (a dev server's HTML
# fallback, a network error) is dropped. The pinned CDN copy is the last resort.
WEB_LAZY = """
const CDN = 'https://cdn.jsdelivr.net/npm/@icon-monks/web@%s/dist/icons/';
let BASES = [];
const cache = new Map();

function setIconBase(url) { BASES = [String(url).replace(/\\/?$/, '/')]; cache.clear(); }

async function fetchIcon(key) {
  for (const base of BASES.slice()) {
    try {
      const res = await fetch(base + key + '.json');
      if (res.ok) return await res.json();
    } catch (e) {
      BASES = BASES.filter((b) => b !== base);
    }
  }
  return undefined;
}

function lookup(name, weight) {
  if (!/^[a-z0-9-]+$/.test(name)) return undefined;
  const key = weight + '/' + name;
  if (!cache.has(key)) cache.set(key, fetchIcon(key).then((d) => { if (d) cache.set(key, d); else cache.delete(key); return d; }));
  return cache.get(key);
}
""" % VERSION

# Where the CDN script finds the icon files: next to itself, or under dist/ when it was loaded by package name
# (https://cdn.jsdelivr.net/npm/@icon-monks/web). <script data-base="..."> overrides both.
WEB_CDN_BASE = """
const script = typeof document !== 'undefined' ? document.currentScript : null;
if (script && script.dataset.base) BASES = [script.dataset.base.replace(/\\/?$/, '/')];
else if (script && script.src) {
  const src = script.src.split(/[?#]/)[0];
  BASES = [/\\.js$/.test(src) ? new URL('icons/', src).href : src.replace(/\\/?$/, '/') + 'dist/icons/', CDN];
} else BASES = [CDN];
"""


def web():
    path = fresh('web')
    dist = os.path.join(path, 'dist')
    for w in WEIGHTS:
        os.makedirs(os.path.join(dist, 'icons', w), exist_ok=True)
        for name, paths in PATHS.items():
            with open(os.path.join(dist, 'icons', w, name + '.json'), 'w') as fh:
                json.dump(paths[w], fh, separators=(',', ':'))
    # The base must be set before the element is defined: defining it renders icons already on the page.
    write(os.path.join(dist, 'index.js'), WEB_LAZY + "BASES = [new URL('./icons/', import.meta.url).href, CDN];\n" +
          WEB_ELEMENT + "\nexport { IconMonkElement, setIconBase };\n")
    write(os.path.join(dist, 'icon-monks.js'), '(function () {\n' + WEB_LAZY + WEB_CDN_BASE + WEB_ELEMENT + '})();\n')
    every = (f"const PATHS = {json.dumps(PATHS, separators=(',', ':'))};\n"
             "function lookup(name, weight) { const icon = PATHS[name]; return icon && (icon[weight] || icon.regular); }\n"
             + WEB_ELEMENT)
    write(os.path.join(dist, 'all.js'), every + "\nexport { IconMonkElement, PATHS as paths };\n")
    write(os.path.join(dist, 'icon-monks.all.js'), '(function () {\n' + every + '})();\n')
    element = """export declare class IconMonkElement extends HTMLElement {}
declare global { interface HTMLElementTagNameMap { 'icon-monks': IconMonkElement; } }
"""
    write(os.path.join(dist, 'index.d.ts'), element + """/** Where icon files are fetched from: a folder holding <weight>/<name>.json, such as a copy of dist/icons/. */
export declare function setIconBase(url: string | URL): void;
""")
    write(os.path.join(dist, 'all.d.ts'), element +
          "export declare const paths: Record<string, Record<string, string | [string, string]>>;\n")
    npm_package(path, '@icon-monks/web', 'Icon Monks as a <icon-monks> custom element. Works in any framework or plain HTML.', {
        'type': 'module', 'main': './dist/index.js', 'types': './dist/index.d.ts', 'unpkg': './dist/icon-monks.js',
        'jsdelivr': './dist/icon-monks.js',
        'exports': {'.': {'types': './dist/index.d.ts', 'default': './dist/index.js'},
                    './all': {'types': './dist/all.d.ts', 'default': './dist/all.js'},
                    './cdn': './dist/icon-monks.js', './cdn-all': './dist/icon-monks.all.js',
                    './icons/*': './dist/icons/*'},
        'files': ['dist'], 'sideEffects': True,
    })
    write(os.path.join(path, 'README.md'), readme_head(
        '@icon-monks/web', npm_badge('@icon-monks/web'),
        f'A dependency-free `<icon-monks>` custom element with {len(ICONS):,} icons in six weights. Works in plain '
        'HTML, Angular, Svelte, Astro, WordPress or anything else that renders HTML.') + f"""
## Install

From a CDN, with no build step:

```html
<script src="https://cdn.jsdelivr.net/npm/@icon-monks/web@{VERSION}"></script>
```

Or from npm, then import it once in your app:

```sh
npm install @icon-monks/web
```

```js
import '@icon-monks/web';
```

## Usage

```html
<icon-monks name="house"></icon-monks>
<icon-monks name="heart" weight="fill" size="32" color="crimson" label="Favorite"></icon-monks>
```

## Attributes

| Attribute | Value | Default |
| --- | --- | --- |
| `name` | Icon name in kebab-case, as on the website | |
| `weight` | `thin` `light` `regular` `bold` `fill` `duotone` | `regular` |
| `size` | Any CSS length | `1em` |
| `color` | Any CSS color | `currentColor` |
| `mirrored` | Present to flip the icon for right-to-left layouts | |
| `label` | Accessible name; without it the icon is hidden from screen readers | |

## How icons load

The script is a few KB. Each icon is fetched the first time a page uses it, about 1 KB per icon and weight, and
cached for the rest of the visit. Files come from `dist/icons/<weight>/<name>.json` next to the script, with the
jsDelivr copy of this version as the fallback.

- **Self-hosting or a strict CSP:** serve a copy of `dist/icons/` and point the element at it with
  `<script src="…/icon-monks.js" data-base="/assets/icon-monks/"></script>`, or `setIconBase('/assets/icon-monks/')`
  when you import the package.
- **Offline, or every icon up front:** use the full bundle instead, which holds every icon in every weight (about
  23 MB): `import '@icon-monks/web/all'`, or the `icon-monks.all.js` script. It also exports the raw `paths`.
""" + README_FOOT)


# ---------------------------------------------------------------------------- fonts
FAMILY = {'thin': 'Thin', 'light': 'Light', 'regular': 'Regular', 'bold': 'Bold', 'fill': 'Fill'}
ASC = 224  # 256-unit em, baseline 32 units above the bottom so icons sit like text


def build_font(weight, cps, out_dir):
    glyphs = {'.notdef': None}
    charstrings, cmap, metrics = {}, {}, {}
    pen = T2CharStringPen(256, None)
    charstrings['.notdef'] = pen.getCharString()
    metrics['.notdef'] = (256, 0)
    for ic in ICONS:
        gname = 'im_' + ic['name'].replace('-', '_')
        pen = T2CharStringPen(256, None)
        parse_path(ic['paths'][weight], TransformPen(pen, (1, 0, 0, -1, 0, ASC)))
        charstrings[gname] = pen.getCharString()
        cmap[cps[ic['name']]] = gname
        metrics[gname] = (256, 0)
        glyphs[gname] = None
    fam = 'Icon Monks' if weight == 'regular' else f'Icon Monks {FAMILY[weight]}'
    ps = f'IconMonks-{FAMILY[weight]}'
    fb = FontBuilder(256, isTTF=False)
    fb.setupGlyphOrder(list(glyphs))
    fb.setupCharacterMap(cmap)
    fb.setupCFF(ps, {'FullName': fam}, charstrings, {})
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ASC, descent=-(256 - ASC))
    fb.setupNameTable({'familyName': fam, 'styleName': 'Regular', 'uniqueFontIdentifier': f'{ps}-{VERSION}',
                       'fullName': fam, 'psName': ps, 'version': f'Version {VERSION}',
                       'copyright': 'Copyright (c) Design Monks. MIT License.'})
    fb.setupOS2(sTypoAscender=ASC, sTypoDescender=-(256 - ASC), usWinAscent=ASC, usWinDescent=256 - ASC)
    fb.setupPost()
    otf = os.path.join(out_dir, f'{ps}.otf')
    fb.save(otf)
    font = TTFont(otf)
    font.flavor = 'woff2'
    font.save(os.path.join(out_dir, f'{ps}.woff2'))
    return fam, ps


def font(cps):
    path = fresh('font')
    out = os.path.join(path, 'dist')
    os.makedirs(out)
    css_all = []
    for w in SOLID_WEIGHTS:
        fam, ps = build_font(w, cps, out)
        cls = 'im' if w == 'regular' else f'im-{w}'
        rules = [f"""@font-face {{
  font-family: '{fam}';
  src: url('./{ps}.woff2') format('woff2'), url('./{ps}.otf') format('opentype');
  font-weight: normal;
  font-style: normal;
  font-display: block;
}}
.{cls} {{
  font-family: '{fam}' !important;
  font-style: normal;
  font-weight: normal;
  font-variant: normal;
  text-transform: none;
  line-height: 1;
  speak: never;
  display: inline-block;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}}"""]
        rules += [f'.{cls}.im-{ic["name"]}::before {{ content: "\\{cps[ic["name"]]:x}"; }}' for ic in ICONS]
        write(os.path.join(out, f'{w}.css'), '\n'.join(rules) + '\n')
        css_all.append(f"@import url('./{w}.css');")
    write(os.path.join(out, 'index.css'), '\n'.join(css_all) + '\n')
    write(os.path.join(out, 'codepoints.json'), json.dumps({k: f'{v:x}' for k, v in cps.items()}, indent=1) + '\n')
    npm_package(path, '@icon-monks/font', 'Icon Monks as icon fonts (OTF + WOFF2) with CSS classes.', {
        'style': './dist/index.css', 'files': ['dist'],
        'exports': {'.': './dist/index.css', './*': './dist/*'},
    })
    write(os.path.join(path, 'README.md'), readme_head(
        '@icon-monks/font', npm_badge('@icon-monks/font'),
        f'Icon Monks as a web font: {len(ICONS):,} icons in five weights (thin, light, regular, bold, fill) as OTF and '
        'WOFF2, with ready-made CSS classes.') + f"""
## Install

From a CDN:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@icon-monks/font@{VERSION}/dist/index.css">
```

Or `npm install @icon-monks/font` and `import '@icon-monks/font';` in your app (or `'@icon-monks/font/bold.css'` for a
single weight).

## Usage

```html
<i class="im im-house"></i>          <!-- regular -->
<i class="im-bold im-house"></i>     <!-- im-thin, im-light, im-bold, im-fill -->
```

Icons size and color with the surrounding text, so `font-size` and `color` style them like any text.

## Notes

- **Smaller downloads:** load only the weights you use with `dist/regular.css`, `dist/bold.css`, and so on.
- **Stable codepoints:** glyphs live in the Private Use Area starting at U+E000 (`dist/codepoints.json`), and
  codepoints never change between releases.
- **No duotone:** fonts are single-color, so duotone is available in the SVG, React, Vue, web component and native
  packages only.
""" + README_FOOT)


# ---------------------------------------------------------------------------- flutter
def flutter(cps):
    path = fresh('flutter')
    fonts = os.path.join(path, 'fonts')
    os.makedirs(fonts)
    for w in SOLID_WEIGHTS:
        shutil.copy(os.path.join(PKG, 'font', 'dist', f'IconMonks-{FAMILY[w]}.otf'), fonts)
    font_yaml = '\n'.join(f"    - family: IconMonks{FAMILY[w]}\n      fonts:\n        - asset: fonts/IconMonks-{FAMILY[w]}.otf"
                          for w in SOLID_WEIGHTS)
    write(os.path.join(path, 'pubspec.yaml'), f"""name: icon_monks
description: Icon Monks for Flutter. 70,000+ open source icons in thin, light, regular, bold and fill weights.
version: {VERSION}
homepage: https://www.iconmonks.co/
repository: https://github.com/designmonks-llc/icon-monks
issue_tracker: https://github.com/designmonks-llc/icon-monks/issues
topics:
  - icons
  - icon-font
  - svg
  - ui
  - design

environment:
  sdk: ">=3.0.0 <4.0.0"
  flutter: ">=3.10.0"

dependencies:
  flutter:
    sdk: flutter

flutter:
  fonts:
{font_yaml}
""")
    # Emitted exactly as `dart format` prints it (pana checks it), as the build job has no Dart SDK:
    # one argument per line with a trailing comma, a blank line before each documented member.
    def const(ic, w, cls, decl):
        title = ic['name'].replace('-', ' ').title()
        return (f"  /// {title} (`{ic['name']}`), {w} weight.\n"
                f"  {decl} {camel(ic['name'])} = {'' if decl.startswith('static') else 'const '}IconData(\n"
                f"    0x{cps[ic['name']]:x},\n    fontFamily: '{cls}',\n    fontPackage: 'icon_monks',\n  );")
    classes = []
    for w in SOLID_WEIGHTS:
        cls = f'IconMonks{FAMILY[w]}'
        consts = '\n\n'.join(const(ic, w, cls, 'final IconData') for ic in ICONS)
        classes.append(f"""/// Icon Monks, {w} weight. Reach it through `IconMonks.{w}`.
class {cls} {{
  const {cls}._();

{consts}
}}""")
    weights = '\n\n'.join(f"  /// The {w} weight: `Icon(IconMonks.{w}.house)`.\n"
                         f"  static const {w} = IconMonks{FAMILY[w]}._();" for w in SOLID_WEIGHTS)
    shorthands = '\n\n'.join(const(ic, 'regular', 'IconMonksRegular', 'static const IconData') for ic in ICONS)
    write(os.path.join(path, 'lib', 'icon_monks.dart'), f"""// GENERATED by scripts/packages.py. Do not edit.

/// Icon Monks for Flutter: {len(ICONS):,} open source icons as [IconData], in
/// thin, light, regular, bold and fill weights.
///
/// Each icon's doc names it in kebab-case (`magnifying-glass`), the name it
/// has on https://www.iconmonks.co/, where you can search and preview it.
library icon_monks;

import 'package:flutter/widgets.dart';

/// Entry point: `Icon(IconMonks.regular.house)` or the shorthand `Icon(IconMonks.house)`.
class IconMonks {{
  const IconMonks._();

{weights}

  // Regular-weight shorthands, usable in const contexts: `const Icon(IconMonks.house)`.
{shorthands}
}}

{(chr(10) * 2).join(classes)}
""")
    flutter_example(path)
    write(os.path.join(path, 'README.md'), """# Icon Monks for Flutter

[![pub version](https://img.shields.io/pub/v/icon_monks)](https://pub.dev/packages/icon_monks)
[![pub points](https://img.shields.io/pub/points/icon_monks)](https://pub.dev/packages/icon_monks/score)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/designmonks-llc/icon-monks/blob/main/LICENSE.md)

![Icon Monks](https://www.iconmonks.co/og-image.png)

%s open source icons for Flutter in five weights: thin, light, regular, bold and fill. Every icon is drawn on
the same 256-unit grid, so they line up with each other and with your text. A product of
[Design Monks](https://monks.company/).

- **One `IconData` per icon and weight**, ready for `Icon`, `IconButton`, `NavigationBar` and anything else that takes an icon.
- **Works on every platform** Flutter supports: Android, iOS, web, macOS, Windows and Linux.
- **Small release builds.** With the `IconMonks.house` shorthands, Flutter's icon tree shaking keeps only the regular
  glyphs your app uses. Using another weight (`IconMonks.bold.house`) bundles that weight's whole font, about 1 MB.
- **No dependencies** beyond Flutter itself.

Browse and search every icon at **[iconmonks.co](https://www.iconmonks.co/)**.

## Install

```sh
flutter pub add icon_monks
```

## Usage

```dart
import 'package:icon_monks/icon_monks.dart';

const Icon(IconMonks.house)                      // regular weight
Icon(IconMonks.bold.heart, color: Colors.red)    // pick a weight
Icon(IconMonks.fill.star, size: 32)
IconButton(icon: Icon(IconMonks.light.gear), onPressed: () {})
```

Icons follow `IconTheme`, so size and color can be set once for a whole subtree:

```dart
IconTheme(
  data: const IconThemeData(size: 20, color: Colors.indigo),
  child: Row(children: [Icon(IconMonks.regular.house), Icon(IconMonks.regular.bell)]),
)
```

## Weights

| Weight | Access | Notes |
| --- | --- | --- |
| Regular | `IconMonks.house` or `IconMonks.regular.house` | The shorthand works in `const` widgets |
| Thin | `IconMonks.thin.house` | |
| Light | `IconMonks.light.house` | |
| Bold | `IconMonks.bold.house` | |
| Fill | `IconMonks.fill.house` | Solid shapes |

Duotone is not included, because icon fonts are single-color. For duotone, use the SVG files from
[iconmonks.co](https://www.iconmonks.co/) with `flutter_svg`.

## Icon names

Names on the site are kebab-case; in Dart they are camelCase. `arrow-right` becomes `IconMonks.arrowRight`,
`calendar-check` becomes `IconMonks.calendarCheck`. Brand logos end in `Logo`, for example `IconMonks.githubLogo`.

## Links

- [Website and icon search](https://www.iconmonks.co/)
- [Source code](https://github.com/designmonks-llc/icon-monks)
- [Request an icon or report a bug](https://github.com/designmonks-llc/icon-monks/issues)

MIT licensed. A product of [Design Monks](https://monks.company/).
""" % f'{len(ICONS):,}')
    write(os.path.join(path, 'CHANGELOG.md'), CHANGELOG)


def flutter_example(path):
    # pub.dev wants an example/; written as `dart format` prints it, like lib/.
    example = os.path.join(path, 'example')
    shutil.rmtree(os.path.join(example, 'lib'), ignore_errors=True)
    write(os.path.join(example, 'pubspec.yaml'), """name: icon_monks_example
description: Shows Icon Monks icons in every weight.
publish_to: none

environment:
  sdk: ">=3.0.0 <4.0.0"
  flutter: ">=3.10.0"

dependencies:
  flutter:
    sdk: flutter
  icon_monks:
    path: ../
""")
    write(os.path.join(example, '.gitignore'), '.dart_tool/\nbuild/\npubspec.lock\n')
    write(os.path.join(example, 'lib', 'main.dart'), """// GENERATED by scripts/packages.py. Do not edit.
import 'package:flutter/material.dart';
import 'package:icon_monks/icon_monks.dart';

void main() => runApp(const IconMonksExample());

/// Shows a few icons in every weight.
class IconMonksExample extends StatelessWidget {
  const IconMonksExample({super.key});

  @override
  Widget build(BuildContext context) {
    final weights = <String, List<IconData>>{
      'thin': [
        IconMonks.thin.house,
        IconMonks.thin.heart,
        IconMonks.thin.star,
        IconMonks.thin.gear,
        IconMonks.thin.bell,
      ],
      'light': [
        IconMonks.light.house,
        IconMonks.light.heart,
        IconMonks.light.star,
        IconMonks.light.gear,
        IconMonks.light.bell,
      ],
      'regular': [
        IconMonks.house,
        IconMonks.heart,
        IconMonks.star,
        IconMonks.gear,
        IconMonks.bell,
      ],
      'bold': [
        IconMonks.bold.house,
        IconMonks.bold.heart,
        IconMonks.bold.star,
        IconMonks.bold.gear,
        IconMonks.bold.bell,
      ],
      'fill': [
        IconMonks.fill.house,
        IconMonks.fill.heart,
        IconMonks.fill.star,
        IconMonks.fill.gear,
        IconMonks.fill.bell,
      ],
    };
    return MaterialApp(
      title: 'Icon Monks',
      home: Scaffold(
        appBar: AppBar(title: const Text('Icon Monks')),
        body: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            for (final entry in weights.entries)
              ListTile(
                title: Text(entry.key),
                subtitle: Row(
                  children: [
                    for (final icon in entry.value)
                      Padding(
                        padding: const EdgeInsets.all(8),
                        child: Icon(icon, size: 32),
                      ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
""")


# ---------------------------------------------------------------------------- android
def android():
    path = fresh('android')
    res = os.path.join(path, 'src', 'main', 'res', 'drawable')
    os.makedirs(res)
    src = os.path.join(path, 'src', 'main', 'java', 'com', 'designmonks', 'icons')
    for w in WEIGHTS:
        suffix = '' if w == 'regular' else f'_{w}'
        obj = pascal(w)
        for ic in ICONS:
            base = 'im_' + ic['name'].replace('-', '_') + suffix
            d = ic['paths'][w]
            if w == 'duotone':
                xml_paths = (f'  <path android:fillColor="@android:color/white" android:fillAlpha="{DUO}" android:pathData="{d[0]}"/>\n'
                             if d[0] else '') + f'  <path android:fillColor="@android:color/white" android:pathData="{d[1]}"/>\n'
                args = (f'"{d[0]}", ' if d[0] else '"", ') + f'"{d[1]}", duotone = true'
            else:
                xml_paths = f'  <path android:fillColor="@android:color/white" android:pathData="{d}"/>\n'
                args = f'"{d}"'
            write(os.path.join(res, base + '.xml'),
                  '<?xml version="1.0" encoding="utf-8"?>\n'
                  '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
                  '  android:width="24dp" android:height="24dp"\n'
                  '  android:viewportWidth="256" android:viewportHeight="256"\n'
                  '  android:tint="?android:attr/colorControlNormal" android:autoMirrored="false">\n' + xml_paths + '</vector>\n')
            n = pascal(ic['name'])
            # One file per icon (like material-icons-extended) keeps each class small for the Kotlin compiler.
            write(os.path.join(src, w, n + '.kt'), f"""// GENERATED by scripts/packages.py. Do not edit.
package com.designmonks.icons.{w}

import androidx.compose.ui.graphics.vector.ImageVector
import com.designmonks.icons.IconMonks
import com.designmonks.icons.iconMonksVector

private var cache: ImageVector? = null

val IconMonks.{obj}.{n}: ImageVector
    get() = cache ?: iconMonksVector("{n}{obj}", {args}).also {{ cache = it }}
""")
    objects = '\n'.join(f'    object {pascal(w)}' for w in WEIGHTS)
    write(os.path.join(src, 'IconMonks.kt'), f"""// GENERATED by scripts/packages.py. Do not edit.
package com.designmonks.icons

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.PathParser
import androidx.compose.ui.unit.dp

/**
 * Icon Monks for Jetpack Compose. Each icon is an extension property in the package for its weight:
 * `import com.designmonks.icons.regular.House` then `Icon(IconMonks.Regular.House, contentDescription = null)`.
 */
object IconMonks {{
{objects}
}}

/** Builds an icon from outline path data; duotone takes (tint, solid). Internal to the generated icons. */
fun iconMonksVector(name: String, vararg paths: String, duotone: Boolean = false): ImageVector {{
    val builder = ImageVector.Builder(
        name = name, defaultWidth = 24.dp, defaultHeight = 24.dp, viewportWidth = 256f, viewportHeight = 256f,
    )
    paths.forEachIndexed {{ i, d ->
        if (d.isNotEmpty()) builder.addPath(
            pathData = PathParser().parsePathString(d).toNodes(),
            fill = SolidColor(Color.Black),
            fillAlpha = if (duotone && i == 0) {DUO}f else 1f,
        )
    }}
    return builder.build()
}}
""")
    write(os.path.join(path, 'src', 'main', 'AndroidManifest.xml'), '<manifest />\n')
    write(os.path.join(path, 'settings.gradle.kts'), """pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositories { google(); mavenCentral() }
}
rootProject.name = "icon-monks"
""")
    write(os.path.join(path, 'gradle.properties'), 'android.useAndroidX=true\norg.gradle.jvmargs=-Xmx4g\nkotlin.code.style=official\n')
    write(os.path.join(path, 'build.gradle.kts'), f"""plugins {{
    id("com.android.library") version "8.5.2"
    id("org.jetbrains.kotlin.android") version "2.0.20"
    id("org.jetbrains.kotlin.plugin.compose") version "2.0.20"
    `maven-publish`
}}

android {{
    namespace = "com.designmonks.icons"
    compileSdk = 34
    defaultConfig {{ minSdk = 21 }}
    buildFeatures {{ compose = true }}
    kotlinOptions {{ jvmTarget = "17" }}
    compileOptions {{
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }}
    publishing {{ singleVariant("release") }}
}}

dependencies {{
    api(platform("androidx.compose:compose-bom:2024.09.00"))
    api("androidx.compose.ui:ui")
}}

afterEvaluate {{
    publishing {{
        publications {{
            create<MavenPublication>("release") {{
                from(components["release"])
                groupId = "com.github.designmonks-llc"
                artifactId = "icon-monks"
                version = System.getenv("VERSION") ?: "{VERSION}"
            }}
        }}
    }}
}}
""")
    write(os.path.join(path, 'README.md'), readme_head(
        'Icon Monks for Android',
        '[![JitPack](https://jitpack.io/v/designmonks-llc/icon-monks.svg)](https://jitpack.io/#designmonks-llc/icon-monks)',
        f'{len(ICONS):,} icons for Android in six weights, as Jetpack Compose `ImageVector`s and classic XML '
        '`VectorDrawable`s, both in one library.') + f"""
## Install

The library is published through JitPack. Add the repository and the dependency:

```kotlin
// settings.gradle.kts
dependencyResolutionManagement {{ repositories {{ google(); mavenCentral(); maven("https://jitpack.io") }} }}

// app/build.gradle.kts
implementation("com.github.designmonks-llc:icon-monks:v{VERSION}")
```

## Jetpack Compose

Each icon is an extension property in its weight's package, so only the icons you import are compiled into your app.

```kotlin
import com.designmonks.icons.IconMonks
import com.designmonks.icons.regular.House
import com.designmonks.icons.bold.Heart
import com.designmonks.icons.duotone.Star

Icon(IconMonks.Regular.House, contentDescription = "Home")
Icon(IconMonks.Bold.Heart, contentDescription = null, tint = Color.Red)
Icon(IconMonks.Duotone.Star, contentDescription = null)
```

Weights: `Thin`, `Light`, `Regular`, `Bold`, `Fill` and `Duotone`.

## Views and XML

VectorDrawables are named `im_<name>` for regular and `im_<name>_<weight>` for the other weights.

```xml
<ImageView android:src="@drawable/im_house" app:tint="@color/brand" />
<ImageView android:src="@drawable/im_heart_fill" />
```

Drawables use `?android:attr/colorControlNormal` as their tint, matching Material icons. Copy `src/main/res/drawable` into
your app if you only need a few icons.

## Icon names

Names on the website are kebab-case. In Compose they are PascalCase (`arrow-right` is `ArrowRight`), and in XML they
are snake_case with the `im_` prefix (`im_arrow_right`).
""" + README_FOOT)


# ---------------------------------------------------------------------------- swift
def swift():
    path = fresh('swift')
    cat = os.path.join(path, 'Sources', 'IconMonks', 'Resources', 'IconMonks.xcassets')
    write(os.path.join(cat, 'Contents.json'), json.dumps({'info': {'author': 'xcode', 'version': 1}}, indent=2) + '\n')
    for w in WEIGHTS:
        for ic in ICONS:
            name = f'{ic["name"]}-{w}'
            iset = os.path.join(cat, f'{name}.imageset')
            shutil.copy(os.path.join(ROOT, 'svg', w, ic['name'] + ('' if w == 'regular' else f'-{w}') + '.svg'),
                        os.path.join(iset, f'{name}.svg') if os.path.isdir(iset) else _mk(iset, f'{name}.svg'))
            write(os.path.join(iset, 'Contents.json'), json.dumps({
                'images': [{'filename': f'{name}.svg', 'idiom': 'universal'}],
                'info': {'author': 'xcode', 'version': 1},
                'properties': {'preserves-vector-representation': True, 'template-rendering-intent': 'template'},
            }, indent=2) + '\n')
    swift_kw = {'repeat', 'return', 'switch', 'case', 'default', 'import', 'in', 'is', 'as', 'do', 'for', 'if', 'else',
                'while', 'break', 'continue', 'class', 'struct', 'enum', 'func', 'let', 'var', 'self', 'super', 'true',
                'false', 'nil', 'init', 'where', 'throw', 'try', 'catch', 'guard', 'defer', 'static', 'protocol', 'extension'}
    sid = lambda n: f'`{n}`' if n in swift_kw else n
    cases = '\n'.join(f'    case {sid(camel(ic["name"]))} = "{ic["name"]}"' for ic in ICONS)
    write(os.path.join(path, 'Sources', 'IconMonks', 'IconMonks.swift'), f"""// GENERATED by scripts/packages.py. Do not edit.
import SwiftUI
#if canImport(UIKit)
import UIKit
#elseif canImport(AppKit)
import AppKit
#endif

public enum IconMonkWeight: String, CaseIterable, Sendable {{
    case thin, light, regular, bold, fill, duotone
}}

public enum IconMonk: String, CaseIterable, Sendable {{
{cases}

    /// Asset catalog name for this icon in the given weight.
    public func assetName(_ weight: IconMonkWeight = .regular) -> String {{ "\\(rawValue)-\\(weight.rawValue)" }}

    /// A template SwiftUI image; size it with `.resizable().frame(...)` and colour it with `.foregroundStyle(...)`.
    public func image(_ weight: IconMonkWeight = .regular) -> Image {{
        Image(assetName(weight), bundle: .module).renderingMode(.template)
    }}

    #if canImport(UIKit)
    public func uiImage(_ weight: IconMonkWeight = .regular) -> UIImage? {{
        UIImage(named: assetName(weight), in: .module, with: nil)?.withRenderingMode(.alwaysTemplate)
    }}
    #elseif canImport(AppKit)
    public func nsImage(_ weight: IconMonkWeight = .regular) -> NSImage? {{
        Bundle.module.image(forResource: assetName(weight))
    }}
    #endif
}}

public extension Image {{
    /// `Image(iconMonks: .house, weight: .bold)`
    init(iconMonks icon: IconMonk, weight: IconMonkWeight = .regular) {{
        self = icon.image(weight)
    }}
}}

/// An icon that scales with Dynamic Type, like text does.
///
/// `IconMonkImage(.house, weight: .bold, size: 24)` is 24 points at the default text size and grows or shrinks
/// with the user's text size setting, following the `relativeTo` text style (`.body` by default).
public struct IconMonkImage: View {{
    private let icon: IconMonk
    private let weight: IconMonkWeight
    @ScaledMetric private var size: CGFloat

    public init(_ icon: IconMonk, weight: IconMonkWeight = .regular, size: CGFloat = 24,
                relativeTo textStyle: Font.TextStyle = .body) {{
        self.icon = icon
        self.weight = weight
        self._size = ScaledMetric(wrappedValue: size, relativeTo: textStyle)
    }}

    public var body: some View {{
        icon.image(weight)
            .resizable()
            .aspectRatio(contentMode: .fit)
            .frame(width: size, height: size)
    }}
}}
""")
    # SwiftPM needs the manifest at the repository root.
    if os.path.exists(os.path.join(path, 'Package.swift')):
        os.remove(os.path.join(path, 'Package.swift'))
    write(os.path.join(ROOT, 'Package.swift'), """// swift-tools-version:5.7
import PackageDescription

let package = Package(
    name: "IconMonks",
    platforms: [.iOS(.v14), .macOS(.v11), .tvOS(.v14), .watchOS(.v7)],
    products: [.library(name: "IconMonks", targets: ["IconMonks"])],
    targets: [.target(name: "IconMonks", path: "packages/swift/Sources/IconMonks", resources: [.process("Resources")])]
)
""")
    write(os.path.join(path, 'README.md'), readme_head(
        'Icon Monks for iOS, macOS, tvOS and watchOS',
        '[![Swift Package Manager](https://img.shields.io/badge/Swift_Package_Manager-compatible-orange)]'
        f'({REPO})\n[![release](https://img.shields.io/github/v/release/designmonks-llc/icon-monks)]({REPO}/releases)',
        f'{len(ICONS):,} icons for SwiftUI and UIKit in six weights, including duotone, as a Swift package. Vector assets '
        'that stay sharp at any size and take the tint color, just like SF Symbols.') + """
## Install

In Xcode choose **File > Add Package Dependencies** and enter `https://github.com/designmonks-llc/icon-monks`, or add it
to `Package.swift`:

```swift
.package(url: "https://github.com/designmonks-llc/icon-monks", from: "%s")
```

Requires iOS 14, macOS 11, tvOS 14 or watchOS 7.

## SwiftUI

```swift
import IconMonks

Image(iconMonks: .house)
    .resizable()
    .frame(width: 24, height: 24)
    .foregroundStyle(.purple)              // iOS 15+; use .foregroundColor(.purple) on iOS 14

Image(iconMonks: .heart, weight: .fill)
```

Icon names are the same in every weight, so changing the look is one parameter, never a rename.

### Dynamic Type

`IconMonkImage` scales with the user's text size, so icons grow alongside your labels at accessibility sizes:

```swift
IconMonkImage(.house)                                   // 24 pt at the default text size, scales like .body
IconMonkImage(.bell, weight: .bold, size: 20, relativeTo: .headline)
    .foregroundStyle(.purple)

Label { Text("Home") } icon: { IconMonkImage(.house, size: 17) }
```

## UIKit and AppKit

```swift
let tabIcon = IconMonk.gear.uiImage(.bold)    // UIKit
let menuIcon = IconMonk.gear.nsImage(.light)  // AppKit
```

Weights: `.thin`, `.light`, `.regular`, `.bold`, `.fill` and `.duotone`. Names on the website are kebab-case; in Swift
they are camelCase, so `arrow-right` is `IconMonk.arrowRight`. `IconMonk.allCases` lists every icon.
""" % VERSION + README_FOOT)


def _mk(directory, filename):
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, filename)


def main():
    cps = codepoints()
    core()
    react()
    vue()
    web()
    font(cps)
    flutter(cps)
    android()
    swift()
    print(f'generated packages for {len(ICONS)} icons, v{VERSION}')


if __name__ == '__main__':
    main()
