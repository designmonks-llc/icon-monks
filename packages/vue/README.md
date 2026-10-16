# @monks-icons/vue

```sh
npm install @monks-icons/vue
```

```vue
<script setup>
import { House, Heart, IconContextKey } from '@monks-icons/vue';
import { provide } from 'vue';
provide(IconContextKey, { size: 24, weight: 'bold' }); // optional defaults for descendants
</script>

<template>
  <House />
  <Heart :size="32" color="crimson" weight="fill" />
</template>
```
