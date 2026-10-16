import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

MD = 'Media'

# ================================================================ small outline engine
# Segments: ('L', p0, p1) | ('C', p0, c1, c2, p1) | ('A', centre, r, a0, a1)  (angles in radians, a1 may be < a0)


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
    c, r, a0, a1 = s[1:]
    return ('A', c, r, a0 + (a1 - a0) * t0, a0 + (a1 - a0) * t1)


def seg_end(s):
    return seg_point(s, 1)


def seg_cmd(s):
    if s[0] == 'L':
        return f'L{pt(s[2])}'
    if s[0] == 'C':
        return f'C{pt(s[2])} {pt(s[3])} {pt(s[4])}'
    c, r, a0, a1 = s[1:]
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


def ang(c, p):
    return math.atan2(p[1] - c[1], p[0] - c[0])



H = math.pi / 2
TAU = 2 * math.pi


def seg_rect(x, y, w, h, r):
    x2, y2 = x + w, y + h
    return [('L', (x, y2 - r), (x, y + r)), ('A', (x + r, y + r), r, 2 * H, 3 * H), ('L', (x + r, y), (x2 - r, y)),
            ('A', (x2 - r, y + r), r, 3 * H, 4 * H), ('L', (x2, y + r), (x2, y2 - r)), ('A', (x2 - r, y2 - r), r, 0, H),
            ('L', (x2 - r, y2), (x + r, y2)), ('A', (x + r, y2 - r), r, H, 2 * H)]


def seg_circle(c, r, a0=0):
    return [('A', c, r, a0, a0 + TAU)]


def seg_poly(pts, close=False):
    out = [('L', pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    if close:
        out.append(('L', pts[-1], pts[0]))
    return out


def scale_d(d, s, c_from, c_to):
    """Scale an absolute M/L/H/V/C/A/Z path about c_from and move it to c_to."""
    toks = re.findall(r'[MLHVCAZ]|-?\d+\.?\d*', d)
    out, i, cmd = [], 0, None
    X = lambda v: f(c_to[0] + (v - c_from[0]) * s)
    Y = lambda v: f(c_to[1] + (v - c_from[1]) * s)
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            out.append(t)
            i += 1
            continue
        if cmd in 'MLC':
            out.append(f'{X(float(t))} {Y(float(toks[i + 1]))}'); i += 2
        elif cmd == 'H':
            out.append(X(float(t))); i += 1
        elif cmd == 'V':
            out.append(Y(float(t))); i += 1
        elif cmd == 'A':
            rx, ry, rotn, la, sw, x, y = toks[i:i + 7]
            out.append(f'{f(float(rx) * s)} {f(float(ry) * s)} {rotn} {la} {sw} {X(float(x))} {Y(float(y))}'); i += 7
    return re.sub(r'([MLHVCAZ]) ', r'\1', ' '.join(out))


# ================================================================ slash helpers
SLASH = L(48, 48, 208, 208)
SG = 30


def seg_dist(p, a=(48, 48), b=(208, 208)):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + dx * t, a[1] + dy * t))


def gapped(outline, closed=True):
    runs, whole = trim(outline, lambda p: seg_dist(p) >= SG, closed)
    if whole:
        return [P(segs_d(outline, closed))]
    return [P(segs_d(r)) for r in runs if r]


def slashed(*shapes):
    """shapes: (segs, closed). Returns line list with the shapes opened around the slash, plus the slash."""
    out = []
    for segs, closed in shapes:
        out += gapped(segs, closed)
    return out + [SLASH]


# ================================================================ badge marks around B (shared vocabulary of the library)
B = (184, 184)
BX, BY = B


def T(pts, dx=BX, dy=BY):
    return [(x + dx, y + dy) for x, y in pts]


def heart_path(c, s):
    def q(x, y):
        return pt((c[0] + (x - 128) * s, c[1] + (y - 140) * s))
    r = f(50 * s)
    return (f'M{q(128, 212)} C{q(128, 212)} {q(32, 160)} {q(32, 98)} A{r} {r} 0 0 1 {q(128, 78)} '
            f'A{r} {r} 0 0 1 {q(224, 98)} C{q(224, 160)} {q(128, 212)} {q(128, 212)} Z')


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


SPARK = 'M128 32 C136 96 160 120 224 128 C160 136 136 160 128 224 C120 160 96 136 32 128 C96 120 120 96 128 32 Z'
MOON = 'M113.51 48.24 A88 88 0 1 0 207.04 148.97 A72 72 0 0 1 113.51 48.24 Z'


def badge(kind):
    """Small mark around B. Returns (roles, clearance radius)."""
    b = dict(line=[], area=[], hole=[], dot=[], detail=[])
    cr = 56
    if kind == 'check':
        b['line'] = [PL(T([(-26, 2), (-8, 20), (26, -16)]))]
    elif kind == 'x':
        b['line'] = [L(BX - 20, BY - 20, BX + 20, BY + 20), L(BX + 20, BY - 20, BX - 20, BY + 20)]
        cr = 54
    elif kind == 'plus':
        b['line'] = [L(BX, BY - 26, BX, BY + 26), L(BX - 26, BY, BX + 26, BY)]
    elif kind == 'minus':
        b['line'] = [L(BX - 26, BY, BX + 26, BY)]
        cr = 50
    elif kind == 'arrow-down':
        b['line'] = [L(BX, BY - 28, BX, BY + 28), PL(T([(-20, 8), (0, 28), (20, 8)]))]
    elif kind == 'arrow-up':
        b['line'] = [L(BX, BY + 28, BX, BY - 28), PL(T([(-20, -8), (0, -28), (20, -8)]))]
    elif kind == 'code':
        b['line'] = [PL(T([(-14, -20), (-34, 0), (-14, 20)])), PL(T([(14, -20), (34, 0), (14, 20)]))]
        cr = 60
    elif kind == 'dollar':
        b['line'] = [P(f'M{BX + 16} {BY - 24} H{BX - 4} A12 12 0 0 0 {BX - 4} {BY} '
                       f'H{BX + 4} A12 12 0 0 1 {BX + 4} {BY + 24} H{BX - 16}'),
                     L(BX, BY - 38, BX, BY - 24), L(BX, BY + 24, BX, BY + 38)]
        cr = 60
    elif kind == 'bitcoin':
        x0 = BX - 14
        b['line'] = [P(f'M{x0 - 8} {BY - 26} H{BX + 2} A13 13 0 0 1 {BX + 2} {BY} H{x0}'),
                     P(f'M{x0} {BY} H{BX + 5} A13 13 0 0 1 {BX + 5} {BY + 26} H{x0 - 8}'),
                     L(x0, BY - 26, x0, BY + 26),
                     L(BX - 4, BY - 38, BX - 4, BY - 26), L(BX - 4, BY + 26, BX - 4, BY + 38)]
        cr = 60
    elif kind == 'gear':
        g = gear_path(B, 20, 31, 6, -90)
        b['line'] = [P(g)]
        b['area'] = [P(g)]
        b['hole'] = [C(BX, BY, 7)]
        cr = 60
    elif kind == 'heart':
        h = heart_path((BX, BY + 2), 0.34)
        b['line'] = [P(h)]
        b['area'] = [P(h)]
        cr = 58
    elif kind == 'lightning':
        bolt = T([(6, -34), (-22, 6), (0, 6), (-6, 34), (22, -6), (0, -6)])
        b['line'] = [PG(bolt)]
        b['area'] = [PG(bolt)]
        cr = 58
    elif kind == 'magnifying-glass':
        b['line'] = [C(BX - 6, BY - 6, 18), L(BX + 8, BY + 8, BX + 26, BY + 26)]
        b['area'] = [C(BX - 6, BY - 6, 18)]
    elif kind == 'moon':
        m = scale_d(MOON, 0.38, (122, 140), B)
        b['line'] = [P(m)]
        b['area'] = [P(m)]
        cr = 58
    elif kind == 'pause':
        b['line'] = [L(BX - 16, BY - 24, BX - 16, BY + 24), L(BX + 16, BY - 24, BX + 16, BY + 24)]
        cr = 54
    elif kind == 'push-pin':
        pp = load('push-pin')

        def pin_pts(d):
            return [(float(a), float(b_)) for a, b_ in re.findall(r'([-\d.]+) ([-\d.]+)', d)]
        body = pin_pts(re.search(r'd="([^"]+)"', pp['line'][0]).group(1))
        needle = pin_pts(re.search(r'd="([^"]+)"', pp['line'][1]).group(1))
        s_, cx0, cy0 = 0.34, 133, 124
        tf = lambda q: [(BX + (x - cx0) * s_, BY + (y - cy0) * s_) for x, y in q]
        b['line'] = [PG(tf(body)), PL(tf(needle))]
        b['area'] = [PG(tf(body))]
        cr = 58
    elif kind == 'question':
        b['line'] = [P(f'M{BX - 18} {BY - 20} A18 18 0 1 1 {BX + 6} {BY - 3} C{BX + 1} {BY} {BX} {BY + 3} {BX} {BY + 8}')]
        b['dot'] = [C(BX, BY + 32, 14)]
        cr = 58
    elif kind == 'share':
        b['line'] = [P(f'M{BX - 28} {BY + 28} V{BY + 16} A24 24 0 0 1 {BX - 4} {BY - 8} H{BX + 28}'),
                     PL(T([(8, -28), (28, -8), (8, 12)]))]
        cr = 60
    elif kind == 'sparkle':
        d = scale_d(SPARK, 0.36, (128, 128), B)
        b['line'] = [P(d)]
        b['area'] = [P(d)]
        cr = 58
    elif kind == 'star':
        st = [polar((BX, BY + 3), 34 if i % 2 == 0 else 15, -90 + i * 36) for i in range(10)]
        b['line'] = [PG(st)]
        b['area'] = [PG(st)]
        cr = 60
    elif kind == 'user':
        b['dot'] = [C(BX, BY - 18, 18)]
        b['line'] = [P(f'M{BX - 28} {BY + 34} A28 28 0 0 1 {BX + 28} {BY + 34}')]
        cr = 60
    elif kind == 'warning':
        b['line'] = [L(BX, BY - 32, BX, BY)]
        b['dot'] = [C(BX, BY + 32, 16)]
        cr = 58
    elif kind == 'record':
        b['dot'] = [C(BX, BY, 32)]
        cr = 56
    else:
        raise ValueError(kind)
    return b, cr


def merge(*ds):
    out = dict(line=[], area=[], hole=[], dot=[], detail=[], dotcut=[])
    for d in ds:
        for k, v in d.items():
            out[k] = out.get(k, []) + list(v)
    return out


# ================================================================ camera (exact geometry of icons/camera.svg)
CAM = [('A', (48, 88), 16, 2 * H, 3 * H), ('L', (48, 72), (80, 72)), ('L', (80, 72), (96, 48)),
       ('L', (96, 48), (160, 48)), ('L', (160, 48), (176, 72)), ('L', (176, 72), (208, 72)),
       ('A', (208, 88), 16, 3 * H, 4 * H), ('L', (224, 88), (224, 192)), ('A', (208, 192), 16, 0, H),
       ('L', (208, 208), (48, 208)), ('A', (48, 192), 16, H, 2 * H), ('L', (32, 192), (32, 88))]
CAM_D = load('camera')['line'][0]
CAM_LENS = load('camera')['detail'][0]
# with a badge in the lower right the lens moves up and left so it keeps clear of the badge notch
LENS_B = C(96, 132, 28)


def camera_badge(kind, lens=True):
    b, cr = badge(kind)
    ln, ar = carve(CAM, B, cr)
    return merge(dict(line=[P(ln)], area=[P(ar)], detail=[LENS_B] if lens else []), b)


CAM_TAGS = {
    'arrow-down': ['camera', 'decrease', 'download', 'photo', 'picture'],
    'arrow-up': ['camera', 'increase', 'upload', 'photo', 'picture'],
    'bitcoin': ['camera', 'crypto', 'bitcoin', 'photo', 'picture'],
    'check': ['camera', 'done', 'approved', 'photo', 'picture'],
    'code': ['camera', 'developer', 'code', 'photo', 'picture'],
    'currency-dollar': ['camera', 'money', 'price', 'photo', 'picture'],
    'gear': ['camera', 'settings', 'configure', 'photo', 'picture'],
    'heart': ['camera', 'favorite', 'like', 'photo', 'picture'],
    'lightning': ['camera', 'fast', 'power', 'photo', 'picture'],
    'magnifying-glass': ['camera', 'search', 'find', 'photo', 'picture'],
    'minus': ['camera', 'remove', 'subtract', 'photo', 'picture'],
    'moon': ['camera', 'night', 'dark', 'photo', 'picture'],
    'pause': ['camera', 'paused', 'hold', 'photo', 'picture'],
    'plus': ['add photo', 'camera', 'new picture', 'capture', 'new'],
    'push-pin': ['camera', 'pinned', 'pin', 'photo', 'picture'],
    'question': ['camera', 'help', 'unknown', 'photo', 'picture'],
    'selfie': ['camera', 'selfie', 'front camera', 'photo', 'picture'],
    'share': ['camera', 'share', 'send', 'photo', 'picture'],
    'sparkle': ['camera', 'ai', 'magic', 'photo', 'picture'],
    'star': ['camera', 'favorite', 'starred', 'photo', 'picture'],
    'warning': ['camera', 'warning', 'error', 'photo', 'picture'],
    'x': ['camera', 'remove', 'cancel', 'photo', 'picture'],
}
KIND = {'currency-dollar': 'dollar', 'selfie': 'user'}
for suffix, tags in CAM_TAGS.items():
    icon(f'camera-{suffix}', MD, tags, **camera_badge(KIND.get(suffix, suffix)))

icon('camera-slash', MD, ['no photography', 'camera off', 'no photos', 'disabled', 'no camera'],
     line=slashed((CAM, True), (seg_circle((128, 140), 36, -H), True)))

# camera-3d: a cube takes the lens' place
cube_c, cube_r = (128, 140), 40
hexa = regular_polygon(cube_c, cube_r, 6)
icon('camera-3d', MD, ['3d camera', 'depth', 'scanner'],
     line=[CAM_D], area=[CAM_D],
     detail=[PG(hexa), PL([hexa[5], cube_c, hexa[1]]), L(cube_c[0], cube_c[1], *hexa[3])])

# camera-rotate: two arrows chase each other around the lens position
rc_, rr_ = (128, 140), 36


def arc_arrow(c, r, a0, a1, head=20):
    """Clockwise arc from a0 to a1 (degrees) with an arrowhead at a1."""
    p0, p1 = polar(c, r, a0), polar(c, r, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    tang = a1 + 90  # travel direction at the end
    return [P(f'M{pt(p0)} A{f(r)} {f(r)} 0 {large} 1 {pt(p1)}'),
            PL([polar(p1, head, tang + 180 - 45), p1, polar(p1, head, tang + 180 + 45)])]


icon('camera-rotate', MD, ['switch camera', 'flip', 'selfie', 'rotate', 'flip camera'],
     line=[CAM_D], area=[CAM_D],
     detail=arc_arrow(rc_, rr_, 190, 320) + arc_arrow(rc_, rr_, 10, 140))

# camera-lens: a lens seen from the front, two rims and aperture blades
def blades(c, ri, ro, n=6, phase=-90):
    """Pinwheel of aperture blades: each edge of the inner polygon runs on until it meets the rim of radius ro."""
    vs = regular_polygon(c, ri, n, phase)
    out = []
    for k in range(n):
        a, b_ = vs[k], vs[(k + 1) % n]
        dx, dy = b_[0] - a[0], b_[1] - a[1]
        ln = math.hypot(dx, dy); dx, dy = dx / ln, dy / ln
        fx, fy = a[0] - c[0], a[1] - c[1]
        bb = fx * dx + fy * dy
        t = -bb + math.sqrt(bb * bb - (fx * fx + fy * fy - ro * ro))
        out.append(L(a[0], a[1], a[0] + dx * t, a[1] + dy * t))
    return out


icon('camera-lens', MD, ['aperture', 'optics', 'lens'],
     line=[C(128, 128, 96)], area=[C(128, 128, 96)],
     detail=[C(128, 128, 62)] + blades((128, 128), 28, 62, 5))

# camera-mirrorless: flat body, viewfinder hump on the left, big lens
MIR_BODY = R(32, 64, 192, 144, 16)
MIR_HUMP = 'M48 64 V56 A8 8 0 0 1 56 48 H96 A8 8 0 0 1 104 56 V64'
icon('camera-mirrorless', MD, ['mirrorless', 'dslr', 'camera', 'lens'],
     line=[MIR_BODY, P(MIR_HUMP)], area=[MIR_BODY, P(MIR_HUMP + ' Z')],
     detail=[C(140, 136, 46)], dotcut=[C(140, 136, 14), C(68, 100, 12)])

# ================================================================ albums
ALB_SLEEVE = (32, 104, 120, 120, 14)
ALB_DC, ALB_DR = (164, 92), 60


def outside_sleeve(p, m=0):
    x, y, w, h, _ = ALB_SLEEVE
    return not (x - m < p[0] < x + w + m and y - m < p[1] < y + h + m)


ALB_ARC = trim(seg_circle(ALB_DC, ALB_DR, H), outside_sleeve)[0][0]
icon('album', MD, ['album', 'record sleeve', 'music', 'collection'],
     line=[R(*ALB_SLEEVE), P(segs_d(ALB_ARC))], area=[R(*ALB_SLEEVE)], dot=[C(*ALB_DC, 14)])
icon('album-slash', MD, ['album', 'disabled', 'off', 'media'],
     line=slashed((seg_rect(*ALB_SLEEVE), True), (ALB_ARC, False)), dot=[C(*ALB_DC, 14)])

# album-list: a photo card on top, list lines under it
icon('album-list', MD, ['gallery list', 'albums', 'photos'],
     line=[R(32, 32, 192, 112, 14), L(32, 180, 224, 180), L(32, 216, 160, 216)], area=[R(32, 32, 192, 112, 14)],
     detail=[PL([(44, 128), (88, 84), (128, 124), (148, 104), (188, 144)]), C(172, 72, 12)])

# album-open: open book whose right page holds a picture
OPEN = 'M128 72 C108 56 76 48 32 52 V196 C76 192 108 200 128 216 C148 200 180 192 224 196 V52 C180 48 148 56 128 72 Z'
icon('album-open', MD, ['open album', 'photo book', 'gallery'],
     line=[P(OPEN)], area=[P(OPEN)],
     detail=[L(128, 72, 128, 216), PL([(128, 180), (164, 140), (192, 168), (224, 140)])], dotcut=[C(186, 96, 14)])

# ================================================================ aperture
icon('aperture', MD, ['aperture', 'shutter', 'camera', 'lens', 'camera lens'],
     line=[C(128, 128, 96)], area=[C(128, 128, 96)], detail=blades((128, 128), 40, 96))


def blade_segs(c, ri, ro, n=6, phase=-90):
    out = []
    for e in blades(c, ri, ro, n, phase):
        x1, y1, x2, y2 = map(float, re.findall(r'-?[\d.]+', e))
        out.append(([('L', (x1, y1), (x2, y2))], False))
    return out


icon('aperture-slash', MD, ['aperture', 'disabled', 'off', 'media'],
     line=slashed((seg_circle((128, 128), 96), True), *blade_segs((128, 128), 40, 96)))

# ================================================================ disc slash (exact geometry of icons/disc.svg)
disc_arc = [('A', (128, 128), 60, ang((128, 128), (71.62, 107.48)), ang((128, 128), (107.48, 71.62)))]
icon('disc-slash', MD, ['disc', 'disabled', 'off', 'media'],
     line=slashed((seg_circle((128, 128), 96), True), (seg_circle((128, 128), 28), True), (disc_arc, False)))

# ================================================================ boombox
BOOM = R(32, 88, 192, 120, 16)
icon('boombox', MD, ['boombox', 'stereo', 'radio', 'music'],
     line=[BOOM, P('M64 88 V64 A16 16 0 0 1 80 48 H176 A16 16 0 0 1 192 64 V88')], area=[BOOM],
     detail=[C(84, 152, 24), C(172, 152, 24)], dotcut=[C(128, 124, 12)])

# ================================================================ cassette
CAS = R(32, 48, 192, 160, 16)
icon('cassette-tape', MD, ['cassette', 'tape', 'audio', 'retro', 'mixtape'],
     line=[CAS], area=[CAS],
     detail=[C(92, 108, 22), C(164, 108, 22), L(92, 130, 164, 130), PL([(64, 208), (80, 168), (176, 168), (192, 208)])])

# ================================================================ clock-record (clock geometry, hands as in clock-lightning)
CLK = [('A', (128, 128), 96, 0, TAU)]
_b, _cr = badge('record')
_ln, _ar = carve(CLK, B, _cr)
icon('clock-record', MD, ['clock', 'record', 'recording', 'time', 'hour'],
     **merge(dict(line=[P(_ln)], area=[P(_ar)], detail=[PL([(128, 76), (128, 128), (88, 128)])]), _b))

# ================================================================ closed captioning
CC_BOX = (32, 48, 192, 160, 14)


def cc_letters(cx0=92, cx1=164, cy=128, r=30, gap=48):
    out = []
    for cx in (cx0, cx1):
        out.append([('A', (cx, cy), r, math.radians(gap), math.radians(360 - gap))])
    return out


CCL = cc_letters()
icon('closed-captioning', MD, ['captions', 'subtitles', 'cc', 'accessibility'],
     line=[R(*CC_BOX)], area=[R(*CC_BOX)], detail=[P(segs_d(s)) for s in CCL])
icon('closed-captioning-slash', MD, ['captions off', 'subtitles', 'cc', 'disabled', 'subtitles off'],
     line=slashed((seg_rect(*CC_BOX), True), *[(s, False) for s in CCL]))

# ================================================================ collage
icon('collage', MD, ['photo collage', 'photo grid', 'layout', 'collage', 'mosaic'],
     line=[R(32, 32, 192, 192, 16)], area=[R(32, 32, 192, 192, 16)],
     detail=[L(112, 32, 112, 224), L(112, 104, 224, 104), L(32, 160, 112, 160)])

# ================================================================ director chair
BACK = R(56, 40, 144, 44, 10)
icon('director-chair', MD, ['film director', 'movie set', 'folding chair', 'film', 'director'],
     line=[BACK, L(72, 84, 72, 152), L(184, 84, 184, 152), L(40, 116, 216, 116), L(48, 152, 208, 152),
           L(72, 152, 184, 224), L(184, 152, 72, 224)],
     area=[BACK])

# ================================================================ equalizer
icon('equalizer', MD, ['rhythm', 'audio levels', 'equalizer', 'music', 'eq'],
     line=[L(48, 184, 48, 128), L(88, 184, 88, 80), L(128, 184, 128, 48), L(168, 184, 168, 104),
           L(208, 184, 208, 144), L(32, 216, 224, 216)])

# ================================================================ exposure
EXP = (32, 32, 192, 192, 16)
EXP_DIAG = ((48 - 8 * math.sqrt(2), 48 - 8 * math.sqrt(2)), (208 + 8 * math.sqrt(2), 208 + 8 * math.sqrt(2)))
EXP_PLUS = [L(168, 64, 168, 112), L(144, 88, 192, 88)]
EXP_MINUS = [L(64, 168, 112, 168)]
icon('exposure', MD, ['exposure', 'photo', 'plus minus', 'camera', 'adjust'],
     line=[R(*EXP)], area=[R(*EXP)], detail=[L(*EXP_DIAG[0], *EXP_DIAG[1])] + EXP_PLUS + EXP_MINUS)


def exposure_badge(kind):
    b, cr = badge(kind)
    ln, ar = carve(seg_rect(*EXP), B, cr)
    d0 = EXP_DIAG[0]
    k = (BX - cr / math.sqrt(2))
    return merge(dict(line=[P(ln)], area=[P(ar)], detail=[L(d0[0], d0[1], k, k)] + EXP_PLUS + EXP_MINUS), b)


icon('exposure-plus', MD, ['exposure', 'add', 'new', 'photo', 'camera'], **exposure_badge('plus'))
icon('exposure-minus', MD, ['exposure', 'remove', 'subtract', 'photo', 'camera'], **exposure_badge('minus'))

# ================================================================ fast forward circle
icon('fast-forward-circle', MD, ['fast forward', 'skip', 'media', 'circle'],
     line=[C(128, 128, 96)], area=[C(128, 128, 96)],
     detail=[PG([(80, 96), (128, 128), (80, 160)]), PG([(128, 96), (176, 128), (128, 160)])])

# ================================================================ film camera: two reels sitting on the body
FC_BODY = R(32, 120, 144, 88, 14)
FC_LENS = [(176, 152), (224, 128), (224, 200), (176, 176)]
icon('film-camera', MD, ['movie camera', 'cinema', 'reels', 'film'],
     line=[FC_BODY, PG(FC_LENS), C(68, 88, 32), C(152, 92, 28)],
     area=[FC_BODY, PG(FC_LENS), C(68, 88, 32), C(152, 92, 28)], dotcut=[C(68, 88, 12), C(152, 92, 10)])

# film projector: reels raised on posts, lens barrel at the front, feet
FP_BODY = R(32, 128, 144, 64, 14)
FP_LENS = PG([(176, 148), (216, 136), (216, 184), (176, 172)])
FP_R1, FP_R2 = (72, 68, 36), (168, 80, 28)
icon('film-projector', MD, ['old cinema', 'movie projector', 'reels'],
     line=[FP_BODY, FP_LENS, C(*FP_R1), C(*FP_R2), L(72, 104, 100, 128), L(168, 108, 144, 128),
           L(64, 192, 64, 216), L(144, 192, 144, 216)],
     area=[FP_BODY, FP_LENS, C(*FP_R1), C(*FP_R2)], dotcut=[C(72, 68, 12), C(168, 80, 10)])

# film reel: reel with four windows and a hub, film running off the bottom
RC, RR = (120, 120), 88
icon('film-reel', MD, ['film', 'cinema', 'reel'],
     line=[C(*RC, RR), L(RC[0], RC[1] + RR, 224, RC[1] + RR)], area=[C(*RC, RR)],
     detail=[C(*polar(RC, 46, 45 + 90 * k), 16) for k in range(4)], dotcut=[C(*RC, 12)])

# film script: punched page with brads and centred dialogue lines
icon('film-script', MD, ['screenplay', 'script', 'movie'],
     line=[R(48, 32, 160, 192, 14)], area=[R(48, 32, 160, 192, 14)],
     detail=[L(120, 88, 176, 88), L(120, 128, 160, 128), L(120, 168, 176, 168)],
     dotcut=[C(84, 72, 14), C(84, 128, 14), C(84, 184, 14)])

# film strip slash (exact geometry of icons/film-strip.svg)
fs_lines = [((72, 48), (72, 208)), ((184, 48), (184, 208)), ((32, 88), (72, 88)), ((32, 128), (72, 128)),
            ((32, 168), (72, 168)), ((184, 88), (224, 88)), ((184, 128), (224, 128)), ((184, 168), (224, 168))]
icon('film-strip-slash', MD, ['no video', 'movie off', 'film off', 'disabled'],
     line=slashed((seg_rect(32, 48, 192, 160, 14), True), *[([('L', a, b_)], False) for a, b_ in fs_lines]))

print(save(overwrite=True))
