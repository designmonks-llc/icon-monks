# @icon-monks/web

A dependency-free `<icon-monks>` custom element for plain HTML, Angular, Svelte, Astro, WordPress or anything else.

```html
<script src="https://cdn.jsdelivr.net/npm/@icon-monks/web@0.3.0"></script>

<icon-monks name="house"></icon-monks>
<icon-monks name="heart" weight="fill" size="32" color="crimson" label="Favorite"></icon-monks>
```

Or `npm install @icon-monks/web` and `import '@icon-monks/web';` once in your app.

Attributes: `name`, `weight`, `size`, `color`, `mirrored`, `label` (sets an accessible name; icons are hidden from screen readers otherwise).

## How icons load

The script is a few KB. Each icon is fetched the first time a page uses it, about 1 KB per icon and weight, and
cached for the rest of the visit. Files come from `dist/icons/<weight>/<name>.json` next to the script, with the
jsDelivr copy of this version as the fallback.

- **Self-hosting or a strict CSP:** serve a copy of `dist/icons/` and point the element at it with
  `<script src="…/icon-monks.js" data-base="/assets/icon-monks/"></script>`, or `setIconBase('/assets/icon-monks/')`
  when you import the package.
- **Offline, or every icon up front:** use the full bundle instead, which holds every icon in every weight (about
  23 MB): `import '@icon-monks/web/all'`, or the `icon-monks.all.js` script. It also exports the raw `paths`.
