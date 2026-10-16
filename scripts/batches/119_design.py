import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

DS = 'Design'
SLASH = L(48, 48, 208, 208)


# ---------------------------------------------------------------- helpers
def rounded_poly(points, rc, close=True):
    """Polygon (or open polyline) path with circular corners of radius rc at interior vertices."""
    n = len(points)
    idx = range(n) if close else range(1, n - 1)
    corners = {}
    for i in idx:
        p0, p, p1 = points[i - 1], points[i], points[(i + 1) % n]
        a = (p0[0] - p[0], p0[1] - p[1]); b = (p1[0] - p[0], p1[1] - p[1])
        la, lb = math.hypot(*a), math.hypot(*b)
        a = (a[0] / la, a[1] / la); b = (b[0] / lb, b[1] / lb)
        ang = math.acos(max(-1, min(1, a[0] * b[0] + a[1] * b[1])))
        t = rc / math.tan(ang / 2)
        s = (p[0] + a[0] * t, p[1] + a[1] * t); e = (p[0] + b[0] * t, p[1] + b[1] * t)
        cross = a[0] * b[1] - a[1] * b[0]
        sweep = 1 if cross < 0 else 0
        corners[i] = (s, e, sweep)
    d = ''
    if close:
        s, e, sw = corners[0]
        d = f'M{pt(e)}'
        for i in list(range(1, n)) + [0]:
            s, e, sw = corners[i]
            d += f' L{pt(s)} A{f(rc)} {f(rc)} 0 0 {sw} {pt(e)}'
        return d + ' Z'
    d = f'M{pt(points[0])}'
    for i in range(1, n - 1):
        s, e, sw = corners[i]
        d += f' L{pt(s)} A{f(rc)} {f(rc)} 0 0 {sw} {pt(e)}'
    return d + f' L{pt(points[-1])}'


def plen(pts):
    return sum(dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def sub_poly(pts, s0, s1):
    """Part of polyline pts between arc lengths s0 and s1."""
    out = []
    acc = 0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        l = dist(a, b)
        if l == 0:
            continue
        lo, hi = acc, acc + l
        if hi >= s0 and lo <= s1:
            t0 = max(0, (s0 - lo) / l); t1 = min(1, (s1 - lo) / l)
            p0 = (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0)
            p1 = (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)
            if not out:
                out.append(p0)
            out.append(p1)
        acc = hi
    return out


def dashes(pts, n, dash):
    """n dashes evenly spread over an open polyline, first and last dash flush with the ends."""
    total = plen(pts)
    gap = (total - n * dash) / (n - 1)
    res = []
    for i in range(n):
        s0 = i * (dash + gap)
        res.append(PL(sub_poly(pts, s0, s0 + dash)))
    return res


def ellipse_pts(c, rx, ry, a0, a1, step=3):
    k = max(2, int(abs(a1 - a0) / step))
    return [(c[0] + rx * math.cos(math.radians(a0 + (a1 - a0) * i / k)),
             c[1] + ry * math.sin(math.radians(a0 + (a1 - a0) * i / k))) for i in range(k + 1)]


def dashed_box(x0, y0, x1, y1, arm=24, mid=True):
    out = [PL([(x0, y0 + arm), (x0, y0), (x0 + arm, y0)]), PL([(x1 - arm, y0), (x1, y0), (x1, y0 + arm)]),
           PL([(x1, y1 - arm), (x1, y1), (x1 - arm, y1)]), PL([(x0 + arm, y1), (x0, y1), (x0, y1 - arm)])]
    if mid:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        out += [L(cx - 24, y0, cx + 24, y0), L(cx - 24, y1, cx + 24, y1), L(x0, cy - 24, x0, cy + 24),
                L(x1, cy - 24, x1, cy + 24)]
    return out


def seg(a, b, ra, rb):
    d = dist(a, b); ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
    return L(a[0] + ux * ra, a[1] + uy * ra, b[0] - ux * rb, b[1] - uy * rb)


def diamond(c, r):
    return [(c[0], c[1] - r), (c[0] + r, c[1]), (c[0], c[1] + r), (c[0] - r, c[1])]


# ---------------------------------------------------------------- keyframes
KF = P(rounded_poly(diamond((128, 128), 92), 14))
icon('keyframe', DS, ['animation', 'keyframe', 'timeline', 'diamond'], line=[KF], area=[KF])

KA = P(rounded_poly(diamond((128, 128), 76), 10))
V_OUT = [L(128, 32, 128, 52), L(128, 204, 128, 224)]
H_OUT = [L(32, 128, 52, 128), L(204, 128, 224, 128)]
V_IN, H_IN = L(128, 84, 128, 172), L(84, 128, 172, 128)
icon('keyframe-align-vertical', DS, ['keyframe align', 'vertical', 'animation', 'diamond'],
     line=[KA] + V_OUT, detail=[V_IN], area=[KA])
icon('keyframe-align-horizontal', DS, ['keyframe align', 'horizontal', 'animation', 'diamond'],
     line=[KA] + H_OUT, detail=[H_IN], area=[KA])
icon('keyframe-align-center', DS, ['keyframe align', 'center', 'animation', 'diamond'],
     line=[KA] + V_OUT + H_OUT, detail=[V_IN, H_IN], area=[KA])

KF_FRONT = P(rounded_poly(diamond((104, 128), 72), 12))
icon('keyframes', DS, ['animation', 'timeline', 'keyframes', 'diamonds'],
     line=[KF_FRONT, P(rounded_poly([(152, 56), (224, 128), (152, 200)], 12, close=False))], area=[KF_FRONT])

# ---------------------------------------------------------------- lasso
LC, LRX, LRY = (138, 98), 86, 60
KNOT_A = 128
KNOT = (LC[0] + LRX * math.cos(math.radians(KNOT_A)), LC[1] + LRY * math.sin(math.radians(KNOT_A)))
LOOP = ellipse_pts(LC, LRX, LRY, KNOT_A + 22, KNOT_A + 360 - 22)
TAIL = P(f'M{pt(KNOT)} C{f(KNOT[0] - 4)} {f(KNOT[1] + 36)} 48 180 56 216')
lasso_dash = dashes(LOOP, 8, 22)
icon('lasso', DS, ['lasso select', 'selection', 'freeform', 'select', 'lasso'],
     line=lasso_dash + [TAIL], dot=[C(*KNOT, 18)])


def far_from_slash(el_pts, clear=26):
    return all(abs(p[1] - p[0]) / math.sqrt(2) > clear for p in el_pts)


lasso_slash = []
total = plen(LOOP); gap = (total - 8 * 22) / 7
for i in range(8):
    seg_pts = sub_poly(LOOP, i * (22 + gap), i * (22 + gap) + 22)
    if far_from_slash(seg_pts):
        lasso_slash.append(PL(seg_pts))
icon('lasso-slash', DS, ['lasso', 'off', 'disabled', 'hidden'],
     line=lasso_slash + [TAIL, SLASH], dot=[C(*KNOT, 18)])

PKNOT = (76, 150)
POLY = [PKNOT, (40, 88), (100, 40), (200, 48), (224, 116), (150, 156), PKNOT]
# open the loop around the knot
pl_total = plen(POLY)
POLY_OPEN = sub_poly(POLY, 22, pl_total - 22)
PTAIL = P(f'M{pt(PKNOT)} C{f(PKNOT[0] - 4)} {f(PKNOT[1] + 32)} 48 182 56 216')
icon('lasso-polygon', DS, ['polygon lasso', 'select', 'freeform', 'tool'],
     line=dashes(POLY_OPEN, 9, 22) + [PTAIL], dot=[C(*PKNOT, 18)])

# ---------------------------------------------------------------- layers
SQ_A = [(160, 140), (160, 48, ), ]
A_PATH = 'M160 120 V48 A16 16 0 0 0 144 32 H48 A16 16 0 0 0 32 48 V144 A16 16 0 0 0 48 160 H76'
icon('layers-linked', DS, ['linked layers', 'shapes', 'connected', 'boolean'],
     line=[P('M160 72 V48 A16 16 0 0 0 144 32 H48 A16 16 0 0 0 32 48 V144 A16 16 0 0 0 48 160 H144 A16 16 0 0 0 160 144 V120'),
           P('M96 136 V112 A16 16 0 0 1 112 96 H208 A16 16 0 0 1 224 112 V208 A16 16 0 0 1 208 224 H112 A16 16 0 0 1 96 208 V184')])

LS_TOP = [(128, 40), (224, 104), (128, 168), (32, 104)]
icon('layers-selected', DS, ['selected layer', 'stack', 'layers', 'active'],
     line=[PG(LS_TOP), PL([(32, 148), (128, 212), (224, 148)])],
     detail=[PL([(100, 106), (120, 126), (156, 90)])], area=[PG(LS_TOP)])

lay = load('layout')
icon('layout-slash', DS, ['layout', 'off', 'disabled', 'hidden'], line=lay['line'] + [SLASH])

# ---------------------------------------------------------------- line caps
CAP_ROUND = 'M32 72 H152 A56 56 0 0 1 152 184 H32'
icon('line-cap', DS, ['stroke cap', 'line end', 'vector', 'path'],
     line=[P(CAP_ROUND)], detail=[L(32, 128, 152, 128)], area=[P(CAP_ROUND + ' Z')], dotcut=[C(152, 128, 16)])
CAP_BUTT = 'M32 72 H200 V184 H32'
icon('line-cap-straight', DS, ['line cap', 'stroke', 'butt cap'],
     line=[P(CAP_BUTT), L(168, 128, 200, 128)], detail=[L(32, 128, 168, 128)], area=[P(CAP_BUTT + ' Z')],
     dot=[C(200, 128, 20)])
CAP_SQ = 'M32 72 H208 V184 H32'
icon('line-cap-projecting', DS, ['line cap', 'stroke', 'square cap'],
     line=[P(CAP_SQ)], detail=[L(32, 128, 152, 128)], area=[P(CAP_SQ + ' Z')], dotcut=[C(152, 128, 16)])

# ---------------------------------------------------------------- line styles
DIAG = [(44, 212), (212, 44)]
icon('line-dashed', DS, ['dashed line', 'stroke', 'dashes', 'style'], line=dashes(DIAG, 3, 52))
icon('line-dotted', DS, ['dotted line', 'stroke', 'dots', 'style'],
     dot=[C(50 + i * 52, 206 - i * 52, 20) for i in range(4)])

icon('line-end-arrow', DS, ['arrowhead', 'line end', 'connector', 'stroke cap'],
     line=[L(32, 128, 152, 128), PG([(152, 80), (224, 128), (152, 176)])], area=[PG([(152, 80), (224, 128), (152, 176)])])
icon('line-end-bar', DS, ['line end', 'bar cap', 'connector', 'stroke cap'],
     line=[L(32, 128, 216, 128), L(216, 64, 216, 192)])
icon('line-end-circle', DS, ['line end', 'dot cap', 'connector', 'stroke cap'],
     line=[L(32, 128, 136, 128), C(180, 128, 44)], area=[C(180, 128, 44)])
LED = diamond((172, 128), 52)
icon('line-end-diamond', DS, ['line end', 'diamond cap', 'connector', 'stroke cap'],
     line=[L(32, 128, 120, 128), PG(LED)], area=[PG(LED)])
icon('line-end-square', DS, ['line end', 'square cap', 'connector', 'stroke cap'],
     line=[L(32, 128, 136, 128), R(136, 84, 88, 88, 12)], area=[R(136, 84, 88, 88, 12)])

# joins: centreline (216,88)->(88,88)->(88,216), half width 48
JOIN_INNER = 'H136 V136 H216'
JOINS = {
    'miter': 'M216 40 H40 V216',
    'bevel': 'M216 40 H88 L40 88 V216',
    'round': 'M216 40 H88 A48 48 0 0 0 40 88 V216',
}
JOIN_TAGS = {
    'bevel': ['bevel join', 'stroke join', 'corner', 'line'],
    'miter': ['miter join', 'stroke join', 'corner', 'line'],
    'round': ['round join', 'stroke join', 'corner', 'line'],
}
for nm in ('bevel', 'miter', 'round'):
    outer = JOINS[nm]
    icon(f'line-join-{nm}', DS, JOIN_TAGS[nm],
         line=[P(outer + ' ' + JOIN_INNER + ' Z')],
         detail=[PL([(188, 88), (88, 88), (88, 188)])],
         area=[P(outer + ' ' + JOIN_INNER + ' Z')])

SEG_A, SEG_B = (64, 192), (192, 64)
icon('line-segment', DS, ['line', 'segment', 'vector', 'diagonal', 'stroke'],
     line=[C(*SEG_A, 24), C(*SEG_B, 24), seg(SEG_A, SEG_B, 24, 24)], area=[C(*SEG_A, 24), C(*SEG_B, 24)])
SEGS = [(52, 176), (100, 80), (156, 176), (204, 80)]
icon('line-segments', DS, ['polyline', 'path', 'vector'],
     line=[C(*p, 20) for p in SEGS] + [seg(SEGS[i], SEGS[i + 1], 20, 20) for i in range(3)],
     area=[C(*p, 20) for p in SEGS])

icon('line-style', DS, ['dashed', 'dotted', 'stroke style', 'border'],
     line=[L(40, 64, 216, 64), L(40, 128, 72, 128), L(112, 128, 144, 128), L(184, 128, 216, 128)],
     dot=[C(40 + i * 44, 192, 16) for i in range(5)])
icon('line-weight', DS, ['stroke width', 'thickness', 'pen size', 'border'],
     line=[L(40, 52, 216, 52), R(40, 92, 176, 24, 12), R(40, 156, 176, 48, 24)],
     area=[R(40, 92, 176, 24, 12), R(40, 156, 176, 48, 24)])

# ---------------------------------------------------------------- box model
icon('margin', DS, ['margin', 'spacing', 'padding', 'box model', 'box margin'],
     line=dashed_box(32, 32, 224, 224) + [R(84, 84, 88, 88, 12)], area=[R(84, 84, 88, 88, 12)])
icon('padding', DS, ['padding', 'spacing', 'inset', 'box model', 'box padding'],
     line=[R(32, 32, 192, 192, 16)], detail=dashed_box(76, 76, 180, 180, arm=26, mid=False),
     area=[R(32, 32, 192, 192, 16)])

# ---------------------------------------------------------------- masks
SQ = R(32, 32, 192, 192, 16)
icon('mask', DS, ['mask', 'clipping', 'layer mask', 'design'],
     line=[SQ, C(128, 128, 56)], area=[SQ], hole=[C(128, 128, 48)])
icon('mask-slash', DS, ['mask', 'off', 'disabled', 'hidden'], line=[SQ, C(128, 128, 56), SLASH])

MC, MR = (152, 152), 100
mp, mq = (224, MC[1] - math.sqrt(MR ** 2 - 72 ** 2)), (MC[0] - math.sqrt(MR ** 2 - 72 ** 2), 224)
MARC = f'M{pt(mp)} ' + arc_to(MC, MR, mp, mq, lambda m: -dist(m, (32, 32)))
icon('mask-shape', DS, ['mask', 'clip', 'shape', 'layer'],
     line=[SQ, P(MARC)],
     area=[P(MARC + ' H208 A16 16 0 0 0 224 208 Z')])

FACE = 'M48 60 C96 36 160 36 208 60 V120 C208 176 168 216 128 216 C88 216 48 176 48 120 Z'
icon('mask-happy', 'Media', ['theater', 'comedy', 'drama'],
     line=[P(FACE)],
     detail=[P('M80 112 A16 16 0 0 1 112 112'), P('M144 112 A16 16 0 0 1 176 112'),
             P('M92 152 A44 44 0 0 0 164 152')],
     area=[P(FACE)])
icon('mask-sad', 'Media', ['theater', 'tragedy', 'drama'],
     line=[P(FACE)],
     detail=[L(80, 112, 112, 100), L(144, 100, 176, 112), P('M92 176 A44 44 0 0 1 164 176')],
     area=[P(FACE)])

# ---------------------------------------------------------------- mesh
def warp(u, v):
    b = 0.13
    return (128 + (160 * u - 80) * (1 + b * math.sin(math.pi * v)),
            128 + (160 * v - 80) * (1 + b * math.sin(math.pi * u)))


def wline(fix, val, k=16):
    return [warp(val, i / k) if fix == 'u' else warp(i / k, val) for i in range(k + 1)]


MESH_OUT = wline('v', 0) + wline('u', 1)[1:] + wline('v', 1)[::-1][1:] + wline('u', 0)[::-1][1:-1]
icon('mesh', DS, ['mesh', 'wireframe', '3d', 'grid'],
     line=[PG(MESH_OUT)],
     detail=[PL(wline('u', t)) for t in (1 / 3, 2 / 3)] + [PL(wline('v', t)) for t in (1 / 3, 2 / 3)],
     area=[PG(MESH_OUT)])

# ---------------------------------------------------------------- objects
OA = R(72, 72, 72, 72, 12)
OB = 'M144 112 H172 A12 12 0 0 1 184 124 V172 A12 12 0 0 1 172 184 H124 A12 12 0 0 1 112 172 V144'
icon('object-group', DS, ['group', 'objects', 'combine', 'selection'],
     line=dashed_box(32, 32, 224, 224) + [OA, P(OB)], area=[OA, R(112, 112, 72, 72, 12)])


def corners(x0, y0, x1, y1, arm, skip):
    cs = {'tl': PL([(x0, y0 + arm), (x0, y0), (x0 + arm, y0)]), 'tr': PL([(x1 - arm, y0), (x1, y0), (x1, y0 + arm)]),
          'br': PL([(x1, y1 - arm), (x1, y1), (x1 - arm, y1)]), 'bl': PL([(x0 + arm, y1), (x0, y1), (x0, y1 - arm)])}
    return [v for k, v in cs.items() if k not in skip]


UA, UB = R(60, 60, 48, 48, 10), R(148, 148, 48, 48, 10)
icon('object-ungroup', DS, ['ungroup', 'objects', 'separate', 'selection', 'split'],
     line=corners(32, 32, 136, 136, 24, ['br']) + corners(120, 120, 224, 224, 24, ['tl']) + [UA, UB],
     area=[UA, UB])

# ---------------------------------------------------------------- octagon
OCT = [(167.76, 32), (224, 88.24), (224, 167.76), (167.76, 224), (88.24, 224), (32, 167.76), (32, 88.24), (88.24, 32)]
BC, BR = (180, 180), 44
RC = 80
oy = BC[1] - math.sqrt(RC ** 2 - (224 - BC[0]) ** 2)
OCT_OPEN = [(224, oy), (224, 88.24), (167.76, 32), (88.24, 32), (32, 88.24), (32, 167.76), (88.24, 224), (oy, 224)]
OCT_AREA = poly(OCT_OPEN) + ' ' + arc_to(BC, RC, (oy, 224), (224, oy), lambda m: -dist(m, (128, 128))) + ' Z'
for nm, tags, det in (
    ('octagon-plus', ['octagon', 'add', 'new', 'create'], [L(180, 164, 180, 196), L(164, 180, 196, 180)]),
    ('octagon-minus', ['octagon', 'remove', 'subtract'], [L(164, 180, 196, 180)]),
):
    icon(nm, DS, tags, line=[PL(OCT_OPEN), C(*BC, BR)], detail=det, area=[P(OCT_AREA), C(*BC, BR)])
icon('octagon-slash', DS, ['octagon', 'off', 'disabled', 'hidden'], line=load('octagon')['line'] + [SLASH])

OH = dict(t=(128, 32), b=(128, 224), l=(36, 112), r=(220, 112), f=(116, 148))
OH_OUT = [OH['t'], OH['r'], OH['b'], OH['l']]
OH_IN = [PL([OH['l'], OH['f'], OH['r']]), L(*OH['t'], *OH['f']), L(*OH['f'], *OH['b'])]
icon('octahedron', DS, ['octahedron', 'd8', 'polyhedron', '3d shape'],
     line=[PG(OH_OUT)], detail=OH_IN, area=[PG(OH_OUT)])
icon('octahedron-slash', DS, ['octahedron', 'off', 'disabled', 'hidden'], line=[PG(OH_OUT)] + OH_IN + [SLASH])

# ---------------------------------------------------------------- paint
HANDLE = 'M108 88 V48 A16 16 0 0 1 124 32 H132 A16 16 0 0 1 148 48 V88'
FERRULE = R(64, 88, 128, 40, 10)
BRISTLE = 'M64 128 L56 208 A16 16 0 0 0 72 224 H184 A16 16 0 0 0 200 208 L192 128'
icon('paint-brush-broad', DS, ['wide brush', 'paint', 'wall brush'],
     line=[P(HANDLE), FERRULE, P(BRISTLE)],
     detail=[L(96, 160, 96, 192), L(128, 160, 128, 192), L(160, 160, 160, 192)],
     area=[P(HANDLE + ' Z'), FERRULE, P(BRISTLE + ' Z')])

pb = load('paint-brush')
icon('paint-brush-slash', DS, ['paint brush', 'disabled', 'off', 'design'], line=pb['line'] + pb['detail'] + [SLASH])

ROLLER = R(32, 32, 160, 64, 16)
WIRE = 'M192 64 H200 A16 16 0 0 1 216 80 V120 A16 16 0 0 1 200 136 H144 A16 16 0 0 0 128 152 V160'
GRIP = R(108, 160, 40, 64, 14)
icon('paint-roller', DS, ['roller', 'painting', 'decorate', 'paint roller', 'format painter'],
     line=[ROLLER, P(WIRE), GRIP], area=[ROLLER, GRIP])
icon('paint-roller-slash', DS, ['paint roller', 'off', 'disabled', 'hidden', 'paint'],
     line=[ROLLER, P(WIRE), GRIP, SLASH])

FRAME = R(32, 80, 192, 144, 14)
icon('painting', DS, ['painting', 'artwork', 'frame', 'art'],
     line=[FRAME, PL([(76, 80), (128, 40), (180, 80)])],
     detail=[PL([(64, 192), (104, 144), (140, 180), (160, 160), (192, 192)])],
     area=[FRAME], dot=[C(128, 40, 16)], dotcut=[C(168, 116, 16)])

pal = load('palette')
icon('palette-slash', DS, ['palette', 'off', 'disabled', 'hidden'],
     line=pal['line'] + [SLASH], dot=[d for d in pal['dotcut'] if 'cx="84"' not in d])

PARA = [(88, 48), (224, 48), (168, 208), (32, 208)]
icon('parallelogram', DS, ['parallelogram', 'quadrilateral', 'shape', 'geometry', 'slanted'],
     line=[PG(PARA)], area=[PG(PARA)])

# ---------------------------------------------------------------- pencil + ruler
s2 = math.sqrt(2)
RH = 32  # ruler half width
ra, rb = (56, 56), (200, 200)
nrm = (1 / s2, -1 / s2)
RUL = [(ra[0] + nrm[0] * RH, ra[1] + nrm[1] * RH), (rb[0] + nrm[0] * RH, rb[1] + nrm[1] * RH),
       (rb[0] - nrm[0] * RH, rb[1] - nrm[1] * RH), (ra[0] - nrm[0] * RH, ra[1] - nrm[1] * RH)]
ticks = []
for i, (s, ln) in enumerate(((52, 26), (88, 16), (124, 26), (160, 16))):
    p0 = (RUL[0][0] + s / s2, RUL[0][1] + s / s2)
    ticks.append(L(*p0, p0[0] - nrm[0] * ln, p0[1] - nrm[1] * ln))
e = RH * s2  # ruler edges at y - x = +-e
tip_piece = [(56 + (104 - e) / 2, 160 - (104 - e) / 2), (56, 160), (40, 216), (96, 200), (96 + (104 - e) / 2, 200 - (104 - e) / 2)]
end_piece = [(56 + (104 + e) / 2, 160 - (104 + e) / 2), (168, 48), (208, 88), (96 + (104 + e) / 2, 200 - (104 + e) / 2)]
icon('pencil-ruler', DS, ['design services', 'drafting', 'design', 'tools', 'draft'],
     line=[PG(RUL), PL(tip_piece), PL(end_piece)],
     detail=ticks + [L(56, 160, 96, 200)],
     area=[PG(RUL), PG(tip_piece), PG(end_piece)])

print(save(overwrite=True))
