import * as React from 'react';

const { createElement, forwardRef } = React;
const DEFAULTS = { color: 'currentColor', size: '1em', weight: 'regular', mirrored: false };

export const IconContext = React.createContext ? React.createContext(DEFAULTS) : null;

export function createIcon(displayName, paths) {
  const Icon = forwardRef(function IconMonk(props, ref) {
    // Merged, so a provider that sets only size or weight keeps the default color.
    const ctx = { ...DEFAULTS, ...(IconContext ? React.useContext(IconContext) : null) };
    const { color = ctx.color, size = ctx.size, weight = ctx.weight, mirrored = ctx.mirrored, children, ...rest } = props;
    const d = paths[weight] ?? paths.regular;
    const body = weight === 'duotone'
      ? [d[0] ? createElement('path', { key: 'a', d: d[0], opacity: 0.2 }) : null, createElement('path', { key: 'l', d: d[1] })]
      : createElement('path', { d });
    return createElement('svg', {
      ref, xmlns: 'http://www.w3.org/2000/svg', width: size, height: size, viewBox: '0 0 256 256', fill: color,
      transform: mirrored ? 'scale(-1, 1)' : undefined, ...ctx.attrs, ...rest,
    }, children, body);
  });
  Icon.displayName = displayName;
  return Icon;
}
