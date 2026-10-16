import { defineComponent, h, inject } from 'vue';

export const IconContextKey = Symbol('monks-icons');

export function createIcon(name, paths) {
  return defineComponent({
    name,
    props: {
      size: { type: [String, Number], default: undefined },
      color: { type: String, default: undefined },
      weight: { type: String, default: undefined },
      mirrored: { type: Boolean, default: undefined },
    },
    setup(props, { slots }) {
      const ctx = inject(IconContextKey, {});
      return () => {
        const weight = props.weight ?? ctx.weight ?? 'regular';
        const size = props.size ?? ctx.size ?? '1em';
        const mirrored = props.mirrored ?? ctx.mirrored ?? false;
        const d = paths[weight] ?? paths.regular;
        const body = weight === 'duotone'
          ? [d[0] ? h('path', { d: d[0], opacity: 0.2 }) : null, h('path', { d: d[1] })]
          : [h('path', { d })];
        return h('svg', {
          xmlns: 'http://www.w3.org/2000/svg', width: size, height: size, viewBox: '0 0 256 256',
          fill: props.color ?? ctx.color ?? 'currentColor', transform: mirrored ? 'scale(-1, 1)' : undefined,
        }, [slots.default?.(), ...body]);
      };
    },
  });
}
