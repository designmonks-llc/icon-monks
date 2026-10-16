import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

N, SP, OB, MP = 'Nature', 'Sports', 'Objects', 'Maps'
SLASH = L(48, 48, 208, 208)
SG = 32  # centerline clearance kept between the slash and the strokes it crosses


# ---------------------------------------------------------------- slash gapping (exact path splitting)
def _attrs(el):
    return {k: v for k, v in re.findall(r'([\w-]+)="([^"]*)"', el)}


def el_d(el):
    a = _attrs(el)
    g = lambda k, d=0: float(a.get(k, d))
    if el.startswith('<path'):
        return a['d']
    if el.startswith('<circle') or el.startswith('<ellipse'):
        cx, cy = g('cx'), g('cy')
        rx = g('r') if el.startswith('<circle') else g('rx')
        ry = g('r') if el.startswith('<circle') else g('ry')
        return f'M{f(cx - rx)} {f(cy)} A{f(rx)} {f(ry)} 0 1 1 {f(cx + rx)} {f(cy)} A{f(rx)} {f(ry)} 0 1 1 {f(cx - rx)} {f(cy)} Z'
    if el.startswith('<rect'):
        x, y, w, h = g('x'), g('y'), g('width'), g('height')
        r = min(g('rx'), w / 2, h / 2)
        if not r:
            return f'M{f(x)} {f(y)} H{f(x + w)} V{f(y + h)} H{f(x)} Z'
        return (f'M{f(x + r)} {f(y)} H{f(x + w - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w)} {f(y + r)} V{f(y + h - r)} '
                f'A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(y + h)} H{f(x + r)} A{f(r)} {f(r)} 0 0 1 {f(x)} {f(y + h - r)} '
                f'V{f(y + r)} A{f(r)} {f(r)} 0 0 1 {f(x + r)} {f(y)} Z')
    raise ValueError(el)


def _ang(u, v):
    a = math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1])
    return a


def parse(d):
    """Absolute M L H V C A Z -> list of subpaths [(segments, closed)]."""
    toks = re.findall(r'[MLHVCAZ]|-?\d*\.?\d+(?:e-?\d+)?', d)
    i = 0; cmd = None; cur = (0, 0); start = (0, 0); subs = []; segs = None
    def num():
        nonlocal i
        v = float(toks[i]); i += 1; return v
    while i < len(toks):
        if re.match(r'[A-Z]', toks[i]):
            cmd = toks[i]; i += 1
            if cmd == 'Z':
                if dist(cur, start) > 1e-6:
                    segs.append(('L', cur, start))
                subs.append((segs, True)); segs = None; cur = start
                continue
        if cmd == 'M':
            if segs:
                subs.append((segs, False))
            cur = start = (num(), num()); segs = []; cmd = 'L'
        elif cmd == 'L':
            p = (num(), num()); segs.append(('L', cur, p)); cur = p
        elif cmd == 'H':
            p = (num(), cur[1]); segs.append(('L', cur, p)); cur = p
        elif cmd == 'V':
            p = (cur[0], num()); segs.append(('L', cur, p)); cur = p
        elif cmd == 'C':
            c1 = (num(), num()); c2 = (num(), num()); p = (num(), num())
            segs.append(('C', cur, c1, c2, p)); cur = p
        elif cmd == 'A':
            rx, ry, _, fa, fs = num(), num(), num(), num(), num(); p = (num(), num())
            x1p, y1p = (cur[0] - p[0]) / 2, (cur[1] - p[1]) / 2
            lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
            if lam > 1:
                rx *= math.sqrt(lam); ry *= math.sqrt(lam)
            num_ = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
            den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
            co = math.sqrt(max(0, num_ / den)) * (-1 if fa == fs else 1)
            cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
            cx, cy = cxp + (cur[0] + p[0]) / 2, cyp + (cur[1] + p[1]) / 2
            u = ((x1p - cxp) / rx, (y1p - cyp) / ry); v = ((-x1p - cxp) / rx, (-y1p - cyp) / ry)
            t1 = math.atan2(u[1], u[0]); dt = _ang(u, v)
            if fs == 0 and dt > 0: dt -= 2 * math.pi
            if fs == 1 and dt < 0: dt += 2 * math.pi
            segs.append(('A', (cx, cy), rx, ry, t1, t1 + dt)); cur = p
    if segs:
        subs.append((segs, False))
    return subs


def at(s, t):
    if s[0] == 'L':
        return (s[1][0] + (s[2][0] - s[1][0]) * t, s[1][1] + (s[2][1] - s[1][1]) * t)
    if s[0] == 'C':
        p0, p1, p2, p3 = s[1:]
        m = 1 - t
        return tuple(m ** 3 * p0[k] + 3 * m * m * t * p1[k] + 3 * m * t * t * p2[k] + t ** 3 * p3[k] for k in (0, 1))
    a = s[4] + (s[5] - s[4]) * t
    return (s[1][0] + s[2] * math.cos(a), s[1][1] + s[3] * math.sin(a))


def subseg(s, t0, t1):
    if s[0] == 'L':
        return ('L', at(s, t0), at(s, t1))
    if s[0] == 'A':
        return ('A', s[1], s[2], s[3], s[4] + (s[5] - s[4]) * t0, s[4] + (s[5] - s[4]) * t1)
    def split(p, t):
        p0, p1, p2, p3 = p
        l = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        a, b, c = l(p0, p1), l(p1, p2), l(p2, p3)
        d, e = l(a, b), l(b, c)
        g = l(d, e)
        return (p0, a, d, g), (g, e, c, p3)
    pts = s[1:]
    if t1 < 1:
        pts = split(pts, t1)[0]
    if t0 > 0:
        pts = split(pts, t0 / t1)[1]
    return ('C',) + tuple(pts)


def seg_cmd(s):
    if s[0] == 'L':
        return f'L{pt(s[2])}'
    if s[0] == 'C':
        return f'C{pt(s[2])} {pt(s[3])} {pt(s[4])}'
    dt = s[5] - s[4]
    end = at(s, 1)
    if abs(s[2] - s[3]) < 1e-6:
        r = f(s[2]); rr = f'{r} {r}'
    else:
        rr = f'{f(s[2])} {f(s[3])}'
    return f'A{rr} 0 {1 if abs(dt) > math.pi else 0} {1 if dt > 0 else 0} {pt(end)}'


def seg_dist(p, a=(48, 48), b=(208, 208)):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + dx * t, a[1] + dy * t))


def gap(el, g=SG, keep=None):
    """Return path elements of el with everything within g of the slash removed."""
    keep = keep or (lambda p: seg_dist(p) >= g)
    out = []
    for segs, closed in parse(el_d(el)):
        pieces = []  # (seg index, t0, t1)
        for si, s in enumerate(segs):
            N = 240
            ks = [keep(at(s, j / N)) for j in range(N + 1)]
            j = 0
            while j <= N:
                if not ks[j]:
                    j += 1; continue
                k = j
                while k < N and ks[k + 1]:
                    k += 1
                def refine(lo, hi):  # lo kept, hi not
                    for _ in range(40):
                        m = (lo + hi) / 2
                        if keep(at(s, m)): lo = m
                        else: hi = m
                    return lo
                t0 = j / N if j == 0 else refine(j / N, (j - 1) / N)
                t1 = k / N if k == N else refine(k / N, (k + 1) / N)
                if t1 - t0 > 1e-4:
                    pieces.append((si, t0, t1))
                j = k + 1
        # join pieces into runs
        runs = []
        for pc in pieces:
            if runs and runs[-1][-1][0] == pc[0] - 1 and runs[-1][-1][2] > 1 - 1e-9 and pc[1] < 1e-9:
                runs[-1].append(pc)
            else:
                runs.append([pc])
        if not runs:
            continue
        full = len(runs) == 1 and len(runs[0]) == len(segs) and runs[0][0][1] < 1e-9 and runs[0][-1][2] > 1 - 1e-9
        if closed and not full and len(runs) > 1 and runs[0][0][0] == 0 and runs[0][0][1] < 1e-9 \
                and runs[-1][-1][0] == len(segs) - 1 and runs[-1][-1][2] > 1 - 1e-9:
            runs[0] = runs.pop() + runs[0]
        for run in runs:
            ss = [subseg(segs[si], t0, t1) for si, t0, t1 in run]
            if sum(dist(at(s, 0), at(s, 0.5)) + dist(at(s, 0.5), at(s, 1)) for s in ss) < 12:
                continue
            d = f'M{pt(at(ss[0], 0))} ' + ' '.join(seg_cmd(s) for s in ss)
            if full and closed:
                d += ' Z'
            out.append(P(d))
    return out


def slashed(src, g=SG, drop_dots=True):
    """Slash variant: area left out, details become lines, every stroke opened around the slash."""
    lines = []
    for el in src.get('line', []) + src.get('detail', []):
        lines += gap(el, g)
    dots = []
    for el in src.get('dot', []) + src.get('dotcut', []):
        a = _attrs(el)
        c, r = (float(a['cx']), float(a['cy'])), float(a['r'])
        if not drop_dots or seg_dist(c) >= g + r * 0.75:
            dots.append(el)
    return dict(line=lines + [SLASH], dot=dots)


# ---------------------------------------------------------------- path transforms
def xf(d, k=1.0, deg=0.0, c=(128, 128), dx=0.0, dy=0.0):
    """Rotate by deg and scale by k about c, then translate; returns a new absolute path string."""
    a = math.radians(deg)
    def m(p):
        x, y = p[0] - c[0], p[1] - c[1]
        x, y = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
        return (c[0] + x * k + dx, c[1] + y * k + dy)
    out = []
    for segs, closed in parse(d):
        ns = []
        for s in segs:
            if s[0] == 'L':
                ns.append(('L', m(s[1]), m(s[2])))
            elif s[0] == 'C':
                ns.append(('C',) + tuple(m(p) for p in s[1:]))
            else:
                ns.append(('A', m(s[1]), s[2] * k, s[3] * k, s[4] + a, s[5] + a))
        if closed and ns and ns[-1][0] == 'L' and dist(ns[-1][1], ns[-1][2]) > 1e-6:
            ns = ns[:-1]
        out.append(f'M{pt(at(ns[0], 0))} ' + ' '.join(seg_cmd(s) for s in ns) + (' Z' if closed else ''))
    return ' '.join(out)


def flip_d(d):
    """Mirror a path horizontally about x=128."""
    out = []
    for segs, closed in parse(d):
        ns = []
        mm = lambda p: (256 - p[0], p[1])
        for s in segs:
            if s[0] == 'L':
                ns.append(('L', mm(s[1]), mm(s[2])))
            elif s[0] == 'C':
                ns.append(('C',) + tuple(mm(p) for p in s[1:]))
            else:
                ns.append(('A', mm(s[1]), s[2], s[3], math.pi - s[4], math.pi - s[5]))
        if closed and ns and ns[-1][0] == 'L' and dist(ns[-1][1], ns[-1][2]) > 1e-6:
            ns = ns[:-1]
        out.append(f'M{pt(at(ns[0], 0))} ' + ' '.join(seg_cmd(s) for s in ns) + (' Z' if closed else ''))
    return ' '.join(out)


def d_of(el):
    return re.search(r' d="([^"]+)"', el).group(1)


# ================================================================ drop badge variants
DROP = load('drop')['line'][0]
DROP_D = xf(d_of(DROP), dx=-24)   # nudged left (like map-pin's badge variants) so the badge bites less
BC = (184, 184)
BELL = load('bell')


def badge_mark(suffix):
    src = load('bell-' + suffix)
    r = float(re.findall(r'A(\d+(?:\.\d+)?) ', d_of(src['area'][0]))[-1])
    lines = [e for e in src['line'] if e not in BELL['line'] and 'L48 184' not in e]
    return r, dict(line=lines, area=src['area'][1:], hole=src['hole'], dot=src['dot'], dotcut=src['dotcut'],
                   detail=src['detail'])


def drop_badge(name, suffix, tags):
    r, mk = badge_mark(suffix)
    cut = gap(P(DROP_D), keep=lambda p: dist(p, BC) >= r)
    d = d_of(cut[0])
    segs = parse(d)[0][0]
    p_end, p_start = at(segs[-1], 1), at(segs[0], 0)
    area = d + ' ' + arc_to(BC, r, p_end, p_start, lambda q: -dist(q, (112, 152))) + ' Z'
    icon(name, N, tags, line=cut + mk['line'], area=[P(area)] + mk['area'], hole=mk['hole'], dot=mk['dot'],
         dotcut=mk['dotcut'], detail=mk['detail'])


for nm, sfx, tg in [
    ('drop-arrow-down', 'arrow-down', ['drop', 'decrease', 'download', 'water', 'liquid']),
    ('drop-arrow-up', 'arrow-up', ['drop', 'increase', 'upload', 'water', 'liquid']),
    ('drop-check', 'check', ['water ok', 'drop', 'check', 'clean']),
    ('drop-code', 'code', ['drop', 'developer', 'code', 'water', 'liquid']),
    ('drop-currency-dollar', 'currency-dollar', ['drop', 'money', 'price', 'water', 'liquid']),
    ('drop-gear', 'gear', ['drop', 'settings', 'configure', 'water', 'liquid']),
    ('drop-heart', 'heart', ['drop', 'favorite', 'like', 'water', 'liquid']),
    ('drop-lightning', 'lightning', ['drop', 'fast', 'power', 'water', 'liquid']),
    ('drop-magnifying-glass', 'magnifying-glass', ['drop', 'search', 'find', 'water', 'liquid']),
    ('drop-minus', 'minus', ['drop', 'remove', 'subtract', 'water', 'liquid']),
    ('drop-pause', 'pause', ['drop', 'paused', 'hold', 'water', 'liquid']),
    ('drop-plus', 'plus', ['drop', 'add', 'new', 'water', 'liquid']),
    ('drop-push-pin', 'push-pin', ['drop', 'pinned', 'pin', 'water', 'liquid']),
    ('drop-question', 'question', ['drop', 'help', 'unknown', 'water', 'liquid']),
    ('drop-share', 'share', ['drop', 'share', 'send', 'water', 'liquid']),
    ('drop-star', 'star', ['drop', 'favorite', 'starred', 'water', 'liquid']),
    ('drop-warning', 'warning', ['drop', 'warning', 'error', 'water', 'liquid']),
    ('drop-x', 'x', ['drop', 'remove', 'cancel', 'water', 'liquid']),
]:
    drop_badge(nm, sfx, tg)

# drop-circle: the drop, scaled down, as a cut inside a circle
dc_d = xf(d_of(DROP), k=0.56, c=(128, 140), dy=-6)
icon('drop-circle', N, ['water', 'drop', 'liquid'], line=[C(128, 128, 96)], detail=[P(dc_d)], area=[C(128, 128, 96)])

# ================================================================ slash variants of existing icons
icon('cactus-slash', N, ['cactus', 'disabled', 'off', 'nature'], **slashed(load('cactus')))
icon('feather-slash', N, ['feather', 'disabled', 'off', 'nature'], **slashed(load('feather')))
icon('flower-slash', N, ['flower', 'off', 'disabled', 'hidden'], **slashed(load('flower')))
icon('leaf-slash', N, ['leaf', 'off', 'disabled', 'hidden'], **slashed(load('leaf')))
icon('mountains-slash', N, ['mountains', 'off', 'disabled', 'hidden'], **slashed(load('mountains')))

# ================================================================ acorn
cap = 'M48 120 C48 84 84 68 128 68 C172 68 208 84 208 120 Z'
nut = 'M68 120 C68 172 96 204 128 220 C160 204 188 172 188 120'
icon('acorn', N, ['acorn', 'nut', 'oak', 'autumn'],
     line=[P(cap), P(nut), P('M128 68 C128 54 132 44 144 36')],
     detail=[L(68, 120, 188, 120)],
     area=[P(cap), P(nut + ' Z')])

# ================================================================ helpers
def wave(y, x0=32, x1=224, amp=16, half=16):
    """Wavy line as cubic curves (quadratic bumps of width `half`, control offset amp)."""
    d = f'M{f(x0)} {f(y)}'
    x = x0; up = True
    while x < x1 - 1e-6:
        cy = y - amp if up else y + amp
        cx = x + half / 2
        nx = x + half
        c1 = (x + 2 / 3 * (cx - x), y + 2 / 3 * (cy - y))
        c2 = (nx + 2 / 3 * (cx - nx), y + 2 / 3 * (cy - y))
        d += f' C{pt(c1)} {pt(c2)} {f(nx)} {f(y)}'
        x = nx; up = not up
    return d


# ================================================================ beach
bsun = (128, 92)
beach_src = dict(
    line=[C(*bsun, 32)] + [L(*polar(bsun, 50, a), *polar(bsun, 64, a)) for a in (180, 225, 270, 315, 0)] +
         [P(wave(168, half=48, amp=18)), P(wave(208, half=48, amp=18))],
    area=[C(*bsun, 32)])
icon('beach', N, ['sea', 'holiday', 'summer', 'beach', 'maps'], **beach_src)
icon('beach-slash', MP, ['beach', 'disabled', 'off', 'maps'], **slashed(beach_src))

# ================================================================ beach-ball
bb = (128, 128)
seams = []
for a in (-90, 30, 150):
    p0 = polar(bb, 24, a); p3 = polar(bb, 96, a + 62)
    c1 = polar(bb, 52, a + 2); c2 = polar(bb, 84, a + 34)
    seams.append(P(f'M{pt(p0)} C{pt(c1)} {pt(c2)} {pt(p3)}'))
icon('beach-ball', SP, ['beach', 'summer', 'ball'],
     line=[C(*bb, 96)], detail=[C(*bb, 24)] + seams, area=[C(*bb, 96)])

# ================================================================ beach-chair
canvas = 'M72 40 C96 96 120 140 148 164 L200 152'
icon('beach-chair', OB, ['sunbathing', 'lounger', 'beach', 'vacation'],
     line=[PL([(56, 48), (104, 152), (216, 152)]), L(120, 152, 192, 216), L(192, 152, 120, 216)])

# ================================================================ bubbles
icon('bubbles', N, ['bubbles', 'soap', 'foam', 'fizz', 'clean'],
     line=[C(96, 156, 56), C(180, 76, 36), C(196, 180, 20)],
     detail=[P(f'M{pt(polar((96, 156), 28, 190))} A28 28 0 0 1 {pt(polar((96, 156), 28, 260))}')],
     area=[C(96, 156, 56), C(180, 76, 36), C(196, 180, 20)],
     dot=[C(60, 64, 14)])

# ================================================================ campfire
flame = ('M128 168 C100 168 80 148 80 120 C80 88 108 72 116 40 C140 56 156 80 156 100 C164 96 170 88 172 80 '
         'C180 96 176 108 176 120 C176 148 156 168 128 168 Z')
icon('campfire', N, ['camping', 'fire', 'logs', 'campfire', 'outdoors'],
     line=[P(flame), L(52, 216, 204, 184), L(52, 184, 204, 216)], area=[P(flame)])

# ================================================================ cannabis
cb = (128, 184)
leaflets = []
for a, ln, hw in ((-90, 144, 18), (-54, 120, 17), (-126, 120, 17), (-18, 84, 15), (-162, 84, 15)):
    u = (math.cos(math.radians(a)), math.sin(math.radians(a))); n = (-u[1], u[0])
    T = (cb[0] + u[0] * ln, cb[1] + u[1] * ln)
    q = lambda t, s: (cb[0] + u[0] * ln * t + n[0] * s, cb[1] + u[1] * ln * t + n[1] * s)
    d = (f'M{pt(cb)} C{pt(q(0.3, hw * 1.5))} {pt(q(0.75, hw * 1.1))} {pt(T)} '
         f'C{pt(q(0.75, -hw * 1.1))} {pt(q(0.3, -hw * 1.5))} {pt(cb)} Z')
    leaflets.append(P(d))
icon('cannabis', N, ['cannabis', 'leaf', 'hemp', 'plant'], line=leaflets + [L(128, 184, 128, 224)], area=leaflets)

# ================================================================ christmas-tree
xstar = PG([polar((128, 60), 28 if i % 2 == 0 else 12, -90 + i * 36) for i in range(10)])
xtree = 'M128 96 L172 148 L156 148 L204 196 L52 196 L100 148 L84 148 Z'
xmas = dict(line=[xstar, P(xtree), L(128, 196, 128, 224)], area=[xstar, P(xtree)],
            dotcut=[C(104, 176, 14), C(152, 176, 14), C(128, 134, 12)])
icon('christmas-tree', N, ['christmas', 'tree', 'holiday', 'xmas'], **xmas)
icon('christmas-tree-slash', N, ['christmas tree', 'disabled', 'off', 'nature'], **slashed(xmas))

# ================================================================ clover
HEART = 'M128 212 C128 212 32 160 32 98 A50 50 0 0 1 128 78 A50 50 0 0 1 224 98 C224 160 128 212 128 212 Z'
leaf1 = xf(HEART, k=0.35, c=(128, 212), dx=0, dy=-212 + 103)
cl_leaves = [P(xf(leaf1, deg=a, c=(128, 128))) for a in (-45, 45, 135, 225)]
icon('clover', N, ['clover', 'luck', 'four leaf', 'shamrock', 'leaf'],
     line=cl_leaves + [P('M128 144 C128 176 136 200 152 220')], area=cl_leaves)

# ================================================================ compost
LEAF = 'M56 200 C48 112 104 48 216 40 C224 144 160 208 56 200 Z'
cleaf = xf(LEAF, k=0.31, c=(56, 200), dx=116 - 56, dy=178 - 200)
cc = (128, 116); cr = 76
ca0, ca1 = polar(cc, cr, 150), polar(cc, cr, 30)
icon('compost', N, ['compost', 'organic', 'recycle', 'soil'],
     line=[P(f'M{pt(ca0)} A{cr} {cr} 0 1 1 {pt(ca1)}'),
           PL([(ca1[0] - 4, ca1[1] - 40), ca1, (ca1[0] - 40, ca1[1] - 8)]),
           P('M40 216 C64 184 192 184 216 216 Z'), P(cleaf), L(116, 192, 116, 178)],
     area=[P('M40 216 C64 184 192 184 216 216 Z'), P(cleaf)])

# ================================================================ desert
dtrunk = 'M76 216 V108 A20 20 0 0 1 116 108 V216'
icon('desert', N, ['desert', 'dunes', 'cactus', 'sun'],
     line=[P(dtrunk), P('M76 176 H64 A12 12 0 0 1 52 164 V140'), P('M116 156 H128 A12 12 0 0 0 140 144 V120'),
           L(32, 216, 224, 216), P('M152 216 C168 188 192 176 224 176'), C(184, 76, 28)],
     area=[P(dtrunk + ' Z'), C(184, 76, 28)])

# ================================================================ farm
fbarn = 'M32 216 V128 L48 92 L92 68 L136 92 L152 128 V216'
icon('farm', N, ['farm', 'barn', 'agriculture', 'rural'],
     line=[P(fbarn), P('M188 216 V84 A18 18 0 0 1 224 84 V216'), L(32, 216, 224, 216)],
     detail=[P('M68 216 V160 H116 V216'), L(68, 160, 116, 216), L(116, 160, 68, 216), L(188, 128, 224, 128)],
     area=[P(fbarn + ' Z'), P('M188 216 V84 A18 18 0 0 1 224 84 V216 Z')])

# ================================================================ flower-lotus
lc = 'M128 196 C96 172 92 108 128 52 C164 108 160 172 128 196 Z'
lsl = 'M128 196 C84 196 56 160 52 104 C76 108 94 116 106 128'
lol = 'M112 198 C72 204 44 188 32 160 C48 152 60 150 72 152'
l_side = [lsl, flip_d(lsl)]
l_out = [lol, flip_d(lol)]
icon('flower-lotus', N, ['lotus', 'yoga', 'zen', 'flower', 'spa'],
     line=[P(lc)] + [P(d) for d in l_side + l_out],
     detail=[P('M106 128 C104 156 112 182 128 196'), P('M150 128 C152 156 144 182 128 196')],
     area=[P(lc)] + [P(d + ' L128 196 Z') for d in l_side] + [P(d + ' L112 198 Z') for d in l_out[:1]] +
          [P(l_out[1] + ' L144 198 Z')])

# ================================================================ flower-tulip
thead = 'M80 64 L104 88 L128 56 L152 88 L176 64 V112 A48 48 0 0 1 80 112 Z'
tleaf = 'M128 216 C128 188 148 172 180 172 C180 200 160 214 128 216 Z'
icon('flower-tulip', N, ['tulip', 'spring', 'flower'],
     line=[P(thead), L(128, 160, 128, 224), P(tleaf)], area=[P(thead), P(tleaf)])

# ================================================================ footprints
SOLE = 'M128 108 C148 108 156 124 156 148 C156 176 148 204 128 204 C108 204 100 180 102 160 C104 138 108 108 128 108 Z'
def foot(dx, dy, deg, mirror=False):
    base = flip_d(SOLE) if mirror else SOLE
    sole = xf(base, k=1.05, deg=deg, c=(128, 156), dx=dx, dy=dy)
    toes = [((112, 84), 13), ((136, 76), 10), ((156, 86), 9)]
    dots = []
    for (x, y), r in toes:
        if mirror:
            x = 256 - x
        p = rot([(128 + (x - 128) * 1.05, 156 + (y - 156) * 1.05)], deg, (128, 156))[0]
        dots.append(C(p[0] + dx, p[1] + dy, r * 1.1))
    return sole, dots
s1, d1 = foot(-46, 10, -8, mirror=True)
s2, d2 = foot(46, -20, 8)
icon('footprints', N, ['footsteps', 'trail', 'walking', 'barefoot', 'steps'],
     line=[P(s1), P(s2)], area=[P(s1), P(s2)], dot=d1 + d2)

# ================================================================ grass
icon('grass', N, ['grass', 'lawn', 'blades', 'field'],
     line=[L(32, 216, 224, 216), P('M56 216 C56 180 52 152 36 128'), P('M92 216 C92 168 96 128 84 88'),
           P('M128 216 C128 152 136 96 160 56'), P('M164 216 C164 172 172 140 196 112'),
           P('M200 216 C200 192 204 172 220 156')])

# ================================================================ greenhouse
gh = 'M40 216 V120 A88 88 0 0 1 216 120 V216 Z'
gx = lambda x: 120 - math.sqrt(88 ** 2 - (x - 128) ** 2)
icon('greenhouse', N, ['greenhouse', 'plants', 'garden', 'glasshouse'],
     line=[P(gh)],
     detail=[L(98, gx(98), 98, 216), L(158, gx(158), 158, 216), L(40, 128, 216, 128)],
     area=[P(gh)])

# ================================================================ hand-seedling
HAND = load('hand-coins')
hs_l = 'M148 96 C148 72 132 56 100 56 C100 80 116 96 148 96 Z'
hs_r = 'M148 84 C148 56 164 40 196 40 C196 68 180 84 148 84 Z'
icon('hand-seedling', N, ['plant', 'growth', 'seedling', 'care'],
     line=HAND['line'][:2] + [L(148, 128, 148, 84), P(hs_l), P(hs_r)],
     detail=[HAND['detail'][0]], area=[HAND['area'][0], P(hs_l), P(hs_r)])

# ================================================================ iceberg
ice = [(120, 48), (144, 72), (156, 60), (184, 104), (216, 156), (172, 216), (88, 208), (40, 152), (76, 104)]
icon('iceberg', N, ['iceberg', 'ice', 'ocean', 'hidden'],
     line=[PG(ice), L(32, 104, 76, 104), L(184, 104, 224, 104)], detail=[L(76, 104, 184, 104)], area=[PG(ice)])

# ================================================================ island
imound = 'M48 184 C72 160 184 160 208 184 Z'
icon('island', N, ['tropical island', 'palm', 'vacation', 'island', 'holiday'],
     line=[P(imound), P(wave(216, 40, 216, half=44, amp=14)), P('M132 166 C132 136 138 112 152 88'),
           P('M152 86 C124 64 92 70 64 100'), P('M152 86 C176 64 204 70 220 100'),
           P('M152 86 C140 60 120 46 92 46'), P('M152 86 C168 56 188 44 212 46')],
     area=[P(imound)])

# ================================================================ jack-o-lantern
PUMP = load('pumpkin')
eyes = [PG([(76, 140), (96, 108), (116, 140)]), PG([(140, 140), (160, 108), (180, 140)])]
mouth = 'M72 160 L104 174 L128 162 L152 174 L184 160 C176 184 152 196 128 196 C104 196 80 184 72 160 Z'
icon('jack-o-lantern', N, ['halloween', 'pumpkin', 'jack o lantern', 'scary'],
     line=PUMP['line'], detail=eyes + [P(mouth)], area=PUMP['area'], hole=eyes + [P(mouth)])

# ================================================================ landslide
icon('landslide', N, ['landslide', 'rockfall', 'hazard', 'mudslide'],
     line=[P('M32 72 L176 216 H32 Z'), PG(regular_polygon((112, 92), 18, 6, -10)),
           PG(regular_polygon((156, 132), 22, 6, 10)), PG(regular_polygon((200, 184), 26, 6, -20))],
     area=[P('M32 72 L176 216 H32 Z'), PG(regular_polygon((112, 92), 18, 6, -10)),
           PG(regular_polygon((156, 132), 22, 6, 10)), PG(regular_polygon((200, 184), 26, 6, -20))])

# ================================================================ leaf-lightning
LF = load('leaf')
bolt = PG([(150, 76), (112, 128), (136, 128), (124, 168), (164, 112), (140, 112)])
icon('leaf-lightning', N, ['green energy', 'renewable', 'eco', 'sustainable'],
     line=LF['line'], detail=[bolt], area=LF['area'])

# ================================================================ maple-leaf
mr = [(128, 32), (150, 80), (180, 68), (170, 120), (216, 100), (204, 140), (224, 152), (168, 184), (176, 204), (128, 192)]
mp = mr + [(256 - x, y) for x, y in reversed(mr[1:-1])]
icon('maple-leaf', N, ['maple leaf', 'autumn', 'fall', 'canada'],
     line=[PG(mp), L(128, 192, 128, 224)], area=[PG(mp)])

# ================================================================ mountain-flag
mtn = 'M32 208 L128 96 L224 208 Z'
mflag = 'M128 40 L176 56 L128 72 Z'
icon('mountain-flag', N, ['summit', 'peak', 'goal', 'achievement'],
     line=[P(mtn), L(128, 96, 128, 40), P(mflag)],
     detail=[PL([(101.6, 126.8), (116, 140), (128, 128), (140, 140), (154.4, 126.8)])],
     area=[P(mtn), P(mflag)])

# ================================================================ mountains-sun
MT = load('mountains')
icon('mountains-sun', N, ['landscape', 'scenery', 'mountains', 'sun'],
     line=MT['line'] + [C(72, 64, 24)], detail=MT['detail'], area=MT['area'] + [C(72, 64, 24)])
print(save(overwrite=True))
