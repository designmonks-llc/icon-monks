export declare class IconMonkElement extends HTMLElement {}
declare global { interface HTMLElementTagNameMap { 'icon-monks': IconMonkElement; } }
/** Where icon files are fetched from: a folder holding <weight>/<name>.json, such as a copy of dist/icons/. */
export declare function setIconBase(url: string | URL): void;
