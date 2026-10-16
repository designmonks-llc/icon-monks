import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

DS = 'Design'
SLASH = L(48, 48, 208, 208)


# ---------------------------------------------------------------- helpers
def unit(a, b):
    d = dist(a, b)
    return ((b[0] - a[0]) / d, (b[1] - a[1]) / d)


def rpath(pts, r, closed=True):
    """Polygon with rounded corners; r is a number or a list (one per vertex, 0 = sharp)."""
    n = len(pts)
    rs = r if isinstance(r, (list, tuple)) else [r] * n
    cmds = []
    rng = range(n) if closed else range(1, n - 1)
    first = None
    for i in rng:
        v = pts[i]; a = pts[i - 1]; b = pts[(i + 1) % n]
        if rs[i] == 0:
            cmds.append(('L', v, None))
            continue
        u1 = unit(v, a); u2 = unit(v, b)
        th = math.acos(max(-1, min(1, u1[0] * u2[0] + u1[1] * u2[1])))
        t = rs[i] / math.tan(th / 2)
        s = (v[0] + u1[0] * t, v[1] + u1[1] * t); e = (v[0] + u2[0] * t, v[1] + u2[1] * t)
        cr = (v[0] - a[0]) * (b[1] - v[1]) - (v[1] - a[1]) * (b[0] - v[0])
        cmds.append(('A', s, f'A{f(rs[i])} {f(rs[i])} 0 0 {1 if cr > 0 else 0} {pt(e)}'))
    if closed:
        d = ''
        for k, (kind, p, arc) in enumerate(cmds):
            d += ('M' if k == 0 else ' L') + pt(p)
            if arc:
                d += ' ' + arc
        return d + ' Z'
    d = 'M' + pt(pts[0])
    for kind, p, arc in cmds:
        d += ' L' + pt(p) + ((' ' + arc) if arc else '')
    return d + ' L' + pt(pts[-1])


def bez(P, t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = P
    m = 1 - t
    return (m ** 3 * x0 + 3 * m * m * t * x1 + 3 * m * t * t * x2 + t ** 3 * x3,
            m ** 3 * y0 + 3 * m * m * t * y1 + 3 * m * t * t * y2 + t ** 3 * y3)


def split(P, t):
    lerp = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    p01, p12, p23 = lerp(P[0], P[1]), lerp(P[1], P[2]), lerp(P[2], P[3])
    a, b = lerp(p01, p12), lerp(p12, p23)
    m = lerp(a, b)
    return [P[0], p01, a, m], [m, b, p23, P[3]]


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def trim_bez(P, r0=0, r1=0, metric=dist):
    """Cut a cubic so it starts r0 away from P[0] and ends r1 away from P[3]."""
    def find(fn, r, rev):
        lo, hi = (0.0, 0.5)
        for _ in range(50):
            mid = (lo + hi) / 2
            t = 1 - mid if rev else mid
            if fn(t) < r:
                lo = mid
            else:
                hi = mid
        return 1 - hi if rev else hi
    t0 = find(lambda t: metric(bez(P, t), P[0]), r0, False) if r0 else 0
    t1 = find(lambda t: metric(bez(P, t), P[3]), r1, True) if r1 else 1
    Q = P
    if t1 < 1:
        Q = split(Q, t1)[0]
    if t0 > 0:
        Q = split(Q, t0 / t1)[1]
    return Q


def cd(Q, move=True):
    return (f'M{pt(Q[0])} ' if move else '') + f'C{pt(Q[1])} {pt(Q[2])} {pt(Q[3])}'


def head(tip, u, ln=36):
    bx, by = -u[0], -u[1]
    w = []
    for s in (45, -45):
        a = math.radians(s)
        w.append((tip[0] + ln * (bx * math.cos(a) - by * math.sin(a)), tip[1] + ln * (bx * math.sin(a) + by * math.cos(a))))
    return PL([w[0], tip, w[1]])


def seg_outside(a, b, poly):
    """Parts of segment ab outside convex polygon poly (Cyrus-Beck)."""
    t0, t1 = 0.0, 1.0
    n = len(poly)
    area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    sgn = 1 if area > 0 else -1
    d = (b[0] - a[0], b[1] - a[1])
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        nx, ny = -(q[1] - p[1]) * sgn, (q[0] - p[0]) * sgn  # inward normal
        num = nx * (a[0] - p[0]) + ny * (a[1] - p[1])
        den = nx * d[0] + ny * d[1]
        if abs(den) < 1e-9:
            if num < 0:
                return [(a, b)]
            continue
        t = -num / den
        if den > 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
    if t0 >= t1:
        return [(a, b)]
    at = lambda t: (a[0] + d[0] * t, a[1] + d[1] * t)
    out = []
    if t0 > 1e-6:
        out.append((a, at(t0)))
    if t1 < 1 - 1e-6:
        out.append((at(t1), b))
    return out


def line_circle(a, b, c, r):
    """First point along a->b at distance r from c."""
    d = (b[0] - a[0], b[1] - a[1]); f0 = (a[0] - c[0], a[1] - c[1])
    A = d[0] ** 2 + d[1] ** 2; B = 2 * (f0[0] * d[0] + f0[1] * d[1]); Cc = f0[0] ** 2 + f0[1] ** 2 - r * r
    t = (-B - math.sqrt(B * B - 4 * A * Cc)) / (2 * A)
    return (a[0] + d[0] * t, a[1] + d[1] * t)


def dashes_on(a, b, n, frac, inset=0):
    """n dashes along segment ab, each frac of its slot, skipping `inset` units at both ends."""
    u = unit(a, b); ln = dist(a, b) - 2 * inset
    s0 = (a[0] + u[0] * inset, a[1] + u[1] * inset)
    slot = ln / n; out = []
    for i in range(n):
        m = slot * (i + 0.5); h = slot * frac / 2
        out.append(L(s0[0] + u[0] * (m - h), s0[1] + u[1] * (m - h), s0[0] + u[0] * (m + h), s0[1] + u[1] * (m + h)))
    return out


# ---------------------------------------------------------------- spiral
def spiral_path():
    a, cy, d = 128, 137, 18
    b = a + d
    x = a + d  # start
    r = d
    s = f'M{f(x)} {cy}'
    upper = True
    while r <= 90:
        if upper:
            x = a - r
        else:
            x = b + r
        s += f' A{f(r)} {f(r)} 0 0 0 {f(x)} {cy}'
        upper = not upper
        r += d
    return s


SPI = P(spiral_path())
icon('spiral', DS, ['spiral', 'swirl', 'hypnotic', 'coil'], line=[SPI])
icon('spiral-slash', DS, ['spiral', 'off', 'disabled', 'hidden'], line=[SPI, SLASH])

# ---------------------------------------------------------------- spline
SP_A = [(56, 192), (128, 128), (200, 64)]
SP_1 = [(56, 192), (56, 112), (96, 96), (128, 128)]
SP_2 = [(128, 128), (160, 160), (200, 144), (200, 64)]
AH = 16
anchors = [R(x - AH, y - AH, 2 * AH, 2 * AH, 6) for x, y in SP_A]
icon('spline', DS, ['spline', 'curve', 'path', 'smooth'],
     line=anchors + [P(cd(trim_bez(SP_1, AH, AH, cheb))), P(cd(trim_bez(SP_2, AH, AH, cheb)))], area=anchors)

# ---------------------------------------------------------------- squares
SQ = R(32, 32, 192, 192, 16)
icon('square-half', DS, ['half', 'contrast', 'square', 'split'],
     line=[SQ, L(128, 32, 128, 224)], area=[P('M128 32 H48 A16 16 0 0 0 32 48 V208 A16 16 0 0 0 48 224 H128 Z')])
icon('square-half-bottom', DS, ['half square', 'fill', 'contrast'],
     line=[SQ, L(32, 128, 224, 128)], area=[P('M32 128 V208 A16 16 0 0 0 48 224 H208 A16 16 0 0 0 224 208 V128 Z')])

# ---------------------------------------------------------------- stack
st = load('stack')
DIAM = st['line'][0]
STACK_TRIM = [DIAM, PL([(32, 132), (128, 184)]), PL([(32, 172), (128, 224)])]
icon('stack-minus', DS, ['remove layer', 'stack', 'minus', 'layers'],
     line=STACK_TRIM + [L(164, 188, 212, 188)], area=st['area'])
icon('stack-plus', DS, ['add layer', 'stack', 'plus', 'layers'],
     line=STACK_TRIM + [L(164, 188, 212, 188), L(188, 164, 188, 212)], area=st['area'])
icon('stack-slash', DS, ['layers off', 'hide layers', 'stack', 'slash', 'clear layers'], line=st['line'] + [SLASH])

# ---------------------------------------------------------------- strokes
icon('stroke-straight', DS, ['straight stroke', 'line', 'path', 'brush'], line=[L(48, 208, 208, 48)])
SC = [(44, 208), (44, 100), (212, 156), (212, 48)]
icon('stroke-curved', DS, ['curved stroke', 'line', 'path', 'brush'], line=[P(cd(SC))])


def tapered(Pc, w, n=40):
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        p = bez(Pc, t)
        q = bez(Pc, min(t + 1e-3, 1)); o = bez(Pc, max(t - 1e-3, 0))
        u = unit(o, q); nn = (-u[1], u[0])
        hw = w * math.sin(math.pi * t) ** 0.8
        left.append((p[0] + nn[0] * hw, p[1] + nn[1] * hw))
        right.append((p[0] - nn[0] * hw, p[1] - nn[1] * hw))
    pts = left + right[::-1][1:-1]
    return PG(pts)


TAP = tapered([(52, 204), (52, 104), (204, 152), (204, 52)], 24)
icon('stroke-dynamic', DS, ['variable stroke', 'pressure', 'brush', 'line'], line=[TAP], area=[TAP])

# ---------------------------------------------------------------- boolean
bc1, br1, bc2, br2 = (104, 152), 72, (160, 96), 64
up_, dn_ = circle_x(bc1, br1, bc2, br2)
# upper point is the one nearer the top-left? sort by x for this diagonal pair
pA, pB = sorted([up_, dn_], key=lambda p: p[0])
CRES = (f'M{pt(pA)} ' + arc_to(bc1, br1, pA, pB, lambda m: dist(m, bc2)) + ' ' +
        arc_to(bc2, br2, pB, pA, lambda m: -dist(m, bc1)) + ' Z')
FRONT_OUT = f'M{pt(pA)} ' + arc_to(bc2, br2, pA, pB, lambda m: dist(m, bc1))
icon('subtract', DS, ['subtract', 'boolean', 'minus front', 'shapes'], line=[P(CRES), P(FRONT_OUT)], area=[P(CRES)])
UNI = (f'M{pt(pA)} ' + arc_to(bc1, br1, pA, pB, lambda m: dist(m, bc2)) + ' ' +
       arc_to(bc2, br2, pB, pA, lambda m: dist(m, bc1)) + ' Z')
icon('unite', DS, ['union', 'boolean', 'combine', 'merge shapes'], line=[P(UNI)], area=[P(UNI)])

LSH = P(rpath([(32, 96), (96, 96), (96, 160), (160, 160), (160, 224), (32, 224)], [14, 0, 0, 0, 14, 14]))
FRONT_SQ = R(96, 32, 128, 128, 14)
icon('subtract-square', DS, ['subtract', 'boolean', 'minus front', 'shapes', 'pathfinder'],
     line=[LSH, FRONT_SQ], area=[LSH])
USQ = P(rpath([(32, 96), (96, 96), (96, 32), (224, 32), (224, 160), (160, 160), (160, 224), (32, 224)],
              [14, 8, 14, 14, 14, 8, 14, 14]))
icon('unite-square', DS, ['union', 'boolean', 'combine', 'shapes', 'merge'], line=[USQ], area=[USQ])

# ---------------------------------------------------------------- swatches
CA = R(32, 32, 80, 192, 16)
piv = (72, 184)
cardB = rot([(32, 32), (112, 32), (112, 224), (32, 224)], 45, piv)
# visible edge of B: left edge from x=112 up to TL, across to TR, down to y=144
tlB, trB = cardB[0], cardB[1]
blB = cardB[3]; brB = cardB[2]


def at_x(a, b, x):
    t = (x - a[0]) / (b[0] - a[0]); return (x, a[1] + (b[1] - a[1]) * t)


def at_y(a, b, y):
    t = (y - a[1]) / (b[1] - a[1]); return (a[0] + (b[0] - a[0]) * t, y)


b_start = at_x(blB, tlB, 112)
b_end = at_y(brB, trB, 144)
B_VIS = rpath([b_start, tlB, trB, b_end], 14, closed=False)
C_VIS = 'M112 144 H208 A16 16 0 0 1 224 160 V208 A16 16 0 0 1 208 224 H112'
SW_LINE = [CA, P(B_VIS), P(C_VIS)]
icon('swatches', DS, ['swatches', 'color samples', 'palette', 'swatchbook', 'color swatches'],
     line=SW_LINE,
     detail=[L(112, b_start[1] + 8, 112, 216), L(112, 144, b_end[0] - 4, 144)],
     area=[CA, PG([b_start, tlB, trB, b_end, (112, 144)]), P(C_VIS + ' Z')],
     dotcut=[C(72, 184, 16)])
icon('swatches-slash', DS, ['color swatch', 'disabled', 'off', 'design'], line=SW_LINE + [SLASH])

# ---------------------------------------------------------------- symmetry
AXH = [L(x - 6, 128, x + 6, 128) for x in (44, 100, 156, 212)]
T_UP = [(128, 32), (200, 96), (56, 96)]
T_DN = [(128, 224), (200, 160), (56, 160)]
icon('symmetry-horizontal', DS, ['symmetry', 'mirror', 'horizontal', 'reflect'],
     line=[PG(T_UP), PG(T_DN)] + AXH, area=[PG(T_UP)])
swap = lambda pts: [(y, x) for x, y in pts]
icon('symmetry-vertical', DS, ['symmetry', 'mirror', 'vertical', 'reflect'],
     line=[PG(swap(T_UP)), PG(swap(T_DN))] + [L(128, x - 6, 128, x + 6) for x in (44, 100, 156, 212)],
     area=[PG(swap(T_UP))])

# ---------------------------------------------------------------- texture
tc = (128, 128); tr_ = 96
tex = []
for k in (-56, 0, 56):  # perpendicular offset from the centre along (1,1)/sqrt2
    half = math.sqrt((tr_ - 30) ** 2 - k * k)
    cx, cy = tc[0] + k / math.sqrt(2), tc[1] + k / math.sqrt(2)
    ux, uy = 1 / math.sqrt(2), -1 / math.sqrt(2)
    tex.append(L(cx - ux * half, cy - uy * half, cx + ux * half, cy + uy * half))
icon('texture', DS, ['texture', 'pattern', 'diagonal lines', 'material'],
     line=[C(128, 128, 96)], detail=tex, area=[C(128, 128, 96)])

# ---------------------------------------------------------------- transform
HS = 16
FR = [(56, 56), (200, 56), (200, 200), (56, 200)]
handles = [R(x - HS, y - HS, 2 * HS, 2 * HS, 6) for x, y in FR]
frame = [L(56 + HS, 56, 200 - HS, 56), L(200, 56 + HS, 200, 200 - HS),
         L(200 - HS, 200, 56 + HS, 200), L(56, 200 - HS, 56, 56 + HS)]
icon('transform', DS, ['transform', 'scale', 'resize', 'handles'],
     line=handles + frame, detail=[L(96, 160, 160, 96), PL([(120, 96), (160, 96), (160, 136)])],
     area=[R(56, 56, 144, 144)] + handles)
icon('transform-point', DS, ['anchor point', 'transform', 'origin', 'pivot'],
     line=handles + frame, detail=[C(128, 128, 24)], area=[R(56, 56, 144, 144)] + handles)

# ---------------------------------------------------------------- transitions
TB = 'M92 152 H56 A16 16 0 0 1 40 136 V48 A16 16 0 0 1 56 32 H200 A16 16 0 0 1 216 48 V136 A16 16 0 0 1 200 152 H164'
icon('transition-bottom', DS, ['transition', 'slide', 'animation', 'bottom'],
     line=[P(TB), L(128, 152, 128, 216), PL([(92, 180), (128, 216), (164, 180)])],
     detail=[L(128, 72, 128, 152)], area=[R(40, 32, 176, 120, 16)])
TT = 'M92 104 H56 A16 16 0 0 0 40 120 V208 A16 16 0 0 0 56 224 H200 A16 16 0 0 0 216 208 V120 A16 16 0 0 0 200 104 H164'
icon('transition-top', DS, ['transition', 'slide', 'animation', 'top'],
     line=[P(TT), L(128, 104, 128, 40), PL([(92, 76), (128, 40), (164, 76)])],
     detail=[L(128, 184, 128, 104)], area=[R(40, 104, 176, 120, 16)])

# ---------------------------------------------------------------- triangles
TRAP = PG([(80, 64), (176, 64), (224, 192), (32, 192)])
icon('trapezoid', DS, ['trapezoid', 'shape', 'geometry', 'quadrilateral'], line=[TRAP], area=[TRAP])

itri = regular_polygon((128, 128), 66, 3)
icon('triangle-circle', DS, ['triangle', 'shape', 'circle'],
     line=[C(128, 128, 96)], detail=[PG(itri)], area=[C(128, 128, 96)])

TRI = [(128, 40), (224, 208), (32, 208)]
tdash = []
for i in range(3):
    a, b = TRI[i], TRI[(i + 1) % 3]
    u = unit(a, b); ln = dist(a, b)
    tdash.append(L(a[0] + u[0] * (ln / 2 - 22), a[1] + u[1] * (ln / 2 - 22),
                   a[0] + u[0] * (ln / 2 + 22), a[1] + u[1] * (ln / 2 + 22)))
for i in range(3):
    v, a, b = TRI[i], TRI[i - 1], TRI[(i + 1) % 3]
    ua, ub = unit(v, a), unit(v, b)
    tdash.append(PL([(v[0] + ua[0] * 30, v[1] + ua[1] * 30), v, (v[0] + ub[0] * 30, v[1] + ub[1] * 30)]))
icon('triangle-dashed', DS, ['dashed triangle', 'shape', 'outline', 'draft'], line=tdash)

TINV = PG([(32, 48), (224, 48), (128, 216)])
icon('triangle-inverted', DS, ['inverted triangle', 'down', 'shape', 'triangle'], line=[TINV], area=[TINV])

BADGE = (188, 188); BR = 58
edge_pt = line_circle((128, 40), (224, 208), BADGE, BR)
base_pt = (BADGE[0] - math.sqrt(BR ** 2 - (208 - BADGE[1]) ** 2), 208)
TRI_OPEN = f'M{pt(edge_pt)} L128 40 L32 208 L{pt(base_pt)}'
TRI_AREA = TRI_OPEN + ' ' + arc_to(BADGE, BR, base_pt, edge_pt, lambda m: -dist(m, (128, 128))) + ' Z'
icon('triangle-minus', DS, ['triangle', 'remove', 'subtract'],
     line=[P(TRI_OPEN), L(164, 188, 212, 188)], area=[P(TRI_AREA)])
icon('triangle-plus', DS, ['triangle', 'add', 'new', 'create'],
     line=[P(TRI_OPEN), L(164, 188, 212, 188), L(188, 164, 188, 212)], area=[P(TRI_AREA)])
icon('triangle-slash', DS, ['triangle', 'off', 'disabled', 'hidden'], line=[PG(TRI), SLASH])

T_BACK = [(104, 40), (176, 168), (32, 168)]
T_FRONT = [(152, 88), (224, 216), (80, 216)]
back_vis = []
for i in range(3):
    for a, b in seg_outside(T_BACK[i], T_BACK[(i + 1) % 3], T_FRONT):
        back_vis.append((a, b))
# join pieces that share the apex into one polyline
tb_lines = [PL([back_vis[0][0], back_vis[0][1]])] if False else []
icon('triangles', DS, ['triangles', 'pattern', 'shapes', 'geometry'],
     line=[PG(T_FRONT)] + [PL([a, b]) for a, b in back_vis], area=[PG(T_FRONT)])

# ---------------------------------------------------------------- typeface
TYPE = [PL([(48, 208), (104, 48), (160, 208)]), L(65, 160, 143, 160), L(32, 208, 68, 208), L(140, 208, 176, 208),
        L(172, 48, 224, 48), L(198, 48, 198, 120), L(184, 120, 212, 120)]
icon('typeface', DS, ['typeface', 'font', 'typography', 'letters'], line=TYPE)
icon('typeface-slash', DS, ['typeface', 'off', 'disabled', 'hidden'], line=TYPE + [SLASH])

# ---------------------------------------------------------------- vector
VH = 18
VP = [(60, 60), (196, 60), (196, 196), (60, 196)]
v_anchor = [R(x - VH, y - VH, 2 * VH, 2 * VH, 6) for x, y in VP]
v_edges = [L(60 + VH, 60, 196 - VH, 60), L(196, 60 + VH, 196, 196 - VH),
           L(196 - VH, 196, 60 + VH, 196), L(60, 196 - VH, 60, 60 + VH)]
icon('vector', DS, ['vector', 'bezier', 'anchor points', 'path'], line=v_anchor + v_edges, area=v_anchor)
icon('vector-slash', DS, ['vector', 'off', 'disabled', 'hidden'], line=v_anchor + v_edges + [L(88, 88, 168, 168)])

O2 = (64, 192)
icon('vector-two', 'Science', ['2d vectors', 'axes', 'coordinates'],
     line=[L(*O2, 64, 40), L(*O2, 216, 192), head((64, 40), (0, -1)), head((216, 192), (1, 0))])
O3 = (128, 152); LN3 = 104
v3 = []
for ang in (-90, 30, 150):
    tip = polar(O3, LN3, ang); u = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
    v3 += [L(*O3, *tip), head(tip, u, 32)]
icon('vector-three', 'Science', ['3d vectors', 'axes', 'coordinates'], line=v3)

VT = [(128, 52), (200, 192), (56, 192)]
vt_anchor = [R(x - VH, y - VH, 2 * VH, 2 * VH, 6) for x, y in VT]
vt_edges = []
for i in range(3):
    a, b = VT[i], VT[(i + 1) % 3]
    u = unit(a, b); k = VH / max(abs(u[0]), abs(u[1]))
    vt_edges.append(L(a[0] + u[0] * k, a[1] + u[1] * k, b[0] - u[0] * k, b[1] - u[1] * k))
icon('vector-triangle', DS, ['vector triangle', 'anchor points', 'polygon', 'path'],
     line=vt_anchor + vt_edges, area=vt_anchor)
icon('vector-triangle-slash', DS, ['vector triangle', 'off', 'disabled', 'hidden', 'vector'],
     line=vt_anchor + vt_edges + [L(48, 48, 168, 168)])

# ---------------------------------------------------------------- views
CUBE_O = [(40, 92), (92, 40), (216, 40), (216, 164), (164, 216), (40, 216)]
CUBE_IN = [PL([(40, 92), (164, 92), (164, 216)]), L(164, 92, 216, 40)]
icon('view-orthogonal', DS, ['orthographic', '3d view', 'front view'],
     line=[PG(CUBE_O)], detail=CUBE_IN, area=[PG(CUBE_O)])

VPt = (236, -4); kk = 0.5
FF = [(32, 88), (164, 88), (164, 220), (32, 220)]
BK = [(VPt[0] + (x - VPt[0]) * kk, VPt[1] + (y - VPt[1]) * kk) for x, y in FF]
pers_o = [FF[0], BK[0], BK[1], BK[2], FF[2], FF[3]]
# centre it
xs = [p[0] for p in pers_o]; ys = [p[1] for p in pers_o]
dx = 128 - (min(xs) + max(xs)) / 2; dy = 128 - (min(ys) + max(ys)) / 2
sh = lambda p: (p[0] + dx, p[1] + dy)
pers_o = [sh(p) for p in pers_o]
icon('view-perspective', DS, ['perspective', '3d view', 'vanishing point'],
     line=[PG(pers_o)], detail=[PL([sh(FF[0]), sh(FF[1]), sh(FF[2])]), L(*sh(FF[1]), *sh(BK[1]))],
     area=[PG(pers_o)])

HID = (92, 164)
xr = [L(92, 116, 92, 136), L(120, 164, 140, 164), L(*polar(HID, 30, 135), *polar(HID, 50, 135))]
icon('view-xray', DS, ['x-ray view', 'wireframe', 'see-through'], line=[PG(CUBE_O)] + CUBE_IN + xr, dot=[C(92, 164, 12)])

# ---------------------------------------------------------------- wallpaper
mon = load('monitor')
WP_DET = [P('M44 160 C76 116 104 112 132 136 C156 156 180 136 212 120'), C(164, 96, 16)]
icon('wallpaper', DS, ['wallpaper', 'background', 'image', 'desktop'],
     line=mon['line'], detail=WP_DET, area=mon['area'])
icon('wallpaper-slash', DS, ['wallpaper', 'off', 'disabled', 'hidden'], line=mon['line'] + WP_DET + [SLASH])

# ---------------------------------------------------------------- warp
WH = 76; WA = 0.42; WR = WH * math.sqrt(2)


def wmap(p):
    d = (p[0] - 128, p[1] - 128); r = math.hypot(*d)
    s = 1 + WA * (1 - (r / WR) ** 2)
    return (128 + d[0] * s, 128 + d[1] * s)


def wline(a, b, n=24):
    return [wmap((a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)) for i in range(n + 1)]


lo, hi = 128 - WH, 128 + WH
w_out = wline((lo, lo), (hi, lo))[:-1] + wline((hi, lo), (hi, hi))[:-1] + wline((hi, hi), (lo, hi))[:-1] + wline((lo, hi), (lo, lo))[:-1]
grid = []
for g in (128 - WH / 3, 128 + WH / 3):
    grid.append(PL(wline((g, lo), (g, hi))))
    grid.append(PL(wline((lo, g), (hi, g))))
icon('warp', DS, ['distort', 'warp', 'mesh', 'transform'], line=[PG(w_out)], detail=grid, area=[PG(w_out)])

# ---------------------------------------------------------------- zigzag
icon('zigzag', DS, ['zigzag', 'wave', 'line', 'pattern'],
     line=[PL([(32, 176), (80, 80), (128, 176), (176, 80), (224, 176)])])

print(save(overwrite=True))
