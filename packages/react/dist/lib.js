import { createContext, createElement, forwardRef, useContext } from 'react';

export const IconContext = createContext({ color: 'currentColor', size: '1em', weight: 'regular', mirrored: false });

export function createIcon(displayName, paths) {
  const Icon = forwardRef(function MonksIcon(props, ref) {
    const ctx = useContext(IconContext);
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
