(function () {

const CDN = 'https://cdn.jsdelivr.net/npm/@icon-monks/web@0.3.0/dist/icons/';
let BASES = [];
const cache = new Map();

function setIconBase(url) { BASES = [String(url).replace(/\/?$/, '/')]; cache.clear(); }

async function fetchIcon(key) {
  for (const base of BASES.slice()) {
    try {
      const res = await fetch(base + key + '.json');
      if (res.ok) return await res.json();
    } catch (e) {
      BASES = BASES.filter((b) => b !== base);
    }
  }
  return undefined;
}

function lookup(name, weight) {
  if (!/^[a-z0-9-]+$/.test(name)) return undefined;
  const key = weight + '/' + name;
  if (!cache.has(key)) cache.set(key, fetchIcon(key).then((d) => { if (d) cache.set(key, d); else cache.delete(key); return d; }));
  return cache.get(key);
}

const script = typeof document !== 'undefined' ? document.currentScript : null;
if (script && script.dataset.base) BASES = [script.dataset.base.replace(/\/?$/, '/')];
else if (script && script.src) {
  const src = script.src.split(/[?#]/)[0];
  BASES = [/\.js$/.test(src) ? new URL('icons/', src).href : src.replace(/\/?$/, '/') + 'dist/icons/', CDN];
} else BASES = [CDN];

const ATTRS = ['name', 'weight', 'size', 'color', 'mirrored', 'label'];
const WEIGHTS = ["thin", "light", "regular", "bold", "fill", "duotone"];

function draw(el, d, weight) {
  const size = el.getAttribute('size') || '1em';
  const color = el.getAttribute('color') || 'currentColor';
  const body = !d ? '' : weight === 'duotone'
    ? (d[0] ? '<path d="' + d[0] + '" opacity="0.2"/>' : '') + '<path d="' + d[1] + '"/>'
    : '<path d="' + d + '"/>';
  const flip = el.hasAttribute('mirrored') ? ' transform="scale(-1, 1)"' : '';
  el.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="' + size + '" height="' + size +
    '" viewBox="0 0 256 256" fill="' + color + '"' + flip + ' style="display:block">' + body + '</svg>';
}

function render(el) {
  const name = el.getAttribute('name') || '';
  const asked = el.getAttribute('weight') || 'regular';
  const weight = WEIGHTS.indexOf(asked) < 0 ? 'regular' : asked;
  const label = el.getAttribute('label');
  if (label) { el.setAttribute('role', 'img'); el.setAttribute('aria-label', label); }
  else { el.removeAttribute('role'); el.removeAttribute('aria-label'); el.setAttribute('aria-hidden', 'true'); }
  const d = lookup(name, weight);
  if (d && typeof d.then === 'function') {
    draw(el, null, weight);  // holds the icon's space while its path data loads
    const ticket = el._iconMonks = {};
    d.then((v) => { if (el._iconMonks !== ticket) return; if (v) draw(el, v, weight); else el.innerHTML = ''; });
  } else {
    el._iconMonks = null;
    if (d) draw(el, d, weight); else el.innerHTML = '';
  }
}

// Importable during server rendering, where there is no HTMLElement; the element only registers in a browser.
class IconMonkElement extends (typeof HTMLElement === 'undefined' ? class {} : HTMLElement) {
  static get observedAttributes() { return ATTRS; }
  connectedCallback() { this.style.display ||= 'inline-block'; this.style.lineHeight ||= '0'; render(this); }
  attributeChangedCallback() { if (this.isConnected) render(this); }
}

if (typeof customElements !== 'undefined' && !customElements.get('icon-monks')) {
  customElements.define('icon-monks', IconMonkElement);
}
})();
