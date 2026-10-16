import type { DefineComponent, InjectionKey } from 'vue';
export type IconWeight = 'thin' | 'light' | 'regular' | 'bold' | 'fill' | 'duotone';
export interface IconProps { size?: number | string; color?: string; weight?: IconWeight; mirrored?: boolean; }
export type Icon = DefineComponent<IconProps>;
export declare const IconContextKey: InjectionKey<IconProps>;
export declare function createIcon(name: string, paths: Record<string, string | [string, string]>): Icon;
