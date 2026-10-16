import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

UI = 'Interface'
SLASH = L(48, 48, 208, 208)


# ---------------------------------------------------------------- path tools (absolute M/L/H/V/C/Z only)
def parse(d):
    """Return a list of subpaths; each subpath is (segments, closed). Segments: ('L', p0, p1) or ('C', p0, c1, c2, p1)."""
    toks = re.findall(r'[A-Za-z]|-?\d+(?:\.\d+)?', d)
    subs, segs, cur, start, i, cmd = [], [], None, None, 0, None
    closed = False
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd == 'Z':
                if dist(cur, start) > 1e-6:
                    segs.append(('L', cur, start))
                cur = start
                closed = True
            continue
        if cmd == 'M':
            if segs:
                subs.append((segs, closed))
            segs, closed = [], False
            cur = start = (float(toks[i]), float(toks[i + 1]))
            i += 2
            cmd = 'L'
        elif cmd == 'L':
            p = (float(toks[i]), float(toks[i + 1])); i += 2
            segs.append(('L', cur, p)); cur = p
        elif cmd == 'H':
            p = (float(toks[i]), cur[1]); i += 1
            segs.append(('L', cur, p)); cur = p
        elif cmd == 'V':
            p = (cur[0], float(toks[i])); i += 1
            segs.append(('L', cur, p)); cur = p
        elif cmd == 'C':
            c1 = (float(toks[i]), float(toks[i + 1])); c2 = (float(toks[i + 2]), float(toks[i + 3]))
            p = (float(toks[i + 4]), float(toks[i + 5])); i += 6
            segs.append(('C', cur, c1, c2, p)); cur = p
        else:
            raise ValueError(cmd)
    if segs:
        subs.append((segs, closed))
    return subs


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def seg_at(s, t):
    if s[0] == 'L':
        return lerp(s[1], s[2], t)
    p0, c1, c2, p1 = s[1:]
    a, b, c = lerp(p0, c1, t), lerp(c1, c2, t), lerp(c2, p1, t)
    d, e = lerp(a, b, t), lerp(b, c, t)
    return lerp(d, e, t)


def seg_sub(s, t0, t1):
    if s[0] == 'L':
        return ('L', seg_at(s, t0), seg_at(s, t1))
    p0, c1, c2, p1 = s[1:]

    def split(seg, t):  # returns right part from t
        q0, q1, q2, q3 = seg
        a, b, c = lerp(q0, q1, t), lerp(q1, q2, t), lerp(q2, q3, t)
        d, e = lerp(a, b, t), lerp(b, c, t)
        m = lerp(d, e, t)
        return (q0, a, d, m), (m, e, c, q3)
    left, right = split((p0, c1, c2, p1), t0)
    if t1 >= 1:
        q = right
    else:
        tt = (t1 - t0) / (1 - t0)
        q, _ = split(right, tt)
    return ('C',) + tuple(q)


def seg_cmd(s):
    if s[0] == 'L':
        return f' L{pt(s[2])}'
    return f' C{pt(s[2])} {pt(s[3])} {pt(s[4])}'


def run_d(run):
    return f'M{pt(run[0][1])}' + ''.join(seg_cmd(s) for s in run)


def hits(s, B, rc, n=400):
    g = lambda t: dist(seg_at(s, t), B) - rc
    out = []
    prev = g(0)
    for k in range(1, n + 1):
        t = k / n
        v = g(t)
        if (prev < 0) != (v < 0):
            lo, hi = (k - 1) / n, t
            for _ in range(50):
                mid = (lo + hi) / 2
                if (g(lo) < 0) == (g(mid) < 0):
                    lo = mid
                else:
                    hi = mid
            out.append((lo + hi) / 2)
        prev = v
    return out


def pieces(segs, B, rc):
    out = []
    for s in segs:
        ts = [0] + [t for t in hits(s, B, rc) if 1e-6 < t < 1 - 1e-6] + [1]
        for t0, t1 in zip(ts, ts[1:]):
            sub = seg_sub(s, t0, t1)
            out.append((sub, dist(seg_at(sub, 0.5), B) < rc))
    return out


def cut_closed(d, B, rc, centroid=(128, 128)):
    """Open a closed outline around the badge at B; returns (line element, area element)."""
    segs, _ = parse(d)[0]
    ps = pieces(segs, B, rc)
    k = next(i for i, (s, ins) in enumerate(ps) if ins)
    ps = ps[k:] + ps[:k]
    run = [s for s, ins in ps if not ins]
    ld = run_d(run)
    a, b = run[-1][-1], run[0][1]
    area = ld + ' ' + arc_to(B, rc, a, b, lambda m: -dist(m, centroid)) + ' Z'
    return P(ld), P(area)


def seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + dx * t, a[1] + dy * t))


def gap(d, D=24, a=(48, 48), b=(208, 208), minlen=8):
    """Open every subpath of d where it passes within D of the slash a-b; returns path elements."""
    out = []
    for segs, closed in parse(d):
        ps = []
        for s in segs:
            g = lambda t: seg_dist(seg_at(s, t), a, b) - D
            n = 400
            ts = [0]
            prev = g(0)
            for k in range(1, n + 1):
                v = g(k / n)
                if (prev < 0) != (v < 0):
                    lo, hi = (k - 1) / n, k / n
                    for _ in range(50):
                        mid = (lo + hi) / 2
                        if (g(lo) < 0) == (g(mid) < 0):
                            lo = mid
                        else:
                            hi = mid
                    ts.append((lo + hi) / 2)
                prev = v
            ts.append(1)
            for t0, t1 in zip(ts, ts[1:]):
                sub = seg_sub(s, t0, t1)
                ps.append((sub, seg_dist(seg_at(sub, 0.5), a, b) < D))
        if closed and any(ins for _, ins in ps):
            k = next(i for i, (s, ins) in enumerate(ps) if ins)
            ps = ps[k:] + ps[:k]
        run = []
        for s, ins in ps + [(None, True)]:
            if ins:
                if run and sum(dist(seg_at(x, 0), seg_at(x, 1)) for x in run) >= minlen:
                    out.append(P(run_d(run)))
                run = []
            else:
                run.append(s)
    return out


def tf_path(d, fn, s=1.0):
    """Apply fn to every point of an absolute M/L/C/A/Z path (no H/V); arc radii scale by s."""
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


def tf(points, s, c_from, c_to):
    return [(c_to[0] + (x - c_from[0]) * s, c_to[1] + (y - c_from[1]) * s) for x, y in points]


# ---------------------------------------------------------------- badge marks (bare, radius ~32) centred at B
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
    elif kind == 'table':
        rect = R(x - 32, y - 28, 64, 56, 8)
        m['line'] += [rect]
        m['area'] += [rect]
        m['detail'] += [L(x - 32, y, x + 32, y), L(x, y - 28, x, y + 28)]
    return m


def badge(name, tags, base, kind, B):
    mk = marks(kind, B)
    icon(name, UI, tags,
         line=base.get('line', []) + mk['line'], detail=base.get('detail', []) + mk['detail'],
         area=base.get('area', []) + mk['area'], hole=base.get('hole', []) + mk['hole'],
         dot=base.get('dot', []) + mk['dot'], dotcut=base.get('dotcut', []) + mk['dotcut'])


# ---------------------------------------------------------------- cursor badges (cursor kept whole, badge clears it)
cur = load('cursor')
CB = (188, 188)
for kind, tags in [
    ('question', ['cursor', 'help', 'unknown', 'question']),
    ('share', ['cursor', 'share', 'send']),
    ('star', ['cursor', 'favorite', 'starred', 'featured']),
    ('warning', ['cursor', 'warning', 'alert', 'error']),
    ('x', ['cursor x', 'remove', 'cancel', 'cursor', 'pointer']),
]:
    badge('cursor-' + kind, tags, cur, kind, CB)

# ---------------------------------------------------------------- eye badges (eye scaled 0.875, nudged up-left)
eye = load('eye')
EYE_D = re.search(r'd="([^"]+)"', eye['line'][0]).group(1)
ES = 0.9
EC = (118, 114)
eye_small = tf_path(EYE_D, lambda p: tf([p], ES, (128, 128), EC)[0])
EB, ERC = (184, 184), 60
eye_ln, eye_ar = cut_closed(eye_small, EB, ERC, centroid=EC)
eye_base = dict(line=[eye_ln], area=[eye_ar], detail=[C(EC[0], EC[1], 32)])

for kind, suffix, tags in [
    ('arrow-down', 'arrow-down', ['eye', 'decrease', 'download', 'view', 'visible']),
    ('arrow-up', 'arrow-up', ['eye', 'increase', 'upload', 'view', 'visible']),
    ('bitcoin', 'bitcoin', ['eye', 'crypto', 'bitcoin', 'view', 'visible']),
    ('check', 'check', ['eye', 'done', 'approved', 'view', 'visible']),
    ('code', 'code', ['eye', 'developer', 'code', 'view', 'visible']),
    ('dollar', 'currency-dollar', ['eye', 'money', 'price', 'view', 'visible']),
    ('percent', 'discount', ['eye', 'sale', 'percent', 'view', 'visible']),
    ('gear', 'gear', ['eye', 'settings', 'configure', 'view', 'visible']),
    ('heart', 'heart', ['eye', 'favorite', 'like', 'view', 'visible']),
    ('lightning', 'lightning', ['eye', 'fast', 'power', 'view', 'visible']),
    ('magnifying-glass', 'magnifying-glass', ['eye', 'search', 'find', 'view', 'visible']),
    ('minus', 'minus', ['eye', 'remove', 'subtract', 'view', 'visible']),
    ('pause', 'pause', ['eye', 'paused', 'hold', 'view', 'visible']),
    ('pencil', 'pencil', ['eye', 'edit', 'write', 'view', 'visible']),
    ('plus', 'plus', ['eye', 'add', 'new', 'view', 'visible']),
    ('push-pin', 'push-pin', ['eye', 'pinned', 'pin', 'view', 'visible']),
    ('question', 'question', ['eye', 'help', 'unknown', 'view', 'visible']),
    ('share', 'share', ['eye', 'share', 'send', 'view', 'visible']),
    ('sparkle', 'sparkle', ['eye', 'ai', 'magic', 'view', 'visible']),
    ('star', 'star', ['eye', 'favorite', 'starred', 'view', 'visible']),
    ('table', 'table', ['eye', 'table', 'data', 'view', 'visible']),
    ('warning', 'warning', ['eye', 'warning', 'error', 'view', 'visible']),
]:
    badge('eye-' + suffix, tags, eye_base, kind, EB)

# ---------------------------------------------------------------- flag badges (flag body opened around the badge)
flag = load('flag')
POLE = flag['line'][0]
FLAG_D = 'M56 48 C104 24 136 72 200 48 L200 160 C136 184 104 136 56 160 Z'  # flag's body, V spelled as L
FS = 0.8
FT = lambda p: tf([p], FS, (44, 36), (44, 36))[0]
flag_small = tf_path(FLAG_D, FT)
POLE = PL([FT((56, 224)), FT((56, 40))])
FB, FRC = (188, 188), 60
flag_ln, flag_ar = cut_closed(flag_small, FB, FRC, centroid=(110, 90))
flag_base = dict(line=[POLE, flag_ln], area=[flag_ar])

for kind, suffix, tags in [
    ('arrow-down', 'arrow-down', ['flag', 'download', 'down', 'decrease']),
    ('arrow-up', 'arrow-up', ['flag', 'upload', 'up', 'increase']),
    ('bitcoin', 'bitcoin', ['flag', 'bitcoin', 'crypto']),
    ('check', 'check', ['flag check', 'done', 'approved', 'flag', 'report']),
    ('code', 'code', ['flag', 'code', 'developer', 'embed']),
    ('dollar', 'currency-dollar', ['flag', 'dollar', 'price', 'money']),
    ('percent', 'discount', ['flag', 'discount', 'sale', 'percent']),
    ('gear', 'gear', ['flag', 'settings', 'configure']),
    ('heart', 'heart', ['flag', 'favorite', 'like', 'love']),
    ('lightning', 'lightning', ['flag', 'fast', 'power', 'instant']),
    ('magnifying-glass', 'magnifying-glass', ['flag', 'search', 'find']),
    ('minus', 'minus', ['flag minus', 'remove', 'subtract', 'flag', 'report']),
]:
    badge('flag-' + suffix, tags, flag_base, kind, FB)

# ---------------------------------------------------------------- details (disclosure triangle split in half)
TRI = [(32, 60), (224, 60), (128, 204)]
icon('details', UI, ['details', 'disclosure', 'expand', 'summary'],
     line=[PG(TRI)], detail=[L(128, 60, 128, 204)], area=[PG(TRI)])
icon('details-slash', UI, ['details', 'disabled', 'disclosure'],
     line=[PG(TRI), L(128, 60, 128, 204), SLASH])

# ---------------------------------------------------------------- dots
icon('dots-six', UI, ['drag handle', 'grip', 'reorder', 'dots'],
     dot=[C(x, y, 16) for y in (92, 164) for x in (56, 128, 200)])
icon('dots-six-vertical', UI, ['drag handle', 'grip', 'reorder', 'dots', 'move'],
     dot=[C(x, y, 16) for x in (92, 164) for y in (56, 128, 200)])
icon('dots-three-circle', UI, ['more', 'menu', 'options', 'ellipsis', 'pending'],
     line=[C(128, 128, 96)], area=[C(128, 128, 96)], dotcut=[C(x, 128, 16) for x in (80, 128, 176)])
icon('dots-three-circle-vertical', UI, ['more', 'menu', 'options', 'kebab'],
     line=[C(128, 128, 96)], area=[C(128, 128, 96)], dotcut=[C(128, y, 16) for y in (80, 128, 176)])
icon('dots-three-diagonal', UI, ['more', 'options', 'diagonal'],
     dot=[C(68, 188, 16), C(128, 128, 16), C(188, 68, 16)])

K = 0.5523 * 16
TRAY = (f'M40 168 L40 200 C40 {f(200 + K)} {f(56 - K)} 216 56 216 L200 216 C{f(200 + K)} 216 216 {f(200 + K)} 216 200 L216 168')
# ---------------------------------------------------------------- download slash (arrow lowered 16 so its head clears the slash)
icon('download-slash', UI, ['download off', 'no download', 'blocked', 'offline', 'download'],
     line=[L(128, 56, 128, 176), PL([(80, 128), (128, 176), (176, 128)]), P(TRAY), L(44, 44, 184, 184)])

# ---------------------------------------------------------------- drag and drop (dashed box + cursor)
CS = 0.5
CT = (140, 136)
cur_pts = tf([(48, 40), (208, 112), (136, 136), (112, 208)], CS, (48, 40), CT)
a, b, r, leg = 32, 176, 14, 32
m = (a + b) / 2
box = [P(f'M{a} {a + leg} V{a + r} A{r} {r} 0 0 1 {a + r} {a} H{a + leg}'),
       P(f'M{b - leg} {a} H{b - r} A{r} {r} 0 0 1 {b} {a + r} V{a + leg}'),
       P(f'M{a + leg} {b} H{a + r} A{r} {r} 0 0 1 {a} {b - r} V{b - leg}'),
       L(m - 16, a, m + 16, a), L(a, m - 16, a, m + 16), L(b, m - 16, b, m + 12), L(m - 16, b, m + 12, b)]
icon('drag-drop', UI, ['drag and drop', 'move', 'dashed box', 'cursor'],
     line=box + [PG(cur_pts)], area=[PG(cur_pts)])

# ---------------------------------------------------------------- dropdown
icon('dropdown', UI, ['select', 'menu', 'list', 'combobox', 'dropdown'],
     line=[R(32, 76, 192, 104, 16)], detail=[PL([(152, 116), (172, 136), (192, 116)])],
     area=[R(32, 76, 192, 104, 16)])

# ---------------------------------------------------------------- escape
ec, er = (144, 144), 80
icon('escape', UI, ['escape', 'exit', 'esc', 'leave'],
     line=[P(f'M{pt(polar(ec, er, 270))} A{er} {er} 0 1 1 {pt(polar(ec, er, 180))}'),
           L(136, 136, 48, 48), PL([(48, 104), (48, 48), (104, 48)])])

# ---------------------------------------------------------------- eye closed
LID = ('C', (40, 88), (68, 132), (100, 148), (128, 148))
LID2 = ('C', (128, 148), (156, 148), (188, 132), (216, 88))


def lash(seg, t, ln=32):
    p = seg_at(seg, t)
    e = 1e-4
    q = seg_at(seg, min(t + e, 1)) if t < 1 else seg_at(seg, t)
    p0 = seg_at(seg, max(t - e, 0))
    q = seg_at(seg, min(t + e, 1))
    dx, dy = q[0] - p0[0], q[1] - p0[1]
    n = math.hypot(dx, dy)
    nx, ny = -dy / n, dx / n
    if ny < 0:
        nx, ny = -nx, -ny
    return L(p[0], p[1], p[0] + nx * ln, p[1] + ny * ln)


lid_d = 'M40 88 C68 132 100 148 128 148 C156 148 188 132 216 88'
icon('eye-closed', UI, ['eye closed', 'hidden', 'sleep', 'lashes'],
     line=[P(lid_d), lash(LID, 0.5), lash(LID, 1.0), lash(LID2, 0.5), lash(LID, 0.2, 24), lash(LID2, 0.8, 24)])

# ---------------------------------------------------------------- eye dotted
segs, _ = parse(EYE_D)[0]
samples = []
for s in segs:
    for k in range(200):
        samples.append(seg_at(s, k / 200))
cum = [0]
for p, q in zip(samples, samples[1:] + samples[:1]):
    cum.append(cum[-1] + dist(p, q))
total = cum[-1]
N = 12
dots = []
for i in range(N):
    target = total * i / N
    j = max(k for k in range(len(samples)) if cum[k] <= target)
    dots.append(samples[j])
icon('eye-dotted', UI, ['eye', 'dotted', 'view', 'visible', 'look'],
     line=[C(128, 128, 36)], dot=[C(p[0], p[1], 14) for p in dots])

print(save(overwrite=True))
