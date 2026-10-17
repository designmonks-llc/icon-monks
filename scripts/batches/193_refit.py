"""Refit tessellated sources: paths stored as hundreds of short line segments (sampled formulas, flattened
boolean outlines) become a few arcs and cubics with anchors on the curve extremes and smooth (G1) joins.
Only paths made of straight segments with more than MIN_SEGMENTS of them are touched; everything else is kept.

  python3 scripts/batches/193_refit.py            # rewrite every tessellated icon in icons/
  python3 scripts/batches/193_refit.py --out DIR  # write refitted copies to DIR instead
"""
import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import ROOT, f, pt

MIN_SEGMENTS = 40    # fewer than this is a hand-drawn polyline, not a tessellated curve
TOL = 0.25           # max distance (grid units) between the refit and the original points
CORNER = math.radians(24)   # a turn sharper than this between neighbouring segments is a corner
LONG = 14            # a segment longer than this is a real straight edge, not part of a curve


def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def add(a, b): return (a[0] + b[0], a[1] + b[1])
def mul(a, s): return (a[0] * s, a[1] * s)
def dot(a, b): return a[0] * b[0] + a[1] * b[1]
def norm(a): return math.hypot(a[0], a[1])
def unit(a):
    n = norm(a)
    return (a[0] / n, a[1] / n) if n else (0.0, 0.0)


def parse(d):
    """Subpaths as (points, closed) for paths made only of M/L/H/V/Z, else None."""
    toks = re.findall(r'[A-Za-z]|-?(?:\d+\.?\d*|\.\d+)', d)
    subs, cur, cmd, i = [], None, None, 0
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            if cmd not in 'MLHVZ':
                return None
            if cmd == 'Z':
                cur[1] = True
                continue
        x, y = cur[0][-1] if cur else (0.0, 0.0)
        if cmd in 'ML':
            x, y = float(toks[i]), float(toks[i + 1])
            i += 2
        else:
            v = float(toks[i])
            i += 1
            x, y = (v, y) if cmd == 'H' else (x, v)
        if cmd == 'M':
            cur = [[(x, y)], False]
            subs.append(cur)
            cmd = 'L'
        else:
            cur[0].append((x, y))
    out = []
    for pts, closed in subs:
        if closed and len(pts) > 1 and norm(sub(pts[0], pts[-1])) < 1e-6:
            pts = pts[:-1]
        out.append((pts, closed))
    return out


def turn(a, b, c):
    u, v = unit(sub(b, a)), unit(sub(c, b))
    return math.acos(max(-1.0, min(1.0, dot(u, v))))


def anchors(pts, closed):
    """Indices that must stay as anchors: corners, ends of long straight edges, and x/y extremes of curves."""
    n = len(pts)
    idx = range(n) if closed else range(1, n - 1)
    keep = set() if closed else {0, n - 1}
    for i in idx:
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        if turn(a, b, c) > CORNER or norm(sub(b, a)) > LONG or norm(sub(c, b)) > LONG:
            keep.add(i)
    # Extremes: where the direction of travel flips in x or y, put the anchor on the most extreme point.
    for axis in (0, 1):
        for i in idx:
            a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
            if (b[axis] - a[axis]) * (c[axis] - b[axis]) < 0 or (b[axis] == a[axis] and i - 1 not in keep and
                                                                  (c[axis] - b[axis]) * (b[axis] - pts[i - 2][axis]) < 0):
                keep.add(i)
    if closed and not keep:
        keep.add(0)
    return sorted(keep)


def tangent(pts, i, closed, side):
    """Unit tangent at pts[i], estimated from a few points on one side (-1 before, +1 after) or both (0)."""
    n = len(pts)
    def at(j):
        return pts[j % n] if closed else pts[max(0, min(n - 1, j))]
    if side == 0:
        return unit(sub(at(i + 3), at(i - 3)))
    if side > 0:
        return unit(sub(at(i + 3), at(i)))
    return unit(sub(at(i), at(i - 3)))


def fit_circle(seg):
    """Algebraic (Kasa) circle fit; returns (centre, r, max error)."""
    n = len(seg)
    mx, my = sum(p[0] for p in seg) / n, sum(p[1] for p in seg) / n
    suu = suv = svv = suuu = svvv = suvv = svuu = 0.0
    for x, y in seg:
        u, v = x - mx, y - my
        suu += u * u; suv += u * v; svv += v * v
        suuu += u ** 3; svvv += v ** 3; suvv += u * v * v; svuu += v * u * u
    det = suu * svv - suv * suv
    if abs(det) < 1e-9:
        return None
    uc = (0.5 * (suuu + suvv) * svv - 0.5 * (svvv + svuu) * suv) / det
    vc = (0.5 * (svvv + svuu) * suu - 0.5 * (suuu + suvv) * suv) / det
    c = (uc + mx, vc + my)
    r = sum(norm(sub(p, c)) for p in seg) / n
    return c, r, max(abs(norm(sub(p, c)) - r) for p in seg)


def bez(p0, c1, c2, p1, t):
    s = 1 - t
    return add(add(mul(p0, s ** 3), mul(c1, 3 * s * s * t)), add(mul(c2, 3 * s * t * t), mul(p1, t ** 3)))


def fit_cubic(seg, t0, t1):
    """Least-squares cubic with fixed end tangents t0 (leaving p0) and t1 (arriving at p1); returns (c1, c2, err)."""
    p0, p1 = seg[0], seg[-1]
    d = [0.0]
    for a, b in zip(seg, seg[1:]):
        d.append(d[-1] + norm(sub(b, a)))
    ts = [x / d[-1] for x in d]
    chord = norm(sub(p1, p0))
    for _ in range(4):
        c00 = c01 = c11 = x0 = x1 = 0.0
        for p, t in zip(seg, ts):
            s = 1 - t
            a0, a1 = mul(t0, 3 * s * s * t), mul(t1, -3 * s * t * t)
            rest = sub(p, add(mul(p0, s ** 3 + 3 * s * s * t), mul(p1, 3 * s * t * t + t ** 3)))
            c00 += dot(a0, a0); c01 += dot(a0, a1); c11 += dot(a1, a1)
            x0 += dot(a0, rest); x1 += dot(a1, rest)
        det = c00 * c11 - c01 * c01
        al0 = (x0 * c11 - x1 * c01) / det if abs(det) > 1e-9 else chord / 3
        al1 = (c00 * x1 - c01 * x0) / det if abs(det) > 1e-9 else chord / 3
        if al0 < chord * 0.05 or al1 < chord * 0.05:
            al0 = al1 = chord / 3
        c1, c2 = add(p0, mul(t0, al0)), sub(p1, mul(t1, al1))
        # Newton step on the parameters so the error is measured to the nearest curve point.
        nts = []
        for p, t in zip(seg, ts):
            s = 1 - t
            q = bez(p0, c1, c2, p1, t)
            d1 = add(add(mul(sub(c1, p0), 3 * s * s), mul(sub(c2, c1), 6 * s * t)), mul(sub(p1, c2), 3 * t * t))
            d2 = add(mul(add(sub(c2, mul(c1, 2)), p0), 6 * s), mul(add(sub(p1, mul(c2, 2)), c1), 6 * t))
            den = dot(d1, d1) + dot(sub(q, p), d2)
            nts.append(min(1.0, max(0.0, t - dot(sub(q, p), d1) / den)) if den else t)
        ts = nts
    err = max(norm(sub(bez(p0, c1, c2, p1, t), p)) for p, t in zip(seg, ts))
    return c1, c2, err


def snap(p):
    """Anchors land on whole units when that moves them less than a quarter unit."""
    return tuple(round(v) if abs(v - round(v)) < 0.25 else v for v in p)


def fit_piece(seg, t0, t1, out, depth=0):
    """Append commands for points seg (seg[0] already emitted) to out."""
    p0, p1 = seg[0], seg[-1]
    chord = sub(p1, p0)
    if max((abs(chord[0] * (p0[1] - p[1]) - chord[1] * (p0[0] - p[0])) / (norm(chord) or 1) for p in seg),
           default=0) < TOL:
        out.append(f'L{pt(snap(p1))}')
        return
    if len(seg) >= 4:
        circ = fit_circle(seg)
        if circ and circ[2] < TOL and circ[1] < 400:
            c, r, _ = circ
            sweep = 1 if (sub(seg[1], p0)[0] * (p0[1] - c[1]) * -1 + sub(seg[1], p0)[1] * (p0[0] - c[0])) > 0 else 0
            a0, a1 = math.atan2(p0[1] - c[1], p0[0] - c[0]), math.atan2(p1[1] - c[1], p1[0] - c[0])
            span = (a1 - a0) % (2 * math.pi) if sweep else (a0 - a1) % (2 * math.pi)
            rr = round(r) if abs(r - round(r)) < 0.2 else r
            out.append(f'A{f(rr)} {f(rr)} 0 {1 if span > math.pi else 0} {sweep} {pt(snap(p1))}')
            return
    c1, c2, err = fit_cubic(seg, t0, t1)
    if err < TOL or len(seg) < 4 or depth > 6:
        out.append(f'C{pt(c1)} {pt(c2)} {pt(snap(p1))}')
        return
    k = len(seg) // 2
    tm = unit(sub(seg[min(k + 2, len(seg) - 1)], seg[max(k - 2, 0)]))
    fit_piece(seg[:k + 1], t0, tm, out, depth + 1)
    fit_piece(seg[k:], tm, t1, out, depth + 1)


def refit(pts, closed):
    n = len(pts)
    keep = anchors(pts, closed)
    # Tangents per anchor: one shared direction at smooth anchors, one-sided at corners.
    corner = {i for i in keep if (not closed and i in (0, n - 1)) or
              turn(pts[i - 1], pts[i], pts[(i + 1) % n]) > CORNER or
              norm(sub(pts[i], pts[i - 1])) > LONG or norm(sub(pts[(i + 1) % n], pts[i])) > LONG}
    def tan(i, side):
        if i in corner:
            return tangent(pts, i, closed, side)
        t = tangent(pts, i, closed, 0)
        # Extremes get an exactly horizontal or vertical tangent.
        if abs(t[0]) > 0.995: t = (math.copysign(1, t[0]), 0.0)
        if abs(t[1]) > 0.995: t = (0.0, math.copysign(1, t[1]))
        return t
    out = [f'M{pt(snap(pts[keep[0]]))}']
    pairs = list(zip(keep, keep[1:])) + ([(keep[-1], keep[0] + n)] if closed else [])
    for a, b in pairs:
        seg = [pts[j % n] for j in range(a, b + 1)]
        fit_piece(seg, tan(a, 1), tan(b % n, -1), out)
    if closed:
        last = out.pop()
        # The closing segment ends where the path started; Z draws it when it is straight.
        if not last.startswith('L'):
            out.append(last)
        out.append('Z')
    return ' '.join(out)


def refit_d(d):
    subs = parse(d)
    if not subs or sum(len(p) for p, _ in subs) <= MIN_SEGMENTS:
        return d
    return ' '.join(refit(p, c) if len(p) > 8 else 'M' + ' L'.join(pt(q) for q in p) + (' Z' if c else '')
                    for p, c in subs)


def main(args):
    out_dir = args[args.index('--out') + 1] if '--out' in args else os.path.join(ROOT, 'icons')
    src = os.path.join(ROOT, 'icons')
    changed = []
    for name in sorted(os.listdir(src)):
        s = open(os.path.join(src, name)).read()
        new = re.sub(r' d="([^"]*)"', lambda m: f' d="{refit_d(m.group(1))}"', s)
        if new != s:
            with open(os.path.join(out_dir, name), 'w') as fh:
                fh.write(new)
            changed.append((name[:-4], len(s), len(new)))
    for n, a, b in changed:
        print(f'{n}: {a} -> {b} bytes')
    print(f'{len(changed)} icons refitted')


if __name__ == '__main__':
    main(sys.argv[1:])
