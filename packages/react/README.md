# @icon-monks/react

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
