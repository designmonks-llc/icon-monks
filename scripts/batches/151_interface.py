import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

UI = 'Interface'
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


# ================================================================ badge marks (same set as the flag/funnel/gear badges of batches 149-150)
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
    icon(name, UI, tags,
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

# ================================================================ gear badges (same base as gear-check / gear-sparkle)
gear = load('gear')
GEAR_D = d_of(gear['line'][0])
GS, GC = 0.875, (116, 116)
GEAR_S = scaled(GEAR_D, GS, (128, 128), GC)
gear_ln, gear_ar = carve(GEAR_S, BADGE, 60)
gear_base = dict(line=[gear_ln, C(GC[0], GC[1], 24)], area=[gear_ar], hole=[C(GC[0], GC[1], 16)])
for kind, suffix, tags in [
    ('star', 'star', ['gear', 'favorite', 'starred', 'featured']),
    ('warning', 'warning', ['gear', 'warning', 'alert', 'error']),
    ('x', 'x', ['gear x', 'remove', 'cancel', 'settings', 'gear']),
]:
    badge('gear-' + suffix, tags, gear_base, kind, BADGE)

# ================================================================ heart
heart = load('heart')
HEART_D = d_of(heart['line'][0])
HS, HC = 0.875, (118, 120)
HEART_S = scaled(HEART_D, HS, (128, 136), HC)
heart_ln, heart_ar = carve(HEART_S, BADGE, 60)
heart_base = dict(line=[heart_ln], area=[heart_ar])
for kind, suffix, tags in [
    ('bitcoin', 'bitcoin', ['heart', 'bitcoin', 'crypto']),
    ('check', 'check', ['heart check', 'done', 'approved', 'heart', 'favorite']),
    ('code', 'code', ['heart', 'code', 'developer', 'embed']),
    ('dollar', 'currency-dollar', ['heart', 'dollar', 'price', 'money']),
    ('percent', 'discount', ['heart', 'discount', 'sale', 'percent']),
    ('gear', 'gear', ['heart', 'settings', 'configure']),
    ('lightning', 'lightning', ['heart', 'fast', 'power', 'instant']),
    ('magnifying-glass', 'magnifying-glass', ['heart', 'search', 'find']),
    ('minus', 'minus', ['heart minus', 'remove', 'subtract', 'heart', 'favorite']),
    ('pause', 'pause', ['heart', 'paused', 'hold']),
    ('plus', 'plus', ['add favourite', 'like', 'heart', 'plus']),
    ('push-pin', 'push-pin', ['heart', 'pin', 'pinned']),
    ('share', 'share', ['heart', 'share', 'send']),
    ('sparkle', 'sparkle', ['heart', 'ai', 'magic', 'smart']),
    ('star', 'star', ['heart', 'favorite', 'starred', 'featured']),
    ('warning', 'warning', ['heart', 'warning', 'alert', 'error']),
    ('x', 'x', ['heart x', 'remove', 'cancel', 'heart', 'favorite']),
]:
    badge('heart-' + suffix, tags, heart_base, kind, BADGE)

icon('heart-slash', UI, ['heart slash', 'off', 'disabled', 'heart', 'favorite'], line=gapped(HEART_D) + [SLASH])
icon('heart-half', UI, ['half heart', 'rating', 'health', 'love'],
     line=[P(HEART_D), L(128, 80, 128, 210)],
     area=[P('M128 212 C128 212 32 160 32 98 A50 50 0 0 1 128 78 Z')])
HEART_IN = scaled(HEART_D, 0.5, (128, 136), (128, 130))
icon('heart-circle', UI, ['heart circle', 'heart', 'circle', 'interface'],
     line=[C(128, 128, 96)], detail=[P(HEART_IN)], area=[C(128, 128, 96)])

# ================================================================ globe
icon('globe-slash', UI, ['offline', 'no internet', 'web off', 'globe', 'public off'],
     line=gapped(circle_d(128, 128, 96)) + gapped(ellipse_d(128, 128, 40, 96)) + gapped('M32 128 L224 128')
     + [SLASH])

# ================================================================ hands
HAND_D = d_of(load('hand')['line'][0])
HD = 0.56
HAND_S = scaled(HAND_D, HD, (130, 132), (128, 128))
icon('hand-drag', UI, ['drag', 'move', 'grab', 'pan'],
     line=[P(HAND_S), PL([(108, 52), (128, 32), (148, 52)]), PL([(108, 204), (128, 224), (148, 204)]),
           PL([(52, 108), (32, 128), (52, 148)]), PL([(204, 108), (224, 128), (204, 148)])],
     area=[P(HAND_S)])

# pinch: palm in the lower left, index finger and thumb reaching to the upper right with their tips nearly touching
import build as _b  # noqa: E402  (pathops union, only to merge the three simple shapes into one outline)


def cap_d(a, b, r):
    d = dist(a, b)
    u = ((b[0] - a[0]) / d, (b[1] - a[1]) / d)
    return capsule(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), d / 2, r, u)


def merged(*ds):
    return _b.to_d(_b.union(*[_b.to_path([d]) for d in ds]))


FIST_D = d_of(load('hand-grabbing')['line'][0])
PINCH = merged(FIST_D, cap_d((94, 132), (82, 58), 18), cap_d((70, 164), (50, 104), 18))
icon('hand-pinch', UI, ['pinch', 'zoom gesture', 'touch', 'gesture'], line=[P(PINCH)],
     detail=[L(148, 106, 148, 150), L(184, 114, 184, 150)], area=[P(PINCH)])

# tap: the pointing hand moved down and cropped by the live area, ripples above its fingertip
pointing = load('hand-pointing')
PT_D = d_of(pointing['line'][0])
DY = 50
PT_S = tf_path(normalize(PT_D), lambda p: (p[0], p[1] + DY))
segs = parse(PT_S)[0][0]
runs, _ = trim(segs, lambda p: p[1] <= 224)
assert len(runs) == 1
TAP_LN = segs_d(runs[0])
TAP_AR = TAP_LN + ' Z'
TAP_DET = [L(148, 116 + DY, 148, 150 + DY), L(184, 122 + DY, 184, 150 + DY)]
TIP = (94, 58 + DY)
tap_ticks = [L(*polar(TIP, 44, a), *polar(TIP, 68, a)) for a in (220, 270, 320)]
def ripple(r, a0, a1):
    return P(f'M{pt(polar(TIP, r, a0))} A{r} {r} 0 0 1 {pt(polar(TIP, r, a1))}')
icon('hand-tap', UI, ['tap', 'touch', 'gesture', 'click', 'select'],
     line=[P(TAP_LN)] + tap_ticks, detail=TAP_DET, area=[P(TAP_AR)])
icon('hand-tap-double', UI, ['double tap', 'touch', 'gesture', 'tap'],
     line=[P(TAP_LN), ripple(44, 215, 325), ripple(76, 220, 320)], detail=TAP_DET, area=[P(TAP_AR)])
icon('hand-tap-slash', UI, ['hand tap', 'off', 'disabled', 'hidden', 'hand'],
     line=gapped(TAP_LN) + sum((gapped(d_of(t)) for t in tap_ticks + TAP_DET), []) + [SLASH])

# ================================================================ import
icon('import', UI, ['import', 'arrow in', 'tray', 'load'],
     line=[P('M88 112 H72 A16 16 0 0 0 56 128 V200 A16 16 0 0 0 72 216 H184 A16 16 0 0 0 200 200 V128 '
             'A16 16 0 0 0 184 112 H168'), L(128, 32, 128, 176), PL([(96, 144), (128, 176), (160, 144)])])

# ================================================================ info
icon('info-slash', UI, ['info off', 'hide info', 'information'],
     line=gapped(circle_d(128, 128, 96)) + gapped('M128 120 L128 176') + [SLASH], dot=[C(128, 84, 16)])
icon('info-square', UI, ['info', 'information', 'about', 'square'],
     line=[R(32, 32, 192, 192, 16)], detail=[L(128, 120, 128, 176)], area=[R(32, 32, 192, 192, 16)],
     dotcut=[C(128, 84, 16)])

# ================================================================ keys
kc, kr = (100, 156), 28
ku = (1 / math.sqrt(2), -1 / math.sqrt(2)); kn = (1 / math.sqrt(2), 1 / math.sqrt(2))
k0 = (kc[0] + ku[0] * kr, kc[1] + ku[1] * kr)
teeth = [(164, 92), (140, 116)]
icon('key-circle', UI, ['key circle', 'key', 'circle', 'interface'],
     line=[C(128, 128, 96)],
     detail=[C(kc[0], kc[1], kr), L(k0[0], k0[1], 176, 80)] + [L(x, y, x + kn[0] * 22, y + kn[1] * 22) for x, y in teeth],
     area=[C(128, 128, 96)])
shift = [(128, 36), (220, 132), (172, 132), (172, 216), (84, 216), (84, 132), (36, 132)]
icon('key-shift', UI, ['shift key', 'keyboard', 'uppercase', 'arrow'], line=[PG(shift)], area=[PG(shift)])

# ================================================================ layouts
icon('layout-board', UI, ['board layout', 'dashboard', 'panels', 'grid'],
     line=[R(40, 40, 64, 176, 12), R(136, 40, 80, 80, 12), R(136, 152, 80, 64, 12)],
     area=[R(40, 40, 64, 176, 12), R(136, 40, 80, 80, 12), R(136, 152, 80, 64, 12)])
icon('layout-grid', UI, ['grid layout', 'tiles', 'dashboard', 'panels'],
     line=[R(40, 40, 72, 72, 12), R(144, 40, 72, 72, 12), R(40, 144, 72, 72, 12), R(144, 144, 72, 72, 12)],
     area=[R(40, 40, 72, 72, 12), R(144, 40, 72, 72, 12), R(40, 144, 72, 72, 12), R(144, 144, 72, 72, 12)])
icon('layout-masonry', UI, ['layout', 'masonry', 'grid', 'pinterest'],
     line=[R(40, 40, 72, 104, 12), R(40, 176, 72, 40, 12), R(144, 40, 72, 40, 12), R(144, 112, 72, 104, 12)],
     area=[R(40, 40, 72, 104, 12), R(40, 176, 72, 40, 12), R(144, 40, 72, 40, 12), R(144, 112, 72, 104, 12)])
icon('layout-cards', UI, ['cards', 'layout', 'tiles', 'panels'],
     line=[R(32, 40, 192, 72, 14), R(32, 144, 192, 72, 14)],
     detail=[L(68, 76, 148, 76), L(68, 180, 148, 180)],
     area=[R(32, 40, 192, 72, 14), R(32, 144, 192, 72, 14)])
icon('layout-list', UI, ['list layout', 'rows', 'view', 'panels'],
     line=[R(40, 48, 64, 64, 12), R(40, 144, 64, 64, 12),
           L(136, 64, 216, 64), L(136, 96, 192, 96), L(136, 160, 216, 160), L(136, 192, 192, 192)],
     area=[R(40, 48, 64, 64, 12), R(40, 144, 64, 64, 12)])
SCREEN = R(32, 48, 192, 160, 14)
icon('layout-top-bar', UI, ['header', 'top bar', 'navigation', 'layout', 'navbar'],
     line=[SCREEN, L(32, 96, 224, 96)], area=[P('M32 96 V62 A14 14 0 0 1 46 48 H210 A14 14 0 0 1 224 62 V96 Z')])
icon('layout-bottom-bar', UI, ['bottom bar', 'tab bar', 'navigation', 'layout', 'footer'],
     line=[SCREEN, L(32, 160, 224, 160)], area=[P('M32 160 V194 A14 14 0 0 0 46 208 H210 A14 14 0 0 0 224 194 V160 Z')])
icon('line-vertical', UI, ['divider', 'separator', 'vertical line'], line=[L(128, 32, 128, 224)])

# ================================================================ links
LINK_D = [d_of(e) for e in load('link')['line']]
cpy_front = R(72, 72, 152, 152, 14)
lc = (148, 148)
icon('link-copy', UI, ['copy link', 'url', 'share', 'clipboard'],
     line=[cpy_front, P('M168 72 V48 A16 16 0 0 0 152 32 H48 A16 16 0 0 0 32 48 V152 A16 16 0 0 0 48 168 H72')],
     detail=[P(capsule((lc[0] - 20 * ku[0], lc[1] - 20 * ku[1]), 16, 18, ku)),
             P(capsule((lc[0] + 20 * ku[0], lc[1] + 20 * ku[1]), 16, 18, ku))],
     area=[cpy_front])
LS, LC = 0.82, (112, 112)
link_small = [P(scaled(d, LS, (128, 128), LC)) for d in LINK_D]
icon('link-plus', UI, ['add link', 'new link', 'hyperlink', 'url', 'insert link'],
     line=link_small + marks('plus', BADGE)['line'])
icon('link-minus', UI, ['remove link', 'unlink', 'chain', 'url'],
     line=link_small + marks('minus', BADGE)['line'])

# ================================================================ lists
icon('list-dropdown', UI, ['dropdown', 'select', 'menu', 'list'],
     line=[L(40, 64, 140, 64), L(40, 128, 140, 128), L(40, 192, 140, 192), PL([(172, 116), (196, 140), (220, 116)])])
HEART_L = scaled(HEART_D, 0.42, (128, 126), (183, 164))
icon('list-heart', UI, ['favorites list', 'wishlist', 'liked'],
     line=[L(40, 64, 216, 64), L(40, 128, 112, 128), L(40, 192, 112, 192), P(HEART_L)], area=[P(HEART_L)])
icon('list-magnifying-glass', UI, ['search list', 'find item', 'filter', 'manage search', 'find'],
     line=[L(40, 64, 216, 64), L(40, 128, 88, 128), L(40, 192, 88, 192), C(160, 152, 40), L(189, 181, 212, 204)],
     area=[C(160, 152, 40)])

# ================================================================ lock
icon('lock-open-slash', UI, ['lock open', 'off', 'disabled', 'hidden', 'lock'],
     line=gapped(rect_d(48, 104, 160, 112, 14)) + gapped('M88 104 V72 A40 40 0 0 1 166 60') + [SLASH])

# ================================================================ magnifying glass
MG = load('magnifying-glass')
icon('magnifying-glass-check', UI, ['found', 'search result', 'match', 'verified', 'magnifying glass check'],
     line=MG['line'], detail=[PL([(82, 114), (104, 136), (144, 94)])], area=MG['area'])
icon('magnifying-glass-code', UI, ['magnifying glass', 'code', 'developer', 'embed', 'magnifying'],
     line=MG['line'], detail=marks('code', (112, 112))['line'], area=MG['area'])
EYE = scaled('M24 128 C56 72 96 56 128 56 C160 56 200 72 232 128 C200 184 160 200 128 200 C96 200 56 184 24 128 Z',
             0.42, (128, 128), (112, 112))
icon('magnifying-glass-eye', UI, ['visual search', 'inspect', 'look', 'find'],
     line=MG['line'], detail=[P(EYE)], area=MG['area'], dotcut=[C(112, 112, 12)])

print(save(overwrite=True))
