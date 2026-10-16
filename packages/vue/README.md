# @icon-monks/vue

```sh
npm install @icon-monks/vue
```

```vue
<script setup>
import { House, Heart, IconContextKey } from '@icon-monks/vue';
import { provide } from 'vue';
provide(IconContextKey, { size: 24, weight: 'bold' }); // optional defaults for descendants
</script>

<template>
  <House />
  <Heart :size="32" color="crimson" weight="fill" />
</template>
```
