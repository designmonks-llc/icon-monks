"""Fixes: exposure-slash, sign-language, seal-percent-slash (missing); arrows-clockwise(-slash) heads out of
bounds; mouse-*-click marks; battery-low/medium/high level scheme; polyhedron(-slash) redrawn as a dodecahedron."""
import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

# ================================================================ small outline engine (as in 161_media.py)
# Segments: ('L', p0, p1) | ('C', p0, c1, c2, p1) | ('A', centre, r, a0, a1)  (angles in radians, a1 may be < a0)
H = math.pi / 2
TAU = 2 * math.pi


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def seg_point(s, t):
    if s[0] == 'L':
        return lerp(s[1], s[2], t)
    if s[0] == 'C':
        p0, c1, c2, p1 = s[1:]
        a, b, c = lerp(p0, c1, t), lerp(c1, c2, t), lerp(c2, p1, t)
        return lerp(lerp(a, b, t), lerp(b, c, t), t)
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
    if abs(a1 - a0) >= TAU - 1e-6:  # full circle: two halves
        m = ('A', c, r, a0, (a0 + a1) / 2)
        return seg_cmd(m) + ' ' + seg_cmd(('A', c, r, (a0 + a1) / 2, a1))
    large = 1 if abs(a1 - a0) > math.pi else 0
    sweep = 1 if a1 > a0 else 0
    return f'A{f(r)} {f(r)} 0 {large} {sweep} {pt(seg_end(s))}'


def segs_d(segs, close=False):
    d = f'M{pt(seg_point(segs[0], 0))} ' + ' '.join(seg_cmd(s) for s in segs)
    return d + (' Z' if close else '')


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


def seg_len(segs, n=40):
    pts = sample(segs, n) + [seg_end(segs[-1])]
    return sum(dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def seg_rect(x, y, w, h, r):
    x2, y2 = x + w, y + h
    return [('L', (x, y2 - r), (x, y + r)), ('A', (x + r, y + r), r, 2 * H, 3 * H), ('L', (x + r, y), (x2 - r, y)),
            ('A', (x2 - r, y + r), r, 3 * H, 4 * H), ('L', (x2, y + r), (x2, y2 - r)), ('A', (x2 - r, y2 - r), r, 0, H),
            ('L', (x2 - r, y2), (x + r, y2)), ('A', (x + r, y2 - r), r, H, 2 * H)]


def seg_poly(pts, close=False):
    out = [('L', pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    if close:
        out.append(('L', pts[-1], pts[0]))
    return out


def seg_circle(c, r, a0=0):
    return [('A', c, r, a0, a0 + TAU)]


# ---------------------------------------------------------------- slash helpers
SLASH_A, SLASH_B = (48, 48), (208, 208)
SG = 30


def seg_dist(p, a=SLASH_A, b=SLASH_B):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + dx * t, a[1] + dy * t))


def gapped(outline, closed=True, a=SLASH_A, b=SLASH_B, sg=SG, minlen=12):
    runs, whole = trim(outline, lambda p: seg_dist(p, a, b) >= sg, closed)
    if whole:
        return [P(segs_d(outline, closed))]
    return [P(segs_d(r)) for r in runs if r and seg_len(r) >= minlen]


def slashed(*shapes, a=SLASH_A, b=SLASH_B):
    out = []
    for segs, closed in shapes:
        out += gapped(segs, closed, a, b)
    return out + [L(*a, *b)]


# ---------------------------------------------------------------- path parsing with a similarity transform
def xform(s=1.0, deg=0.0, c_from=(128, 128), c_to=(128, 128), mirror=False):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)

    def fn(p):
        x, y = p[0] - c_from[0], p[1] - c_from[1]
        if mirror:
            x = -x
        x, y = x * s, y * s
        return (c_to[0] + x * ca - y * sa, c_to[1] + x * sa + y * ca)
    fn.s, fn.a, fn.mirror = s, a, mirror
    return fn


def parse_d(d, X=None):
    """Absolute M/L/H/V/C/A/Z path (circular arcs only) -> list of (segs, closed), transformed by X."""
    X = X or xform()
    toks = re.findall(r'[MLHVCAZ]|-?\d*\.?\d+', d)
    subs, segs, cur, start, cmd, i = [], [], None, None, None, 0
    num = lambda k: float(toks[k])
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd == 'Z':
                if dist(cur, start) > 1e-6:
                    segs.append(('L', cur, start))
                subs.append((segs, True)); segs = []; cur = start
            continue
        if cmd == 'M':
            if segs:
                subs.append((segs, False)); segs = []
            cur = start = (num(i), num(i + 1)); i += 2; cmd = 'L'
        elif cmd == 'L':
            q = (num(i), num(i + 1)); segs.append(('L', cur, q)); cur = q; i += 2
        elif cmd == 'H':
            q = (num(i), cur[1]); segs.append(('L', cur, q)); cur = q; i += 1
        elif cmd == 'V':
            q = (cur[0], num(i)); segs.append(('L', cur, q)); cur = q; i += 1
        elif cmd == 'C':
            c1, c2, q = (num(i), num(i + 1)), (num(i + 2), num(i + 3)), (num(i + 4), num(i + 5))
            segs.append(('C', cur, c1, c2, q)); cur = q; i += 6
        elif cmd == 'A':
            r, large, sweep, q = num(i), int(num(i + 3)), int(num(i + 4)), (num(i + 5), num(i + 6))
            segs.append(_arc(cur, q, r, large, sweep)); cur = q; i += 7
    if segs:
        subs.append((segs, False))
    return [([_xs(s_, X) for s_ in sg], cl) for sg, cl in subs]


def _arc(p, q, r, large, sweep):
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    dx, dy = q[0] - p[0], q[1] - p[1]
    d = math.hypot(dx, dy)
    r = max(r, d / 2)
    h = math.sqrt(max(r * r - d * d / 4, 0))
    ux, uy = -dy / d, dx / d
    sign = 1 if large != sweep else -1
    c = (mx + sign * h * ux, my + sign * h * uy)
    a0, a1 = math.atan2(p[1] - c[1], p[0] - c[0]), math.atan2(q[1] - c[1], q[0] - c[0])
    if sweep and a1 < a0:
        a1 += TAU
    if not sweep and a1 > a0:
        a1 -= TAU
    return ('A', c, r, a0, a1)


def _xs(s, X):
    if s[0] == 'L':
        return ('L', X(s[1]), X(s[2]))
    if s[0] == 'C':
        return ('C',) + tuple(X(p) for p in s[1:])
    c, r, a0, a1 = s[1:]
    if X.mirror:
        a0, a1 = math.pi - a0, math.pi - a1
    return ('A', X(c), r * X.s, a0 + X.a, a1 + X.a)


def subs_d(subs):
    return ' '.join(segs_d(sg, cl) for sg, cl in subs)


# ================================================================ 1. exposure-slash
# The split diagonal is dropped (it would duplicate the slash); the frame opens at the two corners
# the slash points into, the plus and minus stay where they are in exposure.
# The frame is inset to 40..216 so the longer slash (32..224) visibly runs out through the opened corners.
EXP = seg_rect(40, 40, 176, 176, 16)
icon('exposure-slash', 'Media', ['exposure', 'photo', 'plus minus', 'camera', 'adjust'],
     line=slashed((EXP, True), a=(32, 32), b=(224, 224)) + [L(164, 68, 164, 112), L(142, 90, 186, 90), L(70, 164, 114, 164)])

# ================================================================ 2. sign-language
# The library's open hand in front, and the library's pointing hand behind it at the upper left: only its
# index finger and thumb show, trimmed with a clear gap around the front hand (the two-handshape look of
# a signer). The back hand carries no inner details and no tiny fragments, so it stays clean at 24px.
HAND = load('hand')
HAND_OUT = re.search(r'd="([^"]+)"', HAND['line'][0]).group(1)
HAND_DET = [re.search(r'd="([^"]+)"', e).group(1) for e in HAND['detail']]
PT_OUT = re.search(r'd="([^"]+)"', load('hand-pointing')['line'][0]).group(1)

FX = xform(0.72, 6, (130, 128), (156, 152))
BX_ = xform(0.7, -12, (130, 128), (100, 104))
front = parse_d(HAND_OUT, FX)
front_poly = sample(front[0][0], 40)
GAP = 28


def near_front(p):
    return inside(front_poly, p) or min(dist(p, q) for q in front_poly) < GAP


back_lines = []
for sg, cl in parse_d(PT_OUT, BX_):
    runs, whole = trim(sg, lambda p: not near_front(p), cl, steps=120)
    back_lines += [P(segs_d(sg, cl))] if whole else [P(segs_d(r)) for r in runs if r and seg_len(r) >= 30]
icon('sign-language', 'People', ['asl', 'deaf', 'gesture', 'hands', 'communication'],
     line=[P(subs_d(front))] + back_lines,
     detail=[P(subs_d(parse_d(d, FX))) for d in HAND_DET],
     area=[P(subs_d(front))])

# ================================================================ 4. mouse clicks (geometry of 128_devices.py)
MS = R(72, 32, 112, 192, 56)
LEFT_BTN = 'M128 136 H72 V88 A56 56 0 0 1 128 32 Z'
RIGHT_BTN = 'M128 136 H184 V88 A56 56 0 0 0 128 32 Z'
DIV = [L(128, 32, 128, 136), L(72, 136, 184, 136)]
icon('mouse-left-click', 'Devices', ['left click', 'mouse', 'select', 'mouse button', 'primary click'],
     line=[MS] + DIV, area=[P(LEFT_BTN)], detail=[L(102, 72, 102, 108)])
icon('mouse-right-click', 'Devices', ['right click', 'context menu', 'mouse', 'secondary click'],
     line=[MS] + DIV, area=[P(RIGHT_BTN)], detail=[L(154, 72, 154, 108)])
WHEEL = R(112, 60, 32, 48, 16)
icon('mouse-middle-click', 'Devices', ['middle click', 'mouse', 'wheel'],
     line=[MS, L(128, 32, 128, 60), L(128, 108, 128, 136), L(72, 136, 184, 136), WHEEL, L(128, 76, 128, 92)],
     area=[WHEEL])

# ================================================================ 5. battery levels: three evenly spread slots
# low = 1, medium = 2, high = 3 bars on a 3-slot scale (battery-full keeps its 4 thin bars, battery keeps 2).
BODY = R(32, 72, 168, 112, 16)
TERM = L(224, 108, 224, 148)
SLOTS = [66, 116, 166]
bars3 = lambda n: [L(x, 104, x, 152) for x in SLOTS[:n]]
for name, tags, n in (('battery-low', ['low battery', 'charge needed', 'power', 'battery', 'low charge'], 1),
                      ('battery-medium', ['battery', 'half charge', 'power', 'half', 'charge'], 2),
                      ('battery-high', ['battery', 'high charge', 'power', 'charge', 'mostly full'], 3)):
    icon(name, 'Devices', tags, line=[BODY, TERM], detail=bars3(n), area=[BODY])

# ================================================================ 6. polyhedron: dodecahedron (decagon rim, pentagon face)
PC = (128, 128)
DEC = regular_polygon(PC, 96, 10)
PEN = regular_polygon(PC, 46, 5)
SPOKES = [(PEN[i], DEC[2 * i]) for i in range(5)]
icon('polyhedron', 'Design', ['polyhedron', '3d shape', 'gem', 'geometry'],
     line=[PG(DEC)], area=[PG(DEC)], detail=[PG(PEN)] + [L(*a, *b) for a, b in SPOKES])
icon('polyhedron-slash', 'Design', ['polyhedron', 'off', 'disabled', 'hidden'],
     line=slashed((seg_poly(DEC, True), True), (seg_poly(PEN, True), True), *[(seg_poly([a, b]), False) for a, b in SPOKES]))

# ================================================================ 7. seal-percent-slash
# The percent is mirrored so its circles sit off the slash diagonal and the slash takes the place of its bar.
seal_pts = []
for i in range(240):
    t = i * 2 * math.pi / 240
    rr = 88 + 8 * math.cos(10 * t)
    seal_pts.append((128 + rr * math.cos(t), 128 + rr * math.sin(t)))
icon('seal-percent-slash', 'Commerce', ['discount', 'sale', 'percent', 'badge', 'discount badge'],
     line=slashed((seg_poly(seal_pts, True), True)) + [C(156, 100, 12), C(100, 156, 12)])

print(save(overwrite=True))

# ================================================================ 3. arrows-clockwise (+ slash)
# Heads pulled inside the live area: both arms of each head are 39.43 long (the vertical arm used to reach y=27).
ARC1 = 'M50.73 107.29 A80 80 0 0 1 184.57 71.43'
HEAD1 = [(184.57, 32), (184.57, 71.43), (145.14, 71.43)]
ARC2 = 'M205.27 148.71 A80 80 0 0 1 71.43 184.57'
HEAD2 = [(71.43, 224), (71.43, 184.57), (110.86, 184.57)]


def write_raw(name, category, tags, lines):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" '
           f'data-category="{category}" data-tags="{tags}">\n'
           f'  <g data-role="line" {STROKE}>\n' + ''.join(f'    {e}\n' for e in lines) + '  </g>\n</svg>\n')
    with open(os.path.join(ROOT, 'icons', name + '.svg'), 'w') as fh:
        fh.write(svg)
    return name


ac = [P(ARC1), PL(HEAD1), P(ARC2), PL(HEAD2)]
print(write_raw('arrows-clockwise', 'Arrows', 'sync,refresh,reload,update', ac))
acs = []
for d in (ARC1, ARC2):
    for sg, cl in parse_d(d):
        acs += gapped(sg, cl)
acs += [PL(HEAD1), PL(HEAD2), L(48, 48, 208, 208)]
print(write_raw('arrows-clockwise-slash', 'Interface', 'sync off,refresh off,no sync,paused', acs))
