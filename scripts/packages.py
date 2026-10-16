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
LICENSE = open(os.path.join(ROOT, 'LICENSE')).read()
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
        'author': 'Design Monks', 'homepage': 'https://designmonks.github.io/icon-monks/',
        'repository': {'type': 'git', 'url': 'git+https://github.com/designmonks/icon-monks.git'},
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
    write(os.path.join(path, 'README.md'), f"""# @icon-monks/core

Framework-free Icon Monks: {len(ICONS)} icons in {len(WEIGHTS)} weights as SVG files, SVG sprites and path data.

```sh
npm install @icon-monks/core
```

```js
import {{ toSvg, icons }} from '@icon-monks/core';
document.body.innerHTML = toSvg('house', {{ weight: 'bold', size: 32, color: '#6d28d9' }});
```

- `assets/<weight>/<name>[-<weight>].svg`: one file per icon (`regular` has no suffix)
- `dist/sprite/<weight>.svg`: `<svg><use href="sprite/regular.svg#house"/></svg>`
- `dist/icons.json`: names, categories and tags for search
""")


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
    write(os.path.join(path, 'README.md'), """# @icon-monks/react

```sh
npm install @icon-monks/react
```

```jsx
import { House, Heart, IconContext } from '@icon-monks/react';

<House />                                   // 1em, currentColor, regular
<Heart size={32} color="crimson" weight="fill" />

<IconContext.Provider value={{ size: 24, weight: 'duotone' }}>
  <House /> <Heart />
</IconContext.Provider>
```

Props: `size`, `color`, `weight` (`thin` `light` `regular` `bold` `fill` `duotone`), `mirrored`, plus any SVG attribute.
Every icon is also exported with an `Icon` suffix (`HouseIcon`) and as a deep import (`@icon-monks/react/icons/House`).
""")


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
    write(os.path.join(path, 'README.md'), """# @icon-monks/vue

```sh
npm install @icon-monks/vue
```

```vue
<script setup>
import { House, Heart, IconContextKey } from '@icon-monks/vue';
import { provide } from 'vue';
provide(IconContextKey, { size: 24, weight: 'bold' }); // optional defaults for descendants
</script>

<template>
  <House />
  <Heart :size="32" color="crimson" weight="fill" />
</template>
```
""")


# ---------------------------------------------------------------------------- web component
WEB_ELEMENT = """
const ATTRS = ['name', 'weight', 'size', 'color', 'mirrored', 'label'];

function render(el) {
  const name = el.getAttribute('name');
  const icon = PATHS[name];
  if (!icon) { el.innerHTML = ''; return; }
  const weight = el.getAttribute('weight') || 'regular';
  const size = el.getAttribute('size') || '1em';
  const color = el.getAttribute('color') || 'currentColor';
  const label = el.getAttribute('label');
  const d = icon[weight] || icon.regular;
  const body = weight === 'duotone'
    ? (d[0] ? '<path d="' + d[0] + '" opacity="%s"/>' : '') + '<path d="' + d[1] + '"/>'
    : '<path d="' + d + '"/>';
  const flip = el.hasAttribute('mirrored') ? ' transform="scale(-1, 1)"' : '';
  el.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="' + size + '" height="' + size +
    '" viewBox="0 0 256 256" fill="' + color + '"' + flip + ' style="display:block">' + body + '</svg>';
  if (label) { el.setAttribute('role', 'img'); el.setAttribute('aria-label', label); }
  else { el.setAttribute('aria-hidden', 'true'); }
}

class IconMonkElement extends HTMLElement {
  static get observedAttributes() { return ATTRS; }
  connectedCallback() { this.style.display ||= 'inline-block'; this.style.lineHeight ||= '0'; render(this); }
  attributeChangedCallback() { if (this.isConnected) render(this); }
}

if (typeof customElements !== 'undefined' && !customElements.get('icon-monks')) {
  customElements.define('icon-monks', IconMonkElement);
}
""" % DUO


def web():
    path = fresh('web')
    data = f"const PATHS = {json.dumps(PATHS, separators=(',', ':'))};\n"
    write(os.path.join(path, 'dist', 'index.js'),
          data + WEB_ELEMENT + "\nexport { IconMonkElement, PATHS as paths };\n")
    write(os.path.join(path, 'dist', 'icon-monks.js'), '(function () {\n' + data + WEB_ELEMENT + '})();\n')
    write(os.path.join(path, 'dist', 'index.d.ts'), """export declare class IconMonkElement extends HTMLElement {}
export declare const paths: Record<string, Record<string, string | [string, string]>>;
declare global { interface HTMLElementTagNameMap { 'icon-monks': IconMonkElement; } }
""")
    npm_package(path, '@icon-monks/web', 'Icon Monks as a <icon-monks> custom element. Works in any framework or plain HTML.', {
        'type': 'module', 'main': './dist/index.js', 'types': './dist/index.d.ts', 'unpkg': './dist/icon-monks.js',
        'jsdelivr': './dist/icon-monks.js', 'exports': {'.': {'types': './dist/index.d.ts', 'default': './dist/index.js'},
                                                          './cdn': './dist/icon-monks.js'},
        'files': ['dist'], 'sideEffects': True,
    })
    write(os.path.join(path, 'README.md'), f"""# @icon-monks/web

A dependency-free `<icon-monks>` custom element for plain HTML, Angular, Svelte, Astro, WordPress or anything else.

```html
<script src="https://cdn.jsdelivr.net/npm/@icon-monks/web@{VERSION}"></script>

<icon-monks name="house"></icon-monks>
<icon-monks name="heart" weight="fill" size="32" color="crimson" label="Favorite"></icon-monks>
```

Or `npm install @icon-monks/web` and `import '@icon-monks/web';` once in your app.

Attributes: `name`, `weight`, `size`, `color`, `mirrored`, `label` (sets an accessible name; icons are hidden from screen readers otherwise).
""")


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
    write(os.path.join(path, 'README.md'), f"""# @icon-monks/font

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@icon-monks/font@{VERSION}/dist/index.css">

<i class="im im-house"></i>          <!-- regular -->
<i class="im-bold im-house"></i>     <!-- thin, light, bold, fill: im-thin / im-light / im-bold / im-fill -->
```

Load only the weights you use with `dist/regular.css`, `dist/bold.css`, and so on. Glyphs live in the Private Use Area
starting at U+E000 (`dist/codepoints.json`); codepoints never change between releases. Fonts are single-colour, so the
duotone weight is available in the SVG, React, Vue, web component and native packages only.
""")


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
description: Icon Monks for Flutter. {len(ICONS)} open source icons in thin, light, regular, bold and fill weights.
version: {VERSION}
homepage: https://designmonks.github.io/icon-monks/
repository: https://github.com/designmonks/icon-monks
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
    classes = []
    for w in SOLID_WEIGHTS:
        cls = f'IconMonks{FAMILY[w]}'
        consts = '\n'.join(f"  final IconData {camel(ic['name'])} = const IconData(0x{cps[ic['name']]:x}, "
                           f"fontFamily: '{cls}', fontPackage: 'icon_monks');" for ic in ICONS)
        classes.append(f"""/// Icon Monks, {w} weight.
class {cls} {{
  const {cls}._();
{consts}
}}""")
    write(os.path.join(path, 'lib', 'icon_monks.dart'), f"""// GENERATED by scripts/packages.py. Do not edit.
library icon_monks;

import 'package:flutter/widgets.dart';

/// Entry point: `Icon(IconMonks.regular.house)` or the shorthand `Icon(IconMonks.house)`.
class IconMonks {{
  const IconMonks._();
  static const thin = IconMonksThin._();
  static const light = IconMonksLight._();
  static const regular = IconMonksRegular._();
  static const bold = IconMonksBold._();
  static const fill = IconMonksFill._();

  // Regular-weight shorthands, usable in const contexts: `const Icon(IconMonks.house)`.
{chr(10).join(f"  static const IconData {camel(ic['name'])} = IconData(0x{cps[ic['name']]:x}, fontFamily: 'IconMonksRegular', fontPackage: 'icon_monks');" for ic in ICONS)}
}}

{chr(10).join(classes)}
""")
    write(os.path.join(path, 'README.md'), """# icon_monks

```yaml
dependencies:
  icon_monks: ^%s
```

```dart
import 'package:icon_monks/icon_monks.dart';

Icon(IconMonks.house)                         // regular
Icon(IconMonks.bold.heart, color: Colors.red)
Icon(IconMonks.fill.star, size: 32)
```

Weights: `thin`, `light`, `regular`, `bold`, `fill`. Icon fonts are single-colour, so duotone is not offered here.
""" % VERSION)
    write(os.path.join(path, 'CHANGELOG.md'), f'## {VERSION}\n\n- {len(ICONS)} icons in {len({i["category"] for i in ICONS})} categories, six weights each.\n\n'
          '## 0.2.0\n\n- Adds 400 icons (497 total) across 22 categories.\n\n## 0.1.0\n\n- Initial release with 97 icons.\n'
          if VERSION != '0.2.0' else
          f'## 0.2.0\n\n- Adds 400 icons ({len(ICONS)} total) across {len({i["category"] for i in ICONS})} categories.\n\n## 0.1.0\n\n- Initial release with 97 icons.\n')


# ---------------------------------------------------------------------------- android
def android():
    path = fresh('android')
    res = os.path.join(path, 'src', 'main', 'res', 'drawable')
    os.makedirs(res)
    kt = []
    for w in WEIGHTS:
        suffix = '' if w == 'regular' else f'_{w}'
        obj = pascal(w)
        vals = []
        for ic in ICONS:
            base = 'im_' + ic['name'].replace('-', '_') + suffix
            d = ic['paths'][w]
            if w == 'duotone':
                xml_paths = (f'  <path android:fillColor="@android:color/white" android:fillAlpha="{DUO}" android:pathData="{d[0]}"/>\n'
                             if d[0] else '') + f'  <path android:fillColor="@android:color/white" android:pathData="{d[1]}"/>\n'
                kt_paths = ((f'.addPath(pathData = nodes("{d[0]}"), fill = SolidColor(Color.Black), fillAlpha = {DUO}f)\n            '
                             if d[0] else '') + f'.addPath(pathData = nodes("{d[1]}"), fill = SolidColor(Color.Black))')
            else:
                xml_paths = f'  <path android:fillColor="@android:color/white" android:pathData="{d}"/>\n'
                kt_paths = f'.addPath(pathData = nodes("{d}"), fill = SolidColor(Color.Black))'
            write(os.path.join(res, base + '.xml'),
                  '<?xml version="1.0" encoding="utf-8"?>\n'
                  '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
                  '  android:width="24dp" android:height="24dp"\n'
                  '  android:viewportWidth="256" android:viewportHeight="256"\n'
                  '  android:tint="?android:attr/colorControlNormal" android:autoMirrored="false">\n' + xml_paths + '</vector>\n')
            vals.append(f"""    val {pascal(ic['name'])}: ImageVector by lazy {{
        ImageVector.Builder(
            name = "{pascal(ic['name'])}{obj}", defaultWidth = 24.dp, defaultHeight = 24.dp,
            viewportWidth = 256f, viewportHeight = 256f,
        )
            {kt_paths}
            .build()
    }}""")
        kt.append(f'    object {obj} {{\n' + '\n\n'.join(vals) + '\n    }')
    write(os.path.join(path, 'src', 'main', 'java', 'com', 'designmonks', 'icons', 'IconMonks.kt'),
          """// GENERATED by scripts/packages.py. Do not edit.
package com.designmonks.icons

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.PathNode
import androidx.compose.ui.graphics.vector.PathParser
import androidx.compose.ui.unit.dp

/** Icon Monks for Jetpack Compose: `Icon(IconMonks.Regular.House, contentDescription = null)`. */
object IconMonks {
    private fun nodes(d: String): List<PathNode> = PathParser().parsePathString(d).toNodes()

""" + '\n\n'.join(kt) + '\n}\n')
    write(os.path.join(path, 'src', 'main', 'AndroidManifest.xml'), '<manifest />\n')
    write(os.path.join(path, 'settings.gradle.kts'), """pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositories { google(); mavenCentral() }
}
rootProject.name = "icon-monks"
""")
    write(os.path.join(path, 'gradle.properties'), 'android.useAndroidX=true\norg.gradle.jvmargs=-Xmx2g\nkotlin.code.style=official\n')
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
                groupId = "com.github.designmonks"
                artifactId = "icon-monks"
                version = System.getenv("VERSION") ?: "{VERSION}"
            }}
        }}
    }}
}}
""")
    write(os.path.join(path, 'README.md'), f"""# Icon Monks for Android

Published through JitPack. Add the repository and the dependency:

```kotlin
// settings.gradle.kts
dependencyResolutionManagement {{ repositories {{ google(); mavenCentral(); maven("https://jitpack.io") }} }}

// app/build.gradle.kts
implementation("com.github.designmonks:icon-monks:v{VERSION}")
```

Two ways to use the icons, both in this library:

**Jetpack Compose**

```kotlin
import com.designmonks.icons.IconMonks

Icon(IconMonks.Regular.House, contentDescription = "Home")
Icon(IconMonks.Bold.Heart, contentDescription = null, tint = Color.Red)
Icon(IconMonks.Duotone.Star, contentDescription = null)
```

**Views / XML**: VectorDrawables named `im_<name>` (regular) and `im_<name>_<weight>`.

```xml
<ImageView android:src="@drawable/im_house" app:tint="@color/brand" />
<ImageView android:src="@drawable/im_heart_fill" />
```

Drawables use `?android:attr/colorControlNormal` as their tint, matching Material icons. Copy `src/main/res/drawable` into
your app if you only need a few icons.
""")


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
    write(os.path.join(path, 'README.md'), """# Icon Monks for iOS, macOS, tvOS and watchOS

In Xcode choose File > Add Package Dependencies and enter `https://github.com/designmonks/icon-monks`, or in
`Package.swift`:

```swift
.package(url: "https://github.com/designmonks/icon-monks", from: "%s")
```
""" % VERSION + """
```swift
import IconMonks

Image(iconMonks: .house)
    .resizable()
    .frame(width: 24, height: 24)
    .foregroundStyle(.purple)

Image(iconMonks: .heart, weight: .fill)
let tabIcon = IconMonk.gear.uiImage(.bold)   // UIKit
```

Icons ship as vector SVG assets (preserved vector data, template rendering), so they stay sharp at any size and take
the tint colour like SF Symbols. All six weights, including duotone, are available.
""")


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
