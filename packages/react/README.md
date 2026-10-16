# @monks-icons/react

```sh
npm install @monks-icons/react
```

```jsx
import { House, Heart, IconContext } from '@monks-icons/react';

<House />                                   // 1em, currentColor, regular
<Heart size={32} color="crimson" weight="fill" />

<IconContext.Provider value={{ size: 24, weight: 'duotone' }}>
  <House /> <Heart />
</IconContext.Provider>
```

Props: `size`, `color`, `weight` (`thin` `light` `regular` `bold` `fill` `duotone`), `mirrored`, plus any SVG attribute.
Every icon is also exported with an `Icon` suffix (`HouseIcon`) and as a deep import (`@monks-icons/react/icons/House`).
