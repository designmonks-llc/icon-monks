# @icon-monks/web

[![npm](https://img.shields.io/npm/v/@icon-monks/web)](https://www.npmjs.com/package/@icon-monks/web)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/designmonks-llc/icon-monks/blob/main/LICENSE.md)

![Icon Monks](https://www.iconmonks.co/og-image.png)

A dependency-free `<icon-monks>` custom element with 6,054 icons in six weights. Works in plain HTML, Angular, Svelte, Astro, WordPress or anything else that renders HTML. A product of [Design Monks](https://monks.company/). Browse and search every icon at
**[iconmonks.co](https://www.iconmonks.co/)**.

## Install

From a CDN, with no build step:

```html
<script src="https://cdn.jsdelivr.net/npm/@icon-monks/web@0.4.2"></script>
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

## Links

- [Website and icon search](https://www.iconmonks.co/)
- [All platforms and source code](https://github.com/designmonks-llc/icon-monks)
- [Request an icon or report a bug](https://github.com/designmonks-llc/icon-monks/issues)

MIT licensed. A product of [Design Monks](https://monks.company/).
