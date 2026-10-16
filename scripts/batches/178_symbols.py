import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

import pathops
from fontTools.pens.basePen import BasePen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.svgLib.path import parse_path

SLASH = L(48, 48, 208, 208)
CC = (128, 128)


# ---------------------------------------------------------------- local helpers
def _pp(ds):
    p = pathops.Path()
    pen = p.getPen()
    for d in ds:
        parse_path(d, pen)
    return p


def _d(p):
    p.convertConicsToQuads(0.05)
    pen = SVGPathPen(None, f)
    p.draw(pen)
    return pen.getCommands()


class _Flat(BasePen):
    def __init__(self, step=3):
        super().__init__(None)
        self.subs, self.step = [], step

    def _moveTo(self, p):
        self.subs.append([p])

    def _lineTo(self, p):
        a = self.subs[-1][-1]
        n = max(1, int(dist(a, p) / self.step))
        self.subs[-1] += [(a[0] + (p[0] - a[0]) * i / n, a[1] + (p[1] - a[1]) * i / n) for i in range(1, n + 1)]

    def _curveToOne(self, p1, p2, p3):
        p0 = self.subs[-1][-1]
        n = max(2, int((dist(p0, p1) + dist(p1, p2) + dist(p2, p3)) / self.step))
        for i in range(1, n + 1):
            t = i / n; u = 1 - t
            self.subs[-1].append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                                  u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))

    def _qCurveToOne(self, p1, p2):
        p0 = self.subs[-1][-1]
        self._curveToOne((p0[0] + 2 / 3 * (p1[0] - p0[0]), p0[1] + 2 / 3 * (p1[1] - p0[1])),
                         (p2[0] + 2 / 3 * (p1[0] - p2[0]), p2[1] + 2 / 3 * (p1[1] - p2[1])), p2)

    def _closePath(self):
        s = self.subs[-1]
        if dist(s[-1], s[0]) > 0.01:
            self._lineTo(s[0])
        self.subs[-1].append('closed')

    _endPath = lambda self: None


def flatten(d, step=3):
    pen = _Flat(step)
    parse_path(d, pen)
    out = []
    for s in pen.subs:
        closed = s[-1] == 'closed'
        out.append(([p for p in s if p != 'closed'], closed))
    return out


def _seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def _runs_d(runs):
    return [P('M' + ' L'.join(pt(p) for p in r)) for r in runs if len(r) > 1]


def split_by(d, keep, step=2):
    """Pieces of path d whose points satisfy keep(p)."""
    out = []
    for pts, closed in flatten(d, step):
        runs, cur = [], []
        for p in pts:
            if keep(p):
                cur.append(p)
            elif cur:
                runs.append(cur); cur = []
        if cur:
            runs.append(cur)
        if closed and len(runs) > 1 and runs[0][0] == pts[0] and runs[-1][-1] == pts[-1]:
            runs[0] = runs.pop() + runs[0][1:]
        out += _runs_d(runs)
    return out


def occlude(d, front, gap=20, step=2):
    """Parts of path d that stay `gap` units clear of the closed shapes in `front`."""
    fp = _pp(front)
    edges = []
    for pts, _ in sum((flatten(x, 2) for x in front), []):
        edges += list(zip(pts, pts[1:]))
    return split_by(d, lambda p: not fp.contains(p) and all(_seg_dist(p, a, b) >= gap for a, b in edges), step)


def inside_part(d, front, step=2):
    fp = _pp(front)
    return split_by(d, lambda p: fp.contains(p), step)


def heart_path(c, s):
    # the core heart (centre ~ (128,140)) scaled by s around c
    def q(x, y):
        return pt((c[0] + (x - 128) * s, c[1] + (y - 140) * s))
    r = f(50 * s)
    return (f'M{q(128, 212)} C{q(128, 212)} {q(32, 160)} {q(32, 98)} A{r} {r} 0 0 1 {q(128, 78)} '
            f'A{r} {r} 0 0 1 {q(224, 98)} C{q(224, 160)} {q(128, 212)} {q(128, 212)} Z')


def slashed(roles):
    """Slash variant: everything stroked becomes line, dotcuts become dots, no area."""
    return dict(line=roles.get('line', []) + roles.get('detail', []) + [SLASH],
                dot=roles.get('dot', []) + roles.get('dotcut', []))


def c_arc(c, r, open_deg, facing=0):
    """A 'C' arc around c opening towards `facing` degrees with half-opening open_deg."""
    a = polar(c, r, facing - open_deg)
    b = polar(c, r, facing + open_deg)
    return P(f'M{pt(a)} A{f(r)} {f(r)} 0 1 0 {pt(b)}')


# ================================================================ Sports
tro = load('trophy')
icon('trophy-slash', 'Sports', ['trophy', 'off', 'disabled', 'hidden'], **slashed(tro))

# volleyball: three swirling seams from the centre, each with a parallel companion
vb = []
for k in range(3):
    th = -90 + k * 120
    end = polar(CC, 96, th)
    vb.append(P(f'M{pt(CC)} A96 96 0 0 1 {pt(end)}'))
icon('volleyball', 'Sports', ['volleyball', 'ball', 'beach', 'net', 'sport'],
     line=[C(128, 128, 96)], detail=vb, area=[C(128, 128, 96)])

# water polo: swimmer head, raised arm, ball, waves
WAVE = lambda y: P(f'M32 {y} Q48 {y - 15} 64 {y} T96 {y} T128 {y} T160 {y} T192 {y} T224 {y}')
icon('water-polo', 'Sports', ['water polo', 'swimming', 'ball', 'pool', 'swim'],
     line=[C(76, 108, 24), C(172, 68, 32), P('M48 168 C56 152 76 146 100 150 L150 102'), WAVE(184), WAVE(216)],
     area=[C(76, 108, 24), C(172, 68, 32)])

# weight: kettlebell
kb_c, kb_r = (128, 156), 68
hx = math.sqrt(kb_r ** 2 - (216 - kb_c[1]) ** 2)
kb = f'M{pt((128 - hx, 216))} A{kb_r} {kb_r} 0 1 1 {pt((128 + hx, 216))} Z'
hy = kb_c[1] - math.sqrt(kb_r ** 2 - 40 ** 2)
icon('weight', 'Sports', ['weight', 'kettlebell', 'heavy', 'kg'],
     line=[P(kb), P('M80 112 L70 66 A24 24 0 0 1 94 36 H162 A24 24 0 0 1 186 66 L176 112')], area=[P(kb)])

# whistle
wc, wr = (104, 144), 64
wy = 120
wx = wc[0] + math.sqrt(wr ** 2 - (wy - wc[1]) ** 2)
wh = f'M104 80 H208 A8 8 0 0 1 216 88 V112 A8 8 0 0 1 208 120 H{f(wx)} A{wr} {wr} 0 1 1 104 80 Z'
icon('whistle', 'Sports', ['whistle', 'referee', 'coach', 'sports'],
     line=[P(wh)], detail=[C(104, 144, 24)], area=[P(wh)])

# yoga: seated lotus pose
icon('yoga', 'Sports', ['yoga', 'meditation', 'pose', 'wellness'],
     line=[C(128, 60, 24), L(128, 104, 128, 168),
           P('M128 112 C104 116 88 136 72 168'), P('M128 112 C152 116 168 136 184 168'),
           P('M40 200 C72 176 104 176 128 188 C152 176 184 176 216 200')],
     area=[C(128, 60, 24)])

# ================================================================ Symbols
ank = 'M128 124 C100 104 88 84 88 72 A40 40 0 0 1 168 72 C168 84 156 104 128 124 Z'
icon('ankh', 'Symbols', ['ankh', 'egypt', 'life', 'symbol'],
     line=[P(ank), L(128, 124, 128, 224), L(56, 148, 200, 148)], area=[P(ank)])


def tilde(y):
    return P(f'M48 {y + 12} C64 {y - 12} 104 {y - 16} 128 {y} C152 {y + 16} 192 {y + 12} 208 {y - 12}')


icon('approximate-equals', 'Symbols', ['approximately', 'about', 'similar'], line=[tilde(100), tilde(156)])

# @ inside a circle
ri, ro = 24, 62
tr = (ro - ri) / 2
tx = 128 + ri
at_d = (f'M{f(tx)} {f(128 - ri)} V140 A{f(tr)} {f(tr)} 0 0 0 {f(tx + 2 * tr)} 140 V128 '
        f'A{ro} {ro} 0 1 0 {pt(polar(CC, ro, 58))}')
icon('at-circle', 'Symbols', ['email', 'mention', 'at sign'],
     line=[C(128, 128, 96)], detail=[C(128, 128, ri), P(at_d)], area=[C(128, 128, 96)])

icon('circle-dot', 'Symbols', ['concentric', 'circle', 'dot', 'radio'],
     line=[C(128, 128, 96)], detail=[C(128, 128, 44)], area=[C(128, 128, 96)])

# Confucian symbol: a stylised water glyph
icon('confucius', 'Symbols', ['confucianism', 'religion', 'symbol'],
     line=[PL([(128, 36), (128, 204), (104, 188)]), PL([(52, 96), (96, 96), (48, 184)]),
           L(160, 108, 200, 72), L(160, 108, 212, 192)])

CR = 48
icon('copyright', 'Symbols', ['copyright', 'legal', 'c', 'license'],
     line=[C(128, 128, 96)], detail=[c_arc(CC, CR, 48, 0)], area=[C(128, 128, 96)])
icon('copyleft', 'Symbols', ['copyleft', 'license', 'open source', 'reverse c'],
     line=[C(128, 128, 96)], detail=[c_arc(CC, CR, 48, 180)], area=[C(128, 128, 96)])
icon('copyright-slash', 'Symbols', ['copyright', 'disabled', 'off', 'symbols', 'no copyright'],
     line=[C(128, 128, 96), c_arc(CC, CR, 48, 0), SLASH])
icon('copyleft-slash', 'Symbols', ['copyleft', 'disabled', 'off', 'symbols'],
     line=[C(128, 128, 96), c_arc(CC, CR, 48, 180), SLASH])

# creative commons family
CC2 = [c_arc((92, 128), 26, 50, 0), c_arc((164, 128), 26, 50, 0)]
icon('creative-commons', 'Symbols', ['creative commons', 'license', 'cc', 'copyright', 'open'],
     line=[C(128, 128, 96)], detail=CC2, area=[C(128, 128, 96)])
icon('creative-commons-slash', 'Symbols', ['creative commons', 'disabled', 'off', 'symbols', 'no creative commons'],
     line=[C(128, 128, 96)] + CC2 + [SLASH])
icon('creative-commons-by', 'Symbols', ['attribution', 'cc by', 'license', 'credit'],
     line=[C(128, 128, 96)],
     detail=[L(128, 108, 128, 156), L(88, 120, 168, 120), PL([(110, 192), (128, 156), (146, 192)])],
     dotcut=[C(128, 76, 16)], area=[C(128, 128, 96)])
dollar = ('M154 102 C150 92 140 88 128 88 C112 88 102 96 102 108 C102 134 154 122 154 148 '
          'C154 160 144 168 128 168 C116 168 106 164 102 154')
icon('creative-commons-nc', 'Symbols', ['non commercial', 'cc nc', 'license', 'no money'],
     line=[C(128, 128, 96)],
     detail=[P(dollar), L(128, 68, 128, 188), L(*polar(CC, 70, -135), *polar(CC, 70, 45))],
     area=[C(128, 128, 96)])
icon('creative-commons-nd', 'Symbols', ['no derivatives', 'creative commons', 'license', 'equals', 'cc nd'],
     line=[C(128, 128, 96)], detail=[L(80, 108, 176, 108), L(80, 148, 176, 148)], area=[C(128, 128, 96)])
sa_end = polar(CC, 44, 210)
sa_dir = (math.sin(math.radians(210)), -math.cos(math.radians(210)))  # travel direction at the end
wing = lambda s: (sa_end[0] - 26 * (sa_dir[0] * math.cos(s) - sa_dir[1] * math.sin(s)),
                  sa_end[1] - 26 * (sa_dir[0] * math.sin(s) + sa_dir[1] * math.cos(s)))
icon('creative-commons-sa', 'Symbols', ['share alike', 'cc sa', 'license', 'loop'],
     line=[C(128, 128, 96)],
     detail=[P(f'M{pt(polar(CC, 44, 150))} A44 44 0 1 0 {pt(sa_end)}'),
             PL([wing(math.radians(45)), sa_end, wing(math.radians(-45))])],
     area=[C(128, 128, 96)])
icon('creative-commons-zero', 'Symbols', ['public domain', 'cc0', 'license', 'zero'],
     line=[C(128, 128, 96)], detail=[E(128, 128, 32, 50), L(144, 100, 112, 156)], area=[C(128, 128, 96)])
icon('creative-commons-public-domain', 'Symbols', ['public domain', 'license', 'no copyright', 'pd'],
     line=[C(128, 128, 96)],
     detail=[c_arc(CC, CR, 48, 0), L(*polar(CC, 70, -135), *polar(CC, 70, 45))], area=[C(128, 128, 96)])

# curly loop
icon('curly-loop', 'Symbols', ['loop', 'curly', 'symbol'],
     line=[P('M32 184 C100 184 180 160 180 104 A52 52 0 0 0 76 104 C76 160 156 184 224 184')])

icon('divide-circle', 'Symbols', ['divide', 'division', 'math', 'circle'],
     line=[C(128, 128, 96)], detail=[L(80, 128, 176, 128)], dotcut=[C(128, 88, 16), C(128, 168, 16)],
     area=[C(128, 128, 96)])
icon('divide-square', 'Symbols', ['divide', 'division', 'math', 'square'],
     line=[R(32, 32, 192, 192, 16)], detail=[L(80, 128, 176, 128)], dotcut=[C(128, 88, 16), C(128, 168, 16)],
     area=[R(32, 32, 192, 192, 16)])

icon('dot', 'Symbols', ['dot', 'point', 'bullet', 'small circle'], dot=[C(128, 128, 56)])
icon('dot-slash', 'Symbols', ['dot', 'off', 'disabled', 'hidden'], line=[SLASH], dot=[C(128, 128, 56)])

# easter egg
egg = 'M128 32 C172 32 200 108 200 148 A72 72 0 0 1 56 148 C56 108 84 32 128 32 Z'
icon('easter-egg', 'Symbols', ['easter egg', 'decorated egg', 'holiday', 'spring'],
     line=[P(egg)],
     detail=[PL([(88, 132), (108, 112), (128, 132), (148, 112), (168, 132)]), L(92, 176, 164, 176)],
     area=[P(egg)])

icon('empty-set', 'Symbols', ['empty', 'empty set', 'null', 'void'],
     line=[C(128, 128, 72), L(*polar(CC, 100, -60), *polar(CC, 100, 120))])
icon('equals-circle', 'Symbols', ['equals', 'math', 'result', 'circle'],
     line=[C(128, 128, 96)], detail=[L(84, 104, 172, 104), L(84, 152, 172, 152)], area=[C(128, 128, 96)])

EXC = dict(line=[L(128, 40, 128, 152)], dot=[C(128, 204, 20)])
icon('exclamation-mark', 'Symbols', ['exclamation', 'alert', 'important', 'bang', 'priority'], **EXC)
icon('exclamation-mark-slash', 'Symbols', ['exclamation mark', 'disabled', 'off', 'symbols'], **slashed(EXC))

# fallout shelter: three downward triangles
tri = []
for th in (-150, -30, 90):
    cx, cy = polar(CC, 46, th)
    tri.append(PG([(cx - 24, cy - 14), (cx + 24, cy - 14), (cx, cy + 28)]))
icon('fallout-shelter', 'Symbols', ['radiation shelter', 'bunker', 'nuclear'],
     line=[C(128, 128, 96)], detail=tri, hole=tri, area=[C(128, 128, 96)])

fire = load('fire')
icon('fire-slash', 'Symbols', ['no fire', 'no open flame', 'fire off', 'prohibited'], **slashed(fire))

fw = [L(*polar(CC, 40, a), *polar(CC, 92, a)) for a in range(0, 360, 90)]
fw += [L(*polar(CC, 40, a), *polar(CC, 64, a)) for a in range(45, 360, 90)]
icon('fireworks', 'Symbols', ['fireworks', 'celebration', 'new year', 'festival'],
     line=fw, dot=[C(*polar(CC, 90, a), 16) for a in range(45, 360, 90)] + [C(128, 128, 16)])

# gender
icon('gender-ambiguous', 'Symbols', ['gender', 'ambiguous', 'nonbinary', 'symbol'],
     line=[C(128, 164, 56), L(128, 108, 128, 36), L(104, 44, 152, 76), L(152, 44, 104, 76)],
     area=[C(128, 164, 56)])
icon('gender-neuter', 'Symbols', ['genderless', 'neuter', 'gender', 'symbol', 'agender'],
     line=[C(128, 96, 64), L(128, 160, 128, 224)], area=[C(128, 96, 64)])
tg, tgr = (128, 136), 40
ar = polar(tg, tgr, -45); al = polar(tg, tgr, -135)
xb = (52 + 33, 60 + 33)
icon('gender-transgender', 'Symbols', ['transgender', 'gender', 'trans', 'symbol', 'lgbt'],
     line=[C(*tg, tgr), L(*ar, 204, 60), PL([(180, 60), (204, 60), (204, 84)]),
           L(*al, 52, 60), PL([(76, 60), (52, 60), (52, 84)]),
           L(xb[0] + 12, xb[1] - 12, xb[0] - 12, xb[1] + 12),
           L(128, 176, 128, 224), L(104, 204, 152, 204)],
     area=[C(*tg, tgr)])

icon('greater-than', 'Symbols', ['greater than', 'compare', 'math', 'comparison', 'symbol'],
     line=[PL([(64, 56), (192, 128), (64, 200)])])
icon('greater-than-or-equal', 'Symbols',
     ['greater or equal', 'compare', 'math', 'greater than or equal', 'comparison'],
     line=[PL([(64, 40), (192, 100), (64, 160)]), L(64, 208, 192, 208)])

sh = 'M60 224 C60 190 92 178 128 178 C164 178 196 190 196 224'
icon('halo', 'Symbols', ['halo', 'angel', 'saint', 'ring'],
     line=[E(128, 56, 60, 20), C(128, 130, 32), P(sh)], area=[C(128, 130, 32), P(sh + ' Z')])

# heart pierced by an arrow
hp = heart_path((120, 140), 0.68)
shaft = 'M48 208 L208 48'
outside = occlude(shaft, [hp], gap=0)
icon('heart-arrow', 'Symbols', ['love', 'cupid', 'valentine', 'romance'],
     line=[P(hp)] + outside + [PL([(180, 48), (208, 48), (208, 76)]),
                               PL([(44, 188), (68, 188), (68, 212)])],
     area=[P(hp)])

hc = load('heart-check')
icon('heart-arrow-up', 'Interface', ['heart', 'upload', 'up', 'increase'],
     line=[hc['line'][0], L(184, 212, 184, 156), PL([(164, 176), (184, 156), (204, 176)])], area=hc['area'])
icon('heart-arrow-down', 'Interface', ['heart', 'download', 'down', 'decrease'],
     line=[hc['line'][0], L(184, 156, 184, 212), PL([(164, 192), (184, 212), (204, 192)])], area=hc['area'])

HEART = 'M128 212 C128 212 32 160 32 98 A50 50 0 0 1 128 78 A50 50 0 0 1 224 98 C224 160 128 212 128 212 Z'
icon('heart-question', 'Symbols', ['love question', 'unsure', 'heart', 'quiz'],
     line=[P(HEART)], detail=[P('M108 120 A20 20 0 1 1 138 137 C132 140 128 144 128 150 V152')],
     dotcut=[C(128, 180, 14)], area=[P(HEART)])

# two overlapping hearts
hA = heart_path((98, 110), 0.68)
hB = heart_path((158, 150), 0.68)
A_vis = occlude(hA, [hB], gap=20)
B_out = occlude(hB, [hA], gap=0)
B_in = inside_part(hB, [hA])
icon('hearts', 'Symbols', ['hearts', 'love', 'romance', 'valentine'],
     line=A_vis + B_out, detail=B_in, area=[P(hA), P(hB)])
icon('hearts-slash', 'Symbols', ['hearts', 'off', 'disabled', 'hidden'], line=A_vis + [P(hB), SLASH])

# horseshoe
hs_c, ro_, ri_ = (128, 124), 92, 46
oL, oR = polar(hs_c, ro_, 116), polar(hs_c, ro_, 64)
iL, iR = polar(hs_c, ri_, 112), polar(hs_c, ri_, 68)
hs = f'M{pt(oL)} A{ro_} {ro_} 0 1 1 {pt(oR)} L{pt(iR)} A{ri_} {ri_} 0 1 0 {pt(iL)} Z'
mid = (ro_ + ri_) / 2
nails = [C(*polar(hs_c, mid, a), 10) for a in (150, 195, 240, 300, 345, 30)]
icon('horseshoe', 'Symbols', ['horseshoe', 'luck', 'horse', 'fortune'],
     line=[P(hs)], dotcut=nails, area=[P(hs)])

# ichthys
ich = 'M36 76 C96 204 180 188 220 128 C180 68 96 52 36 180'
icon('ichthys', 'Symbols', ['ichthys', 'christian fish', 'religion', 'faith'], line=[P(ich)], area=[P(ich + ' Z')])

inf = load('infinity')
icon('infinity-slash', 'Symbols', ['infinity', 'off', 'disabled', 'hidden'], **slashed(inf))


# laurel wreath: two curved branches of lens leaves
def leaf(base, ang, ln=42, w=16):
    tip = polar(base, ln, ang)
    m = polar(base, ln / 2, ang)
    n1 = polar(m, w, ang - 90); n2 = polar(m, w, ang + 90)
    return P(f'M{pt(base)} Q{pt(polar(n1, w * 0.6, ang - 90))} {pt(tip)} Q{pt(polar(n2, w * 0.6, ang + 90))} {pt(base)} Z')


lw_c, lw_r = (128, 124), 68
lines, areas = [], []
for side in (1, -1):
    a0, a1 = 100, 214
    if side == 1:
        p0, p1 = polar(lw_c, lw_r, a0), polar(lw_c, lw_r, a1)
        lines.append(P(f'M{pt(p0)} A{lw_r} {lw_r} 0 0 1 {pt(p1)}'))
    else:
        p0, p1 = polar(lw_c, lw_r, 180 - a0), polar(lw_c, lw_r, 180 - a1)
        lines.append(P(f'M{pt(p0)} A{lw_r} {lw_r} 0 0 0 {pt(p1)}'))
    for a in (132, 166, 200):
        aa = a if side == 1 else 180 - a
        base = polar(lw_c, lw_r, aa)
        out = aa  # outward direction
        tang = aa + 90 if side == 1 else aa - 90  # direction of travel up the branch
        lf = leaf(base, aa + (62 if side == 1 else -62))
        lines.append(lf); areas.append(lf)
    tip = polar(lw_c, lw_r, a1 if side == 1 else 180 - a1)
    lf = leaf(tip, (a1 + 80) if side == 1 else (180 - a1 - 80))
    lines.append(lf); areas.append(lf)
icon('laurel-wreath', 'Symbols', ['laurel', 'wreath', 'award', 'victory'], line=lines, area=areas)

print(save(overwrite=True))
