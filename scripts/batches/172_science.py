import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

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


def seg_dist(p, a=(48, 48), b=(208, 208)):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + dx * t, a[1] + dy * t))


# ================================================================ helpers for this batch
SC = 'Science'
SLASH = L(48, 48, 208, 208)
SG = 30  # centreline gap left in base strokes either side of the slash
B = (184, 184)
BX, BY = B


def gapped(outline, closed=True):
    runs, whole = trim(outline, lambda p: seg_dist(p) >= SG, closed)
    if whole and closed:
        return [P(segs_d(outline, True))]
    out = []
    for r in runs:
        pts = sample(r, 20) + [seg_end(r[-1])]
        if r and sum(dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)) >= 24:
            out.append(P(segs_d(r)))
    return out


def arc_seg(p, q, r, sweep):
    """Small circular arc p->q as an engine segment; sweep=1 is clockwise on screen."""
    m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    h = dist(p, q) / 2
    d = math.sqrt(max(r * r - h * h, 0))
    ux, uy = (q[0] - p[0]) / (2 * h), (q[1] - p[1]) / (2 * h)
    for s in (1, -1):
        c = (m[0] - uy * d * s, m[1] + ux * d * s)
        a0, a1 = ang(c, p), ang(c, q)
        span = (a1 - a0) % (2 * math.pi) if sweep else -((a0 - a1) % (2 * math.pi))
        if abs(span) <= math.pi + 1e-6:
            return ('A', c, r, a0, a0 + span)


def poly_segs(pts, close=False):
    pts = list(pts) + ([pts[0]] if close else [])
    return [('L', pts[i], pts[i + 1]) for i in range(len(pts) - 1)]


def ellipse_segs(c, rx, ry, rotdeg, n=144):
    a = math.radians(rotdeg)
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        pts.append((c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a)))
    return poly_segs(pts, True)


def plus_badge():
    return [L(BX, BY - 26, BX, BY + 26), L(BX - 26, BY, BX + 26, BY)]


# ================================================================ People
dress = [(112, 96), (144, 96), (180, 180), (76, 180)]
icon('woman', 'People', ['female', 'lady', 'person', 'figure', 'woman'],
     line=[C(128, 56, 24), PG(dress), L(112, 104, 68, 144), L(144, 104, 188, 144), L(108, 180, 108, 220), L(148, 180, 148, 220)],
     area=[C(128, 56, 24), PG(dress)])

# ================================================================ atom slash (atom's own three orbits, opened at the slash)
at_line = []
SG = 36
for deg in (0, 60, 120):
    at_line += gapped(ellipse_segs((128, 128), 96, 36, deg))
SG = 30
icon('atom-slash', SC, ['atom', 'disabled', 'off', 'science'], line=at_line + [SLASH])

# ================================================================ maths marks
icon('average', SC, ['mean', 'average', 'statistics', 'x-bar'],
     line=[L(64, 52, 192, 52), L(72, 96, 184, 208), L(184, 96, 72, 208)])
icon('congruent-to', SC, ['congruent', 'math', 'equal', 'geometry'],
     line=[P('M48 92 C72 60 104 60 128 80 C152 100 184 100 208 68'), L(48, 148, 208, 148), L(48, 196, 208, 196)])
icon('equal-double', SC, ['equivalent', 'math', 'equal'],
     line=[L(48, 68, 208, 68), L(48, 108, 208, 108), L(48, 148, 208, 148), L(48, 188, 208, 188)])
icon('lambda', SC, ['lambda', 'greek', 'function', 'math'],
     line=[P('M64 40 H80 C94 40 100 48 106 62 L166 202 C170 212 178 216 196 216'), L(136, 132, 64, 216)])
icon('cubic-meter', SC, ['cubic meter', 'volume', 'm3', 'unit'],
     line=[P('M40 200 V112'), P('M40 140 A24 24 0 0 1 88 140 V200'), P('M88 140 A24 24 0 0 1 136 140 V200'),
           P('M176 52 H198 A16 16 0 0 1 198 84 H188'), P('M188 84 H200 A18 18 0 0 1 200 120 H176')])
icon('co2', SC, ['carbon dioxide', 'emissions', 'air', 'gas'],
     line=[P(f'M{pt(polar((72, 120), 36, -45))} A36 36 0 1 0 {pt(polar((72, 120), 36, 45))}'), E(146, 120, 26, 36),
           P('M192 176 A13 13 0 1 1 215 184 L192 208 H220')])

# ================================================================ microbiology
bu = (math.cos(math.radians(-40)), math.sin(math.radians(-40)))
bc = (150, 104)
bact = capsule(bc, 34, 36, bu)
ec = (bc[0] - bu[0] * 34, bc[1] - bu[1] * 34)
flag = []
for da in (-34, 34):
    s0 = polar(ec, 36, 140 + da)
    e0 = polar(s0, 72, 140)
    n0 = polar((0, 0), 18, 50)
    c1 = (s0[0] + (e0[0] - s0[0]) / 3 + n0[0], s0[1] + (e0[1] - s0[1]) / 3 + n0[1])
    c2 = (s0[0] + 2 * (e0[0] - s0[0]) / 3 - n0[0], s0[1] + 2 * (e0[1] - s0[1]) / 3 - n0[1])
    flag.append(P(f'M{pt(s0)} C{pt(c1)} {pt(c2)} {pt(e0)}'))
icon('bacteria', SC, ['microbe', 'germ', 'microbiology', 'cell'],
     line=[P(bact)] + flag,
     area=[P(bact)], dotcut=[C(bc[0] - bu[0] * 20, bc[1] - bu[1] * 20, 14), C(bc[0] + bu[0] * 20, bc[1] + bu[1] * 20, 14)])

# ================================================================ glassware
icon('beaker', SC, ['lab', 'chemistry', 'glass', 'experiment'],
     line=[P('M44 40 A20 20 0 0 1 64 60 V200 A16 16 0 0 0 80 216 H176 A16 16 0 0 0 192 200 V40'), L(64, 132, 192, 132)],
     area=[P('M64 132 V200 A16 16 0 0 0 80 216 H176 A16 16 0 0 0 192 200 V132 Z')])
fr_y = 156 - math.sqrt(64 ** 2 - 20 ** 2)
icon('flask-round', SC, ['potion', 'round bottom', 'chemistry', 'lab', 'round-bottom flask'],
     line=[P(f'M108 40 V{f(fr_y)} A64 64 0 1 0 148 {f(fr_y)} V40'), L(92, 40, 164, 40), L(64, 156, 192, 156)],
     area=[P('M64 156 A64 64 0 0 0 192 156 Z')])
FLASK = [('L', (104, 40), (104, 100)), ('L', (104, 100), (44, 192)), ('C', (44, 192), (36, 204), (44, 216), (60, 216)),
         ('L', (60, 216), (196, 216)), ('C', (196, 216), (212, 216), (220, 204), (212, 192)), ('L', (212, 192), (152, 100)),
         ('L', (152, 100), (152, 40))]
icon('flask-slash', SC, ['flask', 'off', 'disabled', 'hidden'],
     line=gapped(FLASK, False) + gapped(poly_segs([(88, 40), (168, 40)]), False)
     + gapped(poly_segs([(70.09, 152), (185.91, 152)]), False) + [SLASH])

# ================================================================ dna slash
DNA1 = [('C', (80, 32), (80, 80), (176, 80), (176, 128)), ('C', (176, 128), (176, 176), (80, 176), (80, 224))]
DNA2 = [('C', (176, 32), (176, 80), (80, 80), (80, 128)), ('C', (80, 128), (80, 176), (176, 176), (176, 224))]
dl = []
for o in (DNA1, DNA2, poly_segs([(104, 112), (152, 112)]), poly_segs([(104, 144), (152, 144)])):
    dl += gapped(o, False)
icon('dna-slash', SC, ['dna', 'disabled', 'off', 'science'], line=dl + [SLASH])

# ================================================================ biohazard: three crescents opening outward
BIO_C = (128, 132)
BIO_D, BIO_R = 66, 30
bio_line, bio_area, bio_arcs = [], [], []
lobes = [polar(BIO_C, BIO_D, a) for a in (-90, 30, 150)]
for a, lc in zip((-90, 30, 150), lobes):
    ic = polar(BIO_C, BIO_D + 16, a)
    p, q = circle_x(lc, BIO_R, ic, 20)
    a0, a1 = ang(lc, p), ang(lc, q)
    span = (a1 - a0) % (2 * math.pi)
    if dist(polar(lc, BIO_R, math.degrees(a0 + span / 2)), BIO_C) > BIO_D:
        span = span - 2 * math.pi
    seg = ('A', lc, BIO_R, a0, a0 + span)
    bio_arcs.append([seg])
    d_ = segs_d([seg])
    bio_line.append(P(d_))
    bio_area.append(P(d_ + ' ' + arc_to(ic, 20, q, p, lambda m: -dist(m, BIO_C)) + ' Z'))
ring_keep = lambda p: all(dist(p, lc) - BIO_R >= 19 for lc in lobes)
ring_runs, _ = trim([('A', BIO_C, 50, -math.pi / 2, 1.5 * math.pi)], ring_keep)
for r in ring_runs:
    bio_line.append(P(segs_d(r)))
    bio_arcs.append(r)
icon('biohazard', SC, ['biohazard', 'danger', 'toxic', 'warning'], line=bio_line, area=bio_area, dot=[C(*BIO_C, 16)])
bs = []
for segs in bio_arcs:
    bs += gapped(segs, False)
icon('biohazard-slash', SC, ['biohazard', 'disabled', 'off', 'science'], line=bs + [SLASH])

# ================================================================ brain badges (brain's own outline, opened around the badge)
BRAIN_R = [arc_seg((128, 56), (184, 64), 32, 1), arc_seg((184, 64), (212, 112), 32, 1), arc_seg((212, 112), (204, 164), 32, 1),
           arc_seg((204, 164), (160, 204), 32, 1), arc_seg((160, 204), (128, 200), 32, 1)]
BRAIN_L = [arc_seg((128, 200), (96, 204), 32, 1), arc_seg((96, 204), (52, 164), 32, 1), arc_seg((52, 164), (44, 112), 32, 1),
           arc_seg((44, 112), (72, 64), 32, 1), arc_seg((72, 64), (128, 56), 32, 1)]
BRAIN = BRAIN_R + BRAIN_L
BRAIN_DET = [L(128, 72, 128, 148), P('M84 132 A28 28 0 0 1 100 104'), P('M172 132 A28 28 0 0 0 156 104')]


def brain_badge(cr, badge):
    ln, ar = carve(BRAIN, B, cr)
    out = dict(line=[P(ln)], area=[P(ar)], detail=list(BRAIN_DET))
    for k, v in badge.items():
        out[k] = out.get(k, []) + v
    return out


bolt = [(BX + x, BY + y) for x, y in [(6, -34), (-22, 6), (0, 6), (-6, 34), (22, -6), (0, -6)]]
icon('brain-lightning', SC, ['brainstorm', 'idea', 'neural'], **brain_badge(60, dict(line=[PG(bolt)], area=[PG(bolt)])))
icon('brain-magnifying-glass', SC, ['neuroscience', 'research', 'analysis'],
     **brain_badge(62, dict(line=[C(178, 178, 22), L(195, 195, 212, 212)], area=[C(178, 178, 22)])))

# ================================================================ measuring
cal_fixed = 'M112 64 H44 A12 12 0 0 0 32 76 V164 L72 204 V92 H112'
cal_jaw = 'M120 104 V204 L156 168 V104'
cal_beam = 'M164 64 H210 A14 14 0 0 1 210 92 H164'
icon('calipers', SC, ['calipers', 'measure', 'diameter', 'precision'],
     line=[P(cal_fixed), R(112, 52, 52, 52, 10), P(cal_jaw), P(cal_beam)],
     area=[P(cal_fixed + ' Z'), R(112, 52, 52, 52, 10), P(cal_jaw + ' Z'), P(cal_beam + ' Z')])
icon('diameter', SC, ['measure', 'circle size', 'diameter'],
     line=[C(128, 128, 96)], detail=[L(68, 128, 188, 128), PL([(92, 104), (68, 128), (92, 152)]), PL([(164, 104), (188, 128), (164, 152)])],
     area=[C(128, 128, 96)])

# ================================================================ circuit schematic symbols (lead wires on y=128)
CIR = ['circuit', 'electronics', 'schematic']
def ctags(nm, extra):
    return [nm] + CIR + [extra]


meter_c = (128, 128)
meter = dict(line=[C(128, 128, 64), L(32, 128, 64, 128), L(192, 128, 224, 128)], area=[C(128, 128, 64)])
icon('circuit-ammeter', SC, ctags('circuit ammeter', 'ammeter'),
     detail=[PL([(106, 156), (128, 100), (150, 156)]), L(114, 138, 142, 138)], **meter)
icon('circuit-voltmeter', SC, ctags('circuit voltmeter', 'voltmeter'),
     detail=[PL([(106, 100), (128, 156), (150, 100)])], **meter)
icon('circuit-motor', SC, ctags('circuit motor', 'motor'),
     detail=[PL([(102, 154), (102, 102), (128, 136), (154, 102), (154, 154)])], **meter)
icon('circuit-bulb', SC, ctags('circuit bulb', 'bulb'),
     detail=[L(*polar(meter_c, 34, 45), *polar(meter_c, 34, 225)), L(*polar(meter_c, 34, 135), *polar(meter_c, 34, -45))], **meter)

icon('circuit-battery', SC, ctags('circuit battery', 'battery'),
     line=[L(32, 128, 80, 128), L(80, 64, 80, 192), L(112, 96, 112, 160), L(144, 64, 144, 192), L(176, 96, 176, 160),
           L(176, 128, 224, 128)])
CELL = [L(32, 128, 112, 128), L(112, 64, 112, 192), L(144, 96, 144, 160), L(144, 128, 224, 128)]
icon('circuit-cell', SC, ctags('circuit cell', 'cell'), line=CELL)
icon('circuit-cell-plus', SC, ['circuit cell', 'add', 'new', 'circuit', 'electronics'],
     line=[L(32, 100, 112, 100), L(112, 36, 112, 164), L(144, 68, 144, 132), L(144, 100, 224, 100)] + plus_badge())
icon('circuit-capacitor', SC, ctags('circuit capacitor', 'capacitor'),
     line=[L(32, 128, 108, 128), L(108, 72, 108, 184), L(148, 72, 148, 184), L(148, 128, 224, 128)])
icon('circuit-capacitor-polarized', SC, ctags('circuit capacitor polarized', 'capacitor'),
     line=[L(32, 128, 104, 128), L(104, 72, 104, 184), P('M164 72 A80 80 0 0 0 164 184'),
           L(164 - (80 - math.sqrt(80 ** 2 - 56 ** 2)), 128, 224, 128), L(64, 60, 64, 92), L(48, 76, 80, 76)])
icon('circuit-resistor', SC, ctags('circuit resistor', 'resistor'),
     line=[PL([(32, 128), (56, 128), (68, 96), (92, 160), (116, 96), (140, 160), (164, 96), (188, 160), (200, 128), (224, 128)])])
icon('circuit-inductor', SC, ctags('circuit inductor', 'inductor'),
     line=[P('M32 144 H50 A26 26 0 0 1 102 144 A26 26 0 0 1 154 144 A26 26 0 0 1 206 144 H224')])
dio = [(88, 80), (168, 128), (88, 176)]
icon('circuit-diode', SC, ctags('circuit diode', 'diode'),
     line=[L(32, 128, 88, 128), PG(dio), L(168, 80, 168, 176), L(168, 128, 224, 128)], area=[PG(dio)])
icon('circuit-diode-zener', SC, ctags('circuit diode zener', 'diode'),
     line=[L(32, 128, 88, 128), PG(dio), PL([(148, 72), (168, 80), (168, 176), (188, 184)]), L(168, 128, 224, 128)], area=[PG(dio)])
icon('circuit-ground', SC, ctags('circuit ground', 'ground'),
     line=[L(128, 40, 128, 128), L(56, 128, 200, 128), L(84, 168, 172, 168), L(112, 208, 144, 208)])
gtri = [(64, 120), (192, 120), (128, 204)]
icon('circuit-ground-digital', SC, ctags('circuit ground digital', 'ground'),
     line=[L(128, 44, 128, 120), PG(gtri)], area=[PG(gtri)])


def term(c):
    return C(c[0], c[1], 16)


def edge_line(a, b, r=16):
    d = dist(a, b); ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
    return L(a[0] + ux * r, a[1] + uy * r, b[0] - ux * r, b[1] - uy * r)


icon('circuit-switch-open', SC, ctags('circuit switch open', 'switch'),
     line=[L(32, 152, 56, 152), term((72, 152)), term((184, 152)), L(200, 152, 224, 152),
           L(*polar((72, 152), 16, -32), *polar((72, 152), 132, -32))])
icon('circuit-switch-closed', SC, ctags('circuit switch closed', 'switch'),
     line=[L(32, 128, 56, 128), term((72, 128)), term((184, 128)), L(200, 128, 224, 128), edge_line((72, 128), (184, 128))])
icon('circuit-changeover', SC, ctags('circuit changeover', 'changeover'),
     line=[L(32, 128, 56, 128), term((72, 128)), term((184, 72)), term((184, 184)), L(200, 72, 224, 72), L(200, 184, 224, 184),
           edge_line((72, 128), (184, 72))])
icon('circuit-pushbutton', SC, ctags('circuit pushbutton', 'pushbutton'),
     line=[L(32, 176, 56, 176), term((72, 176)), term((184, 176)), L(200, 176, 224, 176), L(64, 128, 192, 128),
           L(128, 128, 128, 64), L(100, 64, 156, 64)])

# ================================================================ boards
icon('circuit-board', SC, ['circuit', 'electronics', 'pcb', 'traces'],
     line=[C(48, 64, 16), PL([(48, 80), (48, 128), (88, 168), (88, 224)]),
           C(128, 48, 16), L(128, 64, 128, 224),
           C(208, 96, 16), PL([(208, 112), (208, 128), (168, 168), (168, 224)])])
icon('circuitry', SC, ['circuit board', 'electronics', 'pcb'],
     line=[R(32, 32, 192, 192, 16)],
     detail=[PL([(72, 72), (72, 120), (112, 160), (184, 160)]), PL([(120, 72), (152, 72), (184, 104)])],
     dotcut=[C(72, 72, 16), C(184, 160, 16), C(120, 72, 16), C(184, 104, 16)],
     area=[R(32, 32, 192, 192, 16)])
icon('electronics-transistor', SC, ['transistor', 'electronics', 'circuit'],
     line=[C(128, 128, 96)],
     detail=[L(64, 128, 100, 128), L(100, 84, 100, 172), L(100, 108, 152, 72), L(100, 148, 152, 184),
             PL([(124, 182), (152, 184), (144, 158)])],
     area=[C(128, 128, 96)])

# ================================================================ logic gates
AND = 'M72 64 H128 A64 64 0 0 1 128 192 H72 Z'
icon('logic-and', SC, ['and gate', 'logic', 'circuit', 'boolean'],
     line=[P(AND), L(32, 96, 72, 96), L(32, 160, 72, 160), L(192, 128, 224, 128)], area=[P(AND)])
BUF = [(72, 64), (184, 128), (72, 192)]
icon('logic-buffer', SC, ['buffer gate', 'logic', 'circuit', 'boolean'],
     line=[PG(BUF), L(32, 128, 72, 128), L(184, 128, 224, 128)], area=[PG(BUF)])
NAND = 'M56 64 H112 A64 64 0 0 1 112 192 H56 Z'
icon('logic-nand', SC, ['nand gate', 'logic', 'circuit', 'boolean'],
     line=[P(NAND), C(194, 128, 18), L(32, 96, 56, 96), L(32, 160, 56, 160), L(212, 128, 224, 128)],
     area=[P(NAND), C(194, 128, 18)])

# ================================================================ space
hc = (84, 172)
icon('comet', SC, ['comet', 'space', 'astronomy'],
     line=[C(*hc, 44), L(*polar(hc, 44, -45), 208, 48),
           L(*polar(hc, 44, -135), *polar(polar(hc, 44, -135), 92, -45)),
           L(*polar(hc, 44, 45), *polar(polar(hc, 44, 45), 92, -45))],
     area=[C(*hc, 44)])
arms = []
for off in (0, 180):
    pts = []
    for k in range(0, 91):
        th = math.radians(k * 3)  # 0..270 deg
        r_ = 32 + 64 * (k / 90)
        pts.append(polar((128, 128), r_, off + math.degrees(th)))
    arms.append(PL(pts))
icon('galaxy', SC, ['galaxy', 'space', 'spiral', 'astronomy'], line=arms, dot=[C(128, 128, 16)])

# ================================================================ heads & energy
HEAD = load('head-heart')
icon('head-circuit', SC, ['ai', 'machine learning', 'robot mind'],
     line=HEAD['line'], area=HEAD['area'],
     detail=[PL([(88, 132), (88, 112), (112, 88), (136, 88)]), PL([(124, 136), (156, 136)])],
     dotcut=[C(136, 88, 16), C(88, 140, 16), C(164, 136, 16), C(116, 136, 16)])
sb = [(128 + (x - 128) * 0.44, 128 + (y - 128) * 0.44) for x, y in [(144, 32), (56, 144), (120, 144), (104, 224), (200, 108), (136, 108)]]
ew = []
for r_ in (64, 96):
    for base in (0, 180):
        ew.append(P(f'M{pt(polar((128, 128), r_, base - 38))} A{r_} {r_} 0 0 1 {pt(polar((128, 128), r_, base + 38))}'))
icon('electricity-waves', SC, ['electricity', 'power', 'energy waves', 'current'], line=[PG(sb)] + ew, area=[PG(sb)])

# ================================================================ LEDs
dome = 'M80 160 V104 A48 48 0 0 1 176 104 V160'
icon('led', SC, ['led', 'diode', 'light', 'electronics'],
     line=[P(dome), L(64, 160, 192, 160), L(104, 160, 104, 224), L(152, 160, 152, 208)], area=[P(dome + ' Z')])
cl = lambda x: 128 - 24 * math.sin(2 * math.pi * (x - 40) / 176)
xs = [40 + k * 2 for k in range(89)]
band = [(x, cl(x) - 32) for x in xs] + [(x, cl(x) + 32) for x in reversed(xs)]
icon('led-strip', 'Home', ['light strip', 'led', 'smart light', 'decoration'],
     line=[PG(band)], area=[PG(band)], dotcut=[C(x, cl(x), 14) for x in (62, 106, 150, 194)])

# ================================================================ optics
cr_ = (88 ** 2 + 28 ** 2) / 56
icon('lens-concave', SC, ['concave lens', 'optics', 'physics', 'diverging'],
     line=[P(f'M68 40 H188 A{f(cr_)} {f(cr_)} 0 0 0 188 216 H68 A{f(cr_)} {f(cr_)} 0 0 0 68 40 Z')],
     area=[P(f'M68 40 H188 A{f(cr_)} {f(cr_)} 0 0 0 188 216 H68 A{f(cr_)} {f(cr_)} 0 0 0 68 40 Z')])
vr = (96 ** 2 + 52 ** 2) / 104
icon('lens-convex', SC, ['convex lens', 'optics', 'physics', 'magnify'],
     line=[P(f'M128 32 A{f(vr)} {f(vr)} 0 0 1 128 224 A{f(vr)} {f(vr)} 0 0 1 128 32 Z')],
     area=[P(f'M128 32 A{f(vr)} {f(vr)} 0 0 1 128 224 A{f(vr)} {f(vr)} 0 0 1 128 32 Z')])

print(save(overwrite=True))
