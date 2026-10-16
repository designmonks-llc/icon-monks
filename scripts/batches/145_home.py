import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from draw import *

# ================================================================ small outline engine (as in 113_communication)
# Segments: ('L', p0, p1) | ('C', p0, c1, c2, p1) | ('A', centre, r, a0, a1)
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


def polyline_segs(pts, close=False):
    segs = [('L', pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    if close:
        segs.append(('L', pts[-1], pts[0]))
    return segs


def seg_len(segs):
    pts = sample(segs, 30) + [seg_end(segs[-1])]
    return sum(dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def open_cut(segs, c, r, min_len=10):
    runs, whole = trim(segs, lambda p: dist(p, c) >= r, False)
    if whole:
        return [P(segs_d(segs))]
    return [P(segs_d(run)) for run in runs if run and seg_len(run) >= min_len]


def scale_d(d, s, c_from, c_to):
    """Scale an absolute M/L/C/Z path (no arcs) about c_from and move it to c_to."""
    import re
    out, xy = [], []
    for t in re.findall(r'[MLCZ]|-?\d+\.?\d*', d):
        if t in 'MLCZ':
            out.append(t)
        else:
            xy.append(float(t))
            if len(xy) == 2:
                out.append(pt((c_to[0] + (xy[0] - c_from[0]) * s, c_to[1] + (xy[1] - c_from[1]) * s)))
                xy = []
    return ' '.join(out).replace('M ', 'M').replace('L ', 'L').replace('C ', 'C')


HM = 'Home'
SLASH = L(48, 48, 208, 208)
B = (184, 184)
BX, BY = B
SG = 28  # clear gap (centreline) kept in base strokes on each side of a slash


def seg_dist(p, a=(48, 48), b=(208, 208)):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + dx * t, a[1] + dy * t))


def gapped(outline, closed=True, min_len=12):
    runs, whole = trim(outline, lambda p: seg_dist(p) >= SG, closed)
    if whole:
        return [P(segs_d(outline, closed))]
    return [P(segs_d(r)) for r in runs if r and seg_len(r) >= min_len]


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


def heart_d(c, s):
    def q(x, y):
        return pt((c[0] + (x - 128) * s, c[1] + (y - 140) * s))
    r = f(50 * s)
    return (f'M{q(128, 212)} C{q(128, 212)} {q(32, 160)} {q(32, 98)} A{r} {r} 0 0 1 {q(128, 78)} '
            f'A{r} {r} 0 0 1 {q(224, 98)} C{q(224, 160)} {q(128, 212)} {q(128, 212)} Z')


SPARK = 'M128 32 C136 96 160 120 224 128 C160 136 136 160 128 224 C120 160 96 136 32 128 C96 120 120 96 128 32 Z'
SHIELD = 'M128 32 L208 64 V120 C208 176 168 208 128 224 C88 208 48 176 48 120 V64 Z'


def badge(kind):
    """Returns (roles dict, clearance radius) for a lower-right badge mark around B."""
    b = dict(line=[], area=[], hole=[], dot=[], detail=[])
    cr = 56
    if kind == 'check':
        b['line'] = [PL(T([(-26, 2), (-8, 20), (26, -16)]))]
    elif kind == 'plus':
        b['line'] = [L(BX, BY - 26, BX, BY + 26), L(BX - 26, BY, BX + 26, BY)]
    elif kind == 'minus':
        b['line'] = [L(BX - 26, BY, BX + 26, BY)]
        cr = 50
    elif kind == 'dollar':
        b['line'] = [P(f'M{BX + 16} {BY - 24} H{BX - 4} A12 12 0 0 0 {BX - 4} {BY} '
                       f'H{BX + 4} A12 12 0 0 1 {BX + 4} {BY + 24} H{BX - 16}'),
                     L(BX, BY - 38, BX, BY - 24), L(BX, BY + 24, BX, BY + 38)]
        cr = 60
    elif kind == 'bitcoin':
        x0 = BX - 16
        b['line'] = [P(f'M{x0 - 6} {BY - 26} H{BX + 2} A13 13 0 0 1 {BX + 2} {BY} H{x0}'),
                     P(f'M{x0} {BY} H{BX + 6} A13 13 0 0 1 {BX + 6} {BY + 26} H{x0 - 6}'),
                     L(x0, BY - 26, x0, BY + 26),
                     L(BX - 2, BY - 40, BX - 2, BY - 26), L(BX - 2, BY + 26, BX - 2, BY + 40)]
        cr = 60
    elif kind == 'gear':
        g = gear_path(B, 20, 31, 6, -90)
        b['line'] = [P(g)]
        b['area'] = [P(g)]
        b['hole'] = [C(BX, BY, 7)]
        cr = 60
    elif kind == 'lightning':
        bolt = T([(6, -34), (-22, 6), (0, 6), (-6, 34), (22, -6), (0, -6)])
        b['line'] = [PG(bolt)]
        b['area'] = [PG(bolt)]
        cr = 58
    elif kind == 'magnifying-glass':
        b['line'] = [C(BX - 6, BY - 6, 18), L(BX + 8, BY + 8, BX + 26, BY + 26)]
        b['area'] = [C(BX - 6, BY - 6, 18)]
    elif kind == 'question':
        b['line'] = [P(f'M{BX - 18} {BY - 20} A18 18 0 1 1 {BX + 6} {BY - 3} C{BX + 1} {BY} {BX} {BY + 3} {BX} {BY + 8}')]
        b['dot'] = [C(BX, BY + 32, 14)]
        cr = 58
    elif kind == 'share':
        b['line'] = [P(f'M{BX - 28} {BY + 28} V{BY + 16} A24 24 0 0 1 {BX - 4} {BY - 8} H{BX + 28}'),
                     PL(T([(8, -28), (28, -8), (8, 12)]))]
        cr = 60
    elif kind == 'pencil':
        pc = [(40, 216), (56, 160), (168, 48), (208, 88), (96, 200)]
        s = 0.36
        pts = [(BX + (x - 124) * s, BY + (y - 132) * s) for x, y in pc]
        b['line'] = [PG(pts)]
        b['area'] = [PG(pts)]
        cr = 60
    elif kind == 'sparkle':
        d = scale_d(SPARK, 0.42, (128, 128), B)
        b['line'] = [P(d)]
        b['area'] = [P(d)]
        cr = 60
    elif kind == 'shield':
        d = scale_d(SHIELD.replace('V120', 'L208 120').replace('V64', 'L48 64'), 0.34, (128, 128), B)
        b['line'] = [P(d)]
        b['area'] = [P(d)]
        cr = 60
    else:
        raise ValueError(kind)
    return b, cr


def merge(*ds):
    out = dict(line=[], area=[], hole=[], dot=[], detail=[], dotcut=[])
    for d in ds:
        for k, v in d.items():
            out[k] += v
    return out


# ================================================================ house family (exact house geometry)
HOUSE_WALLS = polyline_segs([(48, 112), (48, 208), (208, 208), (208, 112)])
HOUSE_ROOF = polyline_segs([(32, 124), (128, 40), (224, 124)])
HOUSE_AREA = polyline_segs([(48, 112), (128, 44), (208, 112), (208, 208), (48, 208)], True)
HOUSE_DOOR = 'M108 208 V164 A20 20 0 0 1 148 164 V208'
HOUSE_LINE = [P('M48 112 V208 H208 V112'), PL([(32, 124), (128, 40), (224, 124)])]
HOUSE_AREA_D = 'M48 112 L128 44 L208 112 V208 H48 Z'


def house_badge(kind):
    b, cr = badge(kind)
    ln = open_cut(HOUSE_WALLS, B, cr, 20) + open_cut(HOUSE_ROOF, B, cr, 20)
    _, ar = carve(HOUSE_AREA, B, cr)
    return merge(dict(line=ln, area=[P(ar)]), b)


HB = {
    'bitcoin': ('bitcoin', ['house', 'bitcoin', 'crypto']),
    'check': ('check', ['home verified', 'safe', 'house', 'check']),
    'currency-dollar': ('dollar', ['house', 'dollar', 'price', 'money']),
    'gear': ('gear', ['home settings', 'smart home', 'house', 'gear']),
    'lightning': ('lightning', ['house', 'fast', 'power', 'instant']),
    'magnifying-glass': ('magnifying-glass', ['house', 'search', 'find']),
    'minus': ('minus', ['house', 'remove', 'minus', 'home', 'house minus']),
    'pencil': ('pencil', ['house', 'edit', 'write']),
    'plus': ('plus', ['add home', 'new house', 'property', 'house', 'new property']),
    'question': ('question', ['house', 'help', 'unknown', 'question']),
    'share': ('share', ['house', 'share', 'send']),
    'shield': ('shield', ['home security', 'protected home', 'insurance', 'home insurance', 'protected']),
    'sparkle': ('sparkle', ['house', 'ai', 'magic', 'smart']),
}
for suffix, (kind, tags) in HB.items():
    icon(f'house-{suffix}', HM, tags, **house_badge(kind))

# symbols drawn inside the house in place of the door
icon('house-heart', HM, ['homestay', 'bnb', 'lodging', 'cozy', 'home sweet home'],
     line=HOUSE_LINE, area=[P(HOUSE_AREA_D)], detail=[P(heart_d((128, 156), 0.36))])
leaf = scale_d('M56 200 C48 112 104 48 216 40 C224 144 160 208 56 200 Z', 0.44, (136, 120), (130, 150))
leaf_vein = scale_d('M56 200 L168 88', 0.44, (136, 120), (130, 150))
icon('house-leaf', HM, ['eco house', 'green home', 'sustainable', 'energy'],
     line=HOUSE_LINE, area=[P(HOUSE_AREA_D)], detail=[P(leaf), P(leaf_vein)])

icon('house-slash', HM, ['homeless', 'house off', 'no home', 'slash'], line=HOUSE_LINE + [SLASH])


def house_scaled(s, anchor_from, anchor_to):
    tf = lambda x, y: (anchor_to[0] + (x - anchor_from[0]) * s, anchor_to[1] + (y - anchor_from[1]) * s)
    walls = [tf(*p) for p in [(48, 112), (48, 208), (208, 208), (208, 112)]]
    roof = [tf(*p) for p in [(32, 124), (128, 40), (224, 124)]]
    area = [tf(*p) for p in [(48, 112), (128, 44), (208, 112), (208, 208), (48, 208)]]
    return [PL(walls), PL(roof)], [PG(area)], tf


hs_line, hs_area, hs_tf = house_scaled(0.66, (128, 208), (128, 216))
peak = hs_tf(128, 40)
waves = []
for rr in (36, 72):
    a = polar(peak, rr, -135); b2 = polar(peak, rr, -45)
    waves.append(P(f'M{pt(a)} A{rr} {rr} 0 0 1 {pt(b2)}'))
icon('house-signal', HM, ['smart home', 'connected', 'wifi', 'iot'], line=hs_line + waves, area=hs_area)
icon('house-signal-slash', HM, ['house signal', 'off', 'disabled', 'hidden', 'house'], line=hs_line + waves + [SLASH])

# house in a hand (hand family geometry)
HAND = 'M64 152 H108 C120 152 126 160 132 168 H160 L194 146 A15 15 0 0 1 212 168 L168 212 H64 Z'
hh_walls = 'M104 70 V120 H184 V70'
hh_roof = [(88, 82), (144, 34), (200, 82)]
hh_area = 'M104 70 L144 37 L184 70 V120 H104 Z'
icon('house-hand', HM, ['home insurance', 'shelter', 'care', 'property'],
     line=[R(32, 144, 32, 72, 8), P(HAND), P(hh_walls), PL(hh_roof)],
     detail=[L(96, 184, 140, 184)], area=[P(HAND), P(hh_area)])

# house with a sale sign: the board hangs from an arm on a post in the lower right
# (a yard sign on a post: board 140..220 x 144..196; house strokes kept 28 clear of it)
SIGN = R(140, 144, 80, 52, 10)
_keep = lambda p: not (p[0] > 140 - 28 and p[1] > 144 - 28)
_ln = []
for _segs in (HOUSE_WALLS, HOUSE_ROOF):
    _runs, _ = trim(_segs, _keep, False)
    _ln += [P(segs_d(r_)) for r_ in _runs if r_ and seg_len(r_) >= 20]
icon('house-sale', HM, ['for sale', 'real estate', 'property'],
     line=_ln + [SIGN, L(180, 196, 180, 224)],
     area=[PG([(48, 112), (128, 44), (208, 112), (208, 116), (112, 116), (112, 208), (48, 208)]), SIGN])

# ================================================================ furniture
icon('desk', HM, ['desk', 'table', 'workspace', 'office'],
     line=[L(32, 72, 224, 72), L(48, 72, 48, 208), P('M136 72 V200 A8 8 0 0 0 144 208 H200 A8 8 0 0 0 208 200 V72')],
     detail=[L(136, 140, 208, 140), L(160, 106, 184, 106), L(160, 174, 184, 174)],
     area=[P('M136 72 V200 A8 8 0 0 0 144 208 H200 A8 8 0 0 0 208 200 V72 Z')])

# desk lamp
lp_base = (88, 208)
elbow = (48, 128)
pivot = (132, 60)
sh_ang = 55
def shade_pts():
    loc = [(0, -16), (72, -50), (72, 50), (0, 16)]
    a = math.radians(sh_ang)
    return [(pivot[0] + x * math.cos(a) - y * math.sin(a), pivot[1] + x * math.sin(a) + y * math.cos(a)) for x, y in loc]
shade = shade_pts()
icon('desk-lamp', HM, ['desk lamp', 'reading light', 'study', 'lamp', 'table lamp'],
     line=[L(40, 216, 136, 216), PL([lp_base, elbow, pivot]), PG(shade)], area=[PG(shade)], dot=[C(*elbow, 14)])

icon('dimmer-switch', HM, ['light dimmer', 'rotary switch', 'brightness'],
     line=[R(48, 32, 160, 192, 16)], detail=[C(128, 128, 52), L(128, 128, *polar((128, 128), 22, -60))],
     area=[R(48, 32, 160, 192, 16)])

icon('dining-table', HM, ['table', 'restaurant table', 'dining', 'furniture'],
     line=[L(80, 120, 176, 120), L(128, 120, 128, 208), L(100, 208, 156, 208),
           PL([(32, 72), (32, 208)]), PL([(32, 160), (64, 160), (64, 208)]),
           PL([(224, 72), (224, 208)]), PL([(224, 160), (192, 160), (192, 208)])])

icon('dishwasher', HM, ['dishwasher', 'appliance', 'kitchen', 'dishes', 'clean'],
     line=[R(48, 32, 160, 192, 16)],
     detail=[L(48, 88, 208, 88), L(136, 60, 168, 60), L(96, 120, 160, 120),
             P('M76 192 A24 24 0 0 1 124 192'), P('M132 192 A24 24 0 0 1 180 192')],
     area=[R(48, 32, 160, 192, 16)], dotcut=[C(84, 60, 12)])

# doors
DF = 'M120 216 V56 A16 16 0 0 1 136 40 H208 A16 16 0 0 1 224 56 V216'
DLEAF = [(120, 40), (176, 54), (176, 224), (120, 216)]
icon('door-enter', HM, ['enter', 'entrance', 'login'],
     line=[P(DF), PG(DLEAF), L(32, 136, 88, 136), PL([(60, 108), (88, 136), (60, 164)])], area=[PG(DLEAF)])
icon('door-exit', HM, ['exit', 'leave', 'logout'],
     line=[P(DF), PG(DLEAF), L(88, 136, 32, 136), PL([(60, 108), (32, 136), (60, 164)])], area=[PG(DLEAF)])

PLATE = R(56, 32, 64, 192, 32)
LEVER = P('M88 88 H192 A16 16 0 0 1 208 104')
icon('door-handle', HM, ['handle', 'door', 'lever', 'knob'], line=[PLATE, LEVER], area=[PLATE], dot=[C(88, 88, 16)])
icon('door-lock', HM, ['door lock', 'lock', 'knob', 'security'], line=[PLATE, LEVER], area=[PLATE], dot=[C(88, 88, 16)],
     detail=[L(88, 160, 88, 184)], dotcut=[C(88, 156, 14)])

HANGER = P('M72 88 A56 56 0 0 1 184 88 V208 A16 16 0 0 1 168 224 H88 A16 16 0 0 1 72 208 Z')
icon('door-hanger', HM, ['housekeeping', 'hotel', 'clean room', 'door hanger', 'do not disturb'],
     line=[HANGER, C(128, 88, 24)], hole=[C(128, 88, 16)],
     detail=[L(*polar((128, 88), 24, 40), 184, 128), L(104, 160, 152, 160), L(104, 192, 136, 192)],
     area=[HANGER])
icon('door-hanger-slash', HM, ['do not disturb', 'hotel', 'door hanger', 'privacy'],
     line=[HANGER, C(128, 88, 24), L(*polar((128, 88), 24, 40), 184, 128), SLASH])

door = load('door')
icon('door-slash', HM, ['door', 'disabled', 'off', 'entrance', 'room'], line=door['line'] + [SLASH])

icon('door-sliding', HM, ['sliding door', 'patio', 'glass door', 'door'],
     line=[R(32, 96, 192, 120, 14), L(72, 48, 184, 48), PL([(164, 28), (184, 48), (164, 68)])],
     detail=[L(128, 96, 128, 216)], area=[R(32, 96, 192, 120, 14)])

bc = (104, 152)
bwaves = []
for rr in (96, 128):
    bwaves.append(P(f'M{pt(polar(bc, rr, -70))} A{rr} {rr} 0 0 1 {pt(polar(bc, rr, -20))}'))
icon('doorbell', HM, ['doorbell', 'ring', 'chime', 'entrance'],
     line=[C(*bc, 64)] + bwaves, detail=[C(*bc, 28)], area=[C(*bc, 64)])

icon('drawer', HM, ['cabinet drawer', 'storage', 'chest'],
     line=[R(32, 112, 192, 96, 14), PL([(48, 112), (72, 56), (184, 56), (208, 112)])],
     detail=[L(100, 160, 156, 160)], area=[R(32, 112, 192, 96, 14)])

icon('dresser', HM, ['dresser', 'drawers', 'furniture', 'bedroom'],
     line=[R(48, 32, 160, 168, 14), L(72, 200, 72, 224), L(184, 200, 184, 224)],
     detail=[L(48, 88, 208, 88), L(48, 144, 208, 144), L(112, 60, 144, 60), L(112, 116, 144, 116), L(112, 172, 144, 172)],
     area=[R(48, 32, 160, 168, 14)])

el = load('elevator')
el_det = []
for pts in ([(100, 108), (128, 80), (156, 108)], [(100, 148), (128, 176), (156, 148)]):
    el_det += gapped(polyline_segs(pts), False)
icon('elevator-slash', HM, ['elevator', 'disabled', 'off', 'home'], line=el['line'] + el['detail'] + [SLASH])

# estate: gabled centre block with two wings
est = [(32, 208), (32, 128), (80, 128), (80, 96), (128, 48), (176, 96), (176, 128), (224, 128), (224, 208)]
icon('estate', HM, ['estate', 'mansion', 'property'],
     line=[PG(est)], detail=[L(80, 128, 80, 208), L(176, 128, 176, 208), P(HOUSE_DOOR)],
     area=[PG(est)], dotcut=[C(128, 104, 12)])

# fan
FC = (128, 128)
def blade(deg):
    loc = 'M128 108 C104 100 92 60 112 40 C124 30 152 32 160 52 C166 72 152 96 140 110'
    pts = []
    import re
    nums = [float(v) for v in re.findall(r'-?\d+\.?\d*', loc)]
    pts = [(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]
    r_ = rot(pts, deg, FC)
    return [('C', r_[0], r_[1], r_[2], r_[3]), ('C', r_[3], r_[4], r_[5], r_[6]), ('C', r_[6], r_[7], r_[8], r_[9])]
blade_segs = [blade(d) for d in (0, 120, 240)]
blades = [segs_d(b_) for b_ in blade_segs]
icon('fan', HM, ['fan', 'ventilation', 'cooling', 'airflow', 'air'],
     line=[P(b_) for b_ in blades] + [C(*FC, 20)], area=[P(b_ + ' Z') for b_ in blades] + [C(*FC, 20)],
     dotcut=[C(*FC, 8)])
icon('fan-slash', HM, ['fan off', 'ventilation off', 'air off', 'cooling off'],
     line=sum((gapped(b_, False) for b_ in blade_segs), []) + [SLASH])

drip = 'M200 184 C192 196 188 202 188 208 A12 12 0 0 0 212 208 C212 202 208 196 200 184 Z'
fbody = R(72, 104, 48, 112, 12)
icon('faucet', HM, ['faucet', 'tap', 'sink', 'water'],
     line=[fbody, P('M120 128 H168 A32 32 0 0 1 200 160 V164'), L(96, 104, 96, 64), L(56, 64, 136, 64), P(drip)],
     area=[fbody, P(drip)])

def picket(cx):
    return f'M{cx - 16} 216 V72 L{cx} 48 L{cx + 16} 72 V216 Z'
pk = [P(picket(x)) for x in (48, 128, 208)]
rail_pts = [[(64, y), (112, y)] for y in (104, 168)] + [[(144, y), (192, y)] for y in (104, 168)]
rails = [PL(r_) for r_ in rail_pts]
pk_segs = [polyline_segs([(x - 16, 216), (x - 16, 72), (x, 48), (x + 16, 72), (x + 16, 216)], True) for x in (48, 128, 208)]
icon('fence', HM, ['garden', 'yard', 'fence', 'outdoor', 'picket'], line=pk + rails, area=pk)
icon('fence-slash', HM, ['fence', 'disabled', 'off', 'home'],
     line=pk + rails + [SLASH])

flame = 'M128 208 C108 208 100 196 100 184 C100 168 116 160 120 144 C136 156 156 168 156 184 C156 196 148 208 128 208 Z'
icon('fireplace', HM, ['fireplace', 'hearth', 'fire', 'warm'],
     line=[L(32, 64, 224, 64), L(48, 64, 48, 216), L(208, 64, 208, 216), L(32, 216, 224, 216),
           P('M80 216 V144 A48 48 0 0 1 176 144 V216'), P(flame)],
     area=[R(48, 64, 160, 152)], hole=[P('M88 216 V144 A40 40 0 0 1 168 144 V216 Z')])

icon('floor-plan', HM, ['layout', 'rooms', 'blueprint'],
     line=[P('M48 104 L128 40 L208 104 V208 H48 Z')],
     detail=[L(128, 100, 128, 160), L(160, 152, 208, 152), L(48, 160, 96, 160)],
     area=[P('M48 104 L128 40 L208 104 V208 H48 Z')])

FRIDGE = R(56, 32, 144, 192, 16)
icon('fridge', HM, ['refrigerator', 'fridge', 'kitchen', 'appliance'],
     line=[FRIDGE], detail=[L(56, 104, 200, 104), L(84, 60, 84, 76), L(84, 132, 84, 172)], area=[FRIDGE])
icon('fridge-slash', HM, ['fridge', 'off', 'disabled', 'hidden'],
     line=[FRIDGE, L(56, 104, 200, 104), SLASH])

icon('garage', HM, ['garage', 'car port', 'parking', 'door', 'car'],
     line=[PL([(32, 112), (128, 40), (224, 112)]), P('M48 100 V208 H208 V100')],
     detail=[P('M80 208 V128 H176 V208'), L(80, 160, 176, 160), L(80, 184, 176, 184)],
     area=[P('M48 100 L128 44 L208 100 V208 H48 Z')])

shovel_blade = 'M32 128 H96 V168 L64 216 L32 168 Z'
icon('garden-tools', HM, ['shovel', 'pitchfork', 'garden tools', 'farm'],
     line=[L(44, 40, 84, 40), L(64, 40, 64, 128), P(shovel_blade),
           L(156, 40, 196, 40), L(176, 40, 176, 216), P('M140 216 V144 H212 V216')],
     area=[P(shovel_blade)])

icon('gate', HM, ['gate', 'entrance', 'fence', 'door'],
     line=[L(40, 40, 40, 216), L(216, 40, 216, 216), L(40, 192, 216, 192), P('M40 104 Q128 40 216 104'),
           L(84, 88, 84, 192), L(128, 72, 128, 192), L(172, 88, 172, 192)])

icon('high-chair', HM, ['high chair', 'baby', 'feeding', 'toddler'],
     line=[L(80, 40, 80, 136), L(80, 136, 168, 136), L(80, 96, 192, 96), L(96, 136, 56, 216), L(152, 136, 192, 216),
           L(72, 184, 176, 184)])

tub = 'M56 136 V176 A32 32 0 0 0 88 208 H168 A32 32 0 0 0 200 176 V136'
icon('hot-tub', HM, ['hot tub', 'jacuzzi', 'spa', 'bath'],
     line=[L(40, 136, 216, 136), P(tub), P('M68 136 A28 28 0 0 1 124 136'),
           P('M156 108 C146 96 166 84 156 72 C146 60 166 48 156 36'), P('M200 108 C190 96 210 84 200 72 C190 60 210 48 200 36')],
     area=[P(tub + ' Z')], dot=[C(96, 76, 20)])

print(save(overwrite=True))
