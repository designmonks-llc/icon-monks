import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

MP = 'Maps'
LN = 'Letters & Numbers'
SLASH = L(48, 48, 208, 208)
B = (184, 184)


def rpoly(points, r):
    """Closed polygon with corners rounded by quadratic curves of cut length r (clamped to half each edge)."""
    n = len(points)
    d = ''
    for i in range(n):
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        l1, l2 = dist(p0, p1), dist(p1, p2)
        k1, k2 = min(r, l1 / 2), min(r, l2 / 2)
        a = (p1[0] + (p0[0] - p1[0]) * k1 / l1, p1[1] + (p0[1] - p1[1]) * k1 / l1)
        b = (p1[0] + (p2[0] - p1[0]) * k2 / l2, p1[1] + (p2[1] - p1[1]) * k2 / l2)
        d += (f'M{pt(a)}' if i == 0 else f' L{pt(a)}') + f' Q{pt(p1)} {pt(b)}'
    return d + ' Z'


# ======================================================================= numbers (metrics of batch 156)
class G:
    def __init__(self, s=1.0, cx=128, cy=128):
        self.s, self.cx, self.cy = s, cx, cy

    def p(self, x, y):
        return (self.cx + (x - 128) * self.s, self.cy + (y - 128) * self.s)

    def P(self, x, y):
        return pt(self.p(x, y))

    def r(self, v):
        return f(v * self.s)

    def line(self, pts):
        return PL([self.p(*q) for q in pts])


def ept(c, rx, ry, deg):
    a = math.radians(deg)
    return (c[0] + rx * math.cos(a), c[1] + ry * math.sin(a))


def earc(g, c, rx, ry, a0, a1):
    q = ept(c, rx, ry, a1)
    span = a1 - a0
    return f'A{g.r(rx)} {g.r(ry)} 0 {1 if abs(span) > 180 else 0} {1 if span > 0 else 0} {g.P(*q)}'


def tangent_pt(p, c, r, side):
    dx, dy = c[0] - p[0], c[1] - p[1]
    d = math.hypot(dx, dy)
    base = math.atan2(-dy, -dx)
    off = math.acos(r / d)
    a = base + side * off
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def g_6pts():
    c, r = (128, 162), 46
    top = (156, 48)
    t = tangent_pt(top, c, r, +1)
    if t[0] > c[0]:
        t = tangent_pt(top, c, r, -1)
    return c, r, top, t


def g_9(g):
    # number-6 of batch 156 turned 180 degrees about the glyph centre
    c, r, top, t = g_6pts()
    fl = lambda q: (256 - q[0], 256 - q[1])
    c, top, t = fl(c), fl(top), fl(t)
    return [g.line([top, t]), C(*g.p(*c), float(g.r(r)))]


def g_1(g):
    return [g.line([(88, 82), (136, 48), (136, 208)]), g.line([(92, 208), (180, 208)])]


def g_1s(g):
    return [g.line([(100, 82), (148, 48), (148, 208)])]


def g_2(g):
    c, r = (128, 92), 44
    start = 200
    end_pt = (80, 208)
    t = max(tangent_pt(end_pt, c, r, +1), tangent_pt(end_pt, c, r, -1))
    ta = math.degrees(math.atan2(t[1] - c[1], t[0] - c[0])) % 360
    a = ept(c, r, r, start)
    return [P(f'M{g.P(*a)} ' + earc(g, c, r, r, start - 360, ta) + f' L{g.P(*end_pt)} L{g.P(180, 208)}')]


def g_3(g):
    x, t, b = 80, 48, 208
    r1, r2 = 36, 44
    ym = t + 2 * r1
    a1, a2 = 176 - 8 - r1, 176 - r2
    return [P(f'M{g.P(x, t)} H{f(g.p(a1, 0)[0])} A{g.r(r1)} {g.r(r1)} 0 0 1 {g.P(a1, ym)} H{f(g.p(108, 0)[0])}'),
            P(f'M{g.P(108, ym)} H{f(g.p(a2, 0)[0])} A{g.r(r2)} {g.r(r2)} 0 0 1 {g.P(a2, b)} H{f(g.p(x, 0)[0])}')]


S_BARE, S_CIRC, S_SQ = 176 / 160, 92 / 160, 104 / 160
CIRC = C(128, 128, 96)
SQ = R(32, 32, 192, 192, 16)
icon('number-9', LN, ['nine', '9', 'digit', 'number 9', 'numeral'], line=g_9(G(S_BARE)))
icon('number-9-circle', LN, ['number 9', 'nine', 'digit', 'circle', '9'], line=[CIRC], area=[CIRC],
     detail=g_9(G(S_CIRC)))
icon('number-9-square', LN, ['number 9', 'nine', 'digit', 'square', '9'], line=[SQ], area=[SQ],
     detail=g_9(G(S_SQ)))

# 1 2 3 at a cap height of 88, one stroke family with the digits above
SN = 88 / 160
icon('numbers', LN, ['numbers', '123', 'digits', 'numeric'],
     line=g_1s(G(SN, cx=50)) + g_2(G(SN, cx=124)) + g_3(G(SN, cx=196)))

# ======================================================================= landmarks
# altitude: mountain with an up arrow
mtn = [(32, 208), (100, 64), (168, 208)]
snow = [(68.4, 132), (84, 146), (100, 130), (116, 146), (131.6, 132)]
icon('altitude', MP, ['elevation', 'height', 'mountain', 'above sea level'],
     line=[PG(mtn), L(204, 208, 204, 48), PL([(176, 76), (204, 48), (232 - 8, 68)])],
     detail=[PL(snow)], area=[PG(mtn)])

# anchor-slash (anchor.svg is line-only)
anc = load('anchor')
icon('anchor-slash', MP, ['anchor', 'disabled', 'off', 'maps'], line=anc['line'] + [SLASH])

# ancient gate (paifang): sweeping roof, two posts, a lintel and a centre plaque
roof = 'M32 92 C56 92 68 80 76 56 H180 C188 80 200 92 224 92 Z'
icon('ancient-gate', MP, ['paifang', 'gate', 'landmark', 'temple'],
     line=[P(roof), L(128, 56, 128, 32), L(72, 92, 72, 216), L(184, 92, 184, 216), L(44, 144, 212, 144),
           L(128, 92, 128, 144)],
     area=[P(roof)])

# arc de triomphe: broad block, attic cornice, tall central arch
adt = 'M40 216 V56 A16 16 0 0 1 56 40 H200 A16 16 0 0 1 216 56 V216 H164 V148 A36 36 0 0 0 92 148 V216 Z'
icon('arc-de-triomphe', MP, ['landmark', 'paris', 'monument', 'arch'],
     line=[P(adt), L(24, 216, 92, 216), L(164, 216, 232, 216)], detail=[L(72, 80, 184, 80)], area=[P(adt)])

# arch: triumphal arch with a narrower attic on top
arch = 'M40 216 V96 H72 V48 H184 V96 H216 V216 H160 V156 A32 32 0 0 0 96 156 V216 Z'
icon('arch', MP, ['arch', 'monument', 'gate'], line=[P(arch)], area=[P(arch)])

# archway: thick stone arch with joints
ac = (128, 128)
aw = 'M40 216 V128 A88 88 0 0 1 216 128 V216 H168 V128 A40 40 0 0 0 88 128 V216 Z'
joints = [L(*polar(ac, 48, a), *polar(ac, 80, a)) for a in (-140, -90, -40)] + [L(48, 176, 80, 176), L(176, 176, 208, 176)]
icon('archway', MP, ['arch', 'gate', 'monument', 'entrance'], line=[P(aw)], detail=joints, area=[P(aw)])

# barrier block: striped board on two legs
board = R(32, 56, 192, 80, 16)
stripes = [L(x - 14, 112, x + 14, 80) for x in (80, 128, 176)]
legs = [L(72, 136, 72, 208), L(184, 136, 184, 208), L(48, 208, 96, 208), L(160, 208, 208, 208)]
icon('barrier-block', MP, ['barrier block', 'barrier', 'block', 'maps'],
     line=[board] + legs, detail=stripes, area=[board])
icon('barrier-block-slash', MP, ['barrier block', 'disabled', 'off', 'maps'],
     line=[board] + legs + stripes + [SLASH])

# bridge: arch over the deck with hangers, piers below
barc = 'M40 160 A88 80 0 0 1 216 160'
hang = []
for x in (84, 128, 172):
    y = 160 - 80 * math.sqrt(1 - ((x - 128) / 88) ** 2)
    hang.append(L(x, y + 24, x, 136))
icon('bridge', MP, ['bridge', 'crossing', 'river', 'landmark'],
     line=[P(barc), L(24, 160, 232, 160), L(64, 160, 64, 208), L(192, 160, 192, 208)],
     detail=hang, area=[P(barc + ' Z')])

# apartment block: grid of windows, door
apt = R(48, 32, 160, 184, 16)
icon('building-apartment', MP, ['apartment', 'residential', 'block'],
     line=[P('M48 216 V48 A16 16 0 0 1 64 32 H192 A16 16 0 0 1 208 48 V216'), L(24, 216, 232, 216),
           P('M108 216 V184 H148 V216')],
     dotcut=[C(x, y, 12) for x in (88, 128, 168) for y in (72, 108, 144)],
     area=[P('M48 216 V48 A16 16 0 0 1 64 32 H192 A16 16 0 0 1 208 48 V216 Z')],
     hole=[P('M116 216 V192 H140 V216 Z')])

# burj khalifa: stepped, tapering tower with a spire
bk = [(76, 208), (76, 160), (96, 160), (96, 112), (112, 112), (112, 76), (128, 60),
      (144, 76), (144, 132), (160, 132), (160, 176), (180, 176), (180, 208)]
icon('burj-khalifa', MP, ['skyscraper', 'dubai', 'tower', 'landmark'],
     line=[PL(bk), L(128, 56, 128, 32), L(56, 208, 200, 208)], area=[PG(bk)])

# castle: two crenellated towers, curtain wall, gate
cas = ('M40 216 V48 H56 V72 H84 V48 H100 V112 H156 V48 H172 V72 H200 V48 H216 V216 Z')
gate_l = P('M108 216 V180 A20 20 0 0 1 148 180 V216')
cas_line = [P('M40 216 V48 H56 V72 H84 V48 H100 V112 H156 V48 H172 V72 H200 V48 H216 V216'),
            L(24, 216, 232, 216), gate_l]
slits = [L(70, 108, 70, 140), L(186, 108, 186, 140)]
icon('castle', MP, ['fort', 'fortress', 'castle', 'medieval', 'kingdom'],
     line=cas_line, detail=slits, area=[P(cas)], hole=[P('M116 216 V180 A12 12 0 0 1 140 180 V216 Z')])
icon('castle-slash', MP, ['castle', 'off', 'disabled', 'hidden'], line=cas_line + slits + [SLASH])

# church: steeple with a cross, lower wings, arched door, round window
ch = 'M40 216 V160 L92 132 V112 L128 80 L164 112 V132 L216 160 V216 Z'
icon('church', MP, ['chapel', 'worship', 'religion', 'church'],
     line=[P(ch), L(128, 80, 128, 32), L(108, 52, 148, 52), P('M108 216 V188 A20 20 0 0 1 148 188 V216')],
     detail=[C(128, 136, 12)], area=[P(ch)], hole=[P('M116 216 V188 A12 12 0 0 1 140 188 V216 Z')])

# circus tent: peaked roof with scalloped eave, flag, striped walls
eave = 'M32 128' + ''.join(f' A24 24 0 0 0 {x} 128' for x in (80, 128, 176, 224))
tent_roof = 'M128 64 Q104 112 32 128' + eave[7:] + ' Q152 112 128 64 Z'
icon('circus-tent', MP, ['circus', 'big top', 'carnival', 'tent'],
     line=[P(tent_roof), P('M56 150 V216 H200 V150'), PL([(104, 216), (128, 168), (152, 216)]), L(128, 64, 128, 32), PG([(128, 32), (160, 42), (128, 52)])],
     detail=[L(128, 92, 128, 120), L(112, 96, 92, 122), L(144, 96, 164, 122)],
     area=[P(tent_roof), R(56, 140, 144, 76)], hole=[PG([(108, 216), (128, 176), (148, 216)])])

# city: three towers of different heights
city = 'M32 216 V112 H88 V40 H152 V88 H224 V216 Z'
icon('city', MP, ['city', 'skyline', 'urban', 'buildings'],
     line=[P('M32 216 V112 H88 V40 H152 V88 H224 V216'), L(24, 216, 232, 216)],
     detail=[L(56, 152, 64, 152), L(112, 80, 128, 80), L(112, 120, 128, 120),
             L(112, 160, 128, 160), L(180, 128, 196, 128), L(180, 168, 196, 168)],
     area=[P(city)])

# city gate: crenellated wall with an arched passage, pavilion with a sweeping roof
cg_wall = 'M32 216 V136 H224 V216 H152 V192 A24 24 0 0 0 104 192 V216 Z'
cg_roof = 'M40 100 C60 100 72 92 80 68 H176 C184 92 196 100 216 100 Z'
icon('city-gate', MP, ['gate', 'landmark', 'fortress', 'entrance'],
     line=[P(cg_wall), P(cg_roof), L(80, 100, 80, 136), L(176, 100, 176, 136), L(128, 68, 128, 44)],
     area=[P(cg_wall), P(cg_roof), R(80, 100, 96, 36)])

# clock tower: pointed roof, square shaft, clock face
icon('clock-tower', MP, ['clock tower', 'big ben', 'landmark', 'time'],
     line=[PG([(60, 84), (128, 32), (196, 84)]), P('M72 84 V216 H184 V84'), L(48, 216, 208, 216)],
     detail=[C(128, 140, 32), PL([(128, 124), (128, 140), (140, 148)])],
     area=[PG([(60, 84), (128, 32), (196, 84)]), R(72, 84, 112, 132)])

# compass rose: four-pointed star
rose = []
for i in range(8):
    rose.append(polar((128, 128), 96 if i % 2 == 0 else 32, -90 + i * 45))
icon('compass-rose', MP, ['cardinal directions', 'compass', 'navigation'],
     line=[PG(rose)], area=[PG(rose)], dotcut=[C(128, 128, 16)])

# compass-slash (from compass.svg, no area so the slash reads in fill)
cmp = load('compass')
icon('compass-slash', MP, ['compass', 'disabled', 'off', 'maps'], line=cmp['line'] + cmp['detail'] + [SLASH])

# courthouse: pediment, four columns, base
ped = [(32, 96), (128, 40), (224, 96)]
icon('courthouse', MP, ['court', 'justice', 'law', 'government'],
     line=[PG(ped), L(64, 124, 64, 180), L(106, 124, 106, 180), L(150, 124, 150, 180), L(192, 124, 192, 180),
           L(40, 208, 216, 208)],
     area=[PG(ped)], dotcut=[C(128, 78, 14)])

# crosshair-slash (crosshair.svg is line-only)
icon('crosshair-slash', MP, ['location off', 'gps off', 'disabled', 'no location'],
     line=load('crosshair')['line'] + [SLASH])

# direction sign: rounded diamond with a turn arrow
dia = rpoly([(128, 26), (230, 128), (128, 230), (26, 128)], 22)
turn = [P('M108 168 V140 A12 12 0 0 1 120 128 H162'), PL([(140, 106), (162, 128), (140, 150)])]
icon('direction-sign', MP, ['sign', 'road sign', 'detour', 'directions', 'route'],
     line=[P(dia)], detail=turn, area=[P(dia)])
icon('direction-sign-slash', MP, ['direction sign', 'disabled', 'off', 'sign', 'road sign'],
     line=[P(dia)] + turn + [SLASH])

# dome: domed hall with a finial, door and windows
dome = 'M40 216 V136 H56 A72 72 0 0 1 200 136 H216 V216 Z'
icon('dome', MP, ['dome', 'observatory', 'capitol', 'building'],
     line=[P(dome), L(56, 136, 200, 136), L(128, 64, 128, 40), P('M108 216 V188 A20 20 0 0 1 148 188 V216')],
     detail=[L(72, 168, 72, 188), L(184, 168, 184, 188)],
     area=[P(dome)], hole=[P('M116 216 V188 A12 12 0 0 1 140 188 V216 Z')])

# eiffel tower: curved legs, platforms, base arch
legL = 'M128 40 Q120 152 48 216'
legR = 'M208 216 Q136 152 128 40'
eff = legL + ' H84 A44 40 0 0 1 172 216 H208 Q136 152 128 40 Z'


def leg_x(y):
    # x of the left leg at height y (quadratic from (128,40) via (120,152) to (48,216))
    lo, hi = 0.0, 1.0
    for _ in range(40):
        t = (lo + hi) / 2
        yy = (1 - t) ** 2 * 40 + 2 * (1 - t) * t * 152 + t * t * 216
        lo, hi = (t, hi) if yy < y else (lo, t)
    return (1 - t) ** 2 * 128 + 2 * (1 - t) * t * 120 + t * t * 48


xa, xb = leg_x(104), leg_x(160)
icon('eiffel-tower', MP, ['paris', 'eiffel', 'landmark', 'tower', 'france'],
     line=[P(legL), P(legR), L(128, 40, 128, 24 + 8), P('M84 216 A44 40 0 0 1 172 216'),
           L(xa - 12, 104, 256 - xa + 12, 104), L(xb - 12, 160, 256 - xb + 12, 160)],
     area=[P(eff)])

# escalator: rising band, handrail
esc = rpoly([(32, 176), (80, 176), (160, 96), (224, 96), (224, 152), (184, 152), (120, 216), (32, 216)], 14)
rail = PL([(32, 128), (77, 128), (157, 48), (224, 48)])
icon('escalator', MP, ['escalator', 'moving stairs', 'mall', 'transit'], line=[P(esc), rail], area=[P(esc)])
icon('escalator-up', MP, ['escalator up', 'ascend', 'stairs', 'arrow'],
     line=[P(esc), rail, L(56, 96, 56, 32), PL([(32, 56), (56, 32), (80, 56)])], area=[P(esc)])
icon('escalator-down', MP, ['escalator down', 'descend', 'stairs', 'arrow'],
     line=[P(esc), rail, L(56, 32, 56, 96), PL([(32, 72), (56, 96), (80, 72)])], area=[P(esc)])

# ferris wheel: rim with cabins, spokes, A-frame
fw = (128, 104)
icon('ferris-wheel', MP, ['ferris wheel', 'amusement park', 'attractions', 'fair', 'amusement'],
     line=[C(*fw, 72), L(128, 104, 80, 216), L(128, 104, 176, 216), L(48, 216, 208, 216)]
     + [L(*fw, *polar(fw, 72, a)) for a in (0, 180, -60, -120)],
     dot=[C(*polar(fw, 72, a), 16) for a in range(-90, 270, 60)] + [C(*fw, 16)])

# fortress: star fort seen from above, with a keep
sf = []
for k in range(4):
    base = [(148, 76), (204, 52), (180, 108)]
    sf += rot(base, 90 * k)
icon('fortress', MP, ['fort', 'defense', 'walls'], line=[PG(sf)], detail=[R(108, 108, 40, 40, 8)], area=[PG(sf)])

# ======================================================================= globes
GC, GR = (128, 128), 96


def globe_cut(rc):
    p, q = circle_x(GC, GR, B, rc)
    arc = arc_to(GC, GR, p, q, lambda m: dist(m, B))
    line = f'M{pt(p)} ' + arc
    area = line + ' ' + arc_to(B, rc, q, p, lambda m: -dist(m, GC)) + ' Z'
    xe = B[0] - math.sqrt(rc * rc - (B[1] - 128) ** 2)
    # right half of the meridian ellipse, stopped where it meets the cut circle
    t1 = -90
    while True:
        e = (128 + 40 * math.cos(math.radians(t1 + 1)), 128 + 96 * math.sin(math.radians(t1 + 1)))
        if dist(e, B) < rc:
            break
        t1 += 1
    e1 = (128 + 40 * math.cos(math.radians(t1)), 128 + 96 * math.sin(math.radians(t1)))
    mer = f'M128 224 A40 96 0 0 1 128 32 A40 96 0 0 1 {pt(e1)}'
    return [P(line)], [P(mer), L(32, 128, xe, 128)], [P(area)]


def globe(name, tags, marks, rc=64, mark_area=(), mark_hole=()):
    ln, det, ar = globe_cut(rc)
    icon(name, MP, tags, line=ln + list(marks), detail=det, area=ar + list(mark_area), hole=list(mark_hole))


def arrow(a, b, size):
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    bx, by = -math.cos(ang), -math.sin(ang)
    nx, ny = -by, bx
    return [L(*a, *b), PL([(b[0] + (bx + nx) * size, b[1] + (by + ny) * size), b,
                           (b[0] + (bx - nx) * size, b[1] + (by - ny) * size)])]


globe('globe-arrow-down', ['globe', 'download', 'down', 'decrease'], arrow((184, 152), (184, 216), 28))
globe('globe-arrow-up', ['globe', 'upload', 'up', 'increase'], arrow((184, 216), (184, 152), 28))
globe('globe-check', ['globe check', 'done', 'approved', 'globe', 'world'], [PL([(156, 186), (176, 206), (212, 166)])])
globe('globe-code', ['globe', 'code', 'developer', 'embed'], [PL([(170, 164), (150, 184), (170, 204)]),
                                                             PL([(198, 164), (218, 184), (198, 204)])])
globe('globe-currency-dollar', ['globe', 'dollar', 'price', 'money'],
      [P('M200 160 H180 A12 12 0 0 0 180 184 H188 A12 12 0 0 1 188 208 H168'), L(184, 146, 184, 160), L(184, 208, 184, 222)])
gp = []
for i in range(6):
    t0 = i * 60
    gp += [polar(B, 22, t0 - 20), polar(B, 32, t0 - 11), polar(B, 32, t0 + 11), polar(B, 22, t0 + 20)]
gdd = 'M' + pt(gp[0])
for i in range(6):
    a_, b_, c_, d_ = gp[i * 4:i * 4 + 4]
    if i:
        gdd += f' A22 22 0 0 1 {pt(a_)}'
    gdd += f' L{pt(b_)} L{pt(c_)} L{pt(d_)}'
gdd += f' A22 22 0 0 1 {pt(gp[0])} Z'
globe('globe-gear', ['globe', 'settings', 'configure'], [P(gdd)], mark_area=[P(gdd)], mark_hole=[C(184, 184, 8)])
hrt = ('M184 210.48 C184 210.48 151.36 192.8 151.36 171.72 A17 17 0 0 1 184 164.92 A17 17 0 0 1 216.64 171.72 '
       'C216.64 192.8 184 210.48 184 210.48 Z')
globe('globe-heart', ['globe', 'favorite', 'like', 'love'], [P(hrt)], mark_area=[P(hrt)])
bolt = 'M190 150 L162 190 L184 190 L178 218 L206 178 L184 178 Z'
globe('globe-lightning', ['globe', 'fast', 'power', 'instant'], [P(bolt)], mark_area=[P(bolt)])
globe('globe-magnifying-glass', ['globe', 'search', 'find'], [C(178, 178, 18), L(192, 192, 210, 210)],
      mark_area=[C(178, 178, 18)])
globe('globe-minus', ['globe minus', 'remove', 'subtract', 'globe', 'world'], [L(156, 184, 212, 184)])
globe('globe-pause', ['globe', 'paused', 'hold'], [L(168, 160, 168, 208), L(200, 160, 200, 208)])
globe('globe-plus', ['globe plus', 'add', 'new', 'globe', 'world'], [L(156, 184, 212, 184), L(184, 156, 184, 212)])
pin = ('M193.87 153.27 L210.5 167.23 L202.14 172.36 L192.18 184.24 L190.91 207.46 L157.65 179.55 L180.3 174.27 '
       'L190.27 162.39 Z')
globe('globe-push-pin', ['globe', 'pin', 'pinned'], [P(pin), L(174.28, 193.51, 156.34, 214.89)], mark_area=[P(pin)])

# hemispheres: simplified continents cut into the globe
west = [rpoly([(60, 104), (84, 76), (120, 62), (164, 70), (172, 88), (148, 100), (132, 118), (122, 138), (106, 126),
               (92, 110), (72, 116)], 8),
        rpoly([(126, 156), (156, 150), (174, 166), (150, 192), (132, 204)], 8)]
icon('globe-hemisphere-west', MP, ['americas', 'globe', 'world', 'earth'],
     line=[CIRC], detail=[P(d) for d in west], area=[CIRC])
east = [rpoly([(72, 96), (100, 70), (164, 62), (202, 98), (190, 122), (160, 110), (128, 100), (100, 106)], 8),
        rpoly([(78, 132), (120, 126), (144, 142), (136, 170), (118, 198), (102, 170), (90, 152)], 8)]
icon('globe-hemisphere-east', MP, ['europe', 'africa', 'asia', 'globe'],
     line=[CIRC], detail=[P(d) for d in east], area=[CIRC])
icon('globe-latitude', MP, ['latitude', 'parallels', 'globe', 'coordinates'],
     line=[CIRC], detail=[L(45, 80, 211, 80), L(32, 128, 224, 128), L(45, 176, 211, 176)], area=[CIRC])
icon('globe-longitude', MP, ['longitude', 'meridians', 'globe', 'coordinates'],
     line=[CIRC], detail=[E(128, 128, 48, 96), L(128, 32, 128, 224)], area=[CIRC])

print(save(overwrite=True))
