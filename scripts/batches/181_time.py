import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

TM = 'Time'
TR = 'Transport'

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




# ================================================================ path parsing / transforms (batch 181)
def _arc_center(p, q, r, large, sweep):
    x1, y1 = p; x2, y2 = q
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    d2 = dx * dx + dy * dy
    r = max(r, math.sqrt(d2))
    k = math.sqrt(max(r ** 4 - r * r * d2, 0) / (r * r * d2))
    if large == sweep:
        k = -k
    cx = k * dy + (x1 + x2) / 2
    cy = -k * dx + (y1 + y2) / 2
    a0 = math.atan2(y1 - cy, x1 - cx); a1 = math.atan2(y2 - cy, x2 - cx)
    span = (a1 - a0) % TAU
    if not sweep:
        span -= TAU
    return (cx, cy), r, a0, a0 + span


def _toks(d):
    return re.findall(r'[MLHVCAZmlhvcaz]|-?\d*\.?\d+(?:e-?\d+)?', d)


def parse(d):
    """Absolute M/L/H/V/C/A/Z path -> (segs, closed)."""
    toks = _toks(d); i = 0; cur = start = None; segs = []; cmd = None; closed = False

    def num():
        nonlocal i
        v = float(toks[i]); i += 1; return v
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]; i += 1
        if cmd == 'M':
            cur = (num(), num()); start = cur; cmd = 'L'
        elif cmd == 'L':
            q = (num(), num()); segs.append(('L', cur, q)); cur = q
        elif cmd == 'H':
            q = (num(), cur[1]); segs.append(('L', cur, q)); cur = q
        elif cmd == 'V':
            q = (cur[0], num()); segs.append(('L', cur, q)); cur = q
        elif cmd == 'C':
            c1 = (num(), num()); c2 = (num(), num()); q = (num(), num())
            segs.append(('C', cur, c1, c2, q)); cur = q
        elif cmd == 'A':
            r = num(); num(); num(); large = int(num()); sweep = int(num()); q = (num(), num())
            c, r, a0, a1 = _arc_center(cur, q, r, large, sweep)
            segs.append(('A', c, r, a0, a1)); cur = q
        elif cmd == 'Z':
            if dist(cur, start) > 1e-6:
                segs.append(('L', cur, start))
            cur = start; closed = True
    return segs, closed


def el_segs(e):
    """SVG element string (path/circle/rect) -> (segs, closed)."""
    a = dict(re.findall(r'(\w+)="([^"]*)"', e))
    if e.startswith('<circle'):
        return seg_circle((float(a['cx']), float(a['cy'])), float(a['r']), -H), True
    if e.startswith('<rect'):
        return seg_rect(float(a['x']), float(a['y']), float(a['width']), float(a['height']), float(a.get('rx', 0))), True
    return parse(a['d'])


def xf(d, s=1.0, deg=0.0, cf=(128, 128), ct=None):
    """Scale by s and rotate by deg (clockwise) about cf, then move cf to ct. Absolute paths only."""
    ct = ct or cf
    ca, sa = math.cos(math.radians(deg)), math.sin(math.radians(deg))

    def T_(x, y):
        dx, dy = (x - cf[0]) * s, (y - cf[1]) * s
        return pt((ct[0] + dx * ca - dy * sa, ct[1] + dx * sa + dy * ca))
    toks = _toks(d); out = []; i = 0; cmd = None; cur = None
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]; i += 1
            if cmd == 'Z':
                out.append('Z'); continue
        v = lambda k: float(toks[i + k])
        if cmd in 'ML':
            cur = (v(0), v(1)); out.append(f'{cmd}{T_(*cur)}'); i += 2
            if cmd == 'M':
                cmd = 'L'
        elif cmd == 'H':
            cur = (v(0), cur[1]); out.append(f'L{T_(*cur)}'); i += 1
        elif cmd == 'V':
            cur = (cur[0], v(0)); out.append(f'L{T_(*cur)}'); i += 1
        elif cmd == 'C':
            out.append(f'C{T_(v(0), v(1))} {T_(v(2), v(3))} {T_(v(4), v(5))}'); cur = (v(4), v(5)); i += 6
        elif cmd == 'A':
            cur = (v(5), v(6))
            out.append(f'A{f(v(0) * s)} {f(v(1) * s)} {toks[i + 2]} {toks[i + 3]} {toks[i + 4]} {T_(*cur)}'); i += 7
    return ' '.join(out)


def rrect_d(x, y, w, h, r):
    return (f'M{f(x + r)} {f(y)} H{f(x + w - r)} A{r} {r} 0 0 1 {f(x + w)} {f(y + r)} V{f(y + h - r)} '
            f'A{r} {r} 0 0 1 {f(x + w - r)} {f(y + h)} H{f(x + r)} A{r} {r} 0 0 1 {f(x)} {f(y + h - r)} '
            f'V{f(y + r)} A{r} {r} 0 0 1 {f(x + r)} {f(y)} Z')


def dval(e):
    return re.search(r' d="([^"]+)"', e).group(1)


def slash_all(*els):
    """Element strings -> lines opened around the slash, plus the slash."""
    return slashed(*[el_segs(e) for e in els])


def ellipse_segs(c, rx, ry):
    k = 0.5523
    cx, cy = c
    return [('C', (cx, cy - ry), (cx + rx * k, cy - ry), (cx + rx, cy - ry * k), (cx + rx, cy)),
            ('C', (cx + rx, cy), (cx + rx, cy + ry * k), (cx + rx * k, cy + ry), (cx, cy + ry)),
            ('C', (cx, cy + ry), (cx - rx * k, cy + ry), (cx - rx, cy + ry * k), (cx - rx, cy)),
            ('C', (cx - rx, cy), (cx - rx, cy - ry * k), (cx - rx * k, cy - ry), (cx, cy - ry))]


def keep_out(segs, holes, closed=False):
    """Pieces of segs outside every (centre, radius) in holes, as path elements."""
    runs, whole = trim(segs, lambda p: all(dist(p, c) >= r for c, r in holes), closed)
    if whole:
        return [P(segs_d(segs, closed))]
    return [P(segs_d(r_)) for r_ in runs if r_]


# ================================================================ extra badge marks
def badge2(kind):
    b = dict(line=[], area=[], hole=[], dot=[], detail=[])
    if kind == 'gear':
        g = gear_path(B, 23, 35, 6, -90)
        b['line'] = [P(g)]; b['area'] = [P(g)]; b['hole'] = [C(BX, BY, 8)]
        return b, 62
    if kind == 'pencil':
        pen = xf('M163.37 208.63 L184.59 204.38 L212.87 176.1 L195.9 159.13 L167.62 187.41 Z', 1, 0, (188, 184), B)
        b['line'] = [P(pen)]; b['area'] = [P(pen)]
        return b, 58
    if kind == 'play':
        tri = T([(-16, -26), (24, 0), (-16, 26)])
        b['line'] = [PG(tri)]; b['area'] = [PG(tri)]
        return b, 58
    if kind == 'stop':
        sq = R(BX - 24, BY - 24, 48, 48, 8)
        b['line'] = [sq]; b['area'] = [sq]
        return b, 60
    if kind == 'shield':
        sh = (f'M{BX} {BY - 34} L{BX + 28} {BY - 22} V{BY - 2} C{BX + 28} {BY + 20} {BX + 15} {BY + 30} {BX} {BY + 36} '
              f'C{BX - 15} {BY + 30} {BX - 28} {BY + 20} {BX - 28} {BY - 2} V{BY - 22} Z')
        b['line'] = [P(sh)]; b['area'] = [P(sh)]
        return b, 62
    return badge(kind)


# ================================================================ clock family (geometry of icons/clock.svg; hands as clock-check)
CLK = seg_circle((128, 128), 96)
HANDS = PL([(128, 76), (128, 128), (88, 128)])
CLOCK_BADGES = [
    ('clock-gear', 'gear', ['time settings', 'schedule settings', 'history settings', 'clock', 'settings']),
    ('clock-heart', 'heart', ['clock', 'favorite', 'like', 'time', 'hour']),
    ('clock-magnifying-glass', 'magnifying-glass', ['clock', 'search', 'find', 'time', 'hour']),
    ('clock-minus', 'minus', ['clock', 'remove', 'subtract', 'time', 'hour']),
    ('clock-pause', 'pause', ['clock', 'paused', 'hold', 'time', 'hour']),
    ('clock-pencil', 'pencil', ['clock', 'edit', 'write', 'time', 'hour']),
    ('clock-play', 'play', ['clock', 'start', 'play', 'time', 'hour']),
    ('clock-plus', 'plus', ['add time', 'extend', 'more time', 'clock', 'add']),
    ('clock-push-pin', 'push-pin', ['clock', 'pinned', 'pin', 'time', 'hour']),
    ('clock-question', 'question', ['clock', 'help', 'unknown', 'time', 'hour']),
    ('clock-share', 'share', ['clock', 'share', 'send', 'time', 'hour']),
    ('clock-shield', 'shield', ['clock', 'secure', 'protected', 'time', 'hour']),
    ('clock-star', 'star', ['clock', 'favorite', 'starred', 'time', 'hour']),
    ('clock-stop', 'stop', ['clock', 'stop', 'halt', 'time', 'hour']),
    ('clock-user', 'user', ['timesheet', 'attendance', 'shift']),
    ('clock-warning', 'warning', ['clock', 'warning', 'error', 'time', 'hour']),
    ('clock-x', 'x', ['clock', 'remove', 'cancel', 'time', 'hour']),
]
for _name, _kind, _tags in CLOCK_BADGES:
    _b, _cr = badge2(_kind)
    _ln, _ar = carve(CLK, B, _cr + 4)
    icon(_name, TM, _tags, **merge(dict(line=[P(_ln)], area=[P(_ar)], detail=[HANDS]), _b))

# clock-slash: ring and 12/3 hands opened around the slash
icon('clock-slash', TM, ['clock', 'disabled', 'off', 'time', 'hour'],
     line=slashed((CLK, True), (seg_poly([(128, 60), (128, 128), (196, 128)]), False)))

# clock-globe: globe (as globe-pause) with a small clock badge
GC = 70
_ln, _ar = carve(CLK, B, GC)
_glob_detail = keep_out(ellipse_segs((128, 128), 40, 96), [(B, GC)], True) + keep_out(seg_poly([(32, 128), (224, 128)]), [(B, GC)])
icon('clock-globe', TM, ['time zone', 'world clock', 'global time', 'globe', 'timezone'],
     line=[P(_ln), C(BX, BY, 34)], area=[P(_ar), C(BX, BY, 34)],
     detail=_glob_detail + [PL([(BX, BY - 14), (BX, BY), (BX + 11, BY + 7)])])

# ================================================================ gauges (geometry of icons/gauge.svg)
GA = load('gauge')
for _name, _sgn, _tags in (('gauge-fast', 1, ['speed up', 'speed', 'increase', 'meter']),
                           ('gauge-slow', -1, ['slow down', 'speed', 'decrease', 'meter'])):
    tip = (128 + _sgn * 54 * math.cos(math.radians(15)), 148 - 54 * math.sin(math.radians(15)))
    icon(_name, TM, _tags, line=GA['line'], area=GA['area'], detail=[L(128, 148, *tip)], dotcut=GA['dotcut'])

# ================================================================ hourglasses (geometry of icons/hourglass.svg)
HG = load('hourglass')
SAND_TOP_FULL = 'M100 64 H156 C152 80 136 92 128 100 C120 92 104 80 100 64 Z'
SAND_TOP_HALF = 'M108 80 H148 C146 90 136 96 128 100 C120 96 110 90 108 80 Z'
SAND_BOT_FULL = 'M100 208 H156 C156 190 140 176 128 176 C116 176 100 190 100 208 Z'
SAND_BOT_HALF = 'M108 208 H148 C148 198 140 192 128 192 C116 192 108 198 108 208 Z'
icon('hourglass-empty', TM, ['hourglass', 'time up', 'timer', 'waiting'], line=HG['line'])
for _name, sand, _tags in (
        ('hourglass-high', [SAND_TOP_FULL], ['hourglass', 'start', 'sand', 'timer', 'just started']),
        ('hourglass-medium', [SAND_TOP_HALF, SAND_BOT_HALF], ['hourglass', 'waiting', 'sand', 'timer', 'half time']),
        ('hourglass-low', [SAND_BOT_FULL], ['hourglass', 'time running out', 'sand', 'timer', 'almost done'])):
    icon(_name, TM, _tags, line=HG['line'] + [P(s) for s in sand], area=[P(s) for s in sand])
icon('hourglass-slash', TM, ['hourglass', 'off', 'disabled', 'hidden'], line=slash_all(*HG['line']))

# ================================================================ moon
MO = load('moon')
# the crescent's inner curve runs parallel to the usual slash, so this one leans the other way (as clock-counter-clockwise-slash)
_ms, _ = el_segs(MO['line'][0])
_mr, _ = trim(_ms, lambda p: seg_dist(p, (208, 48), (48, 208)) >= SG, True)
icon('moon-slash', TM, ['bedtime off', 'night mode off', 'sleep', 'moon'],
     line=[P(segs_d(r_)) for r_ in _mr] + [L(208, 48, 48, 208)])
MS = load('moon-stars')
ZZ = [PL([(144, 40), (192, 40), (144, 88), (192, 88)]), PL([(188, 112), (220, 112), (188, 144), (220, 144)])]
icon('moon-z', TM, ['sleep', 'snooze', 'night', 'rest'], line=[MS['line'][0]] + ZZ, area=[MS['area'][0]])

# ================================================================ stopwatch / timer slash
SW = load('stopwatch')
icon('stopwatch-slash', TM, ['timer off', 'stopwatch', 'disabled', 'slash'],
     line=slash_all(*SW['line']))
TI = load('timer')
icon('timer-slash', TM, ['timer off', 'no timer', 'disabled'], line=slash_all(*TI['line'], *TI['detail']))


# ================================================================ airplanes (geometry of icons/airplane.svg)
AP = dval(load('airplane')['line'][0])
AP_C = (128, 136)          # centre of the airplane's bounding box




def plane_outline(nose_r, nose_y, wing, tail, end_y):
    """Airplane pointing up around (0,0): wing = (root lead y, tip x, tip lead y, tip trail y, root trail y),
    tail = (root y, tip x, tip lead y, tip trail y). Body half width = nose_r. Same shape language as airplane.svg."""
    w = nose_r
    ry0, tx, ty0, ty1, ry1 = wing
    try0, ttx, tty0, tty1 = tail
    right = [(w, ry0), (tx, ty0), (tx, ty1), (w, ry1), (w, try0), (ttx, tty0), (ttx, tty1), (0, end_y)]
    left = [(-x, y) for x, y in reversed(right[:-1])]
    pts = right + left + [(-w, nose_y)]
    return f'M{f(-w)} {f(nose_y)} A{f(w)} {f(w)} 0 0 1 {f(w)} {f(nose_y)} ' + ' '.join(f'L{f(x)} {f(y)}' for x, y in pts) + ' Z'


# compact plane (full stroke proportions, 144 x 150) and a mini plane for small marks
CPLANE = plane_outline(16, -60, (-20, 72, 12, 36, 20), (44, 44, 62, 74), 66)
MPLANE = plane_outline(14, -34, (-8, 46, 14, 32, 22), (38, 30, 48, 56), 50)


def plane(c, s, deg, d=None):
    d = xf(d or CPLANE, s, deg, (0, 0), c)
    return dict(line=[P(d)], area=[P(d)])


GROUND = L(32, 216, 224, 216)

# circling: a small plane inside a circular arrow
_c = (128, 128); _r = 92
_a0, _a1 = -62, 238
_end = polar(_c, _r, _a1)
_tan = (-math.sin(math.radians(_a1)), math.cos(math.radians(_a1)))
_nrm = (math.cos(math.radians(_a1)), math.sin(math.radians(_a1)))
_head = [(_end[0] - _tan[0] * 24 + _nrm[0] * 22, _end[1] - _tan[1] * 24 + _nrm[1] * 22), _end,
         (_end[0] - _tan[0] * 24 - _nrm[0] * 22, _end[1] - _tan[1] * 24 - _nrm[1] * 22)]
icon('airplane-circling', TR, ['holding pattern', 'flight loop', 'aircraft'],
     **merge(plane((128, 124), 1, 0, MPLANE),
             dict(line=[P(f'M{pt(polar(_c, _r, _a0))} A{_r} {_r} 0 1 1 {pt(_end)}'), PL(_head)])))

icon('airplane-in-flight', TR, ['flight', 'in flight', 'travel', 'flying', 'airplane'],
     **merge(plane((128, 104), 1, 90), dict(line=[GROUND])))
icon('airplane-takeoff', TR, ['takeoff', 'departure', 'flight', 'plane', 'airplane'],
     **merge(plane((128, 108), 1, 60), dict(line=[GROUND])))
icon('airplane-landing', TR, ['landing', 'arrival', 'flight', 'airplane', 'land'],
     **merge(plane((124, 114), 1, 120), dict(line=[GROUND])))
icon('airplane-taxiing', TR, ['taxiing', 'runway', 'ground'],
     **merge(plane((128, 112), 1, 90), dict(line=[L(32, 216, 64, 216), L(104, 216, 152, 216), L(192, 216, 224, 216)])))

icon('airplane-slash', TR, ['no flights', 'cancelled flight', 'airplane mode off', 'airplane mode', 'flight off'],
     line=slash_all(P(AP)))

# propeller plane seen from the front
FUS_C, FUS_R = (128, 132), 36
FUS = C(*FUS_C, FUS_R)
WING = seg_rect(32, 116, 192, 32, 16)
_wing = keep_out(WING, [(FUS_C, FUS_R)], True)
_wing_area = 'M48 116 H208 A16 16 0 0 1 208 148 H48 A16 16 0 0 1 48 116 Z'
icon('airplane-propeller', TR, ['prop plane', 'propeller', 'small aircraft'],
     line=_wing + [FUS, L(128, 44, 128, 220), L(72, 148, 72, 184), L(184, 148, 184, 184)],
     area=[P(_wing_area), FUS], dot=[C(72, 200, 16), C(184, 200, 16)], dotcut=[C(*FUS_C, 12)])

WIN = R(56, 32, 144, 192, 64)
icon('airplane-window', TR, ['window', 'flight', 'porthole', 'cabin'],
     line=[WIN], area=[WIN], detail=[R(88, 64, 80, 128, 40), L(88, 104, 168, 104)])

# airport: control tower and terminal
CAB = PG([(48, 64), (112, 64), (100, 104), (60, 104)])
TERM = P('M128 216 V144 A8 8 0 0 1 136 136 H200 A8 8 0 0 1 208 144 V216')
icon('airport', TR, ['airport', 'terminal', 'flight'],
     line=[CAB, L(80, 64, 80, 40), PL([(64, 104), (64, 216)]), PL([(96, 104), (96, 216)]), TERM, GROUND],
     area=[CAB, P('M128 216 V144 A8 8 0 0 1 136 136 H200 A8 8 0 0 1 208 144 V216 Z')],
     detail=[L(152, 176, 184, 176)])

# automatic gearbox: shift plate with a P-R-N-D gate (4 stops) and the knob
PLATE = R(56, 32, 144, 192, 16)
icon('automatic-gearbox', TR, ['gearbox', 'transmission', 'automatic', 'car'],
     line=[PLATE], area=[PLATE],
     detail=[PL([(104, 72), (104, 104), (152, 104), (152, 144), (104, 144), (104, 184)])],
     dotcut=[C(104, 184, 18)])

# bicycle slash (geometry of icons/bicycle.svg)
icon('bicycle-slash', TR, ['bicycle', 'disabled', 'off', 'transport'], line=slash_all(*load('bicycle')['line']))

# boarding pass: ticket with a small airplane
TK = load('ticket')
icon('boarding-pass', TR, ['airplane ticket', 'flight', 'boarding', 'travel'],
     line=TK['line'], area=TK['area'],
     detail=TK['detail'] + [P(xf(MPLANE, 0.78, 90, (0, 5), (104, 128)))])

# brake disc with caliper
BD_C = (116, 140); BD_R = 84
CAL_A0, CAL_A1, CAL_RI, CAL_RO = -78, -12, 60, 108
cal = (f'M{pt(polar(BD_C, CAL_RI, CAL_A0))} L{pt(polar(BD_C, CAL_RO, CAL_A0))} '
       f'A{CAL_RO} {CAL_RO} 0 0 1 {pt(polar(BD_C, CAL_RO, CAL_A1))} L{pt(polar(BD_C, CAL_RI, CAL_A1))} '
       f'A{CAL_RI} {CAL_RI} 0 0 0 {pt(polar(BD_C, CAL_RI, CAL_A0))} Z')
cal_pts = sample(parse(cal)[0])
rim = trim(seg_circle(BD_C, BD_R), lambda p: not inside(cal_pts, p))[0]
icon('brake-disc', TR, ['brakes', 'disc', 'car parts', 'maintenance'],
     line=[P(segs_d(r_)) for r_ in rim] + [P(cal)], area=[C(*BD_C, BD_R), P(cal)],
     detail=[C(*BD_C, 24)], dotcut=[C(*polar(BD_C, 54, a), 10) for a in (30, 102, 174, 246)])

# ================================================================ road vehicles
# bulldozer: crawler track, body with cab, front blade on a push arm
TRACK = R(80, 168, 136, 48, 24)
DOZ = 'M96 168 V136 A8 8 0 0 1 104 128 H200 A8 8 0 0 1 208 136 V168 Z'
CABF = 'M120 128 V72 A8 8 0 0 1 128 64 H176 A8 8 0 0 1 184 72 V128'
icon('bulldozer', TR, ['bulldozer', 'construction', 'vehicle', 'dig'],
     line=[TRACK, P(DOZ), P(CABF), P('M64 104 A96 96 0 0 0 48 216 H72'), L(62, 152, 96, 152)],
     area=[TRACK, P(DOZ)], dotcut=[C(104, 192, 12), C(192, 192, 12)])

# school bus, side view: long body with a short hood, window band, wheels
SB = 'M48 56 H176 A16 16 0 0 1 192 72 V112 H208 A16 16 0 0 1 224 128 V168 A16 16 0 0 1 208 184 H48 A16 16 0 0 1 32 168 V72 A16 16 0 0 1 48 56 Z'
SB_W = [((80, 184), 20), ((176, 184), 20)]
_sb, _ = parse(SB)
icon('bus-school', TR, ['school bus', 'bus', 'students', 'transport'],
     line=keep_out(_sb, [(c, r + 16) for c, r in SB_W], True) + [C(*c, r) for c, r in SB_W],
     area=[P(SB)] + [C(*c, r) for c, r in SB_W],
     detail=[R(56, 80, 112, 40, 8), L(93, 80, 93, 120), L(131, 80, 131, 120)])

# bus slash (geometry of icons/bus.svg)
BU = load('bus')
icon('bus-slash', TR, ['bus', 'disabled', 'off', 'transport'],
     line=slash_all(*BU['line'], *BU['detail']), dot=[BU['dotcut'][0]])

# bus stop: sign showing a bus face, on a post
SIGN = R(64, 32, 128, 112, 20)
icon('bus-stop', TR, ['bus stop', 'transit', 'sign', 'station'],
     line=[SIGN, L(128, 144, 128, 224), L(96, 224, 160, 224)], area=[SIGN],
     detail=[R(92, 60, 72, 28, 6)], dotcut=[C(100, 116, 11), C(156, 116, 11)])

# camper van: van body with a pop-up roof
CV = 'M48 80 H160 L192 120 H208 A16 16 0 0 1 224 136 V168 A16 16 0 0 1 208 184 H48 A16 16 0 0 1 32 168 V96 A16 16 0 0 1 48 80 Z'
CV_W = [((80, 184), 20), ((176, 184), 20)]
_cv, _ = parse(CV)
icon('camper-van', TR, ['rv', 'caravan', 'motorhome', 'camping', 'camper'],
     line=keep_out(_cv, [(c, r + 16) for c, r in CV_W], True) + [C(*c, r) for c, r in CV_W]
     + [P('M56 80 L72 44 H136 L152 80')],
     area=[P(CV), P('M56 80 L72 44 H136 L152 80 Z')] + [C(*c, r) for c, r in CV_W],
     detail=[R(60, 104, 56, 32, 8)])

# 4wd: car from above, four wheels on axles
CAR_TOP = R(80, 40, 96, 176, 32)
icon('car-4wd', TR, ['4x4', 'off-road', 'four wheel drive'],
     line=[CAR_TOP] + [L(x, y - 20, x, y + 20) for x in (48, 208) for y in (84, 172)]
     + [L(48, y, 80, y) for y in (84, 172)] + [L(176, y, 208, y) for y in (84, 172)],
     area=[CAR_TOP], detail=[P('M104 104 Q128 92 152 104'), L(108, 172, 148, 172)])

# car battery: box, two terminals, plus and minus
BAT = R(32, 72, 192, 136, 16)
icon('car-battery', TR, ['car battery', 'automotive', '12v', 'power', 'terminal'],
     line=[BAT, P('M64 72 V56 A8 8 0 0 1 72 48 H88 A8 8 0 0 1 96 56 V72'),
           P('M160 72 V56 A8 8 0 0 1 168 48 H184 A8 8 0 0 1 192 56 V72')],
     area=[BAT], detail=[L(60, 140, 100, 140), L(80, 120, 80, 160), L(156, 140, 196, 140)])

# car crash: the car (geometry of icons/car.svg, scaled) with impact lines at its corner
CR = load('car')
_s, _o = 0.8, (32, 216)
car_small = dict(line=[P(xf(rrect_d(32, 112, 192, 72, 16), _s, 0, _o))] + [P(xf(dval(e), _s, 0, _o)) for e in CR['line'][1:]],
                 area=[P(xf(rrect_d(32, 112, 192, 72, 16), _s, 0, _o))],
                 detail=[P(xf(dval(CR['detail'][0]), _s, 0, _o))])
_dc = [C(32 + (x - 32) * _s, 216 + (y - 216) * _s, 14) for x, y in ((72, 148), (184, 148))]
icon('car-crash', TR, ['accident', 'collision', 'crash', 'car', 'insurance'],
     **merge(car_small, dict(dotcut=_dc, line=[L(176, 72, 168, 44), L(196, 88, 220, 64), L(204, 112, 224, 108)])))

# car door: side door with window and handle
DOOR = 'M104 40 H192 A16 16 0 0 1 208 56 V200 A16 16 0 0 1 192 216 H64 A16 16 0 0 1 48 200 V112 Z'
icon('car-door', TR, ['car door', 'car', 'vehicle', 'auto', 'door'],
     line=[P(DOOR)], area=[P(DOOR)],
     detail=[PG([(116, 68), (180, 68), (180, 112), (84, 112)]), L(148, 148, 180, 148)])

print(save(overwrite=True))
