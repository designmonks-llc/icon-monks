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



# ================================================================ batch 153 helpers
BC = (184, 184)


def rrect(x, y, w, h, r):
    return (f'M{f(x + r)} {f(y)} H{f(x + w - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w)} {f(y + r)} V{f(y + h - r)} '
            f'A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(y + h)} H{f(x + r)} A{f(r)} {f(r)} 0 0 1 {f(x)} {f(y + h - r)} '
            f'V{f(y + r)} A{f(r)} {f(r)} 0 0 1 {f(x + r)} {f(y)} Z')


def cut_open(d, R, c=BC):
    """Open every subpath of d around the badge circle (open paths simply stop short)."""
    out = []
    for segs, closed in parse(d):
        runs, whole = trim(segs, lambda p: dist(p, c) >= R, closed)
        if whole:
            out.append(P(segs_d(segs, closed)))
        else:
            out += [P(segs_d(r)) for r in runs if r]
    return out


def slash_all(ds, sg=30):
    out = []
    for d in ds:
        out += gapped(d, sg)
    return out + [SLASH]


# ================================================================ sliders (reuses the sliders geometry; badge rows rearranged)
SL = load('sliders')
SL_D = [d_of(e) if e.startswith('<path') else None for e in SL['line']]
SLIDER_TOP = [L(40, 80, 136, 80), C(160, 80, 24), L(184, 80, 216, 80)]
SLIDER_TOP_AREA = [C(160, 80, 24)]


def sliders_badge(name, tags, kind, R=56):
    bottom = [L(40, 176, 56, 176), C(80, 176, 24)]
    # track to the right of the knob stops short of the badge
    xr = BC[0] - math.sqrt(R * R - 8 * 8)
    if xr - 104 >= 12:
        bottom.append(L(104, 176, xr, 176))
    badge(name, tags, dict(line=SLIDER_TOP + bottom, area=SLIDER_TOP_AREA + [C(80, 176, 24)]), kind, BC)


for kind, tags, rad in [
    ('magnifying-glass', ['sliders', 'search', 'find', 'adjustments', 'controls'], 60),
    ('minus', ['sliders', 'remove', 'subtract', 'adjustments', 'controls'], 56),
    ('pause', ['sliders', 'paused', 'hold', 'adjustments', 'controls'], 56),
    ('plus', ['sliders', 'add', 'new', 'adjustments', 'controls'], 56),
    ('push-pin', ['sliders', 'pinned', 'pin', 'adjustments', 'controls'], 60),
    ('question', ['sliders', 'help', 'unknown', 'adjustments', 'controls'], 56),
    ('share', ['sliders', 'share', 'send', 'adjustments', 'controls'], 60),
    ('sparkle', ['sliders', 'ai', 'magic', 'adjustments', 'controls'], 60),
    ('star', ['sliders', 'favorite', 'starred', 'adjustments', 'controls'], 60),
    ('warning', ['sliders', 'warning', 'error', 'adjustments', 'controls'], 56),
    ('x', ['sliders', 'remove', 'cancel', 'adjustments', 'controls'], 56),
]:
    sliders_badge('sliders-' + kind, tags, kind, rad)

# knobs placed as in the badge variants so the slash clears them
sl_ds = ['M40 80 L136 80', 'M184 80 L216 80', 'M40 176 L56 176', 'M104 176 L216 176']
sl_knobs = [C(160, 80, 24), C(80, 176, 24)]
icon('sliders-slash', UI, ['sliders', 'disabled', 'off', 'adjustments', 'controls'], line=slash_all(sl_ds) + sl_knobs, area=sl_knobs)

# ================================================================ slideshow
SS = R(80, 48, 96, 160, 14)
icon('slideshow', UI, ['slides', 'gallery', 'image viewer', 'presentation', 'slideshow'],
     line=[SS, PL([(52, 100), (32, 128), (52, 156)]), PL([(204, 100), (224, 128), (204, 156)])],
     detail=[PL([(88, 194), (116, 162), (164, 204)])], area=[SS], dotcut=[C(146, 92, 12)])

# ================================================================ sort
BARS_UP = [L(40, 56, 80, 56), L(40, 104, 104, 104), L(40, 152, 128, 152), L(40, 200, 152, 200)]
icon('sort-ascending', UI, ['sort', 'ascending', 'order', 'arrange', 'list'],
     line=BARS_UP + [L(192, 216, 192, 48), PL([(160, 80), (192, 48), (224, 80)])])
BARS_DN = [L(40, 56, 152, 56), L(40, 104, 128, 104), L(40, 152, 104, 152), L(40, 200, 80, 200)]
icon('sort-descending', UI, ['sort', 'descending', 'order', 'arrange', 'sort descending'],
     line=BARS_DN + [L(192, 40, 192, 208), PL([(160, 176), (192, 208), (224, 176)])])

# ================================================================ spacebar
SPACE_D = 'M40 96 L40 168 L216 168 L216 96'
icon('spacebar', UI, ['space', 'spacebar', 'keyboard', 'blank', 'space bar'], line=[P(SPACE_D)])
icon('spacebar-slash', UI, ['spacebar', 'off', 'disabled', 'hidden'], line=slash_all([SPACE_D]))

# ================================================================ spaces
BACK_D = rrect(32, 48, 128, 128, 14)
FRONT_R = (96, 80, 128, 128)
back_runs, _ = trim(parse(BACK_D)[0][0],
                    lambda p: not (FRONT_R[0] - 30 < p[0] < FRONT_R[0] + FRONT_R[2] + 30 and
                                   FRONT_R[1] - 30 < p[1] < FRONT_R[1] + FRONT_R[3] + 30))
icon('spaces', UI, ['spaces', 'workspaces', 'desktops', 'areas'],
     line=[R(*FRONT_R, 14)] + [P(segs_d(r)) for r in back_runs],
     area=[R(*FRONT_R, 14)])

# ================================================================ sparkle slash
SPARK_D = d_of(load('sparkle')['line'][0])
icon('sparkle-slash', UI, ['sparkle', 'off', 'disabled', 'hidden'], line=slash_all([SPARK_D]))

# ================================================================ split
SQ = R(32, 32, 192, 192, 16)
icon('split-horizontal', UI, ['split view', 'side by side', 'panes'],
     line=[SQ], area=[SQ],
     detail=[L(128, 32, 128, 224), PL([(88, 100), (64, 128), (88, 156)]), PL([(168, 100), (192, 128), (168, 156)])])
icon('split-vertical', UI, ['split view', 'stacked', 'panes'],
     line=[SQ], area=[SQ],
     detail=[L(32, 128, 224, 128), PL([(100, 88), (128, 64), (156, 88)]), PL([(100, 168), (128, 192), (156, 168)])])
icon('square-slash', UI, ['square', 'off', 'disabled', 'hidden'], line=slash_all([rrect(32, 32, 192, 192, 16)]))
icon('square-split-horizontal', UI, ['two columns', 'split', 'layout', 'toggle', 'half'],
     line=[SQ], area=[SQ], detail=[L(128, 32, 128, 224)])
icon('square-split-vertical', UI, ['two rows', 'split', 'layout', 'toggle', 'half'],
     line=[SQ], area=[SQ], detail=[L(32, 128, 224, 128)])

# ================================================================ squares four
Q3 = [R(40, 40, 72, 72, 10), R(144, 40, 72, 72, 10), R(40, 144, 72, 72, 10)]
icon('squares-four-minus', UI, ['remove grid', 'delete cell', 'grid'], line=Q3 + [L(148, 180, 212, 180)], area=Q3)
icon('squares-four-plus', UI, ['add widget', 'dashboard', 'grid', 'create', 'apps'],
     line=Q3 + [L(148, 180, 212, 180), L(180, 148, 180, 212)], area=Q3)
icon('squares-four-x', UI, ['remove grid', 'clear grid', 'close grid'],
     line=Q3 + [L(156, 156, 204, 204), L(204, 156, 156, 204)], area=Q3)
icon('squares-four-slash', UI, ['hide grid', 'grid off', 'layout', 'disabled'],
     line=slash_all([rrect(40, 40, 72, 72, 10), rrect(144, 40, 72, 72, 10), rrect(40, 144, 72, 72, 10),
                     rrect(144, 144, 72, 72, 10)]))
SQL = [R(40, 48, 32, 32, 8), R(40, 112, 32, 32, 8), R(40, 176, 32, 32, 8)]
icon('squares-list', UI, ['apps', 'list', 'grid', 'menu'],
     line=SQL + [L(104, 64, 216, 64), L(104, 128, 216, 128), L(104, 192, 192, 192)], area=SQL)

# ================================================================ star
STAR_D = d_of(load('star')['line'][0])
STAR_PTS = [s[1] for s in parse(STAR_D)[0][0]]
dash = []
for i, v in enumerate(STAR_PTS):
    a, b = STAR_PTS[i - 1], STAR_PTS[(i + 1) % len(STAR_PTS)]
    ua = ((a[0] - v[0]) / dist(a, v), (a[1] - v[1]) / dist(a, v))
    ub = ((b[0] - v[0]) / dist(b, v), (b[1] - v[1]) / dist(b, v))
    k = 17
    dash.append(PL([(v[0] + ua[0] * k, v[1] + ua[1] * k), v, (v[0] + ub[0] * k, v[1] + ub[1] * k)]))
icon('star-dashed', UI, ['unrated', 'empty star', 'star outline'], line=dash, area=[P(STAR_D)])
icon('star-slash', UI, ['unfavourite', 'star off', 'unstar', 'slash'], line=slash_all([STAR_D]))

# ================================================================ status change
icon('status-change', UI, ['status change', 'transition', 'state', 'progress'],
     line=[C(72, 184, 32), C(184, 72, 32), L(110, 146, 150, 106), PL([(124, 106), (150, 106), (150, 132)])],
     area=[C(184, 72, 32)])

# ================================================================ sun +/-
SUN_LINE = [C(128, 128, 52)] + [L(*polar((128, 128), 76, i * 45), *polar((128, 128), 96, i * 45)) for i in range(8)]
icon('sun-minus', UI, ['brightness down', 'dim', 'display', 'sun'],
     line=SUN_LINE, detail=[L(104, 128, 152, 128)], area=[C(128, 128, 52)])
icon('sun-plus', UI, ['brightness up', 'brighter', 'display', 'sun'],
     line=SUN_LINE, detail=[L(104, 128, 152, 128), L(128, 104, 128, 152)], area=[C(128, 128, 52)])

# ================================================================ swap
SW = [R(32, 32, 72, 72, 12), R(152, 152, 72, 72, 12)]
sc, sr = (148, 108), 48
s0, s1 = polar(sc, sr, -90), polar(sc, sr, 0)
HEAD = [(s1[0] - 20, s1[1] - 20), s1, (s1[0] + 20, s1[1] - 20)]
arc1 = P(f'M{pt(s0)} A{sr} {sr} 0 0 1 {pt(s1)}')
head1 = PL(HEAD)
arc2_pts = rot([s0, s1], 180)
head2 = PL(rot(HEAD, 180))
arc2 = P(f'M{pt(arc2_pts[0])} A{sr} {sr} 0 0 1 {pt(arc2_pts[1])}')
icon('swap', UI, ['replace', 'swap', 'exchange', 'switch', 'flip'], line=SW + [arc1, head1, arc2, head2], area=SW)

# ================================================================ swipe (a compact pointing hand, fingers r16)
def hand(dx, dy=0):
    T = lambda x, y: pt((x + dx, y + dy))
    d = (f'M{T(96, 165.4)} V{f(108 + dy)} A16 16 0 0 1 {T(128, 108)} V{f(150 + dy)} A16 16 0 0 1 {T(160, 150)} '
         f'V{f(154 + dy)} A16 16 0 0 1 {T(192, 154)} V{f(176 + dy)} C{T(192, 204)} {T(174, 224)} {T(148, 224)} '
         f'H{f(138 + dx)} C{T(120, 224)} {T(100, 216)} {T(85.5, 203.5)} L{T(55.5, 166)} '
         f'A16 16 0 0 1 {T(80.5, 146)} Z')
    return dict(line=[P(d)], area=[P(d)], detail=[L(160 + dx, 150 + dy, 160 + dx, 178 + dy)])


def swipe(name, tags, h, arrows):
    icon(name, UI, tags, line=h['line'] + arrows, area=h['area'], detail=h['detail'])


hh = hand(8)
swipe('swipe', ['swipe', 'gesture', 'touch', 'finger'], hh,
      [L(56, 52, 200, 52), PL([(72, 32), (52, 52), (72, 72)]), PL([(184, 32), (204, 52), (184, 72)])])
swipe('swipe-left', ['swipe left', 'gesture', 'touch', 'scroll'], hh,
      [L(200, 52, 56, 52), PL([(76, 32), (56, 52), (76, 72)])])
swipe('swipe-right', ['swipe right', 'gesture', 'touch', 'scroll'], hh,
      [L(56, 52, 200, 52), PL([(180, 32), (200, 52), (180, 72)])])
hv = hand(-16)
swipe('swipe-up', ['swipe up', 'gesture', 'touch', 'scroll'], hv,
      [L(208, 136, 208, 44), PL([(188, 64), (208, 44), (228, 64)])])
swipe('swipe-down', ['swipe down', 'gesture', 'touch', 'scroll'], hv,
      [L(208, 44, 208, 136), PL([(188, 116), (208, 136), (228, 116)])])

# ================================================================ tab
TAB_D = 'M32 184 H48 A12 12 0 0 0 60 172 V80 A16 16 0 0 1 76 64 H180 A16 16 0 0 1 196 80 V172 A12 12 0 0 0 208 184 H224'
TAB_A = 'M48 184 A12 12 0 0 0 60 172 V80 A16 16 0 0 1 76 64 H180 A16 16 0 0 1 196 80 V172 A12 12 0 0 0 208 184 Z'
icon('tab', UI, ['tab', 'browser tab', 'window', 'page'], line=[P(TAB_D)], area=[P(TAB_A)])
icon('tab-x', UI, ['close tab', 'browser tab', 'remove', 'x'], line=[P(TAB_D)], area=[P(TAB_A)],
     detail=[L(108, 104, 148, 144), L(148, 104, 108, 144)])

TABS_D = ('M32 54 A14 14 0 0 1 46 40 H82 A14 14 0 0 1 96 54 V88 H210 A14 14 0 0 1 224 102 V202 '
          'A14 14 0 0 1 210 216 H46 A14 14 0 0 1 32 202 Z')
T2 = 'M96 54 A14 14 0 0 1 110 40 H146 A14 14 0 0 1 160 54 V88'
T3 = 'M160 54 A14 14 0 0 1 174 40 H210 A14 14 0 0 1 224 54 V88'
icon('tabs', UI, ['tabs', 'browser tabs', 'tab group', 'windows', 'multiple'],
     line=[P(TABS_D), P(T2), P(T3)], area=[P(TABS_D), P(T2 + ' Z'), P(T3 + ' Z')],
     detail=[L(96, 88, 224, 88)])

# ================================================================ table
TB = load('table')
TB_D = rrect(32, 48, 192, 160, 14)
TB_DET = ['M32 96 L224 96', 'M32 152 L224 152', 'M96 96 L96 208']


def table_badge(name, tags, kind, R):
    segs = parse(TB_D)[0][0]
    runs, _ = trim(segs, lambda p: dist(p, BC) >= R, True)
    run = runs[0]
    s, e = seg_point(run[0], 0), seg_end(run[-1])
    area = P(segs_d(run) + ' ' + arc_to(BC, R, e, s, lambda m: -dist(m, (128, 128))) + ' Z')
    det = []
    for d in TB_DET:
        det += cut_open(d, R + 4)
    badge(name, tags, dict(line=[P(segs_d(run))], area=[area], detail=det), kind, BC)


table_badge('table-arrow-down', ['table', 'download', 'down', 'decrease'], 'arrow-down', 52)
table_badge('table-heart', ['table', 'favorite', 'like', 'love'], 'heart', 56)
table_badge('table-share', ['table', 'share', 'send'], 'share', 58)
table_badge('table-sparkle', ['table', 'ai', 'magic', 'smart'], 'sparkle', 58)
icon('table-slash', UI, ['table', 'off', 'disabled', 'hidden'], line=slash_all([TB_D] + TB_DET))

FREEZE_AREA = 'M46 48 H210 A14 14 0 0 1 224 62 V96 H96 V208 H46 A14 14 0 0 1 32 194 V62 A14 14 0 0 1 46 48 Z'
icon('table-freeze', UI, ['freeze panes', 'table', 'spreadsheet', 'lock column'],
     line=TB['line'] + [L(32, 96, 224, 96), L(96, 96, 96, 208), L(96, 152, 224, 152)],
     detail=[L(32, 152, 96, 152)], area=[P(FREEZE_AREA)])

# freeze column: first column shaded, a padlock badge in the lower right
R_LOCK = 60
segs = parse(TB_D)[0][0]
runs, _ = trim(segs, lambda p: dist(p, BC) >= R_LOCK, True)
tline = P(segs_d(runs[0]))
LOCK_BODY = R(156, 176, 56, 40, 8)
SHACKLE = P('M168 176 V164 A16 16 0 0 1 200 164 V176')
COL_AREA = P('M46 48 H96 V208 H46 A14 14 0 0 1 32 194 V62 A14 14 0 0 1 46 48 Z')
icon('table-freeze-column', 'Editor', ['freeze column', 'table', 'pin column', 'spreadsheet'],
     line=[tline, L(96, 48, 96, 208), LOCK_BODY, SHACKLE] + cut_open('M96 96 L224 96', R_LOCK + 4)
     + cut_open('M96 152 L224 152', R_LOCK + 4),
     detail=[L(32, 96, 96, 96), L(32, 152, 96, 152)], area=[COL_AREA, LOCK_BODY])

# ================================================================ tag slash
TAG_D = d_of(load('tag')['line'][0])
icon('tag-slash', UI, ['tag', 'off', 'disabled', 'hidden'], line=slash_all([TAG_D]))

# ================================================================ tooltip
TT = 'M46 48 H210 A14 14 0 0 1 224 62 V162 A14 14 0 0 1 210 176 H156 L128 208 L100 176 H46 A14 14 0 0 1 32 162 V62 A14 14 0 0 1 46 48 Z'
icon('tooltip', UI, ['tooltip', 'hint', 'popover', 'callout', 'bubble'],
     line=[P(TT)], area=[P(TT)], detail=[L(72, 96, 184, 96), L(72, 128, 152, 128)])

print(save(overwrite=True))
