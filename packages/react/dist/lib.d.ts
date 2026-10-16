import type { ForwardRefExoticComponent, RefAttributes, SVGProps, Context } from 'react';

export type IconWeight = 'thin' | 'light' | 'regular' | 'bold' | 'fill' | 'duotone';
export interface IconProps extends Omit<SVGProps<SVGSVGElement>, 'ref'> {
  /** Width and height. Default `1em`. */
  size?: number | string;
  /** Icon color. Default `currentColor`. */
  color?: string;
  /** Visual weight. Default `regular`. */
  weight?: IconWeight;
  /** Flip horizontally, e.g. for right-to-left layouts. */
  mirrored?: boolean;
}
export type Icon = ForwardRefExoticComponent<IconProps & RefAttributes<SVGSVGElement>>;
export interface IconContextValue { color?: string; size?: number | string; weight?: IconWeight; mirrored?: boolean; attrs?: SVGProps<SVGSVGElement>; }
export declare const IconContext: Context<IconContextValue>;
export declare function createIcon(displayName: string, paths: Record<string, string | [string, string]>): Icon;
