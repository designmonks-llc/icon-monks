#!/usr/bin/env python3
"""Outline the stroke-based sources in icons/ into flat, single-path SVGs for every weight.

Writes:
  svg/<weight>/<name>.svg   ready-to-use assets
  build/icons.json          path data + metadata consumed by scripts/packages.py

Requires: pip install skia-pathops fonttools
"""
import json
import math
import os
import re
import xml.etree.ElementTree as ET

import pathops
from fontTools.pens.basePen import decomposeQuadraticSegment, decomposeSuperBezierSegment
from fontTools.pens.recordingPen import RecordingPen
from fontTools.svgLib.path import parse_path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'icons')
SVG_OUT = os.path.join(ROOT, 'svg')
BUILD = os.path.join(ROOT, 'build')

STROKES = {'thin': 8, 'light': 12, 'regular': 16, 'bold': 24}
WEIGHTS = ['thin', 'light', 'regular', 'bold', 'fill', 'duotone']
DUOTONE_OPACITY = 0.2
SLASH_GAP = 16  # clear space between a slash and the icon it crosses, in every weight
BADGE_GAP = 16  # clear space between a corner badge (a plus, a check, a heart) and the icon it sits on
BADGE_DOT = 12  # circles in a badge up to this radius are solid dots (the point of a ! or ?)
BADGE_CENTRE = (188, 188)  # every badge mark is drawn around this point (lint.BADGES)
BADGE_ZONE = (120, 120, 256, 256)  # the badge's corner: base pieces the cut leaves wholly in here are dropped
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
    # simplify can also "succeed" on near-coincident edges and drop part of the shape; a union contains
    # every input, so an input that is not inside the result is a failure too.
    if not _covers(out, oriented):
        return _union_pairwise(paths)
    return out


def _covers(out, parts):
    for p in parts:
        a = _area(p)
        if a < 1:
            continue
        try:
            lost = pathops.op(p, out, pathops.PathOp.DIFFERENCE, fix_winding=False, keep_starting_points=False)
        except pathops.PathOpsError:
            return False
        if _area(lost) > 0.02 * a:
            return False
    return True


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
            if not _covers(nxt, [acc, q]):
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


ARC_TOL = 0.2  # how far (in grid units) a run of quadratic pieces may stray from the circle that replaces it; the
# stroker approximates offset arcs to about 0.15, so the true circle is the closer match to what the source draws


def _qpt(p0, c, p1, t):
    u = 1 - t
    return (u * u * p0[0] + 2 * u * t * c[0] + t * t * p1[0], u * u * p0[1] + 2 * u * t * c[1] + t * t * p1[1])


def _centre(p0, c0, p1, c1):
    """Where the normals at p0 (tangent towards c0) and p1 (tangent from c1) meet: the centre of an arc through both."""
    t0, t1 = (c0[0] - p0[0], c0[1] - p0[1]), (p1[0] - c1[0], p1[1] - c1[1])
    det = t0[0] * t1[1] - t0[1] * t1[0]
    if abs(det) < 1e-9:
        return None
    # p0 + s*n0 = p1 + u*n1 with n = (-ty, tx)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    k = (dx * t1[0] + dy * t1[1]) / det
    return p0[0] - t0[1] * k, p0[1] + t0[0] * k


def _arc(run):
    """An SVG arc for a run of quadratics [(start, control, end)] that all lie on one circle, or None."""
    start, end = run[0][0], run[-1][2]
    centre = _centre(start, run[0][1], end, run[-1][1])
    if not centre:
        return None
    ux, uy = centre
    r = math.hypot(start[0] - ux, start[1] - uy)
    if r > 256 or r < 0.5:
        return None
    sweep = 0.0
    for q in run:
        for t in (0.25, 0.5, 0.75, 1):
            x, y = _qpt(*q, t)
            if abs(math.hypot(x - ux, y - uy) - r) > ARC_TOL:
                return None
        a0 = math.atan2(q[0][1] - uy, q[0][0] - ux)
        a1 = math.atan2(q[2][1] - uy, q[2][0] - ux)
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        if sweep and da * sweep < 0:  # turns back on itself: not one arc
            return None
        sweep += da
    if abs(sweep) > 1.9 * math.pi:
        return None
    large, positive = abs(sweep) > math.pi, sweep > 0
    # Check the arc a renderer will draw: it rebuilds the centre from the rounded radius and end points, which for
    # arcs near a half circle moves the centre a lot for a small change in radius.
    rr, sx, sy, ex, ey = (float(fmt(v)) for v in (r, start[0], start[1], end[0], end[1]))
    mx, my, hx, hy = (sx + ex) / 2, (sy + ey) / 2, (ex - sx) / 2, (ey - sy) / 2
    h = math.hypot(hx, hy)
    if h < 1e-6 or h > rr:
        return None
    k = math.sqrt(rr * rr - h * h) / h
    ux, uy = (mx - hy * k, my + hx * k) if large != positive else (mx + hy * k, my - hx * k)
    for q in run:
        for t in (0.25, 0.5, 0.75):
            x, y = _qpt(*q, t)
            if abs(math.hypot(x - ux, y - uy) - rr) > ARC_TOL:
                return None
    return f'A{fmt(r)} {fmt(r)} 0 {int(large)} {int(positive)} {fmt(end[0])} {fmt(end[1])}'


def _arcs(run):
    """Commands for a run of quadratics: the longest circular stretches become single arcs."""
    out, k = [], 0
    while k < len(run):
        for e in range(len(run), k, -1):
            arc = _arc(run[k:e])
            if arc:
                out.append(arc)
                k = e
                break
        else:
            _, c, p = run[k]
            out.append(f'Q{fmt(c[0])} {fmt(c[1])} {fmt(p[0])} {fmt(p[1])}')
            k += 1
    return out


def to_d(p):
    """Path data for p. The stroker draws round caps and joins as chains of short quadratics; chains that lie on a
    circle are written as one arc, which is how a designer would draw them and roughly halves the file size."""
    rec = RecordingPen()
    p.draw(rec)
    out, run, cur = [], [], (0, 0)
    for op, pts in rec.value + [('endPath', ())]:
        if op == 'qCurveTo':
            if pts[-1] is None:  # closed contour of off-curve points only (a circle): starts between the last and first
                pts = pts[:-1]
                cur = ((pts[-1][0] + pts[0][0]) / 2, (pts[-1][1] + pts[0][1]) / 2)
                out.append(f'M{fmt(cur[0])} {fmt(cur[1])}')
                pts = pts + (cur,)
            for c, e in decomposeQuadraticSegment(pts):
                run.append((cur, c, e))
                cur = e
            continue
        if run:
            out += _arcs(run)
            run = []
        if op == 'moveTo':
            out.append(f'M{fmt(pts[0][0])} {fmt(pts[0][1])}')
        elif op == 'lineTo':
            x, y = pts[0]
            out.append(f'V{fmt(y)}' if fmt(x) == fmt(cur[0]) else f'H{fmt(x)}' if fmt(y) == fmt(cur[1]) else
                       f'L{fmt(x)} {fmt(y)}')
        elif op == 'curveTo':
            for seg in decomposeSuperBezierSegment(pts):
                out.append('C' + ' '.join(f'{fmt(x)} {fmt(y)}' for x, y in seg))
        elif op == 'closePath':
            out.append('Z')
        if pts:
            cur = pts[-1]
    return ''.join(out)


def load(path):
    root = ET.parse(path).getroot()
    roles = {k: [] for k in ('line', 'detail', 'area', 'hole', 'dot', 'dotcut', 'slash', 'badge', 'badgedot',
                             'badgefill')}
    for g in root.iter(NS + 'g'):
        role = g.get('data-role')
        for el in g:
            if role in ('dot', 'dotcut') or (role == 'badge' and el.tag == NS + 'circle' and num(el, 'r') <= BADGE_DOT):
                roles['badgedot' if role == 'badge' else role].append((num(el, 'cx'), num(el, 'cy'), num(el, 'r')))
            elif role == 'badge' and el.tag == NS + 'path' and el.get('d').rstrip().endswith(('Z', 'z')):
                roles['badge'].append(element_d(el))
                roles['badgefill'].append(element_d(el))  # closed outlines (a heart, a star) are solid in fill
            else:
                roles[role].append(element_d(el))
    tags = [t for t in root.get('data-tags', '').split(',') if t]
    return roles, root.get('data-category', 'Other'), tags


def _seg_point(seg, t):
    pts = seg
    while len(pts) > 1:
        pts = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for a, b in zip(pts, pts[1:])]
    return pts[0]


def _seg_split(seg, t0, t1):
    """The part of a line/quadratic/cubic (as its control points) between parameters t0 and t1."""
    def left(pts, t):  # de Casteljau: control points of [0, t]
        out, cur = [pts[0]], pts
        while len(cur) > 1:
            cur = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for a, b in zip(cur, cur[1:])]
            out.append(cur[0])
        return out
    head = left(seg, t1)
    if t1 <= 0:
        return [seg[0]] * len(seg)
    return left(head[::-1], 1 - t0 / t1)[::-1]


def _segments(d):
    """Subpaths of d as (list of control-point tuples, closed)."""
    pen = RecordingPen()
    parse_path(d, pen)
    subs, cur, start = [], None, None
    for op, args in pen.value:
        if op == 'moveTo':
            start = args[0]
            cur = [[], False, start]
            subs.append(cur)
        elif op in ('lineTo', 'curveTo', 'qCurveTo'):
            prev = cur[0][-1][-1] if cur[0] else start
            cur[0].append((prev,) + tuple(args))
        elif op == 'closePath':
            last = cur[0][-1][-1] if cur[0] else start
            if abs(last[0] - start[0]) > 1e-6 or abs(last[1] - start[1]) > 1e-6:
                cur[0].append((last, start))
            cur[1] = True
    return [(segs, closed) for segs, closed, _ in subs]


def _seg_d(seg):
    p = ' '.join(f'{fmt(x)} {fmt(y)}' for x, y in seg[1:])
    return {2: 'L', 3: 'Q', 4: 'C'}[len(seg)] + p


def clip_near(d, a, b, dist):
    """Pieces of path d farther than dist from segment a-b, as open path strings (stroked later with round caps)."""
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    vx, vy = bx - ax, by - ay
    ll = vx * vx + vy * vy

    def far(p):
        t = max(0.0, min(1.0, ((p[0] - ax) * vx + (p[1] - ay) * vy) / ll))
        return ((p[0] - ax - vx * t) ** 2 + (p[1] - ay - vy * t) ** 2) ** 0.5 - dist

    out = []
    for segs, closed in _segments(d):
        pieces = []  # (segment index, t0, t1) kept, in order
        for i, seg in enumerate(segs):
            n = 48
            ts = [0.0]
            prev = far(seg[0])
            for k in range(1, n + 1):
                t = k / n
                cur = far(_seg_point(seg, t))
                if (prev > 0) != (cur > 0):
                    lo, hi = (k - 1) / n, t
                    for _ in range(40):
                        mid = (lo + hi) / 2
                        if (far(_seg_point(seg, mid)) > 0) == (prev > 0):
                            lo = mid
                        else:
                            hi = mid
                    ts.append((lo + hi) / 2)
                prev = cur
            ts.append(1.0)
            for t0, t1 in zip(ts, ts[1:]):
                if t1 - t0 > 1e-6 and far(_seg_point(seg, (t0 + t1) / 2)) > 0:
                    pieces.append((i, t0, t1))
        whole = len(pieces) == len(segs) and all(t0 == 0 and t1 == 1 for _, t0, t1 in pieces)
        if whole:
            out.append('M' + ' '.join(f'{fmt(x)} {fmt(y)}' for x, y in [segs[0][0]]) + ' '
                       + ' '.join(_seg_d(s) for s in segs) + (' Z' if closed else ''))
            continue
        runs = []
        for i, t0, t1 in pieces:
            joined = runs and runs[-1][-1][0] == i - 1 and runs[-1][-1][2] == 1 and t0 == 0
            if joined:
                runs[-1].append((i, t0, t1))
            else:
                runs.append([(i, t0, t1)])
        # A cut closed path may wrap around its start point: join the last run onto the first.
        if closed and len(runs) > 1 and runs[0][0][:2] == (0, 0) and runs[-1][-1][0] == len(segs) - 1 \
                and runs[-1][-1][2] == 1:
            runs[0] = runs.pop() + runs[0]
        for run in runs:
            parts = [_seg_split(segs[i], t0, t1) for i, t0, t1 in run]
            length = sum(((p[-1][0] - p[0][0]) ** 2 + (p[-1][1] - p[0][1]) ** 2) ** 0.5 for p in parts)
            if length < 0.5:
                continue
            out.append(f'M{fmt(parts[0][0][0])} {fmt(parts[0][0][1])} ' + ' '.join(_seg_d(p) for p in parts))
    return out


def _grow(p, by):
    """p grown outward by `by` units: its outline stroked at twice that, merged with p."""
    if p is None:
        return None
    edge = pathops.Path()
    edge.addPath(p)
    edge.stroke(2 * by, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    return union(p, clean(edge))


def _drop_slivers(p, cut, w, zone):
    """p without the pieces the badge cut leaves behind: pieces touching the cut that are too small to read (under
    about two stroke widths long), and pieces lying wholly inside the badge's zone (x0, y0, x1, y1), such as the
    rest of a square the badge replaces. Pieces away from the badge are kept however small."""
    if p is None:
        return p
    keep = pathops.Path()
    shapes = fix_winding(p)
    for c in shapes.contours:
        piece = pathops.Path()
        piece.addPath(c)
        if c.clockwise:
            x0, y0, x1, y1 = piece.bounds
            inside = x0 >= zone[0] and y0 >= zone[1] and x1 <= zone[2] and y1 <= zone[3]
            if inside:
                continue
            if abs(piece.area) < 2.2 * w * w:
                try:
                    touches = abs(pathops.op(piece, cut, pathops.PathOp.INTERSECTION).area) > 0.01
                except pathops.PathOpsError:
                    touches = False
                if touches:
                    continue
        keep.addPath(c)
    return fix_winding(keep)


def _slash_line(roles):
    nums = [float(v) for v in re.findall(r'-?[\d.]+', roles['slash'][0])]
    return (nums[0], nums[1]), (nums[2], nums[3])


def outline(roles):
    """All six weights. A slash (role 'slash', one straight line) is drawn on top of the icon, and everything
    else keeps SLASH_GAP of clear space from it: strokes are trimmed with round ends, filled shapes are cut.
    A badge (role 'badge', a standard mark in the corner) works the same way with BADGE_GAP."""
    out = {}
    slash = roles['slash']
    sa, sb = _slash_line(roles) if slash else (None, None)

    def cut(ds, w):  # stroke centrelines, trimmed so their ink stays clear of the slash at width w
        if not slash:
            return ds
        return [p for d in ds for p in clip_near(d, sa, sb, w + SLASH_GAP)]

    def clear(shape, w):  # filled shapes (areas, dots): cut a band around the slash, then draw the slash
        if roles['badge'] or roles['badgedot']:
            shape = badge(shape, w)
        w = 16 if w == 'fill' else w
        if not slash:
            return shape
        return union(difference(shape, stroke(slash, w + 2 * SLASH_GAP)), stroke(slash, w))

    def badge(shape, w):  # cut BADGE_GAP of clear space around the badge, drop the slivers that leaves, draw it
        solid = w == 'fill'  # the fill weight fills closed marks (a heart, a star) as well as stroking them
        w = 16 if solid else w
        mark = union(stroke(roles['badge'], w), dots(roles['badgedot'], w),
                     filled(roles['badgefill']) if solid and roles['badgefill'] else None)
        # One round clearing for every badge, so every variant gets the same corner: the mark's reach (28) plus
        # half a stroke plus BADGE_GAP. Following the mark's own outline instead bites thin crescents out of
        # nearby edges.
        cx, cy = BADGE_CENTRE
        r = 28 + w / 2 + BADGE_GAP
        room = to_path([f'M{cx - r} {cy} A{r} {r} 0 1 1 {cx + r} {cy} A{r} {r} 0 1 1 {cx - r} {cy} Z'])
        return union(_drop_slivers(difference(shape, room), _grow(room, 1), w, BADGE_ZONE), mark)

    for weight, w in STROKES.items():
        out[weight] = to_d(clear(union(stroke(cut(roles['line'] + roles['detail'], w), w),
                                       dots(roles['dot'], w), dots(roles['dotcut'], w)), w))
    if roles['area'] or roles['detail'] or roles['hole'] or roles['dotcut']:
        base = union(filled(roles['area']), stroke(cut(roles['line'], 16), 16), dots(roles['dot'], 16))
        cuts = [stroke(cut(roles['detail'], 16), 16) if roles['detail'] else None, filled(roles['hole']),
                dots(roles['dotcut'], 16)]
        out['fill'] = to_d(clear(difference(base, *cuts), 'fill'))
    else:
        out['fill'] = out['regular']
    area = filled(roles['area'])
    if area is not None and slash:
        area = difference(area, stroke(slash, 16 + 2 * SLASH_GAP))
    if area is not None and (roles['badge'] or roles['badgedot']):
        cx, cy = BADGE_CENTRE
        r = 28 + 8 + BADGE_GAP
        area = difference(area, to_path([f'M{cx - r} {cy} A{r} {r} 0 1 1 {cx + r} {cy} A{r} {r} 0 1 1 {cx - r} {cy} Z']))
    out['duotone'] = [to_d(area) if area is not None else '', out['regular']]
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
    # Each outline weight carries more ink than the one before it; anything else is a broken boolean.
    broken = []
    for ic in icons:
        # Inked area as drawn (non-zero fill); re-orienting arcs here would misjudge holes by their control points.
        areas = [abs(to_path([ic['paths'][w]]).area) if ic['paths'][w] else 0 for w in STROKES]
        if any(a >= b for a, b in zip(areas, areas[1:])):
            broken.append(ic['name'])
    if broken:
        raise SystemExit(f'weights out of order (thin < light < regular < bold): {", ".join(broken)}')
    os.makedirs(BUILD, exist_ok=True)
    with open(os.path.join(BUILD, 'icons.json'), 'w') as fh:
        json.dump({'weights': WEIGHTS, 'icons': icons}, fh, separators=(',', ':'))
    print(f'built {len(icons)} icons x {len(WEIGHTS)} weights')


if __name__ == '__main__':
    main()
