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


# ================================================================ badge marks (same set as the flag/eye badges of batch 149)
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


# ================================================================ flag
flag = load('flag')
POLE = flag['line'][0]
FLAG_D = d_of(flag['line'][1])
FB, FRC = (184, 184), 60
flag_ln, flag_ar = carve(FLAG_D, FB, FRC)
flag_base = dict(line=[POLE, flag_ln], area=[flag_ar])

for kind, suffix, tags in [
    ('pause', 'pause', ['flag', 'paused', 'hold']),
    ('plus', 'plus', ['flag plus', 'add', 'new', 'flag', 'report']),
    ('push-pin', 'push-pin', ['flag', 'pin', 'pinned']),
    ('question', 'question', ['flag', 'help', 'unknown', 'question']),
    ('share', 'share', ['flag', 'share', 'send']),
    ('sparkle', 'sparkle', ['flag', 'ai', 'magic', 'smart']),
    ('star', 'star', ['flag', 'favorite', 'starred', 'featured']),
    ('warning', 'warning', ['flag', 'warning', 'alert', 'error']),
    ('x', 'x', ['flag x', 'remove', 'cancel', 'flag', 'report']),
]:
    badge('flag-' + suffix, tags, flag_base, kind, FB)

icon('flag-slash', UI, ['unflag', 'flag off', 'no flag', 'slash'],
     line=[POLE] + gapped(FLAG_D, 26) + [SLASH])

# ================================================================ funnel
FUNNEL_D = d_of(load('funnel')['line'][0])
# badge variants: the funnel scaled 0.8 towards the top left so its stem stays whole beside the badge
US, UC = 0.8, (109, 115)
FUNNEL_S = poly(tf([(32, 48), (224, 48), (152, 136), (152, 200), (104, 224), (104, 136)], US, (128, 136), UC), True)
UB = (184, 184)
funnel_base = dict(line=[P(FUNNEL_S)], area=[P(FUNNEL_S)])

for kind, suffix, tags in [
    ('arrow-down', 'arrow-down', ['funnel', 'download', 'down', 'decrease']),
    ('arrow-up', 'arrow-up', ['funnel', 'upload', 'up', 'increase']),
    ('check', 'check', ['funnel check', 'done', 'approved', 'filter', 'funnel']),
    ('code', 'code', ['funnel', 'code', 'developer', 'embed']),
    ('dollar', 'currency-dollar', ['funnel', 'dollar', 'price', 'money']),
    ('percent', 'discount', ['funnel', 'discount', 'sale', 'percent']),
    ('gear', 'gear', ['funnel', 'settings', 'configure']),
    ('heart', 'heart', ['funnel', 'favorite', 'like', 'love']),
    ('lightning', 'lightning', ['funnel', 'fast', 'power', 'instant']),
    ('magnifying-glass', 'magnifying-glass', ['funnel', 'search', 'find']),
    ('minus', 'minus', ['funnel minus', 'remove', 'subtract', 'filter', 'funnel']),
    ('pause', 'pause', ['funnel', 'paused', 'hold']),
    ('pencil', 'pencil', ['funnel', 'edit', 'write']),
    ('plus', 'plus', ['funnel plus', 'add', 'new', 'filter', 'funnel']),
    ('push-pin', 'push-pin', ['funnel', 'pin', 'pinned']),
    ('question', 'question', ['funnel', 'help', 'unknown', 'question']),
    ('share', 'share', ['funnel', 'share', 'send']),
    ('sparkle', 'sparkle', ['funnel', 'ai', 'magic', 'smart']),
    ('star', 'star', ['funnel', 'favorite', 'starred', 'featured']),
    ('warning', 'warning', ['funnel', 'warning', 'alert', 'error']),
]:
    badge('funnel-' + suffix, tags, funnel_base, kind, UB)

icon('funnel-slash', UI, ['filter off', 'clear filter', 'funnel', 'remove', 'no filter'],
     line=gapped(FUNNEL_D) + [SLASH])

icon('funnel-lines', UI, ['filter', 'refine', 'sort', 'list'],
     line=[L(40, 72, 216, 72), L(76, 128, 180, 128), L(112, 184, 144, 184)])
icon('funnel-x', UI, ['clear filter', 'remove filter', 'reset', 'funnel x', 'remove'],
     line=[L(32, 64, 184, 64), L(64, 120, 152, 120), L(96, 176, 120, 176)] + marks('x', (184, 184))['line'])

# ================================================================ gear
gear = load('gear')
GEAR_D = d_of(gear['line'][0])
# badge variants: the gear scaled 0.875 and nudged up-left (like the eye badges), opened around the badge
GS, GC = 0.875, (116, 116)
GEAR_S = tf_path(GEAR_D, lambda p: tf([p], GS, (128, 128), GC)[0], GS)
GB, GRC = (184, 184), 60
gear_ln, gear_ar = carve(GEAR_S, GB, GRC)
gear_base = dict(line=[gear_ln, C(GC[0], GC[1], 24)], area=[gear_ar], hole=[C(GC[0], GC[1], 16)])

for kind, suffix, tags in [
    ('arrow-down', 'arrow-down', ['gear', 'download', 'down', 'decrease']),
    ('arrow-up', 'arrow-up', ['gear', 'upload', 'up', 'increase']),
    ('check', 'check', ['gear check', 'done', 'approved', 'settings', 'gear']),
    ('code', 'code', ['gear', 'code', 'developer', 'embed']),
    ('dollar', 'currency-dollar', ['gear', 'dollar', 'price', 'money']),
    ('heart', 'heart', ['gear', 'favorite', 'like', 'love']),
    ('lightning', 'lightning', ['gear', 'fast', 'power', 'instant']),
    ('magnifying-glass', 'magnifying-glass', ['gear', 'search', 'find']),
    ('minus', 'minus', ['gear minus', 'remove', 'subtract', 'settings', 'gear']),
    ('pause', 'pause', ['gear', 'paused', 'hold']),
    ('plus', 'plus', ['gear plus', 'add', 'new', 'settings', 'gear']),
    ('push-pin', 'push-pin', ['gear', 'pin', 'pinned']),
    ('question', 'question', ['gear', 'help', 'unknown', 'question']),
    ('share', 'share', ['gear', 'share', 'send']),
    ('sparkle', 'sparkle', ['gear', 'ai', 'magic', 'smart']),
]:
    badge('gear-' + suffix, tags, gear_base, kind, GB)

play = PG([(114, 100), (156, 128), (114, 156)])
icon('gear-play', UI, ['automation', 'run settings', 'process', 'workflow'],
     line=[gear['line'][0]], area=gear['area'], detail=[play], hole=[play])

icon('gear-slash', UI, ['gear', 'off', 'disabled', 'hidden'],
     line=gapped(GEAR_D) + gapped(circle_d(128, 128, 28)) + [SLASH])

# ================================================================ gauge
gauge = load('gauge')
GAUGE_D = d_of(gauge['line'][0])
icon('gauge-slash', UI, ['gauge', 'off', 'disabled', 'hidden'],
     line=gapped(GAUGE_D) + gapped('M128 148 L168 96', 26) + [SLASH])

# ================================================================ form
icon('form', UI, ['form', 'input fields', 'survey', 'application', 'input'],
     line=[R(32, 40, 192, 176, 16)],
     detail=[L(64, 94, 84, 94), R(112, 76, 80, 36, 8), L(64, 162, 84, 162), R(112, 144, 80, 36, 8)],
     area=[R(32, 40, 192, 176, 16)])

print(save(overwrite=True))
