# @icon-monks/vue

[![npm](https://img.shields.io/npm/v/@icon-monks/vue)](https://www.npmjs.com/package/@icon-monks/vue)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/designmonks-llc/icon-monks/blob/main/LICENSE.md)

![Icon Monks](https://www.iconmonks.co/og-image.png)

6,054 Vue 3 icon components in six weights: thin, light, regular, bold, fill and duotone. Typed and tree-shakeable. A product of [Design Monks](https://www.designmonks.co). Browse and search every icon at
**[iconmonks.co](https://www.iconmonks.co/)**.

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
| `size` | `number \| string` | `1em` |
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

## Links

- [Website and icon search](https://www.iconmonks.co/)
- [All platforms and source code](https://github.com/designmonks-llc/icon-monks)
- [Request an icon or report a bug](https://github.com/designmonks-llc/icon-monks/issues)

MIT licensed. A product of [Design Monks](https://www.designmonks.co).
