# @icon-monks/font

[![npm](https://img.shields.io/npm/v/@icon-monks/font)](https://www.npmjs.com/package/@icon-monks/font)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/designmonks-llc/icon-monks/blob/main/LICENSE.md)

![Icon Monks](https://www.iconmonks.co/og-image.png)

Icon Monks as a web font: 6,054 icons in five weights (thin, light, regular, bold, fill) as OTF and WOFF2, with ready-made CSS classes. A product of [Design Monks](https://www.designmonks.co). Browse and search every icon at
**[iconmonks.co](https://www.iconmonks.co/)**.

## Install

From a CDN:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@icon-monks/font@0.4.2/dist/index.css">
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

## Links

- [Website and icon search](https://www.iconmonks.co/)
- [All platforms and source code](https://github.com/designmonks-llc/icon-monks)
- [Request an icon or report a bug](https://github.com/designmonks-llc/icon-monks/issues)

MIT licensed. A product of [Design Monks](https://www.designmonks.co).
