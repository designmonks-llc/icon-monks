import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

DV = 'Development'

# ================================================================ small outline engine
# Segments: ('L', p0, p1) | ('C', p0, c1, c2, p1) | ('A', centre, r, a0, a1) | ('E', centre, rx, ry, a0, a1)
# (angles in radians, a1 may be < a0; for 'E' they are the ellipse's parametric angles)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def seg_point(s, t):
    if s[0] == 'L':
        return lerp(s[1], s[2], t)
    if s[0] == 'C':
        p0, c1, c2, p1 = s[1:]
        a, b, c = lerp(p0, c1, t), lerp(c1, c2, t), lerp(c2, p1, t)
        d, e = lerp(a, b, t), lerp(b, c, t)
        return lerp(d, e, t)
    if s[0] == 'E':
        c, rx, ry, a0, a1 = s[1:]
        a = a0 + (a1 - a0) * t
        return (c[0] + rx * math.cos(a), c[1] + ry * math.sin(a))
    c, r, a0, a1 = s[1:]
    a = a0 + (a1 - a0) * t
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def split_cubic(p0, c1, c2, p1, t):
    a, b, c = lerp(p0, c1, t), lerp(c1, c2, t), lerp(c2, p1, t)
    d, e = lerp(a, b, t), lerp(b, c, t)
    m = lerp(d, e, t)
    return (p0, a, d, m), (m, e, c, p1)


def seg_sub(s, t0, t1):
    if s[0] == 'L':
        return ('L', lerp(s[1], s[2], t0), lerp(s[1], s[2], t1))
    if s[0] == 'C':
        _, right = split_cubic(*s[1:], t0)
        if t1 >= 1:
            return ('C',) + right
        left, _ = split_cubic(*right, (t1 - t0) / (1 - t0))
        return ('C',) + left
    if s[0] == 'E':
        c, rx, ry, a0, a1 = s[1:]
        return ('E', c, rx, ry, a0 + (a1 - a0) * t0, a0 + (a1 - a0) * t1)
    c, r, a0, a1 = s[1:]
    return ('A', c, r, a0 + (a1 - a0) * t0, a0 + (a1 - a0) * t1)


def seg_end(s):
    return seg_point(s, 1)


def seg_cmd(s):
    if s[0] == 'L':
        return f'L{pt(s[2])}'
    if s[0] == 'C':
        return f'C{pt(s[2])} {pt(s[3])} {pt(s[4])}'
    if s[0] == 'E':
        c, rx, ry, a0, a1 = s[1:]
        large = 1 if abs(a1 - a0) > math.pi else 0
        sweep = 1 if a1 > a0 else 0
        return f'A{f(rx)} {f(ry)} 0 {large} {sweep} {pt(seg_end(s))}'
    c, r, a0, a1 = s[1:]
    if abs(a1 - a0) >= 2 * math.pi - 1e-6:  # full circle: two halves
        m = seg_point(s, 0.5)
        sweep = 1 if a1 > a0 else 0
        return f'A{f(r)} {f(r)} 0 1 {sweep} {pt(m)} A{f(r)} {f(r)} 0 1 {sweep} {pt(seg_end(s))}'
    large = 1 if abs(a1 - a0) > math.pi else 0
    sweep = 1 if a1 > a0 else 0
    return f'A{f(r)} {f(r)} 0 {large} {sweep} {pt(seg_end(s))}'


def segs_d(segs, close=False):
    d = f'M{pt(seg_point(segs[0], 0))} ' + ' '.join(seg_cmd(s) for s in segs)
    return d + (' Z' if close else '')


def trim(segs, keep, closed=True, steps=240):
    """Split an outline into runs of segments where keep(point) holds."""
    pieces = []  # (seg index, t0, t1)
    for i, s in enumerate(segs):
        ts = [k / steps for k in range(steps + 1)]
        ok = [keep(seg_point(s, t)) for t in ts]

        def edge(ta, tb, oa):
            for _ in range(40):
                tm = (ta + tb) / 2
                if keep(seg_point(s, tm)) == oa:
                    ta = tm
                else:
                    tb = tm
            return (ta + tb) / 2
        start = 0.0 if ok[0] else None
        for k in range(1, len(ts)):
            if ok[k] != ok[k - 1]:
                e = edge(ts[k - 1], ts[k], ok[k - 1])
                if ok[k]:
                    start = e
                else:
                    pieces.append((i, start, e))
                    start = None
        if start is not None:
            pieces.append((i, start, 1.0))
    if len(pieces) == len(segs) and all(t0 == 0 and t1 == 1 for _, t0, t1 in pieces):
        return [segs], True
    runs = []
    for i, t0, t1 in pieces:
        sub = seg_sub(segs[i], t0, t1)
        if runs and t0 == 0 and runs[-1][1] == (i - 1, 1.0):
            runs[-1][0].append(sub)
        else:
            runs.append([[sub], None])
        runs[-1][1] = (i, t1)
    if closed and len(runs) > 1 and pieces[0][1] == 0 and pieces[0][0] == 0 and pieces[-1][2] == 1.0 \
            and pieces[-1][0] == len(segs) - 1:
        last = runs.pop()
        runs[0][0] = last[0] + runs[0][0]
    return [r[0] for r in runs], False


def sample(segs, n=60):
    return [seg_point(s, k / n) for s in segs for k in range(n)]


def run_len(run):
    pts = sample(run, 30) + [seg_end(run[-1])]
    return sum(dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def inside(poly_pts, p):
    x, y = p
    c = False
    for i in range(len(poly_pts)):
        x1, y1 = poly_pts[i]
        x2, y2 = poly_pts[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def carve(segs, cut_c, cut_r):
    """Open the closed outline segs around a circular badge. Returns (line d, area d)."""
    runs, whole = trim(segs, lambda p: dist(p, cut_c) >= cut_r)
    assert not whole and len(runs) == 1, (whole, len(runs))
    run = runs[0]
    s, e = seg_point(run[0], 0), seg_end(run[-1])
    poly_pts = sample(segs)
    arc = arc_to(cut_c, cut_r, e, s, lambda m: 1 if inside(poly_pts, m) else 0)
    return segs_d(run), segs_d(run) + ' ' + arc + ' Z'


def clear(segs, cut_c, cut_r, closed=False, min_len=14):
    """Pieces of an outline (open or closed) that stay out of a badge circle, as path elements."""
    runs, whole = trim(segs, lambda p: dist(p, cut_c) >= cut_r, closed)
    if whole:
        return [P(segs_d(segs, closed))]
    return [P(segs_d(r)) for r in runs if r and run_len(r) >= min_len]


def ang(c, p):
    return math.atan2(p[1] - c[1], p[0] - c[0])


def polyline_segs(points, closed=False):
    pts = list(points) + ([points[0]] if closed else [])
    return [('L', pts[i], pts[i + 1]) for i in range(len(pts) - 1)]


def rpoly_segs(points, r):
    """Closed polygon with round corners of radius r, as segments."""
    n = len(points)
    corners = []
    for i in range(n):
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        u = ((p0[0] - p1[0]) / dist(p0, p1), (p0[1] - p1[1]) / dist(p0, p1))
        v = ((p2[0] - p1[0]) / dist(p2, p1), (p2[1] - p1[1]) / dist(p2, p1))
        th = math.acos(max(-1, min(1, u[0] * v[0] + u[1] * v[1])))
        t = r / math.tan(th / 2)
        a = (p1[0] + u[0] * t, p1[1] + u[1] * t)
        b = (p1[0] + v[0] * t, p1[1] + v[1] * t)
        bis = (u[0] + v[0], u[1] + v[1]); bl = math.hypot(*bis)
        h = r / math.sin(th / 2)
        c = (p1[0] + bis[0] / bl * h, p1[1] + bis[1] / bl * h)
        a0, a1 = ang(c, a), ang(c, b)
        while a1 - a0 > math.pi:
            a1 -= 2 * math.pi
        while a0 - a1 > math.pi:
            a1 += 2 * math.pi
        corners.append((a, b, ('A', c, r, a0, a1)))
    segs = []
    for i in range(n):
        a, b, arc = corners[i]
        segs.append(arc)
        segs.append(('L', b, corners[(i + 1) % n][0]))
    return segs


def rrect_segs(x, y, w, h, r):
    return rpoly_segs([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], r)


def circle_segs(c, r):
    return [('A', c, r, -math.pi / 2, 1.5 * math.pi)]


def seg_tf(segs, s, dx, dy, c=(128, 128)):
    tp = lambda p: (c[0] + (p[0] - c[0]) * s + dx, c[1] + (p[1] - c[1]) * s + dy)
    out = []
    for g in segs:
        if g[0] == 'L':
            out.append(('L', tp(g[1]), tp(g[2])))
        elif g[0] == 'C':
            out.append(('C',) + tuple(tp(p) for p in g[1:]))
        elif g[0] == 'E':
            out.append(('E', tp(g[1]), g[2] * s, g[3] * s, g[4], g[5]))
        else:
            out.append(('A', tp(g[1]), g[2] * s, g[3], g[4]))
    return out


def merge(*ds):
    out = dict(line=[], area=[], hole=[], dot=[], detail=[], dotcut=[])
    for d in ds:
        for k, v in d.items():
            out[k] += v
    return {k: v for k, v in out.items() if v}


# ---------------------------------------------------------------- slash helpers
SLASH = L(48, 48, 208, 208)
SG = 30


def seg_dist(p, a=(48, 48), b=(208, 208)):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + dx * t, a[1] + dy * t))


def gapped(outline, closed=True, min_len=20, sg=SG):
    runs, whole = trim(outline, lambda p: seg_dist(p) >= sg, closed)
    if whole:
        return [P(segs_d(outline, closed))]
    return [P(segs_d(r)) for r in runs if r and run_len(r) >= min_len]


# ---------------------------------------------------------------- badge marks around B
B = (184, 184)
BX, BY = B


def T(pts, dx=BX, dy=BY):
    return [(x + dx, y + dy) for x, y in pts]


def gear_path(c, r_root, r_tip, n, phase=0):
    step = 360 / n
    hr, ht = step * 0.3, step * 0.17
    pts = []
    for i in range(n):
        t = phase + i * step
        pts.append((polar(c, r_root, t - hr), polar(c, r_tip, t - ht), polar(c, r_tip, t + ht), polar(c, r_root, t + hr)))
    d = 'M' + pt(pts[0][0])
    for i, (a, b, cc, dd) in enumerate(pts):
        if i:
            d += f' A{f(r_root)} {f(r_root)} 0 0 1 {pt(a)}'
        d += f' L{pt(b)} L{pt(cc)} L{pt(dd)}'
    d += f' A{f(r_root)} {f(r_root)} 0 0 1 {pt(pts[0][0])} Z'
    return d


def badge(kind):
    """Returns (roles dict, clearance radius)."""
    b = dict(line=[], area=[], hole=[], dot=[], detail=[])
    cr = 56
    if kind == 'plus':
        b['line'] = [L(BX, BY - 26, BX, BY + 26), L(BX - 26, BY, BX + 26, BY)]
    elif kind == 'minus':
        b['line'] = [L(BX - 26, BY, BX + 26, BY)]
        cr = 50
    elif kind == 'arrow-down':
        b['line'] = [L(BX, BY - 30, BX, BY + 30), PL(T([(-22, 8), (0, 30), (22, 8)]))]
        cr = 58
    elif kind == 'arrow-up':
        b['line'] = [L(BX, BY + 30, BX, BY - 30), PL(T([(-22, -8), (0, -30), (22, -8)]))]
        cr = 58
    elif kind == 'arrows':
        b['line'] = [L(BX - 18, BY + 30, BX - 18, BY - 30), PL(T([(-32, -16), (-18, -30), (-4, -16)])),
                     L(BX + 18, BY - 30, BX + 18, BY + 30), PL(T([(4, 16), (18, 30), (32, 16)]))]
        cr = 62
    elif kind == 'backup':
        ac, ar = B, 28
        a_end = polar(ac, ar, -100)
        b['line'] = [P(f'M{pt(polar(ac, ar, -40))} A{ar} {ar} 0 1 1 {pt(a_end)}'),
                     PL([polar(a_end, 20, 170), a_end, polar(a_end, 20, 80)])]
        cr = 62
    elif kind == 'code':
        b['line'] = [PL(T([(-14, -20), (-34, 0), (-14, 20)])), PL(T([(14, -20), (34, 0), (14, 20)]))]
        cr = 60
    elif kind == 'dollar':
        b['line'] = [P(f'M{BX + 16} {BY - 24} H{BX - 4} A12 12 0 0 0 {BX - 4} {BY} '
                       f'H{BX + 4} A12 12 0 0 1 {BX + 4} {BY + 24} H{BX - 16}'),
                     L(BX, BY - 38, BX, BY - 24), L(BX, BY + 24, BX, BY + 38)]
        cr = 60
    elif kind == 'bitcoin':
        x0 = BX - 18
        b['line'] = [P(f'M{x0} {BY - 28} H{BX + 2} A14 14 0 0 1 {BX + 2} {BY} H{x0}'),
                     P(f'M{x0} {BY} H{BX + 4} A14 14 0 0 1 {BX + 4} {BY + 28} H{x0} Z'),
                     L(x0, BY - 28, x0, BY + 28),
                     L(BX - 4, BY - 40, BX - 4, BY - 28), L(BX - 4, BY + 28, BX - 4, BY + 40)]
        cr = 62
    elif kind == 'gear':
        g = gear_path(B, 20, 31, 6, -90)
        b['line'] = [P(g)]
        b['area'] = [P(g)]
        b['hole'] = [C(BX, BY, 7)]
        cr = 60
    elif kind == 'magnifying-glass':
        b['line'] = [C(BX - 6, BY - 6, 18), L(BX + 8, BY + 8, BX + 26, BY + 26)]
        b['area'] = [C(BX - 6, BY - 6, 18)]
    elif kind == 'pause':
        b['line'] = [L(BX - 16, BY - 24, BX - 16, BY + 24), L(BX + 16, BY - 24, BX + 16, BY + 24)]
        cr = 54
    elif kind == 'push-pin':
        import re
        pp = load('push-pin')

        def pin_pts(d):
            return [(float(a), float(bb)) for a, bb in re.findall(r'([-\d.]+) ([-\d.]+)', d)]
        body = pin_pts(re.search(r'd="([^"]+)"', pp['line'][0]).group(1))
        needle = pin_pts(re.search(r'd="([^"]+)"', pp['line'][1]).group(1))
        s_, cx0, cy0 = 0.34, 133, 124
        tf = lambda q: [(BX + (x - cx0) * s_, BY + (y - cy0) * s_) for x, y in q]
        b['line'] = [PG(tf(body)), PL(tf(needle))]
        b['area'] = [PG(tf(body))]
        cr = 58
    elif kind == 'star':
        st = [polar((BX, BY + 3), 34 if i % 2 == 0 else 15, -90 + i * 36) for i in range(10)]
        b['line'] = [PG(st)]
        b['area'] = [PG(st)]
        cr = 60
    elif kind == 'link':
        u = (1 / math.sqrt(2), -1 / math.sqrt(2))
        c1 = (BX - u[0] * 16, BY - u[1] * 16)
        c2 = (BX + u[0] * 16, BY + u[1] * 16)
        b['line'] = [P(capsule(c1, 12, 15, u)), P(capsule(c2, 12, 15, u))]
        cr = 62
    else:
        raise ValueError(kind)
    return b, cr


# ================================================================ base geometry (exact copies of library icons)
CLOUD_D = load('cloud')['line'][0]
_cl_r = 44
CLOUD = [('L', (84, 192), (180, 192)),
         ('A', (180, 148), 44, math.pi / 2, ang((180, 148), (191.06, 105.41))),
         ('A', (132, 116), 60, ang((132, 116), (191.06, 105.41)), ang((132, 116), (72.04, 113.83)) - 2 * math.pi
          if ang((132, 116), (72.04, 113.83)) > ang((132, 116), (191.06, 105.41)) else ang((132, 116), (72.04, 113.83))),
         ('A', (84, 152), 40, ang((84, 152), (72.04, 113.83)), math.pi / 2 - 2 * math.pi)]

DB_D = load('database')['line'][0]
DB = [('E', (128, 64), 88, 32, math.pi, 2 * math.pi), ('L', (216, 64), (216, 192)),
      ('E', (128, 192), 88, 32, 0, math.pi), ('L', (40, 192), (40, 64))]
DB_BANDS = [[('E', (128, 64), 88, 32, math.pi, 0)], [('E', (128, 128), 88, 32, math.pi, 0)]]

CODE_L = polyline_segs([(72, 72), (32, 128), (72, 184)])
CODE_R = polyline_segs([(184, 72), (224, 128), (184, 184)])
CODE_S = polyline_segs([(148, 52), (108, 204)])
CODE = [PL([(72, 72), (32, 128), (72, 184)]), PL([(184, 72), (224, 128), (184, 184)])]
CODE_FULL = CODE + [L(148, 52, 108, 204)]


def badge_on_open(parts, kind):
    """parts: list of open segment lists (strokes); carve them around the badge and add the mark."""
    b, cr = badge(kind)
    out = []
    for p in parts:
        out += clear(p, B, cr + 4)
    return merge(dict(line=out), b)


def cloud_badge(kind):
    b, cr = badge(kind)
    ln, ar = carve(seg_tf(CLOUD, 1, -8, -16), B, cr)
    return merge(dict(line=[P(ln)], area=[P(ar)]), b)


def db_badge(kind):
    b, cr = badge(kind)
    ln, ar = carve(DB, B, cr)
    det = []
    for band in DB_BANDS:
        det += clear(band, B, cr + 4)
    return merge(dict(line=[P(ln)], area=[P(ar)], detail=det), b)


# ================================================================ cloud family
CLOUD_TAGS = {
    'bitcoin': (['cloud', 'crypto', 'bitcoin', 'storage', 'online'], 'bitcoin'),
    'code': (['cloud', 'developer', 'code', 'storage', 'online'], 'code'),
    'currency-dollar': (['cloud', 'money', 'price', 'storage', 'online'], 'dollar'),
    'gear': (['cloud', 'settings', 'configure', 'storage', 'online'], 'gear'),
    'magnifying-glass': (['cloud', 'search', 'find', 'storage', 'online'], 'magnifying-glass'),
    'pause': (['cloud', 'paused', 'hold', 'storage', 'online'], 'pause'),
    'push-pin': (['cloud', 'pinned', 'pin', 'storage', 'online'], 'push-pin'),
    'star': (['cloud', 'favorite', 'starred', 'storage', 'online'], 'star'),
    'link': (['cloud link', 'shared link', 'cloud', 'url'], 'link'),
}
for suffix, (tags, kind) in CLOUD_TAGS.items():
    icon(f'cloud-{suffix}', DV, tags, **cloud_badge(kind))

# cloud above a database cylinder
sc_cloud = seg_tf(CLOUD, 0.62, -4, -50)
icon('cloud-database', DV, ['cloud storage', 'server', 'hosting', 'backup'],
     line=[P(segs_d(sc_cloud, True)), P('M60 172 A68 18 0 0 1 196 172 V206 A68 18 0 0 1 60 206 Z')],
     detail=[P('M60 172 A68 18 0 0 0 196 172')],
     area=[P(segs_d(sc_cloud, True)), P('M60 172 A68 18 0 0 1 196 172 V206 A68 18 0 0 1 60 206 Z')])

# cloud with connected nodes beneath
nc_cloud = seg_tf(CLOUD, 0.72, -6, -44)
icon('cloud-network', DV, ['cloud network', 'cloud', 'storage', 'online', 'network'],
     line=[P(segs_d(nc_cloud, True)), L(128, 130, 128, 200), L(48, 200, 208, 200)],
     area=[P(segs_d(nc_cloud, True))],
     dot=[C(48, 200, 16), C(128, 200, 16), C(208, 200, 16)])

# ================================================================ database family
for suffix, tags in (('arrow-down', ['database', 'download', 'import', 'storage', 'data import']),
                     ('arrow-up', ['database', 'upload', 'export', 'storage']),
                     ('arrows', ['sync data', 'transfer', 'database', 'exchange']),
                     ('backup', ['backup', 'restore point', 'data copy', 'database'])):
    icon(f'database-{suffix}', DV, tags, **db_badge(suffix))


# ================================================================ code family (base: code)
icon('code-minus', DV, ['code', 'remove', 'subtract', 'developer', 'programming'],
     **badge_on_open([CODE_L, CODE_R, CODE_S], 'minus'))
icon('code-plus', DV, ['code', 'add', 'new', 'developer', 'programming'],
     **badge_on_open([CODE_L, CODE_R, CODE_S], 'plus'))
icon('code-arrow-down', DV, ['download code', 'source', 'export', 'arrow'],
     line=CODE + [L(128, 56, 128, 196), PL([(96, 164), (128, 196), (160, 164)])])
icon('code-asterisk', DV, ['code asterisk', 'code', 'developer', 'programming', 'asterisk'],
     line=CODE + [L(*polar((128, 128), 44, a), *polar((128, 128), 44, a + 180)) for a in (-90, -30, 30)])
icon('code-dots', DV, ['code dots', 'code', 'developer', 'programming', 'dots'],
     line=CODE, dot=[C(84, 128, 16), C(128, 128, 16), C(172, 128, 16)])
CODE_IN = [PL([(100, 96), (72, 128), (100, 160)]), PL([(156, 96), (184, 128), (156, 160)]), L(140, 88, 116, 168)]
icon('code-circle', DV, ['code circle', 'code', 'developer', 'programming', 'circle'],
     line=[C(128, 128, 96)], detail=CODE_IN, area=[C(128, 128, 96)])
icon('code-square', DV, ['code', 'square', 'brackets', 'embed'],
     line=[R(32, 32, 192, 192, 16)], detail=CODE_IN, area=[R(32, 32, 192, 192, 16)])
sp_s = 0.42
sp = ('M128 32 C136 96 160 120 224 128 C160 136 136 160 128 224 C120 160 96 136 32 128 C96 120 120 96 128 32 Z')
import re as _re
_nums = [float(v) for v in _re.findall(r'[-\d.]+', sp)]
_sp_pts = [(128 + (_nums[i] - 128) * sp_s, 128 + (_nums[i + 1] - 128) * sp_s) for i in range(0, len(_nums), 2)]
SPARK = 'M' + pt(_sp_pts[0]) + ''.join(' C' + ' '.join(pt(q) for q in _sp_pts[i:i + 3]) for i in range(1, len(_sp_pts), 3)) + ' Z'
icon('code-sparkle', DV, ['ai code', 'copilot', 'generate', 'sparkle'],
     line=CODE + [P(SPARK)], area=[P(SPARK)])
icon('code-slash', DV, ['code off', 'disable code', 'developer', 'brackets', 'no code'],
     line=gapped(CODE_L, False, 20, 24) + gapped(CODE_R, False, 20, 24) + gapped(CODE_S, False, 20, 24) + [SLASH])


# ---------------------------------------------------------------- braces
def brace_segs(x_end, spine, tip, top=40, bot=216, r=20):
    """Left curly brace like the library's brackets-curly; mirror for the right one."""
    q1, q2 = 100 - 40 + top + 0, 156 - 216 + bot
    q1 = top + 60
    q2 = bot - 60
    k = 2 / 3
    return [('L', (x_end, top), (spine + r, top)),
            ('A', (spine + r, top + r), r, -math.pi / 2, -math.pi),
            ('L', (spine, top + r), (spine, q1)),
            ('C', (spine, q1), (spine, q1 + k * (128 - q1)), (tip + k * (spine - tip), 128), (tip, 128)),
            ('C', (tip, 128), (tip + k * (spine - tip), 128), (spine, q2 - k * (q2 - 128)), (spine, q2)),
            ('L', (spine, q2), (spine, bot - r)),
            ('A', (spine + r, bot - r), r, math.pi, math.pi / 2),
            ('L', (spine + r, bot), (x_end, bot))]


def mirror(segs):
    out = []
    mp = lambda p: (256 - p[0], p[1])
    for g in segs:
        if g[0] == 'L':
            out.append(('L', mp(g[1]), mp(g[2])))
        elif g[0] == 'C':
            out.append(('C',) + tuple(mp(q) for q in g[1:]))
        elif g[0] == 'A':
            out.append(('A', mp(g[1]), g[2], math.pi - g[3], math.pi - g[4]))
        else:
            out.append(('E', mp(g[1]), g[2], g[3], math.pi - g[4], math.pi - g[5]))
    return out


CURLY_L = brace_segs(108, 80, 52)
CURLY_R = mirror(CURLY_L)
icon('brackets-curly-slash', DV, ['brackets curly', 'disabled', 'off', 'brackets', 'code'],
     line=gapped(CURLY_L, False, 28, 22) + gapped(CURLY_R, False, 28, 22) + [SLASH])

VAR_L = brace_segs(88, 60, 32)
VAR_R = mirror(VAR_L)
VAR_X = [polyline_segs([(102, 102), (154, 154)]), polyline_segs([(154, 102), (102, 154)])]
VAR_XS = [L(96, 102, 148, 154), L(148, 102, 96, 154)]  # nudged left to clear the badge
icon('code-variable', DV, ['code variable', 'code', 'developer', 'programming', 'variable'],
     line=[P(segs_d(VAR_L)), P(segs_d(VAR_R))] + [P(segs_d(x)) for x in VAR_X])
icon('code-variable-plus', DV, ['code variable', 'add', 'new', 'code', 'developer'],
     **merge(badge_on_open([VAR_L, VAR_R], 'plus'), dict(line=VAR_XS)))
icon('code-variable-minus', DV, ['code variable', 'remove', 'subtract', 'code', 'developer'],
     **merge(badge_on_open([VAR_L, VAR_R], 'minus'), dict(line=VAR_XS)))

# ---------------------------------------------------------------- angle / round / square brackets
ANG_L = polyline_segs([(96, 48), (40, 128), (96, 208)])
ANG_R = polyline_segs([(160, 48), (216, 128), (160, 208)])
icon('brackets-angle', DV, ['angle brackets', 'html', 'xml', 'tag'],
     line=[P(segs_d(ANG_L)), P(segs_d(ANG_R))])
icon('brackets-angle-slash', DV, ['brackets angle', 'disabled', 'off', 'brackets', 'code'],
     line=[P(segs_d(ANG_L)), P(segs_d(ANG_R)), SLASH])

_rc = (180.8, 128)
_rr = dist(_rc, (104, 40))
_ra = ang(_rc, (104, 40))
ROUND_L = [('A', _rc, _rr, _ra, -2 * math.pi - _ra)]
ROUND_R = mirror(ROUND_L)
icon('brackets-round', DV, ['parentheses', 'brackets', 'code', 'round'],
     line=[P(segs_d(ROUND_L)), P(segs_d(ROUND_R))])
icon('brackets-round-slash', DV, ['brackets round', 'off', 'disabled', 'hidden', 'brackets'],
     line=gapped(ROUND_L, False) + gapped(ROUND_R, False) + [SLASH])

SQ_L = polyline_segs([(104, 40), (64, 40), (64, 216), (104, 216)])
SQ_R = mirror(SQ_L)
icon('brackets-square-slash', DV, ['brackets square', 'disabled', 'off', 'brackets', 'code'],
     line=gapped(SQ_L, False, 30) + gapped(SQ_R, False, 30) + [SLASH])

# brackets holding a block of content: both sides, opening side, closing side
icon('brackets-contain', DV, ['brackets contain', 'brackets', 'code', 'contain', 'development'],
     line=[PL([(76, 40), (40, 40), (40, 216), (76, 216)]), PL([(180, 40), (216, 40), (216, 216), (180, 216)]),
           R(92, 92, 72, 72, 12)],
     area=[R(92, 92, 72, 72, 12)])
icon('brackets-contain-start', DV, ['brackets contain start', 'brackets', 'code', 'contain', 'start'],
     line=[PL([(84, 40), (48, 40), (48, 216), (84, 216)]), R(100, 92, 116, 72, 12)],
     area=[R(100, 92, 116, 72, 12)])
icon('brackets-contain-end', DV, ['brackets contain end', 'brackets', 'code', 'contain', 'end'],
     line=[PL([(172, 40), (208, 40), (208, 216), (172, 216)]), R(40, 92, 116, 72, 12)],
     area=[R(40, 92, 116, 72, 12)])

# ================================================================ api: two brackets joined through a hub
API_L = [('L', (84, 56), (56, 56)), ('A', (56, 72), 16, -math.pi / 2, -math.pi), ('L', (40, 72), (40, 184)),
         ('A', (56, 184), 16, math.pi, math.pi / 2), ('L', (56, 200), (84, 200))]
API_R = mirror(API_L)
API_C = [polyline_segs([(40, 128), (100, 128)]), polyline_segs([(156, 128), (216, 128)])]
icon('api', DV, ['api', 'interface', 'endpoint', 'integration'],
     line=[P(segs_d(API_L)), P(segs_d(API_R))] + [P(segs_d(c)) for c in API_C] + [C(128, 128, 28)],
     area=[C(128, 128, 28)])
icon('api-slash', DV, ['api', 'disabled', 'off', 'development'],
     line=gapped(API_L, False) + gapped(API_R, False) + sum((gapped(c, False) for c in API_C), [])
     + gapped(circle_segs((128, 128), 28), False) + [SLASH])

# ================================================================ assembly: hexagon holding a rounded hexagon
HEX_D = load('hexagon')['line'][0]
HEX = polyline_segs(regular_polygon((128, 128), 96, 6), True)
IHEX = rpoly_segs(regular_polygon((128, 128), 48, 6), 10)
icon('assembly', DV, ['assembly', 'build', 'module', 'package'],
     line=[HEX_D], detail=[P(segs_d(IHEX, True))], area=[HEX_D])
icon('assembly-slash', DV, ['assembly', 'disabled', 'off', 'development'],
     line=gapped(HEX) + gapped(IHEX) + [SLASH])

# ================================================================ asset graph
icon('asset', DV, ['asset', 'resource', 'nodes', 'graph'],
     line=[R(100, 32, 56, 56, 12), C(64, 184, 28), C(192, 184, 28),
           L(113.5, 88, 76.8, 159.1), L(142.5, 88, 179.2, 159.1), L(92, 184, 164, 184)],
     area=[R(100, 32, 56, 56, 12), C(64, 184, 28), C(192, 184, 28)])


# ================================================================ binary
def one(cx, y, h=68):
    return [polyline_segs([(cx - 20, y + 18), (cx, y), (cx, y + h)])]


def zero(cx, y, h=68):
    return [rrect_segs(cx - 24, y, 48, h, 24)]


BIN = [(zero(80, 40), True), (one(176, 40), False), (one(80, 148), False), (zero(176, 148), True)]
icon('binary', DV, ['binary', 'code', 'bits', '01'],
     line=[P(segs_d(sg, closed)) for parts, closed in BIN for sg in parts])
icon('binary-slash', DV, ['binary', 'disabled', 'off', 'development'],
     line=[P(segs_d(sg, closed)) for parts, closed in BIN for sg in parts] + [SLASH])

# ================================================================ binary tree
NODES = {'r': (128, 48), 'a': (76, 128), 'b': (180, 128), 'a1': (44, 208), 'a2': (104, 208), 'b1': (152, 208), 'b2': (212, 208)}
icon('binary-tree', DV, ['tree', 'data structure', 'hierarchy', 'nodes'],
     line=[PL([NODES['a'], NODES['r'], NODES['b']]), PL([NODES['a1'], NODES['a'], NODES['a2']]),
           PL([NODES['b1'], NODES['b'], NODES['b2']])],
     dot=[C(*NODES[k], 16) for k in NODES])

# ================================================================ blockchain: three linked cubes


def cube_parts(c, r):
    hx = regular_polygon(c, r, 6)  # top, upper right, lower right, bottom, lower left, upper left
    d = PG(hx)
    det = [PL([hx[5], c, hx[1]]), L(c[0], c[1], hx[3][0], hx[3][1])]
    return d, det


cubes = [((128, 72), 40), ((68, 180), 40), ((188, 180), 40)]
bl_line, bl_det, bl_area = [], [], []
for cc, rr in cubes:
    d_, det_ = cube_parts(cc, rr)
    bl_line.append(d_); bl_area.append(d_); bl_det += det_
for (c1, r1), (c2, r2) in ((cubes[0], cubes[1]), (cubes[0], cubes[2]), (cubes[1], cubes[2])):
    u = ((c2[0] - c1[0]) / dist(c1, c2), (c2[1] - c1[1]) / dist(c1, c2))
    a0, a1 = r1 * 0.866 + 14, dist(c1, c2) - r2 * 0.866 - 14
    bl_line.append(L(c1[0] + u[0] * a0, c1[1] + u[1] * a0, c1[0] + u[0] * a1, c1[1] + u[1] * a1))
icon('blockchain', DV, ['blockchain', 'chain', 'ledger', 'crypto'], line=bl_line, detail=bl_det, area=bl_area)

# ================================================================ blocks: three squares plus one tipped square
DIA = rpoly_segs([(180, 36), (220, 76), (180, 116), (140, 76)], 8)
BLK = [R(40, 56, 68, 68, 10), R(40, 148, 68, 68, 10), R(132, 148, 68, 68, 10), P(segs_d(DIA, True))]
icon('blocks', DV, ['blocks', 'modules', 'components', 'build'], line=BLK, area=BLK)

# ================================================================ bug slash (base: bug)
BUG_BODY = rrect_segs(80, 80, 96, 136, 47.9)
BUG_STROKES = [polyline_segs(p) for p in (
    [(108, 80), (92, 48)], [(148, 80), (164, 48)], [(40, 152), (80, 152)], [(176, 152), (216, 152)],
    [(48, 104), (84, 116)], [(208, 104), (172, 116)], [(48, 204), (84, 188)], [(208, 204), (172, 188)],
    [(80, 128), (176, 128)], [(128, 156), (128, 192)])]
icon('bug-slash', DV, ['bug', 'disabled', 'off', 'development'],
     line=gapped(BUG_BODY) + sum((gapped(sg, False) for sg in BUG_STROKES), []) + [SLASH])

# ================================================================ command slash (base: command)
CMD = [('L', (96, 96), (96, 64)), ('A', (64, 64), 32, 0, -1.5 * math.pi), ('L', (64, 96), (192, 96)),
       ('A', (192, 64), 32, math.pi / 2, -math.pi), ('L', (160, 64), (160, 192)),
       ('A', (192, 192), 32, math.pi, -math.pi / 2), ('L', (192, 160), (64, 160)),
       ('A', (64, 192), 32, -math.pi / 2, -2 * math.pi), ('L', (96, 192), (96, 96))]
icon('command-slash', DV, ['command', 'disabled', 'off', 'development'],
     line=gapped(CMD) + [SLASH])

# ================================================================ container: two stacked shipping containers
CT_RIBS = [L(x, y0, x, y0 + 32) for x in (88, 128, 168) for y0 in (68, 156)]
icon('container', DV, ['container', 'docker', 'shipping', 'box'],
     line=[R(40, 40, 176, 176, 14)], detail=[L(40, 128, 216, 128)] + CT_RIBS, area=[R(40, 40, 176, 176, 14)])
CT_SEGS = [rrect_segs(40, 40, 176, 176, 14), polyline_segs([(40, 128), (216, 128)])] + \
    [polyline_segs([(x, y0), (x, y0 + 32)]) for x in (88, 128, 168) for y0 in (68, 156)]
icon('container-slash', DV, ['container', 'disabled', 'development', 'off'],
     line=gapped(CT_SEGS[0]) + sum((gapped(sg, False, 12) for sg in CT_SEGS[1:]), []) + [SLASH])

# ================================================================ cube send: the library cube, smaller, with motion lines
CUBE_S, CUBE_C = 0.72, (160, 128)
_ct = lambda p: (CUBE_C[0] + (p[0] - 128) * CUBE_S, CUBE_C[1] + (p[1] - 128) * CUBE_S)
_hex = [_ct(p) for p in [(128, 32), (216, 80), (216, 176), (128, 224), (40, 176), (40, 80)]]
icon('cube-send', DV, ['deploy', 'ship', 'package', 'send'],
     line=[PG(_hex), L(48, 96, 76, 96), L(32, 128, 76, 128), L(48, 160, 76, 160)],
     detail=[PL([_hex[5], _ct((128, 128)), _hex[1]]), PL([_ct((128, 128)), _hex[3]])],
     area=[PG(_hex)])

# ================================================================ ai gateway: an arch with a sparkle passing through
ARCH = 'M48 216 V128 A80 80 0 0 1 208 128 V216'
_gs = [(128 + (_nums[i] - 128) * 0.46, 140 + (_nums[i + 1] - 128) * 0.46) for i in range(0, len(_nums), 2)]
GSPARK = 'M' + pt(_gs[0]) + ''.join(' C' + ' '.join(pt(q) for q in _gs[i:i + 3]) for i in range(1, len(_gs), 3)) + ' Z'
icon('ai-gateway', DV, ['ai', 'gateway', 'api', 'router'],
     line=[P(ARCH), L(32, 216, 224, 216)], detail=[P(GSPARK)], area=[P(ARCH + ' Z')])

print(save(overwrite=True))
