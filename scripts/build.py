#!/usr/bin/env python3
"""Outline the stroke-based sources in icons/ into flat, single-path SVGs for every weight.

Writes:
  svg/<weight>/<name>.svg   ready-to-use assets
  build/icons.json          path data + metadata consumed by scripts/packages.py

Requires: pip install skia-pathops fonttools
"""
import json
import os
import re
import xml.etree.ElementTree as ET

import pathops
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.svgLib.path import parse_path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'icons')
SVG_OUT = os.path.join(ROOT, 'svg')
BUILD = os.path.join(ROOT, 'build')

STROKES = {'thin': 8, 'light': 12, 'regular': 16, 'bold': 24}
WEIGHTS = ['thin', 'light', 'regular', 'bold', 'fill', 'duotone']
DUOTONE_OPACITY = 0.2
NS = '{http://www.w3.org/2000/svg}'


def num(el, key, default=0.0):
    return float(el.get(key, default))


def element_d(el):
    tag = el.tag.replace(NS, '')
    if tag == 'path':
        return el.get('d')
    if tag in ('circle', 'ellipse'):
        cx, cy = num(el, 'cx'), num(el, 'cy')
        rx = num(el, 'r') if tag == 'circle' else num(el, 'rx')
        ry = num(el, 'r') if tag == 'circle' else num(el, 'ry')
        return (f'M{cx - rx} {cy} A{rx} {ry} 0 1 1 {cx + rx} {cy} '
                f'A{rx} {ry} 0 1 1 {cx - rx} {cy} Z')
    if tag == 'rect':
        x, y, w, h = num(el, 'x'), num(el, 'y'), num(el, 'width'), num(el, 'height')
        r = min(num(el, 'rx', el.get('ry', 0)), w / 2, h / 2)
        if not r:
            return f'M{x} {y} H{x + w} V{y + h} H{x} Z'
        return (f'M{x + r} {y} H{x + w - r} A{r} {r} 0 0 1 {x + w} {y + r} V{y + h - r} '
                f'A{r} {r} 0 0 1 {x + w - r} {y + h} H{x + r} A{r} {r} 0 0 1 {x} {y + h - r} '
                f'V{y + r} A{r} {r} 0 0 1 {x + r} {y} Z')
    if tag == 'line':
        return f'M{el.get("x1")} {el.get("y1")} L{el.get("x2")} {el.get("y2")}'
    if tag in ('polyline', 'polygon'):
        pts = re.split(r'[\s,]+', el.get('points').strip())
        pairs = [f'{pts[i]} {pts[i + 1]}' for i in range(0, len(pts), 2)]
        return 'M' + ' L'.join(pairs) + (' Z' if tag == 'polygon' else '')
    raise ValueError(f'unsupported element <{tag}>')


def to_path(ds):
    p = pathops.Path()
    pen = p.getPen()
    for d in ds:
        parse_path(d, pen)
    return p


def clean(p):
    p.convertConicsToQuads(0.05)
    return p


def stroke(ds, width):
    pieces = []
    for d in ds:
        p = to_path([d])
        p.stroke(width, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        pieces.append(clean(p))
    # Each stroked element is resolved and oriented on its own before merging (see union()).
    return union(*pieces)


def union(*paths):
    paths = [p for p in paths if p is not None and len(list(p.segments))]
    if not paths:
        return pathops.Path()
    acc = pathops.Path()
    oriented = [_oriented(p) for p in paths]
    for p in oriented:
        # Orient each input first: raw shapes and pathops output can wind opposite ways, and under
        # nonzero filling an overlap of opposite windings would cancel out instead of merging.
        acc.addPath(p)
    try:
        acc.simplify(fix_winding=False, keep_starting_points=False)
    except pathops.PathOpsError:
        return _union_pairwise(paths)
    out = fix_winding(acc)
    # simplify can also "succeed" on near-coincident edges and drop most of the shape; a union is
    # never smaller than its largest input, so treat that as a failure too.
    if _area(out) < 0.98 * max(_area(p) for p in oriented):
        return _union_pairwise(paths)
    return out


def _area(p):
    try:
        return abs(fix_winding(p).area)
    except Exception:
        return 0.0


def _union_pairwise(paths):
    # Fallback when one big simplify fails on a degenerate overlap: merge one input at a time, and
    # keep an input that still will not merge as a separate (already oriented) contour set.
    acc = pathops.Path()
    for p in paths:
        q = _oriented(p)
        try:
            nxt = pathops.op(acc, q, pathops.PathOp.UNION, fix_winding=False, keep_starting_points=False)
            if _area(nxt) < 0.98 * max(_area(acc), _area(q)):
                raise pathops.PathOpsError('union lost area')
            acc = nxt
        except pathops.PathOpsError:
            acc.addPath(q)
    return fix_winding(acc)


def _oriented(p):
    q = pathops.Path()
    q.addPath(p)
    try:
        q.simplify(fix_winding=False, keep_starting_points=False)
    except pathops.PathOpsError:
        return p
    return fix_winding(q)


def difference(a, *subs):
    subs = [s for s in subs if s is not None and len(list(s.segments))]
    if not subs:
        return a
    return fix_winding(pathops.op(a, union(*subs), pathops.PathOp.DIFFERENCE, fix_winding=False,
                                  keep_starting_points=False))


def fix_winding(path):
    """Orient contours by nesting depth (outer clockwise, holes counter-clockwise, ...).

    skia-pathops' built-in fix_winding mis-orients holes when contours touch tangentially.
    """
    contours = list(path.contours)
    out = pathops.Path()
    for i, c in enumerate(contours):
        pts = [p for p in c.points if p is not None][:: max(1, len(c.points) // 7)][:7]
        depth = 0
        for j, other in enumerate(contours):
            if i != j and sum(other.contains(p) for p in pts) * 2 > len(pts):
                depth += 1
        if c.clockwise != (depth % 2 == 0):
            c.reverse()
        out.addPath(c)
    return out


def filled(ds):
    if not ds:
        return None
    return union(*[clean(to_path([d])) for d in ds])


def dots(circles, width):
    if not circles:
        return None
    scale = (width + 8) / 32.0  # a source r of 16 renders r=12 at regular
    ds = []
    for cx, cy, r in circles:
        rr = r * scale
        ds.append(f'M{cx - rr} {cy} A{rr} {rr} 0 1 1 {cx + rr} {cy} A{rr} {rr} 0 1 1 {cx - rr} {cy} Z')
    return filled(ds)


def fmt(v):
    s = ('%.2f' % v).rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def to_d(p):
    pen = SVGPathPen(None, fmt)
    p.draw(pen)
    return pen.getCommands()


def load(path):
    root = ET.parse(path).getroot()
    roles = {k: [] for k in ('line', 'detail', 'area', 'hole', 'dot', 'dotcut')}
    for g in root.iter(NS + 'g'):
        role = g.get('data-role')
        for el in g:
            if role in ('dot', 'dotcut'):
                roles[role].append((num(el, 'cx'), num(el, 'cy'), num(el, 'r')))
            else:
                roles[role].append(element_d(el))
    tags = [t for t in root.get('data-tags', '').split(',') if t]
    return roles, root.get('data-category', 'Other'), tags


def outline(roles):
    out = {}
    for weight, w in STROKES.items():
        out[weight] = to_d(union(stroke(roles['line'] + roles['detail'], w),
                                 dots(roles['dot'], w), dots(roles['dotcut'], w)))
    if roles['area'] or roles['detail'] or roles['hole'] or roles['dotcut']:
        base = union(filled(roles['area']), stroke(roles['line'], 16), dots(roles['dot'], 16))
        cuts = [stroke(roles['detail'], 16) if roles['detail'] else None, filled(roles['hole']),
                dots(roles['dotcut'], 16)]
        out['fill'] = to_d(difference(base, *cuts))
    else:
        out['fill'] = out['regular']
    out['duotone'] = [to_d(filled(roles['area'])) if roles['area'] else '', out['regular']]
    return out


def svg_markup(d, weight):
    if weight == 'duotone':
        area, line = d
        inner = (f'<path d="{area}" opacity="{DUOTONE_OPACITY}"/>' if area else '') + f'<path d="{line}"/>'
    else:
        inner = f'<path d="{d}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor">'
            f'{inner}</svg>\n')


def main():
    names = sorted(f[:-4] for f in os.listdir(SRC) if f.endswith('.svg'))
    icons = []
    for name in names:
        roles, category, tags = load(os.path.join(SRC, name + '.svg'))
        icons.append({'name': name, 'category': category, 'tags': tags, 'paths': outline(roles)})
    for weight in WEIGHTS:
        os.makedirs(os.path.join(SVG_OUT, weight), exist_ok=True)
        for ic in icons:
            suffix = '' if weight == 'regular' else f'-{weight}'
            with open(os.path.join(SVG_OUT, weight, f'{ic["name"]}{suffix}.svg'), 'w') as fh:
                fh.write(svg_markup(ic['paths'][weight], weight))
    os.makedirs(BUILD, exist_ok=True)
    with open(os.path.join(BUILD, 'icons.json'), 'w') as fh:
        json.dump({'weights': WEIGHTS, 'icons': icons}, fh, separators=(',', ':'))
    print(f'built {len(icons)} icons x {len(WEIGHTS)} weights')


if __name__ == '__main__':
    main()
