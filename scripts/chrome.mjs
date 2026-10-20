// The site header shared by every page (icon browser, static pages, showcase), drawn with Icon Monks icons.
// It carries its own width, colours and type, so it looks and sits the same on every page whatever that page's tokens are.
// Each page inlines HEADER_CSS, HEADER_JS and HEADER_THEME (in <head>, so a saved theme applies before first paint).

const pick = (byName, name, weight) => {
  const d = byName[name].paths[weight];
  return Array.isArray(d) ? d[1] : d;
};
// One inline icon from the set; `weight` defaults to regular.
export const icon = (byName, name, size = 18, weight = 'regular') =>
  `<svg class="ui-i" viewBox="0 0 256 256" width="${size}" height="${size}" fill="currentColor" aria-hidden="true"><path d="${pick(byName, name, weight)}"/></svg>`;

// Icon Monks is a product of Design Monks; every page credits the studio in its footer.
export const STUDIO = { name: 'Design Monks', url: 'https://monks.company/' };
export const STUDIO_LINK = `<a href="${STUDIO.url}" target="_blank" rel="noopener">${STUDIO.name}</a>`;
// The bottom line of every footer.
export const CREDIT = `<p class="foot-base">Icon Monks is a product of ${STUDIO_LINK}. Free and open source under the MIT license.</p>`;

// `up` is the relative path to the site root ('' on the homepage); `theme` adds the light/dark button.
export function header({ byName, up = '', REPO, current = '' }) {
  const link = (href, label, key) => `<a href="${up}${href}"${current === key ? ' aria-current="page"' : ''}>${label}</a>`;
  return `<header class="site-head"><div class="site-head-in">
  <a class="site-brand" href="${up || './'}" aria-label="Icon Monks home"><span class="site-logo" style="-webkit-mask-image: url(${up}logo.svg); mask-image: url(${up}logo.svg)"></span></a>
  <nav class="site-links" aria-label="Main">${link('', 'Icons', 'icons')}${link('categories/', 'Categories', 'categories')}${link('getting-started/', 'Get started', 'start')}${link('showcase/', 'Showcase', 'showcase')}</nav>
  <div class="site-acts">
    <a class="site-gh" href="${REPO}" target="_blank" rel="noopener">${icon(byName, 'github-logo', 17, 'fill')}<span>GitHub</span></a>
    <button class="site-theme" id="site-theme" type="button" aria-label="Theme: system">${icon(byName, 'monitor', 17)}${icon(byName, 'sun', 17)}${icon(byName, 'moon', 17)}</button>
  </div>
</div></header>`;
}

// Applies the remembered Light or Dark choice; goes in <head> before any stylesheet.
export const HEADER_THEME = `<script>try { const t = localStorage.getItem('im-theme'); if (t === 'light' || t === 'dark') document.documentElement.dataset.theme = t; } catch (e) {}</script>`;

export const HEADER_CSS = `
.site-head { --h-bg: #f4f5f8; --h-ink: #1b1e3a; --h-muted: #5d6280; --h-rule: #dfe2ec; --h-sheet: #ffffff; --h-focus: #c96a00;
  background: var(--h-bg); border-bottom: 1px solid var(--h-rule); color: var(--h-ink); font: 400 14px/1.5 'DM Sans', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif; }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) .site-head { --h-bg: #11132a; --h-ink: #e8e9f4; --h-muted: #a0a4c4; --h-rule: #2c3058; --h-sheet: #191c38; --h-focus: #f5a53a; color-scheme: dark; }
}
:root[data-theme="dark"] .site-head { --h-bg: #11132a; --h-ink: #e8e9f4; --h-muted: #a0a4c4; --h-rule: #2c3058; --h-sheet: #191c38; --h-focus: #f5a53a; color-scheme: dark; }
.site-head-in { max-width: 1240px; margin: 0 auto; display: flex; align-items: center; gap: 28px; padding-block: 12px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
.site-brand { display: flex; align-items: center; color: var(--h-ink); text-decoration: none; }
/* The wordmark is a mask filled with the header ink, so it follows light and dark themes without a second file. */
.site-logo { display: block; width: 136px; height: 23px; background: currentColor; -webkit-mask: center / contain no-repeat; mask: center / contain no-repeat; }
.site-links { display: flex; gap: 22px; font-size: 14px; }
.site-links a { color: var(--h-muted); text-decoration: none; white-space: nowrap; }
.site-links a:hover, .site-links a[aria-current="page"] { color: var(--h-ink); }
.site-acts { margin-left: auto; display: flex; align-items: center; gap: 8px; }
.site-gh, .site-theme { display: inline-flex; align-items: center; gap: 7px; height: 36px; border: 1px solid var(--h-rule); background: var(--h-sheet);
  color: var(--h-ink); border-radius: 10px; font: inherit; font-size: 13.5px; font-weight: 500; text-decoration: none; cursor: pointer; }
.site-gh { padding: 0 12px; }
.site-theme { width: 36px; justify-content: center; padding: 0; color: var(--h-muted); }
.site-theme:hover, .site-gh:hover { border-color: var(--h-muted); }
.site-theme .ui-i { display: none; }
.site-theme[data-mode="system"] .ui-i:nth-child(1), .site-theme[data-mode="light"] .ui-i:nth-child(2), .site-theme[data-mode="dark"] .ui-i:nth-child(3) { display: block; }
.site-head a:focus-visible, .site-head button:focus-visible { outline: 2px solid var(--h-focus); outline-offset: 2px; }
.ui-i { display: block; flex: none; }
@media (max-width: 720px) {
  .site-head-in { flex-wrap: wrap; gap: 10px 16px; }
  .site-links { order: 3; width: 100%; gap: 18px; overflow-x: auto; scrollbar-width: none; }
  .site-gh span { display: none; }
  .site-gh { width: 36px; justify-content: center; padding: 0; }
}`;

// Theme button: System follows the OS; Light and Dark override it and are remembered. Clicks cycle the three.
export const HEADER_JS = `<script>(() => {
  const b = document.getElementById('site-theme'); if (!b) return;
  const order = ['', 'light', 'dark'], name = { '': 'system', light: 'light', dark: 'dark' };
  const show = () => { const t = document.documentElement.dataset.theme || ''; b.dataset.mode = name[t]; b.setAttribute('aria-label', 'Theme: ' + name[t] + '. Change theme'); b.title = 'Theme: ' + name[t]; };
  b.addEventListener('click', () => {
    const t = order[(order.indexOf(document.documentElement.dataset.theme || '') + 1) % 3];
    if (t) document.documentElement.dataset.theme = t; else delete document.documentElement.dataset.theme;
    try { localStorage.setItem('im-theme', t); } catch (e) {}
    show();
  });
  show();
})();</script>`;
