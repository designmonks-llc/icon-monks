# @monks-icons/core

Framework-free Monks Icons: 97 icons in 6 weights as SVG files, SVG sprites and path data.

```sh
npm install @monks-icons/core
```

```js
import { toSvg, icons } from '@monks-icons/core';
document.body.innerHTML = toSvg('house', { weight: 'bold', size: 32, color: '#6d28d9' });
```

- `assets/<weight>/<name>[-<weight>].svg`: one file per icon (`regular` has no suffix)
- `dist/sprite/<weight>.svg`: `<svg><use href="sprite/regular.svg#house"/></svg>`
- `dist/icons.json`: names, categories and tags for search
