# @icon-monks/react

[![npm](https://img.shields.io/npm/v/@icon-monks/react)](https://www.npmjs.com/package/@icon-monks/react)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/designmonks-llc/icon-monks/blob/main/LICENSE.md)

![Icon Monks](https://www.iconmonks.co/og-image.png)

6,054 React icon components in six weights: thin, light, regular, bold, fill and duotone. Typed, tree-shakeable, and server-rendering friendly. A product of [Design Monks](https://monks.company/). Browse and search every icon at
**[iconmonks.co](https://www.iconmonks.co/)**.

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
| `size` | `number \| string` | `1em` |
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

## Links

- [Website and icon search](https://www.iconmonks.co/)
- [All platforms and source code](https://github.com/designmonks-llc/icon-monks)
- [Request an icon or report a bug](https://github.com/designmonks-llc/icon-monks/issues)

MIT licensed. A product of [Design Monks](https://monks.company/).
