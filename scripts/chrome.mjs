// The site header shared by every page (icon browser, static pages, showcase), drawn with Icon Monks icons.
// Its width follows --head-max so the logo lines up with each page's content column.
// Each page inlines HEADER_CSS (the showcase keeps its own tokens, so colours fall back to them) and HEADER_JS.

const pick = (byName, name, weight) => {
  const d = byName[name].paths[weight];
  return Array.isArray(d) ? d[1] : d;
};
// One inline icon from the set; `weight` defaults to regular.
export const icon = (byName, name, size = 18, weight = 'regular') =>
  `<svg class="ui-i" viewBox="0 0 256 256" width="${size}" height="${size}" fill="currentColor" aria-hidden="true"><path d="${pick(byName, name, weight)}"/></svg>`;

// `up` is the relative path to the site root ('' on the homepage); `theme` adds the light/dark button.
export function header({ byName, up = '', REPO, theme = true, current = '' }) {
  const link = (href, label, key) => `<a href="${up}${href}"${current === key ? ' aria-current="page"' : ''}>${label}</a>`;
  return `<header class="site-head"><div class="site-head-in">
  <a class="site-brand" href="${up || './'}"><img src="${up}favicon.svg" alt="" width="28" height="28">Icon Monks</a>
  <nav class="site-links" aria-label="Main">${link('', 'Icons', 'icons')}${link('categories/', 'Categories', 'categories')}${link('getting-started/', 'Get started', 'start')}${link('showcase/', 'Showcase', 'showcase')}</nav>
  <div class="site-acts">
    <a class="site-gh" href="${REPO}" target="_blank" rel="noopener">${icon(byName, 'github-logo', 17, 'fill')}<span>GitHub</span></a>
    ${theme ? `<button class="site-theme" id="site-theme" type="button" aria-label="Theme: system">${icon(byName, 'monitor', 17)}${icon(byName, 'sun', 17)}${icon(byName, 'moon', 17)}</button>` : ''}
  </div>
</div></header>`;
}

export const HEADER_CSS = `
.site-head { --h-bg: var(--paper, var(--canvas)); --h-ink: var(--ink); --h-muted: var(--muted); --h-rule: var(--rule, var(--line)); --h-sheet: var(--sheet, var(--surface));
  background: var(--h-bg); border-bottom: 1px solid var(--h-rule); }
.site-head-in { max-width: var(--head-max, 1240px); margin: 0 auto; display: flex; align-items: center; gap: 28px; padding-block: 12px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
.site-brand { display: flex; align-items: center; gap: 10px; font: 500 18px var(--display); color: var(--h-ink); text-decoration: none; white-space: nowrap; }
.site-brand img { display: block; border-radius: 7px; }
.site-links { display: flex; gap: 22px; font-size: 14px; }
.site-links a { color: var(--h-muted); text-decoration: none; white-space: nowrap; }
.site-links a:hover, .site-links a[aria-current="page"] { color: var(--h-ink); }
.site-acts { margin-left: auto; display: flex; align-items: center; gap: 8px; }
.site-gh, .site-theme { display: inline-flex; align-items: center; gap: 7px; height: 36px; border: 1px solid var(--h-rule); background: var(--h-sheet);
  color: var(--h-ink); border-radius: 10px; font: 500 13.5px var(--body); text-decoration: none; cursor: pointer; }
.site-gh { padding: 0 12px; }
.site-theme { width: 36px; justify-content: center; padding: 0; color: var(--h-muted); }
.site-theme:hover, .site-gh:hover { border-color: var(--h-muted); }
.site-theme .ui-i { display: none; }
.site-theme[data-mode="system"] .ui-i:nth-child(1), .site-theme[data-mode="light"] .ui-i:nth-child(2), .site-theme[data-mode="dark"] .ui-i:nth-child(3) { display: block; }
.site-head a:focus-visible, .site-head button:focus-visible { outline: 2px solid var(--saffron, var(--accent)); outline-offset: 2px; }
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
