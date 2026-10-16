import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

DS = 'Design'
SLASH = L(48, 48, 208, 208)
B = (184, 184)  # badge centre


# ---------------------------------------------------------------- segment model
# A path is a list of segments: ('L', p, q) or ('E', c, rx, ry, t0, t1) (angles in degrees, screen coords).
def seg_at(s, u):
    if s[0] == 'L':
        p, q = s[1], s[2]
        return (p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u)
    _, c, rx, ry, t0, t1 = s
    t = math.radians(t0 + (t1 - t0) * u)
    return (c[0] + rx * math.cos(t), c[1] + ry * math.sin(t))


def sub(s, a, b):
    if s[0] == 'L':
        return ('L', seg_at(s, a), seg_at(s, b))
    _, c, rx, ry, t0, t1 = s
    return ('E', c, rx, ry, t0 + (t1 - t0) * a, t0 + (t1 - t0) * b)


def seg_cmd(s):
    q = seg_at(s, 1)
    if s[0] == 'L':
        return f'L{pt(q)}'
    _, c, rx, ry, t0, t1 = s
    large = 1 if abs(t1 - t0) > 180 else 0
    sweep = 1 if t1 > t0 else 0
    return f'A{f(rx)} {f(ry)} 0 {large} {sweep} {pt(q)}'


def d_of(segs, close=False):
    return f'M{pt(seg_at(segs[0], 0))} ' + ' '.join(seg_cmd(s) for s in segs) + (' Z' if close else '')


def Pd(segs, close=False):
    return P(d_of(segs, close))


def ell(c, rx, ry, t0, t1):
    return ('E', c, rx, ry, t0, t1)


def lines(points):
    return [('L', points[i], points[i + 1]) for i in range(len(points) - 1)]


def outside_intervals(s, inside, n=400):
    vals = [not inside(seg_at(s, i / n)) for i in range(n + 1)]
    out, start = [], None

    def refine(lo, hi):  # lo outside-state differs from hi
        a = not inside(seg_at(s, lo))
        for _ in range(40):
            m = (lo + hi) / 2
            if (not inside(seg_at(s, m))) == a:
                lo = m
            else:
                hi = m
        return (lo + hi) / 2

    for i, v in enumerate(vals):
        u = i / n
        if v and start is None:
            start = 0.0 if i == 0 else refine((i - 1) / n, u)
        if not v and start is not None:
            out.append((start, refine((i - 1) / n, u)))
            start = None
    if start is not None:
        out.append((start, 1.0))
    return out


def cut(segs, inside, closed=False):
    """Pieces (lists of segments) of a path that lie outside the region inside(p)."""
    pieces, cur = [], None
    for s in segs:
        for a, b in outside_intervals(s, inside):
            part = sub(s, a, b)
            if a < 1e-9 and cur is not None:
                cur[0].append(part)
            else:
                cur = [[part], None]
                pieces.append(cur)
            cur[1] = b
        if not outside_intervals(s, inside) or outside_intervals(s, inside)[-1][1] < 1 - 1e-9:
            cur = None
    res = [p[0] for p in pieces]
    if closed and len(res) > 1 and dist(seg_at(res[-1][-1], 1), seg_at(res[0][0], 0)) < 1e-6:
        res[0] = res.pop() + res[0]
    res = [p for p in res if sum(dist(seg_at(x, 0), seg_at(x, 1)) for x in p) > 2]
    return res


def in_circle(c, r):
    return lambda p: dist(p, c) < r


def in_band(a, b, g):
    """Inside a band of half-width g around the infinite line a-b."""
    d = dist(a, b)
    ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
    return lambda p: abs((p[0] - a[0]) * uy - (p[1] - a[1]) * ux) < g


def sample(segs, n=60):
    pts = []
    for s in segs:
        pts += [seg_at(s, i / n) for i in range(n)]
    return pts


def in_poly(p, poly):
    x, y = p
    c = False
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def area_cut(segs, c, r):
    """Closed shape minus a disc, as a path string."""
    pieces = cut(segs, in_circle(c, r), closed=True)
    poly = sample(segs)
    d = ''
    for i, pc in enumerate(pieces):
        d += d_of(pc) if i == 0 else ' ' + ' '.join(seg_cmd(s) for s in pc)
        nxt = pieces[(i + 1) % len(pieces)]
        d += ' ' + arc_to(c, r, seg_at(pc[-1], 1), seg_at(nxt[0], 0), lambda m: 1 if in_poly(m, poly) else 0)
        if i < len(pieces) - 1:
            d += f' L{pt(seg_at(nxt[0], 0))}'
    return P(d + ' Z')


def cut_paths(paths, c, r, closed_flags=None):
    out = []
    for i, segs in enumerate(paths):
        cl = closed_flags[i] if closed_flags else False
        out += [Pd(pc) for pc in cut(segs, in_circle(c, r), cl)]
    return out


def close_segs(segs):
    a, b = seg_at(segs[-1], 1), seg_at(segs[0], 0)
    return segs + ([('L', a, b)] if dist(a, b) > 1e-6 else [])


def plus_mark(c=B, a=26):
    return [L(c[0] - a, c[1], c[0] + a, c[1]), L(c[0], c[1] - a, c[0], c[1] + a)]


def badge_icon(name, tags, line_closed, line_open, detail_open, area_closed, mark_line, mark_area=(), R=62):
    """line_closed: list of closed segment paths (silhouettes), line_open/detail_open: open segment paths."""
    ln = []
    for segs in line_closed:
        ln += [Pd(pc) for pc in cut(close_segs(segs), in_circle(B, R), True)]
    for segs in line_open:
        ln += [Pd(pc) for pc in cut(segs, in_circle(B, R))]
    dt = []
    for segs in detail_open:
        dt += [Pd(pc) for pc in cut(segs, in_circle(B, R))]
    ar = [area_cut(close_segs(s), B, R) for s in area_closed]
    icon(name, DS, tags, line=ln + list(mark_line), detail=dt, area=ar + list(mark_area))


def sparkle_mark(c=B, s=0.34):
    pts = 'M128 32 C136 96 160 120 224 128 C160 136 136 160 128 224 C120 160 96 136 32 128 C96 120 120 96 128 32 Z'
    import re
    nums = [float(v) for v in re.findall(r'-?\d+\.?\d*', pts)]
    tok = re.findall(r'[MCZ]|-?\d+\.?\d*', pts)
    out, i, xy = [], 0, []
    for t in tok:
        if t in 'MCZ':
            out.append(t)
        else:
            xy.append(float(t))
            if len(xy) == 2:
                out.append(pt((c[0] + (xy[0] - 128) * s, c[1] + (xy[1] - 128) * s)))
                xy = []
    return P(' '.join(out).replace('M ', 'M').replace('C ', 'C'))


# ---------------------------------------------------------------- compass tool
hc, hr = (128, 64), 20
feet = [(56, 216), (200, 216)]
legs, ang = [], []
for fx, fy in feet:
    dx, dy = fx - hc[0], fy - hc[1]
    n = math.hypot(dx, dy)
    ux, uy = dx / n, dy / n
    legs.append(L(hc[0] + ux * hr, hc[1] + uy * hr, fx, fy))
    ang.append(math.degrees(math.atan2(dy, dx)))
ra = 100
cross = P(f'M{pt(polar(hc, ra, ang[0]))} A{ra} {ra} 0 0 0 {pt(polar(hc, ra, ang[1]))}')
icon('compass-tool', DS, ['drafting compass', 'geometry', 'draw circle', 'compasses', 'architecture'],
     line=[C(*hc, hr), L(128, 32, 128, 44)] + legs + [cross])

# ---------------------------------------------------------------- cone
cone_sil = [('L', (48, 192), (128, 32)), ('L', (128, 32), (208, 192)), ell((128, 192), 80, 28, 0, 180)]
cone_back = [ell((128, 192), 80, 28, 180, 360)]
icon('cone', DS, ['cone', '3d', 'geometry', 'shape'],
     line=[Pd(cone_sil, True)], detail=[Pd(cone_back)], area=[Pd(cone_sil, True)])
badge_icon('cone-plus', ['cone', 'add', 'new', 'shape', '3d'], [cone_sil], [], [cone_back], [cone_sil], plus_mark())
icon('cone-slash', DS, ['cone', 'disabled', 'off', 'shape', '3d'],
     line=[Pd(cone_sil, True), Pd(cone_back), SLASH])

# ---------------------------------------------------------------- contrast
icon('contrast', DS, ['contrast', 'brightness', 'adjust', 'tone', 'half circle'],
     line=[C(128, 128, 96), L(128, 32, 128, 224)], area=[P('M128 32 A96 96 0 0 1 128 224 Z')])
icon('contrast-slash', DS, ['contrast', 'disabled', 'off', 'design'],
     line=[C(128, 128, 96), L(128, 32, 128, 92), L(128, 164, 128, 224), SLASH])

# ---------------------------------------------------------------- corners
corner_tl = 'M48 216 V128 A80 80 0 0 1 128 48 H216'
def corner_path(deg):
    # rotate the top-left corner path about the centre
    pts = [(48, 216), (48, 128), (128, 48), (216, 48)]
    a, b, c2, d = rot(pts, deg)
    sweep = 1
    return P(f'M{pt(a)} L{pt(b)} A80 80 0 0 {sweep} {pt(c2)} L{pt(d)}')

for nm, deg in (('top-left', 0), ('top-right', 90), ('bottom-right', 180), ('bottom-left', 270)):
    icon(f'corner-{nm}', DS, ['rounded corner', 'corner radius', 'border'], line=[corner_path(deg)])

icon('corner-round', DS, ['rounded corner', 'radius', 'border radius', 'corner', 'corner radius'],
     line=[P('M48 216 V144 A96 96 0 0 1 144 48 H216')], dot=[C(48, 48, 16)])


def rrect_one(corner, R=96, r=16):
    x0, y0, x1, y1 = 32, 32, 224, 224
    rad = {k: (R if k == corner else r) for k in ('tl', 'tr', 'br', 'bl')}
    return (f'M{x0 + rad["tl"]} {y0} H{x1 - rad["tr"]} A{rad["tr"]} {rad["tr"]} 0 0 1 {x1} {y0 + rad["tr"]} '
            f'V{y1 - rad["br"]} A{rad["br"]} {rad["br"]} 0 0 1 {x1 - rad["br"]} {y1} '
            f'H{x0 + rad["bl"]} A{rad["bl"]} {rad["bl"]} 0 0 1 {x0} {y1 - rad["bl"]} '
            f'V{y0 + rad["tl"]} A{rad["tl"]} {rad["tl"]} 0 0 1 {x0 + rad["tl"]} {y0} Z')

for nm, k in (('top-left', 'tl'), ('top-right', 'tr'), ('bottom-right', 'br'), ('bottom-left', 'bl')):
    d = rrect_one(k)
    words = nm.replace('-', ' ')
    icon(f'corner-radius-{nm}', DS, ['border radius', 'rounded corner', words, 'css'], line=[P(d)], area=[P(d)])

# ---------------------------------------------------------------- crops
def crop_frame(w, h, ov=24):
    x0, x1, y0, y1 = 128 - w / 2, 128 + w / 2, 128 - h / 2, 128 + h / 2
    return [PL([(x0, y0 - ov), (x0, y1), (x1 + ov, y1)]), PL([(x0 - ov, y0), (x1, y0), (x1, y1 + ov)])]

W = 144
for nm, tags, (w, h) in [
    ('crop-16-9', ['crop 16 9', 'crop', 'aspect ratio', 'trim', '16'], (W, W * 9 / 16)),
    ('crop-3-2', ['crop 3 2', 'crop', 'aspect ratio', 'trim', 'design'], (W, W * 2 / 3)),
    ('crop-5-4', ['crop 5 4', 'crop', 'aspect ratio', 'trim', '5'], (W, W * 4 / 5)),
    ('crop-7-5', ['crop 7 5', 'crop', 'aspect ratio', 'trim', '7'], (W, W * 5 / 7)),
    ('crop-landscape', ['crop landscape', 'crop', 'aspect ratio', 'trim', 'landscape'], (W, W * 3 / 4)),
    ('crop-portrait', ['crop portrait', 'crop', 'aspect ratio', 'trim', 'portrait'], (W * 3 / 4, W)),
    ('crop-square', ['crop square', 'crop', 'aspect ratio', 'trim', 'square'], (W, W)),
]:
    icon(nm, DS, tags, line=crop_frame(w, h))

# crop-rotate: smaller crop marks lower-left, rotation arrow over the top-right
cr = [PL([(60, 68), (60, 184), (176, 184)]), PL([(32, 96), (148, 96), (148, 212)])]
rc, rr = (116, 128), 88
a0, a1 = -90, -5
st, en = polar(rc, rr, a0), polar(rc, rr, a1)
back = a1 + 90 + 180
icon('crop-rotate', DS, ['crop', 'rotate', 'image edit', 'straighten', 'rotate crop'],
     line=cr + [P(f'M{pt(st)} A{rr} {rr} 0 0 1 {pt(en)}'),
                PL([polar(en, 28, back - 45), en, polar(en, 28, back + 45)])])

# ---------------------------------------------------------------- cubes
HEX = [(128, 32), (216, 80), (216, 176), (128, 224), (40, 176), (40, 80)]


def cube_parts(s=1.0, c=(128, 128)):
    T = lambda p: (c[0] + (p[0] - 128) * s, c[1] + (p[1] - 128) * s)
    hx = [T(p) for p in HEX]
    mid = T((128, 128))
    sil = lines(hx + [hx[0]])
    det = [lines([hx[5], mid, hx[1]]), lines([mid, hx[3]])]
    return hx, sil, det


hx, sil, det = cube_parts(0.6)
icon('cube-3d-sphere', DS, ['3d', 'sphere', 'cube', 'model'],
     line=[C(128, 128, 96)], detail=[Pd(sil, True)] + [Pd(d) for d in det], area=[C(128, 128, 96)])
icon('cube-3d-sphere-slash', DS, ['cube 3d sphere', 'disabled', 'off', '3d', 'sphere'],
     line=[C(128, 128, 96), Pd(sil, True)] + [Pd(d) for d in det] + [SLASH])

hx, sil, det = cube_parts(0.5)
icon('cube-focus', DS, ['3d scan', 'ar', 'object focus'],
     line=[P('M32 88 V48 A16 16 0 0 1 48 32 H88'), P('M224 88 V48 A16 16 0 0 0 208 32 H168'),
           P('M224 168 V208 A16 16 0 0 1 208 224 H168'), P('M32 168 V208 A16 16 0 0 0 48 224 H88'),
           Pd(sil, True)],
     detail=[Pd(d) for d in det], area=[Pd(sil, True)])

hx, sil, det = cube_parts(1.0)
badge_icon('cube-plus', ['cube', 'add', 'new', '3d', 'box'], [sil], [], det, [sil], plus_mark())
badge_icon('cube-sparkle', ['cube', 'ai', 'magic', '3d', 'box'], [sil], [], det, [sil],
           [sparkle_mark()], [sparkle_mark()], R=66)
icon('cube-slash', DS, ['cube', 'disabled', 'off', '3d', 'box'],
     line=[Pd(sil, True)] + [Pd(d) for d in det] + [SLASH])

hx, sil, det = cube_parts(0.5)
oc, orr = (128, 128), 88
o0, o1 = 212, 520 - 0  # clockwise from left-upper round to left-lower
o1 = 160 + 360
ost, oen = polar(oc, orr, o0), polar(oc, orr, o1)
otd = math.radians(o1 + 90)
oback = math.degrees(otd) + 180
icon('cube-rotate', DS, ['3d rotation', 'rotate', 'cube', 'orbit'],
     line=[P(f'M{pt(ost)} A{orr} {orr} 0 1 1 {pt(oen)}'),
           PL([polar(oen, 30, oback - 45), oen, polar(oen, 30, oback + 45)]),
           Pd(sil, True)],
     detail=[Pd(d) for d in det], area=[Pd(sil, True)])


# cube-transparent: oblique cube, hidden edges dashed
def dashes(p, q, dash=12, gap=28):
    n = dist(p, q)
    k = max(1, round((n + gap) / (dash + gap)))
    step = (n - dash) / (k - 1) if k > 1 else 0
    ux, uy = (q[0] - p[0]) / n, (q[1] - p[1]) / n
    out = []
    for i in range(k):
        a = i * step
        out.append(L(p[0] + ux * a, p[1] + uy * a, p[0] + ux * (a + dash), p[1] + uy * (a + dash)))
    return out

o = 52
FX0, FY0, FX1, FY1 = 40, 92, 164, 216
sil_t = [(FX0, FY0), (FX0 + o, FY0 - o), (FX1 + o, FY0 - o), (FX1 + o, FY1 - o), (FX1, FY1), (FX0, FY1)]
bl_back = (FX0 + o, FY1 - o)
def dash_run(p, q, starts, ln=20):
    n = dist(p, q); ux, uy = (q[0] - p[0]) / n, (q[1] - p[1]) / n
    return [L(p[0] + ux * a, p[1] + uy * a, p[0] + ux * min(a + ln, n), p[1] + uy * min(a + ln, n)) for a in starts]
hidden = (dash_run(bl_back, (bl_back[0], FY0 - o), [0, 44]) + dash_run(bl_back, (FX1 + o, bl_back[1]), [44])
          + dash_run(bl_back, (FX0, FY1), [0])[:0])
hidden = [P(f'M{pt((bl_back[0], bl_back[1] - 20))} L{pt(bl_back)} L{pt((bl_back[0] + 20, bl_back[1]))}')] + \
         dash_run(bl_back, (bl_back[0], FY0 - o), [48]) + dash_run(bl_back, (FX1 + o, bl_back[1]), [48])
icon('cube-transparent', DS, ['3d wireframe', 'transparent cube', 'model'],
     line=[PG(sil_t)],
     detail=[PL([(FX0, FY0), (FX1, FY0), (FX1, FY1)]), L(FX1, FY0, FX1 + o, FY0 - o)]
     + [L(bl_back[0], bl_back[1], bl_back[0], bl_back[1] - 16), L(bl_back[0], bl_back[1] - 52, bl_back[0], bl_back[1] - 76),
        L(bl_back[0] + 36, bl_back[1], bl_back[0] + 60, bl_back[1]), L(bl_back[0] + 96, bl_back[1], bl_back[0] + 96, bl_back[1])][0:0]
     + hidden,
     area=[PG(sil_t)])

# ---------------------------------------------------------------- cube net
s = 48
net = [(104, 32), (152, 32), (152, 80), (200, 80), (200, 128), (152, 128), (152, 224), (104, 224),
       (104, 128), (56, 128), (56, 80), (104, 80)]
icon('cube-unfolded', DS, ['net', 'unfolded', 'cube', 'geometry'],
     line=[PG(net)],
     detail=[L(104, 80, 152, 80), L(104, 128, 152, 128), L(104, 176, 152, 176), L(104, 80, 104, 128),
             L(152, 80, 152, 128)],
     area=[PG(net)])

# ---------------------------------------------------------------- curves
icon('curve', DS, ['line curve', 'bezier', 'path', 'spline'],
     line=[P('M56 180 C56 108 200 148 200 76'), C(56, 200, 20), C(200, 56, 20)],
     area=[C(56, 200, 20), C(200, 56, 20)])
icon('curves', DS, ['curves', 'adjust', 'tone', 'photo edit'],
     line=[R(32, 32, 192, 192, 16)],
     detail=[L(96, 32, 96, 224)][0:0] + [P('M64 192 C128 192 128 64 192 64')],
     area=[R(32, 32, 192, 192, 16)])

# ---------------------------------------------------------------- cylinder
cyl_sil = [ell((128, 64), 80, 28, 180, 360), ('L', (208, 64), (208, 192)), ell((128, 192), 80, 28, 0, 180),
           ('L', (48, 192), (48, 64))]
cyl_front = [ell((128, 64), 80, 28, 180, 0)]
icon('cylinder', DS, ['cylinder', '3d', 'shape', 'geometry'],
     line=[Pd(cyl_sil, True)], detail=[Pd(cyl_front)], area=[Pd(cyl_sil, True)])
badge_icon('cylinder-plus', ['cylinder', 'add', 'new', 'shape', '3d'], [cyl_sil], [], [cyl_front], [cyl_sil],
           plus_mark())
icon('cylinder-slash', DS, ['cylinder', 'disabled', 'off', 'shape', '3d'],
     line=[Pd(cyl_sil, True), Pd(cyl_front), SLASH])

# ---------------------------------------------------------------- diabolo
dia_sil = [ell((128, 60), 80, 24, 180, 360), ('L', (208, 60), (148, 128)), ('L', (148, 128), (208, 196)),
           ell((128, 196), 80, 24, 0, 180), ('L', (48, 196), (108, 128)), ('L', (108, 128), (48, 60))]
dia_det = [[ell((128, 60), 80, 24, 180, 0)], [ell((128, 196), 80, 24, 180, 360)]]
icon('diabolo', DS, ['diabolo', 'shape', 'toy', 'design'],
     line=[Pd(dia_sil, True)], detail=[Pd(d) for d in dia_det], area=[Pd(dia_sil, True)])
badge_icon('diabolo-plus', ['diabolo', 'add', 'new', 'shape', 'toy'], [dia_sil], [], dia_det, [dia_sil],
           plus_mark())
icon('diabolo-slash', DS, ['diabolo', 'disabled', 'off', 'shape', 'toy'],
     line=[Pd(dia_sil, True)] + [Pd(d) for d in dia_det] + [SLASH])


# ---------------------------------------------------------------- diamonds four
def diamonds(off, h):
    out = []
    for cx, cy in ((128, 128 - off), (128 + off, 128), (128, 128 + off), (128 - off, 128)):
        out.append(PG([(cx, cy - h), (cx + h, cy), (cx, cy + h), (cx - h, cy)]))
    return out

dm = diamonds(66, 30)
icon('diamonds-four', DS, ['component', 'symbol', 'design system', 'reusable', 'components'], line=dm, area=dm)
icon('diamonds-four-slash', DS, ['components', 'disabled', 'off', 'design'], line=diamonds(66, 26) + [SLASH])

# ---------------------------------------------------------------- dimensions
icon('dimensions', DS, ['dimensions', 'measure', 'size', 'width'],
     line=[R(96, 96, 128, 128, 14),
           L(104, 48, 216, 48), PL([(120, 32), (104, 48), (120, 64)]), PL([(200, 32), (216, 48), (200, 64)]),
           L(48, 104, 48, 216), PL([(32, 120), (48, 104), (64, 120)]), PL([(32, 200), (48, 216), (64, 200)])],
     area=[R(96, 96, 128, 128, 14)])


# ---------------------------------------------------------------- distribute
def bar(x0, y0, x1, y1, rx=10):
    return R(x0, y0, x1 - x0, y1 - y0, rx)


def T90(p):  # rotate 90 deg clockwise about the centre: left->top, right->bottom
    return (256 - p[1], p[0])


def rect_t(x0, y0, x1, y1, tf):
    a, b = tf((x0, y0)), tf((x1, y1))
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))


BW = 36
BARS = [(32, 84, 172), (110, 60, 196), (188, 100, 156)]  # x0, y0, y1  (x1 = x0 + BW)


def dist_icon(name, tags, mode, vertical):
    tf = T90 if vertical else (lambda p: p)
    ln, ar = [], []
    for x0, y0, y1 in BARS:
        r = rect_t(x0, y0, x0 + BW, y1, tf)
        ln.append(bar(*r)); ar.append(bar(*r))
        if mode == 'center':
            cx = x0 + BW / 2
            for a, b in (((cx, 32), (cx, y0)), ((cx, y1), (cx, 224))):
                if b[1] - a[1] > 4:
                    pa, pb = tf(a), tf(b)
                    ln.append(L(*pa, *pb))
        elif mode in ('left', 'right'):
            ex = x0 if mode == 'left' else x0 + BW
            pa, pb = tf((ex, 32)), tf((ex, 224))
            ln.append(L(*pa, *pb))
    icon(name, DS, tags, line=ln, area=ar)


dist_icon('distribute-horizontal', ['distribute', 'spacing', 'horizontal', 'center', 'space between'], 'center', False)
dist_icon('distribute-horizontal-left', ['distribute', 'spacing', 'horizontal', 'left'], 'left', False)
dist_icon('distribute-horizontal-right', ['distribute', 'spacing', 'horizontal', 'right'], 'right', False)
dist_icon('distribute-vertical', ['distribute', 'spacing', 'vertical', 'center', 'space between'], 'center', True)
dist_icon('distribute-vertical-top', ['distribute', 'spacing', 'vertical', 'top'], 'left', True)
dist_icon('distribute-vertical-bottom', ['distribute', 'spacing', 'vertical', 'bottom'], 'right', True)

walls = [L(32, 40, 32, 216), L(224, 40, 224, 216)]
sa = [bar(70, 76, 110, 180), bar(146, 76, 186, 180)]
icon('distribute-space-around', DS, ['space around', 'space evenly', 'flex', 'layout'], line=walls + sa, area=sa)
sb = [bar(32, 76, 88, 180), bar(168, 76, 224, 180)]
icon('distribute-space-between', DS, ['space between', 'justify', 'flex', 'layout'], line=walls + sb, area=sb)

print(save(overwrite=True))
