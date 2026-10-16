import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

SEC = 'Security'
SLASH = L(48, 48, 208, 208)

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


def arc_seg(p0, r, large, sweep, p1):
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    d = math.hypot(dx, dy)
    h = math.sqrt(max(r * r - (d / 2) ** 2, 0))
    for sgn in (1, -1):
        c = (mx - sgn * h * dy / d, my + sgn * h * dx / d)
        a0 = math.atan2(p0[1] - c[1], p0[0] - c[0])
        a1 = math.atan2(p1[1] - c[1], p1[0] - c[0])
        span = (a1 - a0) % (2 * math.pi) if sweep else -((a0 - a1) % (2 * math.pi))
        if abs(abs(span) - math.pi) < 1e-6 or (abs(span) > math.pi) == bool(large):
            return ('A', c, r, a0, a0 + span)
    raise ValueError('arc')


def parse(d):
    """Absolute M/L/H/V/C/A/Z path -> list of (segments, closed)."""
    toks = re.findall(r'[A-Za-z]|-?\d+(?:\.\d+)?', d)
    subs, segs, cur, start, i, cmd, closed = [], [], None, None, 0, None, False
    num = lambda k: float(toks[k])
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd == 'Z':
                if dist(cur, start) > 1e-6:
                    segs.append(('L', cur, start))
                cur, closed = start, True
            continue
        if cmd == 'M':
            if segs:
                subs.append((segs, closed))
            segs, closed = [], False
            cur = start = (num(i), num(i + 1)); i += 2; cmd = 'L'
        elif cmd == 'L':
            p = (num(i), num(i + 1)); i += 2; segs.append(('L', cur, p)); cur = p
        elif cmd == 'H':
            p = (num(i), cur[1]); i += 1; segs.append(('L', cur, p)); cur = p
        elif cmd == 'V':
            p = (cur[0], num(i)); i += 1; segs.append(('L', cur, p)); cur = p
        elif cmd == 'C':
            c1, c2, p = (num(i), num(i + 1)), (num(i + 2), num(i + 3)), (num(i + 4), num(i + 5)); i += 6
            segs.append(('C', cur, c1, c2, p)); cur = p
        elif cmd == 'A':
            r, large, sweep, p = num(i), int(num(i + 3)), int(num(i + 4)), (num(i + 5), num(i + 6)); i += 7
            segs.append(arc_seg(cur, r, large, sweep, p)); cur = p
        else:
            raise ValueError(cmd)
    if segs:
        subs.append((segs, closed))
    return subs


def trim(segs, keep, closed=True, steps=240):
    """Split an outline into runs of segments where keep(point) holds."""
    pieces = []
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


def carve(d, cut_c, cut_r):
    """Open the closed outline d around a circular badge. Returns (line element, area element)."""
    segs = parse(d)[0][0]
    runs, whole = trim(segs, lambda p: dist(p, cut_c) >= cut_r)
    assert not whole and len(runs) == 1, (whole, len(runs))
    run = runs[0]
    s, e = seg_point(run[0], 0), seg_end(run[-1])
    poly_pts = sample(segs)
    arc = arc_to(cut_c, cut_r, e, s, lambda m: 1 if inside(poly_pts, m) else 0)
    return P(segs_d(run)), P(segs_d(run) + ' ' + arc + ' Z')


def seg_dist(p, a=(48, 48), b=(208, 208)):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + dx * t, a[1] + dy * t))


def gapped(d, sg=30):
    """Open every subpath of d where it passes within sg of the slash."""
    out = []
    for segs, closed in parse(d):
        runs, whole = trim(segs, lambda p: seg_dist(p) >= sg, closed)
        if whole:
            out.append(P(segs_d(segs, closed)))
        else:
            out += [P(segs_d(r)) for r in runs if r]
    return out


def circle_d(cx, cy, r):
    return f'M{f(cx - r)} {f(cy)} A{f(r)} {f(r)} 0 1 1 {f(cx + r)} {f(cy)} A{f(r)} {f(r)} 0 1 1 {f(cx - r)} {f(cy)} Z'


def tf(points, s, c_from, c_to):
    return [(c_to[0] + (x - c_from[0]) * s, c_to[1] + (y - c_from[1]) * s) for x, y in points]


def tf_path(d, fn, s=1.0):
    toks = re.findall(r'[A-Za-z]|-?\d+(?:\.\d+)?', d)
    out, i, cmd = [], 0, None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            out.append(t)
            i += 1
            continue
        if cmd == 'A':
            rx, ry, a, la, sw, x, y = toks[i:i + 7]
            out.append(f'{f(float(rx) * s)} {f(float(ry) * s)} {a} {la} {sw} {pt(fn((float(x), float(y))))}')
            i += 7
        else:
            out.append(pt(fn((float(toks[i]), float(toks[i + 1])))))
            i += 2
    return re.sub(r'([MLCAZ]) ', r'\1', ' '.join(out))


# ================================================================ badge marks (same set as the badges of batches 149-151)
def marks(kind, B):
    x, y = B
    m = {'line': [], 'area': [], 'dot': [], 'dotcut': [], 'detail': [], 'hole': []}
    if kind == 'plus':
        m['line'] += [L(x - 28, y, x + 28, y), L(x, y - 28, x, y + 28)]
    elif kind == 'minus':
        m['line'] += [L(x - 28, y, x + 28, y)]
    elif kind == 'x':
        m['line'] += [L(x - 22, y - 22, x + 22, y + 22), L(x + 22, y - 22, x - 22, y + 22)]
    elif kind == 'check':
        m['line'] += [PL([(x - 28, y + 2), (x - 8, y + 22), (x + 28, y - 14)])]
    elif kind == 'warning':
        m['line'] += [L(x, y - 34, x, y - 2)]
        m['dot'] += [C(x, y + 26, 16)]
    elif kind == 'question':
        c = (x, y - 26)
        st = polar(c, 14, 180)
        en = polar(c, 14, 60)
        m['line'] += [P(f'M{pt(st)} A14 14 0 1 1 {pt(en)} C{f(x + 2)} {f(y - 11)} {f(x)} {f(y - 8)} {f(x)} {f(y - 2)}')]
        m['dot'] += [C(x, y + 26, 16)]
    elif kind == 'arrow-up':
        m['line'] += [L(x, y + 30, x, y - 30), PL([(x - 24, y - 6), (x, y - 30), (x + 24, y - 6)])]
    elif kind == 'arrow-down':
        m['line'] += [L(x, y - 30, x, y + 30), PL([(x - 24, y + 6), (x, y + 30), (x + 24, y + 6)])]
    elif kind == 'pause':
        m['line'] += [L(x - 16, y - 24, x - 16, y + 24), L(x + 16, y - 24, x + 16, y + 24)]
    elif kind == 'code':
        m['line'] += [PL([(x - 12, y - 22), (x - 30, y), (x - 12, y + 22)]),
                      PL([(x + 12, y - 22), (x + 30, y), (x + 12, y + 22)])]
    elif kind == 'dollar':
        m['line'] += [L(x, y - 36, x, y + 36),
                      P(f'M{f(x + 18)} {f(y - 26)} H{f(x - 6)} A13 13 0 0 0 {f(x - 6)} {f(y)} H{f(x + 6)} '
                        f'A13 13 0 0 1 {f(x + 6)} {f(y + 26)} H{f(x - 18)}')]
    elif kind == 'bitcoin':
        x0 = x - 14
        m['line'] += [P(f'M{f(x0 - 8)} {f(y - 26)} H{f(x0 + 16)} A13 13 0 0 1 {f(x0 + 16)} {f(y)} H{f(x0)}'),
                      P(f'M{f(x0)} {f(y)} H{f(x0 + 19)} A13 13 0 0 1 {f(x0 + 19)} {f(y + 26)} H{f(x0 - 8)}'),
                      L(x0, y - 26, x0, y + 26), L(x0 + 10, y - 36, x0 + 10, y - 26), L(x0 + 10, y + 26, x0 + 10, y + 36)]
    elif kind == 'percent':
        m['line'] += [L(x + 22, y - 22, x - 22, y + 22)]
        m['dot'] += [C(x - 20, y - 20, 14), C(x + 20, y + 20, 14)]
    elif kind == 'gear':
        g = []
        for i in range(6):
            t = i * 60 - 90
            g += [polar(B, 21, t - 22), polar(B, 31, t - 13), polar(B, 31, t + 13), polar(B, 21, t + 22)]
        d = 'M' + pt(g[0])
        for i in range(6):
            a, b, cc, dd = g[i * 4:i * 4 + 4]
            if i:
                d += f' A21 21 0 0 1 {pt(a)}'
            d += f' L{pt(b)} L{pt(cc)} L{pt(dd)}'
        d += f' A21 21 0 0 1 {pt(g[0])} Z'
        m['line'] += [P(d)]
        m['area'] += [P(d)]
        m['hole'] = [C(x, y, 12)]
    elif kind == 'heart':
        s = 0.34
        T = lambda px, py: pt((x + (px - 128) * s, y + 4 + (py - 136) * s))
        r = f(50 * s)
        d = (f'M{T(128, 212)} C{T(128, 212)} {T(32, 160)} {T(32, 98)} A{r} {r} 0 0 1 {T(128, 78)} '
             f'A{r} {r} 0 0 1 {T(224, 98)} C{T(224, 160)} {T(128, 212)} {T(128, 212)} Z')
        m['line'] += [P(d)]
        m['area'] += [P(d)]
    elif kind == 'star':
        st = [polar((x, y + 3), 36 if i % 2 == 0 else 16, -90 + i * 36) for i in range(10)]
        m['line'] += [PG(st)]
        m['area'] += [PG(st)]
    elif kind == 'lightning':
        pts = [(144, 32), (56, 144), (120, 144), (104, 224), (200, 108), (136, 108)]
        pp = tf(pts, 0.36, (128, 128), B)
        m['line'] += [PG(pp)]
        m['area'] += [PG(pp)]
    elif kind == 'magnifying-glass':
        m['line'] += [C(x - 6, y - 6, 22), L(x + 11, y + 11, x + 28, y + 28)]
        m['area'] += [C(x - 6, y - 6, 22)]
    elif kind == 'push-pin':
        pts = [(162.03, 33.63), (210.94, 74.67), (186.36, 89.76), (157.05, 124.7), (153.32, 192.99),
               (55.51, 110.92), (122.12, 95.39), (151.43, 60.45)]
        pp = tf(pts, 0.36, (128, 128), (x + 4, y - 4))
        nd = tf([(104.41, 151.96), (51.65, 214.84)], 0.36, (128, 128), (x + 4, y - 4))
        m['line'] += [PG(pp), PL(nd)]
        m['area'] += [PG(pp)]
    elif kind == 'share':
        m['line'] += [P(f'M{f(x - 24)} {f(y + 26)} V{f(y + 14)} A24 24 0 0 1 {f(x)} {f(y - 10)} H{f(x + 26)}'),
                      PL([(x + 10, y - 26), (x + 26, y - 10), (x + 10, y + 6)])]
    elif kind == 'sparkle':
        sp = 'M128 32 C136 96 160 120 224 128 C160 136 136 160 128 224 C120 160 96 136 32 128 C96 120 120 96 128 32 Z'
        d = tf_path(sp, lambda p: tf([p], 0.42, (128, 128), B)[0])
        m['line'] += [P(d)]
        m['area'] += [P(d)]
    elif kind == 'pencil':
        pg = PG([(x - 30, y + 30), (x - 24, y + 8), (x + 8, y - 24), (x + 22, y - 10), (x - 10, y + 22)])
        m['line'] += [pg]
        m['area'] += [pg]
    else:
        raise ValueError(kind)
    return m


def badge(name, tags, base, kind, B):
    mk = marks(kind, B)
    icon(name, SEC, tags,
         line=base.get('line', []) + mk['line'], detail=base.get('detail', []) + mk['detail'],
         area=base.get('area', []) + mk['area'], hole=base.get('hole', []) + mk['hole'],
         dot=base.get('dot', []) + mk['dot'], dotcut=base.get('dotcut', []) + mk['dotcut'])


def d_of(el):
    return re.search(r'd="([^"]+)"', el).group(1)



def rect_d(x, y, w, h, r):
    return (f'M{f(x + r)} {f(y)} H{f(x + w - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w)} {f(y + r)} V{f(y + h - r)} '
            f'A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(y + h)} H{f(x + r)} A{f(r)} {f(r)} 0 0 1 {f(x)} {f(y + h - r)} '
            f'V{f(y + r)} A{f(r)} {f(r)} 0 0 1 {f(x + r)} {f(y)} Z')


def ellipse_d(cx, cy, rx, ry):
    k = 0.5523
    return (f'M{f(cx)} {f(cy - ry)} C{f(cx + k * rx)} {f(cy - ry)} {f(cx + rx)} {f(cy - k * ry)} {f(cx + rx)} {f(cy)} '
            f'C{f(cx + rx)} {f(cy + k * ry)} {f(cx + k * rx)} {f(cy + ry)} {f(cx)} {f(cy + ry)} '
            f'C{f(cx - k * rx)} {f(cy + ry)} {f(cx - rx)} {f(cy + k * ry)} {f(cx - rx)} {f(cy)} '
            f'C{f(cx - rx)} {f(cy - k * ry)} {f(cx - k * rx)} {f(cy - ry)} {f(cx)} {f(cy - ry)} Z')


def normalize(d):
    return ' '.join(segs_d(sg, cl) for sg, cl in parse(d))


def scaled(d, s, c_from, c_to):
    return tf_path(normalize(d), lambda p: tf([p], s, c_from, c_to)[0], s)


BADGE = (184, 184)


def ast(c, r=14):
    """Three-stroke asterisk centred at c."""
    x, y = c
    dx, dy = r * math.cos(math.radians(30)), r * math.sin(math.radians(30))
    return [L(x, y - r, x, y + r), L(x - dx, y - dy, x + dx, y + dy), L(x - dx, y + dy, x + dx, y - dy)]


def rotd(d, deg, c):
    return tf_path(normalize(d), lambda p: rot([p], deg, c)[0])


# ================================================================ shield family (base: shield)
shield = load('shield')
SHIELD_D = d_of(shield['line'][0])
SC = (118, 116)
SHIELD_S = scaled(SHIELD_D, 0.875, (128, 128), SC)
sh_ln, sh_ar = carve(SHIELD_S, BADGE, 60)
shield_base = dict(line=[sh_ln], area=[sh_ar])
for kind, suffix, tags in [
    ('arrow-down', 'arrow-down', ['shield', 'download', 'down', 'decrease']),
    ('arrow-up', 'arrow-up', ['shield', 'upload', 'up', 'increase']),
    ('code', 'code', ['shield', 'code', 'developer', 'embed']),
    ('dollar', 'currency-dollar', ['shield', 'dollar', 'price', 'money']),
    ('gear', 'gear', ['shield', 'settings', 'configure']),
    ('pause', 'pause', ['shield', 'paused', 'hold']),
    ('push-pin', 'push-pin', ['shield', 'pin', 'pinned']),
    ('share', 'share', ['shield', 'share', 'send']),
]:
    badge('shield-' + suffix, tags, shield_base, kind, BADGE)

SH = dict(line=[P(SHIELD_D)], area=[P(SHIELD_D)])


def sh(name, tags, detail=(), hole=(), dotcut=(), line=(), area=None):
    icon(name, SEC, tags, line=SH['line'] + list(line), area=SH['area'] if area is None else area,
         detail=detail, hole=hole, dotcut=dotcut)


sh('shield-minus', ['shield', 'remove', 'minus', 'security', 'remove protection'], detail=[L(92, 128, 164, 128)])
sh('shield-plus', ['shield', 'add', 'plus', 'security', 'health insurance'],
   detail=[L(128, 92, 128, 164), L(92, 128, 164, 128)])
sh('shield-x', ['shield', 'unprotected', 'x', 'security', 'security failed'],
   detail=[L(104, 104, 152, 152), L(152, 104, 104, 152)])
sh('shield-warning', ['security alert', 'warning', 'shield', 'exclamation', 'unsafe'],
   detail=[L(128, 76, 128, 132)], dotcut=[C(128, 170, 16)])
sh('shield-question', ['unknown security', 'security help', 'shield', 'question', 'unknown'],
   detail=[P('M104 100 A24 24 0 1 1 138 122 C131 126 128 130 128 138 V140')], dotcut=[C(128, 174, 16)])

STAR = PG([polar((128, 124), 46 if i % 2 == 0 else 19, -90 + i * 36) for i in range(10)])
sh('shield-star', ['premium protection', 'shield', 'star', 'rank'], detail=[STAR], hole=[STAR])

heart = load('heart')
HEART_D = d_of(heart['line'][0])
HEART_IN = scaled(HEART_D, 0.42, (128, 136), (128, 126))
sh('shield-heart', ['health protection', 'care', 'insurance', 'safe'], detail=[P(HEART_IN)], hole=[P(HEART_IN)])

BOLT = PG(tf([(144, 32), (56, 144), (120, 144), (104, 224), (200, 108), (136, 108)], 0.46, (128, 128), (128, 124)))
sh('shield-lightning', ['power protection', 'shield', 'lightning', 'surge'], detail=[BOLT], hole=[BOLT])

KEYHOLE = P('M118 133.75 A24 24 0 1 1 138 133.75 L146 168 H110 Z')
sh('shield-keyhole', ['secure', 'protected', 'keyhole', 'shield', 'encrypted'], detail=[KEYHOLE], hole=[KEYHOLE])

LOCKB = R(96, 120, 64, 52, 10)
sh('shield-lock', ['secure', 'locked', 'protection', 'encryption', 'shield lock'],
   detail=[LOCKB, P('M108 120 V108 A20 20 0 0 1 148 108 V120')], hole=[LOCKB])

EYE = P('M80 124 C96 100 112 92 128 92 C144 92 160 100 176 124 C160 148 144 156 128 156 C112 156 96 148 80 124 Z')
sh('shield-eye', ['privacy', 'monitoring', 'surveillance protection', 'shield', 'eye'], detail=[EYE], dotcut=[C(128, 124, 16)])

sh('shield-magnifying-glass', ['security scan', 'audit', 'shield', 'inspect'],
   detail=[C(120, 116, 28), L(141, 137, 160, 156)])

HEAD = C(128, 94, 18)
BUST = P('M92 172 C92 154 108 146 128 146 C148 146 164 154 164 172 Z')
sh('shield-user', ['user protection', 'account security', 'admin', 'guard', 'privacy'],
   detail=[HEAD, BUST], hole=[HEAD, BUST])

sh('shield-broken', ['security breach', 'vulnerable', 'broken protection', 'shield', 'crack'],
   detail=[PL([(128, 32), (110, 92), (146, 134), (116, 180), (128, 224)])])

sh('shield-checkered', ['shield', 'checkered', 'protection', 'crest'],
   line=[L(128, 32, 128, 224), L(48, 120, 208, 120)],
   area=[P('M128 32 L48 64 V120 H128 Z'), P('M128 120 H208 C208 176 168 208 128 224 Z')])

sh('shield-half', ['shield', 'half filled', 'security', 'protection'],
   line=[L(128, 32, 128, 224)], area=[P('M128 32 L48 64 V120 C48 176 88 208 128 224 Z')])

icon('shield-slash', SEC, ['remove moderator', 'unprotected', 'shield off', 'security off', 'no security'],
     line=gapped(SHIELD_D) + [SLASH])


# ================================================================ lock badges (base: lock)
lock = load('lock')
LS, LF, LT = 0.875, (128, 124), (116, 118)
LOCK_S = scaled(rect_d(48, 104, 160, 112, 14), LS, LF, LT)
lk_ln, lk_ar = carve(LOCK_S, BADGE, 60)
lock_base = dict(line=[lk_ln, P(scaled('M88 104 V72 A40 40 0 0 1 168 72 V104', LS, LF, LT))], area=[lk_ar],
                 detail=[P(scaled('M128 144 L128 176', LS, LF, LT))])
badge('lock-warning', ['lock', 'warning', 'alert', 'error'], lock_base, 'warning', BADGE)
badge('lock-x', ['lock', 'error', 'denied', 'blocked', 'lock x'], lock_base, 'x', BADGE)

# ================================================================ devices
mon = load('monitor')
MSH = scaled(SHIELD_D, 0.375, (128, 128), (128, 112))
icon('monitor-shield', SEC, ['firewall', 'protected computer', 'antivirus', 'monitor', 'shield'],
     line=mon['line'], area=mon['area'], detail=[P(MSH)])

PH_D = rect_d(72, 32, 112, 192, 20)
ph_ln, ph_ar = carve(PH_D, BADGE, 60)
MINI = scaled(SHIELD_D, 0.4, (128, 128), (184, 186))
icon('two-factor-auth', SEC, ['2fa', 'verification', 'otp', 'security', 'code'], line=[ph_ln, P(MINI)], area=[ph_ar, P(MINI)], detail=[L(112, 64, 144, 64)],
     dotcut=[C(100, 108, 10), C(128, 108, 10), C(156, 108, 10)])
icon('password-phone', SEC, ['phone password', 'pin code', 'mobile', 'otp'], line=[R(72, 32, 112, 192, 20)], area=[R(72, 32, 112, 192, 20)], detail=[L(112, 64, 144, 64)] + ast((128, 136), 26))


icon('password', SEC, ['pin entry', 'asterisks', 'password field', 'secret', 'login'],
     line=[R(32, 72, 192, 112, 16)], area=[R(32, 72, 192, 112, 16)],
     detail=ast((76, 128), 18) + ast((140, 128), 18) + [L(192, 100, 192, 156)])

# document + key badge
DOC = rect_d(56, 32, 144, 192, 14)
dc_ln, dc_ar = carve(DOC, BADGE, 60)
icon('password-phrase', SEC, ['secret phrase', 'recovery phrase', 'passphrase', 'keys'],
     line=[dc_ln, C(170, 198, 18), L(182.73, 185.27, 214, 154), L(203, 165, 214.3, 176.3)],
     area=[dc_ar, C(170, 198, 18)],
     detail=[L(88, 76, 120, 76), L(152, 76, 168, 76), L(88, 116, 104, 116), L(136, 116, 168, 116),
             L(88, 156, 112, 156)])

# passkey: user + key
icon('passkey', SEC, ['passkey', 'login', 'user key', 'passwordless'],
     line=[C(96, 88, 36), P('M32 208 C32 168 60 148 96 148 C132 148 156 168 156 208'),
           C(192, 92, 28), L(192, 120, 192, 212), L(192, 180, 216, 180), L(192, 208, 212, 208)],
     area=[C(96, 88, 36), P('M32 208 C32 168 60 148 96 148 C132 148 156 168 156 208 Z'), C(192, 92, 28)],
     dotcut=[C(192, 92, 12)])

# police badge
PB = 'M128 36 C152 56 180 60 208 52 V120 C208 172 172 204 128 224 C84 204 48 172 48 120 V52 C76 60 104 56 128 36 Z'
PSTAR = PG([polar((128, 128), 44 if i % 2 == 0 else 18, -90 + i * 36) for i in range(10)])
icon('police-badge', SEC, ['police', 'sheriff', 'badge', 'law', 'officer'],
     line=[P(PB)], area=[P(PB)], detail=[PSTAR], hole=[PSTAR])

# scan smiley
icon('scan-smiley', SEC, ['face id', 'face scan', 'recognition', 'scan', 'smiley'],
     line=[PL([(32, 72), (32, 32), (72, 32)]), PL([(184, 32), (224, 32), (224, 72)]),
           PL([(224, 184), (224, 224), (184, 224)]), PL([(72, 224), (32, 224), (32, 184)]), C(128, 128, 60)],
     area=[C(128, 128, 60)], detail=[P('M100 144 A30 30 0 0 0 156 144')],
     dotcut=[C(106, 114, 12), C(150, 114, 12)])

# security camera
CAMC = (136, 88)
CAM_BODY = rotd(rect_d(64, 60, 144, 56, 12), 20, CAMC)
CAM_BAND = rotd('M184 60 L184 116', 20, CAMC)
CAM_ARM = 'M104 110 L104 168 L40 168'
CAM_WALL = 'M40 128 L40 208'
icon('security-camera', SEC, ['cctv', 'surveillance', 'camera', 'security', 'security camera'],
     line=[P(CAM_BODY), P(CAM_ARM), P(CAM_WALL)], area=[P(CAM_BODY)], detail=[P(CAM_BAND)])
icon('security-camera-slash', SEC, ['security camera', 'disabled', 'off', 'cctv', 'surveillance'],
     line=gapped(CAM_BODY) + gapped(CAM_ARM) + gapped(CAM_WALL) + gapped(CAM_BAND) + [L(48, 48, 208, 208)])

# security key
icon('security-key', SEC, ['hardware key', '2fa', 'usb key', 'authentication', 'fingerprint'],
     line=[R(96, 32, 64, 56, 6), R(64, 88, 128, 136, 24)], area=[R(96, 32, 64, 56, 6), R(64, 88, 128, 136, 24)],
     detail=[P('M96 184 V156 A32 32 0 0 1 160 156 V184'), L(128, 152, 128, 192)],
     dotcut=[C(116, 60, 8), C(140, 60, 8)])

# vault open
VB = R(80, 32, 144, 168, 16)
VIN = R(108, 60, 88, 112, 6)
DOOR = PG([(80, 32), (32, 56), (32, 176), (80, 200)])
icon('vault-open', SEC, ['open safe', 'unlocked vault', 'access', 'vault', 'safe'],
     line=[VB, DOOR, L(112, 200, 112, 216), L(192, 200, 192, 216)], area=[VB, DOOR], detail=[VIN], hole=[VIN],
     dotcut=[C(56, 116, 12)])

print(save(overwrite=True))
