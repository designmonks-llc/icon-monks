# @icon-monks/core

[![npm](https://img.shields.io/npm/v/@icon-monks/core)](https://www.npmjs.com/package/@icon-monks/core)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/designmonks-llc/icon-monks/blob/main/LICENSE.md)

![Icon Monks](https://www.iconmonks.co/og-image.png)

Framework-free Icon Monks: 6,054 icons in 6 weights (thin, light, regular, bold, fill, duotone) as SVG files, SVG sprites and path data, for any framework or build tool. A product of [Design Monks](https://monks.company/). Browse and search every icon at
**[iconmonks.co](https://www.iconmonks.co/)**.

## Install

```sh
npm install @icon-monks/core
```

## Usage

```js
import { toSvg, icons, weights } from '@icon-monks/core';

document.body.innerHTML = toSvg('house', { weight: 'bold', size: 32, color: '#6d28d9' });
toSvg('heart', { title: 'Favorite' });   // adds an accessible <title>
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

## Links

- [Website and icon search](https://www.iconmonks.co/)
- [All platforms and source code](https://github.com/designmonks-llc/icon-monks)
- [Request an icon or report a bug](https://github.com/designmonks-llc/icon-monks/issues)

MIT licensed. A product of [Design Monks](https://monks.company/).
