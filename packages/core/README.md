# @icon-monks/core

Framework-free Icon Monks: 6008 icons in 6 weights as SVG files, SVG sprites and path data.

```sh
npm install @icon-monks/core
```

```js
import { toSvg, icons } from '@icon-monks/core';
document.body.innerHTML = toSvg('house', { weight: 'bold', size: 32, color: '#6d28d9' });
```

- `assets/<weight>/<name>[-<weight>].svg`: one file per icon (`regular` has no suffix)
- `dist/sprite/<weight>.svg`: `<svg><use href="sprite/regular.svg#house"/></svg>`
- `dist/icons.json`: names, categories and tags for search
