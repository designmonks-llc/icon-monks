# @icon-monks/font

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@icon-monks/font@0.1.0/dist/index.css">

<i class="im im-house"></i>          <!-- regular -->
<i class="im-bold im-house"></i>     <!-- thin, light, bold, fill: im-thin / im-light / im-bold / im-fill -->
```

Load only the weights you use with `dist/regular.css`, `dist/bold.css`, and so on. Glyphs live in the Private Use Area
starting at U+E000 (`dist/codepoints.json`); codepoints never change between releases. Fonts are single-colour, so the
duotone weight is available in the SVG, React, Vue, web component and native packages only.
